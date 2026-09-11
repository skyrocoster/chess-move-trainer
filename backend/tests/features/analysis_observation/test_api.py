from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.routing import APIRoute

import backend.app.features.analysis_observation.router as router_module
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV, get_rebuilt_database_path
from backend.app.main import app

from .conftest import (
    TARGET_CANONICAL_FEN,
    TARGET_FEN,
    TARGET_WITH_COUNTERS,
    UNSEEN_CANONICAL_FEN,
    UNSEEN_FEN,
    _complete_analysis_result,
    create_insight_database,
)


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


def _queue(database: Path, state: str) -> None:
    position_id = _target_position_id(database)
    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM derived_analysis_queue")
        connection.execute(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id, daq_requested_quality, daq_state,
                daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            ) VALUES (?, 'browser', ?, '2026-09-09T00:00:00Z', ?, ?)
            """,
            (
                position_id,
                state,
                None if state == "queued" else "2026-09-09T00:01:00Z",
                None if state == "queued" else "claim-token",
            ),
        )


def _remove_result(database: Path) -> None:
    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM derived_analysis_line")
        connection.execute("DELETE FROM derived_analysis_result")


def test_finished_analysis_returns_full_detail_and_ignores_unknown_filters(api_context) -> None:
    client, _database = api_context

    response = client.get(
        "/api/analysis",
        params={"fen": TARGET_WITH_COUNTERS, "future_filter": "ignored"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": TARGET_CANONICAL_FEN,
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
                },
                {
                    "rank": 2,
                    "score_kind": "cp",
                    "score_value": 36,
                    "wdl_wins": 450,
                    "wdl_draws": 300,
                    "wdl_losses": 250,
                    "pv_uci": ["g1h3"],
                    "depth": 22,
                },
                {
                    "rank": 3,
                    "score_kind": "cp",
                    "score_value": 37,
                    "wdl_wins": 450,
                    "wdl_draws": 300,
                    "wdl_losses": 250,
                    "pv_uci": ["g1f3"],
                    "depth": 22,
                },
                {
                    "rank": 4,
                    "score_kind": "cp",
                    "score_value": 38,
                    "wdl_wins": 450,
                    "wdl_draws": 300,
                    "wdl_losses": 250,
                    "pv_uci": ["g1e2"],
                    "depth": 22,
                },
                {
                    "rank": 5,
                    "score_kind": "cp",
                    "score_value": 39,
                    "wdl_wins": 450,
                    "wdl_draws": 300,
                    "wdl_losses": 250,
                    "pv_uci": ["f1a6"],
                    "depth": 22,
                },
            ],
        },
    }
    assert set(response.json()) == {"fen", "state", "result"}
    assert "position_id" not in json.dumps(response.json())
    assert "queue" not in json.dumps(response.json()).lower()


@pytest.mark.parametrize("params", ({}, {"fen": "not a fen"}))
def test_missing_or_bad_position_gives_clear_error(client, params: dict[str, str]) -> None:
    response = client.get("/api/analysis", params=params)

    assert response.status_code == 422
    if params:
        assert response.json() == {"code": "invalid_fen", "message": "FEN is invalid"}


def test_unseen_position_returns_empty_result_without_changing_database(api_context) -> None:
    client, database = api_context
    before = database.read_bytes()

    response = client.get("/api/analysis", params={"fen": UNSEEN_FEN})

    assert response.status_code == 200
    assert response.json() == {
        "fen": UNSEEN_CANONICAL_FEN,
        "state": "not_requested",
        "result": None,
    }
    assert database.read_bytes() == before
    assert not list(database.parent.glob(database.name + "-*"))


def test_queued_and_running_show_before_ready_and_keep_old_result(api_context) -> None:
    client, database = api_context

    _queue(database, "queued")
    queued = client.get("/api/analysis", params={"fen": TARGET_FEN})
    assert queued.status_code == 200
    assert queued.json()["state"] == "queued"
    assert queued.json()["result"] is not None

    _queue(database, "running")
    running = client.get("/api/analysis", params={"fen": TARGET_FEN})
    assert running.status_code == 200
    assert running.json()["state"] == "running"
    assert running.json()["result"] is not None


@pytest.mark.parametrize("state", ("queued", "running"))
def test_queued_and_running_show_even_without_result(api_context, state: str) -> None:
    client, database = api_context
    _remove_result(database)
    _queue(database, state)

    response = client.get("/api/analysis", params={"fen": TARGET_FEN})

    assert response.status_code == 200
    assert response.json() == {
        "fen": TARGET_CANONICAL_FEN,
        "state": state,
        "result": None,
    }


def test_injected_database_is_used_when_configured(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_insight_database(tmp_path / "injected.db")
    _complete_analysis_result(injected)
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = client.get("/api/analysis", params={"fen": TARGET_FEN})

    assert response.status_code == 200
    assert response.json()["fen"] == TARGET_CANONICAL_FEN


def test_missing_or_broken_database_gives_unavailable_without_creating_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = client.get("/api/analysis", params={"fen": TARGET_FEN})

    assert missing_response.status_code == 503
    assert missing_response.json() == {
        "code": "analysis_unavailable",
        "message": "Analysis data unavailable",
    }
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    before = incompatible.read_bytes()
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(incompatible))
    incompatible_response = client.get("/api/analysis", params={"fen": TARGET_FEN})

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "analysis_unavailable",
        "message": "Analysis data unavailable",
    }
    assert incompatible.read_bytes() == before


def test_unexpected_failures_stay_safe_without_leaking_details(api_context, monkeypatch) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "read_analysis_observation", fail)
    response = client.get("/api/analysis", params={"fen": TARGET_FEN})

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to observe analysis",
    }
    assert "database secret" not in response.text


def test_analysis_route_uses_expected_name_and_old_evaluation_stays_gone() -> None:
    routes = {
        route.path: route
        for route in app.routes
        if isinstance(route, APIRoute)
    }

    assert "/api/analysis" in routes
    assert "/api/evaluation" not in routes
    assert routes["/api/analysis"].methods == {"GET"}
    assert routes["/api/analysis"].operation_id == "getAnalysis"
