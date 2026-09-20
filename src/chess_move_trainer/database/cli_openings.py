"""Opening lookup commands."""

from __future__ import annotations

from pathlib import Path

import typer

from .cli_apps import openings_app
from .cli_helpers import (
    _interrupted,
    _operational_error,
    _render_recognition,
    _usage_error,
)
from .openings import (
    OpeningInputError,
    OpeningRecognitionError,
    lookup_fen,
    replay_pgn,
)
from .schema import SchemaIncompatibleError


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
