"""SQLite schema validation for the opening Line Library read adapter."""

from __future__ import annotations

import sqlite3

from scripts.opening_catalog.recurrence_schema import RECURRENCE_SCHEMA_VERSION
from scripts.opening_catalog.schema import RELATIONSHIP_SCHEMA_VERSION, SCHEMA_VERSION

from .errors import OpeningLineLibraryUnavailableError

CORPUS_SCHEMA_VERSION = 1

_REQUIRED_COLUMNS = {
    "corpus_schema": ("id", "version"),
    "corpus": ("corpus_id", "subject_player_uuid"),
    "opening_catalog_schema": ("id", "version"),
    "opening_catalog_state": (
        "id",
        "accepted_manifest_hash",
        "accepted_schema_version",
        "record_count",
    ),
    "opening_catalog": (
        "manifest_hash",
        "source_file",
        "source_row_ordinal",
        "eco",
        "name",
        "move_sequence",
    ),
    "opening_relationship_schema": ("id", "version"),
    "opening_relationship_state": ("accepted_manifest_hash", "accepted_schema_version"),
    "opening_parent_link": (
        "manifest_hash",
        "child_source_file",
        "child_source_row_ordinal",
        "child_ply",
        "parent_source_file",
        "parent_source_row_ordinal",
    ),
    "opening_position_membership": (
        "manifest_hash",
        "source_file",
        "source_row_ordinal",
        "ply",
        "placement",
        "side_to_move",
        "castling",
        "en_passant",
        "uci_prefix",
    ),
    "opening_transposition_link": (
        "manifest_hash",
        "placement",
        "side_to_move",
        "castling",
        "en_passant",
        "source_file_a",
        "source_row_ordinal_a",
        "ply_a",
        "uci_prefix_a",
        "source_file_b",
        "source_row_ordinal_b",
        "ply_b",
        "uci_prefix_b",
    ),
    "opening_recurrence_schema": ("id", "version"),
    "opening_recurrence_state": (
        "accepted_manifest_hash",
        "corpus_id",
        "accepted_schema_version",
        "accepted_classification_schema_version",
        "accepted_catalog_schema_version",
        "accepted_relationship_schema_version",
        "accepted_corpus_schema_version",
    ),
    "opening_recurrence_route_projection": (
        "manifest_hash",
        "corpus_id",
        "source_file",
        "source_row_ordinal",
        "color_scope",
        "distinct_game_count",
    ),
}

_VERSION_TABLES = {
    "corpus_schema": CORPUS_SCHEMA_VERSION,
    "opening_catalog_schema": SCHEMA_VERSION,
    "opening_relationship_schema": RELATIONSHIP_SCHEMA_VERSION,
    "opening_recurrence_schema": RECURRENCE_SCHEMA_VERSION,
}


def require_schema(connection: sqlite3.Connection) -> None:
    """Raise the public unavailable error unless every required table is supported."""

    try:
        names = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        if set(_REQUIRED_COLUMNS) - names:
            raise OpeningLineLibraryUnavailableError
        for table, expected_version in _VERSION_TABLES.items():
            row = connection.execute(f"SELECT version FROM {table} WHERE id = 1").fetchone()
            if row is None or row[0] != expected_version:
                raise OpeningLineLibraryUnavailableError
        for table, expected_columns in _REQUIRED_COLUMNS.items():
            columns = {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")}
            if not set(expected_columns).issubset(columns):
                raise OpeningLineLibraryUnavailableError
    except OpeningLineLibraryUnavailableError:
        raise
    except (sqlite3.Error, Exception) as error:
        raise OpeningLineLibraryUnavailableError from error
