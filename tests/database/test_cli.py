from __future__ import annotations

import os
import json
import shutil
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
from chess_move_trainer.database.openings.source import load_opening_sources
from chess_move_trainer.database.preferred_moves.repository import PreferredMoveLockError


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


OPENINGS_FIXTURE_DIR = ROOT / "tests/database/openings/fixtures/catalogue-valid"


def _opening_sources(tmp_path: Path) -> Path:
    source_dir = tmp_path / "opening-sources"
    shutil.copytree(OPENINGS_FIXTURE_DIR, source_dir)
    return source_dir


def test_openings_root_group_and_command_help_expose_only_explicit_inputs() -> None:
    root = _runner().invoke(database_cli.app, ["--help"])
    group = _runner().invoke(database_cli.app, ["openings", "--help"])
    commands = {
        "import": ("--source-dir", "--database", "--json"),
        "lookup": ("--database", "--fen", "--json"),
        "replay": ("--database", "--pgn-file", "--json"),
    }

    assert root.exit_code == group.exit_code == 0
    assert "openings" in root.stdout
    for command, options in commands.items():
        result = _runner().invoke(database_cli.app, ["openings", command, "--help"])
        assert result.exit_code == 0
        assert all(option in result.stdout for option in options)
    assert all(command in group.stdout for command in commands)


def test_openings_import_has_deterministic_default_and_json_output(tmp_path: Path) -> None:
    source_dir = _opening_sources(tmp_path)
    database_path = tmp_path / "import.db"
    create_schema(database_path)

    default = _run_cli(
        "openings",
        "import",
        "--source-dir",
        str(source_dir),
        "--database",
        str(database_path),
        input_bytes=b"stdin must not be read",
    )
    machine = _run_cli(
        "openings",
        "import",
        "--source-dir",
        str(source_dir),
        "--database",
        str(database_path),
        "--json",
    )

    assert default.returncode == machine.returncode == 0
    assert b"Imported 4 opening label(s), 5 route(s), and 20 move(s)." in default.stdout
    assert default.stderr == b""
    assert json.loads(machine.stdout) == {
        "opening_count": 4,
        "route_count": 5,
        "move_count": 20,
    }
    assert machine.stderr == b""


def test_openings_lookup_and_replay_have_default_json_and_stdin_independent_output(
    tmp_path: Path,
) -> None:
    source_dir = _opening_sources(tmp_path)
    database_path = tmp_path / "recognition.db"
    create_schema(database_path)
    _run_cli(
        "openings",
        "import",
        "--source-dir",
        str(source_dir),
        "--database",
        str(database_path),
    )
    route = load_opening_sources(source_dir)[0]
    pgn_file = tmp_path / "route.pgn"
    pgn_file.write_text("1. e4 e5 2. Nf3 Nc6", encoding="utf-8")

    lookup_default = _run_cli(
        "openings",
        "lookup",
        "--database",
        str(database_path),
        "--fen",
        route.endpoint_fen,
        input_bytes=b"not lookup input",
    )
    lookup_json = _run_cli(
        "openings",
        "lookup",
        "--database",
        str(database_path),
        "--fen",
        route.endpoint_fen,
        "--json",
    )
    replay_default = _run_cli(
        "openings",
        "replay",
        "--database",
        str(database_path),
        "--pgn-file",
        str(pgn_file),
        input_bytes=b"not replay input",
    )
    replay_json = _run_cli(
        "openings",
        "replay",
        "--database",
        str(database_path),
        "--pgn-file",
        str(pgn_file),
        "--json",
    )

    assert lookup_default.returncode == replay_default.returncode == 0
    assert b"Recognized openings:" in lookup_default.stdout
    assert b"Current:" in replay_default.stdout
    expected_lookup = {
        "recognized": [
            {"ply": 4, "eco": "A00", "name": "Basic route", "match": "transposition"}
        ],
        "current": {
            "ply": 4,
            "eco": "A00",
            "name": "Basic route",
            "match": "transposition",
        },
    }
    expected_replay = {
        "recognized": [{"ply": 4, "eco": "A00", "name": "Basic route", "match": "route"}],
        "current": {"ply": 4, "eco": "A00", "name": "Basic route", "match": "route"},
    }
    assert json.loads(lookup_json.stdout) == expected_lookup
    assert json.loads(replay_json.stdout) == expected_replay
    assert not lookup_default.stderr
    assert not replay_default.stderr


