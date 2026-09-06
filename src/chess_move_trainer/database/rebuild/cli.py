"""Thin Typer adapters for DB-08 rebuild operations."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS
from .configuration import RebuildConfigurationError, load_rebuild_configuration
from .candidate import CandidateOutcome, stage_candidate
from .replacement import ReplacementError, ReplacementOutcome, replace_rebuilt_neighbour
from .rollback import (
    RollbackError,
    RollbackInputError,
    RollbackOutcome,
    rollback_rebuilt_neighbour,
)
from .refresh import RefreshInputError, RefreshOutcome, refresh_database
from .snapshots import SnapshotError, SnapshotOutcome, create_snapshot
from .verification import VerificationTarget, verify_rebuild_target


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Safely refresh, verify, snapshot, replace, or roll back the managed rebuilt neighbour.",
)


@app.command("refresh")
def refresh(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit YAML configuration containing rebuilt_neighbour.",
    ),
    opening_source_dir: Path | None = typer.Option(
        None,
        "--opening-source-dir",
        "--source-dir",
        help="Optional local directory containing a.tsv through e.tsv.",
    ),
    raw_root: Path | None = typer.Option(
        None,
        "--raw-root",
        help="Optional retained local raw-data root containing games/YYYY/MM.json.",
    ),
    trainer_chesscom_uuid: str | None = typer.Option(
        None,
        "--trainer-chesscom-uuid",
        help="Trainer UUID required when --raw-root is supplied.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Refresh the configured rebuilt neighbour from explicit local sources."""

    try:
        configuration = load_rebuild_configuration(config)
        outcome = refresh_database(
            configuration,
            opening_source_dir=opening_source_dir,
            raw_root=raw_root,
            trainer_chesscom_uuid=trainer_chesscom_uuid,
        )
    except RebuildConfigurationError as error:
        raise typer.BadParameter(str(error), param_hint="--config") from error
    except RefreshInputError as error:
        raise typer.BadParameter(
            str(error), param_hint="--raw-root/--trainer-chesscom-uuid"
        ) from error
    except KeyboardInterrupt:
        typer.echo("Interrupted.", err=True)
        raise typer.Exit(code=130) from None
    except Exception as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error

    _render_refresh(outcome, json_output)


