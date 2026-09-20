"""Preferred-move commands."""

from __future__ import annotations

from pathlib import Path

import typer

from .cli_apps import app as app
from .cli_apps import preferred_moves_app
from .cli_helpers import (
    _interrupted,
    _operational_error,
    _preference_from_options,
    _render_preferred_periods,
    _render_preferred_resolution,
    _render_preferred_setup,
    _usage_error,
)
from .lifecycle import (
    DEFAULT_DATABASE_PATH,
)
from .preferred_moves.ranges import (
    RangeValidationError,
)
from .preferred_moves.repository import (
    PreferredMoveRepository,
    PreferredMoveSchemaError,
    PreferredMoveStorageError,
    PreferredMoveValidationError,
)
from .preferred_moves.setup import (
    PreferredMoveSetupError,
)
from .preferred_moves.setup import (
    setup_preferred_moves as run_preferred_moves_setup,
)


@preferred_moves_app.command("list")
def list_preferred_moves(
    database: Path = typer.Option(
        ..., "--database", help="Explicit existing SQLite database path."
    ),
    fen: str = typer.Option(..., "--fen", help="Exactly four meaningful FEN fields."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """List the normalized preferred-move periods for one position."""

    try:
        periods = PreferredMoveRepository(database).list_periods(fen)
    except KeyboardInterrupt:
        _interrupted()
    except PreferredMoveSchemaError as error:
        _operational_error(error, 3)
    except PreferredMoveValidationError as error:
        _usage_error(error, param_hint="--fen")
    except PreferredMoveStorageError as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_preferred_periods(periods, json_output)


@preferred_moves_app.command("setup")
def setup_preferred_moves_command() -> None:
    """Initialize preferred moves from the fixed app database."""

    try:
        result = run_preferred_moves_setup(DEFAULT_DATABASE_PATH)
    except KeyboardInterrupt:
        _interrupted()
    except PreferredMoveSchemaError as error:
        _operational_error(error, 3)
    except PreferredMoveSetupError as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_preferred_setup(result)


@preferred_moves_app.command("resolve")
def resolve_preferred_move(
    database: Path = typer.Option(
        ..., "--database", help="Explicit existing SQLite database path."
    ),
    fen: str = typer.Option(..., "--fen", help="Exactly four meaningful FEN fields."),
    date_literal: str = typer.Option(..., "--date", help="Literal UTC calendar date YYYY-MM-DD."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Resolve the preferred-move state for one position and date."""

    try:
        resolution = PreferredMoveRepository(database).resolve(fen, date_literal)
    except KeyboardInterrupt:
        _interrupted()
    except PreferredMoveSchemaError as error:
        _operational_error(error, 3)
    except PreferredMoveValidationError as error:
        _usage_error(error, param_hint="--date")
    except PreferredMoveStorageError as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_preferred_resolution(resolution, json_output)


@preferred_moves_app.command("set")
def set_preferred_move(
    database: Path = typer.Option(
        ..., "--database", help="Explicit existing SQLite database path."
    ),
    fen: str = typer.Option(..., "--fen", help="Exactly four meaningful FEN fields."),
    from_date: str = typer.Option(..., "--from", help="Literal UTC start date YYYY-MM-DD."),
    until: str | None = typer.Option(
        None, "--until", help="Optional literal UTC end date YYYY-MM-DD."
    ),
    move: str | None = typer.Option(None, "--move", help="Legal preferred move in UCI notation."),
    no_preference: bool = typer.Option(
        False, "--no-preference", help="Store an explicit no-preference period."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Overlay a legal move or explicit no-preference state on a date range."""

    try:
        preference = _preference_from_options(move, no_preference)
        periods = PreferredMoveRepository(database).set(fen, from_date, until, preference)
    except KeyboardInterrupt:
        _interrupted()
    except (PreferredMoveValidationError, RangeValidationError) as error:
        _usage_error(error, param_hint="--move/--no-preference")
    except PreferredMoveSchemaError as error:
        _operational_error(error, 3)
    except PreferredMoveStorageError as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_preferred_periods(periods, json_output)


@preferred_moves_app.command("unset")
def unset_preferred_move(
    database: Path = typer.Option(
        ..., "--database", help="Explicit existing SQLite database path."
    ),
    fen: str = typer.Option(..., "--fen", help="Exactly four meaningful FEN fields."),
    from_date: str = typer.Option(..., "--from", help="Literal UTC start date YYYY-MM-DD."),
    until: str | None = typer.Option(
        None, "--until", help="Optional literal UTC end date YYYY-MM-DD."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Remove configuration from a date range."""

    try:
        periods = PreferredMoveRepository(database).unset(fen, from_date, until)
    except KeyboardInterrupt:
        _interrupted()
    except PreferredMoveSchemaError as error:
        _operational_error(error, 3)
    except PreferredMoveValidationError as error:
        _usage_error(error, param_hint="--from")
    except PreferredMoveStorageError as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_preferred_periods(periods, json_output)
