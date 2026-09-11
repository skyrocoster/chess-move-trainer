from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

import backend.app.features.preferred_moves.router as router_module
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV, get_rebuilt_database_path
from backend.app.main import app

from .conftest import (
    COUNTER_FEN,
    EP_FEN,
    START_FEN,
    UNSEEN_FEN,
    create_preferred_moves_database,
    request_params,
)


def test_known_timeline_returns_full_segments_and_ignores_unknown_filters(api_context) -> None:
    client, _database = api_context

    response = client.get(
        "/api/preferred-moves",
        params={**request_params(fen=COUNTER_FEN), "future_filter": "ignored"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": START_FEN,
        "from": "2026-01-15",
        "until": "2026-05-15",
        "segments": [
            {
                "from": "2026-01-15",
                "until": "2026-02-01",
                "preference": {"kind": "move", "uci": "e2e4"},
            },
            {
                "from": "2026-02-01",
                "until": "2026-03-01",
                "preference": {"kind": "no_preference"},
            },
            {
                "from": "2026-03-01",
                "until": "2026-04-01",
                "preference": {"kind": "unconfigured"},
            },
            {
                "from": "2026-04-01",
                "until": "2026-05-15",
                "preference": {"kind": "move", "uci": "d2d4"},
            },
        ],
    }
    assert set(response.json()) == {"fen", "from", "until", "segments"}
    assert "position_id" not in json.dumps(response.json())
    assert "derived_position_id" not in json.dumps(response.json())


@pytest.mark.parametrize(
    "params",
    (
        {},
        {"fen": START_FEN, "from": "2026-01-01"},
        {"fen": START_FEN, "until": "2026-02-01"},
        {"from": "2026-01-01", "until": "2026-02-01"},
    ),
)
def test_missing_required_fields_gives_error(api_context, params: dict[str, str]) -> None:
    client, _database = api_context

    assert client.get("/api/preferred-moves", params=params).status_code == 422


@pytest.mark.parametrize(
    ("params", "error"),
    (
        (
            {**request_params(), "fen": "not a fen"},
            {"code": "invalid_fen", "message": "FEN is invalid"},
        ),
        (
            {**request_params(), "from": "2026-1-01"},
            {"code": "invalid_from", "message": "from must be a literal YYYY-MM-DD date"},
        ),
        (
            {**request_params(), "from": "2026-02-30"},
            {"code": "invalid_from", "message": "from must be a literal YYYY-MM-DD date"},
        ),
        (
            {**request_params(), "until": "2026-2-01"},
            {"code": "invalid_until", "message": "until must be a literal YYYY-MM-DD date"},
        ),
        (
            {**request_params(), "until": "2026-02-30"},
            {"code": "invalid_until", "message": "until must be a literal YYYY-MM-DD date"},
        ),
        (
            {**request_params(), "from": "2026-03-01", "until": "2026-03-01"},
            {"code": "invalid_window", "message": "from must be earlier than until"},
        ),
    ),
)
def test_bad_values_give_clear_error(api_context, params, error) -> None:
    client, _database = api_context

    response = client.get("/api/preferred-moves", params=params)

    assert response.status_code == 422
    assert response.json() == error


def test_unseen_position_returns_single_unconfigured_segment_without_changing_database(
    api_context,
) -> None:
    client, database = api_context
    before = database.read_bytes()

    response = client.get(
        "/api/preferred-moves",
        params=request_params(UNSEEN_FEN, "2026-01-01", "2026-01-03"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": " ".join((*UNSEEN_FEN.split()[:4], "0", "1")),
        "from": "2026-01-01",
        "until": "2026-01-03",
        "segments": [
            {
                "from": "2026-01-01",
                "until": "2026-01-03",
                "preference": {"kind": "unconfigured"},
            }
        ],
    }
    assert database.read_bytes() == before
    assert not list(database.parent.glob(database.name + "-*"))
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone() == (1,)


def test_empty_schedule_and_en_passant_position_returns_unconfigured(api_context) -> None:
    client, database = api_context
    empty = client.get(
        "/api/preferred-moves",
        params=request_params(EP_FEN, "2026-01-01", "2026-01-03"),
    )

    assert empty.status_code == 200
    assert empty.json() == {
        "fen": " ".join((*EP_FEN.split()[:4], "0", "1")),
        "from": "2026-01-01",
        "until": "2026-01-03",
        "segments": [
            {
                "from": "2026-01-01",
                "until": "2026-01-03",
                "preference": {"kind": "unconfigured"},
            }
        ],
    }
    assert not list(database.parent.glob(database.name + "-*"))


def test_injected_database_is_used_when_configured(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_preferred_moves_database(tmp_path / "injected.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = client.get("/api/preferred-moves", params=request_params())

    assert response.status_code == 200
    assert response.json()["fen"] == START_FEN


def test_missing_or_broken_database_gives_unavailable_without_creating_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = client.get("/api/preferred-moves", params=request_params())

    assert missing_response.status_code == 503
    assert missing_response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    before = incompatible.read_bytes()
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(incompatible))
    incompatible_response = client.get("/api/preferred-moves", params=request_params())

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert incompatible.read_bytes() == before


def test_unexpected_failures_stay_safe_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
    api_context,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "read_preferred_moves", fail)
    response = client.get("/api/preferred-moves", params=request_params())

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to serve preferred moves",
    }
    assert "database secret" not in response.text


def test_locked_database_gives_unavailable_without_changing_file(
    monkeypatch: pytest.MonkeyPatch, api_context
) -> None:
    client, database = api_context
    before = database.read_bytes()
    real_read = router_module.read_preferred_moves

    def fast_read(database_path, *args, **kwargs):
        kwargs["lock_timeout"] = 0.1
        return real_read(database_path, *args, **kwargs)

    monkeypatch.setattr(router_module, "read_preferred_moves", fast_read)
    lock = sqlite3.connect(database, timeout=0)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        response = client.get("/api/preferred-moves", params=request_params())
    finally:
        lock.rollback()
        lock.close()

    assert response.status_code == 503
    assert response.json()["code"] == "preferred_moves_unavailable"
    assert database.read_bytes() == before
