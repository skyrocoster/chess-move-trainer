from __future__ import annotations

import sqlite3
from pathlib import Path

from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli

ROOT = Path(__file__).parents[2]
V1_RESOURCE = ROOT / "src" / "chess_move_trainer" / "database" / "schema_v1.sql"
runner = CliRunner()


def _create_v1_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript(V1_RESOURCE.read_text(encoding="utf-8"))


def test_schema_upgrade_cli_is_explicit_and_existing_only(tmp_path: Path) -> None:
    database_path = tmp_path / "v1.db"
    _create_v1_database(database_path)

    result = runner.invoke(
        database_cli.app,
        ["schema", "upgrade", "--database", str(database_path)],
    )

    assert result.exit_code == 0
    assert "Upgraded schema v1 to v2" in result.stdout
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2

    repeated = runner.invoke(
        database_cli.app,
        ["schema", "upgrade", "--database", str(database_path)],
    )
    assert repeated.exit_code == 0
    assert "already compatible" in repeated.stdout


def test_schema_upgrade_cli_does_not_create_a_missing_target(tmp_path: Path) -> None:
    database_path = tmp_path / "missing.db"

    result = runner.invoke(
        database_cli.app,
        ["schema", "upgrade", "--database", str(database_path)],
    )

    assert result.exit_code != 0
    assert not database_path.exists()
