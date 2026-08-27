from __future__ import annotations

import sqlite3

import pytest

from backend.app.features.analysis import (
    ANALYSIS_SCHEMA_VERSION,
    AnalysisCandidate,
    AnalysisProfile,
    AnalysisResult,
    AnalysisSchemaError,
    AnalysisValidationError,
    PositionKey,
    canonical_fen,
    initialize_analysis_schema,
    position_key_from_fen,
    require_analysis_schema,
)

from .conftest import candidate, completed_at


def test_schema_requires_explicit_initialization_and_is_independent(connection) -> None:
    connection.execute(
        "CREATE TABLE corpus_schema (id INTEGER PRIMARY KEY, version INTEGER NOT NULL)"
    )
    connection.execute("INSERT INTO corpus_schema VALUES (1, 1)")
    connection.commit()

    with pytest.raises(AnalysisSchemaError, match="not initialized"):
        require_analysis_schema(connection)

    initialize_analysis_schema(connection)
    initialize_analysis_schema(connection)

    assert require_analysis_schema(connection) == ANALYSIS_SCHEMA_VERSION
    assert connection.execute("SELECT version FROM corpus_schema WHERE id=1").fetchone() == (1,)
    foreign_tables = {
        row[0] for row in connection.execute("PRAGMA foreign_key_list(analysis_result)").fetchall()
    }
    assert foreign_tables == set()


def test_incompatible_schema_is_refused_without_repair(connection) -> None:
    connection.execute(
        "CREATE TABLE analysis_schema "
        "(id INTEGER PRIMARY KEY, version INTEGER NOT NULL, applied_at TEXT NOT NULL)"
    )
    connection.execute("INSERT INTO analysis_schema VALUES (1, 99, 'old')")
    connection.commit()

    with pytest.raises(AnalysisSchemaError, match="version 99"):
        initialize_analysis_schema(connection)

    assert connection.execute("SELECT version FROM analysis_schema").fetchone() == (99,)
    assert (
        connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='analysis_result'"
        ).fetchone()
        is None
    )


def test_profile_serialization_and_eligibility_identity_are_deterministic() -> None:
    common = dict(
        profile_id="balanced-v1",
        engine_binary_sha256="b" * 64,
        engine_name="Stockfish",
        engine_version="18",
        node_budget=100_000,
    )
    first = AnalysisProfile(**common, options={"Skill Level": 20, "Clear Hash": True})
    second = AnalysisProfile(**common, options={"Clear Hash": True, "Skill Level": 20})

    assert first.settings_json == second.settings_json
    assert first.fingerprint == second.fingerprint
    assert '"node_budget":100000' in first.settings_json
    assert '"uci_show_wdl":true' in first.settings_json


def test_terminal_serialization_preserves_complete_zero_candidate_outcome(profile) -> None:
    fen = "7k/5Q2/7K/8/8/8/8/8 b - - 0 1"
    result = AnalysisResult(
        fen=fen,
        profile=profile,
        candidates=(),
        terminal_kind="stalemate",
        completed_at=completed_at(),
        wall_time_ms=0,
    )

    assert result.fen == canonical_fen(fen)
    assert result.candidates == ()


@pytest.mark.parametrize(
    ("candidate", "message"),
    [
        (
            AnalysisCandidate(1, "mate", 0, 500, 0, 500, ("e2e4",), 1, 1, 1, 1),
            "candidate count",
        ),
        (
            AnalysisCandidate(1, "mate", 0, 500, 0, 500, ("e2e5",), 1, 1, 1, 1),
            "candidate count",
        ),
    ],
)
def test_partial_or_illegal_nonterminal_serialization_is_refused(
    profile, candidate: AnalysisCandidate, message: str
) -> None:
    with pytest.raises(AnalysisValidationError, match=message):
        AnalysisResult(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            profile=profile,
            candidates=(candidate,),
            terminal_kind=None,
            completed_at=completed_at(),
            wall_time_ms=1,
        )


def test_illegal_full_pv_is_refused_after_complete_candidate_shape(profile) -> None:
    roots = ("e2e4", "d2d4", "g1f3", "c2c4", "b1c3")
    candidates = [candidate(rank, move) for rank, move in enumerate(roots, 1)]
    illegal = candidates[0]
    candidates[0] = AnalysisCandidate(
        illegal.rank,
        illegal.score_kind,
        illegal.score_value,
        illegal.wdl_wins,
        illegal.wdl_draws,
        illegal.wdl_losses,
        ("e2e4", "e7e5", "e1e3"),
        illegal.depth,
        illegal.seldepth,
        illegal.nodes,
        illegal.engine_time_ms,
    )

    with pytest.raises(AnalysisValidationError, match="illegal"):
        AnalysisResult(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            profile=profile,
            candidates=tuple(candidates),
            terminal_kind=None,
            completed_at=completed_at(),
            wall_time_ms=30,
        )


def test_typed_score_wdl_and_canonical_fen_validation() -> None:
    mate = AnalysisCandidate(1, "mate", 0, 1000, 0, 0, ("e2e4",), 1, 1, 1, 1)
    given = AnalysisCandidate(1, "mate_given", 0, 1000, 0, 0, ("e2e4",), 1, 1, 1, 1)
    assert mate.score_kind != given.score_kind

    with pytest.raises(AnalysisValidationError, match="sum to 1000"):
        AnalysisCandidate(1, "cp", 1, 1, 1, 1, ("e2e4",), 1, 1, 1, 1)
    with pytest.raises(AnalysisValidationError, match="six-field"):
        canonical_fen("8/8/8/8/8/8/8/8 w - -")
    with pytest.raises(AnalysisValidationError, match="canonical"):
        canonical_fen(" rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")


def test_position_key_normalizes_only_counters_and_requires_public_six_fields() -> None:
    first = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    second = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42"

    assert canonical_fen(first) == first
    assert canonical_fen(second) == second
    key = position_key_from_fen(first)
    assert key == position_key_from_fen(second)
    assert key == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
    assert PositionKey(key) == key
    with pytest.raises(AnalysisValidationError, match="six-field"):
        position_key_from_fen("8/8/8/8/8/8/8/8 w - -")


def test_run_and_failure_records_are_append_only(connection) -> None:
    initialize_analysis_schema(connection)
    cursor = connection.execute(
        "INSERT INTO analysis_batch_run "
        "(status, selection_json, settings_fingerprint, started_at, finished_at, "
        "selected_positions, eligible_positions, completed_positions, failed_positions) "
        "VALUES ('success', '[]', ?, 'start', 'finish', 1, 0, 0, 1)",
        ("c" * 64,),
    )
    connection.execute(
        "INSERT INTO analysis_position_failure "
        "(run_id, fen, settings_fingerprint, attempts, error_code, details, failed_at) "
        "VALUES (?, ?, ?, 2, 'timeout', 'final failure', 'finish')",
        (cursor.lastrowid, "orphan exact fen", "c" * 64),
    )
    connection.commit()

    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        connection.execute("UPDATE analysis_batch_run SET details='changed'")
    connection.rollback()
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        connection.execute("DELETE FROM analysis_position_failure")
