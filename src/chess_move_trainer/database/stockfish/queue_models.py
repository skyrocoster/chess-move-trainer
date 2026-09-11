"""Queue errors, claims, and live-request views."""

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


def _normalize_quality(value: object) -> AnalysisQuality:
    try:
        return AnalysisQuality(value)
    except (TypeError, ValueError) as error:
        raise QueueValidationError("quality must be 'browser' or 'tool'") from error


def _validate_observation_timestamp(value: object, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} is malformed")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} is malformed") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} is malformed")
