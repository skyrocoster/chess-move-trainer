from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
COUNTER_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42"
UNSEEN_FEN = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
EP_FEN = "rnbqkbnr/1pp1pppp/p7/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"


def create_preferred_moves_database(path: Path) -> Path:
    create_schema(path)
    position_id = PositionRepository(path).resolve_fen(START_FEN)
    with sqlite3.connect(path) as connection:
        connection.executemany(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_effective_until, dpm_move_uci
            ) VALUES (?, ?, ?, ?)
            """,
            (
                (position_id, "2026-01-01", "2026-02-01", "e2e4"),
                (position_id, "2026-02-01", "2026-03-01", None),
                (position_id, "2026-04-01", None, "d2d4"),
            ),
        )
    return path


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    selected = TestClient(app)
    yield selected
    app.dependency_overrides.clear()


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> tuple[TestClient, Path]:
    database = create_preferred_moves_database(tmp_path / "preferred-moves.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    return client, database
