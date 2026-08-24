"""Versioned additive SQLite schema for S5 tracked-player projections."""

from __future__ import annotations

import re
import sqlite3

from .classification_schema import CLASSIFICATION_SCHEMA_TABLES
from .recurrence_schema import RECURRENCE_SCHEMA_TABLES
from .schema import OpeningSchemaError, _table_names
from .tracked_player_contract import (
    TRACKED_PLAYER_BRANCH_IDENTITY_FIELDS,
    TRACKED_PLAYER_CLASSIFICATION_IDENTITY_FIELDS,
    TRACKED_PLAYER_POSITION_IDENTITY_FIELDS,
    TRACKED_PLAYER_ROUTE_BRANCH_IDENTITY_FIELDS,
    TRACKED_PLAYER_ROUTE_IDENTITY_FIELDS,
)

TRACKED_PLAYER_SCHEMA_VERSION = 1

TRACKED_PLAYER_SCHEMA_TABLES = {
    "opening_tracked_player_schema",
    "opening_tracked_player",
    "opening_tracked_player_state",
    "opening_tracked_player_run",
    "opening_player_classification_game",
    "opening_player_position_projection",
    "opening_player_route_projection",
    "opening_player_branch_projection",
    "opening_player_route_branch_projection",
}

_EXPECTED_COLUMNS = {
    "opening_tracked_player_schema": "id version".split(),
    "opening_tracked_player": "player_uuid".split(),
    "opening_tracked_player_state": (
        "player_uuid accepted_manifest_hash corpus_id accepted_schema_version "
        "accepted_classification_schema_version accepted_recurrence_schema_version "
        "classification_input_signature recurrence_input_signature accepted_at "
        "classification_game_count position_projection_count route_projection_count "
        "branch_projection_count route_branch_projection_count"
    ).split(),
    "opening_tracked_player_run": (
        "run_id player_uuid manifest_hash corpus_id schema_version "
        "classification_schema_version recurrence_schema_version "
        "classification_input_signature recurrence_input_signature status started_at "
        "finished_at classification_game_count position_projection_count "
        "route_projection_count branch_projection_count route_branch_projection_count details"
    ).split(),
    "opening_player_classification_game": TRACKED_PLAYER_CLASSIFICATION_IDENTITY_FIELDS,
    "opening_player_position_projection": TRACKED_PLAYER_POSITION_IDENTITY_FIELDS
    + tuple(
        "raw_occurrence_count distinct_game_count first_game_sequence first_game_uuid "
        "first_ply last_game_sequence last_game_uuid last_ply".split()
    ),
    "opening_player_route_projection": TRACKED_PLAYER_ROUTE_IDENTITY_FIELDS
    + tuple(
        "raw_occurrence_count distinct_game_count first_game_sequence first_game_uuid "
        "first_route_ply last_game_sequence last_game_uuid last_route_ply".split()
    ),
    "opening_player_branch_projection": TRACKED_PLAYER_BRANCH_IDENTITY_FIELDS
    + tuple(
        "raw_event_count distinct_game_count first_game_sequence first_game_uuid "
        "first_parent_ply last_game_sequence last_game_uuid last_parent_ply".split()
    ),
    "opening_player_route_branch_projection": TRACKED_PLAYER_ROUTE_BRANCH_IDENTITY_FIELDS
    + tuple(
        "raw_event_count distinct_game_count first_game_sequence first_game_uuid "
        "first_parent_ply last_game_sequence last_game_uuid last_parent_ply".split()
    ),
}

_EXPECTED_PRIMARY_KEYS = {
    "opening_tracked_player_schema": ("id",),
    "opening_tracked_player": ("player_uuid",),
    "opening_tracked_player_state": tuple("player_uuid accepted_manifest_hash corpus_id".split()),
    "opening_tracked_player_run": ("run_id",),
    "opening_player_classification_game": TRACKED_PLAYER_CLASSIFICATION_IDENTITY_FIELDS,
    "opening_player_position_projection": TRACKED_PLAYER_POSITION_IDENTITY_FIELDS,
    "opening_player_route_projection": TRACKED_PLAYER_ROUTE_IDENTITY_FIELDS,
    "opening_player_branch_projection": TRACKED_PLAYER_BRANCH_IDENTITY_FIELDS,
    "opening_player_route_branch_projection": TRACKED_PLAYER_ROUTE_BRANCH_IDENTITY_FIELDS,
}