@app.command("verify")
def verify(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit YAML configuration containing rebuilt_neighbour.",
    ),
    target: VerificationTarget = typer.Option(
        VerificationTarget.NEIGHBOUR,
        "--target",
        help="Managed target to verify: neighbour, candidate, or snapshot.",
    ),
    snapshot: Path | None = typer.Option(
        None,
        "--snapshot",
        help="Explicit SQLite snapshot path when --target snapshot is selected.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Verify structure and replacement readiness of one managed rebuild target."""

    try:
        configuration = load_rebuild_configuration(config)
        result = verify_rebuild_target(
            configuration,
            target,
            snapshot_path=snapshot,
        )
    except RebuildConfigurationError as error:
        raise typer.BadParameter(str(error), param_hint="--config") from error
    except ValueError as error:
        raise typer.BadParameter(str(error), param_hint="--target/--snapshot") from error
    except KeyboardInterrupt:
        _interrupted()
    except Exception as error:
        _operational_error(error)

    _render_verification(result, json_output)


@app.command("snapshot")
def snapshot(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit YAML configuration containing rebuilt_neighbour.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Create and verify a standalone snapshot of the configured neighbour."""

    try:
        configuration = load_rebuild_configuration(config)
        outcome = create_snapshot(configuration)
    except RebuildConfigurationError as error:
        raise typer.BadParameter(str(error), param_hint="--config") from error
    except SnapshotError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    except KeyboardInterrupt:
        _interrupted()
    except Exception as error:
        _operational_error(error)

    _render_snapshot(outcome, json_output)


@app.command("candidate")
def candidate(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit YAML configuration containing rebuilt_neighbour.",
    ),
    opening_source_dir: Path | None = typer.Option(
        None,
        "--opening-source-dir",
        "--source-dir",
        help="Optional local directory containing a.tsv through e.tsv.",
    ),
    raw_root: Path | None = typer.Option(
        None,
        "--raw-root",
        help="Optional retained local raw-data root containing games/YYYY/MM.json.",
    ),
    trainer_chesscom_uuid: str | None = typer.Option(
        None,
        "--trainer-chesscom-uuid",
        help="Trainer UUID required when --raw-root is supplied.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Build and verify the package-owned sibling candidate in isolation."""

    try:
        configuration = load_rebuild_configuration(config)
        outcome = stage_candidate(
            configuration,
            opening_source_dir=opening_source_dir,
            raw_root=raw_root,
            trainer_chesscom_uuid=trainer_chesscom_uuid,
        )
    except RebuildConfigurationError as error:
        raise typer.BadParameter(str(error), param_hint="--config") from error
    except RefreshInputError as error:
        raise typer.BadParameter(
            str(error), param_hint="--raw-root/--trainer-chesscom-uuid"
        ) from error
    except KeyboardInterrupt:
        typer.echo("Interrupted.", err=True)
        raise typer.Exit(code=130) from None
    except Exception as error:
        _operational_error(error)

    _render_candidate(outcome, json_output)


@app.command("replace")
def replace(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit YAML configuration containing rebuilt_neighbour.",
    ),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Exclusively replace the neighbour from its verified sibling candidate."""

    try:
        configuration = load_rebuild_configuration(config)
        outcome = replace_rebuilt_neighbour(
            configuration,
            lock_timeout=lock_timeout,
        )
    except RebuildConfigurationError as error:
        raise typer.BadParameter(str(error), param_hint="--config") from error
    except ReplacementError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    except KeyboardInterrupt:
        typer.echo("Interrupted.", err=True)
        raise typer.Exit(code=130) from None
    except Exception as error:
        _operational_error(error)

    _render_replacement(outcome, json_output)


@app.command("rollback")
def rollback(
    config: Path = typer.Option(
        ...,
        "--config",
        help="Explicit YAML configuration containing rebuilt_neighbour.",
    ),
    snapshot: Path | None = typer.Option(
        None,
        "--snapshot",
        help="Optional retained managed snapshot; newest is used by default.",
    ),
    lock_timeout: float = typer.Option(
        DEFAULT_LOCK_TIMEOUT_SECONDS,
        "--lock-timeout",
        help="Finite positive SQLite lock wait in seconds.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON output."),
) -> None:
    """Exclusively roll back the neighbour from a retained managed snapshot."""

    try:
        configuration = load_rebuild_configuration(config)
        outcome = rollback_rebuilt_neighbour(
            configuration,
            snapshot_path=snapshot,
            lock_timeout=lock_timeout,
        )
    except RebuildConfigurationError as error:
        raise typer.BadParameter(str(error), param_hint="--config") from error
    except RollbackInputError as error:
        raise typer.BadParameter(str(error), param_hint="--snapshot") from error
    except RollbackError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error
    except KeyboardInterrupt:
        typer.echo("Interrupted.", err=True)
        raise typer.Exit(code=130) from None
    except Exception as error:
        _operational_error(error)

    _render_rollback(outcome, json_output)


def _render_refresh(result: RefreshOutcome, json_output: bool) -> None:
    exit_code = int(result.exit_code)
    if json_output:
        typer.echo(
            json.dumps(
                result.as_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            err=exit_code != 0,
        )
    else:
        lines = [
            result.message,
            f"Target: {result.database_path}",
        ]
        for stage in result.stages:
            lines.append(
                f"{stage.stage.value.title()}: {stage.status.value} - {stage.message}"
            )
        typer.echo("\n".join(lines), err=exit_code != 0)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


def _render_snapshot(result: SnapshotOutcome, json_output: bool) -> None:
    exit_code = int(result.exit_code)
    if json_output:
        typer.echo(
            json.dumps(
                result.as_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            err=exit_code != 0,
        )
    else:
        lines = [
            result.message,
            f"Source: {result.source_path}",
            f"Snapshot: {result.snapshot_path or 'none'}",
            f"Retained: {len(result.retained_snapshots)}",
        ]
        typer.echo("\n".join(lines), err=exit_code != 0)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


def _render_candidate(result: CandidateOutcome, json_output: bool) -> None:
    exit_code = int(result.exit_code)
    if json_output:
        typer.echo(
            json.dumps(
                result.as_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            err=exit_code != 0,
        )
    else:
        lines = [
            result.message,
            f"Candidate: {result.candidate_path}",
            (
                "Replacement-ready: "
                f"{'yes' if result.verification is not None and result.verification.replacement_ready else 'no'}"
            ),
        ]
        typer.echo("\n".join(lines), err=exit_code != 0)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


def _render_replacement(result: ReplacementOutcome, json_output: bool) -> None:
    _render_operation(result, json_output)


def _render_rollback(result: RollbackOutcome, json_output: bool) -> None:
    _render_operation(result, json_output)


def _render_operation(result: ReplacementOutcome | RollbackOutcome, json_output: bool) -> None:
    exit_code = int(result.exit_code)
    if json_output:
        typer.echo(
            json.dumps(
                result.as_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            err=exit_code != 0,
        )
    else:
        lines = [
            result.message,
            f"Neighbour: {result.neighbour_path}",
            f"Snapshot: {result.snapshot_path or 'none'}",
        ]
        if isinstance(result, ReplacementOutcome):
            lines.append(f"Candidate: {result.candidate_path}")
        else:
            lines.append(f"Selected snapshot: {result.selected_snapshot or 'none'}")
        typer.echo("\n".join(lines), err=exit_code != 0)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


def _render_verification(result: object, json_output: bool) -> None:
    exit_code = int(result.exit_code)
    if json_output:
        typer.echo(
            json.dumps(
                result.as_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            err=exit_code != 0,
        )
    else:
        lines = [
            result.message,
            f"Target: {result.target.value}",
            f"Path: {result.database_path}",
            f"Schema compatible: {'yes' if result.schema_compatible else 'no'}",
            f"PRAGMA user_version: {result.user_version}",
            f"SQLite integrity: {result.integrity_result}",
            f"Foreign-key integrity: {'ok' if not result.foreign_key_errors else 'invalid'}",
            f"Openings ready: {'yes' if result.openings_ready else 'no'} "
            f"(labels={result.opening_count}, routes={result.opening_route_count}, "
            f"moves={result.opening_move_count}, positions={result.position_count})",
            f"Games ready: {'yes' if result.games_ready else 'no'} "
            f"(games={result.game_count}, positions={result.game_position_count})",
        ]
        typer.echo("\n".join(lines), err=exit_code != 0)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)


def _interrupted() -> None:
    typer.echo("Interrupted.", err=True)
    raise typer.Exit(code=130)


def _operational_error(error: Exception) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=1) from error


__all__ = ["app"]
