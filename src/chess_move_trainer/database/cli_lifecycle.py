"""Lifecycle and schema commands."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from .cli_apps import app, schema_app, update_app
from .cli_helpers import (
    _interrupted,
    _operational_error,
    _run_lifecycle,
    _usage_error,
)
from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS
from .inspection import inspect_schema, render_schema_markdown
from .lifecycle import HOST_SEED_DATABASE_PATH
from .publication import SchemaPublicationCollisionError, publish_schema
from .schema import SchemaIncompatibleError, create_schema, upgrade_schema


@app.command(
    "setup",
    help=(
        "Create the database at the requested path "
        "(default data/database/chess-seed.db). "
        "Inside containers the live database remains "
        "/workspace/data/database/chess.db; Datasette uses /data/chess.db."
    ),
)
def setup_command(
    database: Path = typer.Option(
        HOST_SEED_DATABASE_PATH,
        "--database",
        help="Explicit SQLite database path.",
    ),
) -> None:
    """Create the direct database through the package lifecycle service."""

    from . import cli as _cli_module

    _run_lifecycle(lambda: _cli_module.setup_database(database), target=database)


@update_app.command(
    "games",
    help=(
        "Refresh games in the database at the requested path "
        "(default data/database/chess-seed.db). "
        "Inside containers the live database remains "
        "/workspace/data/database/chess.db; Datasette uses /data/chess.db."
    ),
)
def update_games_command(
    database: Path = typer.Option(
        HOST_SEED_DATABASE_PATH,
        "--database",
        help="Explicit SQLite database path.",
    ),
) -> None:
    """Refresh the direct database's game data."""

    from . import cli as _cli_module

    _run_lifecycle(lambda: _cli_module.update_games(database), target=database)


@update_app.command(
    "openings",
    help=(
        "Refresh openings in the database at the requested path "
        "(default data/database/chess-seed.db). "
        "Inside containers the live database remains "
        "/workspace/data/database/chess.db; Datasette uses /data/chess.db."
    ),
)
def update_openings_command(
    database: Path = typer.Option(
        HOST_SEED_DATABASE_PATH,
        "--database",
        help="Explicit SQLite database path.",
    ),
) -> None:
    """Refresh the direct database's opening data."""

    from . import cli as _cli_module

    _run_lifecycle(lambda: _cli_module.update_openings(database), target=database)


@schema_app.command("create")
def create(
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
) -> None:
    """Create schema v2 or accept an exactly compatible existing database."""

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
            typer.echo(f"Created schema v2: {result.database_path}")
        else:
            typer.echo(f"Schema v2 is already compatible: {result.database_path}")


@schema_app.command("upgrade")
def upgrade(
    database: Path = typer.Option(..., "--database", help="Existing SQLite database path."),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
) -> None:
    """Upgrade an existing exact schema v1 database to schema v2."""

    try:
        result = upgrade_schema(database, lock_timeout=lock_timeout)
    except SchemaIncompatibleError as error:
        _operational_error(error, 3)
    except ValueError as error:
        _usage_error(error)
    except KeyboardInterrupt:
        _interrupted()
    except Exception as error:
        _operational_error(error, 1)
    else:
        if result.upgraded:
            typer.echo(f"Upgraded schema v1 to v2: {result.database_path}")
        else:
            typer.echo(f"Schema v2 is already compatible: {result.database_path}")


@schema_app.command("inspect")
def inspect(
    database: Path = typer.Option(
        ..., "--database", help="Explicit readable SQLite database path."
    ),
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
