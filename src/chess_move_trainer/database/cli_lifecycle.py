"""Lifecycle and schema commands."""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Callable
from pathlib import Path

import typer

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS
from .inspection import inspect_schema, render_schema_markdown
from .lifecycle import (
    DEFAULT_DATABASE_PATH,
    LifecycleResult,
    setup_database,
    update_games,
    update_openings,
)
from .openings import (
    OpeningInputError,
    OpeningRecognition,
    OpeningRecognitionError,
    lookup_fen,
    replay_pgn,
)
from .preferred_moves.ranges import (
    NormalizedPeriod,
    Preference,
    RangeValidationError,
    ResolutionState,
)
from .preferred_moves.repository import (
    PreferredMoveRepository,
    PreferredMoveSchemaError,
    PreferredMoveStorageError,
    PreferredMoveValidationError,
)
from .preferred_moves.setup import (
    PreferredMoveSetupError,
    PreferredMoveSetupResult,
    setup_preferred_moves as run_preferred_moves_setup,
)
from .publication import SchemaPublicationCollisionError, publish_schema
from .schema import SchemaIncompatibleError, create_schema
from .stockfish import (
    BenchmarkCompatibilityError,
    BenchmarkInputError,
    BulkInputError,
    BulkRunner,
    INITIAL_TECHNICAL_CATEGORIES,
    TargetInputError,
    WorkerInputError,
    WorkerRunner,
    run_benchmark,
)


from .cli_apps import app, openings_app, preferred_moves_app, schema_app, stockfish_app, update_app
from .cli_helpers import _interrupted, _is_schema_error, _operational_error, _preference_from_options, _preferred_period_json, _render_preferred_periods, _render_preferred_resolution, _render_preferred_setup, _render_recognition, _render_stockfish_outcome, _run_lifecycle, _stockfish_operational_error, _usage_error, _validate_stockfish_lock_timeout

@app.command(
    "setup",
    help=(
        "Create the one fixed database at data/database/chess.db. "
        "The destination is not configurable."
    ),
)
def setup_command() -> None:
    """Create the fixed direct database through the package lifecycle service."""

    from . import cli as _cli_module
    _run_lifecycle(_cli_module.setup_database)


@update_app.command(
    "games",
    help=(
        "Refresh games directly in data/database/chess.db. "
        "The destination is not configurable."
    ),
)
def update_games_command() -> None:
    """Refresh the fixed direct database's game data."""

    from . import cli as _cli_module
    _run_lifecycle(_cli_module.update_games)


@update_app.command(
    "openings",
    help=(
        "Refresh openings directly in data/database/chess.db. "
        "The destination is not configurable."
    ),
)
def update_openings_command() -> None:
    """Refresh the fixed direct database's opening data."""

    from . import cli as _cli_module
    _run_lifecycle(_cli_module.update_openings)


@schema_app.command("create")
def create(
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
) -> None:
    """Create schema v1 or accept an exactly compatible existing database."""

    try:
        result = create_schema(database, lock_timeout=lock_timeout)
    except SchemaIncompatibleError as error:
        _operational_error(error, 3)
    except ValueError as error:
        _usage_error(error)
    except Exception as error:
        _operational_error(error, 1)
    else:
        if result.created:
            typer.echo(f"Created schema v1: {result.database_path}")
        else:
            typer.echo(f"Schema v1 is already compatible: {result.database_path}")


@schema_app.command("inspect")
def inspect(
    database: Path = typer.Option(..., "--database", help="Explicit readable SQLite database path."),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        help="Optional Markdown destination, replaced atomically after inspection.",
    ),
) -> None:
    """Inspect any readable SQLite database and emit deterministic Markdown."""

    try:
        if output is None:
            markdown = render_schema_markdown(inspect_schema(database, lock_timeout=lock_timeout))
        else:
            markdown = publish_schema(database, output, lock_timeout=lock_timeout)
    except SchemaPublicationCollisionError as error:
        _operational_error(error, 1)
    except ValueError as error:
        _usage_error(error)
    except Exception as error:
        _operational_error(error, 1)
    else:
        sys.stdout.buffer.write(markdown)
        sys.stdout.buffer.flush()


