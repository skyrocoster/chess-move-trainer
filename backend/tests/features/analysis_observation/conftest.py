from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import chess
import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from backend.tests.features.position_insight.conftest import (
    STARTING_FEN,
    TARGET_CANONICAL_FEN,
    TARGET_FEN,
    TARGET_WITH_COUNTERS,
    UNSEEN_CANONICAL_FEN,
    UNSEEN_FEN,
    create_insight_database,
)


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> tuple[TestClient, Path]:
    database = create_insight_database(tmp_path / "analysis-observation.db")
    _complete_analysis_result(database)
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    return client, database


def _complete_analysis_result(database: Path) -> None:
    """Extend the shared position-insight fixture to Stage 1's complete result."""

    board = chess.Board(TARGET_FEN)
    additional_moves = ("g1h3", "g1f3", "g1e2", "f1a6")
    with sqlite3.connect(database) as connection:
        position_id = connection.execute(
            """
            SELECT dp_position_id
            FROM derived_position
            WHERE dp_placement = ?
              AND dp_side_to_move = ?
              AND dp_castling_rights = ?
              AND dp_legal_en_passant = ?
            """,
            tuple(TARGET_FEN.split()[:4]),
        ).fetchone()[0]
        legal_moves = {move.uci() for move in board.legal_moves}
        assert set(additional_moves).issubset(legal_moves)
        connection.executemany(
            """
            INSERT INTO derived_analysis_line (
                derived_analysis_result_id, dal_rank, dal_score_kind, dal_score_value,
                dal_wdl_wins, dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json, dal_depth
            ) VALUES (?, ?, 'cp', ?, 450, 300, 250, ?, 22)
            """,
            (
                (position_id, rank, 34 + rank, json.dumps([move]))
                for rank, move in enumerate(additional_moves, 2)
            ),
        )


__all__ = [
    "STARTING_FEN",
    "TARGET_CANONICAL_FEN",
    "TARGET_FEN",
    "TARGET_WITH_COUNTERS",
    "UNSEEN_CANONICAL_FEN",
    "UNSEEN_FEN",
]
