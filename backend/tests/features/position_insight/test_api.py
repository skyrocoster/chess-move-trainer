from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.routing import APIRoute

import backend.app.features.position_insight.router as router_module
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV, get_rebuilt_database_path
from backend.app.main import app

from .conftest import (
    STARTING_FEN,
    TARGET_CANONICAL_FEN,
    TARGET_FEN,
    TARGET_WITH_COUNTERS,
    UNSEEN_CANONICAL_FEN,
    UNSEEN_FEN,
    create_insight_database,
)


def _params(fen: str = TARGET_FEN, trainer_color: str = "white", as_of: str = "2026-01-15") -> dict[str, str]:
    return {"fen": fen, "trainer_color": trainer_color, "as_of": as_of}


def _target_position_id(database: Path) -> int:
    placement, side_to_move, castling, en_passant = TARGET_FEN.split()[:4]
    with sqlite3.connect(database) as connection:
        return connection.execute(
            """
            SELECT dp_position_id
            FROM derived_position
            WHERE dp_placement = ?
              AND dp_side_to_move = ?
              AND dp_castling_rights = ?
              AND dp_legal_en_passant = ?
            """,
            (placement, side_to_move, castling, en_passant),
        ).fetchone()[0]


def test_success_returns_exact_public_position_insight_and_ignores_unknown_queries(
    api_context,
) -> None:
    client, _database = api_context

    response = client.get(
        "/api/positions/insight",
        params={**_params(fen=TARGET_WITH_COUNTERS), "future_filter": "ignored"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": TARGET_CANONICAL_FEN,
        "trainer_color": "white",
        "as_of": "2026-01-15",
        "opening": {
            "key": "C20:King's Pawn Game",
            "eco": "C20",
            "name": "King's Pawn Game",
            "ply": 2,
            "match": "transposition",
        },
        "experience": {"distinct_game_count": 2, "occurrence_count": 3},
        "observed_moves": [
            {"move_uci": "a2a3", "distinct_game_count": 1, "occurrence_count": 2},
            {"move_uci": "b2b3", "distinct_game_count": 1, "occurrence_count": 1},
        ],
        "analysis": {
            "state": "ready",
            "result": {
                "quality": "tool",
                "configuration_version": 7,
                "settings": {"Hash": 16},
                "engine_name": "Stockfish",
                "engine_version": "18",
                "terminal_kind": None,
                "lines": [
                    {
                        "rank": 1,
                        "score_kind": "cp",
                        "score_value": 34,
                        "wdl_wins": 450,
                        "wdl_draws": 300,
                        "wdl_losses": 250,
                        "pv_uci": ["a2a3"],
                        "depth": 22,
                    }
                ],
            },
        },
        "preference": {"kind": "move", "uci": "a2a3"},
    }
    assert "position_id" not in json.dumps(response.json())
    assert "route_id" not in json.dumps(response.json())


@pytest.mark.parametrize(
    "params",
    (
        {},
        {"trainer_color": "white", "as_of": "2026-01-15"},
        {"fen": TARGET_FEN, "as_of": "2026-01-15"},
        {"fen": TARGET_FEN, "trainer_color": "white"},
    ),
)
def test_required_query_fields_are_required(api_context, params: dict[str, str]) -> None:
    client, _database = api_context

    response = client.get("/api/positions/insight", params=params)

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("params", "error"),
    (
        ({**_params(), "fen": "not a fen"}, {"code": "invalid_fen", "message": "FEN is invalid"}),
        (
            {**_params(), "trainer_color": "purple"},
            {
                "code": "invalid_trainer_color",
                "message": "trainer_color must be 'white' or 'black'",
            },
        ),
        (
            {**_params(), "as_of": "2026-9-9"},
            {
                "code": "invalid_as_of",
                "message": "as_of must be a literal YYYY-MM-DD date",
            },
        ),
        (
            {**_params(), "as_of": "2026-02-30"},
            {
                "code": "invalid_as_of",
                "message": "as_of must be a literal YYYY-MM-DD date",
            },
        ),
    ),
)
def test_invalid_values_use_strict_typed_422_errors(api_context, params, error) -> None:
    client, _database = api_context

    response = client.get("/api/positions/insight", params=params)

    assert response.status_code == 422
    assert response.json() == error


