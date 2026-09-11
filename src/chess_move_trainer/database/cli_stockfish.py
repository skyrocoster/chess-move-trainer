"""Stockfish commands."""

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


