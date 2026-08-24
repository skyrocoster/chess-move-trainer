"""Versioned SQLite schema for direct preferred-move histories."""

from __future__ import annotations

import sqlite3

from .schema import OpeningSchemaError, _table_names

PREFERRED_MOVE_SCHEMA_VERSION = 1
PREFERRED_MOVE_SCHEMA_TABLES = {
    "opening_preferred_move_schema",
    "opening_preferred_move_requirement_event",
    "opening_preferred_move_event",
}
PREFERRED_MOVE_SCHEMA_TRIGGERS = {
    "opening_preferred_move_requirement_no_update",
    "opening_preferred_move_requirement_no_delete",
    "opening_preferred_move_no_update",
    "opening_preferred_move_no_delete",
}


def _required_tables(connection: sqlite3.Connection) -> set[str]:
    return {
        "players",
        "games",
        "position_state",
        "position_occurrence",
    }


def _validate_existing_schema(connection: sqlite3.Connection) -> None:
    expected = {
        "opening_preferred_move_schema": ("id", "version"),
        "opening_preferred_move_requirement_event": (
            "event_id",
            "player_uuid",
            "placement",
            "side_to_move",
            "castling",
            "en_passant",
            "action",
            "effective_at",
            "recorded_at",
        ),
        "opening_preferred_move_event": (
            "event_id",
            "player_uuid",
            "placement",
            "side_to_move",
            "castling",
            "en_passant",
            "action",
            "move_uci",
            "move_san",
            "effective_at",
            "recorded_at",
        ),
    }
    for table, columns in expected.items():
        actual = tuple(row[1] for row in connection.execute(f"PRAGMA table_info({table})"))
        if actual != columns:
            raise OpeningSchemaError(f"preferred-move table {table} has incompatible columns")
    trigger_rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'trigger'"
    ).fetchall()
    if PREFERRED_MOVE_SCHEMA_TRIGGERS - {str(row[0]) for row in trigger_rows}:
        raise OpeningSchemaError("preferred-move append-only triggers are incomplete")


def ensure_preferred_move_schema(
    connection: sqlite3.Connection, wanted: int = PREFERRED_MOVE_SCHEMA_VERSION
) -> None:
    """Create or validate the additive, append-only preferred-move schema."""

    connection.execute("PRAGMA foreign_keys = ON")
    names = _table_names(connection)
    missing_required = _required_tables(connection) - names
    if missing_required:
        raise OpeningSchemaError(
            "players, games, position_state, and position_occurrence are required "
            f"({', '.join(sorted(missing_required))}); no changes made"
        )
    if "opening_preferred_move_schema" in names:
        version = connection.execute(
            "SELECT version FROM opening_preferred_move_schema WHERE id = 1"
        ).fetchone()
        if version is None:
            raise OpeningSchemaError(
                "preferred-move schema has no singleton version row; no changes made"
            )
        if version[0] != wanted:
            raise OpeningSchemaError(
                f"incompatible preferred-move schema version {version[0]}; "
                f"expected {wanted}; no changes made"
            )
        missing = PREFERRED_MOVE_SCHEMA_TABLES - names
        if missing:
            raise OpeningSchemaError(
                f"preferred-move schema is incomplete ({', '.join(sorted(missing))}); "
                "no changes made"
            )
        _validate_existing_schema(connection)
        return
    if names & PREFERRED_MOVE_SCHEMA_TABLES:
        raise OpeningSchemaError(
            "preferred-move objects exist without a version table; no changes made"
        )

    statements = (
        """
        CREATE TABLE opening_preferred_move_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_preferred_move_requirement_event (
            event_id INTEGER PRIMARY KEY,
            player_uuid TEXT NOT NULL,
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL CHECK (side_to_move IN ('w', 'b')),
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            action TEXT NOT NULL CHECK (action IN ('active', 'inactive')),
            effective_at TEXT NOT NULL,
            recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            FOREIGN KEY (player_uuid) REFERENCES players(uuid),
            FOREIGN KEY (placement, side_to_move, castling, en_passant)
                REFERENCES position_state(placement, side_to_move, castling, en_passant)
        )
        """,
        """
        CREATE TABLE opening_preferred_move_event (
            event_id INTEGER PRIMARY KEY,
            player_uuid TEXT NOT NULL,
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL CHECK (side_to_move IN ('w', 'b')),
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            action TEXT NOT NULL CHECK (action IN ('set', 'remove')),
            move_uci TEXT,
            move_san TEXT,
            effective_at TEXT NOT NULL,
            recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            CHECK (
                (action = 'set' AND move_uci IS NOT NULL AND move_san IS NOT NULL)
                OR (action = 'remove' AND move_uci IS NULL AND move_san IS NULL)
            ),
            FOREIGN KEY (player_uuid) REFERENCES players(uuid),
            FOREIGN KEY (placement, side_to_move, castling, en_passant)
                REFERENCES position_state(placement, side_to_move, castling, en_passant)
        )
        """,
        """
        CREATE INDEX opening_preferred_move_requirement_lookup
            ON opening_preferred_move_requirement_event(
                player_uuid, placement, side_to_move, castling, en_passant,
                effective_at, recorded_at, event_id
            )
        """,
        """
        CREATE INDEX opening_preferred_move_lookup
            ON opening_preferred_move_event(
                player_uuid, placement, side_to_move, castling, en_passant,
                effective_at, recorded_at, event_id
            )
        """,
        """
        CREATE TRIGGER opening_preferred_move_requirement_no_update
        BEFORE UPDATE ON opening_preferred_move_requirement_event
        BEGIN
            SELECT RAISE(ABORT, 'preferred-move requirement history is append-only');
        END
        """,
        """
        CREATE TRIGGER opening_preferred_move_requirement_no_delete
        BEFORE DELETE ON opening_preferred_move_requirement_event
        BEGIN
            SELECT RAISE(ABORT, 'preferred-move requirement history is append-only');
        END
        """,
        """
        CREATE TRIGGER opening_preferred_move_no_update
        BEFORE UPDATE ON opening_preferred_move_event
        BEGIN
            SELECT RAISE(ABORT, 'preferred-move history is append-only');
        END
        """,
        """
        CREATE TRIGGER opening_preferred_move_no_delete
        BEFORE DELETE ON opening_preferred_move_event
        BEGIN
            SELECT RAISE(ABORT, 'preferred-move history is append-only');
        END
        """,
    )
    with connection:
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO opening_preferred_move_schema (id, version) VALUES (1, ?)",
            (wanted,),
        )
