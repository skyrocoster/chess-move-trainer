"""Versioned additive SQLite schema for neutral opening classification."""

from __future__ import annotations

import sqlite3

from .schema import (
    RELATIONSHIP_SCHEMA_TABLES,
    SCHEMA_TABLES,
    OpeningSchemaError,
    _table_names,
)

CLASSIFICATION_SCHEMA_VERSION = 1

CLASSIFICATION_SCHEMA_TABLES = {
    "opening_classification_schema",
    "opening_classification_state",
    "opening_classification_run",
    "opening_classification_game",
    "opening_classification_anchor",
    "opening_classification_route",
}


def ensure_classification_schema(
    connection: sqlite3.Connection, wanted: int = CLASSIFICATION_SCHEMA_VERSION
) -> None:
    """Create or validate the additive, neutral classification contract.

    The schema references the accepted opening catalog, relationship state, and game
    corpus but never creates or owns game-derived position rows.
    """

    connection.execute("PRAGMA foreign_keys = ON")
    names = _table_names(connection)
    required = (
        SCHEMA_TABLES
        | RELATIONSHIP_SCHEMA_TABLES
        | {
            "corpus",
            "corpus_game",
            "position_state",
            "position_occurrence",
        }
    )
    missing_required = required - names
    if missing_required:
        missing_text = ", ".join(sorted(missing_required))
        raise OpeningSchemaError(
            f"S1, S2, and accepted corpus schemas are required ({missing_text}); no changes made"
        )

    if "opening_classification_schema" in names:
        version_row = connection.execute(
            "SELECT version FROM opening_classification_schema WHERE id = 1"
        ).fetchone()
        if version_row is None:
            raise OpeningSchemaError(
                "opening classification schema has no singleton version row; no changes made"
            )
        if version_row[0] != wanted:
            raise OpeningSchemaError(
                f"incompatible opening classification schema version {version_row[0]}; "
                f"expected {wanted}; no changes made"
            )
        missing = CLASSIFICATION_SCHEMA_TABLES - names
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise OpeningSchemaError(
                f"opening classification schema is incomplete ({missing_text}); no changes made"
            )
        return

    if names & CLASSIFICATION_SCHEMA_TABLES:
        raise OpeningSchemaError(
            "opening classification objects exist without a version table; no changes made"
        )

    statements = (
        """
        CREATE TABLE opening_classification_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_classification_state (
            accepted_manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            accepted_schema_version INTEGER NOT NULL,
            accepted_catalog_schema_version INTEGER NOT NULL,
            accepted_relationship_schema_version INTEGER NOT NULL,
            accepted_at TEXT NOT NULL,
            PRIMARY KEY (accepted_manifest_hash, corpus_id),
            FOREIGN KEY (accepted_manifest_hash)
                REFERENCES opening_source_manifest(manifest_hash),
            FOREIGN KEY (accepted_manifest_hash)
                REFERENCES opening_relationship_state(accepted_manifest_hash),
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_classification_run (
            run_id TEXT PRIMARY KEY,
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            schema_version INTEGER NOT NULL,
            catalog_schema_version INTEGER NOT NULL,
            relationship_schema_version INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (
            status IN ('running', 'success', 'failed', 'interrupted')
            ),
            started_at TEXT NOT NULL,
            finished_at TEXT,
            details TEXT,
            UNIQUE (manifest_hash, corpus_id),
            FOREIGN KEY (manifest_hash) REFERENCES opening_source_manifest(manifest_hash),
            FOREIGN KEY (manifest_hash)
                REFERENCES opening_relationship_state(accepted_manifest_hash),
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_classification_game (
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            source_fingerprint TEXT NOT NULL,
            PRIMARY KEY (manifest_hash, corpus_id, game_uuid),
            FOREIGN KEY (manifest_hash) REFERENCES opening_source_manifest(manifest_hash),
            FOREIGN KEY (corpus_id, game_uuid) REFERENCES corpus_game(corpus_id, game_uuid)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_classification_anchor (
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            anchor_ply INTEGER NOT NULL CHECK (anchor_ply > 0),
            source_file TEXT NOT NULL,
            source_row_ordinal INTEGER NOT NULL CHECK (source_row_ordinal > 0),
            anchor_placement TEXT NOT NULL,
            anchor_side_to_move TEXT NOT NULL,
            anchor_castling TEXT NOT NULL,
            anchor_en_passant TEXT NOT NULL,
            anchor_san TEXT NOT NULL,
            anchor_uci TEXT NOT NULL,
            PRIMARY KEY (
                manifest_hash,
                corpus_id,
                game_uuid,
                anchor_ply,
                source_file,
                source_row_ordinal
            ),
            FOREIGN KEY (manifest_hash, corpus_id, game_uuid)
                REFERENCES opening_classification_game(manifest_hash, corpus_id, game_uuid),
            FOREIGN KEY (manifest_hash, source_file, source_row_ordinal)
                REFERENCES opening_catalog(manifest_hash, source_file, source_row_ordinal),
            FOREIGN KEY (game_uuid, anchor_ply)
                REFERENCES position_occurrence(game_uuid, ply)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_classification_route (
            manifest_hash TEXT NOT NULL,
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            anchor_ply INTEGER NOT NULL,
            source_file TEXT NOT NULL,
            source_row_ordinal INTEGER NOT NULL,
            route_ply INTEGER NOT NULL CHECK (route_ply >= anchor_ply),
            route_placement TEXT NOT NULL,
            route_side_to_move TEXT NOT NULL,
            route_castling TEXT NOT NULL,
            route_en_passant TEXT NOT NULL,
            route_san TEXT NOT NULL,
            route_uci TEXT NOT NULL,
            route_halfmove_clock INTEGER NOT NULL,
            route_fullmove_number INTEGER NOT NULL,
            PRIMARY KEY (
                manifest_hash,
                corpus_id,
                game_uuid,
                anchor_ply,
                source_file,
                source_row_ordinal,
                route_ply
            ),
            FOREIGN KEY (
                manifest_hash,
                corpus_id,
                game_uuid,
                anchor_ply,
                source_file,
                source_row_ordinal
            ) REFERENCES opening_classification_anchor(
                manifest_hash,
                corpus_id,
                game_uuid,
                anchor_ply,
                source_file,
                source_row_ordinal
            ),
            FOREIGN KEY (game_uuid, route_ply)
                REFERENCES position_occurrence(game_uuid, ply)
        ) WITHOUT ROWID
        """,
        """
        CREATE INDEX opening_classification_anchor_position_idx
            ON opening_classification_anchor(
                manifest_hash,
                anchor_placement,
                anchor_side_to_move,
                anchor_castling,
                anchor_en_passant
            )
        """,
        """
        CREATE INDEX opening_classification_route_game_idx
            ON opening_classification_route(manifest_hash, corpus_id, game_uuid, route_ply)
        """,
    )

    with connection:
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO opening_classification_schema (id, version) VALUES (1, ?)",
            (wanted,),
        )
