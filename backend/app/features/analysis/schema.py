"""Explicit initialization for the independent analysis schema."""

from __future__ import annotations

import sqlite3

from .errors import AnalysisSchemaError

ANALYSIS_SCHEMA_VERSION = 2
_LEGACY_ANALYSIS_SCHEMA_VERSION = 1
ANALYSIS_TABLES = {
    "analysis_schema",
    "analysis_result",
    "analysis_candidate",
    "analysis_batch_run",
    "analysis_position_failure",
}
ANALYSIS_TRIGGERS = {
    "analysis_batch_run_no_update",
    "analysis_batch_run_no_delete",
    "analysis_failure_no_update",
    "analysis_failure_no_delete",
}
REQUIRED_COLUMNS = {
    "analysis_schema": {"id", "version", "applied_at"},
    "analysis_result": {
        "position_key",
        "fen",
        "schema_version",
        "profile_id",
        "settings_json",
        "settings_fingerprint",
        "engine_binary_sha256",
        "engine_name",
        "engine_version",
        "terminal_kind",
        "candidate_count",
        "completed_at",
        "wall_time_ms",
    },
    "analysis_candidate": {
        "position_key",
        "fen",
        "rank",
        "score_kind",
        "score_value",
        "wdl_wins",
        "wdl_draws",
        "wdl_losses",
        "pv_uci_json",
        "depth",
        "seldepth",
        "nodes",
        "engine_time_ms",
    },
    "analysis_batch_run": {
        "run_id",
        "status",
        "selection_json",
        "settings_fingerprint",
        "started_at",
        "finished_at",
        "selected_positions",
        "eligible_positions",
        "completed_positions",
        "failed_positions",
        "details",
    },
    "analysis_position_failure": {
        "failure_id",
        "run_id",
        "fen",
        "settings_fingerprint",
        "attempts",
        "error_code",
        "details",
        "failed_at",
    },
}
_LEGACY_REQUIRED_COLUMNS = {
    **REQUIRED_COLUMNS,
    "analysis_result": REQUIRED_COLUMNS["analysis_result"] - {"position_key"},
    "analysis_candidate": REQUIRED_COLUMNS["analysis_candidate"] - {"position_key"},
}


def _existing_tables(connection: sqlite3.Connection) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'analysis_%'"
        )
    }


def require_analysis_schema(connection: sqlite3.Connection) -> int:
    """Require the complete supported schema without creating or repairing it."""

    existing = _existing_tables(connection)
    if "analysis_schema" not in existing:
        raise AnalysisSchemaError("analysis schema is not initialized; run explicit initialization")
    try:
        row = connection.execute("SELECT version FROM analysis_schema WHERE id = 1").fetchone()
    except sqlite3.Error as error:
        raise AnalysisSchemaError("analysis schema version table is incompatible") from error
    if row is None or row[0] != ANALYSIS_SCHEMA_VERSION:
        found = "missing" if row is None else repr(row[0])
        raise AnalysisSchemaError(
            f"incompatible analysis schema version {found}; expected {ANALYSIS_SCHEMA_VERSION}"
        )
    if existing != ANALYSIS_TABLES:
        raise AnalysisSchemaError("analysis schema tables are incomplete or unexpected")
    for table, expected_columns in REQUIRED_COLUMNS.items():
        try:
            columns = {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")}
        except sqlite3.Error as error:
            raise AnalysisSchemaError("analysis schema table shape is incompatible") from error
        if columns != expected_columns:
            raise AnalysisSchemaError(f"analysis schema table {table} is incompatible")
    triggers = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'analysis_%'"
        )
    }
    if triggers != ANALYSIS_TRIGGERS:
        raise AnalysisSchemaError("analysis append-only protections are incomplete or unexpected")
    return ANALYSIS_SCHEMA_VERSION


def _require_legacy_analysis_schema(connection: sqlite3.Connection) -> None:
    """Validate the v1 shape accepted by the one-time position-key transition."""

    existing = _existing_tables(connection)
    if existing != ANALYSIS_TABLES:
        raise AnalysisSchemaError("legacy analysis schema tables are incomplete or unexpected")
    try:
        row = connection.execute("SELECT version FROM analysis_schema WHERE id = 1").fetchone()
    except sqlite3.Error as error:
        raise AnalysisSchemaError("legacy analysis schema version table is incompatible") from error
    if row is None or row[0] != _LEGACY_ANALYSIS_SCHEMA_VERSION:
        found = "missing" if row is None else repr(row[0])
        raise AnalysisSchemaError(
            f"incompatible legacy analysis schema version {found}; expected 1"
        )
    for table, expected_columns in _LEGACY_REQUIRED_COLUMNS.items():
        columns = {str(row[1]) for row in connection.execute(f"PRAGMA table_info({table})")}
        if columns != expected_columns:
            raise AnalysisSchemaError(f"legacy analysis schema table {table} is incompatible")
    triggers = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'analysis_%'"
        )
    }
    if triggers != ANALYSIS_TRIGGERS:
        raise AnalysisSchemaError("legacy analysis append-only protections are incomplete")


