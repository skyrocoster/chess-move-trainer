"""Stockfish commands."""

from __future__ import annotations

import math
import time
from pathlib import Path

import typer

from .cli_apps import stockfish_app
from .cli_helpers import (
    _interrupted,
    _operational_error,
    _render_stockfish_outcome,
    _stockfish_operational_error,
    _usage_error,
    _validate_stockfish_lock_timeout,
)
from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS
from .stockfish import (
    INITIAL_TECHNICAL_CATEGORIES,
    BenchmarkCompatibilityError,
    BenchmarkInputError,
    BulkInputError,
    BulkRunner,
    TargetInputError,
    WorkerInputError,
    WorkerOutcome,
    WorkerRunner,
    run_benchmark,
)


@stockfish_app.command("benchmark")
def benchmark_stockfish(
    executable: Path = typer.Option(
        ...,
        "--executable",
        help="Explicit Stockfish 19 executable path.",
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
        ..., "--executable", help="Explicit Stockfish 19 executable path."
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
        ..., "--executable", help="Explicit Stockfish 19 executable path."
    ),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
    poll_interval: float = typer.Option(
        0.0,
        "--poll-interval",
        help=(
            "Idle seconds between queue polls; 0 drains the current queue and exits, "
            "a positive value keeps listening quietly until interrupted."
        ),
    ),
) -> None:
    """Drain current queued analysis requests and exit, or keep listening."""

    try:
        _validate_stockfish_lock_timeout(lock_timeout)
        _validate_stockfish_poll_interval(poll_interval)
        if poll_interval <= 0:
            outcome = WorkerRunner(
                database,
                executable,
                lock_timeout=lock_timeout,
            ).run()
        else:
            outcome = _run_worker_loop(database, executable, lock_timeout, poll_interval)
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


def _validate_stockfish_poll_interval(value: float) -> None:
    if isinstance(value, bool) or not math.isfinite(float(value)) or float(value) < 0:
        raise ValueError("poll-interval must be finite and non-negative")


def _run_worker_loop(
    database: Path,
    executable: Path,
    lock_timeout: float,
    poll_interval: float,
) -> WorkerOutcome:
    """Poll quietly and spin the engine up only while work is claimed.

    Resting usage is one sleeping Python process: the Stockfish child is
    created lazily inside each drain and closed before the next idle sleep.
    """

    completed_total = 0
    claimed_total = 0
    was_idle = False
    while True:
        outcome = WorkerRunner(
            database,
            executable,
            lock_timeout=lock_timeout,
        ).run()
        completed_total += outcome.completed_count
        claimed_total += outcome.claimed_count
        if outcome.interrupted:
            return WorkerOutcome(
                claimed_count=claimed_total,
                completed_count=completed_total,
                not_saved_count=outcome.not_saved_count,
                failures=outcome.failures,
                interrupted=True,
                drained=outcome.drained,
                recovery_polls=outcome.recovery_polls,
            )
        for failure in outcome.failures:
            subject = (
                "database" if failure.position_id is None else f"position {failure.position_id}"
            )
            typer.echo(f"Error: {subject}: {failure.message}", err=True)
        if outcome.completed_count:
            typer.echo(
                f"Worker: {outcome.completed_count} completed "
                f"({completed_total} total, {claimed_total} claimed)."
            )
        if outcome.claimed_count == 0 or outcome.failures:
            if not was_idle:
                typer.echo(f"Worker idle: listening quietly (poll every {poll_interval:g}s).")
                was_idle = True
            try:
                time.sleep(poll_interval)
            except KeyboardInterrupt:
                _interrupted()
        else:
            was_idle = False
