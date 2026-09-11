from __future__ import annotations

import sqlite3
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
    delete_body,
    request_params,
)


def test_delete_splits_schedule_and_ignores_unknown_fields(
    api_context,
) -> None:
    client, _database = api_context

    response = delete_body(
        client,
        fen=COUNTER_FEN,
        effective_from="2026-01-15",
        effective_until="2026-01-20",
        preference={"kind": "not-a-preference", "uci": "e2e9"},
        future_filter="ignored",
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": START_FEN,
        "effective_from": "2026-01-15",
        "effective_until": "2026-01-20",
        "periods": [
            {
                "effective_from": "2026-01-01",
                "effective_until": "2026-01-15",
                "preference": {"kind": "move", "uci": "e2e4"},
            },
            {
                "effective_from": "2026-01-20",
                "effective_until": "2026-02-01",
                "preference": {"kind": "move", "uci": "e2e4"},
            },
            {
                "effective_from": "2026-02-01",
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
        "periods",
    }
    assert not any(
        private_name in response.text
        for private_name in ("position_id", "child", "action", "history", "changed")
    )


def test_delete_open_end_accepts_missing_or_null_and_repeats_safely(api_context) -> None:
    client, _database = api_context
    expected = {
        "fen": START_FEN,
        "effective_from": "2026-02-15",
        "effective_until": None,
        "periods": [
            {
                "effective_from": "2026-01-01",
                "effective_until": "2026-02-01",
                "preference": {"kind": "move", "uci": "e2e4"},
            },
            {
                "effective_from": "2026-02-01",
                "effective_until": "2026-02-15",
                "preference": {"kind": "no_preference"},
            },
        ],
    }

    omitted = delete_body(
        client,
        effective_from="2026-02-15",
        include_until=False,
    )
    repeated = delete_body(
        client,
        effective_from="2026-02-15",
        effective_until=None,
    )

    assert omitted.status_code == repeated.status_code == 200
    assert omitted.json() == repeated.json() == expected


def test_delete_outside_schedule_is_noop(api_context) -> None:
    client, _database = api_context

    response = delete_body(
        client,
        effective_from="2025-01-01",
        effective_until="2025-02-01",
    )

    assert response.status_code == 200
    assert response.json()["periods"] == [
        {
            "effective_from": "2026-01-01",
            "effective_until": "2026-02-01",
            "preference": {"kind": "move", "uci": "e2e4"},
        },
        {
            "effective_from": "2026-02-01",
            "effective_until": "2026-03-01",
            "preference": {"kind": "no_preference"},
        },
        {
            "effective_from": "2026-04-01",
            "effective_until": None,
            "preference": {"kind": "move", "uci": "d2d4"},
        },
    ]


def test_delete_new_position_returns_empty_and_stays_unconfigured(
    api_context,
) -> None:
    client, database = api_context

    response = delete_body(
        client,
        fen=UNSEEN_FEN,
        effective_from="2026-06-01",
        effective_until="2026-07-01",
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": " ".join((*UNSEEN_FEN.split()[:4], "0", "1")),
        "effective_from": "2026-06-01",
        "effective_until": "2026-07-01",
        "periods": [],
    }
    assert client.get(
        "/api/preferred-moves",
        params=request_params(UNSEEN_FEN, "2026-06-01", "2026-07-01"),
    ).json()["segments"] == [
        {
            "from": "2026-06-01",
            "until": "2026-07-01",
            "preference": {"kind": "unconfigured"},
        }
    ]
    insight = client.get(
        "/api/positions/insight",
        params={"fen": UNSEEN_FEN, "trainer_color": "white", "as_of": "2026-06-15"},
    )
    assert insight.status_code == 200
    assert insight.json()["preference"] == {"kind": "unconfigured"}
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone() == (3,)


def test_delete_makes_get_and_insight_show_unconfigured(api_context) -> None:
    client, _database = api_context

    response = delete_body(
        client,
        effective_from="2026-02-01",
        effective_until="2026-03-01",
    )
    assert response.status_code == 200

    timeline = client.get(
        "/api/preferred-moves",
        params=request_params(START_FEN, "2026-01-01", "2026-04-01"),
    )
    assert timeline.status_code == 200
    assert timeline.json()["segments"] == [
        {
            "from": "2026-01-01",
            "until": "2026-02-01",
            "preference": {"kind": "move", "uci": "e2e4"},
        },
        {
            "from": "2026-02-01",
            "until": "2026-04-01",
            "preference": {"kind": "unconfigured"},
        },
    ]
    insight = client.get(
        "/api/positions/insight",
        params={"fen": START_FEN, "trainer_color": "white", "as_of": "2026-02-15"},
    )
    assert insight.status_code == 200
    assert insight.json()["preference"] == {"kind": "unconfigured"}


@pytest.mark.parametrize(
    ("body", "error"),
    (
        (
            {"fen": "not a fen", "effective_from": "2026-01-01"},
            {"code": "invalid_fen", "message": "FEN is invalid"},
        ),
        (
            {"fen": START_FEN, "effective_from": "2026-1-01"},
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
            },
            {
                "code": "invalid_window",
                "message": "effective_until must be later than effective_from",
            },
        ),
    ),
)
def test_delete_bad_values_give_clear_error(api_context, body, error) -> None:
    client, _database = api_context

    response = client.request("DELETE", "/api/preferred-moves", json=body)

    assert response.status_code == 422
    assert response.json() == error


def test_delete_requires_body_and_rejects_query_params(api_context) -> None:
    client, _database = api_context

    response = client.delete(
        "/api/preferred-moves",
        params={
            "fen": START_FEN,
            "effective_from": "2026-01-01",
            "effective_until": "2026-02-01",
        },
    )

    assert response.status_code == 422


def test_delete_uses_injected_database_when_configured(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_preferred_moves_database(tmp_path / "injected.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = delete_body(
        client,
        effective_from="2026-06-01",
        effective_until="2026-07-01",
    )

    assert response.status_code == 200
    assert response.json()["fen"] == START_FEN
    assert not (tmp_path / "wrong.db").exists()


def test_delete_missing_or_broken_database_gives_unavailable_without_creating_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = delete_body(client)

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
    incompatible_response = delete_body(client)

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert incompatible.read_bytes() == before


def test_delete_locked_database_gives_unavailable_without_changing_file(
    monkeypatch: pytest.MonkeyPatch, api_context
) -> None:
    client, database = api_context
    before = database.read_bytes()
    real_delete = router_module.delete_preferred_move

    def fast_delete(database_path, request, *args, **kwargs):
        kwargs["lock_timeout"] = 0.1
        return real_delete(database_path, request, *args, **kwargs)

    monkeypatch.setattr(router_module, "delete_preferred_move", fast_delete)
    lock = sqlite3.connect(database, timeout=0)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        response = delete_body(client)
    finally:
        lock.rollback()
        lock.close()

    assert response.status_code == 503
    assert response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert database.read_bytes() == before


def test_delete_unexpected_failure_stays_safe_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
    api_context,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "delete_preferred_move", fail)
    response = delete_body(client)

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to delete preferred moves",
    }
    assert "database secret" not in response.text
