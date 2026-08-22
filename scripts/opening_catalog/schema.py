"""Versioned SQLite schema for the opening-owned catalog."""

from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1
RELATIONSHIP_SCHEMA_VERSION = 1

SCHEMA_TABLES = {
    "opening_catalog_schema",
    "opening_source_manifest",
    "opening_source_file",
    "opening_import_run",
    "opening_catalog_state",
    "opening_catalog",
}

RELATIONSHIP_SCHEMA_TABLES = {
    "opening_relationship_schema",
    "opening_relationship_state",
    "opening_relationship_run",
    "opening_relationship_position",
    "opening_position_membership",
    "opening_parent_link",
    "opening_transposition_link",
}


class OpeningSchemaError(RuntimeError):
    """The opening catalog schema is missing or incompatible."""


def _table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def ensure_schema(connection: sqlite3.Connection, wanted: int = SCHEMA_VERSION) -> None:
    """Create the opening-owned schema or refuse an incompatible one."""

    connection.execute("PRAGMA foreign_keys = ON")
    names = _table_names(connection)
    if "opening_catalog_schema" in names:
        version_row = connection.execute(
            "SELECT version FROM opening_catalog_schema WHERE id = 1"
        ).fetchone()
        if version_row is None:
            raise OpeningSchemaError(
                "opening catalog schema has no singleton version row; no changes made"
            )
        if version_row[0] != wanted:
            raise OpeningSchemaError(
                f"incompatible opening catalog schema version {version_row[0]}; "
                f"expected {wanted}; no changes made"
            )
        missing = SCHEMA_TABLES - names
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise OpeningSchemaError(
                f"opening catalog schema is incomplete ({missing_text}); no changes made"
            )
        return

    if names & SCHEMA_TABLES:
        raise OpeningSchemaError(
            "opening catalog objects exist without a version table; no changes made"
        )

    statements = (
        """
        CREATE TABLE opening_catalog_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE opening_source_manifest (
            manifest_hash TEXT PRIMARY KEY,
            source_dataset TEXT NOT NULL,
            file_count INTEGER NOT NULL CHECK (file_count = 5),
            record_count INTEGER NOT NULL CHECK (record_count >= 0),
            created_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE opening_source_file (
            manifest_hash TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_file_hash TEXT NOT NULL,
            record_count INTEGER NOT NULL CHECK (record_count >= 0),
            PRIMARY KEY (manifest_hash, source_file),
            FOREIGN KEY (manifest_hash) REFERENCES opening_source_manifest(manifest_hash)
        )
        """,
        """
        CREATE TABLE opening_import_run (
            run_id TEXT PRIMARY KEY,
            manifest_hash TEXT NOT NULL,
            schema_version INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed', 'interrupted')),
            started_at TEXT NOT NULL,
            finished_at TEXT,
            record_count INTEGER NOT NULL DEFAULT 0,
            details TEXT,
            FOREIGN KEY (manifest_hash) REFERENCES opening_source_manifest(manifest_hash)
        )
        """,
        """
        CREATE TABLE opening_catalog_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            accepted_manifest_hash TEXT NOT NULL,
            accepted_schema_version INTEGER NOT NULL,
            accepted_at TEXT NOT NULL,
            record_count INTEGER NOT NULL,
            FOREIGN KEY (accepted_manifest_hash) REFERENCES opening_source_manifest(manifest_hash)
        )
        """,
        """
        CREATE TABLE opening_catalog (
            manifest_hash TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_row_ordinal INTEGER NOT NULL CHECK (source_row_ordinal > 0),
            source_row_hash TEXT NOT NULL,
            eco TEXT NOT NULL,
            name TEXT NOT NULL,
            move_sequence TEXT NOT NULL,
            endpoint_fen TEXT NOT NULL,
            endpoint_placement TEXT NOT NULL,
            endpoint_side_to_move TEXT NOT NULL,
            endpoint_castling TEXT NOT NULL,
            endpoint_en_passant TEXT NOT NULL,
            endpoint_halfmove_clock INTEGER NOT NULL,
            endpoint_fullmove_number INTEGER NOT NULL,
            PRIMARY KEY (manifest_hash, source_file, source_row_ordinal),
            FOREIGN KEY (manifest_hash, source_file)
                REFERENCES opening_source_file(manifest_hash, source_file)
        )
        """,
        """
        CREATE INDEX opening_catalog_endpoint_idx
            ON opening_catalog(
                endpoint_placement,
                endpoint_side_to_move,
                endpoint_castling,
                endpoint_en_passant
            )
        """,
        "CREATE INDEX opening_import_run_manifest_idx ON opening_import_run(manifest_hash)",
    )

    with connection:
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO opening_catalog_schema (id, version, applied_at) "
            "VALUES (1, ?, datetime('now'))",
            (wanted,),
        )


