from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

import backend.app.features.move_response_distribution.router as router_module

from .conftest import (
    AFTER_E4_FEN,
    COUNTER_FEN,
    START_FEN,
    UNKNOWN_FEN,
    create_distribution_database,
)


def _get(client: TestClient, fen: str = START_FEN, color: str = "white"):
    return client.get("/api/move-response-distribution", params={"fen": fen, "color": color})


def test_white_response_distribution_returns_complete_normalized_ranked_replies(
    api_context,
) -> None:
    client, _database = api_context

    response = _get(client)

    assert response.status_code == 200
    assert response.json() == {
        "fen": START_FEN,
        "color": "white",
        "matching_game_count": 4,
        "replies": [
            {
                "rank": 1,
                "child_uci": "d2d4",
                "san": "d4",
                "distinct_game_count": 3,
                "opening_name": None,
            },
            {
                "rank": 2,
                "child_uci": "e2e4",
                "san": "e4",
                "distinct_game_count": 3,
                "opening_name": None,
            },
            {
                "rank": 3,
                "child_uci": "c2c4",
                "san": "c4",
                "distinct_game_count": 1,
                "opening_name": None,
            },
            {
                "rank": 4,
                "child_uci": "g1f3",
                "san": "Nf3",
                "distinct_game_count": 0,
                "opening_name": None,
            },
        ],
    }


def test_black_selected_color_returns_only_black_branches(api_context) -> None:
    client, _database = api_context

    response = _get(client, color="black")

    assert response.status_code == 200
    assert response.json() == {
        "fen": START_FEN,
        "color": "black",
        "matching_game_count": 2,
        "replies": [
            {
                "rank": 1,
                "child_uci": "c2c4",
                "san": "c4",
                "distinct_game_count": 2,
                "opening_name": None,
            },
            {
                "rank": 2,
                "child_uci": "e2e4",
                "san": "e4",
                "distinct_game_count": 2,
                "opening_name": None,
            },
        ],
    }


def test_full_fen_counters_do_not_change_the_four_field_identity(api_context) -> None:
    client, _database = api_context

    response = _get(client, fen=COUNTER_FEN)

    assert response.status_code == 200
    assert response.json()["fen"] == COUNTER_FEN
    assert response.json()["matching_game_count"] == 4
    assert response.json()["replies"] == _get(client).json()["replies"]


def test_repeated_parent_counts_are_distinct_per_child_not_globally_deduplicated(
    api_context,
) -> None:
    client, _database = api_context

    replies = _get(client).json()["replies"]

    assert [(reply["child_uci"], reply["distinct_game_count"]) for reply in replies[:2]] == [
        ("d2d4", 3),
        ("e2e4", 3),
    ]
    assert sum(reply["distinct_game_count"] for reply in replies) == 7
    assert _get(client).json()["matching_game_count"] == 4


def test_zero_matching_games_is_successful_empty_data(api_context) -> None:
    client, _database = api_context

    response = _get(client, fen=UNKNOWN_FEN, color="black")

    assert response.status_code == 200
    assert response.json() == {
        "fen": UNKNOWN_FEN,
        "color": "black",
        "matching_game_count": 0,
        "replies": [],
    }


def test_zero_replies_with_matching_games_is_successful_data(api_context) -> None:
    client, _database = api_context

    response = _get(client, fen=AFTER_E4_FEN, color="black")

    assert response.status_code == 200
    assert response.json() == {
        "fen": AFTER_E4_FEN,
        "color": "black",
        "matching_game_count": 2,
        "replies": [],
    }


def test_invalid_fen_and_color_use_strict_error_envelopes(api_context) -> None:
    client, _database = api_context

    invalid_fen = _get(client, fen="not a fen")
    invalid_color = _get(client, color="green")

    assert invalid_fen.status_code == 422
    assert invalid_fen.json() == {"code": "invalid_fen", "message": "FEN is invalid"}
    assert invalid_color.status_code == 422
    assert invalid_color.json() == {
        "code": "invalid_color",
        "message": "color must be 'white' or 'black'",
    }


def test_missing_database_is_unavailable_and_not_created(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    from backend.app.main import app

    response = _get(TestClient(app))

    assert response.status_code == 503
    assert response.json() == {
        "code": "move_response_distribution_unavailable",
        "message": "Move response distribution unavailable",
    }
    assert not database.exists()


def test_incompatible_recurrence_schema_is_unavailable_without_change(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database = tmp_path / "incompatible.db"
    create_distribution_database(database, schema_version=2)
    before = database.read_bytes()
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    from backend.app.main import app

    response = _get(TestClient(app))

    assert response.status_code == 503
    assert response.json() == {
        "code": "move_response_distribution_unavailable",
        "message": "Move response distribution unavailable",
    }
    assert database.read_bytes() == before


def test_malformed_accepted_branch_is_unavailable(
    api_context,
) -> None:
    client, database = api_context
    with sqlite3.connect(database) as db:
        db.execute(
            "INSERT INTO opening_recurrence_branch_projection VALUES "
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "accepted-manifest",
                1,
                *START_FEN.split(" ")[:4],
                "move",
                "not-a-uci-move",
                "white",
                1,
            ),
        )

    response = _get(client)

    assert response.status_code == 503
    assert response.json()["code"] == "move_response_distribution_unavailable"


def test_unexpected_failure_is_safe_and_contains_no_internal_message(
    api_context,
    monkeypatch,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "get_move_response_distribution", fail)
    response = _get(client)

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to serve move response distribution",
    }
    assert "database secret" not in response.text


def test_request_is_read_only_and_does_not_create_sidecars(api_context) -> None:
    client, database = api_context
    before_digest = hashlib.sha256(database.read_bytes()).digest()
    with sqlite3.connect(database) as db:
        before_tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()

    response = _get(client)

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
