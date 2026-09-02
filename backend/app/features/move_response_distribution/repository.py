"""Non-initializing read-only adapter for accepted recurrence projections."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from backend.app.features.positions.repository import SUBJECT_PLAYER_UUID, database_path
from scripts.opening_catalog.recurrence_schema import RECURRENCE_SCHEMA_VERSION

from .errors import MoveResponseDistributionUnavailableError

PositionKey = tuple[str, str, str, str]
_COLORS = frozenset(("white", "black"))

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
    "opening_recurrence_branch_projection": (
        "manifest_hash",
        "corpus_id",
        "parent_placement",
        "parent_side_to_move",
        "parent_castling",
        "parent_en_passant",
        "branch_kind",
        "child_uci",
        "color_scope",
        "distinct_game_count",
    ),
}


@dataclass(frozen=True)
class MoveResponseBranch:
    child_uci: object
    distinct_game_count: object


@dataclass(frozen=True)
class MoveResponseRead:
    matching_game_count: object | None
    branches: tuple[MoveResponseBranch, ...]


def _database_uri(path: Path, mode: str) -> str:
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
        if set(_REQUIRED_COLUMNS) - names:
            raise MoveResponseDistributionUnavailableError

        version = connection.execute(
            "SELECT version FROM opening_recurrence_schema WHERE id = 1"
        ).fetchone()
        if version is None or version[0] != RECURRENCE_SCHEMA_VERSION:
            raise MoveResponseDistributionUnavailableError

        for table, expected in _REQUIRED_COLUMNS.items():
            if not set(expected).issubset(_columns(connection, table)):
                raise MoveResponseDistributionUnavailableError
    except MoveResponseDistributionUnavailableError:
        raise
    except (sqlite3.Error, Exception) as error:
        raise MoveResponseDistributionUnavailableError from error


def open_read_connection() -> sqlite3.Connection:
    """Open an existing supported database without schema creation or writes."""

    path = database_path().expanduser().resolve()
    if not path.is_file():
        raise MoveResponseDistributionUnavailableError

    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(_database_uri(path, "ro"), uri=True, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        _require_schema(connection)
        return connection
    except MoveResponseDistributionUnavailableError:
        if connection is not None:
            connection.close()
        raise
    except sqlite3.Error as error:
        if connection is not None:
            connection.close()
        raise MoveResponseDistributionUnavailableError from error


class MoveResponseDistributionRepository:
    """Read the accepted parent and move-branch projections for one position."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def lookup(self, key: PositionKey, color: str) -> MoveResponseRead:
        if color not in _COLORS:
            raise ValueError("unsupported response color")
        manifest_hash, corpus_id = self._accepted_scope()
        matching_game_count = self._parent_count(manifest_hash, corpus_id, key, color)
        branches = self._branches(manifest_hash, corpus_id, key, color)
        if matching_game_count is None and branches:
            raise MoveResponseDistributionUnavailableError
        return MoveResponseRead(matching_game_count, tuple(branches))

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
            raise MoveResponseDistributionUnavailableError from error

        if len(rows) != 1:
            raise MoveResponseDistributionUnavailableError
        manifest_hash = rows[0]["accepted_manifest_hash"]
        corpus_id = rows[0]["corpus_id"]
        if (
            not isinstance(manifest_hash, str)
            or not manifest_hash
            or isinstance(corpus_id, bool)
            or not isinstance(corpus_id, int)
        ):
            raise MoveResponseDistributionUnavailableError
        return manifest_hash, corpus_id

    def _parent_count(
        self,
        manifest_hash: str,
        corpus_id: int,
        key: PositionKey,
        color: str,
    ) -> object | None:
        try:
            rows = self._connection.execute(
                "SELECT distinct_game_count "
                "FROM opening_recurrence_position_projection "
                "WHERE manifest_hash = ? AND corpus_id = ? "
                "AND placement = ? AND side_to_move = ? "
                "AND castling = ? AND en_passant = ? "
                "AND color_scope = ?",
                (manifest_hash, corpus_id, *key, color),
            ).fetchall()
        except sqlite3.Error as error:
            raise MoveResponseDistributionUnavailableError from error
        if len(rows) > 1:
            raise MoveResponseDistributionUnavailableError
        return None if not rows else rows[0]["distinct_game_count"]

    def _branches(
        self,
        manifest_hash: str,
        corpus_id: int,
        key: PositionKey,
        color: str,
    ) -> list[MoveResponseBranch]:
        try:
            rows = self._connection.execute(
                "SELECT child_uci, distinct_game_count "
                "FROM opening_recurrence_branch_projection "
                "WHERE manifest_hash = ? AND corpus_id = ? "
                "AND parent_placement = ? AND parent_side_to_move = ? "
                "AND parent_castling = ? AND parent_en_passant = ? "
                "AND branch_kind = 'move' AND color_scope = ?",
                (manifest_hash, corpus_id, *key, color),
            ).fetchall()
        except sqlite3.Error as error:
            raise MoveResponseDistributionUnavailableError from error
        return [
            MoveResponseBranch(
                child_uci=row["child_uci"],
                distinct_game_count=row["distinct_game_count"],
            )
            for row in rows
        ]