def test_unseen_legal_position_is_sparse_success_and_read_only(api_context) -> None:
    client, database = api_context
    before = database.read_bytes()

    response = client.get("/api/positions/insight", params=_params(UNSEEN_FEN, "black", "2026-09-09"))

    assert response.status_code == 200
    assert response.json() == {
        "fen": UNSEEN_CANONICAL_FEN,
        "trainer_color": "black",
        "as_of": "2026-09-09",
        "opening": None,
        "experience": {"distinct_game_count": 0, "occurrence_count": 0},
        "observed_moves": [],
        "analysis": {"state": "not_requested", "result": None},
        "preference": {"kind": "unconfigured"},
    }
    assert database.read_bytes() == before
    assert not list(database.parent.glob(database.name + "-*"))
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1


def test_analysis_queue_precedence_and_date_resolved_preference_are_public(api_context) -> None:
    client, database = api_context
    with sqlite3.connect(database) as connection:
        position_id = _target_position_id(database)
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', 'queued', '2026-09-09T00:00:00Z', NULL, NULL)
            """,
            (position_id,),
        )

    queued = client.get(
        "/api/positions/insight",
        params=_params(as_of="2026-02-15"),
    )

    assert queued.status_code == 200
    assert queued.json()["analysis"] == {
        "state": "queued",
        "result": queued.json()["analysis"]["result"],
    }
    assert queued.json()["preference"] == {"kind": "no_preference"}

    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM derived_analysis_queue")
        position_id = _target_position_id(database)
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', 'running', '2026-09-09T00:00:00Z',
                      '2026-09-09T00:01:00Z', 'claim-token')
            """,
            (position_id,),
        )

    running = client.get("/api/positions/insight", params=_params(as_of="2026-03-01"))

    assert running.status_code == 200
    assert running.json()["analysis"]["state"] == "running"
    assert running.json()["analysis"]["result"] is not None
    assert running.json()["preference"] == {"kind": "move", "uci": "b2b3"}


def test_clean_dependency_override_selects_the_injected_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_insight_database(tmp_path / "injected.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = client.get("/api/positions/insight", params=_params())

    assert response.status_code == 200
    assert response.json()["fen"] == TARGET_CANONICAL_FEN


def test_missing_or_incompatible_data_is_typed_503_without_target_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = client.get("/api/positions/insight", params=_params())

    assert missing_response.status_code == 503
    assert missing_response.json() == {
        "code": "position_insight_unavailable",
        "message": "Position insight unavailable",
    }
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    before = incompatible.read_bytes()
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(incompatible))
    incompatible_response = client.get("/api/positions/insight", params=_params())

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "position_insight_unavailable",
        "message": "Position insight unavailable",
    }
    assert incompatible.read_bytes() == before


def test_unexpected_failures_are_safe_and_do_not_leak_internal_messages(api_context, monkeypatch) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "read_position_insight", fail)
    response = client.get("/api/positions/insight", params=_params())

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to serve position insight",
    }
    assert "database secret" not in response.text


def test_new_clean_route_coexists_with_accepted_clean_and_legacy_routes() -> None:
    routes = {route.path for route in app.routes if isinstance(route, APIRoute)}

    assert "/api/positions/insight" in routes
    assert "/api/games" in routes
    assert "/api/games/{game_uuid}" in routes
    assert "/api/games/{game_uuid}/positions" in routes
    assert "/api/openings" in routes
    assert "/api/openings/{opening_key}" in routes
    assert "/api/position-context" in routes


def test_position_insight_route_has_the_settled_operation_id() -> None:
    route = next(
        route
        for route in app.routes
        if isinstance(route, APIRoute) and route.path == "/api/positions/insight"
    )

    assert route.operation_id == "getPositionInsight"
