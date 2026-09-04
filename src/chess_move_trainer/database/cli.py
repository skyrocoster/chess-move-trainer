"""Thin Typer adapters for supported database commands."""

from __future__ import annotations

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
from .publication import SchemaPublicationCollisionError, publish_schema
from .schema import SchemaIncompatibleError, create_schema


app = typer.Typer(add_completion=False, no_args_is_help=True)
schema_app = typer.Typer(add_completion=False, no_args_is_help=True)
games_app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(schema_app, name="schema")
app.add_typer(games_app, name="games")


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


def _usage_error(error: Exception) -> None:
    raise typer.BadParameter(str(error), param_hint="--lock-timeout")


def _games_configuration_error(error: Exception) -> None:
    raise typer.BadParameter(str(error), param_hint="--config")


def _interrupted() -> None:
    typer.echo("Interrupted.", err=True)
    raise typer.Exit(code=130)


def _operational_error(error: Exception, exit_code: int) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=exit_code)
