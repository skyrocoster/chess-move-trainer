"""Versioned additive SQLite schema for authoritative S4 recurrence facts.

The schema is a contract gate only.  It creates no facts and performs no
derivation.  All S4 tables are additive, manifest/corpus scoped, and use
natural composite keys with ``WITHOUT ROWID``.  Projection count columns are
raw occurrence/event counts and distinct-game counts kept separately; no rate,
share, threshold, weight, priority, or frontier column is defined here.
"""

from __future__ import annotations

import sqlite3

from .classification_schema import CLASSIFICATION_SCHEMA_TABLES
from .schema import (
    RELATIONSHIP_SCHEMA_TABLES,
    SCHEMA_TABLES,
    OpeningSchemaError,
    _table_names,
)

RECURRENCE_SCHEMA_VERSION = 1

RECURRENCE_SCHEMA_TABLES = {
    "opening_recurrence_schema",
    "opening_recurrence_state",
    "opening_recurrence_run",
    "opening_recurrence_game",
    "opening_recurrence_occurrence",
    "opening_recurrence_route_event",
    "opening_recurrence_branch_event",
    "opening_recurrence_position_projection",
    "opening_recurrence_route_projection",
    "opening_recurrence_branch_projection",
    "opening_recurrence_route_branch_projection",
}

_CORPUS_TABLES = {
    "corpus_schema",
    "corpus",
    "corpus_game",
    "position_state",
    "position_occurrence",
}
_REQUIRED_TABLES = (
    SCHEMA_TABLES | RELATIONSHIP_SCHEMA_TABLES | CLASSIFICATION_SCHEMA_TABLES | _CORPUS_TABLES
)


