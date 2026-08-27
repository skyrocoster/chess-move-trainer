from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.app.features.evaluation.router as evaluation_router_module
from backend.app.features.analysis import AnalysisRepository
from backend.app.features.evaluation import claim_next, complete, fail
from backend.app.main import app

from .conftest import FOOLS_MATE_FEN, START_FEN, initialized, result_for

ANALYSIS_ONLY_FEN = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42"


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    profile,
) -> tuple[TestClient, Path]:
    database = tmp_path / "api.db"
    with sqlite3.connect(database) as connection:
        initialized(connection)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    monkeypatch.setattr(evaluation_router_module, "active_profile", lambda: profile)
    return TestClient(app), database


def _observe(client: TestClient, fen: str = START_FEN):
    return client.get("/api/evaluation", params={"fen": fen})


def _status(client: TestClient, fen: str = START_FEN):
    return client.get("/api/evaluation/status", params={"fen": fen})


def _action(client: TestClient, action: str, fen: str = START_FEN):
    return client.post("/api/evaluation", json={"fen": fen, "action": action})


def _database_connection(database: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _add_corpus_fixture(database: Path) -> None:
    with _database_connection(database) as connection:
        connection.executescript(
            """
            CREATE TABLE corpus_schema (id INTEGER PRIMARY KEY, version INTEGER NOT NULL);
            CREATE TABLE games (uuid TEXT PRIMARY KEY);
            CREATE TABLE corpus (
                corpus_id INTEGER PRIMARY KEY,
                subject_player_uuid TEXT NOT NULL
            );
            CREATE TABLE corpus_game (corpus_id INTEGER NOT NULL, game_uuid TEXT NOT NULL);
            CREATE TABLE position_state (
                state_id INTEGER PRIMARY KEY,
                placement TEXT NOT NULL,
                side_to_move TEXT NOT NULL,
                castling TEXT NOT NULL,
                en_passant TEXT NOT NULL
            );
            CREATE TABLE position_occurrence (
                occurrence_id INTEGER PRIMARY KEY,
                game_uuid TEXT NOT NULL,
                ply INTEGER NOT NULL,
                state_id INTEGER NOT NULL,
                halfmove_clock INTEGER NOT NULL,
                fullmove_number INTEGER NOT NULL
            );
            INSERT INTO corpus_schema VALUES (1, 1);
            INSERT INTO games VALUES ('stored-game');
            INSERT INTO corpus VALUES (1, 'subject');
            INSERT INTO corpus_game VALUES (1, 'stored-game');
            INSERT INTO position_state VALUES (1, '8/8/8/8/8/8/8/8', 'w', '-', '-');
            INSERT INTO position_occurrence VALUES (1, 'stored-game', 0, 1, 0, 1);
            """
        )


def _corpus_snapshot(database: Path) -> tuple[tuple[str, tuple[tuple[object, ...], ...]], ...]:
    tables = (
        "corpus_schema",
        "games",
        "corpus",
        "corpus_game",
        "position_state",
        "position_occurrence",
    )
    with _database_connection(database) as connection:
        return tuple(
            (
                table,
                tuple(tuple(row) for row in connection.execute(f"SELECT * FROM {table}")),
            )
            for table in tables
        )


def test_eligible_observation_returns_exact_typed_result_without_computation(
    api_context,
    profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, database = api_context
    with _database_connection(database) as connection:
        AnalysisRepository(connection).publish(result_for(profile, START_FEN))
    before = database.read_bytes()

    def unexpected_enqueue(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("an observation must not enqueue or compute")

    monkeypatch.setattr(evaluation_router_module, "request", unexpected_enqueue)
    response = _observe(client)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"fen", "eligibility", "result", "status", "terminal"}
    assert body["fen"] == START_FEN
    assert body["eligibility"] == "eligible"
    assert body["status"] is None
    assert body["terminal"] is False
    assert set(body["result"]) == {
        "fen",
        "profile_id",
        "candidates",
        "terminal_kind",
        "completed_at",
        "wall_time_ms",
    }
    assert len(body["result"]["candidates"]) == 5
    assert set(body["result"]["candidates"][0]) == {
        "rank",
        "score_kind",
        "score_value",
        "wdl_wins",
        "wdl_draws",
        "wdl_losses",
        "pv_uci",
        "depth",
        "seldepth",
        "nodes",
        "engine_time_ms",
    }
    assert database.read_bytes() == before


def test_counter_variant_observation_uses_one_internal_identity(api_context, profile) -> None:
    client, database = api_context
    with _database_connection(database) as connection:
        AnalysisRepository(connection).publish(result_for(profile, START_FEN))

    response = _observe(client, COUNTER_VARIANT_FEN)

    assert response.status_code == 200
    assert response.json()["fen"] == COUNTER_VARIANT_FEN
    assert response.json()["eligibility"] == "eligible"
    assert response.json()["result"]["fen"] == COUNTER_VARIANT_FEN


def test_missing_observation_is_read_only_and_terminal_classification_is_instant(
    api_context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, database = api_context
    before = database.read_bytes()
    monkeypatch.setattr(
        evaluation_router_module,
        "_open_write_connection",
        lambda: (_ for _ in ()).throw(AssertionError("read path opened a writer")),
    )

    missing = _observe(client)
    terminal = _observe(client, FOOLS_MATE_FEN)

    assert missing.status_code == 200
    assert missing.json() == {
        "fen": START_FEN,
        "eligibility": "missing",
        "result": None,
        "status": None,
        "terminal": False,
    }
    assert terminal.status_code == 200
    assert terminal.json()["eligibility"] == "missing"
    assert terminal.json()["terminal"] is True
    assert database.read_bytes() == before


def test_analysis_only_fen_does_not_mutate_corpus_tables(api_context, profile) -> None:
    client, database = api_context
    _add_corpus_fixture(database)
    before = _corpus_snapshot(database)

    missing = _observe(client, ANALYSIS_ONLY_FEN)
    assert missing.status_code == 200
    assert missing.json() == {
        "fen": ANALYSIS_ONLY_FEN,
        "eligibility": "missing",
        "result": None,
        "status": None,
        "terminal": False,
    }
    assert _corpus_snapshot(database) == before

    queued = _action(client, "analyze", ANALYSIS_ONLY_FEN)
    assert queued.status_code == 202
    assert queued.json()["fen"] == ANALYSIS_ONLY_FEN
    assert queued.json()["status"]["state"] == "queued"

    with _database_connection(database) as connection:
        assert claim_next(connection) is not None
        AnalysisRepository(connection).publish(result_for(profile, ANALYSIS_ONLY_FEN))
        complete(connection, ANALYSIS_ONLY_FEN, ANALYSIS_ONLY_FEN)

    reused = _observe(client, ANALYSIS_ONLY_FEN)
    assert reused.status_code == 200
    assert reused.json()["eligibility"] == "eligible"
    assert reused.json()["result"]["fen"] == ANALYSIS_ONLY_FEN
    assert _corpus_snapshot(database) == before


def test_enqueue_response_is_exact_and_duplicate_analyze_is_a_typed_transition_error(
    api_context,
) -> None:
    client, database = api_context

    first = _action(client, "analyze")
    duplicate = _action(client, "analyze")

    assert first.status_code == 202
    assert set(first.json()) == {"fen", "action", "outcome", "eligibility", "status"}
    assert first.json()["outcome"] == "queued"
    assert first.json()["eligibility"] == "missing"
    assert first.json()["status"]["state"] == "queued"
    assert set(first.json()["status"]) == {
        "state",
        "position",
        "attempts",
        "enqueued_at",
        "started_at",
        "completed_at",
        "error_code",
    }
    assert duplicate.status_code == 409
    assert duplicate.json() == {
        "code": "invalid_transition",
        "message": "Evaluation action is not valid for the current queue state",
    }
    with _database_connection(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM evaluation_queue").fetchone() == (1,)


def test_status_observes_running_done_and_completion(api_context) -> None:
    client, database = api_context
    _action(client, "analyze")

    connection = _database_connection(database)
    try:
        assert claim_next(connection) is not None
    finally:
        connection.close()
    running = _status(client)
    assert running.status_code == 200
    assert running.json()["state"] == "running"
    assert running.json()["completed_at"] is None
    assert running.json()["error_code"] is None

    connection = _database_connection(database)
    try:
        complete(connection, START_FEN, START_FEN)
    finally:
        connection.close()
    done = _status(client)
    assert done.status_code == 200
    assert done.json()["state"] == "done"
    assert done.json()["completed_at"] is not None


def test_status_observes_terminal_failure_without_partial_result(api_context) -> None:
    client, database = api_context
    _action(client, "analyze", FOOLS_MATE_FEN)
    connection = _database_connection(database)
    try:
        assert claim_next(connection) is not None
        fail(connection, FOOLS_MATE_FEN, "engine_failure", "offline test failure")
    finally:
        connection.close()

    status = _status(client, FOOLS_MATE_FEN)
    observed = _observe(client, FOOLS_MATE_FEN)
    assert status.json() == {
        "fen": FOOLS_MATE_FEN,
        "state": "failed",
        "completed_at": status.json()["completed_at"],
        "error_code": "engine_failure",
    }
    assert observed.status_code == 200
    assert observed.json()["status"]["state"] == "failed"
    assert observed.json()["result"] is None
    assert observed.json()["terminal"] is True


def test_update_and_retry_are_deliberate_and_requeue_through_service_rules(
    api_context,
    profile,
) -> None:
    client, database = api_context
    _action(client, "analyze")
    connection = _database_connection(database)
    try:
        claim_next(connection)
        complete(connection, START_FEN, START_FEN)
    finally:
        connection.close()

    updated = _action(client, "update")
    assert updated.status_code == 202
    assert updated.json()["outcome"] == "requeued"

    connection = _database_connection(database)
    try:
        claim_next(connection)
        fail(connection, START_FEN, "engine_failure", "offline test failure")
    finally:
        connection.close()
    retried = _action(client, "retry")
    assert retried.status_code == 202
    assert retried.json()["outcome"] == "retried"


@pytest.mark.parametrize(
    ("fen", "code"),
    (
        (START_FEN.replace(" ", "  ", 1), "invalid_fen"),
        ("x" * 129, "request_too_large"),
    ),
)
def test_fen_validation_and_size_bounds_are_typed(api_context, fen: str, code: str) -> None:
    client, _database = api_context
    response = _observe(client, fen)
    assert response.status_code == 422
    assert response.json()["code"] == code
    assert set(response.json()) == {"code", "message"}


def test_action_validation_and_extra_request_keys_are_rejected(api_context) -> None:
    client, database = api_context
    invalid_action = _action(client, "compute")
    extra_key = client.post(
        "/api/evaluation",
        json={"fen": START_FEN, "action": "analyze", "extra": "refused"},
    )

    assert invalid_action.status_code == 422
    assert invalid_action.json() == {
        "code": "invalid_action",
        "message": "action must be one of analyze, update, retry",
    }
    assert extra_key.status_code == 422
    assert "detail" in extra_key.json()
    with _database_connection(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM evaluation_queue").fetchone() == (0,)


def test_status_for_unknown_position_has_no_queue_state(api_context) -> None:
    client, _database = api_context
    response = _status(client)
    assert response.status_code == 200
    assert response.json() == {
        "fen": START_FEN,
        "state": None,
        "completed_at": None,
        "error_code": None,
    }


def test_missing_database_is_typed_and_does_not_get_created(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    response = TestClient(app).get("/api/evaluation", params={"fen": START_FEN})
    assert response.status_code == 503
    assert response.json() == {
        "code": "evaluation_unavailable",
        "message": "Evaluation data unavailable",
    }
    assert not database.exists()


def test_evaluation_cors_allows_only_the_new_post_method(api_context) -> None:
    client, _database = api_context
    response = client.options(
        "/api/evaluation",
        headers={
            "Origin": "http://localhost:8444",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8444"
    assert "POST" in response.headers["access-control-allow-methods"]
