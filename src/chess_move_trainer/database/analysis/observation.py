"""Read-only FEN-facing observation of current analysis state and result."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..positions.canonicalization import (
    CanonicalPosition,
    PositionValidationError,
    canonicalize_fen,
)
from ..positions.repository import (
    PositionStorageError,
    _find_existing_position_id,
)
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .models import (
    AnalysisError,
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisStorageError,
    AnalysisTerminalKind,
    AnalysisValidationError,
)
from .reading import AnalysisReadError, AnalysisReadResult, _read_current_result
from .validation import validate_analysis_position, validate_settings_object


class AnalysisObservationError(AnalysisError):
    """Base class for bounded FEN-observation failures."""


class AnalysisObservationValidationError(
    AnalysisObservationError, AnalysisValidationError
):
    """Raised when an observation request is invalid."""


class AnalysisObservationStorageError(AnalysisObservationError, AnalysisStorageError):
    """Raised when a compatible database cannot provide a valid observation."""


class AnalysisObservationSchemaError(AnalysisObservationStorageError):
    """Raised when the selected database is not the exact supported schema."""


class AnalysisObservationState(str, Enum):
    """The four public lifecycle states for one current-analysis observation."""

    NOT_REQUESTED = "not_requested"
    QUEUED = "queued"
    RUNNING = "running"
    READY = "ready"


@dataclass(frozen=True, slots=True)
class AnalysisObservationRequest:
    """One complete FEN normalized to the database's canonical identity."""

    fen: str

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (PositionValidationError, TypeError, ValueError) as error:
            raise AnalysisObservationValidationError(
                "fen must be a complete legal FEN"
            ) from error
        object.__setattr__(self, "fen", _canonical_fen(position))


@dataclass(frozen=True, slots=True)
class AnalysisObservationResult:
    """The complete current result without its private position identity."""

    quality: AnalysisQuality
    configuration_version: int
    settings: Mapping[str, Any]
    engine_name: str
    engine_version: str
    terminal_kind: AnalysisTerminalKind | None
    lines: tuple[AnalysisLine, ...]

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "quality", AnalysisQuality(self.quality))
            object.__setattr__(self, "settings", validate_settings_object(self.settings))
            if self.terminal_kind is not None:
                object.__setattr__(
                    self, "terminal_kind", AnalysisTerminalKind(self.terminal_kind)
                )
            normalized_lines = tuple(self.lines)
        except (TypeError, ValueError) as error:
            raise AnalysisObservationStorageError(
                "analysis result value is malformed"
            ) from error
        if type(self.configuration_version) is not int or self.configuration_version < 1:
            raise AnalysisObservationStorageError(
                "analysis result configuration is malformed"
            )
        if not isinstance(self.engine_name, str) or not self.engine_name:
            raise AnalysisObservationStorageError(
                "analysis result engine name is malformed"
            )
        if not isinstance(self.engine_version, str) or not self.engine_version:
            raise AnalysisObservationStorageError(
                "analysis result engine version is malformed"
            )
        if any(not isinstance(line, AnalysisLine) for line in normalized_lines):
            raise AnalysisObservationStorageError("analysis result lines are malformed")
        if tuple(line.rank for line in normalized_lines) != tuple(
            range(1, len(normalized_lines) + 1)
        ):
            raise AnalysisObservationStorageError(
                "analysis result lines are not complete and contiguous"
            )
        if self.terminal_kind is not None and normalized_lines:
            raise AnalysisObservationStorageError(
                "terminal analysis result has candidate lines"
            )
        if self.terminal_kind is None and not normalized_lines:
            raise AnalysisObservationStorageError(
                "analysis result has no candidate lines"
            )
        object.__setattr__(self, "lines", normalized_lines)


@dataclass(frozen=True, slots=True)
class AnalysisObservation:
    """The public canonical FEN, lifecycle state, and optional current result."""

    fen: str
    state: AnalysisObservationState
    result: AnalysisObservationResult | None

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "state", AnalysisObservationState(self.state))
        except (TypeError, ValueError) as error:
            raise AnalysisObservationStorageError("analysis state is malformed") from error
        if self.result is not None and not isinstance(
            self.result, AnalysisObservationResult
        ):
            raise AnalysisObservationStorageError("analysis result value is malformed")
        if self.state is AnalysisObservationState.READY and self.result is None:
            raise AnalysisObservationStorageError("ready analysis has no result")
        if self.state is AnalysisObservationState.NOT_REQUESTED and self.result is not None:
            raise AnalysisObservationStorageError(
                "not-requested analysis has a result"
            )


