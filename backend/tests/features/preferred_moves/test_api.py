from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.routing import APIRoute

import backend.app.features.preferred_moves.router as router_module
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV, get_rebuilt_database_path
from backend.app.main import app

from .conftest import (
    COUNTER_FEN,
    EP_FEN,
    START_FEN,
    UNSEEN_FEN,
    create_preferred_moves_database,
)


def _params(
    fen: str = START_FEN,
    from_date: str = "2026-01-15",
    until: str = "2026-05-15",
) -> dict[str, str]:
    return {"fen": fen, "from": from_date, "until": until}


def _put_body(
    client,
    *,
    fen: str = START_FEN,
    effective_from: str = "2026-06-01",
    effective_until: str | None = "2026-07-01",
    preference: dict[str, object] | None = None,
    include_until: bool = True,
    **extra: object,
):
    body: dict[str, object] = {
        "fen": fen,
        "effective_from": effective_from,
        "preference": preference or {"kind": "move", "uci": "e2e4"},
        **extra,
    }
    if include_until:
        body["effective_until"] = effective_until
    return client.put("/api/preferred-moves", json=body)


def _delete_body(
    client,
    *,
    fen: str = START_FEN,
    effective_from: str = "2026-06-01",
    effective_until: str | None = "2026-07-01",
    include_until: bool = True,
    **extra: object,
):
    body: dict[str, object] = {
        "fen": fen,
        "effective_from": effective_from,
        **extra,
    }
    if include_until:
        body["effective_until"] = effective_until
    return client.request("DELETE", "/api/preferred-moves", json=body)


