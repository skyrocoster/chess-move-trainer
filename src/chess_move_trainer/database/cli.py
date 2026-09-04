"""Thin Typer adapters for supported database commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS
from .games.acquisition import acquire_months
from .games.configuration import (
    GamesConfigurationError,
    load_acquire_configuration,
    load_import_configuration,
)
from .games.persistence import GameRepository, import_raw_months
from .inspection import inspect_schema, render_schema_markdown
from .openings import (
    OpeningCatalogueRepository,
    OpeningInputError,
    OpeningPersistenceError,
    OpeningRecognition,
    OpeningRecognitionError,
    OpeningSourceError,
    import_opening_catalogue,
    lookup_fen,
    replay_pgn,
)
from .publication import SchemaPublicationCollisionError, publish_schema
from .schema import SchemaIncompatibleError, create_schema


app = typer.Typer(add_completion=False, no_args_is_help=True)
schema_app = typer.Typer(add_completion=False, no_args_is_help=True)
games_app = typer.Typer(add_completion=False, no_args_is_help=True)
openings_app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(schema_app, name="schema")
app.add_typer(games_app, name="games")
app.add_typer(openings_app, name="openings")


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


@games_app.command("acquire")
def acquire_games(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit package-owned YAML configuration file.",
    ),
    raw_root: Path = typer.Option(
        ...,
        "--raw-root",
        help="Explicit raw-data root containing games/YYYY/MM.json.",
    ),
    username: str | None = typer.Option(
        None,
        "--username",
        help="Override the separate Chess.com username from YAML.",
    ),
    trainer_chesscom_uuid: str | None = typer.Option(
        None,
        "--trainer-chesscom-uuid",
        help="Override the trainer participant UUID from YAML.",
    ),
    request_timeout: float | None = typer.Option(
        None,
        "--request-timeout",
        help="Request timeout seconds (default: 30.0); must be finite and positive.",
    ),
    request_delay: float | None = typer.Option(
        None,
        "--request-delay",
        help="Delay seconds (default: 0.25); must be finite and nonnegative.",
    ),
) -> None:
    """Acquire raw months from the fixed Chess.com API endpoint (not configurable)."""

    try:
        configuration = load_acquire_configuration(
            config,
            username=username,
            trainer_chesscom_uuid=trainer_chesscom_uuid,
            request_timeout=request_timeout,
            request_delay=request_delay,
        )
    except GamesConfigurationError as error:
        _games_configuration_error(error)
    try:
        result = acquire_months(configuration, raw_root)
    except KeyboardInterrupt:
        _interrupted()
    except Exception as error:
        _operational_error(error, 1)

    typer.echo(
        f"Acquisition published {len(result.published_months)} month(s); "
        f"skipped {len(result.skipped_months)} immutable month(s)."
    )
    if not result.completed:
        for failure in result.failures:
            subject = failure.month if failure.month is not None else "archive discovery"
            typer.echo(f"Error: {subject}: {failure.message}", err=True)
        raise typer.Exit(code=1)


@games_app.command("import")
def import_games(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit package-owned YAML configuration file.",
    ),
    raw_root: Path = typer.Option(
        ...,
        "--raw-root",
        help="Explicit local raw-data root containing games/YYYY/MM.json.",
    ),
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    trainer_chesscom_uuid: str | None = typer.Option(
        None,
        "--trainer-chesscom-uuid",
        help="Override the trainer participant UUID from YAML.",
    ),
) -> None:
    """Import local raw months without network access."""

    try:
        configuration = load_import_configuration(
            config, trainer_chesscom_uuid=trainer_chesscom_uuid
        )
    except GamesConfigurationError as error:
        _games_configuration_error(error)
    try:
        result = import_raw_months(
            raw_root,
            configuration.trainer_chesscom_uuid,
            GameRepository(database),
        )
    except KeyboardInterrupt:
        _interrupted()
    except Exception as error:
        _operational_error(error, 1)

    for warning in result.warnings:
        subject = warning.game_uuid if warning.game_uuid is not None else "unknown game"
        typer.echo(f"Warning: {subject}: {warning.message}", err=True)
    typer.echo(
        f"Imported {result.imported_count} game(s); skipped {result.skipped_count} game(s)."
    )
    if result.failure is not None:
        typer.echo(
            f"Error: {result.failure.game_uuid}: {result.failure.message}", err=True
        )
        raise typer.Exit(code=1)


@openings_app.command("import")
def import_openings(
    source_dir: Path = typer.Option(
        ..., "--source-dir", help="Explicit directory containing a.tsv through e.tsv."
    ),
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Replace the opening catalogue from one explicit five-file source directory."""

    try:
        publication = import_opening_catalogue(
            source_dir, OpeningCatalogueRepository(database)
        )
    except KeyboardInterrupt:
        _interrupted()
    except SchemaIncompatibleError as error:
        _operational_error(error, 3)
    except (OpeningSourceError, OpeningPersistenceError) as error:
        _operational_error(error, 1)
    except Exception as error:
        _operational_error(error, 1)
    else:
        _render_publication(publication, json_output)


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


def _usage_error(error: Exception, *, param_hint: str = "--lock-timeout") -> None:
    raise typer.BadParameter(str(error), param_hint=param_hint)


def _games_configuration_error(error: Exception) -> None:
    raise typer.BadParameter(str(error), param_hint="--config")


def _interrupted() -> None:
    typer.echo("Interrupted.", err=True)
    raise typer.Exit(code=130)


def _operational_error(error: Exception, exit_code: int) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=exit_code)


def _render_publication(publication: object, json_output: bool) -> None:
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "opening_count": publication.opening_count,
                    "route_count": publication.route_count,
                    "move_count": publication.move_count,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return
    typer.echo(
        f"Imported {publication.opening_count} opening label(s), "
        f"{publication.route_count} route(s), and {publication.move_count} move(s)."
    )


def _render_recognition(result: OpeningRecognition, json_output: bool) -> None:
    recognized = [
        {
            "ply": item.ply,
            "eco": item.eco,
            "name": item.name,
            "match": item.match,
        }
        for item in result.recognized
    ]
    current = (
        {
            "ply": result.current.ply,
            "eco": result.current.eco,
            "name": result.current.name,
            "match": result.current.match,
        }
        if result.current is not None
        else None
    )
    if json_output:
        typer.echo(
            json.dumps(
                {"recognized": recognized, "current": current},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return
    if not recognized:
        typer.echo("No recognized opening.")
        return
    typer.echo("Recognized openings:")
    for item in recognized:
        label = f"{item['eco']} {item['name']}".rstrip()
        typer.echo(f"- ply {item['ply']}: {label} ({item['match']})")
    assert current is not None
    label = f"{current['eco']} {current['name']}".rstrip()
    typer.echo(f"Current: {label} (ply {current['ply']}, {current['match']})")
