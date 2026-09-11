"""Game acquisition, persistence, reading, and public search services."""

from .reading import GameDetail, GameDetailOccurrence, read_game
from .search import (
    CoverageState,
    DeepestOpening,
    GameCoverage,
    GameSearchError,
    GameSearchPage,
    GameSearchQuery,
    GameSearchRepository,
    GameSearchSchemaError,
    GameSearchSort,
    GameSearchStorageError,
    GameSearchValidationError,
    GameSummary,
    OpeningMatch,
    search_games,
)

__all__ = [
    "CoverageState",
    "DeepestOpening",
    "GameDetail",
    "GameDetailOccurrence",
    "GameCoverage",
    "GameSearchError",
    "GameSearchPage",
    "GameSearchQuery",
    "GameSearchRepository",
    "GameSearchSchemaError",
    "GameSearchStorageError",
    "GameSearchSort",
    "GameSearchValidationError",
    "GameSummary",
    "OpeningMatch",
    "read_game",
    "search_games",
]