def test_success_returns_exact_canonical_timeline_and_ignores_unknown_queries(api_context) -> None:
    client, _database = api_context

    response = client.get(
        "/api/preferred-moves",
        params={**_params(fen=COUNTER_FEN), "future_filter": "ignored"},
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
def test_required_query_aliases_are_required(api_context, params: dict[str, str]) -> None:
    client, _database = api_context

    assert client.get("/api/preferred-moves", params=params).status_code == 422


@pytest.mark.parametrize(
    ("params", "error"),
    (
        ({**_params(), "fen": "not a fen"}, {"code": "invalid_fen", "message": "FEN is invalid"}),
        (
            {**_params(), "from": "2026-1-01"},
            {"code": "invalid_from", "message": "from must be a literal YYYY-MM-DD date"},
        ),
        (
            {**_params(), "from": "2026-02-30"},
            {"code": "invalid_from", "message": "from must be a literal YYYY-MM-DD date"},
        ),
        (
            {**_params(), "until": "2026-2-01"},
            {"code": "invalid_until", "message": "until must be a literal YYYY-MM-DD date"},
        ),
        (
            {**_params(), "until": "2026-02-30"},
            {"code": "invalid_until", "message": "until must be a literal YYYY-MM-DD date"},
        ),
        (
            {**_params(), "from": "2026-03-01", "until": "2026-03-01"},
            {"code": "invalid_window", "message": "from must be earlier than until"},
        ),
    ),
)
def test_invalid_values_use_strict_typed_422_errors(api_context, params, error) -> None:
    client, _database = api_context

    response = client.get("/api/preferred-moves", params=params)

    assert response.status_code == 422
    assert response.json() == error


def test_unseen_legal_position_is_one_unconfigured_segment_and_read_only(api_context) -> None:
    client, database = api_context
    before = database.read_bytes()

    response = client.get(
        "/api/preferred-moves",
        params=_params(UNSEEN_FEN, "2026-01-01", "2026-01-03"),
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


def test_empty_schedule_and_legal_en_passant_identity_are_successful(api_context) -> None:
    client, database = api_context
    empty = client.get(
        "/api/preferred-moves",
        params=_params(EP_FEN, "2026-01-01", "2026-01-03"),
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


def test_clean_dependency_override_selects_injected_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_preferred_moves_database(tmp_path / "injected.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = client.get("/api/preferred-moves", params=_params())

    assert response.status_code == 200
    assert response.json()["fen"] == START_FEN


def test_missing_or_incompatible_data_is_typed_503_without_target_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = client.get("/api/preferred-moves", params=_params())

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
    incompatible_response = client.get("/api/preferred-moves", params=_params())

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert incompatible.read_bytes() == before


def test_unexpected_failure_is_safe_and_does_not_leak_internal_messages(
    monkeypatch: pytest.MonkeyPatch,
    api_context,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "read_preferred_moves", fail)
    response = client.get("/api/preferred-moves", params=_params())

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to serve preferred moves",
    }
    assert "database secret" not in response.text


def test_locked_database_is_typed_503_and_does_not_write(api_context) -> None:
    client, database = api_context
    before = database.read_bytes()
    lock = sqlite3.connect(database, timeout=0)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        response = client.get("/api/preferred-moves", params=_params())
    finally:
        lock.rollback()
        lock.close()

    assert response.status_code == 503
    assert response.json()["code"] == "preferred_moves_unavailable"
    assert database.read_bytes() == before


def test_new_route_coexists_with_all_singular_preferred_move_routes() -> None:
    routes = {
        (route.path, method)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    }

    assert ("/api/preferred-moves", "GET") in routes
    assert ("/api/preferred-move", "GET") in routes
    assert ("/api/preferred-move", "PUT") in routes
    assert ("/api/preferred-move", "DELETE") in routes


def test_new_route_has_the_settled_operation_id() -> None:
    get_route = next(
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/preferred-moves"
        and "GET" in route.methods
    )
    put_route = next(
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/preferred-moves"
        and "PUT" in route.methods
    )
    delete_route = next(
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/preferred-moves"
        and "DELETE" in route.methods
    )

    assert get_route.operation_id == "getPreferredMoves"
    assert put_route.operation_id == "putPreferredMoves"
    assert delete_route.operation_id == "deletePreferredMoves"


def test_delete_returns_exact_canonical_split_schedule_and_ignores_unknown_fields(
    api_context,
) -> None:
    client, _database = api_context

    response = _delete_body(
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


def test_delete_open_end_accepts_omitted_or_null_end_and_is_repeatable(api_context) -> None:
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

    omitted = _delete_body(
        client,
        effective_from="2026-02-15",
        include_until=False,
    )
    repeated = _delete_body(
        client,
        effective_from="2026-02-15",
        effective_until=None,
    )

    assert omitted.status_code == repeated.status_code == 200
    assert omitted.json() == repeated.json() == expected


def test_delete_non_intersecting_existing_schedule_is_a_200_noop(api_context) -> None:
    client, _database = api_context

    response = _delete_body(
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


def test_delete_novel_legal_position_is_empty_success_and_immediately_unconfigured(
    api_context,
) -> None:
    client, database = api_context

    response = _delete_body(
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
        params=_params(UNSEEN_FEN, "2026-06-01", "2026-07-01"),
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


def test_delete_immediately_derives_unconfigured_get_and_insight_segments(api_context) -> None:
    client, _database = api_context

    response = _delete_body(
        client,
        effective_from="2026-02-01",
        effective_until="2026-03-01",
    )
    assert response.status_code == 200

    timeline = client.get(
        "/api/preferred-moves",
        params=_params(START_FEN, "2026-01-01", "2026-04-01"),
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
def test_delete_semantic_invalid_values_use_exact_four_errors(api_context, body, error) -> None:
    client, _database = api_context

    response = client.request("DELETE", "/api/preferred-moves", json=body)

    assert response.status_code == 422
    assert response.json() == error


def test_delete_requires_body_fields_and_does_not_accept_query_aliases(api_context) -> None:
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


def test_delete_dependency_override_selects_injected_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_preferred_moves_database(tmp_path / "injected.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = _delete_body(
        client,
        effective_from="2026-06-01",
        effective_until="2026-07-01",
    )

    assert response.status_code == 200
    assert response.json()["fen"] == START_FEN
    assert not (tmp_path / "wrong.db").exists()


def test_delete_missing_or_incompatible_data_is_typed_503_without_target_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = _delete_body(client)

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
    incompatible_response = _delete_body(client)

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert incompatible.read_bytes() == before


def test_delete_locked_database_is_typed_503_without_writing(api_context) -> None:
    client, database = api_context
    before = database.read_bytes()
    lock = sqlite3.connect(database, timeout=0)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        response = _delete_body(client)
    finally:
        lock.rollback()
        lock.close()

    assert response.status_code == 503
    assert response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert database.read_bytes() == before


def test_delete_unexpected_failure_is_safe_and_does_not_leak_internal_messages(
    monkeypatch: pytest.MonkeyPatch,
    api_context,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "delete_preferred_move", fail)
    response = _delete_body(client)

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to delete preferred moves",
    }
    assert "database secret" not in response.text


def test_put_returns_exact_canonical_result_and_ignores_unknown_body_fields(api_context) -> None:
    client, _database = api_context

    response = _put_body(
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


def test_put_supports_omitted_and_null_open_ends_and_is_idempotent(api_context) -> None:
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


def test_put_novel_position_is_visible_to_get_and_position_insight(api_context) -> None:
    client, database = api_context

    response = _put_body(
        client,
        fen=UNSEEN_FEN,
        effective_from="2026-06-01",
        effective_until="2026-07-01",
        preference={"kind": "move", "uci": "g1f3"},
    )

    assert response.status_code == 200
    assert client.get(
        "/api/preferred-moves",
        params=_params(UNSEEN_FEN, "2026-06-01", "2026-07-01"),
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
            {"fen": "not a fen", "effective_from": "2026-01-01", "preference": {"kind": "no_preference"}},
            {"code": "invalid_fen", "message": "FEN is invalid"},
        ),
        (
            {"fen": START_FEN, "effective_from": "2026-1-01", "preference": {"kind": "no_preference"}},
            {"code": "invalid_effective_from", "message": "effective_from must be a literal YYYY-MM-DD date"},
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-01-01",
                "effective_until": "2026-2-01",
                "preference": {"kind": "no_preference"},
            },
            {"code": "invalid_effective_until", "message": "effective_until must be a literal YYYY-MM-DD date"},
        ),
        (
            {
                "fen": START_FEN,
                "effective_from": "2026-02-01",
                "effective_until": "2026-01-01",
                "preference": {"kind": "no_preference"},
            },
            {"code": "invalid_window", "message": "effective_until must be later than effective_from"},
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
def test_put_semantic_invalid_values_use_settled_errors(api_context, body, error) -> None:
    client, _database = api_context

    response = client.put("/api/preferred-moves", json=body)

    assert response.status_code == 422
    assert response.json() == error


def test_put_missing_body_fields_and_query_aliases_retain_fastapi_422(api_context) -> None:
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


def test_put_dependency_override_selects_injected_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    injected = create_preferred_moves_database(tmp_path / "injected.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(tmp_path / "wrong.db"))
    app.dependency_overrides[get_rebuilt_database_path] = lambda: injected

    response = _put_body(client, effective_from="2026-06-01", effective_until="2026-07-01")

    assert response.status_code == 200
    assert response.json()["fen"] == START_FEN
    assert not (tmp_path / "wrong.db").exists()


def test_put_missing_or_incompatible_data_is_typed_503_without_target_creation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))
    missing_response = _put_body(client)

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
    incompatible_response = _put_body(client)

    assert incompatible_response.status_code == 503
    assert incompatible_response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert incompatible.read_bytes() == before


def test_put_locked_database_is_typed_503_without_writing(api_context) -> None:
    client, database = api_context
    before = database.read_bytes()
    lock = sqlite3.connect(database, timeout=0)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        response = _put_body(client)
    finally:
        lock.rollback()
        lock.close()

    assert response.status_code == 503
    assert response.json() == {
        "code": "preferred_moves_unavailable",
        "message": "Preferred moves unavailable",
    }
    assert database.read_bytes() == before


def test_put_unexpected_failure_is_safe_and_does_not_leak_internal_messages(
    monkeypatch: pytest.MonkeyPatch,
    api_context,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "put_preferred_move", fail)
    response = _put_body(client)

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to update preferred moves",
    }
    assert "database secret" not in response.text


def test_put_serializes_competing_writers_and_get_observes_both_results(api_context) -> None:
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
        params=_params(START_FEN, "2026-06-01", "2026-08-01"),
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
