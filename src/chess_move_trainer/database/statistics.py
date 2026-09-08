"""Direct, read-only statistics over normalized game occurrences."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sqlalchemy import text

from .connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from .schema import SchemaIncompatibleError, _assert_compatible_schema


TrainerColor = Literal["white", "black"]


class StatisticsReadError(RuntimeError):
    """Raised when direct statistics cannot be read safely."""


@dataclass(frozen=True, slots=True)
class PositionContext:
    """Distinct-game context for one canonical position."""

    position_id: int
    trainer_color: TrainerColor | None
    distinct_game_count: int

    @property
    def game_count(self) -> int:
        """Return the distinct game count under the selected color filter."""

        return self.distinct_game_count


@dataclass(frozen=True, slots=True)
class MoveResponseDistribution:
    """Occurrence and outgoing-move counts with actor derived at read time."""

    position_id: int
    trainer_color: TrainerColor | None
    occurrence_count: int
    final_occurrence_count: int
    outgoing_moves: dict[str, int]
    my_choices: dict[str, int]
    opponent_responses: dict[str, int]

    @property
    def played_occurrence_count(self) -> int:
        """Return occurrences that have an outgoing move."""

        return self.occurrence_count - self.final_occurrence_count

    @property
    def final_count(self) -> int:
        """Return the separately reported final-occurrence count."""

        return self.final_occurrence_count


class PositionContextReader:
    """Count distinct games directly from game occurrences."""

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
        position_id: int,
        trainer_color: TrainerColor | None = None,
    ) -> PositionContext:
        _validate_position_id(position_id)
        _validate_trainer_color(trainer_color)
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                count = connection.execute(
                    text(
                        """
                        SELECT COUNT(DISTINCT o.datasource_game_id)
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        WHERE o.derived_position_id = :position_id
                          AND (
                              :trainer_color IS NULL
                              OR g.dg_trainer_color = :trainer_color
                          )
                        """
                    ),
                    {"position_id": position_id, "trainer_color": trainer_color},
                ).scalar_one()
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise StatisticsReadError("position context could not be read") from error
        return PositionContext(
            position_id=position_id,
            trainer_color=trainer_color,
            distinct_game_count=int(count),
        )

    count = read


class MoveResponseDistributionReader:
    """Count outgoing moves and derive trainer/opponent actors from stored facts."""

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
        position_id: int,
        trainer_color: TrainerColor | None = None,
    ) -> MoveResponseDistribution:
        _validate_position_id(position_id)
        _validate_trainer_color(trainer_color)
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                rows = connection.execute(
                    text(
                        """
                        SELECT o.dgp_move_uci, p.dp_side_to_move, g.dg_trainer_color
                        FROM derived_game_position AS o
                        JOIN datasource_game AS g
                          ON g.dg_game_id = o.datasource_game_id
                        JOIN derived_position AS p
                          ON p.dp_position_id = o.derived_position_id
                        WHERE o.derived_position_id = :position_id
                          AND (
                              :trainer_color IS NULL
                              OR g.dg_trainer_color = :trainer_color
                          )
                        ORDER BY o.datasource_game_id, o.dgp_ply
                        """
                    ),
                    {"position_id": position_id, "trainer_color": trainer_color},
                ).all()
        except SchemaIncompatibleError:
            raise
        except Exception as error:
            raise StatisticsReadError("move response distribution could not be read") from error

        outgoing_moves: dict[str, int] = {}
        my_choices: dict[str, int] = {}
        opponent_responses: dict[str, int] = {}
        final_occurrences = 0
        for row in rows:
            try:
                move_uci = row[0]
                side_to_move = row[1]
                game_trainer_color = row[2]
            except IndexError as error:
                raise StatisticsReadError("move response row is malformed") from error
            if move_uci is None:
                final_occurrences += 1
                continue
            if not isinstance(move_uci, str) or side_to_move not in ("w", "b"):
                raise StatisticsReadError("move response row is malformed")
            if game_trainer_color not in ("white", "black"):
                raise StatisticsReadError("move response row has an invalid trainer color")
            outgoing_moves[move_uci] = outgoing_moves.get(move_uci, 0) + 1
            trainer_side = "w" if game_trainer_color == "white" else "b"
            actor_counts = my_choices if side_to_move == trainer_side else opponent_responses
            actor_counts[move_uci] = actor_counts.get(move_uci, 0) + 1

        return MoveResponseDistribution(
            position_id=position_id,
            trainer_color=trainer_color,
            occurrence_count=len(rows),
            final_occurrence_count=final_occurrences,
            outgoing_moves=outgoing_moves,
            my_choices=my_choices,
            opponent_responses=opponent_responses,
        )


def _validate_position_id(position_id: object) -> None:
    if type(position_id) is not int or position_id < 1:
        raise StatisticsReadError("position_id must be a positive integer")


def _validate_trainer_color(trainer_color: object) -> None:
    if trainer_color not in (None, "white", "black"):
        raise StatisticsReadError("trainer_color must be white, black, or omitted")


__all__ = [
    "MoveResponseDistribution",
    "MoveResponseDistributionReader",
    "PositionContext",
    "PositionContextReader",
    "StatisticsReadError",
]
