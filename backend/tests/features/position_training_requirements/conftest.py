from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import (
    REBUILT_DATABASE_PATH_ENV,
    TRAINING_CREDIT_HALF_LIFE_DAYS_ENV,
    TRAINING_TARGET_SUCCESS_RATE_ENV,
)
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository


TARGET_FEN = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
TARGET_CANONICAL_FEN = " ".join((*TARGET_FEN.split()[:4], "0", "1"))


def _game(connection: sqlite3.Connection, game_id: int, color: str, started: str) -> None:
    connection.execute(
        """
        INSERT INTO datasource_game (
            dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
            dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            game_id,
            f"training-api-game-{game_id}",
            f"https://example.test/training-api-game-{game_id}",
            "[Result \"*\"]\n\n*",
            color,
            f"trainer-{game_id}",
            started,
        ),
    )


def _occurrence(
    connection: sqlite3.Connection,
    game_id: int,
    position_id: int,
    ply: int,
    move_uci: str,
) -> None:
    connection.execute(
        """
        INSERT INTO derived_game_position (
            datasource_game_id, dgp_ply, derived_position_id,
            dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
        ) VALUES (?, ?, ?, ?, 0, 1)
        """,
        (game_id, ply, position_id, move_uci),
    )


def create_training_database(path: Path) -> tuple[Path, int]:
    create_schema(path)
    position_id = PositionRepository(path).resolve_fen(TARGET_FEN)
    with sqlite3.connect(path) as connection:
        _game(connection, 1, "white", "2026-01-01T00:00:00Z")
        _game(connection, 2, "white", "2026-01-02T00:00:00Z")
        _game(connection, 3, "black", "2026-01-03T00:00:00Z")
        _occurrence(connection, 1, position_id, 1, "a2a3")
        _occurrence(connection, 2, position_id, 1, "b2b3")
        _occurrence(connection, 3, position_id, 1, "a2a3")
        connection.execute(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_move_uci
            ) VALUES (?, '2026-01-01', 'a2a3')
            """,
            (position_id,),
        )
        opening_id = connection.execute(
            """
            INSERT INTO datasource_opening (do_eco, do_name)
            VALUES ('A00', 'Training Opening')
            RETURNING do_opening_id
            """
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?)
            """,
            (opening_id, position_id),
        )
    return path, position_id


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
) -> tuple[TestClient, Path, int]:
    database, position_id = create_training_database(tmp_path / "position-training.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    monkeypatch.delenv(TRAINING_TARGET_SUCCESS_RATE_ENV, raising=False)
    monkeypatch.delenv(TRAINING_CREDIT_HALF_LIFE_DAYS_ENV, raising=False)
    return client, database, position_id
