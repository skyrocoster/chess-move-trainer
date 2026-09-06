"""Idempotent local refresh orchestration for the DB-08 neighbour."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from ..connection import (
    DEFAULT_LOCK_TIMEOUT_SECONDS,
    _open_connection,
    _validate_lock_timeout,
)
from ..games.normalization import NormalizedGame, normalize_game
from ..games.persistence import GameRepository, ImportResult, import_raw_months
from ..games.raw_storage import load_month
from ..openings import (
    CataloguePublication,
    OpeningCatalogueRepository,
)
from ..openings.source import OpeningRouteSource, load_opening_sources
from ..schema import SchemaIncompatibleError, create_schema
from .configuration import RebuildConfiguration
from .operations import ExitCode, OperationExitCode, OperationStatus, RebuildOperation
from .verification import (
    VerificationResult,
    VerificationStatus,
    VerificationTarget,
    verify_rebuild_target,
)


class RefreshInputError(ValueError):
    """Raised when explicit refresh inputs cannot be used safely."""


class RefreshStage(str, Enum):
    """The independently reported parts of one refresh."""

    SCHEMA = "schema"
    OPENINGS = "openings"
    GAMES = "games"
    VERIFICATION = "verification"


class RefreshStageStatus(str, Enum):
    """The result of one refresh stage."""

    SUCCEEDED = "succeeded"
    SKIPPED = "skipped"
    OMITTED = "omitted"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class RefreshInputs:
    """Explicit local inputs for a refresh; no acquisition settings are accepted."""

    configuration: RebuildConfiguration
    opening_source_dir: Path | None = None
    raw_root: Path | None = None
    trainer_chesscom_uuid: UUID | str | None = None
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if not isinstance(self.configuration, RebuildConfiguration):
            raise RefreshInputError("configuration must be a RebuildConfiguration")
        for field_name in ("opening_source_dir", "raw_root"):
            value = getattr(self, field_name)
            if value is None:
                continue
            try:
                normalized = Path(value).expanduser().resolve(strict=False)
            except (OSError, RuntimeError, TypeError, ValueError) as error:
                raise RefreshInputError(f"{field_name} must be a safe path: {error}") from error
            object.__setattr__(self, field_name, normalized)

        if self.trainer_chesscom_uuid is not None:
            try:
                trainer_uuid = (
                    self.trainer_chesscom_uuid
                    if isinstance(self.trainer_chesscom_uuid, UUID)
                    else UUID(self.trainer_chesscom_uuid)
                )
            except (AttributeError, TypeError, ValueError) as error:
                raise RefreshInputError(
                    "trainer_chesscom_uuid must be a valid UUID"
                ) from error
            object.__setattr__(self, "trainer_chesscom_uuid", trainer_uuid)

        try:
            _validate_lock_timeout(self.lock_timeout)
        except ValueError as error:
            raise RefreshInputError(str(error)) from error


@dataclass(frozen=True, slots=True)
class RefreshStageOutcome:
    """Stable facts and diagnostics for one refresh stage."""

    stage: RefreshStage
    status: RefreshStageStatus
    message: str
    created: bool | None = None
    publication: CataloguePublication | None = None
    import_result: ImportResult | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return deterministic ordinary values for CLI JSON output."""

        value: dict[str, Any] = {
            "message": self.message,
            "stage": self.stage.value,
            "status": self.status.value,
        }
        if self.created is not None:
            value["created"] = self.created
        if self.publication is not None:
            value["publication"] = {
                "move_count": self.publication.move_count,
                "opening_count": self.publication.opening_count,
                "route_count": self.publication.route_count,
            }
        if self.import_result is not None:
            value["import"] = {
                "completed": self.import_result.completed,
                "failure": (
                    None
                    if self.import_result.failure is None
                    else {
                        "game_uuid": self.import_result.failure.game_uuid,
                        "message": self.import_result.failure.message,
                    }
                ),
                "imported_count": self.import_result.imported_count,
                "skipped_count": self.import_result.skipped_count,
                "warnings": [warning.message for warning in self.import_result.warnings],
            }
        return value


