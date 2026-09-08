"""Database-bound preferred-move setup over the rebuilt schema."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions import (
    CanonicalPosition,
    PositionValidationError,
    canonicalize_fen,
)
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .inference import (
    PreferredMoveInferenceResult,
    PreferredMoveObservation,
    infer_preferred_moves,
)
from .ranges import (
    NormalizedPeriod,
    PreferenceState,
    RangeValidationError,
    normalize_periods,
)
from .repository import (
    PreferredMoveError,
    PreferredMoveSchemaError,
    PreferredMoveStorageError,
    _translate_storage_error,
)


class PreferredMoveSetupError(PreferredMoveError, RuntimeError):
    """Raised when setup cannot safely complete."""


class PreferredMoveSetupValidationError(PreferredMoveSetupError, ValueError):
    """Raised when normalized setup input or its complete result is invalid."""


class PreferredMoveSetupRefused(PreferredMoveSetupError):
    """Raised when the current preferred-move schedule is not empty."""


@dataclass(frozen=True, slots=True)
class PreferredMoveSetupResult:
    """The fixed summary units produced by one setup operation."""

    examined_games: int
    skipped_games: int
    qualifying_positions: int
    periods_applied: int
    conflicting_positions: int

    def __post_init__(self) -> None:
        for name, value in (
            ("examined_games", self.examined_games),
            ("skipped_games", self.skipped_games),
            ("qualifying_positions", self.qualifying_positions),
            ("periods_applied", self.periods_applied),
            ("conflicting_positions", self.conflicting_positions),
        ):
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")


@dataclass(frozen=True, slots=True)
class _ReadData:
    observations: tuple[PreferredMoveObservation, ...]
    position_ids: dict[CanonicalPosition, int]
    examined_games: int
    skipped_games: int


class PreferredMoveSetupService:
    """Infer and atomically initialize an empty preferred-move schedule."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        _checkpoint: Callable[[str], None] | None = None,
        _inference: Callable[
            [tuple[PreferredMoveObservation, ...]], PreferredMoveInferenceResult
        ] = infer_preferred_moves,
    ) -> None:
        self._database_path = database_path
        self._lock_timeout = lock_timeout
        self._checkpoint = _checkpoint if _checkpoint is not None else lambda _: None
        self._inference = _inference

    def run(self) -> PreferredMoveSetupResult:
        """Scan, validate, and publish one complete setup result or none."""

        try:
            with _open_existing_connection(
                self._database_path, self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                self._checkpoint("before_lock")
                connection.exec_driver_sql("BEGIN IMMEDIATE")
                transaction = connection.get_transaction()
                if transaction is None:
                    raise PreferredMoveSetupError(
                        "SQLite did not establish the setup transaction"
                    )
                try:
                    self._require_empty_schedule(connection)
                    read_data = _read_data(connection)
                    inference = self._inference(read_data.observations)
                    periods = _validate_complete_result(
                        inference, read_data.position_ids
                    )
                    self._insert_periods(connection, periods, read_data.position_ids)
                    result = PreferredMoveSetupResult(
                        examined_games=read_data.examined_games,
                        skipped_games=read_data.skipped_games,
                        qualifying_positions=len(periods),
                        periods_applied=sum(
                            len(position_periods) for position_periods in periods.values()
                        ),
                        conflicting_positions=len(inference.conflicting_positions),
                    )
                except BaseException:
                    transaction.rollback()
                    raise
                else:
                    transaction.commit()
                    return result
        except KeyboardInterrupt:
            raise
        except PreferredMoveError:
            raise
        except SchemaIncompatibleError as error:
            raise PreferredMoveSchemaError(str(error)) from error
        except (PositionValidationError, RangeValidationError, ValueError) as error:
            raise PreferredMoveSetupValidationError(str(error)) from error
        except Exception as error:
            translated = _translate_storage_error(error)
            raise PreferredMoveSetupError(str(translated)) from error

    def _require_empty_schedule(self, connection: object) -> None:
        row_count = connection.execute(
            text("SELECT COUNT(*) FROM datasource_preferred_move_period")
        ).scalar_one()
        if int(row_count) != 0:
            raise PreferredMoveSetupRefused(
                "preferred-move setup requires an empty schedule"
            )

    def _insert_periods(
        self,
        connection: object,
        periods: dict[CanonicalPosition, tuple[NormalizedPeriod, ...]],
        position_ids: dict[CanonicalPosition, int],
    ) -> None:
        for position in sorted(periods, key=_position_sort_key):
            position_id = position_ids[position]
            for period in periods[position]:
                connection.execute(
                    text(
                        """
                        INSERT INTO datasource_preferred_move_period (
                            derived_position_id,
                            dpm_effective_from,
                            dpm_effective_until,
                            dpm_move_uci
                        ) VALUES (
                            :position_id,
                            :effective_from,
                            :effective_until,
                            :move
                        )
                        """
                    ),
                    {
                        "position_id": position_id,
                        "effective_from": period.effective_from.isoformat(),
                        "effective_until": (
                            None
                            if period.effective_until is None
                            else period.effective_until.isoformat()
                        ),
                        "move": period.preference.move,
                    },
                )
                self._checkpoint("inserted")


def setup_preferred_moves(
    database_path: str | Path,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> PreferredMoveSetupResult:
    """Run preferred-move setup through the package-owned service boundary."""

    return PreferredMoveSetupService(
        database_path, lock_timeout=lock_timeout
    ).run()


def _read_data(connection: object) -> _ReadData:
    rows = connection.execute(
        text(
            """
            SELECT
                g.dg_game_id,
                g.dg_started_at_utc,
                g.dg_trainer_color,
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
            ORDER BY g.dg_game_id, o.dgp_ply
            """
        )
    ).all()

    examined_game_ids: set[int] = set()
    skipped_game_ids: set[int] = set()
    game_dates: dict[int, date] = {}
    game_colors: dict[int, str] = {}
    observations: list[PreferredMoveObservation] = []
    position_ids: dict[CanonicalPosition, int] = {}
    position_by_id: dict[int, CanonicalPosition] = {}

    for row in rows:
        game_id, started_at, trainer_color = _game_header(row)
        if game_id not in examined_game_ids:
            examined_game_ids.add(game_id)
            if trainer_color not in ("white", "black"):
                raise PreferredMoveSetupValidationError(
                    "stored game has an invalid trainer color"
                )
            game_colors[game_id] = trainer_color
            if started_at is None:
                skipped_game_ids.add(game_id)
            else:
                game_dates[game_id] = _parse_started_at_utc(started_at)
        elif game_colors[game_id] != trainer_color:
            raise PreferredMoveSetupValidationError(
                "stored game metadata changed within its occurrence rows"
            )

        if game_id in skipped_game_ids:
            continue
        if row[3] is None:
            continue

        occurrence = _occurrence_from_row(row)
        position = occurrence["position"]
        position_id = occurrence["position_id"]
        prior_position = position_by_id.setdefault(position_id, position)
        if prior_position != position:
            raise PreferredMoveSetupValidationError(
                "stored position identity is inconsistent"
            )
        prior_id = position_ids.setdefault(position, position_id)
        if prior_id != position_id:
            raise PreferredMoveSetupValidationError(
                "stored canonical position has multiple identities"
            )

        move_uci = occurrence["move_uci"]
        if (
            0 <= occurrence["ply"] <= 29
            and move_uci is not None
            and position.side_to_move
            == ("w" if game_colors[game_id] == "white" else "b")
        ):
            observations.append(
                PreferredMoveObservation(position, game_dates[game_id], move_uci)
            )

    return _ReadData(
        observations=tuple(observations),
        position_ids=position_ids,
        examined_games=len(examined_game_ids),
        skipped_games=len(skipped_game_ids),
    )


def _game_header(row: object) -> tuple[int, object, object]:
    try:
        game_id = row[0]
        started_at = row[1]
        trainer_color = row[2]
    except (IndexError, TypeError) as error:
        raise PreferredMoveSetupValidationError("stored game row is malformed") from error
    if type(game_id) is not int or game_id < 1:
        raise PreferredMoveSetupValidationError("stored game has an invalid identity")
    return game_id, started_at, trainer_color


def _occurrence_from_row(row: object) -> dict[str, object]:
    try:
        ply = row[3]
        position_id = row[4]
        move_uci = row[5]
        halfmove_clock = row[6]
        fullmove_number = row[7]
        position = CanonicalPosition(
            placement=row[8],
            side_to_move=row[9],
            castling_rights=row[10],
            legal_en_passant=row[11],
        )
    except (IndexError, TypeError) as error:
        raise PreferredMoveSetupValidationError(
            "stored occurrence row is malformed"
        ) from error
    if type(ply) is not int or ply < 0:
        raise PreferredMoveSetupValidationError("stored occurrence has an invalid ply")
    if type(position_id) is not int or position_id < 1:
        raise PreferredMoveSetupValidationError(
            "stored occurrence has an invalid position identity"
        )
    if type(halfmove_clock) is not int or halfmove_clock < 0:
        raise PreferredMoveSetupValidationError(
            "stored occurrence has an invalid halfmove clock"
        )
    if type(fullmove_number) is not int or fullmove_number < 1:
        raise PreferredMoveSetupValidationError(
            "stored occurrence has an invalid fullmove number"
        )
    if move_uci is not None:
        if not isinstance(move_uci, str) or not move_uci:
            raise PreferredMoveSetupValidationError(
                "stored occurrence has an invalid move"
            )
        try:
            chess.Move.from_uci(move_uci)
        except ValueError as error:
            raise PreferredMoveSetupValidationError(
                "stored occurrence has an invalid move"
            ) from error
    _validate_canonical_position(position)
    return {
        "ply": ply,
        "position_id": position_id,
        "move_uci": move_uci,
        "position": position,
    }


def _parse_started_at_utc(value: object) -> date:
    if not isinstance(value, str) or not value:
        raise PreferredMoveSetupValidationError(
            "non-null game start timestamp is malformed"
        )
    literal = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(literal)
    except ValueError as error:
        raise PreferredMoveSetupValidationError(
            "non-null game start timestamp is malformed"
        ) from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PreferredMoveSetupValidationError(
            "non-null game start timestamp must include UTC offset"
        )
    return parsed.astimezone(UTC).date()


def _validate_canonical_position(position: CanonicalPosition) -> None:
    fields = (
        position.placement,
        position.side_to_move,
        position.castling_rights,
        position.legal_en_passant,
    )
    if any(not isinstance(field, str) or not field for field in fields):
        raise PreferredMoveSetupValidationError("stored canonical position is malformed")
    try:
        canonical = canonicalize_fen(" ".join((*fields, "0", "1")))
    except PositionValidationError as error:
        raise PreferredMoveSetupValidationError(
            "stored canonical position is invalid"
        ) from error
    if canonical != position:
        raise PreferredMoveSetupValidationError(
            "stored canonical position is not canonical"
        )


def _validate_complete_result(
    inference: PreferredMoveInferenceResult,
    position_ids: dict[CanonicalPosition, int],
) -> dict[CanonicalPosition, tuple[NormalizedPeriod, ...]]:
    if not isinstance(inference, PreferredMoveInferenceResult):
        raise PreferredMoveSetupValidationError("inference result is malformed")

    periods_by_position: dict[CanonicalPosition, tuple[NormalizedPeriod, ...]] = {}
    for summary in inference.summaries:
        if summary.position not in position_ids:
            raise PreferredMoveSetupValidationError(
                "inference result contains an unread position"
            )
        _validate_canonical_position(summary.position)
        try:
            periods = normalize_periods(summary.periods)
        except RangeValidationError as error:
            raise PreferredMoveSetupValidationError(
                "inference result schedule is not normalized"
            ) from error
        if periods != summary.periods or not periods:
            raise PreferredMoveSetupValidationError(
                "inference result schedule is not complete"
            )
        if periods[-1].effective_until is not None:
            raise PreferredMoveSetupValidationError(
                "inference result final period must be open-ended"
            )
        for index, period in enumerate(periods):
            if period.preference.state is not PreferenceState.PREFERRED_MOVE:
                raise PreferredMoveSetupValidationError(
                    "inference result cannot contain no-preference periods"
                )
            if index and periods[index - 1].effective_until != period.effective_from:
                raise PreferredMoveSetupValidationError(
                    "inference result periods must be contiguous"
                )
            _validate_legal_move(summary.position, period)
        periods_by_position[summary.position] = periods
    return periods_by_position


def _validate_legal_move(position: CanonicalPosition, period: NormalizedPeriod) -> None:
    fen = " ".join(
        (
            position.placement,
            position.side_to_move,
            position.castling_rights,
            position.legal_en_passant,
            "0",
            "1",
        )
    )
    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(period.preference.move or "")
    except ValueError as error:
        raise PreferredMoveSetupValidationError(
            "inference result move is not valid UCI"
        ) from error
    if move not in board.legal_moves:
        raise PreferredMoveSetupValidationError(
            "inference result move is not legal from its position"
        )


def _position_sort_key(position: CanonicalPosition) -> tuple[str, str, str, str]:
    return (
        position.placement,
        position.side_to_move,
        position.castling_rights,
        position.legal_en_passant,
    )


__all__ = [
    "PreferredMoveSetupError",
    "PreferredMoveSetupRefused",
    "PreferredMoveSetupResult",
    "PreferredMoveSetupService",
    "PreferredMoveSetupValidationError",
    "setup_preferred_moves",
]
