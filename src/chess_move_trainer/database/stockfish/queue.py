"""Transactional operations for the six-column live analysis queue."""

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


class QueueError(RuntimeError):
    """Base class for bounded analysis-queue failures."""


class QueueValidationError(QueueError, ValueError):
    """Raised when a queue operation receives an invalid value."""


class QueueStorageError(QueueError):
    """Raised when the queue cannot safely use its compatible database."""


def _read_observed_queue_state(connection: object, position_id: int) -> str | None:
    """Read and validate one live queue row without changing it."""

    live = _read_live_queue_request(connection, position_id)
    return None if live is None else live.state


@dataclass(frozen=True, slots=True)
class _LiveQueueRequest:
    """Validated live queue data for package-internal composition."""

    quality: AnalysisQuality
    state: str
    requested_at_utc: str
    claimed_at_utc: str | None
    claim_token: str | None


def _read_live_queue_request(
    connection: object,
    position_id: int,
) -> _LiveQueueRequest | None:
    """Read one validated live request without changing it."""

    try:
        row = connection.execute(
            text(
                """
                SELECT daq_requested_quality, daq_state, daq_requested_at_utc,
                       daq_claimed_at_utc, daq_claim_token
                FROM derived_analysis_queue
                WHERE derived_position_id = :position_id
                """
            ),
            {"position_id": position_id},
        ).first()
        if row is None:
            return None
        quality = _normalize_quality(row[0])
        if row[1] not in ("queued", "running"):
            raise ValueError("analysis queue state is malformed")
        _validate_observation_timestamp(row[2], "analysis queue request timestamp")
        if row[1] == "queued":
            if row[3] is not None or row[4] is not None:
                raise ValueError("queued analysis has claim data")
        else:
            if not isinstance(row[4], str) or not row[4]:
                raise ValueError("running analysis has no claim token")
            _validate_observation_timestamp(row[3], "analysis queue claim timestamp")
        return _LiveQueueRequest(
            quality=quality,
            state=row[1],
            requested_at_utc=row[2],
            claimed_at_utc=row[3],
            claim_token=row[4],
        )
    except QueueStorageError:
        raise
    except Exception as error:
        raise QueueStorageError("analysis queue state is malformed") from error


class QueueQualityError(QueueValidationError):
    """Raised when a completion does not match its immutable claimed quality."""


@dataclass(frozen=True, slots=True)
class QueueClaim:
    """The worker-local ticket and quality captured by one queue claim."""

    position_id: int
    quality: AnalysisQuality
    claimed_at_utc: str
    claim_token: str

    def __post_init__(self) -> None:
        if type(self.position_id) is not int or self.position_id < 1:
            raise QueueValidationError("position_id must be a positive integer")
        try:
            object.__setattr__(self, "quality", AnalysisQuality(self.quality))
        except (TypeError, ValueError) as error:
            raise QueueValidationError("claimed quality must be 'browser' or 'tool'") from error
        if not isinstance(self.claimed_at_utc, str) or not self.claimed_at_utc:
            raise QueueValidationError("claimed_at_utc must be a non-empty string")
        if not isinstance(self.claim_token, str) or not self.claim_token:
            raise QueueValidationError("claim_token must be a non-empty string")

    @property
    def claimed_quality(self) -> AnalysisQuality:
        """The immutable quality captured when this ticket was issued."""

        return self.quality


@dataclass(frozen=True, slots=True)
class QueueCompletionOutcome:
    """Result of one matching-token completion attempt."""

    applied: bool
    publication: PublicationOutcome | None = None
    released: bool = False
    deleted: bool = False

    @property
    def stale(self) -> bool:
        """Whether the worker ticket no longer owns the queue row."""

        return not self.applied


