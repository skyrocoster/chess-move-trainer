"""Explicit initialization for the independent evaluation queue schema."""

from __future__ import annotations

import sqlite3

from .errors import EvaluationSchemaError
from .models import QUEUE_STATES

EVALUATION_SCHEMA_VERSION = 1
EVALUATION_TABLES = {"evaluation_schema", "evaluation_queue"}
REQUIRED_COLUMNS = {
    "evaluation_schema": {"id", "version", "applied_at"},
    "evaluation_queue": {
        "fen",
        "state",
        "position",
        "attempts",
        "schema_version",
        "enqueued_at",
        "started_at",
        "finished_at",
        "last_error_code",
        "last_error_details",
    },
}
_STATES_SQL = ", ".join(f"'{state}'" for state in QUEUE_STATES)


def _existing_tables(connection: sqlite3.Connection) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'evaluation_%'"
        )
    }


def require_evaluation_schema(connection: sqlite3.Connection) -> int:
    """Require the complete supported evaluation schema without creating or repairing it."""

    existing = _existing_tables(connection)
    if "evaluation_schema" not in existing:
        raise EvaluationSchemaError(
            "evaluation schema is not initialized; run explicit initialization"
        )
    try:
        row = connection.execute("SELECT version FROM evaluation_schema WHERE id = 1").fetchone()
    except sqlite3.Error as error:
        raise EvaluationSchemaError("evaluation schema version table is incompatible") from error
    if row is None or row[0] != EVALUATION_SCHEMA_VERSION:
        found = "missing" if row is None else repr(row[0])
        raise EvaluationSchemaError(
            f"incompatible evaluation schema version {found}; expected {EVALUATION_SCHEMA_VERSION}"
        )
    if existing != EVALUATION_TABLES:
        raise EvaluationSchemaError("evaluation schema tables are incomplete or unexpected")
    for table, expected_columns in REQUIRED_COLUMNS.items():
        try:
            columns = {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")}
        except sqlite3.Error as error:
            raise EvaluationSchemaError(
                f"evaluation schema table {table} is incompatible"
            ) from error
        if columns != expected_columns:
            raise EvaluationSchemaError(f"evaluation schema table {table} is incompatible")
    indexes = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'evaluation_%'"
        )
    }
    if indexes != {"evaluation_queue_fifo"}:
        raise EvaluationSchemaError("evaluation schema indexes are incomplete or unexpected")
    return EVALUATION_SCHEMA_VERSION


def initialize_evaluation_schema(connection: sqlite3.Connection) -> None:
    """Create the evaluation queue namespace only through this explicit operation."""

    connection.execute("PRAGMA foreign_keys = ON")
    existing = _existing_tables(connection)
    if existing:
        require_evaluation_schema(connection)
        return

    statements = (
        """
        CREATE TABLE evaluation_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        )
        """,
        f"""
        CREATE TABLE evaluation_queue (
            fen TEXT PRIMARY KEY,
            state TEXT NOT NULL CHECK (state IN ({_STATES_SQL})),
            position INTEGER NOT NULL,
            attempts INTEGER NOT NULL CHECK (attempts >= 0),
            schema_version INTEGER NOT NULL,
            enqueued_at TEXT NOT NULL,
            started_at TEXT NULL,
            finished_at TEXT NULL,
            last_error_code TEXT NULL,
            last_error_details TEXT NULL
        )
        """,
        """
        CREATE INDEX evaluation_queue_fifo ON evaluation_queue (state, position)
        """,
    )
    try:
        connection.execute("BEGIN")
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO evaluation_schema (id, version, applied_at) "
            "VALUES (1, ?, datetime('now'))",
            (EVALUATION_SCHEMA_VERSION,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
