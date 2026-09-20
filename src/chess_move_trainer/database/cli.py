"""Thin Typer adapters for supported database commands.

Thin compatibility shim. Implementation lives in cli_apps, cli_helpers,
cli_lifecycle, cli_openings, cli_preferred, and cli_stockfish.
"""

from __future__ import annotations

from .cli_apps import (
    app,
)
from .cli_lifecycle import (
    create,
    inspect,
    setup_command,
    upgrade,
)
from .cli_openings import lookup_opening, replay_opening
from .cli_preferred import (
    list_preferred_moves,
    resolve_preferred_move,
    set_preferred_move,
    unset_preferred_move,
)
from .cli_stockfish import benchmark_stockfish, bulk_stockfish, worker_stockfish
from .lifecycle import setup_database as setup_database
from .lifecycle import update_games as update_games
from .lifecycle import update_openings as update_openings

__all__ = [
    "app",
    "benchmark_stockfish",
    "bulk_stockfish",
    "create",
    "inspect",
    "list_preferred_moves",
    "lookup_opening",
    "replay_opening",
    "resolve_preferred_move",
    "set_preferred_move",
    "setup_command",
    "upgrade",
    "unset_preferred_move",
    "worker_stockfish",
]