class QueueService:
    """Own the live queue lifecycle without holding SQLite during engine work."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        _checkpoint: Callable[[str], None] | None = None,
        _token_factory: Callable[[], str] | None = None,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout
        self._checkpoint = _checkpoint if _checkpoint is not None else lambda _: None
        self._token_factory = _token_factory if _token_factory is not None else _random_token

    def enqueue(
        self,
        position_id: int,
        quality: AnalysisQuality | str,
        *,
        requested_at: datetime | str | None = None,
    ) -> None:
        """Insert or promote one live request without disturbing an active claim."""

        _validate_position_id(position_id)
        normalized_quality = _normalize_quality(quality)
        requested_at_utc = _format_timestamp(requested_at)
        with self._connection() as connection:
            transaction = _begin_immediate(connection)
            try:
                _enqueue_in_transaction(
                    connection,
                    position_id,
                    normalized_quality,
                    requested_at=requested_at_utc,
                )
                transaction.commit()
            except BaseException as error:
                _rollback_if_active(connection, transaction)
                if isinstance(error, (KeyboardInterrupt, SystemExit, AnalysisError, QueueError)):
                    raise
                raise _translate_storage_error(error) from error

    def claim(
        self,
        *,
        now: datetime | str | None = None,
        exclude_position_ids: Collection[int] | None = None,
    ) -> QueueClaim | None:
        """Claim the oldest queued or two-minute-stale running request."""

        current_time = _parse_timestamp(now)
        stale_before = current_time - STALE_CLAIM_AFTER
        claimed_at_utc = _format_timestamp(current_time)
        excluded = frozenset(exclude_position_ids or ())
        if any(type(position_id) is not int or position_id < 1 for position_id in excluded):
            raise QueueValidationError("excluded position ids must be positive integers")
        with self._connection() as connection:
            transaction = _begin_immediate(connection)
            try:
                candidate = _oldest_claimable(connection, stale_before, excluded)
                if candidate is None:
                    transaction.commit()
                    return None
                position_id, quality, state, old_claimed_at, old_token = candidate
                claim_token = self._fresh_token(connection)
                if state == "queued":
                    update = connection.execute(
                        text(
                            """
                            UPDATE derived_analysis_queue
                            SET daq_state = 'running',
                                daq_claimed_at_utc = :claimed_at,
                                daq_claim_token = :claim_token
                            WHERE derived_position_id = :position_id
                              AND daq_state = 'queued'
                            """
                        ),
                        {
                            "position_id": position_id,
                            "claimed_at": claimed_at_utc,
                            "claim_token": claim_token,
                        },
                    )
                else:
                    update = connection.execute(
                        text(
                            """
                            UPDATE derived_analysis_queue
                            SET daq_state = 'running',
                                daq_claimed_at_utc = :claimed_at,
                                daq_claim_token = :claim_token
                            WHERE derived_position_id = :position_id
                              AND daq_state = 'running'
                              AND daq_claimed_at_utc = :old_claimed_at
                              AND daq_claim_token = :old_claim_token
                            """
                        ),
                        {
                            "position_id": position_id,
                            "claimed_at": claimed_at_utc,
                            "claim_token": claim_token,
                            "old_claimed_at": old_claimed_at,
                            "old_claim_token": old_token,
                        },
                    )
                if update.rowcount != 1:
                    raise QueueStorageError("queue claim was superseded before it could be recorded")
                transaction.commit()
                return QueueClaim(
                    position_id=position_id,
                    quality=quality,
                    claimed_at_utc=claimed_at_utc,
                    claim_token=claim_token,
                )
            except BaseException as error:
                _rollback_if_active(connection, transaction)
                if isinstance(error, (KeyboardInterrupt, SystemExit, AnalysisError, QueueError)):
                    raise
                raise _translate_storage_error(error) from error

    def young_running_claim_deadline(
        self,
        *,
        now: datetime | str | None = None,
    ) -> datetime | None:
        """Return the stale boundary for the only remaining young running row.

        This read-only observation is used only after an abandoned database
        mutex acquisition.  A queued row, multiple rows, or an already stale
        running row is deliberately not a recovery window.
        """

        current_time = _parse_timestamp(now)
        with self._connection() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT daq_state, daq_claimed_at_utc, daq_claim_token
                    FROM derived_analysis_queue
                    """
                )
            ).all()
        if len(rows) != 1 or rows[0][0] != "running":
            return None
        claimed_at = rows[0][1]
        if claimed_at is None or rows[0][2] is None:
            raise QueueStorageError("running queue row is missing claim data")
        deadline = _parse_timestamp(claimed_at) + STALE_CLAIM_AFTER
        if deadline <= current_time:
            return None
        return deadline

    def release(self, claim: QueueClaim | int, claim_token: str | None = None) -> bool:
        """Release a matching running ticket back to queued work."""

        position_id, token = _claim_identity(claim, claim_token)
        with self._connection() as connection:
            transaction = _begin_immediate(connection)
            try:
                update = connection.execute(
                    text(
                        """
                        UPDATE derived_analysis_queue
                        SET daq_state = 'queued',
                            daq_claimed_at_utc = NULL,
                            daq_claim_token = NULL
                        WHERE derived_position_id = :position_id
                          AND daq_state = 'running'
                          AND daq_claim_token = :claim_token
                        """
                    ),
                    {"position_id": position_id, "claim_token": token},
                )
                transaction.commit()
                return update.rowcount == 1
            except BaseException:
                _rollback_if_active(connection, transaction)
                raise

    def delete(self, claim: QueueClaim | int, claim_token: str | None = None) -> bool:
        """Delete a matching running ticket after completed or skipped work."""

        position_id, token = _claim_identity(claim, claim_token)
        with self._connection() as connection:
            transaction = _begin_immediate(connection)
            try:
                deleted = connection.execute(
                    text(
                        """
                        DELETE FROM derived_analysis_queue
                        WHERE derived_position_id = :position_id
                          AND daq_state = 'running'
                          AND daq_claim_token = :claim_token
                        """
                    ),
                    {"position_id": position_id, "claim_token": token},
                )
                transaction.commit()
                return deleted.rowcount == 1
            except BaseException:
                _rollback_if_active(connection, transaction)
                raise

    def fail(self, claim: QueueClaim) -> bool:
        """Apply matching-token failure handling without retaining a failure record."""

        position_id, token = _claim_identity(claim, None)
        with self._connection() as connection:
            transaction = _begin_immediate(connection)
            try:
                row = connection.execute(
                    text(
                        """
                        SELECT daq_requested_quality
                        FROM derived_analysis_queue
                        WHERE derived_position_id = :position_id
                          AND daq_state = 'running'
                          AND daq_claim_token = :claim_token
                        """
                    ),
                    {"position_id": position_id, "claim_token": token},
                ).first()
                if row is None:
                    transaction.commit()
                    return False
                requested_quality = _normalize_quality(row[0])
                if _quality_rank(requested_quality) > _quality_rank(claim.quality):
                    changed = connection.execute(
                        text(
                            """
                            UPDATE derived_analysis_queue
                            SET daq_state = 'queued',
                                daq_claimed_at_utc = NULL,
                                daq_claim_token = NULL
                            WHERE derived_position_id = :position_id
                              AND daq_state = 'running'
                              AND daq_claim_token = :claim_token
                            """
                        ),
                        {"position_id": position_id, "claim_token": token},
                    )
                else:
                    changed = connection.execute(
                        text(
                            """
                            DELETE FROM derived_analysis_queue
                            WHERE derived_position_id = :position_id
                              AND daq_state = 'running'
                              AND daq_claim_token = :claim_token
                            """
                        ),
                        {"position_id": position_id, "claim_token": token},
                    )
                transaction.commit()
                return changed.rowcount == 1
            except BaseException:
                _rollback_if_active(connection, transaction)
                raise

    def complete(
        self,
        claim: QueueClaim,
        result: AnalysisResultInput,
    ) -> QueueCompletionOutcome:
        """Publish and finalize one matching ticket in one immediate transaction."""

        position_id, token = _claim_identity(claim, None)
        with self._connection() as connection:
            transaction = _begin_immediate(connection)
            try:
                row = connection.execute(
                    text(
                        """
                        SELECT daq_requested_quality, daq_state, daq_claim_token
                        FROM derived_analysis_queue
                        WHERE derived_position_id = :position_id
                        """
                    ),
                    {"position_id": position_id},
                ).first()
                if row is None or row[1] != "running" or row[2] != token:
                    transaction.rollback()
                    return QueueCompletionOutcome(applied=False)

                requested_quality = _normalize_quality(row[0])
                if not isinstance(result, AnalysisResultInput):
                    raise AnalysisValidationError("result must be an AnalysisResultInput value")
                if result.quality is not claim.quality:
                    raise QueueQualityError(
                        "result quality must match the immutable claimed quality"
                    )
                if _quality_rank(requested_quality) < _quality_rank(claim.quality):
                    raise QueueQualityError("queue requested quality cannot downgrade a claim")

                validated = _prepare_publication(connection, position_id, result)
                publication = _publish_in_transaction(
                    connection,
                    position_id,
                    result,
                    validated,
                    self._checkpoint,
                )
                promoted = _quality_rank(requested_quality) > _quality_rank(claim.quality)
                if promoted:
                    transitioned = connection.execute(
                        text(
                            """
                            UPDATE derived_analysis_queue
                            SET daq_state = 'queued',
                                daq_claimed_at_utc = NULL,
                                daq_claim_token = NULL
                            WHERE derived_position_id = :position_id
                              AND daq_state = 'running'
                              AND daq_claim_token = :claim_token
                            """
                        ),
                        {"position_id": position_id, "claim_token": token},
                    )
                    if transitioned.rowcount != 1:
                        raise QueueStorageError("queue completion lost its matching claim")
                else:
                    transitioned = connection.execute(
                        text(
                            """
                            DELETE FROM derived_analysis_queue
                            WHERE derived_position_id = :position_id
                              AND daq_state = 'running'
                              AND daq_claim_token = :claim_token
                            """
                        ),
                        {"position_id": position_id, "claim_token": token},
                    )
                    if transitioned.rowcount != 1:
                        raise QueueStorageError("queue completion lost its matching claim")
                transaction.commit()
                return QueueCompletionOutcome(
                    applied=True,
                    publication=publication,
                    released=promoted,
                    deleted=not promoted,
                )
            except BaseException as error:
                _rollback_if_active(connection, transaction)
                if isinstance(error, (KeyboardInterrupt, SystemExit, AnalysisError, QueueError)):
                    raise
                raise _translate_storage_error(error) from error

    def _connection(self):
        try:
            return _checked_connection(self._database_path, self._lock_timeout)
        except (FileNotFoundError, ValueError):
            raise
        except Exception as error:
            raise _translate_queue_error(error) from error

    def _fresh_token(self, connection: object) -> str:
        for _ in range(10):
            token = self._token_factory()
            if not isinstance(token, str) or not token:
                raise QueueStorageError("claim token factory returned an invalid token")
            exists = connection.execute(
                text(
                    "SELECT 1 FROM derived_analysis_queue WHERE daq_claim_token = :claim_token"
                ),
                {"claim_token": token},
            ).first()
            if exists is None:
                return token
        raise QueueStorageError("could not create a fresh unique queue claim token")


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


AnalysisQueue = QueueService
QueueRepository = QueueService


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


def _normalize_quality(value: object) -> AnalysisQuality:
    try:
        return AnalysisQuality(value)
    except (TypeError, ValueError) as error:
        raise QueueValidationError("quality must be 'browser' or 'tool'") from error


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


def _validate_observation_timestamp(value: object, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} is malformed")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} is malformed") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} is malformed")


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


__all__ = [
    "AnalysisQueue",
    "QueueClaim",
    "QueueCompletionOutcome",
    "QueueError",
    "QueueQualityError",
    "QueueRepository",
    "QueueService",
    "QueueStorageError",
    "QueueValidationError",
    "STALE_CLAIM_AFTER",
]
