from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import backend.app.features.preferred_moves.router as router_module
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV, get_rebuilt_database_path
from backend.app.main import app

from .conftest import (
    COUNTER_FEN,
    START_FEN,
    UNSEEN_FEN,
    create_preferred_moves_database,
    put_body,
    request_params,
)


def test_put_returns_full_result_and_ignores_unknown_fields(api_context) -> None:
    client, _database = api_context

    response = put_body(
        client,
        fen=COUNTER_FEN,
        effective_from="2026-01-15",
        effective_until="2026-02-15",
        future_filter="ignored",
        preference={"kind": "move", "uci": "e2e4", "future": "ignored"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": START_FEN,
        "effective_from": "2026-01-15",
        "effective_until": "2026-02-15",
        "preference": {"kind": "move", "uci": "e2e4"},
        "periods": [
            {
                "effective_from": "2026-01-01",
                "effective_until": "2026-02-15",
                "preference": {"kind": "move", "uci": "e2e4"},
            },
            {
                "effective_from": "2026-02-15",
                "effective_until": "2026-03-01",
                "preference": {"kind": "no_preference"},
            },
            {
                "effective_from": "2026-04-01",
                "effective_until": None,
                "preference": {"kind": "move", "uci": "d2d4"},
            },
        ],
    }
    assert set(response.json()) == {
        "fen",
        "effective_from",
        "effective_until",
        "preference",
        "periods",
    }
    assert "position_id" not in json.dumps(response.json())
    assert "child" not in json.dumps(response.json())


def test_put_open_end_accepts_missing_or_null_and_repeats_safely(api_context) -> None:
    client, database = api_context
    body = {
        "fen": UNSEEN_FEN,
        "effective_from": "2026-01-01",
        "preference": {"kind": "no_preference"},
    }

    first = client.put("/api/preferred-moves", json=body)
    repeat = client.put("/api/preferred-moves", json={**body, "effective_until": None})

    assert first.status_code == repeat.status_code == 200
    assert first.json() == repeat.json() == {
        "fen": " ".join((*UNSEEN_FEN.split()[:4], "0", "1")),
        "effective_from": "2026-01-01",
        "effective_until": None,
        "preference": {"kind": "no_preference"},
        "periods": [
            {
                "effective_from": "2026-01-01",
                "effective_until": None,
                "preference": {"kind": "no_preference"},
            }
        ],
    }
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone() == (4,)


def test_put_new_position_shows_in_get_and_insight(api_context) -> None:
    client, database = api_context

    response = put_body(
        client,
        fen=UNSEEN_FEN,
        effective_from="2026-06-01",
        effective_until="2026-07-01",
        preference={"kind": "move", "uci": "g1f3"},
    )

    assert response.status_code == 200
    assert client.get(
        "/api/preferred-moves",
        params=request_params(UNSEEN_FEN, "2026-06-01", "2026-07-01"),
    ).json()["segments"] == [
        {
            "from": "2026-06-01",
            "until": "2026-07-01",
            "preference": {"kind": "move", "uci": "g1f3"},
        }
    ]
    insight = client.get(
        "/api/positions/insight",
        params={"fen": UNSEEN_FEN, "trainer_color": "white", "as_of": "2026-06-15"},
    )
    assert insight.status_code == 200
    assert insight.json()["preference"] == {"kind": "move", "uci": "g1f3"}
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone() == (2,)


@pytest.mark.parametrize(
    ("body", "error"),
    (
        (
            {
                "fen": "not a fen",
                "effective_from": "2026-01-01",
                "preference": {"kind": "no_preference"},
            },
            {"code": "invalid_fen", "message": "FEN is invalid"},
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-1-01",
                "preference": {"kind": "no_preference"},
            },
            {
                "code": "invalid_effective_from",
                "message": "effective_from must be a literal YYYY-MM-DD date",
            },
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-01-01",
                "effective_until": "2026-2-01",
                "preference": {"kind": "no_preference"},
            },
            {
                "code": "invalid_effective_until",
                "message": "effective_until must be a literal YYYY-MM-DD date",
            },
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-02-01",
                "effective_until": "2026-01-01",
                "preference": {"kind": "no_preference"},
            },
            {
                "code": "invalid_window",
                "message": "effective_until must be later than effective_from",
            },
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-01-01",
                "preference": {"kind": "no_preference", "uci": "e2e4"},
            },
            {"code": "invalid_preference", "message": "Preference is invalid"},
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-01-01",
                "preference": {"kind": "move", "uci": "e2e9"},
            },
            {"code": "invalid_uci", "message": "UCI move is invalid"},
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-01-01",
                "preference": {"kind": "move", "uci": "e2e5"},
            },
            {"code": "illegal_move", "message": "Move is illegal from the parent FEN"},
        ),
    ),
)
def test_put_bad_values_give_clear_error(api_context, body, error) -> None:
    client, _database = api_context

    response = client.put("/api/preferred-moves", json=body)

    assert response.status_code == 422
    assert response.json() == error


