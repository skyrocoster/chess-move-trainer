from __future__ import annotations

import sqlite3

import chess
import pytest

from backend.app.features.evaluation import (
    EvaluationQueueError,
    EvaluationValidationError,
    claim_next,
    complete,
    enqueue,
    fail,
    observe,
    observe_many,
    pending_count,
    requeue_running,
)

from .conftest import START_FEN, initialized

SECOND_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
THIRD_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"


def test_enqueue_inserts_fifo_positions(connection: sqlite3.Connection) -> None:
    initialized(connection)

    outcome, item = enqueue(connection, START_FEN)
    assert outcome == "queued"
    assert item.state == "queued"
    assert item.position == 1
    assert item.attempts == 0
    assert item.started_at is None
    assert item.finished_at is None

    _, second = enqueue(connection, SECOND_FEN)
    assert second.position == 2


def test_enqueue_dedupes_queued_and_running(connection: sqlite3.Connection) -> None:
    initialized(connection)

    _, first = enqueue(connection, START_FEN)
    outcome, again = enqueue(connection, START_FEN)
    assert outcome == "already_queued"
    assert again == first

    claimed = claim_next(connection)
    assert claimed is not None
    outcome, running_again = enqueue(connection, START_FEN)
    assert outcome == "already_running"
    assert running_again == claimed

    rows = connection.execute("SELECT COUNT(*) FROM evaluation_queue").fetchone()
    assert rows == (1,)


def test_claim_is_fifo_and_marks_running(connection: sqlite3.Connection) -> None:
    initialized(connection)

    enqueue(connection, START_FEN)
    enqueue(connection, SECOND_FEN)
    enqueue(connection, THIRD_FEN)

    first = claim_next(connection)
    second = claim_next(connection)
    third = claim_next(connection)
    assert [first.fen, second.fen, third.fen] == [START_FEN, SECOND_FEN, THIRD_FEN]
    assert all(item.state == "running" for item in (first, second, third))
    assert all(item.started_at is not None for item in (first, second, third))
    assert claim_next(connection) is None

    queued, running = pending_count(connection)
    assert (queued, running) == (0, 3)


def test_complete_requires_running(connection: sqlite3.Connection) -> None:
    initialized(connection)

    enqueue(connection, START_FEN)
    with pytest.raises(EvaluationQueueError, match="not running"):
        complete(connection, START_FEN, START_FEN)

    claimed = claim_next(connection)
    assert claimed is not None
    complete(connection, START_FEN, START_FEN)
    item = observe(connection, START_FEN)
    assert item is not None
    assert item.state == "done"
    assert item.finished_at is not None

    with pytest.raises(EvaluationQueueError, match="not running"):
        complete(connection, START_FEN, START_FEN)


def test_complete_rejects_result_fen_mismatch(connection: sqlite3.Connection) -> None:
    initialized(connection)

    enqueue(connection, START_FEN)
    claim_next(connection)
    with pytest.raises(EvaluationValidationError, match="does not match"):
        complete(connection, START_FEN, SECOND_FEN)


def test_fail_requires_running_and_records_details(connection: sqlite3.Connection) -> None:
    initialized(connection)

    enqueue(connection, START_FEN)
    with pytest.raises(EvaluationQueueError, match="not running"):
        fail(connection, START_FEN, "engine_failure", "boom")

    claim_next(connection)
    fail(connection, START_FEN, "engine_failure", "boom")
    item = observe(connection, START_FEN)
    assert item is not None
    assert item.state == "failed"
    assert item.last_error_code == "engine_failure"
    assert item.last_error_details == "boom"

    with pytest.raises(EvaluationQueueError, match="not running"):
        fail(connection, START_FEN, "engine_failure", "again")


def test_requeue_after_done_and_retry_after_failed(connection: sqlite3.Connection) -> None:
    initialized(connection)

    enqueue(connection, START_FEN)
    claim_next(connection)
    complete(connection, START_FEN, START_FEN)
    outcome, item = enqueue(connection, START_FEN)
    assert outcome == "requeued"
    assert item.state == "queued"
    assert item.position == 2

    claim_next(connection)
    fail(connection, START_FEN, "engine_failure", "boom")
    outcome, item = enqueue(connection, START_FEN)
    assert outcome == "retried"
    assert item.state == "queued"
    assert item.position == 3
    assert item.last_error_code is None


def test_requeue_running_returns_running_to_tail(connection: sqlite3.Connection) -> None:
    initialized(connection)

    enqueue(connection, START_FEN)
    enqueue(connection, SECOND_FEN)
    claim_next(connection)
    claim_next(connection)
    assert pending_count(connection) == (0, 2)

    count = requeue_running(connection)
    assert count == 2
    queued, running = pending_count(connection)
    assert (queued, running) == (2, 0)

    first = claim_next(connection)
    second = claim_next(connection)
    assert [first.fen, second.fen] == [START_FEN, SECOND_FEN]


def test_restart_durability_requeues_interrupted_run(
    connection: sqlite3.Connection,
) -> None:
    initialized(connection)

    enqueue(connection, START_FEN)
    enqueue(connection, SECOND_FEN)
    claim_next(connection)

    # Simulate a restart: the database persists, running work is requeued.
    count = requeue_running(connection)
    assert count == 1
    assert pending_count(connection) == (2, 0)


def test_observe_and_observe_many_are_read_only(connection: sqlite3.Connection) -> None:
    initialized(connection)

    assert observe(connection, START_FEN) is None
    enqueue(connection, START_FEN)
    enqueue(connection, SECOND_FEN)

    observed = observe_many(connection, [START_FEN, SECOND_FEN, THIRD_FEN])
    assert [observed[fen] is not None for fen in (START_FEN, SECOND_FEN)] == [True, True]
    assert observed[THIRD_FEN] is None

    with pytest.raises(EvaluationValidationError, match="bounded"):
        observe_many(connection, [START_FEN] * 100)


def test_validation_and_size_bounds(connection: sqlite3.Connection) -> None:
    initialized(connection)

    with pytest.raises(EvaluationValidationError, match="FEN"):
        enqueue(connection, "not a fen")

    with pytest.raises(EvaluationValidationError, match="128"):
        enqueue(connection, "8/8/8/8/8/8/8/8 w - - 0 1 " + "x" * 200)

    with pytest.raises(EvaluationValidationError, match="FEN"):
        observe(connection, 12345)

    assert chess.Board(THIRD_FEN).is_valid()
