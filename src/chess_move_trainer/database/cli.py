"""Thin Typer adapters for supported database commands."""

from __future__ import annotations

import json
import math
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
from .publication import SchemaPublicationCollisionError, publish_schema
from .rebuild.cli import app as rebuild_app
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


app = typer.Typer(add_completion=False, no_args_is_help=True)
schema_app = typer.Typer(add_completion=False, no_args_is_help=True)
games_app = typer.Typer(add_completion=False, no_args_is_help=True)
openings_app = typer.Typer(add_completion=False, no_args_is_help=True)
preferred_moves_app = typer.Typer(add_completion=False, no_args_is_help=True)
stockfish_app = typer.Typer(add_completion=False, no_args_is_help=True)
app.add_typer(schema_app, name="schema")
app.add_typer(games_app, name="games")
app.add_typer(openings_app, name="openings")
app.add_typer(preferred_moves_app, name="preferred-moves")
app.add_typer(stockfish_app, name="stockfish")
app.add_typer(rebuild_app, name="rebuild")


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


@preferred_moves_app.command("list")
def list_preferred_moves(
    database: Path = typer.Option(..., "--database", help="Explicit existing SQLite database path."),
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


@preferred_moves_app.command("resolve")
def resolve_preferred_move(
    database: Path = typer.Option(..., "--database", help="Explicit existing SQLite database path."),
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
    database: Path = typer.Option(..., "--database", help="Explicit existing SQLite database path."),
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
        periods = PreferredMoveRepository(database).set(
            fen, from_date, until, preference
        )
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
    database: Path = typer.Option(..., "--database", help="Explicit existing SQLite database path."),
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


@stockfish_app.command("benchmark")
def benchmark_stockfish(
    executable: Path = typer.Option(
        ...,
        "--executable",
        help="Explicit Stockfish 18 executable path.",
    ),
    position_input: Path = typer.Option(
        ...,
        "--position-input",
        help="Explicit JSON file containing benchmark positions.",
    ),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        help="Explicit directory owned by this benchmark run.",
    ),
    node_budget: list[int] = typer.Option(
        ...,
        "--node-budget",
        help="Positive node budget; repeat for a matrix.",
    ),
    threads: list[int] = typer.Option(
        ...,
        "--threads",
        help="Positive Stockfish thread count; repeat for a matrix.",
    ),
    hash_mb: list[int] = typer.Option(
        ...,
        "--hash-mb",
        help="Positive Stockfish hash size in MiB; repeat for a matrix.",
    ),
    repetitions: int = typer.Option(
        ...,
        "--repetitions",
        help="Positive repetition count.",
    ),
    shuffle_seed: int = typer.Option(
        ...,
        "--shuffle-seed",
        help="Deterministic integer job-order seed.",
    ),
) -> None:
    """Run one explicit, resumable Stockfish benchmark matrix."""

    try:
        outcome = run_benchmark(
            executable=executable,
            position_input=position_input,
            output_dir=output_dir,
            node_budgets=node_budget,
            thread_counts=threads,
            hash_sizes_mb=hash_mb,
            repetitions=repetitions,
            shuffle_seed=shuffle_seed,
        )
    except KeyboardInterrupt:
        _interrupted()
    except BenchmarkInputError as error:
        _usage_error(error, param_hint="--position-input/--node-budget")
    except BenchmarkCompatibilityError as error:
        _operational_error(error, 1)
    except Exception as error:
        _stockfish_operational_error(error)
    else:
        if outcome.interrupted:
            _interrupted()
        if not outcome.complete:
            _operational_error(
                RuntimeError(
                    f"benchmark incomplete: {outcome.successful_jobs}/"
                    f"{outcome.total_jobs} successful"
                ),
                1,
            )
        typer.echo(
            f"Benchmark complete: {outcome.successful_jobs}/{outcome.total_jobs} "
            f"successful; artifacts={outcome.artifact_dir}"
        )


@stockfish_app.command("bulk")
def bulk_stockfish(
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    executable: Path = typer.Option(
        ..., "--executable", help="Explicit Stockfish 18 executable path."
    ),
    limit: int | None = typer.Option(
        None,
        "--limit",
        help="Optional positive number of eligible targets for this launch.",
    ),
    preset: str | None = typer.Option(
        None,
        "--preset",
        help=(
            "Optional deterministic initial preset: 20 common positions plus "
            "checkmate, stalemate, legal en passant, promotion, and castling."
        ),
    ),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
) -> None:
    """Publish eligible Tool analyses directly and exit when the launch drains."""

    try:
        _validate_stockfish_lock_timeout(lock_timeout)
        runner = BulkRunner(
            database,
            executable,
            lock_timeout=lock_timeout,
        )
        if preset is None:
            outcome = runner.run(limit=limit)
        else:
            outcome = runner.run(preset=preset)
    except KeyboardInterrupt:
        _interrupted()
    except (BulkInputError, TargetInputError, ValueError) as error:
        _usage_error(error, param_hint="--limit/--lock-timeout")
    except Exception as error:
        _stockfish_operational_error(error)
    else:
        if preset == "initial":
            categories = ", ".join(INITIAL_TECHNICAL_CATEGORIES)
            message = (
                f"Initial analysis complete: {outcome.published_count} published, "
                f"{outcome.selected_count} selected; technical categories={categories}"
            )
        else:
            message = (
                f"Bulk complete: {outcome.published_count} published, "
                f"{outcome.selected_count} selected"
            )
        _render_stockfish_outcome(
            message,
            outcome,
        )


@stockfish_app.command("worker")
def worker_stockfish(
    database: Path = typer.Option(..., "--database", help="Explicit SQLite database path."),
    executable: Path = typer.Option(
        ..., "--executable", help="Explicit Stockfish 18 executable path."
    ),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
) -> None:
    """Drain current queued analysis requests and exit."""

    try:
        _validate_stockfish_lock_timeout(lock_timeout)
        outcome = WorkerRunner(
            database,
            executable,
            lock_timeout=lock_timeout,
        ).run()
    except KeyboardInterrupt:
        _interrupted()
    except (WorkerInputError, ValueError) as error:
        _usage_error(error, param_hint="--database/--executable")
    except Exception as error:
        _stockfish_operational_error(error)
    else:
        _render_stockfish_outcome(
            f"Worker complete: {outcome.completed_count} completed, "
            f"{outcome.claimed_count} claimed",
            outcome,
        )


def _render_stockfish_outcome(message: str, outcome: object) -> None:
    if getattr(outcome, "interrupted", False):
        _interrupted()
    failures = getattr(outcome, "failures", ())
    for failure in failures:
        subject = "database" if failure.position_id is None else f"position {failure.position_id}"
        typer.echo(f"Error: {subject}: {failure.message}", err=True)
    if getattr(outcome, "exit_code", 1) != 0:
        if any("compatible schema" in str(failure.message).lower() for failure in failures):
            raise typer.Exit(code=3)
        raise typer.Exit(code=1)
    typer.echo(message)


def _stockfish_operational_error(error: Exception) -> None:
    if _is_schema_error(error):
        _operational_error(error, 3)
    _operational_error(error, 1)


def _validate_stockfish_lock_timeout(value: float) -> None:
    if isinstance(value, bool) or not math.isfinite(float(value)) or float(value) <= 0:
        raise ValueError("lock-timeout must be finite and greater than zero")


def _is_schema_error(error: BaseException) -> bool:
    candidate: BaseException | None = error
    while candidate is not None:
        if isinstance(candidate, SchemaIncompatibleError):
            return True
        candidate = candidate.__cause__ or candidate.__context__
    return "compatible schema" in str(error).lower()


def _usage_error(error: Exception, *, param_hint: str = "--lock-timeout") -> None:
    raise typer.BadParameter(str(error), param_hint=param_hint)


def _games_configuration_error(error: Exception) -> None:
    raise typer.BadParameter(str(error), param_hint="--config")


def _preference_from_options(move: str | None, no_preference: bool) -> Preference:
    if (move is not None) == no_preference:
        raise RangeValidationError(
            "exactly one of --move or --no-preference is required",
        )
    if no_preference:
        return Preference.no_preference()
    return Preference.preferred_move(move or "")


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


def _preferred_period_json(period: NormalizedPeriod) -> dict[str, str | None]:
    return {
        "effective_from": period.effective_from.isoformat(),
        "effective_until": (
            None
            if period.effective_until is None
            else period.effective_until.isoformat()
        ),
        "move": period.preference.move,
        "state": period.preference.state.value,
    }


def _render_preferred_periods(
    periods: tuple[NormalizedPeriod, ...], json_output: bool
) -> None:
    serialized = [_preferred_period_json(period) for period in periods]
    if json_output:
        typer.echo(
            json.dumps(
                {"periods": serialized},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return
    if not periods:
        typer.echo("No preferred-move periods configured.")
        return
    typer.echo("Preferred-move periods:")
    for period in serialized:
        end = period["effective_until"] or "indefinite"
        value = period["move"] or "no preference"
        typer.echo(f"- {period['effective_from']} to {end}: {value}")


def _render_preferred_resolution(result: object, json_output: bool) -> None:
    state = result.state.value
    move = result.move
    payload = {"move": move, "state": state}
    if json_output:
        typer.echo(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return
    if result.state is ResolutionState.PREFERRED_MOVE:
        typer.echo(f"Preferred move: {move}")
    elif result.state is ResolutionState.NO_PREFERENCE:
        typer.echo("Explicit no preference.")
    else:
        typer.echo("Unconfigured.")
