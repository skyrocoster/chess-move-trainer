"""Atomic storage services for current preferred-move schedules."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path

import chess
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from ..connection import (
    DEFAULT_LOCK_TIMEOUT_SECONDS,
    _open_connection,
    _open_existing_connection,
)
from ..positions import CanonicalPosition, PositionValidationError, canonicalize_fen
from ..positions.repository import (
    PositionStorageError,
    _PositionUnitOfWork,
    _find_existing_position_id,
)
from ..schema import SchemaIncompatibleError, _assert_compatible_schema
from .ranges import (
    DateResolution,
    NormalizedPeriod,
    Preference,
    PreferenceState,
    RangeValidationError,
    normalize_periods,
    period_from_literals,
    resolve_date,
    set_preference,
    unset_preference,
)


class PreferredMoveError(Exception):
    """Base error for bounded preferred-move failures."""


class PreferredMoveValidationError(PreferredMoveError, ValueError):
    """Raised when preferred-move input is invalid."""


class PreferredMoveSchemaError(PreferredMoveError, RuntimeError):
    """Raised when the selected database is not exactly schema v1."""


class PreferredMoveStorageError(PreferredMoveError, RuntimeError):
    """Raised when preferred-move storage cannot be used safely."""


class PreferredMoveLockError(PreferredMoveStorageError):
    """Raised when the finite SQLite writer reservation cannot be acquired."""


class PreferredMoveRepository:
    """Read and amend preferred moves without exposing database handles."""

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

    def list_periods(self, fen: str) -> tuple[NormalizedPeriod, ...]:
        """Return the normalized schedule without creating a position."""

        position = _canonicalize_four_field_fen(fen)
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                position_id = _find_existing_position_id(connection, position)
                if position_id is None:
                    connection.rollback()
                    return ()
                schedule = _load_schedule(connection, position_id)
                connection.rollback()
                return schedule
        except KeyboardInterrupt:
            raise
        except PreferredMoveError:
            raise
        except SchemaIncompatibleError as error:
            raise PreferredMoveSchemaError(str(error)) from error
        except (PositionValidationError, RangeValidationError) as error:
            raise PreferredMoveValidationError(str(error)) from error
        except Exception as error:
            raise _translate_storage_error(error) from error

    def read_periods_for_position(
        self, position: CanonicalPosition
    ) -> tuple[NormalizedPeriod, ...]:
        """Read one canonical position schedule through a read-only connection."""

        if not isinstance(position, CanonicalPosition):
            raise PreferredMoveValidationError(
                "position must be a CanonicalPosition value"
            )
        try:
            with _open_connection(
                self._database_path, "read-only", self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                position_id = _find_existing_position_id(connection, position)
                if position_id is None:
                    connection.rollback()
                    return ()
                schedule = _load_schedule(
                    connection,
                    position_id,
                    position=position,
                )
                connection.rollback()
                return schedule
        except KeyboardInterrupt:
            raise
        except PreferredMoveError:
            raise
        except SchemaIncompatibleError as error:
            raise PreferredMoveSchemaError(str(error)) from error
        except (PositionValidationError, RangeValidationError) as error:
            raise PreferredMoveValidationError(str(error)) from error
        except Exception as error:
            raise _translate_storage_error(error) from error

    def resolve(self, fen: str, date_literal: str) -> DateResolution:
        """Resolve one strict date without creating a position or period."""

        try:
            return resolve_date(self.list_periods(fen), date_literal)
        except RangeValidationError as error:
            raise PreferredMoveValidationError(str(error)) from error

    def set(
        self,
        fen: str,
        effective_from: str,
        effective_until: str | None,
        preference: Preference,
    ) -> tuple[NormalizedPeriod, ...]:
        """Atomically overlay a legal move or explicit no-preference period."""

        position = _canonicalize_four_field_fen(fen)
        _validate_preference(position, preference)
        return self._amend(
            position,
            lambda schedule: set_preference(
                schedule, effective_from, effective_until, preference
            ),
        )

    def unset(
        self,
        fen: str,
        effective_from: str,
        effective_until: str | None,
    ) -> tuple[NormalizedPeriod, ...]:
        """Atomically remove configuration from one date range."""

        position = _canonicalize_four_field_fen(fen)
        return self._amend(
            position,
            lambda schedule: unset_preference(
                schedule, effective_from, effective_until
            ),
        )

    def _amend(
        self,
        position: CanonicalPosition,
        amendment: Callable[
            [tuple[NormalizedPeriod, ...]], tuple[NormalizedPeriod, ...]
        ],
    ) -> tuple[NormalizedPeriod, ...]:
        try:
            with _open_existing_connection(
                self._database_path, self._lock_timeout
            ) as connection:
                _assert_compatible_schema(connection, self._lock_timeout)
                self._checkpoint("before_lock")
                connection.exec_driver_sql("BEGIN IMMEDIATE")
                transaction = connection.get_transaction()
                if transaction is None:
                    raise PreferredMoveStorageError(
                        "SQLite did not establish the immediate transaction"
                    )
                try:
                    self._checkpoint("locked")
                    position_id = _PositionUnitOfWork(connection)._resolve(position)
                    self._checkpoint("position")
                    current = _load_schedule(
                        connection,
                        position_id,
                        position=position,
                    )
                    replacement = normalize_periods(amendment(current))
                    self._checkpoint("normalized")
                    _replace_schedule(connection, position_id, replacement)
                    self._checkpoint("replaced")
                    persisted = _load_schedule(connection, position_id)
                    if persisted != replacement:
                        raise PreferredMoveStorageError(
                            "persisted schedule did not match its normalized replacement"
                        )
                    self._checkpoint("verified")
                except BaseException:
                    transaction.rollback()
                    raise
                else:
                    transaction.commit()
                    return persisted
        except KeyboardInterrupt:
            raise
        except PreferredMoveError:
            raise
        except SchemaIncompatibleError as error:
            raise PreferredMoveSchemaError(str(error)) from error
        except (PositionValidationError, RangeValidationError, ValueError) as error:
            raise PreferredMoveValidationError(str(error)) from error
        except Exception as error:
            raise _translate_storage_error(error) from error


def _canonicalize_four_field_fen(fen: str) -> CanonicalPosition:
    if not isinstance(fen, str) or len(fen.split()) != 4:
        raise PreferredMoveValidationError("FEN must contain exactly four fields")
    try:
        return canonicalize_fen(f"{' '.join(fen.split())} 0 1")
    except PositionValidationError as error:
        raise PreferredMoveValidationError(str(error)) from error


def _validate_preference(
    position: CanonicalPosition,
    preference: Preference,
    *,
    require_canonical_uci: bool = False,
) -> None:
    if not isinstance(preference, Preference):
        raise PreferredMoveValidationError("preference must be a Preference")
    if preference.state is PreferenceState.NO_PREFERENCE:
        return
    board = chess.Board(
        " ".join(
            (
                position.placement,
                position.side_to_move,
                position.castling_rights,
                position.legal_en_passant,
                "0",
                "1",
            )
        )
    )
    try:
        move = chess.Move.from_uci(preference.move or "")
    except ValueError as error:
        raise PreferredMoveValidationError("move must be valid UCI") from error
    if require_canonical_uci and move.uci() != preference.move:
        raise PreferredMoveValidationError("move must be valid UCI")
    if move not in board.legal_moves:
        raise PreferredMoveValidationError("move must be legal from the canonical position")


def _load_schedule(
    connection: object,
    position_id: int,
    *,
    position: CanonicalPosition | None = None,
) -> tuple[NormalizedPeriod, ...]:
    try:
        rows = connection.execute(
            text(
                """
                SELECT dpm_effective_from, dpm_effective_until, dpm_move_uci
                FROM datasource_preferred_move_period
                WHERE derived_position_id = :position_id
                ORDER BY dpm_effective_from
                """
            ),
            {"position_id": position_id},
        ).all()
        periods_list: list[NormalizedPeriod] = []
        for row in rows:
            if not isinstance(row[0], str):
                raise ValueError("stored preferred-move start date is malformed")
            if row[1] is not None and not isinstance(row[1], str):
                raise ValueError("stored preferred-move end date is malformed")
            if row[2] is not None and not isinstance(row[2], str):
                raise ValueError("stored preferred-move is malformed")
            move = row[2]
            if move is not None and position is not None:
                _validate_stored_move(position, move)
            periods_list.append(
                period_from_literals(
                    row[0],
                    row[1],
                    Preference.no_preference()
                    if move is None
                    else Preference.preferred_move(move),
                )
            )
        periods = tuple(periods_list)
        return normalize_periods(periods)
    except (IndexError, TypeError, ValueError, RangeValidationError) as error:
        raise PreferredMoveStorageError(
            "stored preferred-move schedule is malformed"
        ) from error


def _validate_stored_move(position: CanonicalPosition, move_uci: str) -> None:
    board = chess.Board(
        " ".join(
            (
                position.placement,
                position.side_to_move,
                position.castling_rights,
                position.legal_en_passant,
                "0",
                "1",
            )
        )
    )
    try:
        move = chess.Move.from_uci(move_uci)
    except ValueError as error:
        raise ValueError("stored preferred-move is not valid UCI") from error
    if move.uci() != move_uci or move not in board.legal_moves:
        raise ValueError("stored preferred-move is not legal")


def _replace_schedule(
    connection: object,
    position_id: int,
    periods: tuple[NormalizedPeriod, ...],
) -> None:
    connection.execute(
        text(
            "DELETE FROM datasource_preferred_move_period "
            "WHERE derived_position_id = :position_id"
        ),
        {"position_id": position_id},
    )
    for period in periods:
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


def _translate_storage_error(error: Exception) -> PreferredMoveStorageError:
    candidate: BaseException | None = error
    while candidate is not None:
        if isinstance(candidate, sqlite3.OperationalError) and "locked" in str(
            candidate
        ).lower():
            return PreferredMoveLockError(
                "preferred-move writer lock was not acquired before timeout"
            )
        candidate = candidate.__cause__ or candidate.__context__
    if isinstance(error, OperationalError) and "locked" in str(error).lower():
        return PreferredMoveLockError(
            "preferred-move writer lock was not acquired before timeout"
        )
    if isinstance(error, PositionStorageError):
        return PreferredMoveStorageError(str(error))
    return PreferredMoveStorageError("preferred-move database operation failed")
