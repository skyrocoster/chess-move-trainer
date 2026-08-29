from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.app.features.preferred_move.repository as repository_module
import backend.app.features.preferred_move.router as router_module
from backend.app.main import app

from .conftest import (
    COUNTER_FEN,
    OTHER_UUID,
    START_FEN,
    SUBJECT_UUID,
    UNKNOWN_FEN,
    UNOBSERVED_FEN,
    create_database,
)

EARLY = "2026-01-01T00:00:00Z"
LATE = "2026-01-10T00:00:00Z"
FUTURE = "2999-01-01T00:00:00Z"
MOVE_TABLE = "opening_preferred_move_event"
REQUIREMENT_TABLE = "opening_preferred_move_requirement_event"


def _get(client: TestClient, fen: str = START_FEN, as_of: str | None = None):
    params = {"fen": fen}
    if as_of is not None:
        params["as_of"] = as_of
    return client.get("/api/preferred-move", params=params)


def _put(
    client: TestClient,
    fen: str = START_FEN,
    move_uci: str = "e2e4",
    effective_at: object = EARLY,
):
    body: dict[str, object] = {"fen": fen, "move_uci": move_uci}
    if effective_at is not ...:
        body["effective_at"] = effective_at
    return client.put("/api/preferred-move", json=body)


def _delete(client: TestClient, fen: str = START_FEN, effective_at: str | None = EARLY):
    params: dict[str, str] = {"fen": fen}
    if effective_at is not None:
        params["effective_at"] = effective_at
    return client.delete("/api/preferred-move", params=params)


def _count(database: Path, table: str = MOVE_TABLE) -> int:
    with sqlite3.connect(database) as db:
        return int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_read_connection_uses_a_five_second_sqlite_busy_timeout(api_context) -> None:
    _client, _database = api_context

    connection = repository_module.open_read_connection()
    try:
        assert tuple(connection.execute("PRAGMA busy_timeout").fetchone()) == (5000,)
    finally:
        connection.close()


def test_lifecycle_returns_explicit_unassigned_state_and_preserves_append_only_history(
    api_context,
) -> None:
    client, database = api_context

    assert _get(client).json() == {"fen": START_FEN, "state": "unassigned", "move": None}

    assigned = _put(client)
    replaced = _put(client, move_uci="d2d4")
    removed = _delete(client, effective_at="2026-01-02T00:00:00Z")

    assert assigned.status_code == replaced.status_code == removed.status_code == 200
    assert assigned.json() == {
        "fen": START_FEN,
        "changed": True,
        "effective_at": "2026-01-01T00:00:00.000000Z",
    }
    assert replaced.json()["changed"] is True
    assert removed.json() == {
        "fen": START_FEN,
        "changed": True,
        "effective_at": "2026-01-02T00:00:00.000000Z",
    }
    assert _get(client, as_of="2026-01-01T00:00:00Z").json() == {
        "fen": START_FEN,
        "state": "assigned",
        "move": {"uci": "d2d4", "san": "d4"},
    }
    assert _get(client, as_of="2026-01-03T00:00:00Z").json() == {
        "fen": START_FEN,
        "state": "unassigned",
        "move": None,
    }

    with sqlite3.connect(database) as db:
        rows = db.execute(
            f"SELECT player_uuid, action, move_uci, move_san, effective_at FROM {MOVE_TABLE} "
            "ORDER BY event_id"
        ).fetchall()
        assert rows == [
            (SUBJECT_UUID, "set", "e2e4", "e4", "2026-01-01T00:00:00.000000Z"),
            (SUBJECT_UUID, "set", "d2d4", "d4", "2026-01-01T00:00:00.000000Z"),
            (SUBJECT_UUID, "remove", None, None, "2026-01-02T00:00:00.000000Z"),
        ]
        assert db.execute(f"SELECT COUNT(*) FROM {REQUIREMENT_TABLE}").fetchone() == (0,)
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            db.execute(f"UPDATE {MOVE_TABLE} SET action = 'remove' WHERE event_id = 1")
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            db.execute(f"DELETE FROM {MOVE_TABLE} WHERE event_id = 1")


