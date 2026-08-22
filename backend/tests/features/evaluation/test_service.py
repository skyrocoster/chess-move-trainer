from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable

import pytest

from backend.app.features.analysis import (
    AnalysisLockError,
    AnalysisProfile,
    AnalysisRepository,
    AnalysisRunLock,
    ResultEligibility,
)
from backend.app.features.evaluation import (
    EvaluationQueueError,
    EvaluationValidationError,
    claim_next,
    complete,
    enqueue,
    inspect,
    request,
    run_session,
)

from .conftest import (
    FOOLS_MATE_FEN,
    QUALIFIED_PROFILE_ID,
    STALEMATE_FEN,
    START_FEN,
    initialized,
    result_for,
)


class FakeEngine:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.closed = False
        self.calls: list[str] = []

    def analyse(self, fen: str):
        if self.fail:
            raise RuntimeError("fake engine failure")
        self.calls.append(fen)
        return result_for(self.profile, fen)

    def close(self) -> None:
        self.closed = True

    def force_terminate(self) -> None:
        self.closed = True


def _factory(
    profile: AnalysisProfile, *, fail: bool = False
) -> tuple[list[FakeEngine], Callable[[], FakeEngine]]:
    engines: list[FakeEngine] = []

    def factory() -> FakeEngine:
        engine = FakeEngine(fail=fail)
        engine.profile = profile
        engines.append(engine)
        return engine

    return engines, factory


