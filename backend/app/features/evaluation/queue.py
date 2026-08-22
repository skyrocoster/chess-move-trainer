"""Durable FIFO evaluation queue with exact-FEN dedupe and explicit transitions."""

from __future__ import annotations

import sqlite3
import time
from datetime import UTC, datetime
from typing import Callable

from backend.app.features.analysis import AnalysisBusyError, AnalysisValidationError, canonical_fen

from .errors import EvaluationQueueError, EvaluationValidationError
from .models import EvaluationQueueItem
from .schema import require_evaluation_schema

MAX_FEN_LENGTH = 128
MAX_OBSERVE_FENS = 64

_QUEUE_COLUMNS = (
    "fen, state, position, attempts, schema_version, enqueued_at, "
    "started_at, finished_at, last_error_code, last_error_details"
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _is_busy(error: sqlite3.Error) -> bool:
    message = str(error).lower()
    return "locked" in message or "busy" in message


def _begin_immediate(connection: sqlite3.Connection) -> None:
    try:
        connection.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError as error:
        if _is_busy(error):
            raise AnalysisBusyError(
                "evaluation coordinator could not acquire SQLite writer lock"
            ) from error
        raise


def _transaction(connection: sqlite3.Connection, operation: Callable[[], None]) -> None:
    for attempt in range(3):
        try:
            _begin_immediate(connection)
            operation()
            connection.commit()
            return
        except AnalysisBusyError:
            connection.rollback()
            if attempt == 2:
                raise
            time.sleep(0.02 * (attempt + 1))
        except Exception:
            connection.rollback()
            raise


def _canonical(fen: object) -> str:
    if not isinstance(fen, str) or len(fen) > MAX_FEN_LENGTH:
        raise EvaluationValidationError(
            f"FEN must be a string no longer than {MAX_FEN_LENGTH} characters"
        )
    try:
        return canonical_fen(fen)
    except AnalysisValidationError as error:
        raise EvaluationValidationError(str(error)) from error


def _item_from_row(row: tuple[object, ...]) -> EvaluationQueueItem:
    return EvaluationQueueItem(
        fen=str(row[0]),
        state=str(row[1]),
        position=int(row[2]),
        attempts=int(row[3]),
        enqueued_at=str(row[5]),
        started_at=None if row[6] is None else str(row[6]),
        finished_at=None if row[7] is None else str(row[7]),
        last_error_code=None if row[8] is None else str(row[8]),
        last_error_details=None if row[9] is None else str(row[9]),
    )


def _next_position(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        "SELECT COALESCE(MAX(position), 0) + 1 FROM evaluation_queue"
    ).fetchone()
    return int(row[0])


def enqueue(connection: sqlite3.Connection, fen: object) -> tuple[str, EvaluationQueueItem]:
    """Accept evaluation work with exact-FEN dedupe; never duplicates queued/running work.

    Returns (outcome, item): queued (new), already_queued, already_running (dedupe),
    requeued (done -> queued), or retried (failed -> queued).
    """

    require_evaluation_schema(connection)
    selected = _canonical(fen)
    outcome = "queued"
    item: EvaluationQueueItem | None = None

    def operation() -> None:
        nonlocal outcome, item
        row = connection.execute(
            f"SELECT {_QUEUE_COLUMNS} FROM evaluation_queue WHERE fen = ?", (selected,)
        ).fetchone()
        if row is None:
            position = _next_position(connection)
            connection.execute(
                "INSERT INTO evaluation_queue "
                "(fen, state, position, attempts, schema_version, enqueued_at, "
                "started_at, finished_at, last_error_code, last_error_details) "
                "VALUES (?, 'queued', ?, 0, ?, ?, NULL, NULL, NULL, NULL)",
                (selected, position, 1, _now()),
            )
            outcome = "queued"
            item = _item_from_row(
                connection.execute(
                    f"SELECT {_QUEUE_COLUMNS} FROM evaluation_queue WHERE fen = ?",
                    (selected,),
                ).fetchone()
            )
            return
        existing = _item_from_row(row)
        if existing.state in ("queued", "running"):
            outcome = f"already_{existing.state}"
            item = existing
            return
        position = _next_position(connection)
        connection.execute(
            "UPDATE evaluation_queue SET state = 'queued', position = ?, "
            "started_at = NULL, finished_at = NULL, "
            "last_error_code = NULL, last_error_details = NULL WHERE fen = ?",
            (position, selected),
        )
        outcome = "requeued" if existing.state == "done" else "retried"
        item = _item_from_row(
            connection.execute(
                f"SELECT {_QUEUE_COLUMNS} FROM evaluation_queue WHERE fen = ?",
                (selected,),
            ).fetchone()
        )

    _transaction(connection, operation)
    assert item is not None
    return outcome, item


def claim_next(connection: sqlite3.Connection) -> EvaluationQueueItem | None:
    """Claim the oldest queued item for a worker; FIFO by position, atomically."""

    require_evaluation_schema(connection)
    item: EvaluationQueueItem | None = None

    def operation() -> None:
        nonlocal item
        row = connection.execute(
            f"SELECT {_QUEUE_COLUMNS} FROM evaluation_queue "
            "WHERE state = 'queued' ORDER BY position ASC LIMIT 1"
        ).fetchone()
        if row is None:
            return
        connection.execute(
            "UPDATE evaluation_queue SET state = 'running', started_at = ? WHERE fen = ?",
            (_now(), row[0]),
        )
        item = _item_from_row(
            connection.execute(
                f"SELECT {_QUEUE_COLUMNS} FROM evaluation_queue WHERE fen = ?",
                (row[0],),
            ).fetchone()
        )

    _transaction(connection, operation)
    return item


def complete(connection: sqlite3.Connection, fen: object, result_fen: object) -> None:
    """Mark a running item done after its complete result was published."""

    require_evaluation_schema(connection)
    selected = _canonical(fen)
    selected_result = _canonical(result_fen)
    if selected_result != selected:
        raise EvaluationValidationError("result FEN does not match the queued item")

    def operation() -> None:
        row = connection.execute(
            "SELECT state FROM evaluation_queue WHERE fen = ?", (selected,)
        ).fetchone()
        if row is None or row[0] != "running":
            raise EvaluationQueueError("cannot complete an item that is not running")
        connection.execute(
            "UPDATE evaluation_queue SET state = 'done', finished_at = ? WHERE fen = ?",
            (_now(), selected),
        )

    _transaction(connection, operation)


def fail(
    connection: sqlite3.Connection,
    fen: object,
    error_code: str,
    details: str,
) -> None:
    """Record a final failure; no automatic retry is performed."""

    require_evaluation_schema(connection)
    selected = _canonical(fen)

    def operation() -> None:
        row = connection.execute(
            "SELECT state FROM evaluation_queue WHERE fen = ?", (selected,)
        ).fetchone()
        if row is None or row[0] != "running":
            raise EvaluationQueueError("cannot fail an item that is not running")
        connection.execute(
            "UPDATE evaluation_queue SET state = 'failed', finished_at = ?, "
            "last_error_code = ?, last_error_details = ? WHERE fen = ?",
            (_now(), error_code[:200], details[:2000], selected),
        )

    _transaction(connection, operation)


def requeue_running(connection: sqlite3.Connection) -> int:
    """Move every running item back to the FIFO tail; restart durability."""

    require_evaluation_schema(connection)
    count = 0

    def operation() -> None:
        nonlocal count
        rows = connection.execute(
            "SELECT fen FROM evaluation_queue WHERE state = 'running' ORDER BY position ASC"
        ).fetchall()
        base = _next_position(connection)
        for index, (fen,) in enumerate(rows):
            connection.execute(
                "UPDATE evaluation_queue SET state = 'queued', position = ?, "
                "started_at = NULL, finished_at = NULL, "
                "last_error_code = NULL, last_error_details = NULL WHERE fen = ?",
                (base + index, fen),
            )
            count += 1

    _transaction(connection, operation)
    return count


def observe(connection: sqlite3.Connection, fen: object) -> EvaluationQueueItem | None:
    """Read-only queue state for one exact FEN; never computes."""

    require_evaluation_schema(connection)
    selected = _canonical(fen)
    row = connection.execute(
        f"SELECT {_QUEUE_COLUMNS} FROM evaluation_queue WHERE fen = ?", (selected,)
    ).fetchone()
    return _item_from_row(row) if row is not None else None


def observe_many(
    connection: sqlite3.Connection, fens: object
) -> dict[str, EvaluationQueueItem | None]:
    """Read-only queue state for a bounded set of exact FENs; never computes."""

    require_evaluation_schema(connection)
    if not isinstance(fens, (list, tuple)):
        raise EvaluationValidationError("FEN list must be a bounded sequence")
    if len(fens) > MAX_OBSERVE_FENS:
        raise EvaluationValidationError(
            f"observation is bounded to {MAX_OBSERVE_FENS} FENs per request"
        )
    selected = tuple(_canonical(fen) for fen in fens)
    found: dict[str, EvaluationQueueItem | None] = {}
    for start in range(0, len(selected), 100):
        chunk = tuple(selected[start : start + 100])
        placeholders = ",".join("?" for _ in chunk)
        rows = connection.execute(
            f"SELECT {_QUEUE_COLUMNS} FROM evaluation_queue WHERE fen IN ({placeholders})",
            chunk,
        ).fetchall()
        for row in rows:
            item = _item_from_row(row)
            found[item.fen] = item
    return {fen: found.get(fen) for fen in selected}


def pending_count(connection: sqlite3.Connection) -> tuple[int, int]:
    """Return (queued, running) counts for observability and drain control."""

    require_evaluation_schema(connection)
    row = connection.execute(
        "SELECT "
        "SUM(CASE WHEN state = 'queued' THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN state = 'running' THEN 1 ELSE 0 END) "
        "FROM evaluation_queue"
    ).fetchone()
    return int(row[0] or 0), int(row[1] or 0)