def ensure_recurrence_schema(
    connection: sqlite3.Connection, wanted: int = RECURRENCE_SCHEMA_VERSION
) -> None:
    """Create or validate the additive S4 contract without changing upstream facts."""

    connection.execute("PRAGMA foreign_keys = ON")
    names = _table_names(connection)
    missing_required = _REQUIRED_TABLES - names
    if missing_required:
        missing_text = ", ".join(sorted(missing_required))
        raise OpeningSchemaError(
            f"S1, S2, S3, and accepted corpus schemas are required ({missing_text}); "
            "no changes made"
        )

    if "opening_recurrence_schema" in names:
        version_row = connection.execute(
            "SELECT version FROM opening_recurrence_schema WHERE id = 1"
        ).fetchone()
        if version_row is None:
            raise OpeningSchemaError(
                "opening recurrence schema has no singleton version row; no changes made"
            )
        if version_row[0] != wanted:
            raise OpeningSchemaError(
                f"incompatible opening recurrence schema version {version_row[0]}; "
                f"expected {wanted}; no changes made"
            )
        missing = RECURRENCE_SCHEMA_TABLES - names
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise OpeningSchemaError(
                f"opening recurrence schema is incomplete ({missing_text}); no changes made"
            )
        return

    if names & RECURRENCE_SCHEMA_TABLES:
        raise OpeningSchemaError(
            "opening recurrence objects exist without a version table; no changes made"
        )

    statements = (
        """
        CREATE TABLE opening_recurrence_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_state (
            accepted_manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            accepted_schema_version INTEGER NOT NULL,
            accepted_classification_schema_version INTEGER NOT NULL,
            accepted_catalog_schema_version INTEGER NOT NULL,
            accepted_relationship_schema_version INTEGER NOT NULL,
            accepted_corpus_schema_version INTEGER NOT NULL,
            classification_input_signature TEXT NOT NULL,
            corpus_input_signature TEXT NOT NULL,
            game_metadata_input_signature TEXT NOT NULL,
            accepted_at TEXT NOT NULL,
            game_count INTEGER NOT NULL CHECK (game_count >= 0),
            occurrence_count INTEGER NOT NULL CHECK (occurrence_count >= 0),
            route_event_count INTEGER NOT NULL CHECK (route_event_count >= 0),
            branch_event_count INTEGER NOT NULL CHECK (branch_event_count >= 0),
            PRIMARY KEY (accepted_manifest_hash, corpus_id),
            FOREIGN KEY (accepted_manifest_hash)
                REFERENCES opening_source_manifest(manifest_hash),
            FOREIGN KEY (accepted_manifest_hash)
                REFERENCES opening_relationship_state(accepted_manifest_hash),
            FOREIGN KEY (accepted_manifest_hash, corpus_id)
                REFERENCES opening_classification_state(accepted_manifest_hash, corpus_id),
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_run (
            run_id TEXT PRIMARY KEY,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            schema_version INTEGER NOT NULL,
            classification_schema_version INTEGER NOT NULL,
            catalog_schema_version INTEGER NOT NULL,
            relationship_schema_version INTEGER NOT NULL,
            corpus_schema_version INTEGER NOT NULL,
            classification_input_signature TEXT NOT NULL,
            corpus_input_signature TEXT NOT NULL,
            game_metadata_input_signature TEXT NOT NULL,
            status TEXT NOT NULL CHECK (
                status IN ('running', 'success', 'failed', 'interrupted')
            ),
            started_at TEXT NOT NULL,
            finished_at TEXT,
            game_count INTEGER NOT NULL CHECK (game_count >= 0),
            occurrence_count INTEGER NOT NULL CHECK (occurrence_count >= 0),
            route_event_count INTEGER NOT NULL CHECK (route_event_count >= 0),
            branch_event_count INTEGER NOT NULL CHECK (branch_event_count >= 0),
            details TEXT,
            UNIQUE (manifest_hash, corpus_id, run_id),
            FOREIGN KEY (manifest_hash, corpus_id)
                REFERENCES opening_classification_state(accepted_manifest_hash, corpus_id),
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_game (
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            source_fingerprint TEXT NOT NULL,
            metadata_fingerprint TEXT NOT NULL,
            game_sequence INTEGER NOT NULL CHECK (game_sequence > 0),
            game_color TEXT NOT NULL DEFAULT 'white' CHECK (game_color IN ('white', 'black')),
            end_time INTEGER,
            year INTEGER,
            month INTEGER,
            time_control TEXT,
            time_class TEXT,
            white_rating INTEGER,
            black_rating INTEGER,
            white_result TEXT,
            black_result TEXT,
            PRIMARY KEY (manifest_hash, corpus_id, game_uuid),
            UNIQUE (manifest_hash, corpus_id, game_sequence),
            FOREIGN KEY (manifest_hash, corpus_id, game_uuid)
                REFERENCES opening_classification_game(manifest_hash, corpus_id, game_uuid),
            FOREIGN KEY (corpus_id, game_uuid)
                REFERENCES corpus_game(corpus_id, game_uuid)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_occurrence (
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            ply INTEGER NOT NULL CHECK (ply >= 0),
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL CHECK (side_to_move IN ('w', 'b')),
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            san TEXT,
            uci TEXT,
            halfmove_clock INTEGER NOT NULL CHECK (halfmove_clock >= 0),
            fullmove_number INTEGER NOT NULL CHECK (fullmove_number >= 1),
            PRIMARY KEY (manifest_hash, corpus_id, game_uuid, ply),
            FOREIGN KEY (manifest_hash, corpus_id, game_uuid)
                REFERENCES opening_recurrence_game(manifest_hash, corpus_id, game_uuid),
            FOREIGN KEY (game_uuid, ply) REFERENCES position_occurrence(game_uuid, ply),
            FOREIGN KEY (placement, side_to_move, castling, en_passant)
                REFERENCES position_state(placement, side_to_move, castling, en_passant)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_route_event (
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            anchor_ply INTEGER NOT NULL CHECK (anchor_ply > 0),
            source_file TEXT NOT NULL,
            source_row_ordinal INTEGER NOT NULL CHECK (source_row_ordinal > 0),
            route_ply INTEGER NOT NULL CHECK (route_ply >= anchor_ply),
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL CHECK (side_to_move IN ('w', 'b')),
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            san TEXT NOT NULL,
            uci TEXT NOT NULL,
            halfmove_clock INTEGER NOT NULL CHECK (halfmove_clock >= 0),
            fullmove_number INTEGER NOT NULL CHECK (fullmove_number >= 1),
            PRIMARY KEY (
                manifest_hash, corpus_id, game_uuid, anchor_ply,
                source_file, source_row_ordinal, route_ply
            ),
            FOREIGN KEY (
                manifest_hash, corpus_id, game_uuid, anchor_ply,
                source_file, source_row_ordinal, route_ply
            ) REFERENCES opening_classification_route(
                manifest_hash, corpus_id, game_uuid, anchor_ply,
                source_file, source_row_ordinal, route_ply
            ),
            FOREIGN KEY (manifest_hash, corpus_id, game_uuid, route_ply)
                REFERENCES opening_recurrence_occurrence(manifest_hash, corpus_id, game_uuid, ply)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_branch_event (
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            parent_ply INTEGER NOT NULL CHECK (parent_ply >= 0),
            parent_placement TEXT NOT NULL,
            parent_side_to_move TEXT NOT NULL CHECK (parent_side_to_move IN ('w', 'b')),
            parent_castling TEXT NOT NULL,
            parent_en_passant TEXT NOT NULL,
            branch_kind TEXT NOT NULL CHECK (branch_kind IN ('move', 'terminal')),
            child_ply INTEGER NOT NULL CHECK (child_ply >= parent_ply),
            child_placement TEXT,
            child_side_to_move TEXT CHECK (child_side_to_move IN ('w', 'b')),
            child_castling TEXT,
            child_en_passant TEXT,
            child_san TEXT,
            child_uci TEXT,
            terminal_outcome TEXT,
            PRIMARY KEY (manifest_hash, corpus_id, game_uuid, parent_ply, branch_kind),
            CHECK (
                (branch_kind = 'move' AND child_ply = parent_ply + 1 AND child_uci IS NOT NULL)
                OR (branch_kind = 'terminal' AND child_ply = parent_ply AND child_uci IS NULL)
            ),
            FOREIGN KEY (manifest_hash, corpus_id, game_uuid, parent_ply)
                REFERENCES opening_recurrence_occurrence(manifest_hash, corpus_id, game_uuid, ply),
            FOREIGN KEY (manifest_hash, corpus_id, game_uuid, child_ply)
                REFERENCES opening_recurrence_occurrence(manifest_hash, corpus_id, game_uuid, ply)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_position_projection (
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
                manifest_hash, corpus_id, placement, side_to_move, castling,
                en_passant, color_scope
            ),
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_route_projection (
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
                manifest_hash, corpus_id, anchor_ply, source_file, source_row_ordinal,
                placement, side_to_move, castling, en_passant, color_scope
            ),
            FOREIGN KEY (manifest_hash, source_file, source_row_ordinal)
                REFERENCES opening_catalog(manifest_hash, source_file, source_row_ordinal)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_branch_projection (
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
                manifest_hash, corpus_id, parent_placement, parent_side_to_move,
                parent_castling, parent_en_passant, branch_kind, child_uci, color_scope
            ),
             FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id),
            CHECK (
                (branch_kind = 'move' AND child_uci <> '')
                OR (branch_kind = 'terminal' AND child_uci = '')
            )
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_recurrence_route_branch_projection (
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
                manifest_hash, corpus_id, anchor_ply, source_file, source_row_ordinal,
                parent_placement, parent_side_to_move, parent_castling, parent_en_passant,
                branch_kind, child_uci, color_scope
            ),
            FOREIGN KEY (manifest_hash, source_file, source_row_ordinal)
                REFERENCES opening_catalog(manifest_hash, source_file, source_row_ordinal),
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id),
            CHECK (
                (branch_kind = 'move' AND child_uci <> '')
                OR (branch_kind = 'terminal' AND child_uci = '')
            )
        ) WITHOUT ROWID
        """,
        "CREATE INDEX opening_recurrence_occurrence_position_idx ON opening_recurrence_occurrence("
        "manifest_hash, corpus_id, placement, side_to_move, castling, en_passant)",
        "CREATE INDEX opening_recurrence_route_event_position_idx "
        "ON opening_recurrence_route_event("
        "manifest_hash, corpus_id, placement, side_to_move, castling, en_passant)",
        "CREATE INDEX opening_recurrence_branch_event_parent_idx "
        "ON opening_recurrence_branch_event("
        "manifest_hash, corpus_id, parent_placement, parent_side_to_move, parent_castling, "
        "parent_en_passant)",
    )

    with connection:
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO opening_recurrence_schema (id, version) VALUES (1, ?)",
            (wanted,),
        )
