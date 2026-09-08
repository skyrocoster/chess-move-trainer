"""Read-only reconstruction of normalized games and their occurrences."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..positions import CanonicalPosition
from ..schema import SchemaIncompatibleError, _assert_compatible_schema


TrainerColor = Literal["white", "black"]


class GameReadError(RuntimeError):
    """Raised when a compatible game database cannot be reconstructed safely."""


@dataclass(frozen=True, slots=True)
class GameOccurrenceRead:
    """One ordered occurrence, including the move leaving that position."""

    ply: int
    position_id: int
    position: CanonicalPosition
    move_uci: str | None
    halfmove_clock: int
    fullmove_number: int

    @property
    def derived_position_id(self) -> int:
        """Return the catalogue name for the canonical position identity."""

        return self.position_id


@dataclass(frozen=True, slots=True)
class GameRead:
    """Game metadata followed by all occurrences in ascending ply order."""

    game_id: int
    chesscom_game_uuid: str
    source_url: str
    original_pgn: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: str
    opponent_chesscom_uuid: str | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: Literal["win", "loss", "draw"] | None
    termination_reason: str | None
    time_control_source: str | None
    time_class: str | None
    occurrences: tuple[GameOccurrenceRead, ...]

    @property
    def metadata(self) -> GameRead:
        """Return the metadata-bearing read value without another database query."""

        return self


class GameReadRepository:
    """Reconstruct one normalized game through an owned read-only connection."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout

    def read(
        self,
        game_id: int | None = None,
        *,
        chesscom_game_uuid: str | None = None,
    ) -> GameRead | None:
        """Return one game by internal id or Chess.com UUID, or ``None`` when absent."""

        selector_count = (game_id is not None) + (chesscom_game_uuid is not None)
        if selector_count != 1:
            raise GameReadError("exactly one game id or Chess.com UUID is required")
        if game_id is not None and (type(game_id) is not int or game_id < 1):
            raise GameReadError("game_id must be a positive integer")
        if chesscom_game_uuid is not None and (
            not isinstance(chesscom_game_uuid, str) or not chesscom_game_uuid
        ):
            raise GameReadError("chesscom_game_uuid must be a non-empty string")

        if game_id is not None:
            where = "g.dg_game_id = :game_id"
            parameters = {"game_id": game_id}
        else:
            where = "g.dg_chesscom_game_uuid = :game_uuid"
            parameters = {"game_uuid": chesscom_game_uuid}

        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                rows = connection.execute(
                    text(
                        f"""
                        SELECT
                            g.dg_game_id,
                            g.dg_chesscom_game_uuid,
                            g.dg_source_url,
                            g.dg_original_pgn,
                            g.dg_trainer_color,
                            g.dg_trainer_chesscom_uuid,
                            g.dg_opponent_chesscom_uuid,
                            g.dg_trainer_rating,
                            g.dg_opponent_rating,
                            g.dg_started_at_utc,
                            g.dg_ended_at_utc,
                            g.dg_trainer_outcome,
                            g.dg_termination_reason,
                            g.dg_time_control_source,
                            g.dg_time_class,
                            o.dgp_ply,
                            o.derived_position_id,
                            o.dgp_move_uci,
                            o.dgp_halfmove_clock,
                            o.dgp_fullmove_number,
                            p.dp_placement,
                            p.dp_side_to_move,
                            p.dp_castling_rights,
                            p.dp_legal_en_passant
                        FROM datasource_game AS g
                        LEFT JOIN derived_game_position AS o
                          ON o.datasource_game_id = g.dg_game_id
                        LEFT JOIN derived_position AS p
                          ON p.dp_position_id = o.derived_position_id
                        WHERE {where}
                        ORDER BY o.dgp_ply
                        """
                    ),
                    parameters,
                ).all()
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise GameReadError("game could not be read") from error

        if not rows:
            return None
        return _materialize_game(rows)

    def read_by_id(self, game_id: int) -> GameRead | None:
        """Return one game by its package-owned integer identity."""

        return self.read(game_id)

    def read_by_uuid(self, chesscom_game_uuid: str) -> GameRead | None:
        """Return one game by its retained Chess.com UUID."""

        return self.read(chesscom_game_uuid=chesscom_game_uuid)

    get = read


def _materialize_game(rows: list[object]) -> GameRead:
    first = rows[0]
    try:
        trainer_color = first[4]
        if trainer_color not in ("white", "black"):
            raise ValueError("invalid trainer color")
        occurrences = tuple(_occurrence_from_row(row) for row in rows if row[15] is not None)
        return GameRead(
            game_id=int(first[0]),
            chesscom_game_uuid=_required_text(first[1], "game UUID"),
            source_url=_required_text(first[2], "source URL"),
            original_pgn=_required_text(first[3], "source PGN"),
            trainer_color=trainer_color,
            trainer_chesscom_uuid=_required_text(first[5], "trainer UUID"),
            opponent_chesscom_uuid=_optional_text(first[6]),
            trainer_rating=_optional_int(first[7]),
            opponent_rating=_optional_int(first[8]),
            started_at_utc=_optional_text(first[9]),
            ended_at_utc=_optional_text(first[10]),
            trainer_outcome=_trainer_outcome(first[11]),
            termination_reason=_optional_text(first[12]),
            time_control_source=_optional_text(first[13]),
            time_class=_optional_text(first[14]),
            occurrences=occurrences,
        )
    except (IndexError, TypeError, ValueError) as error:
        raise GameReadError("game row is malformed") from error


def _occurrence_from_row(row: object) -> GameOccurrenceRead:
    try:
        position = CanonicalPosition(
            placement=_required_text(row[20], "position placement"),
            side_to_move=_required_text(row[21], "position side"),
            castling_rights=_required_text(row[22], "position castling"),
            legal_en_passant=_required_text(row[23], "position en-passant"),
        )
        return GameOccurrenceRead(
            ply=int(row[15]),
            position_id=int(row[16]),
            position=position,
            move_uci=_optional_text(row[17]),
            halfmove_clock=int(row[18]),
            fullmove_number=int(row[19]),
        )
    except (IndexError, TypeError, ValueError) as error:
        raise GameReadError("game occurrence row is malformed") from error


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional text value is malformed")
    return value


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if type(value) is not int:
        raise ValueError("optional integer value is malformed")
    return value


def _trainer_outcome(value: object) -> Literal["win", "loss", "draw"] | None:
    if value is None:
        return None
    if value not in ("win", "loss", "draw"):
        raise ValueError("invalid trainer outcome")
    return value


__all__ = [
    "GameOccurrenceRead",
    "GameRead",
    "GameReadError",
    "GameReadRepository",
]
