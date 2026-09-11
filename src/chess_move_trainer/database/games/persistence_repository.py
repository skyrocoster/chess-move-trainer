"""Per-game repository and persistence models."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions.repository import PositionIdentity, _PositionUnitOfWork, _position_identity
from ..schema import _assert_compatible_schema
from .normalization import (
    NormalizationResult,
    NormalizationWarning,
    NormalizedGame,
    normalize_game,
)
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


class _BulkImportAbort(Exception):
    """Carry one ordinary import failure out of the bulk transaction."""

    def __init__(self, result: ImportResult) -> None:
        super().__init__(result.failure.message if result.failure is not None else "bulk import failed")
        self.result = result


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
        self._last_import_writes = 0

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
                return self._persist_on_connection(connection, game)
        except KeyboardInterrupt:
            raise
        except Exception as error:
            raise GamePersistenceError(f"game could not be persisted: {error}") from error

    @contextmanager
    def _validated_connection(self) -> Iterator[object]:
        """Open one validated connection for an independent import run."""

        with _open_existing_connection(
            self._database_path, self._lock_timeout
        ) as connection:
            _assert_compatible_schema(connection, self._lock_timeout)
            yield connection

    def _persist_on_connection(
        self,
        connection: object,
        game: NormalizedGame,
        *,
        position_cache: dict[PositionIdentity, int] | None = None,
    ) -> PersistedGame:
        """Persist one game in its own transaction on an already validated connection."""

        if not isinstance(game, NormalizedGame):
            raise TypeError("game must be a fully normalized game")
        with connection.begin():
            return self._persist_in_transaction(
                connection,
                game,
                position_cache=position_cache,
            )

    def _persist_in_transaction(
        self,
        connection: object,
        game: NormalizedGame,
        *,
        position_cache: dict[PositionIdentity, int] | None = None,
    ) -> PersistedGame:
        """Persist one game while the caller owns the active transaction."""

        if not isinstance(game, NormalizedGame):
            raise TypeError("game must be a fully normalized game")
        existing = connection.execute(
            text(
                """
                SELECT dg_game_id, dg_source_url, dg_original_pgn,
                       dg_trainer_color, dg_trainer_chesscom_uuid,
                       dg_opponent_chesscom_uuid, dg_trainer_rating,
                       dg_opponent_rating, dg_started_at_utc, dg_ended_at_utc,
                       dg_trainer_outcome, dg_termination_reason,
                       dg_time_control_source, dg_time_class
                FROM datasource_game
                WHERE dg_chesscom_game_uuid = :game_uuid
                """
            ),
            {"game_uuid": str(game.chesscom_game_uuid)},
        ).first()

        if existing is not None:
            game_id = int(existing[0])
            if _stored_game_matches(connection, game, existing):
                return PersistedGame(
                    game_id=game_id,
                    corrected=False,
                    occurrence_count=len(game.occurrences),
                )
        else:
            game_id = None

        corrected = existing is not None
        if corrected:
            assert game_id is not None
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

        run_position_cache = position_cache if position_cache is not None else {}
        position_work = _PositionUnitOfWork(
            connection,
            position_cache=run_position_cache,
        )
        position_ids_by_identity: dict[PositionIdentity, int] = {}
        for occurrence in game.occurrences:
            identity = _position_identity(occurrence.position)
            if identity not in position_ids_by_identity:
                position_ids_by_identity[identity] = position_work._resolve(
                    occurrence.position
                )
            self._checkpoint("position")

        if corrected:
            connection.execute(
                text(
                    "DELETE FROM derived_game_position "
                    "WHERE datasource_game_id = :game_id"
                ),
                {"game_id": game_id},
            )
        occurrence_parameters = [
            {
                "game_id": game_id,
                "ply": occurrence.ply,
                "position_id": position_ids_by_identity[
                    _position_identity(occurrence.position)
                ],
                "move_uci": occurrence.move_uci,
                "halfmove_clock": occurrence.halfmove_clock,
                "fullmove_number": occurrence.fullmove_number,
            }
            for occurrence in game.occurrences
        ]
        connection.execute(text(_INSERT_OCCURRENCE_SQL), occurrence_parameters)
        for _ in occurrence_parameters:
            self._checkpoint("occurrence")

        if position_cache is not None:
            position_cache.update(position_work._new_positions)
        self._last_import_writes += 1
        return PersistedGame(
            game_id=game_id,
            corrected=corrected,
            occurrence_count=len(game.occurrences),
        )




def _stored_game_matches(
    connection: object,
    game: NormalizedGame,
    existing: object,
) -> bool:
    """Compare all persisted metadata and ordered occurrence facts for one game."""

    if tuple(existing[1:]) != _game_metadata(game):
        return False
    stored_occurrences = tuple(
        tuple(occurrence)
        for occurrence in connection.execute(
            text(
                """
                SELECT g.dgp_ply, p.dp_placement, p.dp_side_to_move,
                       p.dp_castling_rights, p.dp_legal_en_passant,
                       g.dgp_move_uci, g.dgp_halfmove_clock,
                       g.dgp_fullmove_number
                FROM derived_game_position AS g
                JOIN derived_position AS p
                  ON p.dp_position_id = g.derived_position_id
                WHERE g.datasource_game_id = :game_id
                ORDER BY g.dgp_ply
                """
            ),
            {"game_id": int(existing[0])},
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
    return stored_occurrences == expected_occurrences


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
