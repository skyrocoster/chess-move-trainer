"""Game search error types."""

from __future__ import annotations


class GameSearchError(Exception):
    """Base class for bounded game-search failures."""


class GameSearchValidationError(GameSearchError, ValueError):
    """Raised when a game-search query is invalid."""


class GameSearchSchemaError(GameSearchError, RuntimeError):
    """Raised when the selected database is not exactly schema v1."""


class GameSearchStorageError(GameSearchError, RuntimeError):
    """Raised when a compatible game database cannot be read safely."""