def test_same_effective_move_is_a_noop_without_a_new_event(api_context) -> None:
    client, database = api_context
    first = _put(client)
    before = _count(database)

    repeat = _put(client)

    assert first.json()["changed"] is True
    assert repeat.status_code == 200
    assert repeat.json() == {
        "fen": START_FEN,
        "changed": False,
        "effective_at": "2026-01-01T00:00:00.000000Z",
    }
    assert _count(database) == before == 1


def test_full_fen_counters_share_one_four_field_identity(api_context) -> None:
    client, database = api_context

    response = _put(client, fen=COUNTER_FEN)

    assert response.status_code == 200
    assert response.json()["fen"] == COUNTER_FEN
    assert _get(client, START_FEN, as_of=EARLY).json()["move"] == {"uci": "e2e4", "san": "e4"}
    assert _get(client, COUNTER_FEN, as_of=EARLY).json() == {
        "fen": COUNTER_FEN,
        "state": "assigned",
        "move": {"uci": "e2e4", "san": "e4"},
    }
    with sqlite3.connect(database) as db:
        assert db.execute(f"SELECT COUNT(*) FROM {MOVE_TABLE}").fetchone() == (1,)
        assert db.execute(
            f"SELECT placement, side_to_move, castling, en_passant FROM {MOVE_TABLE}"
        ).fetchone() == tuple(COUNTER_FEN.split()[:4])


def test_as_of_reads_backdated_and_same_effective_event_ordering(api_context) -> None:
    client, _database = api_context

    assert _put(client, move_uci="e2e4", effective_at=LATE).status_code == 200
    assert _put(client, move_uci="d2d4", effective_at="2026-01-05T00:00:00Z").status_code == 200

    assert _get(client, as_of="2026-01-06T00:00:00Z").json()["move"] == {
        "uci": "d2d4",
        "san": "d4",
    }
    assert _get(client, as_of="2026-01-11T00:00:00Z").json()["move"] == {
        "uci": "e2e4",
        "san": "e4",
    }
    assert _get(client, as_of=FUTURE).json()["move"] == {"uci": "e2e4", "san": "e4"}


def test_omitted_null_and_blank_mutation_times_capture_current_utc(api_context) -> None:
    client, database = api_context
    responses = [
        _put(client, move_uci="e2e4", effective_at=...),
        _put(client, move_uci="d2d4", effective_at=None),
        _put(client, move_uci="c2c4", effective_at=""),
    ]

    assert all(response.status_code == 200 for response in responses)
    times = [_parse_time(response.json()["effective_at"]) for response in responses]
    now = datetime.now(UTC)
    assert all(timestamp <= now for timestamp in times)
    assert all(response.json()["changed"] is True for response in responses)
    with sqlite3.connect(database) as db:
        stored = [
            row[0] for row in db.execute(f"SELECT effective_at FROM {MOVE_TABLE} ORDER BY event_id")
        ]
    assert stored == [response.json()["effective_at"] for response in responses]

    removed = _delete(client, effective_at="")
    assert removed.status_code == 200
    assert removed.json()["changed"] is True
    assert _get(client).json()["state"] == "unassigned"


def test_invalid_and_future_times_are_typed_and_do_not_append(api_context) -> None:
    client, database = api_context
    assert _put(client, effective_at=FUTURE).json()["code"] == "future_effective_time"
    assert _delete(client, effective_at=FUTURE).json()["code"] == "future_effective_time"
    assert _put(client, effective_at="not-a-time").json()["code"] == "invalid_timestamp"
    assert _get(client, as_of="").json()["code"] == "invalid_timestamp"
    assert _count(database) == 0


def test_invalid_fen_and_uci_are_422(api_context) -> None:
    client, _database = api_context
    invalid_fen = START_FEN.replace(" ", "  ", 1)

    assert _get(client, invalid_fen).status_code == 422
    assert _get(client, invalid_fen).json()["code"] == "invalid_fen"
    invalid_move = _put(client, move_uci="e2e5")
    assert invalid_move.status_code == 422
    assert invalid_move.json() == {
        "code": "invalid_move",
        "message": "move_uci is not a legal UCI move",
    }