def _db(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    initialized(connection)
    return connection


def test_inspect_missing_never_launches_engine(connection: sqlite3.Connection, profile) -> None:
    initialized(connection)
    engines, _ = _factory(profile)
    result = inspect(connection, START_FEN, profile)

    assert result.eligibility is ResultEligibility.MISSING
    assert result.result is None
    assert result.item is None
    assert result.terminal is False
    assert all(engine.calls == [] for engine in engines)


def test_inspect_eligible_returns_result_without_computation(
    connection: sqlite3.Connection, profile
) -> None:
    initialized(connection)
    AnalysisRepository(connection).publish(result_for(profile, START_FEN))

    engines, _ = _factory(profile)
    result = inspect(connection, START_FEN, profile)

    assert result.eligibility is ResultEligibility.ELIGIBLE
    assert result.result is not None
    assert result.result.fen == START_FEN
    assert len(result.result.candidates) == 5
    assert all(engine.calls == [] for engine in engines)


def test_inspect_stale_keeps_result_readable(connection: sqlite3.Connection, profile) -> None:
    initialized(connection)
    AnalysisRepository(connection).publish(result_for(profile, START_FEN))
    stale_profile = AnalysisProfile(
        profile_id=QUALIFIED_PROFILE_ID,
        engine_binary_sha256="b" * 64,
        engine_name="Stockfish 18 fake",
        engine_version="18-test",
        node_budget=200_000,
    )

    engines, _ = _factory(profile)
    result = inspect(connection, START_FEN, stale_profile)

    assert result.eligibility is ResultEligibility.STALE
    assert result.result is not None
    assert result.result.fen == START_FEN
    assert all(engine.calls == [] for engine in engines)


def test_inspect_detects_terminal_position(connection: sqlite3.Connection, profile) -> None:
    initialized(connection)
    terminal = inspect(connection, FOOLS_MATE_FEN, profile)
    assert terminal.terminal is True
    nonterminal = inspect(connection, START_FEN, profile)
    assert nonterminal.terminal is False


def test_request_actions_follow_deliberate_semantics(
    connection: sqlite3.Connection, profile
) -> None:
    initialized(connection)
    # Analyze on a missing position queues it.
    outcome = request(connection, START_FEN, profile, "analyze")
    assert outcome.outcome == "queued"
    assert outcome.item is not None and outcome.item.state == "queued"

    # Analyze again is refused while queued or running.
    with pytest.raises(EvaluationQueueError, match="already queued"):
        request(connection, START_FEN, profile, "analyze")
    claim_next(connection)
    with pytest.raises(EvaluationQueueError, match="already queued"):
        request(connection, START_FEN, profile, "analyze")

    # Update is refused before anything is done.
    with pytest.raises(EvaluationQueueError, match="nothing to update"):
        request(connection, START_FEN, profile, "update")

    # Complete, then update re-queues.
    complete(connection, START_FEN, START_FEN)
    outcome = request(connection, START_FEN, profile, "update")
    assert outcome.outcome == "requeued"
    assert outcome.item is not None and outcome.item.state == "queued"

    # Retry is refused when nothing failed.
    with pytest.raises(EvaluationQueueError, match="nothing to retry"):
        request(connection, START_FEN, profile, "retry")


def test_request_rejects_invalid_action(connection: sqlite3.Connection, profile) -> None:
    initialized(connection)
    with pytest.raises(EvaluationValidationError, match="action"):
        request(connection, START_FEN, profile, "explode")


def test_run_session_drains_fifo_with_five_bounded_workers(database_path: Path, profile) -> None:
    connection = _db(database_path)
    enqueue(connection, START_FEN)
    enqueue(connection, STALEMATE_FEN)
    enqueue(connection, FOOLS_MATE_FEN)
    connection.close()

    engines, factory = _factory(profile)
    result = run_session(database_path, profile, factory, workers=5)

    assert result.completed == 3
    assert result.failed == 0
    assert result.left_queued == 0
    assert len(engines) <= 5
    # Terminal positions never launch an engine; the starting position does.
    calls = [call for engine in engines for call in engine.calls]
    assert calls == [START_FEN]
    assert all(engine.closed for engine in engines)


def test_run_session_marks_failure_without_auto_retry(database_path: Path, profile) -> None:
    connection = _db(database_path)
    enqueue(connection, START_FEN)
    connection.close()

    engines, factory = _factory(profile, fail=True)
    result = run_session(database_path, profile, factory, workers=5)

    assert result.completed == 0
    assert result.failed == 1
    assert result.left_queued == 0
    # No automatic retry: exactly one engine attempt for the single item.
    assert len(engines) == 1
    assert len(engines[0].calls) == 0

    # The item is failed and a deliberate retry re-queues it.
    connection = _db(database_path)
    item = request(connection, START_FEN, profile, "retry")
    assert item.outcome == "retried"
    assert item.item is not None and item.item.state == "queued"
    connection.close()


def test_run_session_respects_shared_analysis_lock(database_path: Path, profile) -> None:
    connection = _db(database_path)
    connection.close()

    holder = AnalysisRunLock(database_path)
    holder.acquire()
    try:
        engines, factory = _factory(profile)
        with pytest.raises(AnalysisLockError, match="another"):
            run_session(database_path, profile, factory, workers=5)
        # Nothing was written while the corpus-fill-style lock was held.
        connection = sqlite3.connect(database_path)
        try:
            queued, running = connection.execute(
                "SELECT "
                "SUM(CASE WHEN state='queued' THEN 1 ELSE 0 END), "
                "SUM(CASE WHEN state='running' THEN 1 ELSE 0 END) "
                "FROM evaluation_queue"
            ).fetchone()
        finally:
            connection.close()
        assert (int(queued or 0), int(running or 0)) == (0, 0)
    finally:
        holder.release()


def test_run_session_restart_requeues_interrupted_running(database_path: Path, profile) -> None:
    connection = _db(database_path)
    enqueue(connection, START_FEN)
    enqueue(connection, STALEMATE_FEN)
    claim_next(connection)
    connection.close()

    engines, factory = _factory(profile)
    result = run_session(database_path, profile, factory, workers=5)

    assert result.requeued == 1
    assert result.completed == 2
    assert result.left_queued == 0
    calls = [call for engine in engines for call in engine.calls]
    assert calls == [START_FEN]


def test_run_session_refuses_workers_ceiling_and_wrong_profile(
    database_path: Path, profile
) -> None:
    connection = _db(database_path)
    connection.close()

    _, factory = _factory(profile)
    with pytest.raises(ValueError, match="between 1 and 5"):
        run_session(database_path, profile, factory, workers=6)

    other = AnalysisProfile(
        profile_id="some-other-profile",
        engine_binary_sha256="a" * 64,
        engine_name="Stockfish 18 fake",
        engine_version="18-test",
        node_budget=200_000,
    )
    with pytest.raises(EvaluationValidationError, match="fixed MP-09 profile"):
        run_session(database_path, other, factory, workers=5)
