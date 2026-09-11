"""Queue transactions, timestamps, and validation."""

from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Callable, Collection
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterator

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from ..analysis import (
    AnalysisError,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisValidationError,
    PublicationOutcome,
)
from ..analysis.repository import (
    _prepare_publication,
    _publish_in_transaction,
    _translate_storage_error,
)
from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..schema import SchemaIncompatibleError, _assert_compatible_schema

STALE_CLAIM_AFTER = timedelta(minutes=2)

from .queue_models import QueueClaim, _normalize_quality, _validate_observation_timestamp


def _enqueue_in_transaction(
    connection: object,
    position_id: int,
    quality: AnalysisQuality | str,
    *,
    requested_at: datetime | str | None = None,
) -> None:
    """Insert or promote one request on a caller-owned transaction.

    The caller owns the immediate transaction and its rollback/commit.  The
    statement intentionally matches ``QueueService.enqueue``: quality uses
    max semantics and the running claim columns are not updated.
    """

    _validate_position_id(position_id)
    normalized_quality = _normalize_quality(quality)
    requested_at_utc = _format_timestamp(requested_at)
    connection.execute(
        text(
            """
            INSERT INTO derived_analysis_queue (
                derived_position_id,
                daq_requested_quality,
                daq_state,
                daq_requested_at_utc,
                daq_claimed_at_utc,
                daq_claim_token
            ) VALUES (
                :position_id, :quality, 'queued', :requested_at, NULL, NULL
            )
            ON CONFLICT (derived_position_id) DO UPDATE SET
                daq_requested_quality = CASE
                    WHEN derived_analysis_queue.daq_requested_quality = 'tool'
                      OR excluded.daq_requested_quality = 'tool'
                    THEN 'tool'
                    ELSE 'browser'
                END,
                daq_requested_at_utc = excluded.daq_requested_at_utc
            """
        ),
        {
            "position_id": position_id,
            "quality": normalized_quality.value,
            "requested_at": requested_at_utc,
        },
    )




@contextmanager
def _checked_connection(
    database_path: str | Path,
    lock_timeout: float,
) -> Iterator[object]:
    with _open_existing_connection(database_path, lock_timeout) as connection:
        try:
            _assert_compatible_schema(connection, lock_timeout)
        except BaseException as error:
            if isinstance(error, (KeyboardInterrupt, SystemExit, QueueError)):
                raise
            raise _translate_queue_error(error) from error
        yield connection


def _oldest_claimable(
    connection: object,
    stale_before: datetime,
    excluded_position_ids: Collection[int] = (),
):
    rows = connection.execute(
        text(
            """
            SELECT derived_position_id, daq_requested_quality, daq_state,
                   daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token
            FROM derived_analysis_queue
            WHERE daq_state IN ('queued', 'running')
            """
        )
    ).all()
    candidates: list[tuple[datetime, int, AnalysisQuality, str, str | None, str | None]] = []
    for row in rows:
        position_id = row[0]
        if type(position_id) is not int or position_id < 1:
            raise QueueStorageError("queue contains an invalid position id")
        if position_id in excluded_position_ids:
            continue
        quality = _normalize_quality(row[1])
        state = row[2]
        requested_at = _parse_timestamp(row[3])
        claimed_at = row[4]
        token = row[5]
        if state == "queued":
            if claimed_at is not None or token is not None:
                raise QueueStorageError("queued queue row has claim data")
        elif state == "running":
            if claimed_at is None or token is None:
                raise QueueStorageError("running queue row is missing claim data")
            if _parse_timestamp(claimed_at) > stale_before:
                continue
        else:
            raise QueueStorageError("queue contains an invalid state")
        candidates.append((requested_at, position_id, quality, state, claimed_at, token))
    if not candidates:
        return None
    candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))
    _, position_id, quality, state, claimed_at, token = candidates[0]
    return position_id, quality, state, claimed_at, token


def _claim_identity(
    claim: QueueClaim | int,
    claim_token: str | None,
) -> tuple[int, str]:
    if isinstance(claim, QueueClaim):
        if claim_token is not None:
            raise QueueValidationError("claim_token must not be supplied with a QueueClaim")
        return claim.position_id, claim.claim_token
    _validate_position_id(claim)
    if not isinstance(claim_token, str) or not claim_token:
        raise QueueValidationError("claim_token must be a non-empty string")
    return claim, claim_token


def _validate_position_id(position_id: object) -> None:
    if type(position_id) is not int or position_id < 1:
        raise QueueValidationError("position_id must be a positive integer")


def _quality_rank(value: AnalysisQuality) -> int:
    return 0 if value is AnalysisQuality.BROWSER else 1


def _parse_timestamp(value: datetime | str | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise QueueValidationError("queue timestamps must be ISO-8601 values") from error
    else:
        raise QueueValidationError("queue timestamps must be datetime or ISO-8601 values")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise QueueValidationError("queue timestamps must include a UTC offset")
    return parsed.astimezone(UTC)


def _format_timestamp(value: datetime | str | None) -> str:
    return _parse_timestamp(value).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _random_token() -> str:
    return str(uuid.uuid4())


def _begin_immediate(connection: object):
    connection.exec_driver_sql("BEGIN IMMEDIATE")
    transaction = connection.get_transaction()
    if transaction is None:
        raise QueueStorageError("SQLite did not establish the immediate queue transaction")
    return transaction


def _rollback_if_active(connection: object, transaction: object) -> None:
    if connection.in_transaction():
        transaction.rollback()


def _translate_queue_error(error: Exception) -> QueueError:
    if isinstance(error, QueueError):
        return error
    if isinstance(error, AnalysisError):
        return error  # type: ignore[return-value]
    if isinstance(error, SchemaIncompatibleError):
        return QueueStorageError("database is not a readable compatible schema v1 database")
    candidate: BaseException | None = error
    while candidate is not None:
        if isinstance(candidate, sqlite3.OperationalError) and "locked" in str(candidate).lower():
            return QueueStorageError("analysis queue writer lock was not acquired before timeout")
        candidate = candidate.__cause__ or candidate.__context__
    if isinstance(error, OperationalError) and "locked" in str(error).lower():
        return QueueStorageError("analysis queue writer lock was not acquired before timeout")
    return QueueStorageError("analysis queue database operation failed")
