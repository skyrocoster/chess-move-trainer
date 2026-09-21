"""Atomic server-judged training-answer submission."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .canonicalization import CanonicalPosition, PositionValidationError, canonicalize_fen
from .repository import _find_existing_position_id
from .training_answer_support import (
    UtcCalendarDateClock,
    _clock_date,
    _is_lock_failure,
    _utc_today,
)
from .training_requirements_models import (
    TrainerColor,
    TrainingRequirementError,
    TrainingRequirementItem,
    TrainingRequirementPolicy,
    TrainingRequirementSchemaError,
    TrainingRequirementStaleError,
    TrainingRequirementStorageError,
    TrainingRequirementValidationError,
    parse_calendar_date,
    validate_uci,
)
from .training_requirements_repository import (
    _active_preference,
    _load_occurrences,
    _load_preferences,
    _usable_game_date,
)
from .training_requirements_scoring import (
    effective_training_balance,
    score_training_pair,
    training_adjustment,
)


class TrainingAnswerValidationError(TrainingRequirementValidationError):
    """Raised when an answer request is invalid."""


class TrainingAnswerNotFoundError(TrainingRequirementError, LookupError):
    """Raised when the requested current training pair does not exist."""


class TrainingAnswerStaleError(TrainingRequirementStaleError):
    """Raised when the requested answer date predates persisted credit."""


class TrainingAnswerLockError(TrainingRequirementStorageError):
    """Raised when SQLite cannot acquire the bounded writer lock."""


@dataclass(frozen=True, slots=True)
class TrainingAnswerRequest:
    """A complete, legal move answer for one canonical training position."""

    fen: str
    trainer_color: TrainerColor
    as_of: str
    played_move_uci: str

    def __post_init__(self) -> None:
        try:
            position = canonicalize_fen(self.fen)
        except (PositionValidationError, TypeError, ValueError) as error:
            raise TrainingAnswerValidationError("fen must be a complete legal FEN") from error

        if self.trainer_color not in ("white", "black"):
            raise TrainingAnswerValidationError("trainer_color must be 'white' or 'black'")
        expected_color = "white" if position.side_to_move == "w" else "black"
        if self.trainer_color != expected_color:
            raise TrainingAnswerValidationError(
                "trainer_color must agree with the FEN side to move"
            )

        try:
            parsed_as_of = parse_calendar_date(self.as_of, "as_of")
        except TrainingRequirementValidationError as error:
            raise TrainingAnswerValidationError(str(error)) from error

        board = chess.Board(_canonical_fen(position))
        if not isinstance(self.played_move_uci, str):
            raise TrainingAnswerValidationError("played_move_uci is malformed")
        try:
            move = chess.Move.from_uci(self.played_move_uci)
        except (TypeError, ValueError) as error:
            raise TrainingAnswerValidationError("played_move_uci is malformed") from error
        if move.uci() != self.played_move_uci:
            raise TrainingAnswerValidationError("played_move_uci must be canonical UCI")
        if not board.is_legal(move):
            raise TrainingAnswerValidationError("played_move_uci must be legal from fen")

        object.__setattr__(self, "fen", _canonical_fen(position))
        object.__setattr__(self, "as_of", parsed_as_of.isoformat())


@dataclass(frozen=True, slots=True)
class TrainingAnswerResult:
    """The server judgment and the newly scored training item."""

    as_of: str
    correct: bool
    item: TrainingRequirementItem

    @property
    def scored_item(self) -> TrainingRequirementItem:
        """Return the resulting scored item using an explicit adapter-friendly name."""

        return self.item

    def public_dict(self) -> dict[str, object]:
        return {
            "as_of": self.as_of,
            "correct": self.correct,
            "item": self.item.public_dict(),
        }


class TrainingAnswerRepository:
    """Judge and persist one answer in an existing compatible database."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        clock: UtcCalendarDateClock | None = None,
        today: UtcCalendarDateClock | None = None,
    ) -> None:
        if clock is not None and today is not None:
            raise TrainingAnswerValidationError("clock and today cannot both be supplied")
        self._database_path = database_path
        self._lock_timeout = lock_timeout
        self._clock = clock or today or _utc_today

    def submit(
        self,
        request: TrainingAnswerRequest,
        policy: TrainingRequirementPolicy,
    ) -> TrainingAnswerResult:
        """Judge one answer and atomically update its aggregate credit."""

        if not isinstance(request, TrainingAnswerRequest):
            raise TrainingAnswerValidationError("request must be a TrainingAnswerRequest value")
        if not isinstance(policy, TrainingRequirementPolicy):
            raise TrainingAnswerValidationError("policy must be a TrainingRequirementPolicy")

        answer_date = parse_calendar_date(request.as_of, "as_of")
        today = _clock_date(self._clock)
        if answer_date > today:
            raise TrainingAnswerValidationError(
                "as_of cannot be later than the current UTC calendar date"
            )

        try:
            with _open_existing_connection(
                self._database_path,
                self._lock_timeout,
            ) as connection:
                try:
                    _assert_compatible_schema(connection, self._lock_timeout)
                    connection.rollback()
                    connection.exec_driver_sql("BEGIN IMMEDIATE")
                    result = self._submit_connection(
                        connection,
                        request,
                        answer_date,
                        policy,
                    )
                    connection.commit()
                    return result
                except BaseException:
                    if connection.in_transaction():
                        connection.rollback()
                    raise
        except SchemaIncompatibleError as error:
            raise TrainingRequirementSchemaError(str(error)) from error
        except TrainingRequirementValidationError:
            raise
        except (TrainingRequirementStaleError, TrainingAnswerNotFoundError):
            raise
        except Exception as error:
            if _is_lock_failure(error):
                raise TrainingAnswerLockError(
                    "training answer could not acquire the database writer lock"
                ) from error
            raise TrainingRequirementStorageError(
                "training answer could not be submitted"
            ) from error

    submit_answer = submit

    def _submit_connection(
        self,
        connection: object,
        request: TrainingAnswerRequest,
        answer_date: date,
        policy: TrainingRequirementPolicy,
    ) -> TrainingAnswerResult:
        position = canonicalize_fen(request.fen)
        position_id = _find_existing_position_id(connection, position)
        if position_id is None:
            raise TrainingAnswerNotFoundError("training position does not exist")

        preferences = _load_preferences(connection)
        periods = preferences.get(position_id, ())
        preferred_move_uci = _active_preference(periods, answer_date)
        if preferred_move_uci is None:
            raise TrainingAnswerNotFoundError("no preferred move is active for the requested date")
        validate_uci(preferred_move_uci, "stored preferred move")

        hits, misses = _eligible_evidence(
            connection,
            position_id,
            request.trainer_color,
            periods,
            preferred_move_uci,
        )
        if hits + misses == 0:
            raise TrainingAnswerNotFoundError(
                "current preferred-move pair has no eligible evidence"
            )

        stored_balance, stored_updated_on = _load_current_aggregate(
            connection,
            position_id,
            preferred_move_uci,
        )
        if stored_updated_on is not None:
            updated_date = parse_calendar_date(
                stored_updated_on,
                "training_updated_on",
            )
            if updated_date > answer_date:
                raise TrainingAnswerStaleError(
                    "training state is newer than the requested as_of date"
                )

        effective_balance = effective_training_balance(
            stored_balance,
            stored_updated_on,
            answer_date,
            policy,
        )
        correct = request.played_move_uci == preferred_move_uci
        resulting_balance = effective_balance + (1.0 if correct else -1.0)
        if not math.isfinite(resulting_balance):
            raise TrainingRequirementStorageError("resulting training balance is not finite")

        connection.execute(
            text(
                """
                INSERT INTO derived_position_training_aggregate (
                    derived_position_id,
                    dpta_preferred_move_uci,
                    dpta_training_balance,
                    dpta_updated_on
                ) VALUES (
                    :position_id,
                    :preferred_move_uci,
                    :training_balance,
                    :updated_on
                )
                ON CONFLICT (derived_position_id, dpta_preferred_move_uci)
                DO UPDATE SET
                    dpta_training_balance = excluded.dpta_training_balance,
                    dpta_updated_on = excluded.dpta_updated_on
                """
            ),
            {
                "position_id": position_id,
                "preferred_move_uci": preferred_move_uci,
                "training_balance": resulting_balance,
                "updated_on": answer_date.isoformat(),
            },
        )

        (
            game_value,
            scored_effective_balance,
            result_requirement,
            is_required,
            correct_answers_needed,
        ) = score_training_pair(
            hits,
            misses,
            resulting_balance,
            answer_date,
            answer_date,
            policy,
        )
        encounters = hits + misses
        item = TrainingRequirementItem(
            fen=_canonical_fen(position),
            trainer_color=request.trainer_color,
            preferred_move_uci=preferred_move_uci,
            encounters=encounters,
            hits=hits,
            misses=misses,
            observed_success_rate=hits / encounters,
            game_balance=game_value,
            effective_training_balance=scored_effective_balance,
            training_adjustment=training_adjustment(scored_effective_balance),
            training_updated_on=answer_date.isoformat(),
            training_requirement=result_requirement,
            training_required=is_required,
            correct_answers_needed=correct_answers_needed,
        )
        return TrainingAnswerResult(answer_date.isoformat(), correct, item)


