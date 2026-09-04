from __future__ import annotations

import os
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from chess_move_trainer.database import create_schema
from chess_move_trainer.database import cli as database_cli
from chess_move_trainer.database.games.acquisition import (
    AcquisitionFailure,
    AcquisitionResult,
)


ROOT = Path(__file__).parents[2]
CLI_TIMEOUT_SECONDS = 15
TRAINER_UUID = "11111111-1111-4111-8111-111111111111"


def _run_cli(*arguments: str, input_bytes: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, "-m", "chess_move_trainer.database", *arguments],
        cwd=ROOT,
        env=environment,
        input=input_bytes,
        capture_output=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )


def test_each_supported_command_has_useful_help() -> None:
    for command in ("create", "inspect"):
        result = _run_cli("schema", command, "--help")

        assert result.returncode == 0
        help_text = result.stdout.decode("utf-8")
        assert "--database" in help_text
        assert "--lock-timeout" in help_text
        assert result.stderr == b""


@pytest.mark.parametrize("command", ["create", "inspect"])
def test_database_option_is_required(command: str, tmp_path: Path) -> None:
    result = _run_cli("schema", command)

    assert result.returncode == 2
    assert b"--database" in result.stderr
    assert not (tmp_path / "database.db").exists()


def test_create_succeeds_idempotently_and_reports_on_stdout(tmp_path: Path) -> None:
    database_path = tmp_path / "created.db"

    first = _run_cli("schema", "create", "--database", str(database_path))
    original_bytes = database_path.read_bytes()
    second = _run_cli("schema", "create", "--database", str(database_path))

    assert first.returncode == 0
    assert second.returncode == 0
    assert first.stdout
    assert second.stdout
    assert first.stderr == b""
    assert second.stderr == b""
    assert database_path.read_bytes() == original_bytes


def test_incompatible_create_exits_three_without_changing_target(tmp_path: Path) -> None:
    database_path = tmp_path / "incompatible.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    original_bytes = database_path.read_bytes()

    result = _run_cli("schema", "create", "--database", str(database_path))

    assert result.returncode == 3
    assert result.stdout == b""
    assert b"compatible" in result.stderr.lower()
    assert database_path.read_bytes() == original_bytes


@pytest.mark.parametrize("timeout", ["0", "-1", "nan", "inf", "-inf"])
def test_invalid_lock_timeout_is_usage_error(timeout: str, tmp_path: Path) -> None:
    result = _run_cli(
        "schema",
        "create",
        "--database",
        str(tmp_path / "invalid.db"),
        "--lock-timeout",
        timeout,
    )

    assert result.returncode == 2
    assert b"lock-timeout" in result.stderr
    assert not (tmp_path / "invalid.db").exists()


def test_inspect_invalid_lock_timeout_is_usage_error(tmp_path: Path) -> None:
    database_path = tmp_path / "invalid-inspect.db"
    sqlite3.connect(database_path).close()

    result = _run_cli(
        "schema",
        "inspect",
        "--database",
        str(database_path),
        "--lock-timeout",
        "nan",
    )

    assert result.returncode == 2
    assert b"lock-timeout" in result.stderr
    assert result.stdout == b""


def test_malformed_or_operational_failure_is_one_and_uses_stderr(tmp_path: Path) -> None:
    database_path = tmp_path / "malformed.db"
    database_path.write_bytes(b"not a sqlite database")

    malformed = _run_cli("schema", "create", "--database", str(database_path))
    missing_parent = _run_cli(
        "schema", "create", "--database", str(tmp_path / "missing" / "database.db")
    )

    assert malformed.returncode == 1
    assert malformed.stdout == b""
    assert malformed.stderr
    assert missing_parent.returncode == 1
    assert missing_parent.stdout == b""
    assert missing_parent.stderr


def test_inspect_missing_database_is_operational_failure(tmp_path: Path) -> None:
    database_path = tmp_path / "missing-inspect.db"

    result = _run_cli("schema", "inspect", "--database", str(database_path))

    assert result.returncode == 1
    assert result.stdout == b""
    assert result.stderr
    assert not database_path.exists()


def test_inspect_output_collision_exits_one_without_stdout_or_database_damage(tmp_path: Path) -> None:
    database_path = tmp_path / "collision.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE preserved (id INTEGER PRIMARY KEY)")
    original_bytes = database_path.read_bytes()

    result = _run_cli(
        "schema",
        "inspect",
        "--database",
        str(database_path),
        "--output",
        str(database_path),
    )

    assert result.returncode == 1
    assert result.stdout == b""
    assert b"selected database" in result.stderr.lower()
    assert database_path.read_bytes() == original_bytes


