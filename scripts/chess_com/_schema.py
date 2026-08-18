"""Corpus schema DDL and initialization."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from ._errors import CorpusSchemaError

SCHEMA_VERSION = 1


def _table_exists(connection: sqlite3.Connection, name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def _schema_statements() -> tuple[str, ...]:
    return (
        """
        CREATE TABLE IF NOT EXISTS corpus (
            corpus_id INTEGER PRIMARY KEY,
            subject_player_uuid TEXT NOT NULL UNIQUE,
            FOREIGN KEY (subject_player_uuid) REFERENCES players(uuid)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS corpus_game (
            corpus_id INTEGER NOT NULL,
            game_uuid TEXT NOT NULL,
            rules TEXT NOT NULL CHECK (rules = 'chess'),
            fingerprint TEXT NOT NULL,
            PRIMARY KEY (corpus_id, game_uuid),
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id),
            FOREIGN KEY (game_uuid) REFERENCES games(uuid)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS position_state (
            state_id INTEGER PRIMARY KEY,
            placement TEXT,
            side_to_move TEXT,
            castling TEXT,
            en_passant TEXT,
            UNIQUE (placement, side_to_move, castling, en_passant)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS position_occurrence (
            occurrence_id INTEGER PRIMARY KEY,
            game_uuid TEXT NOT NULL,
            ply INTEGER NOT NULL,
            state_id INTEGER NOT NULL,
            san TEXT NULL,
            uci TEXT NULL,
            halfmove_clock INTEGER NOT NULL,
            fullmove_number INTEGER NOT NULL,
            UNIQUE (game_uuid, ply),
            FOREIGN KEY (game_uuid) REFERENCES games(uuid),
            FOREIGN KEY (state_id) REFERENCES position_state(state_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS corpus_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS corpus_run (
            run_id INTEGER PRIMARY KEY,
            corpus_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed', 'interrupted')),
            started_at TEXT,
            finished_at TEXT NULL,
            accepted_games INTEGER NOT NULL DEFAULT 0,
            excluded_games INTEGER NOT NULL DEFAULT 0,
            new_games INTEGER NOT NULL DEFAULT 0,
            changed_games INTEGER NOT NULL DEFAULT 0,
            removed_games INTEGER NOT NULL DEFAULT 0,
            unchanged_games INTEGER NOT NULL DEFAULT 0,
            ordered_positions INTEGER NOT NULL DEFAULT 0,
            unique_states INTEGER NOT NULL,
            validation TEXT NOT NULL,
            details TEXT NULL,
            FOREIGN KEY (corpus_id) REFERENCES corpus(corpus_id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS position_occurrence_state_idx ON position_occurrence(state_id)",
    )


def ensure_corpus_schema(connection: sqlite3.Connection, wanted: int = SCHEMA_VERSION) -> None:
    """Create the versioned corpus schema or reject an incompatible one."""

    connection.execute("PRAGMA foreign_keys = ON")
    schema_exists = _table_exists(connection, "corpus_schema")
    if schema_exists:
        version_row = connection.execute(
            "SELECT version FROM corpus_schema WHERE id = 1"
        ).fetchone()
        if version_row is None:
            raise CorpusSchemaError(
                "Corpus schema has no singleton version row; "
                f"expected version {wanted}; no changes made"
            )
        version = version_row[0]
        if version != wanted:
            raise CorpusSchemaError(
                f"Incompatible corpus schema version {version}; expected {wanted}; no changes made"
            )

    with connection:
        for statement in _schema_statements():
            connection.execute(statement)
        if not schema_exists:
            connection.execute(
                "INSERT INTO corpus_schema (id, version, applied_at) "
                "VALUES (1, ?, datetime('now'))",
                (wanted,),
            )


def initialize_corpus(
    database: Path, subject_uuid: str, logger: logging.Logger | None = None
) -> None:
    """Initialize the schema and the selected subject metadata row."""

    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        ensure_corpus_schema(connection)
        with connection:
            connection.execute(
                "INSERT INTO corpus (subject_player_uuid) VALUES (?) "
                "ON CONFLICT(subject_player_uuid) DO NOTHING",
                (subject_uuid,),
            )
        if logger:
            logger.info("Initialized corpus schema version %d for %s", SCHEMA_VERSION, subject_uuid)
    finally:
        connection.close()