_POSITION_KEY_ANALYSIS_TABLES = (
    """
    CREATE TABLE analysis_result (
        position_key TEXT PRIMARY KEY NOT NULL,
        fen TEXT NOT NULL,
        schema_version INTEGER NOT NULL,
        profile_id TEXT NOT NULL,
        settings_json TEXT NOT NULL,
        settings_fingerprint TEXT NOT NULL,
        engine_binary_sha256 TEXT NOT NULL,
        engine_name TEXT NOT NULL,
        engine_version TEXT NOT NULL,
        terminal_kind TEXT NULL,
        candidate_count INTEGER NOT NULL CHECK (candidate_count BETWEEN 0 AND 5),
        completed_at TEXT NOT NULL,
        wall_time_ms INTEGER NOT NULL CHECK (wall_time_ms >= 0)
    )
    """,
    """
    CREATE TABLE analysis_candidate (
        position_key TEXT NOT NULL,
        fen TEXT NOT NULL,
        rank INTEGER NOT NULL CHECK (rank BETWEEN 1 AND 5),
        score_kind TEXT NOT NULL CHECK (score_kind IN ('cp', 'mate', 'mate_given')),
        score_value INTEGER NOT NULL,
        wdl_wins INTEGER NOT NULL,
        wdl_draws INTEGER NOT NULL,
        wdl_losses INTEGER NOT NULL,
        pv_uci_json TEXT NOT NULL,
        depth INTEGER NOT NULL,
        seldepth INTEGER NOT NULL,
        nodes INTEGER NOT NULL,
        engine_time_ms INTEGER NOT NULL,
        PRIMARY KEY (position_key, rank),
        FOREIGN KEY (position_key) REFERENCES analysis_result(position_key) ON DELETE CASCADE
    )
    """,
)


def initialize_analysis_schema(connection: sqlite3.Connection) -> None:
    """Create the analysis namespace only through this explicit operation."""

    connection.execute("PRAGMA foreign_keys = ON")
    existing = _existing_tables(connection)
    if existing:
        require_analysis_schema(connection)
        return

    statements = (
        """
        CREATE TABLE analysis_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        )
        """,
        *_POSITION_KEY_ANALYSIS_TABLES,
        """
        CREATE TABLE analysis_batch_run (
            run_id INTEGER PRIMARY KEY,
            status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'interrupted')),
            selection_json TEXT NOT NULL,
            settings_fingerprint TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT NOT NULL,
            selected_positions INTEGER NOT NULL,
            eligible_positions INTEGER NOT NULL,
            completed_positions INTEGER NOT NULL,
            failed_positions INTEGER NOT NULL,
            details TEXT NULL
        )
        """,
        """
        CREATE TABLE analysis_position_failure (
            failure_id INTEGER PRIMARY KEY,
            run_id INTEGER NOT NULL,
            fen TEXT NOT NULL,
            settings_fingerprint TEXT NOT NULL,
            attempts INTEGER NOT NULL CHECK (attempts >= 1),
            error_code TEXT NOT NULL,
            details TEXT NOT NULL,
            failed_at TEXT NOT NULL,
            UNIQUE (run_id, fen),
            FOREIGN KEY (run_id) REFERENCES analysis_batch_run(run_id)
        )
        """,
        """
        CREATE TRIGGER analysis_batch_run_no_update
        BEFORE UPDATE ON analysis_batch_run BEGIN
            SELECT RAISE(ABORT, 'analysis batch summaries are append-only');
        END
        """,
        """
        CREATE TRIGGER analysis_batch_run_no_delete
        BEFORE DELETE ON analysis_batch_run BEGIN
            SELECT RAISE(ABORT, 'analysis batch summaries are append-only');
        END
        """,
        """
        CREATE TRIGGER analysis_failure_no_update
        BEFORE UPDATE ON analysis_position_failure BEGIN
            SELECT RAISE(ABORT, 'analysis failures are append-only');
        END
        """,
        """
        CREATE TRIGGER analysis_failure_no_delete
        BEFORE DELETE ON analysis_position_failure BEGIN
            SELECT RAISE(ABORT, 'analysis failures are append-only');
        END
        """,
    )
    try:
        connection.execute("BEGIN")
        for statement in statements:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO analysis_schema (id, version, applied_at) VALUES (1, ?, datetime('now'))",
            (ANALYSIS_SCHEMA_VERSION,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def migrate_position_key_schema(connection: sqlite3.Connection) -> None:
    """Reset disposable v1 analysis and queue rows in one transaction."""

    from backend.app.features.evaluation.schema import (
        EVALUATION_SCHEMA_VERSION,
        _position_key_queue_index,
        _position_key_queue_table,
        _require_legacy_evaluation_schema,
    )

    _require_legacy_analysis_schema(connection)
    _require_legacy_evaluation_schema(connection)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.execute("BEGIN")
        connection.execute("DELETE FROM analysis_candidate")
        connection.execute("DELETE FROM analysis_result")
        connection.execute("DELETE FROM evaluation_queue")
        connection.execute("DROP TABLE analysis_candidate")
        connection.execute("DROP TABLE analysis_result")
        connection.execute("DROP TABLE evaluation_queue")
        for statement in _POSITION_KEY_ANALYSIS_TABLES:
            connection.execute(statement)
        connection.execute(_position_key_queue_table())
        connection.execute(_position_key_queue_index())
        connection.execute(
            "UPDATE analysis_schema SET version = ? WHERE id = 1", (ANALYSIS_SCHEMA_VERSION,)
        )
        connection.execute(
            "UPDATE evaluation_schema SET version = ? WHERE id = 1",
            (EVALUATION_SCHEMA_VERSION,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
