from __future__ import annotations

from pathlib import Path

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisResultInput,
    AnalysisScoreKind,
)
from chess_move_trainer.database.analysis.reading import AnalysisReadRepository
from chess_move_trainer.database.positions import PositionRepository


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
ROOT_MOVES = ("a2a3", "a2a4", "b2b3", "b2b4", "c2c3")


def _result(quality: AnalysisQuality, configuration_version: int) -> AnalysisResultInput:
    return AnalysisResultInput(
        quality=quality,
        configuration_version=configuration_version,
        settings={"Hash": 16, "Threads": 1},
        engine_name="synthetic-engine",
        engine_version="synthetic-1",
        lines=tuple(
            AnalysisLine(
                rank=rank,
                score_kind=AnalysisScoreKind.CP,
                score_value=rank,
                wdl_wins=400,
                wdl_draws=300,
                wdl_losses=300,
                pv_uci=(move,),
                depth=12,
            )
            for rank, move in enumerate(ROOT_MOVES, start=1)
        ),
    )


def test_analysis_reader_returns_complete_current_result(tmp_path: Path) -> None:
    database = tmp_path / "analysis-reading.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    repository = AnalysisRepository(database)
    assert repository.publish(
        position_id, _result(AnalysisQuality.BROWSER, 1)
    ).saved
    assert repository.publish(position_id, _result(AnalysisQuality.TOOL, 1)).saved

    result = AnalysisReadRepository(database).read(position_id)

    assert result is not None
    assert result.position_id == position_id
    assert result.quality is AnalysisQuality.TOOL
    assert result.quality_order == 1
    assert result.settings == {"Hash": 16, "Threads": 1}
    assert [line.rank for line in result.lines] == [1, 2, 3, 4, 5]
    assert [line.pv_uci for line in result.lines] == [(move,) for move in ROOT_MOVES]
    assert result.terminal_kind is None
