"""Fixed-destination lifecycle services."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final, Literal

from .games.acquisition import (
    AcquisitionClock,
    AcquisitionResult,
    JsonTransport,
    acquire_incremental_months,
    acquire_months,
)
from .games.configuration import load_acquire_configuration
from .games.persistence import GameRepository, import_raw_month, import_raw_months
from .openings.acquisition import (
    OpeningAcquisitionResult,
    OpeningAcquisitionTransport,
    acquire_openings,
)
from .openings.persistence import (
    CataloguePublication,
    OpeningCatalogueRepository,
    import_opening_catalogue,
)
from .schema import create_schema

DEFAULT_DATABASE_PATH: Final[Path] = Path("data/database/chess.db")
DEFAULT_RAW_ROOT: Final[Path] = Path("data/chess-com/raw")
DEFAULT_OPENING_SOURCE_DIR: Final[Path] = Path("data/chess-com/openings")
DEFAULT_GAMES_CONFIGURATION: Final[Path] = Path("data/chess-com/db-09-games.yaml")
LifecycleExitCode = Literal[0, 1, 2, 130]


class LifecycleOperation(str, Enum):
    """The three public direct data-loading operations."""

    SETUP = "setup"
    UPDATE_GAMES = "update games"
    UPDATE_OPENINGS = "update openings"


@dataclass(frozen=True, slots=True)
class LifecycleResult:
    """Ordinary result data crossing from a lifecycle service to its adapter."""

    operation: LifecycleOperation
    database_path: Path = DEFAULT_DATABASE_PATH
    message: str = ""
    exit_code: LifecycleExitCode = 0


def setup_database() -> LifecycleResult:
    """Create and populate the one fixed database."""

    return _setup_database()


def update_games() -> LifecycleResult:
    """Dispatch the fixed-path direct game-update operation."""

    return _update_games()


def update_openings() -> LifecycleResult:
    """Dispatch the fixed-path direct opening-update operation."""

    return _update_openings()


def _setup_database(
    *,
    _database_path: str | Path = DEFAULT_DATABASE_PATH,
    _raw_root: str | Path = DEFAULT_RAW_ROOT,
    _opening_source_dir: str | Path = DEFAULT_OPENING_SOURCE_DIR,
    _games_configuration: str | Path = DEFAULT_GAMES_CONFIGURATION,
    _game_transport: JsonTransport | None = None,
    _game_clock: AcquisitionClock | None = None,
    _opening_transport: OpeningAcquisitionTransport | None = None,
    _sleep: Callable[[float], None] | None = None,
) -> LifecycleResult:
    """Run setup with private seams for deterministic, temporary-path proof."""

    database_path = Path(_database_path)
    if _path_exists(database_path):
        return _failure(
            database_path,
            f"Setup refused: database already exists: {database_path}",
        )

    created_by_setup = False
    try:
        sidecar_cleanup_error = _remove_stale_database_sidecars(database_path)
        if sidecar_cleanup_error is not None:
            raise SetupError(
                f"stale database sidecar cleanup failed: {sidecar_cleanup_error}"
            )
        schema_result = create_schema(database_path)
        created_by_setup = schema_result.created
        if not created_by_setup:
            raise SetupError(
                "setup refused because the database appeared before it could be created"
            )

        configuration = load_acquire_configuration(Path(_games_configuration))
        game_acquisition = acquire_months(
            configuration,
            Path(_raw_root),
            transport=_game_transport,
            clock=_game_clock,
            sleep=(time.sleep if _sleep is None else _sleep),
        )
        _require_game_acquisition(game_acquisition)

        game_import = import_raw_months(
            Path(_raw_root),
            configuration.trainer_chesscom_uuid,
            GameRepository(database_path),
            bulk=True,
        )
        if not game_import.completed:
            failure = game_import.failure
            detail = "game import failed"
            if failure is not None:
                detail = f"game import failed for {failure.game_uuid}: {failure.message}"
            raise SetupError(detail)

        opening_acquisition = acquire_openings(
            Path(_opening_source_dir),
            transport=_opening_transport,
            sleep=(time.sleep if _sleep is None else _sleep),
        )
        _require_opening_acquisition(opening_acquisition)

        opening_publication = import_opening_catalogue(
            Path(_opening_source_dir), OpeningCatalogueRepository(database_path)
        )
    except KeyboardInterrupt:
        if created_by_setup:
            _remove_created_database(database_path)
        raise
    except Exception as error:
        cleanup_error = None
        if created_by_setup:
            cleanup_error = _remove_created_database(database_path)
        message = f"Setup failed: {error}"
        if cleanup_error is not None:
            message = f"{message}; cleanup failed: {cleanup_error}"
        return _failure(database_path, message)

    return _success(
        database_path,
        "Setup completed: "
        f"imported {game_import.imported_count} game(s), "
        f"skipped {game_import.skipped_count}; "
        f"published {opening_publication.opening_count} opening label(s), "
        f"{opening_publication.route_count} route(s), and "
        f"{opening_publication.move_count} route move(s).",
        operation=LifecycleOperation.SETUP,
    )


def _update_games(
    *,
    _database_path: str | Path = DEFAULT_DATABASE_PATH,
    _raw_root: str | Path = DEFAULT_RAW_ROOT,
    _games_configuration: str | Path = DEFAULT_GAMES_CONFIGURATION,
    _game_transport: JsonTransport | None = None,
    _game_clock: AcquisitionClock | None = None,
    _sleep: Callable[[float], None] | None = None,
) -> LifecycleResult:
    """Refetch and import the saved month ledger one month at a time."""

    database_path = Path(_database_path)
    raw_root = Path(_raw_root)
    try:
        configuration = load_acquire_configuration(Path(_games_configuration))
        acquisition = acquire_incremental_months(
            configuration,
            raw_root,
            transport=_game_transport,
            clock=_game_clock,
            sleep=(time.sleep if _sleep is None else _sleep),
        )

        repository = GameRepository(database_path)
        imported_count = 0
        skipped_count = 0
        warnings: list[str] = []
        failures = [
            f"{failure.month or 'archive discovery'}: {failure.message}"
            for failure in acquisition.failures
        ]
        try:
            repository.validate()
        except Exception as error:
            failures.append(f"database: {error}")
        else:
            for month in acquisition.published_months:
                year, month_number = (int(month[:4]), int(month[5:]))
                month_path = raw_root / "games" / f"{year:04d}" / f"{month_number:02d}.json"
                try:
                    result = import_raw_month(
                        month_path,
                        configuration.trainer_chesscom_uuid,
                        repository,
                    )
                except KeyboardInterrupt:
                    raise
                except Exception as error:
                    failures.append(f"{month}: {error}")
                    continue
                imported_count += result.imported_count
                skipped_count += result.skipped_count
                warnings.extend(
                    f"{warning.game_uuid or 'unknown game'}: {warning.message}"
                    for warning in result.warnings
                )
                if result.failure is not None:
                    failures.append(
                        f"{month}: {result.failure.game_uuid}: {result.failure.message}"
                    )

        detail = (
            "Update games "
            f"processed {len(acquisition.published_months)} month(s), "
            f"imported {imported_count} game(s), skipped {skipped_count}."
        )
        if warnings:
            detail += " Skipped games: " + "; ".join(warnings)
        if failures:
            detail += " Failures: " + "; ".join(failures)
            return _failure(
                database_path,
                detail,
                operation=LifecycleOperation.UPDATE_GAMES,
            )
        return _success(
            database_path,
            detail,
            operation=LifecycleOperation.UPDATE_GAMES,
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        return _failure(
            database_path,
            f"Update games failed: {error}",
            operation=LifecycleOperation.UPDATE_GAMES,
        )


def _update_openings(
    *,
    _database_path: str | Path = DEFAULT_DATABASE_PATH,
    _opening_source_dir: str | Path = DEFAULT_OPENING_SOURCE_DIR,
    _opening_transport: OpeningAcquisitionTransport | None = None,
    _sleep: Callable[[float], None] | None = None,
) -> LifecycleResult:
    """Acquire and publish one complete latest opening catalogue."""

    database_path = Path(_database_path)
    source_dir = Path(_opening_source_dir)
    try:
        acquisition = acquire_openings(
            source_dir,
            transport=_opening_transport,
            sleep=(time.sleep if _sleep is None else _sleep),
        )
        if not acquisition.completed:
            details = "; ".join(
                f"{failure.subject}: {failure.message}"
                for failure in acquisition.failures
            )
            return _failure(
                database_path,
                f"Update openings failed: {details}",
                operation=LifecycleOperation.UPDATE_OPENINGS,
            )

        publication = import_opening_catalogue(
            source_dir,
            OpeningCatalogueRepository(database_path),
        )
        return _success(
            database_path,
            "Update openings completed: "
            f"published {publication.opening_count} opening label(s), "
            f"{publication.route_count} route(s), and "
            f"{publication.move_count} route move(s).",
            operation=LifecycleOperation.UPDATE_OPENINGS,
        )
    except KeyboardInterrupt:
        raise
    except Exception as error:
        return _failure(
            database_path,
            f"Update openings failed: {error}",
            operation=LifecycleOperation.UPDATE_OPENINGS,
        )


class SetupError(RuntimeError):
    """Raised internally when one setup composition step is incomplete."""


def _require_game_acquisition(result: AcquisitionResult) -> None:
    if result.completed:
        return
    details = "; ".join(
        f"{failure.month or 'archive discovery'}: {failure.message}"
        for failure in result.failures
    )
    raise SetupError(f"game acquisition failed: {details}")


def _require_opening_acquisition(result: OpeningAcquisitionResult) -> None:
    if result.completed:
        return
    details = "; ".join(
        f"{failure.subject}: {failure.message}" for failure in result.failures
    )
    raise SetupError(f"opening acquisition failed: {details}")


def _path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _remove_created_database(path: Path) -> OSError | None:
    first_error = _remove_database_file(path)
    for sidecar in _database_sidecars(path):
        error = _remove_database_file(sidecar)
        if first_error is None:
            first_error = error
    return first_error


def _remove_stale_database_sidecars(path: Path) -> OSError | None:
    """Remove exact sidecars left beside an absent setup target."""

    first_error: OSError | None = None
    for sidecar in _database_sidecars(path):
        error = _remove_database_file(sidecar)
        if first_error is None:
            first_error = error
    return first_error


def _remove_database_file(path: Path) -> OSError | None:
    if not path.is_file() or path.is_symlink():
        return None
    try:
        path.unlink()
    except OSError as error:
        return error
    return None


def _database_sidecars(path: Path) -> tuple[Path, ...]:
    return tuple(path.with_name(path.name + suffix) for suffix in ("-journal", "-wal", "-shm"))


def _success(
    path: Path,
    message: str,
    *,
    operation: LifecycleOperation = LifecycleOperation.SETUP,
) -> LifecycleResult:
    return LifecycleResult(
        operation=operation,
        database_path=path,
        message=message,
        exit_code=0,
    )


def _failure(
    path: Path,
    message: str,
    *,
    operation: LifecycleOperation = LifecycleOperation.SETUP,
) -> LifecycleResult:
    return LifecycleResult(
        operation=operation,
        database_path=path,
        message=message,
        exit_code=1,
    )


def _pending(operation: LifecycleOperation, detail: str) -> LifecycleResult:
    return LifecycleResult(
        operation=operation,
        message=f"{operation.value} is not available yet: {detail}",
        exit_code=1,
    )


__all__ = [
    "DEFAULT_DATABASE_PATH",
    "LifecycleExitCode",
    "LifecycleOperation",
    "LifecycleResult",
    "setup_database",
    "update_games",
    "update_openings",
]
