"""Opaque per-game persistence and raw-game import orchestration.

Thin compatibility shim. Implementation lives in persistence_repository
and persistence_import.
"""

from __future__ import annotations

from .persistence_import import (
    import_normalized_games,
    import_raw_games,
    import_raw_month,
    import_raw_months,
    load_normalized_months,
    normalize_raw_games,
)
from .persistence_repository import (
    GamePersistenceError,
    GameRepository,
    ImportFailure,
    ImportResult,
    _game_metadata,
    _metadata_parameters,
    _stored_game_matches,
)

__all__ = [
    "GamePersistenceError",
    "GameRepository",
    "ImportFailure",
    "ImportResult",
    "import_normalized_games",
    "import_raw_games",
    "import_raw_month",
    "import_raw_months",
    "load_normalized_months",
    "normalize_raw_games",
]
