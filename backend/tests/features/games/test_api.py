from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from backend.app.dependencies import (
    REBUILT_DATABASE_PATH_ENV,
    get_rebuilt_database_path,
)
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games.normalization import normalize_game
from chess_move_trainer.database.games.persistence import GameRepository


ROOT = Path(__file__).parents[4]
TRAINER_UUID = "11111111-1111-4111-8111-111111111111"
OPPONENT_UUID = "99999999-9999-4999-8999-999999999991"
GAME_UUID = "dddddddd-dddd-4ddd-8ddd-ddddddddddd1"


def _database(tmp_path: Path) -> Path:
    database = tmp_path / "games.db"
    create_schema(database)
    raw = {
        "uuid": GAME_UUID,
        "url": "https://www.chess.com/game/live/clean-api",
        "rules": "chess",
        "pgn": (
            '[Event "clean adapter"]\n'
            '[UTCDate "2026.08.01"]\n'
            '[UTCTime "12:00:00"]\n'
            '[EndDate "2026.08.01"]\n'
            '[EndTime "12:30:00"]\n'
            '[Result "*"]\n\n'
            "1. e4 e5 *"
        ),
        "white": {"uuid": TRAINER_UUID, "rating": 1500, "result": "win"},
        "black": {"uuid": OPPONENT_UUID, "rating": 1490, "result": "resigned"},
        "time_control": "300+5",
        "time_class": "blitz",
    }
    normalized = normalize_game(raw, UUID(TRAINER_UUID))
    assert normalized.game is not None, normalized.warning
    GameRepository(database).persist(normalized.game)
    return database


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _use_database(monkeypatch: pytest.MonkeyPatch, database: Path) -> None:
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))


def test_clean_route_uses_rebuilt_path_unknown_fields_and_public_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    database = _database(tmp_path)
    _use_database(monkeypatch, database)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(tmp_path / "legacy.db"))

    response = client.get("/api/games?future_filter=ignored")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "items": [
            {
                "game_uuid": GAME_UUID,
                "source_url": "https://www.chess.com/game/live/clean-api",
                "trainer_color": "white",
                "trainer_chesscom_uuid": TRAINER_UUID,
                "opponent_chesscom_uuid": OPPONENT_UUID,
                "trainer_rating": 1500,
                "opponent_rating": 1490,
                "started_at_utc": "2026-08-01T12:00:00Z",
                "ended_at_utc": "2026-08-01T12:30:00Z",
                "trainer_outcome": "win",
                "termination_reason": "resigned",
                "time_control": "300+5",
                "time_class": "blitz",
                "occurrence_count": 3,
                "length_plies": 2,
                "deepest_opening": None,
                "coverage": {
                    "distinct_position_count": 3,
                    "analyzed_position_count": 0,
                    "preferred_position_count": 0,
                    "analysis_coverage": "none",
                    "preferred_coverage": "none",
                },
            }
        ],
        "page": 1,
        "page_size": 50,
        "total": 1,
        "total_pages": 1,
        "has_next": False,
    }
    assert not {"game_id", "position_id", "opening_id", "route_id"} & set(
        json.dumps(body).split('"')
    )


def test_game_detail_returns_metadata_pgn_ordered_fens_and_public_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    database = _database(tmp_path)
    _use_database(monkeypatch, database)

    response = client.get(f"/api/games/{GAME_UUID}?future_filter=ignored")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "game_uuid": GAME_UUID,
        "source_url": "https://www.chess.com/game/live/clean-api",
        "original_pgn": (
            '[Event "clean adapter"]\n'
            '[UTCDate "2026.08.01"]\n'
            '[UTCTime "12:00:00"]\n'
            '[EndDate "2026.08.01"]\n'
            '[EndTime "12:30:00"]\n'
            '[Result "*"]\n\n'
            "1. e4 e5 *"
        ),
        "trainer_color": "white",
        "trainer_chesscom_uuid": TRAINER_UUID,
        "opponent_chesscom_uuid": OPPONENT_UUID,
        "trainer_rating": 1500,
        "opponent_rating": 1490,
        "started_at_utc": "2026-08-01T12:00:00Z",
        "ended_at_utc": "2026-08-01T12:30:00Z",
        "trainer_outcome": "win",
        "termination_reason": "resigned",
        "time_control": "300+5",
        "time_class": "blitz",
        "occurrences": [
            {
                "ply": 0,
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "move_uci": "e2e4",
            },
            {
                "ply": 1,
                "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
                "move_uci": "e7e5",
            },
            {
                "ply": 2,
                "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
                "move_uci": None,
            },
        ],
    }
    assert not {"game_id", "position_id", "opening_id", "route_id"} & set(
        json.dumps(body).split('"')
    )