def ensure_relationship_schema(
    connection: sqlite3.Connection, wanted: int = RELATIONSHIP_SCHEMA_VERSION
) -> None:
    """Create or validate the additive, manifest-scoped relationship schema."""

    connection.execute("PRAGMA foreign_keys = ON")
    names = _table_names(connection)
    if "opening_relationship_schema" in names:
        version_row = connection.execute(
            "SELECT version FROM opening_relationship_schema WHERE id = 1"
        ).fetchone()
        if version_row is None:
            raise OpeningSchemaError(
                "opening relationship schema has no singleton version row; no changes made"
            )
        if version_row[0] != wanted:
            raise OpeningSchemaError(
                f"incompatible opening relationship schema version {version_row[0]}; "
                f"expected {wanted}; no changes made"
            )
        missing = RELATIONSHIP_SCHEMA_TABLES - names
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise OpeningSchemaError(
                f"opening relationship schema is incomplete ({missing_text}); no changes made"
            )
        return

    if names & RELATIONSHIP_SCHEMA_TABLES:
        raise OpeningSchemaError(
            "opening relationship objects exist without a version table; no changes made"
        )

    statements = (
        """
        CREATE TABLE opening_relationship_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_relationship_state (
            accepted_manifest_hash TEXT PRIMARY KEY,
            accepted_schema_version INTEGER NOT NULL,
            record_count INTEGER NOT NULL CHECK (record_count >= 0),
            position_count INTEGER NOT NULL CHECK (position_count >= 0),
            membership_count INTEGER NOT NULL CHECK (membership_count >= 0),
            parent_link_count INTEGER NOT NULL CHECK (parent_link_count >= 0),
            transposition_link_count INTEGER NOT NULL CHECK (transposition_link_count >= 0),
            FOREIGN KEY (accepted_manifest_hash)
                REFERENCES opening_source_manifest(manifest_hash)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_relationship_run (
            run_id TEXT PRIMARY KEY,
            manifest_hash TEXT NOT NULL UNIQUE,
            schema_version INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('running', 'success')),
            record_count INTEGER NOT NULL CHECK (record_count >= 0),
            position_count INTEGER NOT NULL CHECK (position_count >= 0),
            membership_count INTEGER NOT NULL CHECK (membership_count >= 0),
            parent_link_count INTEGER NOT NULL CHECK (parent_link_count >= 0),
            transposition_link_count INTEGER NOT NULL CHECK (transposition_link_count >= 0),
            details TEXT,
            FOREIGN KEY (manifest_hash) REFERENCES opening_source_manifest(manifest_hash)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_relationship_position (
            manifest_hash TEXT NOT NULL,
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL,
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            PRIMARY KEY (
                manifest_hash,
                placement,
                side_to_move,
                castling,
                en_passant
            ),
            FOREIGN KEY (manifest_hash)
                REFERENCES opening_source_manifest(manifest_hash)
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_position_membership (
            manifest_hash TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_row_ordinal INTEGER NOT NULL,
            ply INTEGER NOT NULL CHECK (ply > 0),
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL,
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            uci TEXT NOT NULL,
            san TEXT NOT NULL,
            uci_prefix TEXT NOT NULL,
            PRIMARY KEY (manifest_hash, source_file, source_row_ordinal, ply),
            FOREIGN KEY (manifest_hash, source_file, source_row_ordinal)
                REFERENCES opening_catalog(manifest_hash, source_file, source_row_ordinal),
            FOREIGN KEY (
                manifest_hash,
                placement,
                side_to_move,
                castling,
                en_passant
            ) REFERENCES opening_relationship_position(
                manifest_hash,
                placement,
                side_to_move,
                castling,
                en_passant
            )
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_parent_link (
            manifest_hash TEXT NOT NULL,
            child_source_file TEXT NOT NULL,
            child_source_row_ordinal INTEGER NOT NULL,
            child_ply INTEGER NOT NULL CHECK (child_ply > 0),
            parent_source_file TEXT NOT NULL,
            parent_source_row_ordinal INTEGER NOT NULL,
            PRIMARY KEY (
                manifest_hash,
                child_source_file,
                child_source_row_ordinal,
                child_ply,
                parent_source_file,
                parent_source_row_ordinal
            ),
            FOREIGN KEY (manifest_hash, child_source_file, child_source_row_ordinal)
                REFERENCES opening_catalog(manifest_hash, source_file, source_row_ordinal),
            FOREIGN KEY (manifest_hash, parent_source_file, parent_source_row_ordinal)
                REFERENCES opening_catalog(manifest_hash, source_file, source_row_ordinal),
            FOREIGN KEY (manifest_hash, child_source_file, child_source_row_ordinal, child_ply)
                REFERENCES opening_position_membership(
                    manifest_hash, source_file, source_row_ordinal, ply
                )
        ) WITHOUT ROWID
        """,
        """
        CREATE TABLE opening_transposition_link (
            manifest_hash TEXT NOT NULL,
            placement TEXT NOT NULL,
            side_to_move TEXT NOT NULL,
            castling TEXT NOT NULL,
            en_passant TEXT NOT NULL,
            source_file_a TEXT NOT NULL,
            source_row_ordinal_a INTEGER NOT NULL,
            ply_a INTEGER NOT NULL CHECK (ply_a > 0),
            uci_prefix_a TEXT NOT NULL,
            source_file_b TEXT NOT NULL,
            source_row_ordinal_b INTEGER NOT NULL,
            ply_b INTEGER NOT NULL CHECK (ply_b > 0),
            uci_prefix_b TEXT NOT NULL,
            PRIMARY KEY (
                manifest_hash,
                placement,
                side_to_move,
                castling,
                en_passant,
                source_file_a,
                source_row_ordinal_a,
                ply_a,
                source_file_b,
                source_row_ordinal_b,
                ply_b
            ),
            CHECK (
                source_file_a < source_file_b OR (
                    source_file_a = source_file_b
                    AND source_row_ordinal_a < source_row_ordinal_b
                )
            ),
            CHECK (uci_prefix_a <> uci_prefix_b),
            FOREIGN KEY (
                manifest_hash,
                placement,
                side_to_move,
                castling,
                en_passant
            ) REFERENCES opening_relationship_position(
                manifest_hash,
                placement,
                side_to_move,
                castling,
                en_passant
            ),
            FOREIGN KEY (manifest_hash, source_file_a, source_row_ordinal_a, ply_a)
                REFERENCES opening_position_membership(
                    manifest_hash, source_file, source_row_ordinal, ply
                ),
            FOREIGN KEY (manifest_hash, source_file_b, source_row_ordinal_b, ply_b)
                REFERENCES opening_position_membership(
                    manifest_hash, source_file, source_row_ordinal, ply
                )
        ) WITHOUT ROWID
        """,
        """
        CREATE INDEX opening_position_membership_position_idx
            ON opening_position_membership(
                manifest_hash, placement, side_to_move, castling, en_passant
            )
        """,
        """
        CREATE INDEX opening_parent_link_parent_idx
            ON opening_parent_link(manifest_hash, parent_source_file, parent_source_row_ordinal)
        """,
        """
        CREATE INDEX opening_transposition_link_position_idx
            ON opening_transposition_link(
                manifest_hash, placement, side_to_move, castling, en_passant
            )
        """,
    )

    with connection:
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO opening_relationship_schema (id, version) VALUES (1, ?)",
            (wanted,),
        )