def submit_training_answer(
    database_path: str | Path,
    request: TrainingAnswerRequest,
    policy: TrainingRequirementPolicy,
    *,
    lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    clock: UtcCalendarDateClock | None = None,
    today: UtcCalendarDateClock | None = None,
) -> TrainingAnswerResult:
    """Submit one validated answer against one explicit existing database."""

    return TrainingAnswerRepository(
        database_path,
        lock_timeout=lock_timeout,
        clock=clock,
        today=today,
    ).submit(request, policy)


answer_training_position = submit_training_answer


def _eligible_evidence(
    connection: object,
    position_id: int,
    trainer_color: TrainerColor,
    periods: tuple[object, ...],
    preferred_move_uci: str,
) -> tuple[int, int]:
    hits = 0
    misses = 0
    expected_side = "w" if trainer_color == "white" else "b"
    for row in _load_occurrences(connection, position_id=position_id):
        (
            occurrence_position_id,
            move_uci,
            _game_id,
            stored_trainer_color,
            started_at_utc,
            position,
        ) = row
        if occurrence_position_id != position_id:
            continue
        if position.side_to_move not in ("w", "b"):
            raise TrainingRequirementStorageError("stored position side is malformed")
        if stored_trainer_color not in ("white", "black"):
            raise TrainingRequirementStorageError("stored trainer color is malformed")
        if position.side_to_move != expected_side or stored_trainer_color != trainer_color:
            continue
        if move_uci is None:
            continue
        game_date = _usable_game_date(started_at_utc)
        if game_date is None:
            continue
        active_move = _active_preference(periods, game_date)
        if active_move is None:
            continue
        validate_uci(move_uci, "stored outgoing move")
        validate_uci(active_move, "stored preferred move")
        if active_move != preferred_move_uci:
            continue
        if move_uci == preferred_move_uci:
            hits += 1
        else:
            misses += 1
    return hits, misses


