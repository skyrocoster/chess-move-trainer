from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli
from chess_move_trainer.database.preferred_moves.repository import PreferredMoveSchemaError
from chess_move_trainer.database.preferred_moves.setup import (
    PreferredMoveSetupError,
    PreferredMoveSetupRefused,
    PreferredMoveSetupResult,
)


def _runner() -> CliRunner:
    return CliRunner()


def test_preferred_moves_setup_help_registers_exact_command_without_options() -> None:
    group = _runner().invoke(database_cli.app, ["preferred-moves", "--help"])
    command = _runner().invoke(
        database_cli.app, ["preferred-moves", "setup", "--help"]
    )

    assert group.exit_code == 0
    assert "setup" in group.stdout
    assert command.exit_code == 0
    assert "--database" not in command.stdout
    assert "--json" not in command.stdout
    assert "--yes" not in command.stdout


def test_preferred_moves_setup_forwards_fixed_path_without_reading_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[Path] = []

    def setup(database: Path) -> PreferredMoveSetupResult:
        seen.append(database)
        return PreferredMoveSetupResult(0, 0, 0, 0, 0)

    monkeypatch.setattr(database_cli, "run_preferred_moves_setup", setup)
    result = _runner().invoke(
        database_cli.app,
        ["preferred-moves", "setup"],
        input="stdin must not be read",
    )
    option_result = _runner().invoke(
        database_cli.app,
        ["preferred-moves", "setup", "--database", "alternate.db"],
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    assert seen == [database_cli.DEFAULT_DATABASE_PATH]
    assert option_result.exit_code == 2
    assert option_result.stdout == ""


@pytest.mark.parametrize(
    "summary",
    [
        PreferredMoveSetupResult(12, 2, 3, 4, 1),
        PreferredMoveSetupResult(0, 0, 0, 0, 0),
    ],
)
def test_preferred_moves_setup_prints_only_the_five_summary_counts(
    monkeypatch: pytest.MonkeyPatch, summary: PreferredMoveSetupResult
) -> None:
    monkeypatch.setattr(
        database_cli, "run_preferred_moves_setup", lambda path: summary
    )

    result = _runner().invoke(database_cli.app, ["preferred-moves", "setup"])

    assert result.exit_code == 0
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        f"Examined games: {summary.examined_games}",
        f"Skipped games: {summary.skipped_games}",
        f"Qualifying positions: {summary.qualifying_positions}",
        f"Periods applied: {summary.periods_applied}",
        f"Conflicting positions: {summary.conflicting_positions}",
    ]


@pytest.mark.parametrize(
    "error, exit_code",
    [
        (PreferredMoveSetupRefused("preferred-move setup requires an empty schedule"), 1),
        (PreferredMoveSetupError("synthetic setup failure"), 1),
        (PreferredMoveSchemaError("incompatible schema"), 3),
    ],
)
def test_preferred_moves_setup_maps_failures_to_stderr_status(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    exit_code: int,
) -> None:
    def fail(path: Path) -> PreferredMoveSetupResult:
        del path
        raise error

    monkeypatch.setattr(database_cli, "run_preferred_moves_setup", fail)

    result = _runner().invoke(database_cli.app, ["preferred-moves", "setup"])

    assert result.exit_code == exit_code
    assert result.stdout == ""
    assert str(error) in result.stderr
