"""Non-initializing database adapter for the existing preferred-move history."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from backend.app.features.positions.repository import SUBJECT_PLAYER_UUID, database_path
from scripts.opening_catalog.preferred_move import (
    MOVE_TABLE,
    PreferredMoveError,
    _latest_event,
    _set_preferred_move,
    _state_from_events,
)
from scripts.opening_catalog.preferred_move_contract import PreferredMoveState
from scripts.opening_catalog.preferred_move_schema import (
    PREFERRED_MOVE_SCHEMA_TABLES,
    PREFERRED_MOVE_SCHEMA_TRIGGERS,
    PREFERRED_MOVE_SCHEMA_VERSION,
    _validate_existing_schema,
)

from .errors import PreferredMovePositionNotFoundError, PreferredMoveUnavailableError

PositionKey = tuple[str, str, str, str]

_BASE_TABLE_COLUMNS = {
    "players": ("uuid",),
    "games": ("uuid",),
    "position_state": ("placement", "side_to_move", "castling", "en_passant"),
    "position_occurrence": ("game_uuid", "state_id"),
}


@dataclass(frozen=True)
class PreferredPosition:
    key: PositionKey


@dataclass(frozen=True)
class PreferredMoveRead:
    state: PreferredMoveState
    effective_at: str | None


def _database_uri(path: Path, mode: str) -> str:
    return f"{path.expanduser().resolve().as_uri()}?mode={mode}"


def _table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def _columns(connection: sqlite3.Connection, table: str) -> tuple[str, ...]:
    return tuple(str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})"))


def _require_schema(connection: sqlite3.Connection) -> None:
    try:
        names = _table_names(connection)
        required = set(_BASE_TABLE_COLUMNS) | PREFERRED_MOVE_SCHEMA_TABLES
        missing = required - names
        if missing:
            raise PreferredMoveUnavailableError

        version = connection.execute(
            "SELECT version FROM opening_preferred_move_schema WHERE id = 1"
        ).fetchone()
        if version is None or version[0] != PREFERRED_MOVE_SCHEMA_VERSION:
            raise PreferredMoveUnavailableError

        for table, expected in _BASE_TABLE_COLUMNS.items():
            if not set(expected).issubset(_columns(connection, table)):
                raise PreferredMoveUnavailableError
        _validate_existing_schema(connection)

        trigger_names = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'trigger'"
            ).fetchall()
        }
        if not PREFERRED_MOVE_SCHEMA_TRIGGERS.issubset(trigger_names):
            raise PreferredMoveUnavailableError

        owner = connection.execute(
            "SELECT 1 FROM players WHERE uuid = ?", (SUBJECT_PLAYER_UUID,)
        ).fetchone()
        if owner is None:
            raise PreferredMoveUnavailableError
    except PreferredMoveUnavailableError:
        raise
    except sqlite3.Error as error:
        raise PreferredMoveUnavailableError from error
    except Exception as error:
        raise PreferredMoveUnavailableError from error


def _open_connection(mode: str, *, timeout: float) -> sqlite3.Connection:
    path = database_path().expanduser().resolve()
    if not path.is_file():
        raise PreferredMoveUnavailableError
    try:
        connection = sqlite3.connect(_database_uri(path, mode), uri=True, timeout=timeout)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        _require_schema(connection)
        return connection
    except PreferredMoveUnavailableError:
        try:
            connection.close()
        except UnboundLocalError:
            pass
        raise
    except sqlite3.Error as error:
        try:
            connection.close()
        except UnboundLocalError:
            pass
        raise PreferredMoveUnavailableError from error


def open_read_connection() -> sqlite3.Connection:
    """Open an existing supported database without write permission or DDL."""

    return _open_connection("ro", timeout=5.0)


def open_write_connection() -> sqlite3.Connection:
    """Open an existing supported database for append-only event writes only."""

    return _open_connection("rw", timeout=0)


class PreferredMoveRepository:
    """Resolve observed positions and delegate event semantics to storage primitives."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def position(self, key: PositionKey) -> PreferredPosition:
        try:
            row = self._connection.execute(
                "SELECT 1 FROM position_state AS ps "
                "JOIN position_occurrence AS po ON po.state_id = ps.state_id "
                "WHERE ps.placement = ? AND ps.side_to_move = ? "
                "AND ps.castling = ? AND ps.en_passant = ? LIMIT 1",
                key,
            ).fetchone()
        except sqlite3.Error as error:
            raise PreferredMoveUnavailableError from error
        if row is None:
            raise PreferredMovePositionNotFoundError
        return PreferredPosition(key)

    def state_at(self, position: PreferredPosition, effective_at: str):
        try:
            state = _state_from_events(
                self._connection, SUBJECT_PLAYER_UUID, position.key, effective_at
            )
            move_event = _latest_event(
                self._connection,
                MOVE_TABLE,
                SUBJECT_PLAYER_UUID,
                position.key,
                effective_at,
            )
            selected_effective_at = (
                None
                if move_event is None or move_event[7] is None
                else str(move_event[9])
            )
            return PreferredMoveRead(state, selected_effective_at)
        except sqlite3.Error as error:
            raise PreferredMoveUnavailableError from error

    def append(self, position: PreferredPosition, move_uci: str | None, effective_at: str):
        try:
            self._connection.execute("BEGIN IMMEDIATE")
            result = _set_preferred_move(
                self._connection,
                SUBJECT_PLAYER_UUID,
                position.key,
                move_uci,
                effective_at,
            )
            self._connection.commit()
            return result
        except PreferredMoveError as error:
            self._connection.rollback()
            raise PreferredMoveUnavailableError from error
        except sqlite3.OperationalError as error:
            self._connection.rollback()
            raise PreferredMoveUnavailableError from error
        except sqlite3.Error as error:
            self._connection.rollback()
            raise PreferredMoveUnavailableError from error
        except Exception:
            self._connection.rollback()
            raise