def _foreign_key(
    target: str, source: tuple[str, ...], destination: tuple[str, ...]
) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    return target, source, destination


_EXPECTED_FOREIGN_KEYS = {
    "opening_tracked_player": (_foreign_key("players", ("player_uuid",), ("uuid",)),),
    "opening_tracked_player_state": (
        _foreign_key("opening_tracked_player", ("player_uuid",), ("player_uuid",)),
        _foreign_key(
            "opening_recurrence_state",
            ("accepted_manifest_hash", "corpus_id"),
            ("accepted_manifest_hash", "corpus_id"),
        ),
    ),
    "opening_tracked_player_run": (
        _foreign_key("opening_tracked_player", ("player_uuid",), ("player_uuid",)),
        _foreign_key(
            "opening_recurrence_state",
            ("manifest_hash", "corpus_id"),
            ("accepted_manifest_hash", "corpus_id"),
        ),
    ),
    "opening_player_classification_game": (
        _foreign_key(
            "opening_tracked_player_state",
            ("player_uuid", "manifest_hash", "corpus_id"),
            ("player_uuid", "accepted_manifest_hash", "corpus_id"),
        ),
        _foreign_key(
            "opening_classification_game",
            ("manifest_hash", "corpus_id", "game_uuid"),
            ("manifest_hash", "corpus_id", "game_uuid"),
        ),
    ),
}

_PROJECTION_FOREIGN_KEYS = {
    "opening_player_position_projection": (
        "opening_recurrence_position_projection",
        TRACKED_PLAYER_POSITION_IDENTITY_FIELDS,
    ),
    "opening_player_route_projection": (
        "opening_recurrence_route_projection",
        TRACKED_PLAYER_ROUTE_IDENTITY_FIELDS,
    ),
    "opening_player_branch_projection": (
        "opening_recurrence_branch_projection",
        TRACKED_PLAYER_BRANCH_IDENTITY_FIELDS,
    ),
    "opening_player_route_branch_projection": (
        "opening_recurrence_route_branch_projection",
        TRACKED_PLAYER_ROUTE_BRANCH_IDENTITY_FIELDS,
    ),
}

for _table, (_target, _identity) in _PROJECTION_FOREIGN_KEYS.items():
    _EXPECTED_FOREIGN_KEYS[_table] = (
        _foreign_key(
            "opening_tracked_player_state",
            ("player_uuid", "manifest_hash", "corpus_id"),
            ("player_uuid", "accepted_manifest_hash", "corpus_id"),
        ),
        _foreign_key(_target, _identity[1:], _identity[1:]),
    )

_REQUIRED_TABLES = (
    set("players games corpus_schema corpus corpus_game position_state position_occurrence".split())
    | CLASSIFICATION_SCHEMA_TABLES
    | RECURRENCE_SCHEMA_TABLES
)


def _actual_foreign_keys(
    connection: sqlite3.Connection, table: str
) -> frozenset[tuple[str, tuple[str, ...], tuple[str, ...]]]:
    grouped: dict[int, list[tuple[int, str, str, str]]] = {}
    for row in connection.execute(f"PRAGMA foreign_key_list({table})"):
        grouped.setdefault(int(row[0]), []).append(
            (int(row[1]), str(row[2]), str(row[3]), str(row[4]))
        )
    return frozenset(
        (
            rows[0][1],
            tuple(row[2] for row in sorted(rows)),
            tuple(row[3] for row in sorted(rows)),
        )
        for rows in grouped.values()
    )


