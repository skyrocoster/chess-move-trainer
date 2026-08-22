from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import chess
import pytest

from backend.app.features.analysis import (
    AnalysisCandidate,
    AnalysisProfile,
    AnalysisResult,
    initialize_analysis_schema,
)
from backend.app.features.evaluation import initialize_evaluation_schema

QUALIFIED_PROFILE_ID = "mp09-balanced-nodes-v2-200000"
START_FEN = chess.STARTING_FEN
FOOLS_MATE_FEN = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
STALEMATE_FEN = "k7/8/1Q6/8/8/8/8/7K b - - 0 1"


@pytest.fixture
def connection(tmp_path: Path):
    database = tmp_path / "evaluation.db"
    db = sqlite3.connect(database)
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    return tmp_path / "evaluation.db"


@pytest.fixture
def profile() -> AnalysisProfile:
    return AnalysisProfile(
        profile_id=QUALIFIED_PROFILE_ID,
        engine_binary_sha256="a" * 64,
        engine_name="Stockfish 18 fake",
        engine_version="18-test",
        node_budget=200_000,
    )


def initialized(db: sqlite3.Connection) -> None:
    initialize_analysis_schema(db)
    initialize_evaluation_schema(db)


def completed_at() -> str:
    return datetime(2026, 8, 20, 12, 0, tzinfo=UTC).isoformat()


def result_for(profile: AnalysisProfile, fen: str) -> AnalysisResult:
    board = chess.Board(fen)
    candidates = tuple(
        AnalysisCandidate(
            rank=rank,
            score_kind="cp",
            score_value=rank,
            wdl_wins=300,
            wdl_draws=500,
            wdl_losses=200,
            pv_uci=(move.uci(),),
            depth=12,
            seldepth=16,
            nodes=profile.node_budget,
            engine_time_ms=2,
        )
        for rank, move in enumerate(list(board.legal_moves)[:5], 1)
    )
    return AnalysisResult(
        fen=fen,
        profile=profile,
        candidates=candidates,
        terminal_kind=None,
        completed_at=completed_at(),
        wall_time_ms=2,
    )
