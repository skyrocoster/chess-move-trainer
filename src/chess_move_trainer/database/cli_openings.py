"""Opening lookup commands."""

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

@openings_app.command("lookup")
def lookup_opening(
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    fen: str = typer.Option(..., "--fen", help="Complete six-field FEN to recognize."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Recognize opening labels for one explicit full FEN."""

    try:
        result = lookup_fen(database, fen)
    except KeyboardInterrupt:
        _interrupted()
    except SchemaIncompatibleError as error:
        _operational_error(error, 3)
    except OpeningInputError as error:
        _usage_error(error, param_hint="--fen")
    except OpeningRecognitionError as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_recognition(result, json_output)


@openings_app.command("replay")
def replay_opening(
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    pgn_file: Path = typer.Option(..., "--pgn-file", help="Explicit one-game PGN file."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Replay one explicit PGN file and recognize its opening labels."""

    try:
        pgn = pgn_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        _usage_error(error, param_hint="--pgn-file")

    try:
        result = replay_pgn(database, pgn)
    except KeyboardInterrupt:
        _interrupted()
    except SchemaIncompatibleError as error:
        _operational_error(error, 3)
    except OpeningInputError as error:
        _usage_error(error, param_hint="--pgn-file")
    except OpeningRecognitionError as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_recognition(result, json_output)


