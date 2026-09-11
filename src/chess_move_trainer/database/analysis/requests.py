"""Atomic desired-quality analysis requests for one public FEN."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

from sqlalchemy.exc import OperationalError

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions.canonicalization import CanonicalPosition, canonicalize_fen
from ..positions.repository import (
    PositionStorageError,
    _resolve_canonical_position,
)
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .models import (
    AnalysisError,
    AnalysisQuality,
    AnalysisStorageError,
    AnalysisValidationError,
)
from .observation import (
    AnalysisObservation,
    AnalysisObservationError,
    AnalysisObservationResult,
    _canonical_fen,
    _materialize_observation,
    _observation_result,
)
from .reading import AnalysisReadError, AnalysisReadResult, _read_current_result


class AnalysisRequestError(AnalysisError):
    """Base class for bounded desired-analysis request failures."""


class AnalysisRequestValidationError(
    AnalysisRequestError, AnalysisValidationError
):
    """Raised when a desired-analysis request is invalid."""


class AnalysisRequestStorageError(AnalysisRequestError, AnalysisStorageError):
    """Raised when desired-analysis storage cannot be used safely."""


class AnalysisRequestSchemaError(AnalysisRequestStorageError):
    """Raised when the selected database is not the exact supported schema."""


class AnalysisRequestDisposition(str, Enum):
    """The package-private reason for the request response status."""

    RESULT_REUSED = "result_reused"
    LIVE_REUSED = "live_reused"
    ENQUEUED = "enqueued"
    PROMOTED = "promoted"


@dataclass(frozen=True, slots=True)
class AnalysisRequest:
    """One canonical public FEN and its fixed desired quality."""

    fen: str
    quality: AnalysisQuality = AnalysisQuality.BROWSER

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (TypeError, ValueError) as error:
            raise AnalysisRequestValidationError(
                "fen must be a complete legal FEN"
            ) from error
        try:
            quality = AnalysisQuality(self.quality)
        except (TypeError, ValueError) as error:
            raise AnalysisRequestValidationError(
                "quality must be 'browser' or 'tool'"
            ) from error
        object.__setattr__(self, "fen", _canonical_fen(position))
        object.__setattr__(self, "quality", quality)


@dataclass(frozen=True, slots=True)
class AnalysisRequestResult:
    """The current observation and status-translation disposition."""

    observation: AnalysisObservation
    disposition: AnalysisRequestDisposition

    def __post_init__(self) -> None:
        if not isinstance(self.observation, AnalysisObservation):
            raise AnalysisRequestStorageError("analysis observation value is malformed")
        try:
            object.__setattr__(
                self, "disposition", AnalysisRequestDisposition(self.disposition)
            )
        except (TypeError, ValueError) as error:
            raise AnalysisRequestStorageError(
                "analysis request disposition is malformed"
            ) from error


class AnalysisRequestRepository:
    """Compose one desired-result request through an explicit database path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        _checkpoint: Callable[[str], None] | None = None,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout
        self._checkpoint = _checkpoint if _checkpoint is not None else lambda _: None

    def request(
        self,
        request: AnalysisRequest | str,
        quality: AnalysisQuality | str = AnalysisQuality.BROWSER,
    ) -> AnalysisRequestResult:
        """Request one current analysis result atomically."""

        normalized_request = (
            request
            if isinstance(request, AnalysisRequest)
            else AnalysisRequest(request, quality)
        )
        return self._request(normalized_request)

    def _request(self, request: AnalysisRequest) -> AnalysisRequestResult:
        # Local import: stockfish.queue needs analysis at load time, so importing
        # it here keeps both import orders working.
        from ..stockfish.queue import _enqueue_in_transaction, _read_live_queue_request

        try:
            with _open_existing_connection(
                self._database_path, self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                connection.rollback()

                self._checkpoint("before_lock")
                connection.exec_driver_sql("BEGIN IMMEDIATE")
                transaction = connection.get_transaction()
                if transaction is None:
                    connection.rollback()
                    raise AnalysisRequestStorageError(
                        "SQLite did not establish the immediate analysis request transaction"
                    )

                try:
                    self._checkpoint("locked")
                    position = _canonicalize_request_fen(request.fen)
                    position_id = _resolve_canonical_position(connection, position)
                    self._checkpoint("position_resolved")

                    current_result = _read_current_result(connection, position_id)
                    _validate_current_result(current_result, position)
                    live_request = _read_live_queue_request(connection, position_id)

                    if live_request is not None:
                        if _quality_rank(live_request.quality) < _quality_rank(
                            request.quality
                        ):
                            _enqueue_in_transaction(
                                connection,
                                position_id,
                                request.quality,
                            )
                            self._checkpoint("queue_promoted")
                            live_request = _read_live_queue_request(
                                connection, position_id
                            )
                            if live_request is None:
                                raise AnalysisRequestStorageError(
                                    "promoted analysis request was not returned"
                                )
                            disposition = AnalysisRequestDisposition.PROMOTED
                        else:
                            disposition = AnalysisRequestDisposition.LIVE_REUSED
                    elif _result_satisfies(current_result, request.quality):
                        disposition = AnalysisRequestDisposition.RESULT_REUSED
                    else:
                        _enqueue_in_transaction(
                            connection,
                            position_id,
                            request.quality,
                        )
                        self._checkpoint("queue_enqueued")
                        live_request = _read_live_queue_request(
                            connection, position_id
                        )
                        if live_request is None:
                            raise AnalysisRequestStorageError(
                                "enqueued analysis request was not returned"
                            )
                        disposition = AnalysisRequestDisposition.ENQUEUED

                    observation = _materialize_observation(
                        connection,
                        position,
                        position_id,
                        queue_state=(
                            None if live_request is None else live_request.state
                        ),
                    )
                    self._checkpoint("before_commit")
                    transaction.commit()
                except BaseException:
                    if connection.in_transaction():
                        transaction.rollback()
                    raise
                return AnalysisRequestResult(observation, disposition)
        except AnalysisRequestError:
            raise
        except SchemaIncompatibleError as error:
            raise AnalysisRequestSchemaError(str(error)) from error
        except Exception as error:
            raise _translate_storage_error(error) from error


def request_analysis(
    database_path: str | Path,
    fen: str | AnalysisRequest,
    quality: AnalysisQuality | str = AnalysisQuality.BROWSER,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> AnalysisRequestResult:
    """Request one desired analysis through an explicit rebuilt database path."""

    return AnalysisRequestRepository(
        database_path,
        lock_timeout=lock_timeout,
    ).request(fen, quality)


def _canonicalize_request_fen(fen: str) -> CanonicalPosition:
    try:
        return canonicalize_fen(fen)
    except (TypeError, ValueError) as error:
        raise AnalysisRequestValidationError(
            "fen must be a complete legal FEN"
        ) from error


def _validate_current_result(
    result: AnalysisReadResult | None,
    position: CanonicalPosition,
) -> AnalysisObservationResult | None:
    try:
        return _observation_result(result, position)
    except AnalysisObservationError as error:
        raise AnalysisRequestStorageError(
            "analysis result is incomplete or malformed"
        ) from error


def _result_satisfies(
    result: AnalysisReadResult | None,
    requested_quality: AnalysisQuality,
) -> bool:
    # Local import: see _request above for why this stays out of module scope.
    from ..stockfish.configuration import CONFIGURATION_VERSION, STOCKFISH_VERSION

    if result is None:
        return False
    if _quality_rank(result.quality) > _quality_rank(requested_quality):
        return True
    if result.quality is not requested_quality:
        return False
    return (
        result.configuration_version == CONFIGURATION_VERSION
        and result.engine_version == STOCKFISH_VERSION
    )


def _quality_rank(quality: AnalysisQuality) -> int:
    return 0 if quality is AnalysisQuality.BROWSER else 1


def _translate_storage_error(error: Exception) -> AnalysisRequestStorageError:
    # Local import: see _request above for why this stays out of module scope.
    from ..stockfish.queue import QueueStorageError

    candidate: BaseException | None = error
    while candidate is not None:
        if isinstance(candidate, sqlite3.OperationalError) and "locked" in str(
            candidate
        ).lower():
            return AnalysisRequestStorageError(
                "analysis request writer lock was not acquired before timeout"
            )
        candidate = candidate.__cause__ or candidate.__context__
    if isinstance(error, OperationalError) and "locked" in str(error).lower():
        return AnalysisRequestStorageError(
            "analysis request writer lock was not acquired before timeout"
        )
    if isinstance(error, PositionStorageError):
        return AnalysisRequestStorageError(
            "canonical position could not be resolved"
        )
    if isinstance(error, QueueStorageError):
        return AnalysisRequestStorageError(
            "analysis queue could not be used safely"
        )
    if isinstance(error, AnalysisReadError):
        return AnalysisRequestStorageError(
            "analysis result could not be read"
        )
    if isinstance(error, AnalysisObservationError):
        return AnalysisRequestStorageError(
            "analysis observation could not be materialized"
        )
    return AnalysisRequestStorageError("analysis request could not be completed")


__all__ = [
    "AnalysisRequest",
    "AnalysisRequestDisposition",
    "AnalysisRequestError",
    "AnalysisRequestRepository",
    "AnalysisRequestResult",
    "AnalysisRequestSchemaError",
    "AnalysisRequestStorageError",
    "AnalysisRequestValidationError",
    "request_analysis",
]
