"""Read-only composition of the public insight for one chess position.

Thin compatibility shim. Implementation lives in insight_models,
insight_repository, insight_readers, and insight_helpers.
"""

from __future__ import annotations

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
)
from .insight_repository import (
    PositionInsightRepository,
    get_position_insight,
    read_position_insight,
)

__all__ = [
    "AnalysisState",
    "PreferenceKind",
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
    "TrainerColor",
    "get_position_insight",
    "read_position_insight",
]
