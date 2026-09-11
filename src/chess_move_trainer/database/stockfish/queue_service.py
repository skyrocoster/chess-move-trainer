"""Transactional live analysis queue service."""

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

from .queue_helpers import _begin_immediate, _checked_connection, _claim_identity, _enqueue_in_transaction, _format_timestamp, _oldest_claimable, _parse_timestamp, _quality_rank, _random_token, _rollback_if_active, _translate_queue_error, _validate_position_id
from .queue_models import _normalize_quality, _validate_observation_timestamp
from .queue_models import QueueClaim, QueueCompletionOutcome, QueueError, QueueQualityError, QueueStorageError, QueueValidationError


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
                    raise QueueStorageError(
                        "queue claim was superseded before it could be recorded"
                    )
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


AnalysisQueue = QueueService
QueueRepository = QueueService