@pytest.mark.parametrize("fen", (UNKNOWN_FEN, UNOBSERVED_FEN))
def test_unknown_and_non_game_derived_positions_are_typed_not_found(api_context, fen: str) -> None:
    client, _database = api_context

    for response in (
        _get(client, fen),
        _put(client, fen=fen, move_uci="a2a3"),
        _delete(client, fen=fen),
    ):
        assert response.status_code == 404
        assert response.json() == {"code": "position_not_found", "message": "Position not found"}


def test_fixed_ownership_and_extra_player_selection_are_rejected(api_context) -> None:
    client, database = api_context
    assert _put(client).status_code == 200
    extra = client.put(
        "/api/preferred-move",
        json={"fen": START_FEN, "move_uci": "d2d4", "player_uuid": OTHER_UUID},
    )

    assert extra.status_code == 422
    assert _count(database) == 1
    with sqlite3.connect(database) as db:
        assert db.execute(f"SELECT DISTINCT player_uuid FROM {MOVE_TABLE}").fetchall() == [
            (SUBJECT_UUID,)
        ]


def test_missing_preferred_schema_is_503_and_is_not_created(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "without-preferred-schema.db"
    create_database(database, preferred_schema=False)
    before = database.read_bytes()
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    client = TestClient(app)

    assert _get(client).status_code == 503
    assert _put(client).status_code == 503
    assert database.read_bytes() == before
    with sqlite3.connect(database) as db:
        assert db.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name LIKE 'opening_preferred_move%'"
        ).fetchone() == (0,)


def test_incompatible_schema_is_503_without_data_change(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "incompatible.db"
    create_database(database, version=2)
    before = database.read_bytes()
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))

    response = TestClient(app).get("/api/preferred-move", params={"fen": START_FEN})

    assert response.status_code == 503
    assert response.json() == {
        "code": "preferred_move_unavailable",
        "message": "Preferred-move data unavailable",
    }
    assert database.read_bytes() == before


def test_missing_database_is_503_and_not_created(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    client = TestClient(app)

    assert _get(client).status_code == 503
    assert _put(client).status_code == 503
    assert not database.exists()


def test_locked_database_is_503_without_an_event(api_context) -> None:
    client, database = api_context
    lock = sqlite3.connect(database, timeout=0)
    lock.execute("BEGIN EXCLUSIVE")
    try:
        response = _put(client)
    finally:
        lock.rollback()
        lock.close()

    assert response.status_code == 503
    assert response.json()["code"] == "preferred_move_unavailable"
    assert _count(database) == 0


def test_unexpected_failure_is_safe_and_contains_no_internal_message(
    monkeypatch: pytest.MonkeyPatch,
    api_context,
) -> None:
    client, _database = api_context

    def fail(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("database secret")

    monkeypatch.setattr(router_module, "get_preferred_move", fail)
    response = _get(client)

    assert response.status_code == 500
    assert response.json() == {
        "code": "unexpected_failure",
        "message": "Unable to serve preferred move",
    }
    assert "database secret" not in response.text


def test_api_mutates_only_the_configured_temporary_database(api_context) -> None:
    client, database = api_context
    runtime = Path("data/database/chess_games.db").resolve()
    before = database.read_bytes()

    response = _put(client)

    assert response.status_code == 200
    assert database.resolve() != runtime
    assert database.read_bytes() != before
    assert _count(database) == 1


def test_cors_allows_only_the_approved_mutation_methods(api_context) -> None:
    client, _database = api_context
    for method in ("PUT", "DELETE"):
        response = client.options(
            "/api/preferred-move",
            headers={
                "Origin": "http://localhost:8444",
                "Access-Control-Request-Method": method,
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:8444"
        assert method in response.headers["access-control-allow-methods"]
