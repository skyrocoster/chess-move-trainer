from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[2]
CLI_TIMEOUT_SECONDS = 15


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