def test_commands_are_non_interactive(tmp_path: Path) -> None:
    database_path = tmp_path / "non-interactive.db"

    create_result = _run_cli(
        "schema",
        "create",
        "--database",
        str(database_path),
        input_bytes=b"",
    )
    inspect_result = _run_cli(
        "schema",
        "inspect",
        "--database",
        str(database_path),
        input_bytes=b"",
    )

    assert create_result.returncode == 0
    assert inspect_result.returncode == 0
    assert inspect_result.stdout
    assert create_result.stderr == b""
    assert inspect_result.stderr == b""


def _config(tmp_path: Path, *, extra: str = "") -> Path:
    path = tmp_path / "games.yaml"
    path.write_text(
        f"username: synthetic-trainer\ntrainer_chesscom_uuid: {TRAINER_UUID}\n{extra}",
        encoding="utf-8",
    )
    return path


def _runner() -> CliRunner:
    return CliRunner()


def test_games_help_has_exact_supported_surface_and_no_base_url() -> None:
    acquire = _runner().invoke(database_cli.app, ["games", "acquire", "--help"])
    import_result = _runner().invoke(database_cli.app, ["games", "import", "--help"])

    assert acquire.exit_code == 0
    assert import_result.exit_code == 0
    for option in (
        "--config",
        "--raw-root",
        "--username",
        "--trainer-chesscom-uuid",
        "--request-timeout",
        "30.0",
        "--request-delay",
        "0.25",
    ):
        assert option in acquire.stdout
    assert "fixed Chess.com API endpoint" in acquire.stdout
    assert "base-url" not in acquire.stdout
    for option in ("--config", "--raw-root", "--database", "--trainer-chesscom-uuid"):
        assert option in import_result.stdout
    assert "base-url" not in import_result.stdout


@pytest.mark.parametrize(
    "arguments",
    [
        ["games", "acquire"],
        ["games", "acquire", "--config", "missing.yaml"],
        ["games", "import"],
        ["games", "import", "--config", "missing.yaml", "--raw-root", "raw"],
    ],
)
def test_games_explicit_paths_are_required(arguments: list[str]) -> None:
    result = _runner().invoke(database_cli.app, arguments)

    assert result.exit_code == 2


def test_acquire_wires_yaml_values_defaults_and_cli_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path, extra="request_timeout: 9.0\nrequest_delay: 1.5\n")
    seen: list[object] = []

    def acquire(configuration: object, raw_root: Path) -> AcquisitionResult:
        seen.extend([configuration, raw_root])
        return AcquisitionResult(("2026-08",), (), ())

    monkeypatch.setattr(database_cli, "acquire_months", acquire)
    yaml_result = _runner().invoke(
        database_cli.app,
        ["games", "acquire", "--config", str(config), "--raw-root", str(tmp_path / "raw")],
    )
    override_result = _runner().invoke(
        database_cli.app,
        [
            "games",
            "acquire",
            "--config",
            str(config),
            "--raw-root",
            str(tmp_path / "raw-two"),
            "--username",
            "synthetic-override",
            "--trainer-chesscom-uuid",
            "22222222-2222-4222-8222-222222222222",
            "--request-timeout",
            "4.0",
            "--request-delay",
            "0.0",
        ],
    )

    assert yaml_result.exit_code == override_result.exit_code == 0
    yaml_configuration, yaml_root, override_configuration, override_root = seen
    assert yaml_configuration.username == "synthetic-trainer"
    assert yaml_configuration.request_timeout == 9.0
    assert yaml_configuration.request_delay == 1.5
    assert yaml_root == tmp_path / "raw"
    assert override_configuration.username == "synthetic-override"
    assert str(override_configuration.trainer_chesscom_uuid) == "22222222-2222-4222-8222-222222222222"
    assert override_configuration.request_timeout == 4.0
    assert override_configuration.request_delay == 0.0
    assert override_root == tmp_path / "raw-two"


def test_acquire_uses_exact_defaults_when_yaml_omits_timing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[object] = []

    def acquire(configuration: object, raw_root: Path) -> AcquisitionResult:
        del raw_root
        seen.append(configuration)
        return AcquisitionResult((), (), ())

    monkeypatch.setattr(database_cli, "acquire_months", acquire)
    result = _runner().invoke(
        database_cli.app,
        [
            "games",
            "acquire",
            "--config",
            str(_config(tmp_path)),
            "--raw-root",
            str(tmp_path / "raw"),
        ],
    )

    assert result.exit_code == 0
    assert seen[0].request_timeout == 30.0
    assert seen[0].request_delay == 0.25


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--request-timeout", "0"),
        ("--request-timeout", "nan"),
        ("--request-delay", "-1"),
        ("--request-delay", "inf"),
    ],
)
def test_acquire_invalid_timing_is_status_two(
    tmp_path: Path, option: str, value: str
) -> None:
    result = _runner().invoke(
        database_cli.app,
        [
            "games",
            "acquire",
            "--config",
            str(_config(tmp_path)),
            "--raw-root",
            str(tmp_path / "raw"),
            option,
            value,
        ],
    )

    assert result.exit_code == 2


