"""Read-only, explicit-path search over normalized schema-v1 games.

Thin compatibility shim. Implementation lives in search_models,
search_repository, search_filters, and search_validation.
"""

from __future__ import annotations

from .search_errors import (
    GameSearchError,
    GameSearchSchemaError,
    GameSearchStorageError,
    GameSearchValidationError,
)
from .search_models import (
    CoverageState,
    DeepestOpening,
    GameCoverage,
    GameSearchPage,
    GameSearchQuery,
    GameSearchSort,
    GameSummary,
    OpeningMatch,
)
from .search_repository import (
    GameSearchRepository,
    search_games,
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
