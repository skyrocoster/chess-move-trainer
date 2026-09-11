"""Application dependencies for clean rebuilt-database capabilities."""

from __future__ import annotations

import os
from pathlib import Path

from chess_move_trainer.database.lifecycle import DEFAULT_DATABASE_PATH

REBUILT_DATABASE_PATH_ENV = "CHESS_REBUILT_DATABASE_PATH"


def get_rebuilt_database_path() -> Path:
    """Return the explicit clean database path for the current application process."""

    return Path(os.environ.get(REBUILT_DATABASE_PATH_ENV, str(DEFAULT_DATABASE_PATH)))


__all__ = ["REBUILT_DATABASE_PATH_ENV", "get_rebuilt_database_path"]