def _validate_existing_schema(connection: sqlite3.Connection) -> None:
    for table in sorted(TRACKED_PLAYER_SCHEMA_TABLES):
        info = connection.execute(f"PRAGMA table_info({table})").fetchall()
        actual_columns = tuple(str(row[1]) for row in info)
        if actual_columns != tuple(_EXPECTED_COLUMNS[table]):
            raise OpeningSchemaError(
                f"opening tracked-player table {table} has incompatible columns"
            )
        actual_primary_key = tuple(
            str(row[1]) for row in sorted(info, key=lambda row: int(row[5])) if row[5]
        )
        if actual_primary_key != _EXPECTED_PRIMARY_KEYS[table]:
            raise OpeningSchemaError(
                f"opening tracked-player table {table} has an incompatible key"
            )
        expected_foreign_keys = frozenset(_EXPECTED_FOREIGN_KEYS.get(table, ()))
        if _actual_foreign_keys(connection, table) != expected_foreign_keys:
            raise OpeningSchemaError(
                f"opening tracked-player table {table} has incompatible foreign keys"
            )
        sql_row = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
        ).fetchone()
        if (
            sql_row is None
            or re.search(r"\bWITHOUT\s+ROWID\s*$", str(sql_row[0]), re.IGNORECASE) is None
        ):
            raise OpeningSchemaError(
                f"opening tracked-player table {table} is not an owned WITHOUT ROWID table"
            )


