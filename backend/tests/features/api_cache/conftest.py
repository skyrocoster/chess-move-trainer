from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.caching import clear_caches
from backend.app.dependencies import (
    REBUILT_DATABASE_PATH_ENV,
    TRAINING_CREDIT_HALF_LIFE_DAYS_ENV,
    TRAINING_TARGET_SUCCESS_RATE_ENV,
)
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository

TARGET_FEN = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
UNSEEN_FEN = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"

TRAINING_PARAMS = {"as_of": "2026-01-15", "training_requirement_gte": -100}
OPENINGS_PARAMS = {"page": 1, "page_size": 50}


@pytest.fixture(autouse=True)
def _isolated_caches():
    clear_caches()
    yield
    clear_caches()


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    selected = TestClient(app)
    yield selected
    app.dependency_overrides.clear()


def create_cache_database(path: Path) -> Path:
    """One small database serving training, openings, and preferred-move writes."""

    create_schema(path)
    target_id = PositionRepository(path).resolve_fen(TARGET_FEN)
    PositionRepository(path).resolve_fen(START_FEN)
    with sqlite3.connect(path) as connection:
        for game_id, color, started in (
            (1, "white", "2026-01-01T00:00:00Z"),
            (2, "white", "2026-01-02T00:00:00Z"),
            (3, "black", "2026-01-03T00:00:00Z"),
        ):
            connection.execute(
                """
                INSERT INTO datasource_game (
                    dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                    dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    game_id,
                    f"00000000-0000-4000-8000-{game_id:012d}",
                    f"https://example.test/cache-api-game-{game_id}",
                    '[Result "*"]\n\n*',
                    color,
                    f"11111111-1111-4111-8111-11111111110{game_id}",
                    started,
                ),
            )
        for game_id, move_uci in ((1, "a2a3"), (2, "b2b3"), (3, "a2a3")):
            connection.execute(
                """
                INSERT INTO derived_game_position (
                    datasource_game_id, dgp_ply, derived_position_id,
                    dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
                ) VALUES (?, 1, ?, ?, 0, 1)
                """,
                (game_id, target_id, move_uci),
            )
        connection.execute(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_move_uci
            ) VALUES (?, '2026-01-01', 'a2a3')
            """,
            (target_id,),
        )
        opening_id = connection.execute(
            """
            INSERT INTO datasource_opening (do_eco, do_name)
            VALUES ('A00', 'Cache Opening')
            RETURNING do_opening_id
            """
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?)
            """,
            (opening_id, target_id),
        )
    return path


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> tuple[TestClient, Path]:
    database = create_cache_database(tmp_path / "api-cache.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    monkeypatch.delenv(TRAINING_TARGET_SUCCESS_RATE_ENV, raising=False)
    monkeypatch.delenv(TRAINING_CREDIT_HALF_LIFE_DAYS_ENV, raising=False)
    return client, database


def count_reader_calls(
    monkeypatch: pytest.MonkeyPatch, module: object, name: str
) -> list[tuple[tuple, dict]]:
    """Wrap one router-level reader so tests can count underlying invocations."""

    original = getattr(module, name)
    calls: list[tuple[tuple, dict]] = []

    def wrapper(*args: object, **kwargs: object):
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(module, name, wrapper)
    return calls
