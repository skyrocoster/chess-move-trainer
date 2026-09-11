"""Shared CLI rendering and error helpers."""

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


def _run_lifecycle(service: Callable[[], LifecycleResult]) -> None:
    """Run one fixed-path service and render only its ordinary result data."""

    try:
        result = service()
    except KeyboardInterrupt:
        _interrupted()
    except Exception as error:
        _operational_error(error, 1)

    if result.database_path != DEFAULT_DATABASE_PATH:
        _operational_error(
            RuntimeError(
                "lifecycle service returned a destination other than "
                f"{DEFAULT_DATABASE_PATH}"
            ),
            1,
        )
    if result.exit_code == 130:
        _interrupted()
    if result.exit_code not in (0, 1, 2):
        _operational_error(RuntimeError("lifecycle service returned an invalid exit code"), 1)
    typer.echo(
        f"{result.message}\nTarget: {DEFAULT_DATABASE_PATH}",
        err=result.exit_code != 0,
    )
    if result.exit_code != 0:
        raise typer.Exit(code=result.exit_code)


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


def _render_preferred_setup(result: PreferredMoveSetupResult) -> None:
    """Render only the five ordinary setup summary counts."""

    typer.echo(
        "\n".join(
            (
                f"Examined games: {result.examined_games}",
                f"Skipped games: {result.skipped_games}",
                f"Qualifying positions: {result.qualifying_positions}",
                f"Periods applied: {result.periods_applied}",
                f"Conflicting positions: {result.conflicting_positions}",
            )
        )
    )


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
