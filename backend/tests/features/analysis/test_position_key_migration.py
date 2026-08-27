from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from backend.app.features.analysis import (
    AnalysisRepository,
    AnalysisResult,
    migrate_position_key_schema,
    position_key_from_fen,
    require_analysis_schema,
)
from backend.app.features.evaluation import (
    enqueue,
    observe,
    require_evaluation_schema,
)

from .conftest import candidate, completed_at

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42"


def _create_v1_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE analysis_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        );
        CREATE TABLE analysis_result (
            fen TEXT PRIMARY KEY,
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
        );
        CREATE TABLE analysis_candidate (
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
            PRIMARY KEY (fen, rank),
            FOREIGN KEY (fen) REFERENCES analysis_result(fen) ON DELETE CASCADE
        );
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
        );
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
        );
        CREATE TRIGGER analysis_batch_run_no_update
        BEFORE UPDATE ON analysis_batch_run BEGIN
            SELECT RAISE(ABORT, 'analysis batch summaries are append-only');
        END;
        CREATE TRIGGER analysis_batch_run_no_delete
        BEFORE DELETE ON analysis_batch_run BEGIN
            SELECT RAISE(ABORT, 'analysis batch summaries are append-only');
        END;
        CREATE TRIGGER analysis_failure_no_update
        BEFORE UPDATE ON analysis_position_failure BEGIN
            SELECT RAISE(ABORT, 'analysis failures are append-only');
        END;
        CREATE TRIGGER analysis_failure_no_delete
        BEFORE DELETE ON analysis_position_failure BEGIN
            SELECT RAISE(ABORT, 'analysis failures are append-only');
        END;
        INSERT INTO analysis_schema VALUES (1, 1, 'v1');

        CREATE TABLE evaluation_schema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        );
        CREATE TABLE evaluation_queue (
            fen TEXT PRIMARY KEY,
            state TEXT NOT NULL CHECK (state IN ('queued', 'running', 'done', 'failed')),
            position INTEGER NOT NULL,
            attempts INTEGER NOT NULL CHECK (attempts >= 0),
            schema_version INTEGER NOT NULL,
            enqueued_at TEXT NOT NULL,
            started_at TEXT NULL,
            finished_at TEXT NULL,
            last_error_code TEXT NULL,
            last_error_details TEXT NULL
        );
        CREATE INDEX evaluation_queue_fifo ON evaluation_queue (state, position);
        INSERT INTO evaluation_schema VALUES (1, 1, 'v1');
        """
    )


@pytest.fixture
def v1_connection(tmp_path: Path):
    connection = sqlite3.connect(tmp_path / "position-key-v1.db")
    connection.execute("PRAGMA foreign_keys = ON")
    _create_v1_schema(connection)
    for index, fen in enumerate((START_FEN, COUNTER_VARIANT_FEN), 1):
        connection.execute(
            "INSERT INTO analysis_result "
            "(fen, schema_version, profile_id, settings_json, settings_fingerprint, "
            "engine_binary_sha256, engine_name, engine_version, terminal_kind, candidate_count, "
            "completed_at, wall_time_ms) VALUES (?, 1, 'legacy', '{}', ?, ?, 'Fakefish', '18', "
            "NULL, 1, 'v1', 1)",
            (fen, "f{index}" * 64, "a" * 64),
        )
        connection.execute(
            "INSERT INTO analysis_candidate "
            "(fen, rank, score_kind, score_value, wdl_wins, wdl_draws, wdl_losses, "
            "pv_uci_json, depth, seldepth, nodes, engine_time_ms) "
            "VALUES (?, 1, 'cp', ?, 300, 500, 200, '[\"e2e4\"]', 1, 1, 1, 1)",
            (fen, index),
        )
        connection.execute(
            "INSERT INTO evaluation_queue "
            "(fen, state, position, attempts, schema_version, enqueued_at, started_at, "
            "finished_at, last_error_code, last_error_details) "
            "VALUES (?, ?, ?, 0, 1, 'v1', NULL, NULL, NULL, NULL)",
            (fen, "queued" if index == 1 else "running", index),
        )
    connection.execute(
        "INSERT INTO analysis_batch_run "
        "(run_id, status, selection_json, settings_fingerprint, started_at, finished_at, "
        "selected_positions, eligible_positions, completed_positions, failed_positions, details) "
        "VALUES (41, 'failed', '[]', ?, 'start', 'finish', 2, 2, 1, 1, 'historical')",
        ("b" * 64,),
    )
    connection.execute(
        "INSERT INTO analysis_position_failure "
        "(failure_id, run_id, fen, settings_fingerprint, attempts, error_code, details, failed_at) "
        "VALUES (9, 41, ?, ?, 1, 'timeout', 'historical failure', 'finish')",
        (COUNTER_VARIANT_FEN, "b" * 64),
    )
    connection.commit()
    try:
        yield connection
    finally:
        connection.close()


def _result(profile, fen: str) -> AnalysisResult:
    roots = ("e2e4", "d2d4", "g1f3", "c2c4", "b1c3")
    return AnalysisResult(
        fen=fen,
        profile=profile,
        candidates=tuple(candidate(rank, move) for rank, move in enumerate(roots, 1)),
        terminal_kind=None,
        completed_at=completed_at(),
        wall_time_ms=1,
    )


def test_v1_transition_resets_disposable_rows_and_preserves_history(
    v1_connection: sqlite3.Connection,
) -> None:
    assert v1_connection.execute("SELECT COUNT(*) FROM analysis_result").fetchone() == (2,)
    assert v1_connection.execute("SELECT COUNT(*) FROM analysis_candidate").fetchone() == (2,)
    assert v1_connection.execute("SELECT COUNT(*) FROM evaluation_queue").fetchone() == (2,)

    migrate_position_key_schema(v1_connection)

    assert require_analysis_schema(v1_connection) == 2
    assert require_evaluation_schema(v1_connection) == 2
    assert v1_connection.execute("SELECT COUNT(*) FROM analysis_result").fetchone() == (0,)
    assert v1_connection.execute("SELECT COUNT(*) FROM analysis_candidate").fetchone() == (0,)
    assert v1_connection.execute("SELECT COUNT(*) FROM evaluation_queue").fetchone() == (0,)
    assert v1_connection.execute(
        "SELECT status, details FROM analysis_batch_run WHERE run_id = 41"
    ).fetchone() == ("failed", "historical")
    assert v1_connection.execute(
        "SELECT fen, error_code, details FROM analysis_position_failure WHERE failure_id = 9"
    ).fetchone() == (COUNTER_VARIANT_FEN, "timeout", "historical failure")

    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        v1_connection.execute("UPDATE analysis_batch_run SET details = 'changed' WHERE run_id = 41")
    v1_connection.rollback()


def test_new_position_key_schema_dedupes_counter_variants(v1_connection, profile) -> None:
    migrate_position_key_schema(v1_connection)
    repository = AnalysisRepository(v1_connection)

    repository.publish(_result(profile, START_FEN))
    repository.publish(_result(profile, COUNTER_VARIANT_FEN))

    assert position_key_from_fen(START_FEN) == position_key_from_fen(COUNTER_VARIANT_FEN)
    assert v1_connection.execute("SELECT COUNT(*) FROM analysis_result").fetchone() == (1,)
    assert v1_connection.execute("SELECT COUNT(*) FROM analysis_candidate").fetchone() == (5,)
    assert v1_connection.execute("SELECT fen FROM analysis_result").fetchone() == (
        COUNTER_VARIANT_FEN,
    )
    assert len(v1_connection.execute("SELECT fen FROM analysis_result").fetchone()[0].split()) == 6

    first_outcome, first_item = enqueue(v1_connection, START_FEN)
    second_outcome, second_item = enqueue(v1_connection, COUNTER_VARIANT_FEN)
    assert first_outcome == "queued"
    assert second_outcome == "already_queued"
    assert first_item == second_item
    assert observe(v1_connection, COUNTER_VARIANT_FEN) == first_item
    assert v1_connection.execute("SELECT COUNT(*) FROM evaluation_queue").fetchone() == (1,)
