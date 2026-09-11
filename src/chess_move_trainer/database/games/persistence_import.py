"""Raw-game import orchestration over the game repository."""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import ExitStack
from pathlib import Path
from uuid import UUID

from .normalization import NormalizationResult, NormalizationWarning, normalize_game
from .persistence_repository import GamePersistenceError, GameRepository, ImportResult
from .raw_storage import load_month

def import_raw_games(
    raw_games: Iterable[object],
    trainer_uuid: UUID,
    repository: GameRepository,
) -> ImportResult:
    """Normalize first, then commit accepted games independently in source order."""

    return import_normalized_games(
        normalize_raw_games(raw_games, trainer_uuid),
        repository,
    )


def normalize_raw_games(
    raw_games: Iterable[object],
    trainer_uuid: UUID,
) -> tuple[NormalizationResult, ...]:
    """Normalize a source batch once while retaining warnings in source order."""

    return tuple(normalize_game(raw_game, trainer_uuid) for raw_game in raw_games)


def load_normalized_months(
    raw_root: Path,
    trainer_uuid: UUID,
) -> tuple[NormalizationResult, ...]:
    """Load and normalize every local month once in deterministic source order."""

    if not raw_root.is_dir():
        raise GamePersistenceError(f"raw root does not exist or is not a directory: {raw_root}")
    games_root = raw_root / "games"
    month_paths = (
        sorted(games_root.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9].json"))
        if games_root.is_dir()
        else []
    )
    raw_games: list[object] = []
    for month_path in month_paths:
        raw_games.extend(load_month(month_path)["games"])
    return normalize_raw_games(raw_games, trainer_uuid)


def import_normalized_games(
    normalized_games: Iterable[NormalizationResult],
    repository: GameRepository,
    *,
    bulk: bool = False,
) -> ImportResult:
    """Persist one already-normalized source batch in source order."""

    imported_count = 0
    skipped_count = 0
    warnings: list[NormalizationWarning] = []
    repository._last_import_writes = 0
    position_cache: dict[PositionIdentity, int] = {}
    normalized_iterator = iter(normalized_games)
    with ExitStack() as stack:
        connection: object | None = None
        for normalized in normalized_iterator:
            if normalized.game is None:
                skipped_count += 1
                assert normalized.warning is not None
                warnings.append(normalized.warning)
                continue
            if connection is None:
                try:
                    connection = stack.enter_context(repository._validated_connection())
                except KeyboardInterrupt:
                    raise
                except Exception as error:
                    return ImportResult(
                        imported_count=imported_count,
                        skipped_count=skipped_count,
                        warnings=tuple(warnings),
                        failure=ImportFailure(
                            game_uuid=str(normalized.game.chesscom_game_uuid),
                            message=f"game could not be persisted: {error}",
                        ),
                    )
            if bulk:
                try:
                    with connection.begin():
                        for pending in chain((normalized,), normalized_iterator):
                            if pending.game is None:
                                skipped_count += 1
                                assert pending.warning is not None
                                warnings.append(pending.warning)
                                continue
                            try:
                                repository._persist_in_transaction(
                                    connection,
                                    pending.game,
                                    position_cache=position_cache,
                                )
                            except KeyboardInterrupt:
                                raise
                            except Exception as error:
                                raise _BulkImportAbort(
                                    ImportResult(
                                        imported_count=0,
                                        skipped_count=skipped_count,
                                        warnings=tuple(warnings),
                                        failure=ImportFailure(
                                            game_uuid=str(pending.game.chesscom_game_uuid),
                                            message=f"game could not be persisted: {error}",
                                        ),
                                    )
                                ) from error
                            imported_count += 1
                except _BulkImportAbort as abort:
                    return abort.result
                return ImportResult(
                    imported_count=imported_count,
                    skipped_count=skipped_count,
                    warnings=tuple(warnings),
                    failure=None,
                )
            try:
                repository._persist_on_connection(
                    connection,
                    normalized.game,
                    position_cache=position_cache,
                )
            except KeyboardInterrupt:
                raise
            except Exception as error:
                return ImportResult(
                    imported_count=imported_count,
                    skipped_count=skipped_count,
                    warnings=tuple(warnings),
                    failure=ImportFailure(
                        game_uuid=str(normalized.game.chesscom_game_uuid),
                        message=f"game could not be persisted: {error}",
                    ),
                )
            imported_count += 1
    return ImportResult(
        imported_count=imported_count,
        skipped_count=skipped_count,
        warnings=tuple(warnings),
        failure=None,
    )


def import_raw_months(
    raw_root: Path,
    trainer_uuid: UUID,
    repository: GameRepository,
    *,
    bulk: bool = False,
) -> ImportResult:
    """Read only DB-03 month files in deterministic order and import their games."""

    return import_normalized_games(
        load_normalized_months(raw_root, trainer_uuid),
        repository,
        bulk=bulk,
    )


def import_raw_month(
    month_path: Path,
    trainer_uuid: UUID,
    repository: GameRepository,
) -> ImportResult:
    """Normalize and persist one validated month independently."""

    envelope = load_month(month_path)
    return import_raw_games(envelope["games"], trainer_uuid, repository)


