from __future__ import annotations

import sqlite3

import pytest

from backend.app.features.analysis import AnalysisRepository
from backend.app.features.evaluation import (
    EVALUATION_SCHEMA_VERSION,
    EvaluationSchemaError,
    initialize_evaluation_schema,
    require_evaluation_schema,
)

from .conftest import START_FEN, initialized, result_for


def test_init_creates_tables_and_index(connection: sqlite3.Connection) -> None:
    initialize_evaluation_schema(connection)

    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'evaluation_%'"
        )
    }
    assert tables == {"evaluation_schema", "evaluation_queue"}
    indexes = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'evaluation_%'"
        )
    }
    assert indexes == {"evaluation_queue_fifo"}
    assert require_evaluation_schema(connection) == EVALUATION_SCHEMA_VERSION


def test_require_refuses_missing_schema(connection: sqlite3.Connection) -> None:
    with pytest.raises(EvaluationSchemaError, match="not initialized"):
        require_evaluation_schema(connection)


def test_require_refuses_wrong_version(connection: sqlite3.Connection) -> None:
    initialize_evaluation_schema(connection)
    connection.execute("UPDATE evaluation_schema SET version = 99 WHERE id = 1")
    connection.commit()
    with pytest.raises(EvaluationSchemaError, match="99"):
        require_evaluation_schema(connection)


def test_require_refuses_incomplete_tables(connection: sqlite3.Connection) -> None:
    initialize_evaluation_schema(connection)
    connection.execute("DROP TABLE evaluation_queue")
    connection.commit()
    with pytest.raises(EvaluationSchemaError, match="incomplete"):
        require_evaluation_schema(connection)


def test_require_refuses_incompatible_columns(connection: sqlite3.Connection) -> None:
    initialize_evaluation_schema(connection)
    connection.execute("ALTER TABLE evaluation_queue DROP COLUMN attempts")
    connection.commit()
    with pytest.raises(EvaluationSchemaError, match="incompatible"):
        require_evaluation_schema(connection)


def test_require_refuses_missing_index(connection: sqlite3.Connection) -> None:
    initialize_evaluation_schema(connection)
    connection.execute("DROP INDEX evaluation_queue_fifo")
    connection.commit()
    with pytest.raises(EvaluationSchemaError, match="index"):
        require_evaluation_schema(connection)


def test_init_is_idempotent_for_compatible_schema(connection: sqlite3.Connection) -> None:
    initialize_evaluation_schema(connection)
    initialize_evaluation_schema(connection)
    assert require_evaluation_schema(connection) == EVALUATION_SCHEMA_VERSION


def test_coexists_with_analysis_schema(connection: sqlite3.Connection, profile) -> None:
    initialized(connection)

    assert require_evaluation_schema(connection) == EVALUATION_SCHEMA_VERSION
    AnalysisRepository(connection).publish(result_for(profile, START_FEN))
    assert connection.execute("SELECT COUNT(*) FROM analysis_result").fetchone() == (1,)

    # Dropping the queue table must not disturb independent analysis tables.
    connection.execute("DROP TABLE evaluation_queue")
    connection.commit()
    with pytest.raises(EvaluationSchemaError, match="incomplete"):
        require_evaluation_schema(connection)
    assert connection.execute("SELECT COUNT(*) FROM analysis_result").fetchone() == (1,)
