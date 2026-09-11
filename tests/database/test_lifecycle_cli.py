from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli
from chess_move_trainer.database.lifecycle import (
    DEFAULT_DATABASE_PATH,
    LifecycleOperation,
    LifecycleResult,
)

runner = CliRunner()


def test_supported_lifecycle_help_uses_one_fixed_destination() -> None:
    for arguments in (("setup",), ("update", "games"), ("update", "openings")):
        result = runner.invoke(database_cli.app, [*arguments, "--help"])

        assert result.exit_code == 0
        assert DEFAULT_DATABASE_PATH.as_posix() in result.stdout
        help_text = result.stdout.lower()
        assert "destination is" in help_text
        assert "configurable" in help_text
        assert "--database" not in result.stdout
        assert "--config" not in result.stdout


def test_root_help_has_no_retired_database_file_lifecycle_commands() -> None:
    result = runner.invoke(database_cli.app, ["--help"])

    assert result.exit_code == 0
    help_text = result.stdout.lower()
    for retired_term in (
        "rebuild",
        "acquire",
        "snapshot",
        "rollback",
        "recovery",
        "replacement",
        "verification",
    ):
        assert retired_term not in help_text


def test_lifecycle_adapters_forward_fixed_path_service_results(monkeypatch) -> None:
    cases = (
        (("setup",), "setup_database", LifecycleOperation.SETUP),
        (("update", "games"), "update_games", LifecycleOperation.UPDATE_GAMES),
        (("update", "openings"), "update_openings", LifecycleOperation.UPDATE_OPENINGS),
    )

    for arguments, service_name, operation in cases:
        monkeypatch.setattr(
            database_cli,
            service_name,
            lambda operation=operation: LifecycleResult(
                operation=operation,
                database_path=DEFAULT_DATABASE_PATH,
                message="completed",
            ),
        )
        result = runner.invoke(database_cli.app, list(arguments))

        assert result.exit_code == 0
        assert "completed" in result.stdout
        assert str(DEFAULT_DATABASE_PATH) in result.stdout


@pytest.mark.parametrize("exit_code", [1, 2, 130])
def test_lifecycle_adapters_preserve_service_exit_mapping(monkeypatch, exit_code: int) -> None:
    monkeypatch.setattr(
        database_cli,
        "setup_database",
        lambda: LifecycleResult(
            operation=LifecycleOperation.SETUP,
            database_path=DEFAULT_DATABASE_PATH,
            message="failed",
            exit_code=exit_code,
        ),
    )

    result = runner.invoke(database_cli.app, ["setup"])

    assert result.exit_code == exit_code
    assert ("Interrupted" if exit_code == 130 else "failed") in result.stderr


def test_lifecycle_adapter_rejects_a_service_destination_override(monkeypatch) -> None:
    monkeypatch.setattr(
        database_cli,
        "setup_database",
        lambda: LifecycleResult(
            operation=LifecycleOperation.SETUP,
            database_path=Path("other.db"),
            message="completed",
        ),
    )

    result = runner.invoke(database_cli.app, ["setup"])

    assert result.exit_code == 1
    assert "destination" in result.stderr.lower()
