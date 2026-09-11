from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.routing import APIRoute

import backend.app.features.analysis_requests.router as router_module
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV, get_rebuilt_database_path
from backend.app.main import app
from backend.tests.features.analysis_observation.conftest import (
    STARTING_FEN,
    TARGET_CANONICAL_FEN,
    TARGET_FEN,
    TARGET_WITH_COUNTERS,
)
from chess_move_trainer.database.stockfish import QueueService


def _post(client, body: dict[str, object]):
    return client.post("/api/analysis-requests", json=body)


def _position_id(database: Path, fen: str) -> int:
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
            tuple(fen.split()[:4]),
        ).fetchone()[0]


def _queue_row(database: Path, position_id: int) -> tuple[object, ...] | None:
    with sqlite3.connect(database) as connection:
        return connection.execute(
            """
            SELECT daq_requested_quality, daq_state, daq_requested_at_utc,
                   daq_claimed_at_utc, daq_claim_token
            FROM derived_analysis_queue
            WHERE derived_position_id = ?
            """,
            (position_id,),
        ).fetchone()


def test_finished_analysis_is_reused_and_ignores_unknown_fields(
    api_context,
) -> None:
    client, _database = api_context

    get_response = client.get(
        "/api/analysis",
        params={"fen": TARGET_WITH_COUNTERS},
    )
    post_response = _post(
        client,
        {"fen": TARGET_WITH_COUNTERS, "future_filter": "ignored"},
    )

    assert get_response.status_code == 200
    assert post_response.status_code == 200
    assert post_response.json() == get_response.json()
    assert set(post_response.json()) == {"fen", "state", "result"}
    assert "position_id" not in json.dumps(post_response.json())
    assert "queue" not in json.dumps(post_response.json()).lower()


def test_first_request_queues_work_and_read_back_matches(
    api_context,
) -> None:
    client, database = api_context

    response = _post(client, {"fen": STARTING_FEN})

    assert response.status_code == 202
    assert response.json() == {
        "fen": STARTING_FEN,
        "state": "queued",
        "result": None,
    }
    observed = client.get("/api/analysis", params={"fen": STARTING_FEN})
    assert observed.status_code == 200
    assert observed.json() == response.json()
    position_id = _position_id(database, STARTING_FEN)
    assert _queue_row(database, position_id)[0] == "browser"


def test_tool_request_queues_but_keeps_old_complete_result(
    api_context,
) -> None:
    client, _database = api_context

    response = _post(client, {"fen": TARGET_FEN, "quality": "tool"})

    assert response.status_code == 202
    assert response.json()["fen"] == TARGET_CANONICAL_FEN
    assert response.json()["state"] == "queued"
    assert response.json()["result"] is not None
    assert response.json()["result"]["quality"] == "tool"


def test_repeat_request_upgrades_quality_without_losing_running_work(
    api_context,
) -> None:
    client, database = api_context

    first = _post(client, {"fen": STARTING_FEN})
    assert first.status_code == 202
    position_id = _position_id(database, STARTING_FEN)
    queue = QueueService(database)
    claim = queue.claim()
    assert claim is not None

    promoted = _post(client, {"fen": STARTING_FEN, "quality": "tool"})
    reused = _post(client, {"fen": STARTING_FEN, "quality": "browser"})

    assert promoted.status_code == 202
    assert promoted.json()["state"] == "running"
    assert reused.status_code == 202
    assert reused.json()["state"] == "running"
    row = _queue_row(database, position_id)
    assert row is not None
    assert row[0:2] == ("tool", "running")
    assert row[3:] == (claim.claimed_at_utc, claim.claim_token)


@pytest.mark.parametrize(
    ("body", "error"),
    (
        (
            {"fen": "not a FEN"},
            {"code": "invalid_fen", "message": "FEN is invalid"},
        ),
        (
            {"fen": STARTING_FEN, "quality": "deep"},
            {"code": "invalid_quality", "message": "Quality is invalid"},
        ),
    ),
)
def test_bad_values_give_clear_error(api_context, body, error) -> None:
    client, _database = api_context

    response = _post(client, body)

    assert response.status_code == 422
    assert response.json() == error


def test_missing_or_wrong_type_fields_give_error(api_context) -> None:
    client, _database = api_context

    missing_fen = _post(client, {"quality": "browser"})
    non_string_fen = _post(client, {"fen": 42})
    non_string_quality = _post(client, {"fen": STARTING_FEN, "quality": 1})

    assert missing_fen.status_code == 422
    assert non_string_fen.status_code == 422
    assert non_string_quality.status_code == 422


def test_missing_or_broken_database_gives_unavailable_without_creating_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = _post(client, {"fen": STARTING_FEN})
    assert missing_response.status_code == 503
    assert missing_response.json() == {
        "code": "analysis_unavailable",
        "message": "Analysis data unavailable",
    }
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(incompatible))
    incompatible_response = _post(client, {"fen": STARTING_FEN})
    assert incompatible_response.status_code == 503
    assert incompatible_response.json()["code"] == "analysis_unavailable"

    malformed = tmp_path / "malformed.db"
    malformed.write_bytes(b"not a SQLite database")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(malformed))
    malformed_response = _post(client, {"fen": STARTING_FEN})
    assert malformed_response.status_code == 503
    assert malformed_response.json()["code"] == "analysis_unavailable"


def test_injected_database_is_used_when_configured(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    from backend.tests.features.analysis_observation.conftest import (
        _complete_analysis_result,
        create_insight_database,
    )

    injected = create_insight_database(tmp_path / "injected.db")
    _complete_analysis_result(injected)
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = _post(client, {"fen": TARGET_FEN})

    assert response.status_code == 200
    assert response.json()["fen"] == TARGET_CANONICAL_FEN


def test_unexpected_failures_stay_safe_without_leaking_details(monkeypatch, api_context) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "request_analysis", fail)
    response = _post(client, {"fen": TARGET_FEN})

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to request analysis",
    }
    assert "database secret" not in response.text


def test_request_route_coexists_with_observation_and_uses_expected_name() -> None:
    routes = {
        (route.path, tuple(sorted(route.methods))): route
        for route in app.routes
        if isinstance(route, APIRoute)
    }

    request_route = routes[("/api/analysis-requests", ("POST",))]
    assert request_route.operation_id == "requestAnalysis"
    assert ("/api/analysis", ("GET",)) in routes
    assert ("/api/evaluation", ("POST",)) not in routes
