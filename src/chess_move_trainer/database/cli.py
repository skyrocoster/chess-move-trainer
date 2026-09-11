"""Thin Typer adapters for supported database commands.

Thin compatibility shim. Implementation lives in cli_apps, cli_helpers,
cli_lifecycle, cli_openings, cli_preferred, and cli_stockfish.
"""

from __future__ import annotations

from .cli_apps import (
    app,
    openings_app,
    preferred_moves_app,
    schema_app,
    stockfish_app,
    update_app,
)
from .cli_helpers import (
    _interrupted,
    _is_schema_error,
    _operational_error,
    _preference_from_options,
    _preferred_period_json,
    _render_preferred_periods,
    _render_preferred_resolution,
    _render_preferred_setup,
    _render_recognition,
    _render_stockfish_outcome,
    _run_lifecycle,
    _stockfish_operational_error,
    _usage_error,
    _validate_stockfish_lock_timeout,
)
from .cli_lifecycle import (
    create,
    inspect,
    setup_command,
    setup_database,
    update_games,
    update_games_command,
    update_openings,
    update_openings_command,
)
from .cli_openings import lookup_opening, replay_opening
from .cli_preferred import (
    list_preferred_moves,
    resolve_preferred_move,
    set_preferred_move,
    setup_preferred_moves_command,
    unset_preferred_move,
)
from .cli_stockfish import benchmark_stockfish, bulk_stockfish, worker_stockfish

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
    "unset_preferred_move",
    "worker_stockfish",
]