@dataclass(frozen=True, slots=True)
class RefreshOutcome:
    """The overall result crossing from the refresh service to its CLI adapter."""

    operation: RebuildOperation
    status: OperationStatus
    message: str
    exit_code: ExitCode
    database_path: Path
    stages: tuple[RefreshStageOutcome, ...]
    verification: VerificationResult | None

    @property
    def replacement_ready(self) -> bool:
        """Whether the final verifier accepted the neighbour for replacement."""

        return self.verification is not None and self.verification.replacement_ready

    @property
    def completed(self) -> bool:
        """Whether every required stage and final readiness check passed."""

        return self.status is OperationStatus.SUCCEEDED

    def as_dict(self) -> dict[str, Any]:
        """Return deterministic ordinary values for JSON CLI output."""

        return {
            "database_path": str(self.database_path),
            "exit_code": int(self.exit_code),
            "message": self.message,
            "operation": self.operation.value,
            "replacement_ready": self.replacement_ready,
            "stages": [stage.as_dict() for stage in self.stages],
            "status": self.status.value,
            "verification": (
                None if self.verification is None else self.verification.as_dict()
            ),
        }


# The alias keeps the refresh-specific vocabulary convenient without creating a
# second set of overall status and exit-code categories.
RefreshStatus = OperationStatus