def test_put_requires_body_and_rejects_query_params(api_context) -> None:
    client, _database = api_context

    assert client.put(
        "/api/preferred-moves",
        params={"fen": START_FEN, "effective_from": "2026-01-01"},
        json={"preference": {"kind": "no_preference"}},
    ).status_code == 422
    assert client.put(
        "/api/preferred-moves",
        json={"fen": START_FEN, "effective_from": "2026-01-01"},
    ).status_code == 422


def test_put_uses_injected_database_when_configured(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_preferred_moves_database(tmp_path / "injected.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = put_body(client, effective_from="2026-06-01", effective_until="2026-07-01")

    assert response.status_code == 200
    assert response.json()["fen"] == START_FEN
    assert not (tmp_path / "wrong.db").exists()


def test_put_missing_or_broken_database_gives_unavailable_without_creating_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = put_body(client)

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
    incompatible_response = put_body(client)

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert incompatible.read_bytes() == before


def test_put_locked_database_gives_unavailable_without_changing_file(
    monkeypatch: pytest.MonkeyPatch, api_context
) -> None:
    client, database = api_context
    before = database.read_bytes()
    real_put = router_module.put_preferred_move

    def fast_put(database_path, request, *args, **kwargs):
        kwargs["lock_timeout"] = 0.1
        return real_put(database_path, request, *args, **kwargs)

    monkeypatch.setattr(router_module, "put_preferred_move", fast_put)
    lock = sqlite3.connect(database, timeout=0)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        response = put_body(client)
    finally:
        lock.rollback()
        lock.close()

    assert response.status_code == 503
    assert response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert database.read_bytes() == before


def test_put_unexpected_failure_stays_safe_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
    api_context,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "put_preferred_move", fail)
    response = put_body(client)

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to update preferred moves",
    }
    assert "database secret" not in response.text


def test_concurrent_puts_both_succeed_and_get_shows_both(api_context) -> None:
    client, _database = api_context
    bodies = (
        {
            "fen": START_FEN,
            "effective_from": "2026-06-01",
            "effective_until": "2026-07-01",
            "preference": {"kind": "move", "uci": "e2e4"},
        },
        {
            "fen": START_FEN,
            "effective_from": "2026-07-01",
            "effective_until": "2026-08-01",
            "preference": {"kind": "no_preference"},
        },
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(lambda body: client.put("/api/preferred-moves", json=body), bodies)
        )

    assert [response.status_code for response in responses] == [200, 200]
    timeline = client.get(
        "/api/preferred-moves",
        params=request_params(START_FEN, "2026-06-01", "2026-08-01"),
    )
    assert timeline.status_code == 200
    assert timeline.json()["segments"] == [
        {
            "from": "2026-06-01",
            "until": "2026-07-01",
            "preference": {"kind": "move", "uci": "e2e4"},
        },
        {
            "from": "2026-07-01",
            "until": "2026-08-01",
            "preference": {"kind": "no_preference"},
        },
    ]