def ensure_tracked_player_schema(
    connection: sqlite3.Connection, wanted: int = TRACKED_PLAYER_SCHEMA_VERSION
) -> None:
    """Create or validate the additive S5 contract without changing neutral facts."""

    connection.execute("PRAGMA foreign_keys = ON")
    names = _table_names(connection)
    missing_required = _REQUIRED_TABLES - names
    if missing_required:
        missing_text = ", ".join(sorted(missing_required))
        raise OpeningSchemaError(
            f"players, accepted corpus, S3, and S4 schemas are required ({missing_text}); "
            "no changes made"
        )
    if "opening_tracked_player_schema" in names:
        try:
            version_row = connection.execute(
                "SELECT version FROM opening_tracked_player_schema WHERE id = 1"
            ).fetchone()
        except sqlite3.Error as error:
            raise OpeningSchemaError(
                "opening tracked-player schema version table is malformed; no changes made"
            ) from error
        if version_row is None:
            raise OpeningSchemaError(
                "opening tracked-player schema has no singleton version row; no changes made"
            )
        if version_row[0] != wanted:
            raise OpeningSchemaError(
                f"incompatible opening tracked-player schema version {version_row[0]}; "
                f"expected {wanted}; no changes made"
            )
        missing = TRACKED_PLAYER_SCHEMA_TABLES - names
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise OpeningSchemaError(
                f"opening tracked-player schema is incomplete ({missing_text}); no changes made"
            )
        _validate_existing_schema(connection)
        return
    if names & TRACKED_PLAYER_SCHEMA_TABLES:
        raise OpeningSchemaError(
            "opening tracked-player objects exist without a version table; no changes made"
        )

    statements = (
        """
        CREATE TABLE opening_tracked_player_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_tracked_player (
            player_uuid TEXT PRIMARY KEY,
            FOREIGN KEY (player_uuid) REFERENCES players(uuid)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_tracked_player_state (
            player_uuid TEXT NOT NULL,
            accepted_manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            accepted_schema_version INTEGER NOT NULL,
            accepted_classification_schema_version INTEGER NOT NULL,
            accepted_recurrence_schema_version INTEGER NOT NULL,
            classification_input_signature TEXT NOT NULL,
            recurrence_input_signature TEXT NOT NULL,
            accepted_at TEXT NOT NULL,
            classification_game_count INTEGER NOT NULL CHECK (classification_game_count >= 0),
            position_projection_count INTEGER NOT NULL CHECK (position_projection_count >= 0),
            route_projection_count INTEGER NOT NULL CHECK (route_projection_count >= 0),
            branch_projection_count INTEGER NOT NULL CHECK (branch_projection_count >= 0),
            route_branch_projection_count INTEGER NOT NULL CHECK (
                route_branch_projection_count >= 0
            ),
            PRIMARY KEY (player_uuid, accepted_manifest_hash, corpus_id),
            FOREIGN KEY (player_uuid) REFERENCES opening_tracked_player(player_uuid),
            FOREIGN KEY (accepted_manifest_hash, corpus_id)
                REFERENCES opening_recurrence_state(accepted_manifest_hash, corpus_id)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_tracked_player_run (
            run_id TEXT PRIMARY KEY,
            player_uuid TEXT NOT NULL,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            schema_version INTEGER NOT NULL,
            classification_schema_version INTEGER NOT NULL,
            recurrence_schema_version INTEGER NOT NULL,
            classification_input_signature TEXT NOT NULL,
            recurrence_input_signature TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('running', 'success', 'failed', 'interrupted')
            ),
            started_at TEXT NOT NULL,
            finished_at TEXT,
            classification_game_count INTEGER NOT NULL CHECK (classification_game_count >= 0),
            position_projection_count INTEGER NOT NULL CHECK (position_projection_count >= 0),
            route_projection_count INTEGER NOT NULL CHECK (route_projection_count >= 0),
            branch_projection_count INTEGER NOT NULL CHECK (branch_projection_count >= 0),
            route_branch_projection_count INTEGER NOT NULL CHECK (
                route_branch_projection_count >= 0
            ),
            details TEXT,
            UNIQUE (player_uuid, manifest_hash, corpus_id, run_id),
            FOREIGN KEY (player_uuid) REFERENCES opening_tracked_player(player_uuid),
            FOREIGN KEY (manifest_hash, corpus_id)
                REFERENCES opening_recurrence_state(accepted_manifest_hash, corpus_id)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_player_classification_game (
            player_uuid TEXT NOT NULL,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            PRIMARY KEY (player_uuid, manifest_hash, corpus_id, game_uuid),
            FOREIGN KEY (player_uuid, manifest_hash, corpus_id)
                REFERENCES opening_tracked_player_state(
                    player_uuid, accepted_manifest_hash, corpus_id
                ),
            FOREIGN KEY (manifest_hash, corpus_id, game_uuid)
                REFERENCES opening_classification_game(manifest_hash, corpus_id, game_uuid)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_player_position_projection (
            player_uuid TEXT NOT NULL,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL CHECK (side_to_move IN ('w', 'b')),
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            color_scope TEXT NOT NULL CHECK (color_scope IN ('overall', 'white', 'black')),
            raw_occurrence_count INTEGER NOT NULL CHECK (raw_occurrence_count >= 0),
            distinct_game_count INTEGER NOT NULL CHECK (distinct_game_count >= 0),
            first_game_sequence INTEGER,
            first_game_uuid TEXT,
            first_ply INTEGER,
            last_game_sequence INTEGER,
            last_game_uuid TEXT,
            last_ply INTEGER,
            PRIMARY KEY (
                player_uuid, manifest_hash, corpus_id, placement, side_to_move,
                castling, en_passant, color_scope
            ),
            FOREIGN KEY (player_uuid, manifest_hash, corpus_id)
                REFERENCES opening_tracked_player_state(
                    player_uuid, accepted_manifest_hash, corpus_id
                ),
            FOREIGN KEY (
                manifest_hash, corpus_id, placement, side_to_move, castling,
                en_passant, color_scope
            ) REFERENCES opening_recurrence_position_projection(
                manifest_hash, corpus_id, placement, side_to_move, castling,
                en_passant, color_scope
            )
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_player_route_projection (
            player_uuid TEXT NOT NULL,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            anchor_ply INTEGER NOT NULL CHECK (anchor_ply > 0),
            source_file TEXT NOT NULL,
            source_row_ordinal INTEGER NOT NULL CHECK (source_row_ordinal > 0),
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL CHECK (side_to_move IN ('w', 'b')),
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            color_scope TEXT NOT NULL CHECK (color_scope IN ('overall', 'white', 'black')),
            raw_occurrence_count INTEGER NOT NULL CHECK (raw_occurrence_count >= 0),
            distinct_game_count INTEGER NOT NULL CHECK (distinct_game_count >= 0),
            first_game_sequence INTEGER,
            first_game_uuid TEXT,
            first_route_ply INTEGER,
            last_game_sequence INTEGER,
            last_game_uuid TEXT,
            last_route_ply INTEGER,
            PRIMARY KEY (
                player_uuid, manifest_hash, corpus_id, anchor_ply, source_file,
                source_row_ordinal, placement, side_to_move, castling, en_passant, color_scope
            ),
            FOREIGN KEY (player_uuid, manifest_hash, corpus_id)
                REFERENCES opening_tracked_player_state(
                    player_uuid, accepted_manifest_hash, corpus_id
                ),
            FOREIGN KEY (
                manifest_hash, corpus_id, anchor_ply, source_file, source_row_ordinal,
                placement, side_to_move, castling, en_passant, color_scope
            ) REFERENCES opening_recurrence_route_projection(
                manifest_hash, corpus_id, anchor_ply, source_file, source_row_ordinal,
                placement, side_to_move, castling, en_passant, color_scope
            )
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_player_branch_projection (
            player_uuid TEXT NOT NULL,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            parent_placement TEXT NOT NULL,
            parent_side_to_move TEXT NOT NULL CHECK (parent_side_to_move IN ('w', 'b')),
            parent_castling TEXT NOT NULL,
            parent_en_passant TEXT NOT NULL,
            branch_kind TEXT NOT NULL CHECK (branch_kind IN ('move', 'terminal')),
            child_uci TEXT NOT NULL,
            color_scope TEXT NOT NULL CHECK (color_scope IN ('overall', 'white', 'black')),
            raw_event_count INTEGER NOT NULL CHECK (raw_event_count >= 0),
            distinct_game_count INTEGER NOT NULL CHECK (distinct_game_count >= 0),
            first_game_sequence INTEGER,
            first_game_uuid TEXT,
            first_parent_ply INTEGER,
            last_game_sequence INTEGER,
            last_game_uuid TEXT,
            last_parent_ply INTEGER,
            PRIMARY KEY (
                player_uuid, manifest_hash, corpus_id, parent_placement, parent_side_to_move,
                parent_castling, parent_en_passant, branch_kind, child_uci, color_scope
            ),
            FOREIGN KEY (player_uuid, manifest_hash, corpus_id)
                REFERENCES opening_tracked_player_state(
                    player_uuid, accepted_manifest_hash, corpus_id
                ),
            FOREIGN KEY (
                manifest_hash, corpus_id, parent_placement, parent_side_to_move,
                parent_castling, parent_en_passant, branch_kind, child_uci, color_scope
            ) REFERENCES opening_recurrence_branch_projection(
                manifest_hash, corpus_id, parent_placement, parent_side_to_move,
                parent_castling, parent_en_passant, branch_kind, child_uci, color_scope
            )
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_player_route_branch_projection (
            player_uuid TEXT NOT NULL,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            anchor_ply INTEGER NOT NULL CHECK (anchor_ply > 0),
            source_file TEXT NOT NULL,
            source_row_ordinal INTEGER NOT NULL CHECK (source_row_ordinal > 0),
            parent_placement TEXT NOT NULL,
            parent_side_to_move TEXT NOT NULL CHECK (parent_side_to_move IN ('w', 'b')),
            parent_castling TEXT NOT NULL,
            parent_en_passant TEXT NOT NULL,
            branch_kind TEXT NOT NULL CHECK (branch_kind IN ('move', 'terminal')),
            child_uci TEXT NOT NULL,
            color_scope TEXT NOT NULL CHECK (color_scope IN ('overall', 'white', 'black')),
            raw_event_count INTEGER NOT NULL CHECK (raw_event_count >= 0),
            distinct_game_count INTEGER NOT NULL CHECK (distinct_game_count >= 0),
            first_game_sequence INTEGER,
            first_game_uuid TEXT,
            first_parent_ply INTEGER,
            last_game_sequence INTEGER,
            last_game_uuid TEXT,
            last_parent_ply INTEGER,
            PRIMARY KEY (
                player_uuid, manifest_hash, corpus_id, anchor_ply, source_file,
                source_row_ordinal, parent_placement, parent_side_to_move, parent_castling,
                parent_en_passant, branch_kind, child_uci, color_scope
            ),
            FOREIGN KEY (player_uuid, manifest_hash, corpus_id)
                REFERENCES opening_tracked_player_state(
                    player_uuid, accepted_manifest_hash, corpus_id
                ),
            FOREIGN KEY (
                manifest_hash, corpus_id, anchor_ply, source_file, source_row_ordinal,
                parent_placement, parent_side_to_move, parent_castling, parent_en_passant,
                branch_kind, child_uci, color_scope
            ) REFERENCES opening_recurrence_route_branch_projection(
                manifest_hash, corpus_id, anchor_ply, source_file, source_row_ordinal,
                parent_placement, parent_side_to_move, parent_castling, parent_en_passant,
                branch_kind, child_uci, color_scope
            )
        ) WITHOUT ROWID
        """,
    )
    with connection:
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO opening_tracked_player_schema (id, version) VALUES (1, ?)",
            (wanted,),
        )