def refresh_database(
    configuration: RebuildConfiguration,
    *,
    opening_source_dir: str | Path | None = None,
    raw_root: str | Path | None = None,
    trainer_chesscom_uuid: UUID | str | None = None,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> RefreshOutcome:
    """Refresh one configured neighbour from explicit local sources only.

    The schema is established first.  Opening and game publication then run as
    separate stages, so a failure or omission in one does not erase successful
    work in the other.  A later verifier determines whether the result is only
    a valid checkpoint or is ready for replacement.
    """

    inputs = RefreshInputs(
        configuration=configuration,
        opening_source_dir=opening_source_dir,
        raw_root=raw_root,
        trainer_chesscom_uuid=trainer_chesscom_uuid,
        lock_timeout=lock_timeout,
    )
    return _run_refresh(inputs)


def refresh_rebuilt_neighbour(inputs: RefreshInputs) -> RefreshOutcome:
    """Run a refresh from an already validated typed input object."""

    if not isinstance(inputs, RefreshInputs):
        raise RefreshInputError("inputs must be RefreshInputs")
    return _run_refresh(inputs)


def _run_refresh(inputs: RefreshInputs) -> RefreshOutcome:
    configuration = inputs.configuration
    database_path = configuration.rebuilt_neighbour
    stages: list[RefreshStageOutcome] = []

    try:
        schema_result = create_schema(database_path, lock_timeout=inputs.lock_timeout)
    except KeyboardInterrupt:
        raise
    except SchemaIncompatibleError as error:
        stages.append(
            RefreshStageOutcome(
                RefreshStage.SCHEMA,
                RefreshStageStatus.FAILED,
                f"schema is incompatible: {error}",
            )
        )
        return _finish(
            inputs,
            stages,
            status=OperationStatus.INCOMPATIBLE,
            message="Refresh could not start because the neighbour schema is incompatible.",
        )
    except Exception as error:
        stages.append(
            RefreshStageOutcome(
                RefreshStage.SCHEMA,
                RefreshStageStatus.FAILED,
                f"schema could not be created or opened: {error}",
            )
        )
        return _finish(
            inputs,
            stages,
            status=OperationStatus.FAILED,
            message="Refresh could not start because the neighbour schema was unavailable.",
        )

    stages.append(
        RefreshStageOutcome(
            RefreshStage.SCHEMA,
            RefreshStageStatus.SUCCEEDED,
            (
                "created schema v1"
                if schema_result.created
                else "schema v1 is already compatible"
            ),
            created=schema_result.created,
        )
    )

    current = _current_verification(inputs)
    stages.append(_run_openings(inputs, current))
    stages.append(_run_games(inputs, current))
    return _finish(inputs, stages)


def _current_verification(inputs: RefreshInputs) -> VerificationResult | None:
    try:
        return verify_rebuild_target(
            inputs.configuration,
            VerificationTarget.NEIGHBOUR,
            lock_timeout=inputs.lock_timeout,
        )
    except KeyboardInterrupt:
        raise
    except Exception:
        # The operation still attempts both explicitly supplied stages.  The
        # final verification below reports the actual reason for failure.
        return None


def _run_openings(
    inputs: RefreshInputs, current: VerificationResult | None
) -> RefreshStageOutcome:
    source_dir = inputs.opening_source_dir
    if source_dir is None:
        if current is not None and current.openings_ready:
            return RefreshStageOutcome(
                RefreshStage.OPENINGS,
                RefreshStageStatus.SKIPPED,
                "opening source omitted; existing opening catalogue is already ready",
            )
        return RefreshStageOutcome(
            RefreshStage.OPENINGS,
            RefreshStageStatus.OMITTED,
            "opening source omitted; no opening publication was requested",
        )
    if not _is_directory(source_dir):
        return RefreshStageOutcome(
            RefreshStage.OPENINGS,
            RefreshStageStatus.UNAVAILABLE,
            f"opening source is unavailable or not a directory: {source_dir}",
        )

    try:
        routes = load_opening_sources(source_dir)
        if _opening_source_matches(
            inputs.configuration.rebuilt_neighbour,
            routes,
            lock_timeout=inputs.lock_timeout,
        ):
            return RefreshStageOutcome(
                RefreshStage.OPENINGS,
                RefreshStageStatus.SKIPPED,
                "opening source already matches the current catalogue; publication skipped",
            )
        publication = OpeningCatalogueRepository(
            inputs.configuration.rebuilt_neighbour,
            lock_timeout=inputs.lock_timeout,
        ).replace(routes)
    except KeyboardInterrupt:
        raise
    except Exception as error:
        return RefreshStageOutcome(
            RefreshStage.OPENINGS,
            RefreshStageStatus.FAILED,
            f"opening publication failed: {error}",
        )
    return RefreshStageOutcome(
        RefreshStage.OPENINGS,
        RefreshStageStatus.SUCCEEDED,
        (
            f"published {publication.opening_count} opening label(s), "
            f"{publication.route_count} route(s), and {publication.move_count} move(s)"
        ),
        publication=publication,
    )


def _run_games(
    inputs: RefreshInputs, current: VerificationResult | None
) -> RefreshStageOutcome:
    raw_root = inputs.raw_root
    if raw_root is None:
        if current is not None and current.games_ready:
            return RefreshStageOutcome(
                RefreshStage.GAMES,
                RefreshStageStatus.SKIPPED,
                "game source omitted; existing imported games are already ready",
            )
        return RefreshStageOutcome(
            RefreshStage.GAMES,
            RefreshStageStatus.OMITTED,
            "game source omitted; no game import was requested",
        )
    if not _is_directory(raw_root):
        return RefreshStageOutcome(
            RefreshStage.GAMES,
            RefreshStageStatus.UNAVAILABLE,
            f"game source is unavailable or not a directory: {raw_root}",
        )
    if inputs.trainer_chesscom_uuid is None:
        return RefreshStageOutcome(
            RefreshStage.GAMES,
            RefreshStageStatus.UNAVAILABLE,
            "game source is unavailable because trainer_chesscom_uuid was not supplied",
        )

    try:
        normalized_games = _load_normalized_games(raw_root, inputs.trainer_chesscom_uuid)
        if normalized_games is not None and _games_source_matches(
            inputs.configuration.rebuilt_neighbour,
            normalized_games,
            lock_timeout=inputs.lock_timeout,
        ):
            return RefreshStageOutcome(
                RefreshStage.GAMES,
                RefreshStageStatus.SKIPPED,
                (
                    f"{len(normalized_games)} unchanged valid game(s) already match "
                    "the current database; import skipped"
                ),
            )
        result = import_raw_months(
            raw_root,
            inputs.trainer_chesscom_uuid,
            GameRepository(
                inputs.configuration.rebuilt_neighbour,
                lock_timeout=inputs.lock_timeout,
            ),
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        return RefreshStageOutcome(
            RefreshStage.GAMES,
            RefreshStageStatus.FAILED,
            f"game import failed: {error}",
        )

    if result.failure is not None:
        message = (
            f"game import stopped after {result.imported_count} committed game(s); "
            f"{result.failure.game_uuid}: {result.failure.message}"
        )
        status = RefreshStageStatus.FAILED
    else:
        message = (
            f"imported {result.imported_count} game(s) and skipped "
            f"{result.skipped_count} invalid game(s)"
        )
        status = RefreshStageStatus.SUCCEEDED
    return RefreshStageOutcome(
        RefreshStage.GAMES,
        status,
        message,
        import_result=result,
    )


def _finish(
    inputs: RefreshInputs,
    stages: list[RefreshStageOutcome],
    *,
    status: OperationStatus | None = None,
    message: str | None = None,
) -> RefreshOutcome:
    verification: VerificationResult | None
    try:
        verification = verify_rebuild_target(
            inputs.configuration,
            VerificationTarget.NEIGHBOUR,
            lock_timeout=inputs.lock_timeout,
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        verification = None
        verification_message = f"final verification failed: {error}"
    else:
        verification_message = (
            f"final verification is {verification.status.value}; "
            f"replacement_ready={'yes' if verification.replacement_ready else 'no'}"
        )

    required_stages = {
        RefreshStage.SCHEMA,
        RefreshStage.OPENINGS,
        RefreshStage.GAMES,
    }
    stage_map = {stage.stage: stage for stage in stages}
    stages_ready = all(
        stage_map.get(stage) is not None
        and stage_map[stage].status
        in {RefreshStageStatus.SUCCEEDED, RefreshStageStatus.SKIPPED}
        for stage in required_stages
    )
    final_ready = verification is not None and verification.replacement_ready

    if status is None:
        if verification is not None and verification.status is VerificationStatus.INCOMPATIBLE:
            status = OperationStatus.INCOMPATIBLE
        elif stages_ready and final_ready:
            status = OperationStatus.SUCCEEDED
        else:
            status = OperationStatus.FAILED

    if message is None:
        if status is OperationStatus.SUCCEEDED:
            message = "Refresh completed: the neighbour is replacement-ready."
        elif status is OperationStatus.INCOMPATIBLE:
            message = "Refresh failed: the neighbour is incompatible with schema v1."
        else:
            message = "Refresh incomplete: required stages or final readiness did not pass."

    stages.append(
        RefreshStageOutcome(
            RefreshStage.VERIFICATION,
            (
                RefreshStageStatus.SUCCEEDED
                if final_ready
                else RefreshStageStatus.FAILED
            ),
            verification_message,
        )
    )
    exit_code = _exit_code_for(status)
    return RefreshOutcome(
        operation=RebuildOperation.REFRESH,
        status=status,
        message=message,
        exit_code=exit_code,
        database_path=inputs.configuration.rebuilt_neighbour,
        stages=tuple(stages),
        verification=verification,
    )


def _exit_code_for(status: OperationStatus) -> ExitCode:
    if status is OperationStatus.SUCCEEDED:
        return OperationExitCode.SUCCEEDED
    if status is OperationStatus.INCOMPATIBLE:
        return OperationExitCode.INCOMPATIBLE
    return OperationExitCode.FAILED


def _is_directory(path: Path) -> bool:
    try:
        return path.is_dir()
    except OSError:
        return False


def _opening_source_matches(
    database_path: Path,
    routes: tuple[OpeningRouteSource, ...],
    *,
    lock_timeout: float,
) -> bool:
    """Compare normalized source routes with the current published catalogue."""

    expected_labels = {(route.eco, route.name) for route in routes}
    expected_routes = {
        (route.eco, route.name, route.moves_uci, route.endpoint_key) for route in routes
    }
    with _open_connection(database_path, "read-only", lock_timeout) as connection:
        labels = {
            (str(row[0]), str(row[1]))
            for row in connection.exec_driver_sql(
                "SELECT do_eco, do_name FROM datasource_opening"
            ).all()
        }
        if labels != expected_labels:
            return False

        current_routes: set[tuple[str, str, tuple[str, ...], tuple[str, ...]]] = set()
        route_rows = connection.exec_driver_sql(
            """
            SELECT r.dor_route_id, o.do_eco, o.do_name,
                   p.dp_placement, p.dp_side_to_move,
                   p.dp_castling_rights, p.dp_legal_en_passant
            FROM derived_opening_route AS r
            JOIN datasource_opening AS o
              ON o.do_opening_id = r.datasource_opening_id
            JOIN derived_position AS p
              ON p.dp_position_id = r.derived_position_id
            """
        ).all()
        for route_id, eco, name, placement, side, castling, en_passant in route_rows:
            move_rows = connection.exec_driver_sql(
                """
                SELECT dorm_move_uci
                FROM derived_opening_route_move
                WHERE derived_opening_route_id = ?
                ORDER BY dorm_ply
                """,
                (route_id,),
            ).all()
            current_routes.add(
                (
                    str(eco),
                    str(name),
                    tuple(str(row[0]) for row in move_rows),
                    (str(placement), str(side), str(castling), str(en_passant)),
                )
            )
        return (
            len(route_rows) == len(expected_routes)
            and current_routes == expected_routes
        )


def _load_normalized_games(
    raw_root: Path,
    trainer_uuid: UUID,
) -> tuple[NormalizedGame, ...] | None:
    """Read and normalize local months, returning ``None`` for invalid games.

    Invalid raw games deliberately fall back to the accepted importer so its
    warning and continuation behavior remains unchanged.
    """

    games_root = raw_root / "games"
    month_paths = (
        sorted(games_root.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9].json"))
        if games_root.is_dir()
        else []
    )
    raw_games: list[object] = []
    for month_path in month_paths:
        raw_games.extend(load_month(month_path)["games"])

    normalized: list[NormalizedGame] = []
    for raw_game in raw_games:
        result = normalize_game(raw_game, trainer_uuid)
        if result.game is None:
            return None
        normalized.append(result.game)
    return tuple(normalized)


def _games_source_matches(
    database_path: Path,
    games: tuple[NormalizedGame, ...],
    *,
    lock_timeout: float,
) -> bool:
    """Compare normalized source games with their stored per-game output."""

    with _open_connection(database_path, "read-only", lock_timeout) as connection:
        for game in games:
            row = connection.exec_driver_sql(
                """
                SELECT dg_game_id, dg_source_url, dg_original_pgn,
                       dg_trainer_color, dg_trainer_chesscom_uuid,
                       dg_opponent_chesscom_uuid, dg_trainer_rating,
                       dg_opponent_rating, dg_started_at_utc, dg_ended_at_utc,
                       dg_trainer_outcome, dg_termination_reason,
                       dg_time_control_source, dg_time_class
                FROM datasource_game
                WHERE dg_chesscom_game_uuid = ?
                """,
                (str(game.chesscom_game_uuid),),
            ).first()
            if row is None or tuple(row[1:]) != _game_metadata(game):
                return False

            stored_occurrences = tuple(
                tuple(occurrence)
                for occurrence in connection.exec_driver_sql(
                    """
                    SELECT g.dgp_ply, p.dp_placement, p.dp_side_to_move,
                           p.dp_castling_rights, p.dp_legal_en_passant,
                           g.dgp_move_uci, g.dgp_halfmove_clock,
                           g.dgp_fullmove_number
                    FROM derived_game_position AS g
                    JOIN derived_position AS p
                      ON p.dp_position_id = g.derived_position_id
                    WHERE g.datasource_game_id = ?
                    ORDER BY g.dgp_ply
                    """,
                    (int(row[0]),),
                ).all()
            )
            expected_occurrences = tuple(
                (
                    occurrence.ply,
                    occurrence.position.placement,
                    occurrence.position.side_to_move,
                    occurrence.position.castling_rights,
                    occurrence.position.legal_en_passant,
                    occurrence.move_uci,
                    occurrence.halfmove_clock,
                    occurrence.fullmove_number,
                )
                for occurrence in game.occurrences
            )
            if stored_occurrences != expected_occurrences:
                return False
    return True


def _game_metadata(game: NormalizedGame) -> tuple[object, ...]:
    return (
        game.source_url,
        game.original_pgn,
        game.trainer_color,
        str(game.trainer_chesscom_uuid),
        (
            None
            if game.opponent_chesscom_uuid is None
            else str(game.opponent_chesscom_uuid)
        ),
        game.trainer_rating,
        game.opponent_rating,
        game.started_at_utc,
        game.ended_at_utc,
        game.trainer_outcome,
        game.termination_reason,
        game.time_control_source,
        game.time_class,
    )


__all__ = [
    "RefreshInputError",
    "RefreshInputs",
    "RefreshOutcome",
    "RefreshStage",
    "RefreshStageOutcome",
    "RefreshStageStatus",
    "RefreshStatus",
    "refresh_database",
    "refresh_rebuilt_neighbour",
]
