from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli
from chess_move_trainer.database import cli_stockfish
from chess_move_trainer.database.stockfish import WorkerOutcome


runner = CliRunner()


def test_worker_help_exposes_explicit_parallel_opt_in() -> None:
    result = runner.invoke(database_cli.app, ["stockfish", "worker", "--help"])

    assert result.exit_code == 0
    assert "--parallel" in result.stdout


def test_worker_cli_forwards_parallel_mode_without_changing_default(
    monkeypatch,
    tmp_path: Path,
) -> None:
    seen: list[bool] = []

    class _FakeRunner:
        def __init__(self, _database, _executable, **kwargs) -> None:
            seen.append(kwargs["parallel"])

        def run(self) -> WorkerOutcome:
            return WorkerOutcome(claimed_count=0, completed_count=0, not_saved_count=0)

    monkeypatch.setattr(cli_stockfish, "WorkerRunner", _FakeRunner)
    arguments = [
        "stockfish",
        "worker",
        "--database",
        str(tmp_path / "worker.db"),
        "--executable",
        "stockfish.exe",
    ]

    normal = runner.invoke(database_cli.app, arguments)
    accelerated = runner.invoke(database_cli.app, [*arguments, "--parallel"])

    assert normal.exit_code == 0
    assert accelerated.exit_code == 0
    assert seen == [False, True]
