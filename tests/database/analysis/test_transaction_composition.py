from __future__ import annotations

from pathlib import Path

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisScoreKind,
    PublicationOutcome,
    validate_analysis_result,
)
from chess_move_trainer.database.analysis import repository as repository_module
from chess_move_trainer.database.positions import PositionRepository

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
ROOTS = (
    "e2e4",
    "d2d4",
    "g1f3",
    "c2c4",
    "b1c3",
)


def _result() -> object:
    return validate_analysis_result(
        quality=AnalysisQuality.TOOL,
        configuration_version=1,
        settings={"Hash": 16},
        engine_name="composition-test-engine",
        engine_version="engine-1",
        lines=tuple(
            AnalysisLine(
                rank=rank,
                score_kind=AnalysisScoreKind.CP,
                score_value=rank,
                wdl_wins=400,
                wdl_draws=300,
                wdl_losses=300,
                pv_uci=(root, "e7e5" if root != "b1c3" else "b8c6"),
                depth=12,
            )
            for rank, root in enumerate(ROOTS, start=1)
        ),
    )


def test_public_publish_delegates_to_private_transaction_participant(
    tmp_path: Path, monkeypatch
) -> None:
    database_path = tmp_path / "composition.db"
    create_schema(database_path)
    position_id = PositionRepository(database_path).resolve_fen(STARTING_FEN)
    calls: list[object] = []
    original = repository_module._publish_in_transaction

    def participant(*args, **kwargs):
        calls.append(args[0])
        return original(*args, **kwargs)

    monkeypatch.setattr(repository_module, "_publish_in_transaction", participant)

    outcome = AnalysisRepository(database_path).publish(position_id, _result())

    assert outcome == PublicationOutcome.saved_result()
    assert len(calls) == 1
