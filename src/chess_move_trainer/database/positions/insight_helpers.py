"""Position insight helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

import chess
from sqlalchemy import text

from ..analysis.models import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisScoreKind,
    AnalysisTerminalKind,
)
from ..analysis.reading import AnalysisReadError, AnalysisReadRepository
from ..analysis.validation import validate_settings_object
from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..openings.keys import opening_api_key
from ..openings.recognition import (
    OpeningInputError,
    OpeningRecognitionError,
    lookup_fen,
)
from ..preferred_moves.ranges import (
    NormalizedPeriod,
    Preference,
    RangeValidationError,
    ResolutionState,
    normalize_periods,
    period_from_literals,
    resolve_date,
)
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .canonicalization import CanonicalPosition, PositionValidationError, canonicalize_fen
from .repository import _find_existing_position_id


TrainerColor = Literal["white", "black"]
AnalysisState = Literal["not_requested", "queued", "running", "ready"]
PreferenceKind = Literal["move", "no_preference", "unconfigured"]


from .insight_models import AnalysisState, PositionInsight, PositionInsightAnalysis, PositionInsightError, PositionInsightExperience, PositionInsightObservedMove, PositionInsightObservedMoveTotals, PositionInsightOpening, PositionInsightPreference, PositionInsightRequest, PositionInsightResult, PositionInsightSchemaError, PositionInsightStorageError, PositionInsightTerminalTotals, PositionInsightValidationError, PreferenceKind, TrainerColor, _PositionInsightStatistics, _canonical_fen


def _read_statistics_count(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise PositionInsightStorageError(f"{name} is malformed")
    return value


def _read_statistics_flag(value: object) -> bool:
    if type(value) is not int or value not in (0, 1):
        raise PositionInsightStorageError("position observation flag is malformed")
    return bool(value)


def _read_queue_state(connection: object, position_id: int) -> str | None:
    from ..stockfish.queue import QueueStorageError, _read_observed_queue_state

    try:
        return _read_observed_queue_state(connection, position_id)
    except QueueStorageError as error:
        raise PositionInsightStorageError(str(error)) from error


def _read_preference(
    connection: object,
    position_id: int,
    as_of: str,
) -> PositionInsightPreference:
    rows = connection.execute(
        text(
            """
            SELECT dpm_effective_from, dpm_effective_until, dpm_move_uci
            FROM datasource_preferred_move_period
            WHERE derived_position_id = :position_id
            ORDER BY dpm_effective_from
            """
        ),
        {"position_id": position_id},
    ).all()
    periods: list[NormalizedPeriod] = []
    try:
        for row in rows:
            if not isinstance(row[0], str):
                raise ValueError("preference start date")
            if row[1] is not None and not isinstance(row[1], str):
                raise ValueError("preference end date")
            if row[2] is not None:
                _validate_stored_move(row[2])
            preference = (
                Preference.no_preference()
                if row[2] is None
                else Preference.preferred_move(row[2])
            )
            periods.append(period_from_literals(row[0], row[1], preference))
        resolution = resolve_date(normalize_periods(periods), as_of)
    except (IndexError, TypeError, ValueError, RangeValidationError) as error:
        raise PositionInsightStorageError("preferred-move schedule is malformed") from error
    if resolution.state is ResolutionState.PREFERRED_MOVE:
        return PositionInsightPreference("move", resolution.move)
    if resolution.state is ResolutionState.NO_PREFERENCE:
        return PositionInsightPreference("no_preference")
    return PositionInsightPreference("unconfigured")


def _read_opening(database_path: str | Path, fen: str) -> PositionInsightOpening | None:
    try:
        recognition = lookup_fen(database_path, fen)
    except (OpeningInputError, OpeningRecognitionError, SchemaIncompatibleError) as error:
        raise PositionInsightStorageError("opening recognition could not be read") from error
    except PositionInsightError:
        raise
    except Exception as error:
        raise PositionInsightStorageError("opening recognition could not be read") from error
    current = recognition.current
    if current is None:
        return None
    try:
        return PositionInsightOpening(
            key=opening_api_key(current.eco, current.name),
            eco=current.eco,
            name=current.name,
            ply=current.ply,
            match=current.match,
        )
    except ValueError as error:
        raise PositionInsightStorageError("opening recognition is malformed") from error


def _read_analysis_result(
    database_path: str | Path,
    position_id: int,
) -> PositionInsightResult | None:
    try:
        result = AnalysisReadRepository(database_path).read(position_id)
    except (AnalysisReadError, SchemaIncompatibleError) as error:
        raise PositionInsightStorageError("analysis result could not be read") from error
    except PositionInsightError:
        raise
    except Exception as error:
        raise PositionInsightStorageError("analysis result could not be read") from error
    if result is None:
        return None
    return PositionInsightResult(
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
    result: PositionInsightResult | None,
) -> AnalysisState:
    if queue_state == "running":
        return "running"
    if queue_state == "queued":
        return "queued"
    if result is not None:
        return "ready"
    return "not_requested"


def _validate_stored_move(value: object) -> None:
    if not isinstance(value, str) or not value:
        raise PositionInsightStorageError("stored UCI move is malformed")
    try:
        move = chess.Move.from_uci(value)
    except (TypeError, ValueError) as error:
        raise PositionInsightStorageError("stored UCI move is malformed") from error
    if move.uci() != value:
        raise PositionInsightStorageError("stored UCI move is not canonical")