class AnalysisObservationRepository:
    """Compose one FEN observation through an explicit read-only database path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def read(self, request: AnalysisObservationRequest) -> AnalysisObservation:
        """Read one observation without resolving or creating a position."""

        if not isinstance(request, AnalysisObservationRequest):
            raise AnalysisObservationValidationError(
                "request must be an AnalysisObservationRequest value"
            )

        # Local import: stockfish.queue needs analysis at load time, so importing
        # it here keeps both import orders working.
        from ..stockfish.queue import QueueStorageError, _read_observed_queue_state

        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                position = canonicalize_fen(request.fen)
                position_id = _find_existing_position_id(connection, position)
                if position_id is None:
                    return _sparse_observation(request.fen)
                queue_state = _read_observed_queue_state(connection, position_id)
                return _materialize_observation(
                    connection,
                    position,
                    position_id,
                    queue_state=queue_state,
                )
        except SchemaIncompatibleError as error:
            raise AnalysisObservationSchemaError(str(error)) from error
        except AnalysisObservationError:
            raise
        except (
            AnalysisReadError,
            PositionStorageError,
            QueueStorageError,
    ) as error:
            raise AnalysisObservationStorageError(
                "analysis observation could not be read"
            ) from error
        except Exception as error:
            raise AnalysisObservationStorageError(
                "analysis observation could not be read"
            ) from error

    get = read


def read_analysis_observation(
    database_path: str | Path,
    fen: str | AnalysisObservationRequest,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> AnalysisObservation:
    """Read one FEN observation from an explicit rebuilt database path."""

    if isinstance(fen, AnalysisObservationRequest):
        request = fen
    else:
        request = AnalysisObservationRequest(fen)
    return AnalysisObservationRepository(
        database_path, lock_timeout=lock_timeout
    ).read(request)


get_analysis_observation = read_analysis_observation


def _materialize_observation(
    connection: object,
    position: CanonicalPosition,
    position_id: int,
    *,
    queue_state: str | None,
) -> AnalysisObservation:
    """Materialize one observation on a caller-owned connection."""

    current_result = _read_current_result(connection, position_id)
    result = _observation_result(current_result, position)
    state = _analysis_state(queue_state, result)
    return AnalysisObservation(fen=_canonical_fen(position), state=state, result=result)


def _sparse_observation(fen: str) -> AnalysisObservation:
    return AnalysisObservation(
        fen=fen,
        state=AnalysisObservationState.NOT_REQUESTED,
        result=None,
    )


def _observation_result(
    result: AnalysisReadResult | None,
    position: CanonicalPosition,
) -> AnalysisObservationResult | None:
    if result is None:
        return None
    try:
        validated = validate_analysis_position(
            position,
            AnalysisResultInput(
                quality=result.quality,
                configuration_version=result.configuration_version,
                settings=result.settings,
                engine_name=result.engine_name,
                engine_version=result.engine_version,
                lines=result.lines,
            ),
        )
    except (AnalysisError, TypeError, ValueError) as error:
        raise AnalysisObservationStorageError(
            "analysis result is incomplete or malformed"
        ) from error
    if validated.terminal_kind is not result.terminal_kind:
        raise AnalysisObservationStorageError(
            "analysis result terminal kind is malformed"
        )
    return AnalysisObservationResult(
        quality=result.quality,
        configuration_version=result.configuration_version,
        settings=result.settings,
        engine_name=result.engine_name,
        engine_version=result.engine_version,
        terminal_kind=result.terminal_kind,
        lines=result.lines,
    )


def _analysis_state(
    queue_state: str | None,
    result: AnalysisObservationResult | None,
) -> AnalysisObservationState:
    if queue_state == "running":
        return AnalysisObservationState.RUNNING
    if queue_state == "queued":
        return AnalysisObservationState.QUEUED
    if result is not None:
        return AnalysisObservationState.READY
    return AnalysisObservationState.NOT_REQUESTED


def _canonical_fen(position: CanonicalPosition) -> str:
    return " ".join(
        (
            position.placement,
            position.side_to_move,
            position.castling_rights,
            position.legal_en_passant,
            "0",
            "1",
        )
    )


__all__ = [
    "AnalysisObservation",
    "AnalysisObservationError",
    "AnalysisObservationRepository",
    "AnalysisObservationRequest",
    "AnalysisObservationResult",
    "AnalysisObservationSchemaError",
    "AnalysisObservationState",
    "AnalysisObservationStorageError",
    "AnalysisObservationValidationError",
    "get_analysis_observation",
    "read_analysis_observation",
]