def test_openings_valid_no_match_is_status_zero_with_empty_json_result(tmp_path: Path) -> None:
    source_dir = _opening_sources(tmp_path)
    database_path = tmp_path / "no-match.db"
    create_schema(database_path)
    _run_cli(
        "openings",
        "import",
        "--source-dir",
        str(source_dir),
        "--database",
        str(database_path),
    )

    result = _run_cli(
        "openings",
        "lookup",
        "--database",
        str(database_path),
        "--fen",
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "--json",
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {"recognized": [], "current": None}
    assert result.stderr == b""


def test_openings_invalid_input_source_and_database_failures_use_settled_exits(
    tmp_path: Path,
) -> None:
    source_dir = _opening_sources(tmp_path)
    database_path = tmp_path / "errors.db"
    create_schema(database_path)
    invalid_fen = _run_cli(
        "openings",
        "lookup",
        "--database",
        str(database_path),
        "--fen",
        "not a FEN",
    )
    missing_pgn = _run_cli(
        "openings",
        "replay",
        "--database",
        str(database_path),
        "--pgn-file",
        str(tmp_path / "missing.pgn"),
    )
    second_game = tmp_path / "second-game.pgn"
    second_game.write_text('1. e4 * [Event "second"] 1. d4', encoding="utf-8")
    multiple_games = _run_cli(
        "openings",
        "replay",
        "--database",
        str(database_path),
        "--pgn-file",
        str(second_game),
    )
    bad_source = _opening_sources(tmp_path / "bad")
    (bad_source / "a.tsv").write_text(
        "eco\tname\tpgn\nA00\tBad\t1. e4 Nonsense\n", encoding="utf-8"
    )
    bad_catalogue = _run_cli(
        "openings",
        "import",
        "--source-dir",
        str(bad_source),
        "--database",
        str(database_path),
    )
    missing_database = _run_cli(
        "openings",
        "import",
        "--source-dir",
        str(source_dir),
        "--database",
        str(tmp_path / "missing.db"),
    )
    incompatible = tmp_path / "incompatible.db"
    sqlite3.connect(incompatible).close()
    incompatible_result = _run_cli(
        "openings",
        "import",
        "--source-dir",
        str(source_dir),
        "--database",
        str(incompatible),
    )

    assert invalid_fen.returncode == 2
    assert missing_pgn.returncode == 2
    assert multiple_games.returncode == 2
    assert bad_catalogue.returncode == 1
    assert missing_database.returncode == 1
    assert incompatible_result.returncode == 3
    for result in (
        invalid_fen,
        missing_pgn,
        multiple_games,
        bad_catalogue,
        missing_database,
        incompatible_result,
    ):
        assert result.stdout == b""
        assert result.stderr


def test_openings_operational_failure_and_interruption_are_status_one_and_130(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise database_cli.OpeningPersistenceError("synthetic storage failure")

    monkeypatch.setattr(database_cli, "import_opening_catalogue", fail)
    failed = _runner().invoke(
        database_cli.app,
        ["openings", "import", "--source-dir", "sources", "--database", "database.db"],
    )

    def interrupt(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise KeyboardInterrupt

    monkeypatch.setattr(database_cli, "import_opening_catalogue", interrupt)
    interrupted = _runner().invoke(
        database_cli.app,
        ["openings", "import", "--source-dir", "sources", "--database", "database.db"],
    )

    assert failed.exit_code == 1
    assert interrupted.exit_code == 130
    assert "synthetic storage failure" in failed.stderr
    assert "Interrupted" in interrupted.stderr


PREFERRED_MOVES_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"


def test_preferred_moves_help_exposes_exact_group_and_commands() -> None:
    root = _runner().invoke(database_cli.app, ["--help"])
    group = _runner().invoke(database_cli.app, ["preferred-moves", "--help"])
    commands = {
        "list": ("--database", "--fen", "--json"),
        "resolve": ("--database", "--fen", "--date", "--json"),
        "set": ("--database", "--fen", "--from", "--until", "--move", "--no-preference", "--json"),
        "unset": ("--database", "--fen", "--from", "--until", "--json"),
    }

    assert root.exit_code == 0
    assert group.exit_code == 0
    assert "preferred-moves" in root.stdout
    assert all(command in group.stdout for command in commands)
    for command, options in commands.items():
        result = _runner().invoke(
            database_cli.app, ["preferred-moves", command, "--help"]
        )
        assert result.exit_code == 0
        assert all(option in result.stdout for option in options)


@pytest.mark.parametrize(
    "arguments",
    [
        ["preferred-moves", "list"],
        ["preferred-moves", "resolve", "--database", "database.db", "--fen", PREFERRED_MOVES_FEN],
        [
            "preferred-moves",
            "set",
            "--database",
            "database.db",
            "--fen",
            PREFERRED_MOVES_FEN,
            "--from",
            "2026-01-01",
        ],
        [
            "preferred-moves",
            "unset",
            "--database",
            "database.db",
            "--fen",
            PREFERRED_MOVES_FEN,
        ],
    ],
)
def test_preferred_moves_required_options_are_noninteractive(arguments: list[str]) -> None:
    result = _runner().invoke(database_cli.app, arguments, input="stdin must not be read")

    assert result.exit_code == 2
    assert result.stdout == ""
    assert result.stderr


@pytest.mark.parametrize("extra", [["--move", "e2e4", "--no-preference"], []])
def test_preferred_moves_set_requires_exactly_one_selector(
    tmp_path: Path, extra: list[str]
) -> None:
    database = tmp_path / "selectors.db"
    create_schema(database)
    result = _runner().invoke(
        database_cli.app,
        [
            "preferred-moves",
            "set",
            "--database",
            str(database),
            "--fen",
            PREFERRED_MOVES_FEN,
            "--from",
            "2026-01-01",
            *extra,
        ],
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert result.stderr


def test_preferred_moves_list_resolve_set_and_unset_have_stable_outputs(
    tmp_path: Path,
) -> None:
    database = tmp_path / "preferred.db"
    create_schema(database)
    base = [
        "preferred-moves",
        "list",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
    ]

    empty = _run_cli(*base, "--json", input_bytes=b"stdin must not be read")
    unconfigured = _run_cli(
        "preferred-moves",
        "resolve",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
        "--date",
        "2026-01-15",
        "--json",
    )
    preferred = _run_cli(
        "preferred-moves",
        "set",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
        "--from",
        "2026-01-01",
        "--until",
        "2026-02-01",
        "--move",
        "e2e4",
        "--json",
        input_bytes=b"stdin must not be read",
    )
    no_preference = _run_cli(
        "preferred-moves",
        "set",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
        "--from",
        "2026-02-01",
        "--until",
        "2026-03-01",
        "--no-preference",
        "--json",
    )
    listed = _run_cli(*base, "--json")
    preferred_resolution = _run_cli(
        "preferred-moves",
        "resolve",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
        "--date",
        "2026-01-15",
    )
    no_preference_resolution = _run_cli(
        "preferred-moves",
        "resolve",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
        "--date",
        "2026-02-15",
        "--json",
    )
    unset = _run_cli(
        "preferred-moves",
        "unset",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
        "--from",
        "2026-01-15",
        "--until",
        "2026-02-15",
        "--json",
    )
    no_op_unset = _run_cli(
        "preferred-moves",
        "unset",
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
        "--from",
        "2027-01-01",
        "--until",
        "2027-02-01",
        "--json",
    )

    assert all(result.returncode == 0 for result in (
        empty,
        unconfigured,
        preferred,
        no_preference,
        listed,
        preferred_resolution,
        no_preference_resolution,
        unset,
        no_op_unset,
    ))
    assert json.loads(empty.stdout) == {"periods": []}
    assert json.loads(unconfigured.stdout) == {"move": None, "state": "unconfigured"}
    assert json.loads(preferred.stdout) == {
        "periods": [
            {
                "effective_from": "2026-01-01",
                "effective_until": "2026-02-01",
                "move": "e2e4",
                "state": "preferred_move",
            }
        ]
    }
    assert json.loads(no_preference.stdout) == {
        "periods": [
            {
                "effective_from": "2026-01-01",
                "effective_until": "2026-02-01",
                "move": "e2e4",
                "state": "preferred_move",
            },
            {
                "effective_from": "2026-02-01",
                "effective_until": "2026-03-01",
                "move": None,
                "state": "no_preference",
            },
        ]
    }
    assert json.loads(listed.stdout) == json.loads(no_preference.stdout)
    assert preferred_resolution.stdout.decode().splitlines() == ["Preferred move: e2e4"]
    assert json.loads(no_preference_resolution.stdout) == {
        "move": None,
        "state": "no_preference",
    }
    assert json.loads(unset.stdout) == {
        "periods": [
            {
                "effective_from": "2026-01-01",
                "effective_until": "2026-01-15",
                "move": "e2e4",
                "state": "preferred_move",
            },
            {
                "effective_from": "2026-02-15",
                "effective_until": "2026-03-01",
                "move": None,
                "state": "no_preference",
            }
        ]
    }
    assert json.loads(no_op_unset.stdout) == json.loads(unset.stdout)
    for result in (
        empty,
        unconfigured,
        preferred,
        no_preference,
        listed,
        preferred_resolution,
        no_preference_resolution,
        unset,
        no_op_unset,
    ):
        assert result.stderr == b""


def test_preferred_moves_human_output_covers_empty_and_all_resolution_shapes(
    tmp_path: Path,
) -> None:
    database = tmp_path / "human-output.db"
    create_schema(database)
    common = [
        "--database",
        str(database),
        "--fen",
        PREFERRED_MOVES_FEN,
    ]

    empty_list = _run_cli("preferred-moves", "list", *common)
    unconfigured = _run_cli(
        "preferred-moves",
        "resolve",
        *common,
        "--date",
        "2026-01-15",
    )
    finite = _run_cli(
        "preferred-moves",
        "set",
        *common,
        "--from",
        "2026-01-01",
        "--until",
        "2026-02-01",
        "--move",
        "e2e4",
    )
    indefinite = _run_cli(
        "preferred-moves",
        "set",
        *common,
        "--from",
        "2026-02-01",
        "--no-preference",
    )
    periods = _run_cli("preferred-moves", "list", *common)
    no_preference = _run_cli(
        "preferred-moves",
        "resolve",
        *common,
        "--date",
        "2026-02-15",
    )

    assert all(result.returncode == 0 for result in (
        empty_list,
        unconfigured,
        finite,
        indefinite,
        periods,
        no_preference,
    ))
    assert empty_list.stdout.decode().splitlines() == [
        "No preferred-move periods configured."
    ]
    assert unconfigured.stdout.decode().splitlines() == ["Unconfigured."]
    assert periods.stdout.decode().splitlines() == [
        "Preferred-move periods:",
        "- 2026-01-01 to 2026-02-01: e2e4",
        "- 2026-02-01 to indefinite: no preference",
    ]
    assert no_preference.stdout.decode().splitlines() == ["Explicit no preference."]
    for result in (
        empty_list,
        unconfigured,
        finite,
        indefinite,
        periods,
        no_preference,
    ):
        assert result.stderr == b""


def test_preferred_moves_lock_failure_is_status_one_and_stderr_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class LockedRepository:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        def list_periods(self, fen: str) -> tuple[object, ...]:
            del fen
            raise PreferredMoveLockError("synthetic preferred-move lock failure")

    monkeypatch.setattr(database_cli, "PreferredMoveRepository", LockedRepository)
    result = _runner().invoke(
        database_cli.app,
        [
            "preferred-moves",
            "list",
            "--database",
            str(tmp_path / "locked.db"),
            "--fen",
            PREFERRED_MOVES_FEN,
        ],
    )

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "lock failure" in result.stderr


@pytest.mark.parametrize(
    "arguments",
    [
        ["list", "--fen", "not a FEN"],
        ["resolve", "--fen", PREFERRED_MOVES_FEN, "--date", "today"],
        [
            "set",
            "--fen",
            PREFERRED_MOVES_FEN,
            "--from",
            "2026-02-01",
            "--until",
            "2026-01-01",
            "--move",
            "e2e4",
        ],
        [
            "set",
            "--fen",
            PREFERRED_MOVES_FEN,
            "--from",
            "2026-01-01",
            "--move",
            "e2e5",
        ],
    ],
)
def test_preferred_moves_invalid_inputs_are_status_two(
    tmp_path: Path, arguments: list[str]
) -> None:
    database = tmp_path / "invalid.db"
    create_schema(database)
    result = _run_cli(
        "preferred-moves",
        arguments[0],
        "--database",
        str(database),
        *arguments[1:],
    )

    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr


def test_preferred_moves_schema_and_storage_failures_use_status_three_and_one(
    tmp_path: Path,
) -> None:
    incompatible = tmp_path / "incompatible.db"
    sqlite3.connect(incompatible).close()
    schema_failure = _run_cli(
        "preferred-moves",
        "list",
        "--database",
        str(incompatible),
        "--fen",
        PREFERRED_MOVES_FEN,
    )
    storage_failure = _run_cli(
        "preferred-moves",
        "list",
        "--database",
        str(tmp_path / "missing.db"),
        "--fen",
        PREFERRED_MOVES_FEN,
    )

    assert schema_failure.returncode == 3
    assert storage_failure.returncode == 1
    for result in (schema_failure, storage_failure):
        assert result.stdout == b""
        assert result.stderr


def test_preferred_moves_interruption_is_status_130_and_stderr_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class InterruptedRepository:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        def set(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            raise KeyboardInterrupt

    monkeypatch.setattr(database_cli, "PreferredMoveRepository", InterruptedRepository)
    result = _runner().invoke(
        database_cli.app,
        [
            "preferred-moves",
            "set",
            "--database",
            str(tmp_path / "interrupted.db"),
            "--fen",
            PREFERRED_MOVES_FEN,
            "--from",
            "2026-01-01",
            "--move",
            "e2e4",
        ],
    )

    assert result.exit_code == 130
    assert result.stdout == ""
    assert "Interrupted" in result.stderr
