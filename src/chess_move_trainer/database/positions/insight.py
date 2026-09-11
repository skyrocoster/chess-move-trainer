"""Read-only composition of the public insight for one chess position.

Thin compatibility shim. Implementation lives in insight_models,
insight_repository, insight_readers, and insight_helpers.
"""

from __future__ import annotations

from .insight_helpers import (
    _analysis_state,
    _read_analysis_result,
    _read_opening,
    _read_preference,
    _read_queue_state,
    _read_statistics_count,
    _read_statistics_flag,
    _validate_stored_move,
)
from .insight_models import (
    AnalysisState,
    PositionInsight,
    PositionInsightAnalysis,
    PositionInsightError,
    PositionInsightExperience,
    PositionInsightObservedMove,
    PositionInsightObservedMoveTotals,
    PositionInsightOpening,
    PositionInsightPreference,
    PositionInsightRequest,
    PositionInsightResult,
    PositionInsightSchemaError,
    PositionInsightStorageError,
    PositionInsightTerminalTotals,
    PositionInsightValidationError,
    PreferenceKind,
    TrainerColor,
    _PositionInsightStatistics,
    _canonical_fen,
)
from .insight_readers import _read_position_data, _read_position_statistics
from .insight_repository import (
    PositionInsightRepository,
    _sparse_insight,
    get_position_insight,
    read_position_insight,
)

__all__ = [
    "AnalysisState",
    "PositionInsight",
    "PositionInsightAnalysis",
    "PositionInsightError",
    "PositionInsightExperience",
    "PositionInsightObservedMove",
    "PositionInsightObservedMoveTotals",
    "PositionInsightOpening",
    "PositionInsightPreference",
    "PositionInsightRepository",
    "PositionInsightRequest",
    "PositionInsightResult",
    "PositionInsightSchemaError",
    "PositionInsightStorageError",
    "PositionInsightTerminalTotals",
    "PositionInsightValidationError",
    "read_position_insight",
]