def _load_current_aggregate(
    connection: object,
    position_id: int,
    preferred_move_uci: str,
) -> tuple[float, str | None]:
    row = connection.execute(
        text(
            """
            SELECT dpta_training_balance, dpta_updated_on
            FROM derived_position_training_aggregate
            WHERE derived_position_id = :position_id
              AND dpta_preferred_move_uci = :preferred_move_uci
            """
        ),
        {
            "position_id": position_id,
            "preferred_move_uci": preferred_move_uci,
        },
    ).first()
    if row is None:
        return 0.0, None
    try:
        balance = float(row[0])
    except (TypeError, ValueError, OverflowError) as error:
        raise TrainingRequirementStorageError(
            "stored aggregate training balance is malformed"
        ) from error
    if not math.isfinite(balance):
        raise TrainingRequirementStorageError("stored aggregate training balance is not finite")
    updated_on = row[1]
    if updated_on is not None:
        try:
            updated_on = parse_calendar_date(
                updated_on,
                "stored aggregate update date",
            ).isoformat()
        except TrainingRequirementValidationError as error:
            raise TrainingRequirementStorageError(
                "stored aggregate update date is malformed"
            ) from error
    return balance, updated_on


def _canonical_fen(position: CanonicalPosition) -> str:
    return " ".join(
        (
            position.placement,
            position.side_to_move,
            position.castling_rights,
            position.legal_en_passant,
            "0",
            "1",
        )
    )


__all__ = [
    "TrainingAnswerLockError",
    "TrainingAnswerNotFoundError",
    "TrainingAnswerRepository",
    "TrainingAnswerRequest",
    "TrainingAnswerResult",
    "TrainingAnswerStaleError",
    "TrainingAnswerValidationError",
    "UtcCalendarDateClock",
    "answer_training_position",
    "submit_training_answer",
]
