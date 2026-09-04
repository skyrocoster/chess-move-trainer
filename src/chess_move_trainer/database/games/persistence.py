"""Opaque per-game persistence and raw-game import orchestration."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions.repository import _PositionUnitOfWork
from ..schema import _assert_compatible_schema
from .normalization import NormalizationWarning, NormalizedGame, normalize_game
from .raw_storage import load_month


class GamePersistenceError(RuntimeError):
    """Raised when one normalized game cannot be persisted atomically."""


@dataclass(frozen=True, slots=True)
class PersistedGame:
    game_id: int
    corrected: bool
    occurrence_count: int


@dataclass(frozen=True, slots=True)
class ImportFailure:
    game_uuid: str
    message: str


@dataclass(frozen=True, slots=True)
class ImportResult:
    imported_count: int
    skipped_count: int
    warnings: tuple[NormalizationWarning, ...]
    failure: ImportFailure | None

    @property
    def completed(self) -> bool:
        return self.failure is None


class GameRepository:
    """Persist complete normalized games without exposing database handles."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        _checkpoint: Callable[[str], None] | None = None,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout
        self._checkpoint = _checkpoint if _checkpoint is not None else lambda _: None

    def validate(self) -> None:
        """Verify that the configured target is an existing compatible v1 database."""

        try:
            with _open_existing_connection(
                self._database_path, self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
        except Exception as error:
            raise GamePersistenceError(f"database cannot be used for game import: {error}") from error

    def persist(self, game: NormalizedGame) -> PersistedGame:
        """Insert or fully replace one prevalidated game in its own transaction."""

        if not isinstance(game, NormalizedGame):
            raise TypeError("game must be a fully normalized game")
        try:
            with _open_existing_connection(
                self._database_path, self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                with connection.begin():
                    existing = connection.execute(
                        text(
                            "SELECT dg_game_id FROM datasource_game "
                            "WHERE dg_chesscom_game_uuid = :game_uuid"
                        ),
                        {"game_uuid": str(game.chesscom_game_uuid)},
                    ).first()
                    corrected = existing is not None
                    if corrected:
                        game_id = int(existing[0])
                        connection.execute(
                            text(_UPDATE_GAME_SQL),
                            _metadata_parameters(game, game_id=game_id),
                        )
                    else:
                        connection.execute(text(_INSERT_GAME_SQL), _metadata_parameters(game))
                        inserted = connection.execute(
                            text(
                                "SELECT dg_game_id FROM datasource_game "
                                "WHERE dg_chesscom_game_uuid = :game_uuid"
                            ),
                            {"game_uuid": str(game.chesscom_game_uuid)},
                        ).one()
                        game_id = int(inserted[0])
                    self._checkpoint("metadata")

                    position_work = _PositionUnitOfWork(connection)
                    position_ids: list[int] = []
                    for occurrence in game.occurrences:
                        position_ids.append(position_work._resolve(occurrence.position))
                        self._checkpoint("position")

                    if corrected:
                        connection.execute(
                            text(
                                "DELETE FROM derived_game_position "
                                "WHERE datasource_game_id = :game_id"
                            ),
                            {"game_id": game_id},
                        )
                    for occurrence, position_id in zip(
                        game.occurrences, position_ids, strict=True
                    ):
                        connection.execute(
                            text(_INSERT_OCCURRENCE_SQL),
                            {
                                "game_id": game_id,
                                "ply": occurrence.ply,
                                "position_id": position_id,
                                "move_uci": occurrence.move_uci,
                                "halfmove_clock": occurrence.halfmove_clock,
                                "fullmove_number": occurrence.fullmove_number,
                            },
                        )
                        self._checkpoint("occurrence")
        except KeyboardInterrupt:
            raise
        except Exception as error:
            raise GamePersistenceError(f"game could not be persisted: {error}") from error

        return PersistedGame(
            game_id=game_id,
            corrected=corrected,
            occurrence_count=len(game.occurrences),
        )


def import_raw_games(
    raw_games: Iterable[object],
    trainer_uuid: UUID,
    repository: GameRepository,
) -> ImportResult:
    """Normalize first, then commit accepted games independently in source order."""

    imported_count = 0
    skipped_count = 0
    warnings: list[NormalizationWarning] = []
    for raw_game in raw_games:
        normalized = normalize_game(raw_game, trainer_uuid)
        if normalized.game is None:
            skipped_count += 1
            assert normalized.warning is not None
            warnings.append(normalized.warning)
            continue
        try:
            repository.persist(normalized.game)
        except KeyboardInterrupt:
            raise
        except GamePersistenceError as error:
            return ImportResult(
                imported_count=imported_count,
                skipped_count=skipped_count,
                warnings=tuple(warnings),
                failure=ImportFailure(
                    game_uuid=str(normalized.game.chesscom_game_uuid),
                    message=str(error),
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
) -> ImportResult:
    """Read only DB-03 month files in deterministic order and import their games."""

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
    repository.validate()
    return import_raw_games(raw_games, trainer_uuid, repository)


def _metadata_parameters(
    game: NormalizedGame, *, game_id: int | None = None
) -> dict[str, Any]:
    return {
        "game_id": game_id,
        "game_uuid": str(game.chesscom_game_uuid),
        "source_url": game.source_url,
        "original_pgn": game.original_pgn,
        "trainer_color": game.trainer_color,
        "trainer_uuid": str(game.trainer_chesscom_uuid),
        "opponent_uuid": (
            str(game.opponent_chesscom_uuid)
            if game.opponent_chesscom_uuid is not None
            else None
        ),
        "trainer_rating": game.trainer_rating,
        "opponent_rating": game.opponent_rating,
        "started_at": game.started_at_utc,
        "ended_at": game.ended_at_utc,
        "outcome": game.trainer_outcome,
        "termination": game.termination_reason,
        "time_control": game.time_control_source,
        "time_class": game.time_class,
    }


_GAME_COLUMNS = """
    dg_chesscom_game_uuid,
    dg_source_url,
    dg_original_pgn,
    dg_trainer_color,
    dg_trainer_chesscom_uuid,
    dg_opponent_chesscom_uuid,
    dg_trainer_rating,
    dg_opponent_rating,
    dg_started_at_utc,
    dg_ended_at_utc,
    dg_trainer_outcome,
    dg_termination_reason,
    dg_time_control_source,
    dg_time_class
"""
_GAME_VALUES = """
    :game_uuid,
    :source_url,
    :original_pgn,
    :trainer_color,
    :trainer_uuid,
    :opponent_uuid,
    :trainer_rating,
    :opponent_rating,
    :started_at,
    :ended_at,
    :outcome,
    :termination,
    :time_control,
    :time_class
"""
_INSERT_GAME_SQL = f"INSERT INTO datasource_game ({_GAME_COLUMNS}) VALUES ({_GAME_VALUES})"
_UPDATE_GAME_SQL = """
    UPDATE datasource_game SET
        dg_chesscom_game_uuid = :game_uuid,
        dg_source_url = :source_url,
        dg_original_pgn = :original_pgn,
        dg_trainer_color = :trainer_color,
        dg_trainer_chesscom_uuid = :trainer_uuid,
        dg_opponent_chesscom_uuid = :opponent_uuid,
        dg_trainer_rating = :trainer_rating,
        dg_opponent_rating = :opponent_rating,
        dg_started_at_utc = :started_at,
        dg_ended_at_utc = :ended_at,
        dg_trainer_outcome = :outcome,
        dg_termination_reason = :termination,
        dg_time_control_source = :time_control,
        dg_time_class = :time_class
    WHERE dg_game_id = :game_id
"""
_INSERT_OCCURRENCE_SQL = """
    INSERT INTO derived_game_position (
        datasource_game_id,
        dgp_ply,
        derived_position_id,
        dgp_move_uci,
        dgp_halfmove_clock,
        dgp_fullmove_number
    ) VALUES (
        :game_id,
        :ply,
        :position_id,
        :move_uci,
        :halfmove_clock,
        :fullmove_number
    )
"""