def test_acquire_incomplete_and_operational_failures_are_status_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    monkeypatch.setattr(
        database_cli,
        "acquire_months",
        lambda configuration, raw_root: AcquisitionResult(
            (), (), (AcquisitionFailure("2026-08", "synthetic rate limit"),)
        ),
    )
    incomplete = _runner().invoke(
        database_cli.app,
        ["games", "acquire", "--config", str(config), "--raw-root", str(tmp_path / "raw")],
    )

    def fail(configuration: object, raw_root: Path) -> AcquisitionResult:
        del configuration, raw_root
        raise OSError("synthetic operational failure")

    monkeypatch.setattr(database_cli, "acquire_months", fail)
    failed = _runner().invoke(
        database_cli.app,
        ["games", "acquire", "--config", str(config), "--raw-root", str(tmp_path / "raw")],
    )

    assert incomplete.exit_code == failed.exit_code == 1
    assert "rate limit" in incomplete.stderr
    assert "operational failure" in failed.stderr


def test_import_reads_only_month_files_and_completes_with_reported_skip(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw"
    month = raw_root / "games" / "2026" / "08.json"
    month.parent.mkdir(parents=True)
    valid = json.loads(
        (ROOT / "tests/database/games/fixtures/game-trainer-white.json").read_text(encoding="utf-8")
    )
    skipped = json.loads(
        (ROOT / "tests/database/games/fixtures/game-non-standard.json").read_text(encoding="utf-8")
    )
    month.write_text(json.dumps({"games": [valid, skipped]}), encoding="utf-8")
    archives = raw_root / "archives"
    archives.mkdir()
    (archives / "synthetic-trainer.json").write_text("not JSON", encoding="utf-8")
    database = tmp_path / "import.db"
    create_schema(database)

    result = _runner().invoke(
        database_cli.app,
        [
            "games",
            "import",
            "--config",
            str(_config(tmp_path)),
            "--raw-root",
            str(raw_root),
            "--database",
            str(database),
        ],
        input="",
    )

    assert result.exit_code == 0
    assert "Imported 1 game" in result.stdout
    assert "skipped 1" in result.stdout
    assert "Warning:" in result.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0] == 1


def test_import_cli_uuid_override_wins_over_yaml(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw"
    month = raw_root / "games" / "2026" / "08.json"
    month.parent.mkdir(parents=True)
    valid = json.loads(
        (ROOT / "tests/database/games/fixtures/game-trainer-white.json").read_text(encoding="utf-8")
    )
    month.write_text(json.dumps({"games": [valid]}), encoding="utf-8")
    config = _config(tmp_path)
    config.write_text(
        "trainer_chesscom_uuid: 22222222-2222-4222-8222-222222222222\n",
        encoding="utf-8",
    )
    database = tmp_path / "override.db"
    create_schema(database)

    result = _runner().invoke(
        database_cli.app,
        [
            "games",
            "import",
            "--config",
            str(config),
            "--raw-root",
            str(raw_root),
            "--database",
            str(database),
            "--trainer-chesscom-uuid",
            TRAINER_UUID,
        ],
    )

    assert result.exit_code == 0
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0] == 1


def test_import_operational_failure_is_one_and_invalid_config_is_two(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    valid_config = _config(tmp_path)
    invalid_config = tmp_path / "invalid.yaml"
    invalid_config.write_text("trainer_chesscom_uuid: invalid\n", encoding="utf-8")
    arguments = ["--raw-root", str(raw_root), "--database", str(tmp_path / "missing.db")]

    operational = _runner().invoke(
        database_cli.app, ["games", "import", "--config", str(valid_config), *arguments]
    )
    invalid = _runner().invoke(
        database_cli.app, ["games", "import", "--config", str(invalid_config), *arguments]
    )

    assert operational.exit_code == 1
    assert invalid.exit_code == 2


@pytest.mark.parametrize("command", ["acquire", "import"])
def test_games_interruption_is_status_130(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    def interrupt(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise KeyboardInterrupt

    if command == "acquire":
        monkeypatch.setattr(database_cli, "acquire_months", interrupt)
        arguments = [
            "games",
            "acquire",
            "--config",
            str(_config(tmp_path)),
            "--raw-root",
            str(tmp_path / "raw"),
        ]
    else:
        monkeypatch.setattr(database_cli, "import_raw_months", interrupt)
        database = tmp_path / "interrupt.db"
        create_schema(database)
        arguments = [
            "games",
            "import",
            "--config",
            str(_config(tmp_path)),
            "--raw-root",
            str(tmp_path),
            "--database",
            str(database),
        ]

    result = _runner().invoke(database_cli.app, arguments)

    assert result.exit_code == 130
    assert "Interrupted" in result.stderr
