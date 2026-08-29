from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from .conftest import AFTER_E4_FEN, COUNTER_FEN, START_FEN, UNKNOWN_FEN, create_context_database


def test_valid_context_returns_overall_and_distinct_game_color_counts(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _ = api_context

    response = client.get("/api/position-context", params={"fen": START_FEN})

    assert response.status_code == 200
    assert response.json() == {
        "fen": START_FEN,
        "overall_exists": True,
        "white_count": 2,
        "black_count": 1,
    }


def test_full_fen_counters_do_not_change_the_four_field_identity(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _ = api_context

    response = client.get("/api/position-context", params={"fen": COUNTER_FEN})

    assert response.status_code == 200
    assert response.json() == {
        "fen": COUNTER_FEN,
        "overall_exists": True,
        "white_count": 2,
        "black_count": 1,
    }


def test_zero_personal_color_count_is_distinct_from_absent_overall_position(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _ = api_context

    seen_response = client.get("/api/position-context", params={"fen": AFTER_E4_FEN})
    absent_response = client.get("/api/position-context", params={"fen": UNKNOWN_FEN})

    assert seen_response.status_code == 200
    assert seen_response.json() == {
        "fen": AFTER_E4_FEN,
        "overall_exists": True,
        "white_count": 2,
        "black_count": 0,
    }
    assert absent_response.status_code == 200
    assert absent_response.json() == {
        "fen": UNKNOWN_FEN,
        "overall_exists": False,
        "white_count": 0,
        "black_count": 0,
    }


def test_invalid_fen_returns_safe_validation_error(
    api_context: tuple[TestClient, Path],
) -> None:
    client, _ = api_context

    response = client.get(
        "/api/position-context",
        params={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"},
    )

    assert response.status_code == 422
    assert response.json() == {"code": "invalid_fen", "message": "FEN is invalid"}


def test_missing_database_returns_safe_unavailable_error(
    api_context: tuple[TestClient, Path],
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _ = api_context
    missing = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(missing))

    response = client.get("/api/position-context", params={"fen": START_FEN})

    assert response.status_code == 503
    assert response.json() == {
        "code": "position_context_unavailable",
        "message": "Position context unavailable",
    }
    assert not missing.exists()


def test_incompatible_database_returns_safe_unavailable_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database = tmp_path / "incompatible.db"
    create_context_database(database, schema_version=2)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    from backend.app.main import app

    response = TestClient(app).get("/api/position-context", params={"fen": START_FEN})

    assert response.status_code == 503
    assert response.json() == {
        "code": "position_context_unavailable",
        "message": "Position context unavailable",
    }


def test_request_is_read_only_and_does_not_create_sidecars(
    api_context: tuple[TestClient, Path],
) -> None:
    client, database = api_context
    before_digest = hashlib.sha256(database.read_bytes()).digest()
    with sqlite3.connect(database) as db:
        before_tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()

    response = client.get("/api/position-context", params={"fen": START_FEN})

    assert response.status_code == 200
    assert hashlib.sha256(database.read_bytes()).digest() == before_digest
    with sqlite3.connect(database) as db:
        after_tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    assert after_tables == before_tables
    assert not database.with_name(database.name + "-wal").exists()
    assert not database.with_name(database.name + "-shm").exists()
    assert not database.with_name(database.name + "-journal").exists()
