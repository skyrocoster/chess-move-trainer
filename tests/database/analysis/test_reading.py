from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisResultInput,
    AnalysisScoreKind,
)
from chess_move_trainer.database.analysis.reading import AnalysisReadError, AnalysisReadRepository
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.stockfish import BROWSER_PROFILE, TOOL_PROFILE

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
ROOT_MOVES = ("a2a3", "a2a4", "b2b3", "b2b4", "c2c3")


def _result(quality: AnalysisQuality, configuration_version: int) -> AnalysisResultInput:
    profile = BROWSER_PROFILE if quality is AnalysisQuality.BROWSER else TOOL_PROFILE
    return AnalysisResultInput(
        quality=quality,
        configuration_version=configuration_version,
        settings=profile.settings,
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
            for rank, move in enumerate(ROOT_MOVES[: profile.multipv], start=1)
        ),
    )


def test_analysis_reader_returns_complete_current_result(tmp_path: Path) -> None:
    database = tmp_path / "analysis-reading.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    repository = AnalysisRepository(database)
    assert repository.publish(position_id, _result(AnalysisQuality.BROWSER, 2)).saved
    assert repository.publish(position_id, _result(AnalysisQuality.TOOL, 1)).saved

    result = AnalysisReadRepository(database).read(position_id)

    assert result is not None
    assert result.position_id == position_id
    assert result.quality is AnalysisQuality.TOOL
    assert result.quality_order == 1
    assert result.settings == dict(TOOL_PROFILE.settings)
    assert [line.rank for line in result.lines] == [1, 2, 3, 4, 5]
    assert [line.pv_uci for line in result.lines] == [(move,) for move in ROOT_MOVES]
    assert result.terminal_kind is None


def test_analysis_reader_rejects_incomplete_current_full_result(tmp_path: Path) -> None:
    database = tmp_path / "incomplete-analysis-reading.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    repository = AnalysisRepository(database)
    assert repository.publish(position_id, _result(AnalysisQuality.TOOL, 1)).saved

    with sqlite3.connect(database) as connection:
        connection.execute(
            "DELETE FROM derived_analysis_line "
            "WHERE derived_analysis_result_id = ? AND dal_rank = 5",
            (position_id,),
        )
        connection.commit()

    with pytest.raises(AnalysisReadError, match="incomplete or inconsistent"):
        AnalysisReadRepository(database).read(position_id)


def test_analysis_reader_rejects_profile_inconsistent_current_result(tmp_path: Path) -> None:
    database = tmp_path / "inconsistent-analysis-reading.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(STARTING_FEN)
    repository = AnalysisRepository(database)
    assert repository.publish(position_id, _result(AnalysisQuality.TOOL, 1)).saved

    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE derived_analysis_result SET dar_settings_json = ? "
            "WHERE derived_position_id = ?",
            (json.dumps({"Hash": 16}), position_id),
        )
        connection.commit()

    with pytest.raises(AnalysisReadError, match="incomplete or inconsistent"):
        AnalysisReadRepository(database).read(position_id)
