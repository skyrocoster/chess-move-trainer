"""Non-initializing read-only adapter for accepted S4 position projections."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from backend.app.features.positions.repository import (
    SUBJECT_PLAYER_UUID,
    database_path,
)
from scripts.opening_catalog.recurrence_schema import RECURRENCE_SCHEMA_VERSION

from .errors import PositionContextUnavailableError

PositionKey = tuple[str, str, str, str]

_REQUIRED_COLUMNS = {
    "corpus": ("corpus_id", "subject_player_uuid"),
    "opening_recurrence_schema": ("id", "version"),
    "opening_recurrence_state": (
        "accepted_manifest_hash",
        "corpus_id",
        "accepted_schema_version",
    ),
    "opening_recurrence_position_projection": (
        "manifest_hash",
        "corpus_id",
        "placement",
        "side_to_move",
        "castling",
        "en_passant",
        "color_scope",
        "distinct_game_count",
    ),
    "opening_recurrence_game": ("manifest_hash", "corpus_id", "game_uuid", "game_color"),
}
_COLOR_SCOPES = frozenset(("overall", "white", "black"))
_GAME_COLORS = frozenset(("white", "black"))


@dataclass(frozen=True)
class PositionContext:
    """Neutral corpus context for one exact four-field position identity."""

    overall_exists: bool
    white_count: int
    black_count: int
    white_total: int
    black_total: int


def _database_uri(path, mode: str) -> str:
    return f"{path.expanduser().resolve().as_uri()}?mode={mode}"


def _table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def _columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")}


def _require_schema(connection: sqlite3.Connection) -> None:
    try:
        names = _table_names(connection)
        missing_tables = set(_REQUIRED_COLUMNS) - names
        if missing_tables:
            raise PositionContextUnavailableError

        version = connection.execute(
            "SELECT version FROM opening_recurrence_schema WHERE id = 1"
        ).fetchone()
        if version is None or version[0] != RECURRENCE_SCHEMA_VERSION:
            raise PositionContextUnavailableError

        for table, expected in _REQUIRED_COLUMNS.items():
            if not set(expected).issubset(_columns(connection, table)):
                raise PositionContextUnavailableError
    except PositionContextUnavailableError:
        raise
    except sqlite3.Error as error:
        raise PositionContextUnavailableError from error
    except Exception as error:
        raise PositionContextUnavailableError from error


def open_read_connection() -> sqlite3.Connection:
    """Open an existing supported database without schema creation or write access."""

    path = database_path().expanduser().resolve()
    if not path.is_file():
        raise PositionContextUnavailableError

    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(_database_uri(path, "ro"), uri=True, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        _require_schema(connection)
        return connection
    except PositionContextUnavailableError:
        if connection is not None:
            connection.close()
        raise
    except sqlite3.Error as error:
        if connection is not None:
            connection.close()
        raise PositionContextUnavailableError from error


class PositionContextRepository:
    """Resolve accepted S4 recurrence counts from an already-open read-only connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def lookup(self, key: PositionKey) -> PositionContext:
        manifest_hash, corpus_id = self._accepted_scope()
        totals = self._game_totals(manifest_hash, corpus_id)
        try:
            rows = self._connection.execute(
                "SELECT color_scope, distinct_game_count "
                "FROM opening_recurrence_position_projection "
                "WHERE manifest_hash = ? AND corpus_id = ? "
                "AND placement = ? AND side_to_move = ? "
                "AND castling = ? AND en_passant = ? "
                "AND color_scope IN ('overall', 'white', 'black')",
                (manifest_hash, corpus_id, *key),
            ).fetchall()
        except sqlite3.Error as error:
            raise PositionContextUnavailableError from error

        counts: dict[str, int] = {}
        for row in rows:
            scope = row["color_scope"]
            count = row["distinct_game_count"]
            if (
                scope not in _COLOR_SCOPES
                or scope in counts
                or isinstance(count, bool)
                or not isinstance(count, int)
                or count < 0
            ):
                raise PositionContextUnavailableError
            counts[scope] = count

        return PositionContext(
            overall_exists="overall" in counts,
            white_count=counts.get("white", 0),
            black_count=counts.get("black", 0),
            white_total=totals["white"],
            black_total=totals["black"],
        )

    def _game_totals(self, manifest_hash: str, corpus_id: int) -> dict[str, int]:
        try:
            rows = self._connection.execute(
                "SELECT game_color, COUNT(*) AS game_count "
                "FROM opening_recurrence_game "
                "WHERE manifest_hash = ? AND corpus_id = ? "
                "GROUP BY game_color",
                (manifest_hash, corpus_id),
            ).fetchall()
        except sqlite3.Error as error:
            raise PositionContextUnavailableError from error

        totals = {color: 0 for color in _GAME_COLORS}
        for row in rows:
            color = row["game_color"]
            count = row["game_count"]
            if (
                color not in _GAME_COLORS
                or isinstance(count, bool)
                or not isinstance(count, int)
                or count < 0
            ):
                raise PositionContextUnavailableError
            totals[color] = count
        return totals

    def _accepted_scope(self) -> tuple[str, int]:
        try:
            rows = self._connection.execute(
                "SELECT s.accepted_manifest_hash, s.corpus_id "
                "FROM opening_recurrence_state AS s "
                "JOIN corpus AS c ON c.corpus_id = s.corpus_id "
                "WHERE c.subject_player_uuid = ? "
                "AND s.accepted_schema_version = ? LIMIT 2",
                (SUBJECT_PLAYER_UUID, RECURRENCE_SCHEMA_VERSION),
            ).fetchall()
        except sqlite3.Error as error:
            raise PositionContextUnavailableError from error
        if len(rows) != 1:
            raise PositionContextUnavailableError

        manifest_hash = rows[0]["accepted_manifest_hash"]
        corpus_id = rows[0]["corpus_id"]
        if (
            not isinstance(manifest_hash, str)
            or not manifest_hash
            or isinstance(corpus_id, bool)
            or not isinstance(corpus_id, int)
        ):
            raise PositionContextUnavailableError
        return manifest_hash, corpus_id
