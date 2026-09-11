"""Position insight repository."""

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
from .insight_readers import _read_position_data, _read_position_statistics
from .insight_helpers import _analysis_state, _read_analysis_result, _read_opening, _read_preference, _read_queue_state


class PositionInsightRepository:
    """Compose one insight using only an explicit, compatible database path."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def read(self, request: PositionInsightRequest) -> PositionInsight:
        """Read one insight without resolving or creating a derived position."""

        if not isinstance(request, PositionInsightRequest):
            raise PositionInsightValidationError(
                "request must be a PositionInsightRequest value"
            )

        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                position_id = _find_existing_position_id(
                    connection, canonicalize_fen(request.fen)
                )
                if position_id is None:
                    statistics = _read_position_statistics(connection, None, request)
                    return _sparse_insight(request, statistics)
                statistics, queue_state, preference = _read_position_data(
                    connection, position_id, request
                )
        except SchemaIncompatibleError as error:
            raise PositionInsightSchemaError(str(error)) from error
        except PositionInsightError:
            raise
        except Exception as error:
            raise PositionInsightStorageError("position insight could not be read") from error

        opening = _read_opening(self._database_path, request.fen)
        result = _read_analysis_result(self._database_path, position_id)
        state = _analysis_state(queue_state, result)
        return PositionInsight(
            fen=request.fen,
            trainer_color=request.trainer_color,
            as_of=request.as_of,
            opening=opening,
            observed_in_games=statistics.observed_in_games,
            experience=statistics.experience,
            observed_moves=statistics.observed_moves,
            observed_move_totals=statistics.observed_move_totals,
            analysis=PositionInsightAnalysis(state=state, result=result),
            preference=preference,
        )

    get = read


def read_position_insight(
    database_path: str | Path,
    fen: str | PositionInsightRequest,
    trainer_color: TrainerColor | None = None,
    as_of: str | None = None,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> PositionInsight:
    """Read one position insight from an explicit database path."""

    if isinstance(fen, PositionInsightRequest):
        if trainer_color is not None or as_of is not None:
            raise PositionInsightValidationError(
                "request cannot be combined with trainer_color or as_of"
            )
        request = fen
    else:
        if trainer_color is None or as_of is None:
            raise PositionInsightValidationError(
                "fen, trainer_color, and as_of are required"
            )
        request = PositionInsightRequest(fen, trainer_color, as_of)
    return PositionInsightRepository(database_path, lock_timeout=lock_timeout).read(request)


get_position_insight = read_position_insight


def _sparse_insight(
    request: PositionInsightRequest,
    statistics: _PositionInsightStatistics,
) -> PositionInsight:
    return PositionInsight(
        fen=request.fen,
        trainer_color=request.trainer_color,
        as_of=request.as_of,
        opening=None,
        observed_in_games=statistics.observed_in_games,
        experience=statistics.experience,
        observed_moves=statistics.observed_moves,
        observed_move_totals=statistics.observed_move_totals,
        analysis=PositionInsightAnalysis("not_requested", None),
        preference=PositionInsightPreference("unconfigured"),
    )





