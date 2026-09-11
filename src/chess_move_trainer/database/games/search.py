"""Read-only, explicit-path search over normalized schema-v1 games.

Thin compatibility shim. Implementation lives in search_models,
search_repository, search_filters, and search_validation.
"""

from __future__ import annotations

from .search_filters import _compare_games, _compare_nullable, _coverage_state, _matches
from .search_models import (
    CoverageState,
    DeepestOpening,
    GameCoverage,
    GameSearchError,
    GameSearchPage,
    GameSearchQuery,
    GameSearchSchemaError,
    GameSearchSort,
    GameSearchStorageError,
    GameSearchValidationError,
    GameSummary,
    OpeningMatch,
    TrainerColor,
    TrainerOutcome,
)
from .search_repository import (
    GameSearchRepository,
    _load_games,
    _load_occurrences,
    _load_openings,
    _load_position_ids,
    _summarize,
    search_games,
)
from .search_validation import (
    _in_datetime_bounds,
    _in_numeric_bounds,
    _normalize_fen,
    _normalize_timestamp,
    _opening_api_key,
    _optional_int,
    _optional_text,
    _parse_opening_key,
    _require_optional_non_negative_int,
    _require_ordered_bounds,
    _require_positive_int,
    _required_int,
    _required_text,
    _stored_position,
    _stored_timestamp,
    _validate_legal_move,
    _validate_optional_non_empty_text,
)

__all__ = [
    "CoverageState",
    "DeepestOpening",
    "GameCoverage",
    "GameSearchError",
    "GameSearchPage",
    "GameSearchQuery",
    "GameSearchRepository",
    "GameSearchSchemaError",
    "GameSearchSort",
    "GameSearchStorageError",
    "GameSearchValidationError",
    "GameSummary",
    "OpeningMatch",
    "search_games",
]