def test_game_detail_invalid_uuid_and_missing_game_use_typed_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    _use_database(monkeypatch, _database(tmp_path))

    invalid = client.get("/api/games/not-a-uuid")
    assert invalid.status_code == 422

    missing = client.get("/api/games/00000000-0000-4000-8000-000000000000")
    assert missing.status_code == 404
    assert missing.json() == {"code": "game_not_found", "message": "Game not found"}


@pytest.mark.parametrize(
    "query",
    (
        "trainer_color=purple",
        "opening_key=C20:King%27s%20Pawn%20Game",
        "opening_match=reached",
        "page_size=101",
    ),
)
def test_invalid_known_values_and_combinations_use_typed_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
    query: str,
) -> None:
    _use_database(monkeypatch, _database(tmp_path))

    response = client.get(f"/api/games?{query}")

    assert response.status_code == 422
    assert response.json() == {"code": "invalid_filter", "message": "Invalid game filter"}


def test_clean_read_is_read_only_and_no_sidecars_remain(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    database = _database(tmp_path)
    _use_database(monkeypatch, database)
    before = database.read_bytes()

    response = client.get("/api/games?page_size=1")

    assert response.status_code == 200
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("games.db-*"))


def test_game_detail_is_read_only_and_no_sidecars_remain(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    database = _database(tmp_path)
    _use_database(monkeypatch, database)
    before = database.read_bytes()

    response = client.get(f"/api/games/{GAME_UUID}")

    assert response.status_code == 200
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("games.db-*"))


def test_missing_or_incompatible_clean_data_is_503_without_target_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    missing = tmp_path / "missing.db"
    _use_database(monkeypatch, missing)
    missing_response = client.get("/api/games")
    assert missing_response.status_code == 503
    assert missing_response.json() == {
        "code": "games_unavailable",
        "message": "Games unavailable",
    }
    assert not missing.exists()

    missing_detail = client.get(f"/api/games/{GAME_UUID}")
    assert missing_detail.status_code == 503
    assert missing_detail.json() == {
        "code": "games_unavailable",
        "message": "Games unavailable",
    }
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE not_schema_v1 (value TEXT)")
    before = incompatible.read_bytes()
    _use_database(monkeypatch, incompatible)
    incompatible_response = client.get("/api/games")
    assert incompatible_response.status_code == 503
    assert incompatible_response.json()["code"] == "games_unavailable"
    assert incompatible.read_bytes() == before

    _use_database(monkeypatch, incompatible)
    incompatible_detail = client.get(f"/api/games/{GAME_UUID}")
    assert incompatible_detail.status_code == 503
    assert incompatible_detail.json()["code"] == "games_unavailable"


def test_unexpected_failures_are_safe_and_legacy_route_remains_registered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    import backend.app.features.games.router as router_module

    _use_database(monkeypatch, _database(tmp_path))

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("private failure details")

    monkeypatch.setattr(router_module, "search_games", fail)
    response = client.get("/api/games")

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to load games",
    }

    def fail_detail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("private detail failure")

    monkeypatch.setattr(router_module, "read_game", fail_detail)
    detail_response = client.get(f"/api/games/{GAME_UUID}")
    assert detail_response.status_code == 500
    assert detail_response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to load game",
    }
    routes = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert "/api/games" in routes
    assert "/api/games/{game_uuid}" in routes
    assert "/api/games/{game_uuid}/positions" not in routes


def test_default_dependency_is_the_clean_rebuilt_database_and_real_call_is_bounded(
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    monkeypatch.delenv(REBUILT_DATABASE_PATH_ENV, raising=False)
    monkeypatch.delenv("CHESS_DATABASE_PATH", raising=False)
    monkeypatch.chdir(ROOT)

    assert get_rebuilt_database_path() == Path("data/database/chess.db")
    response = client.get("/api/games?page_size=1")

    assert response.status_code == 200
    assert response.json()["page_size"] == 1
    assert len(response.json()["items"]) <= 1
    if response.json()["items"]:
        detail = client.get(f"/api/games/{response.json()['items'][0]['game_uuid']}")
        assert detail.status_code == 200
        assert detail.json()["game_uuid"] == response.json()["items"][0]["game_uuid"]
