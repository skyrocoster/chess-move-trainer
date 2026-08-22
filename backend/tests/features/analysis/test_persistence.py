from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

import pytest

from backend.app.features.analysis import (
    AnalysisCandidate,
    AnalysisProfile,
    AnalysisRepository,
    AnalysisResult,
    ResultEligibility,
    initialize_analysis_schema,
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
ROOTS = ("e2e4", "d2d4", "g1f3", "c2c4", "b1c3")


def complete_result(profile: AnalysisProfile, *, completed_at: str) -> AnalysisResult:
    candidates = tuple(
        AnalysisCandidate(
            rank=rank,
            score_kind="cp",
            score_value=rank,
            wdl_wins=300,
            wdl_draws=500,
            wdl_losses=200,
            pv_uci=(move,),
            depth=12,
            seldepth=16,
            nodes=profile.node_budget,
            engine_time_ms=20,
        )
        for rank, move in enumerate(ROOTS, 1)
    )
    return AnalysisResult(
        fen=START_FEN,
        profile=profile,
        candidates=candidates,
        terminal_kind=None,
        completed_at=completed_at,
        wall_time_ms=25,
    )


def test_persistence_and_profile_eligibility(connection, profile) -> None:
    initialize_analysis_schema(connection)
    repository = AnalysisRepository(connection)
    assert repository.eligibility(START_FEN, profile) is ResultEligibility.MISSING

    first_time = datetime(2026, 8, 20, 12, 0, tzinfo=UTC).isoformat()
    repository.publish(complete_result(profile, completed_at=first_time))

    assert repository.eligibility(START_FEN, profile) is ResultEligibility.ELIGIBLE
    assert connection.execute(
        "SELECT candidate_count, completed_at FROM analysis_result WHERE fen=?",
        (START_FEN,),
    ).fetchone() == (5, first_time)
    assert connection.execute(
        "SELECT score_kind, pv_uci_json FROM analysis_candidate WHERE fen=? ORDER BY rank",
        (START_FEN,),
    ).fetchall()[0] == ("cp", '["e2e4"]')

    stale = AnalysisProfile(
        profile_id="changed",
        engine_binary_sha256="b" * 64,
        engine_name="Fakefish",
        engine_version="18-test",
        node_budget=100_000,
        options={"Clear Hash": True},
    )
    assert repository.eligibility(START_FEN, stale) is ResultEligibility.STALE


def test_atomic_stale_replacement_rolls_back_to_old_parent_and_candidates(
    connection, profile
) -> None:
    initialize_analysis_schema(connection)
    repository = AnalysisRepository(connection)
    old_time = datetime(2026, 8, 20, 12, 0, tzinfo=UTC).isoformat()
    repository.publish(complete_result(profile, completed_at=old_time))
    before_parent = connection.execute(
        "SELECT profile_id, completed_at FROM analysis_result WHERE fen=?", (START_FEN,)
    ).fetchone()
    before_candidates = connection.execute(
        "SELECT rank, score_value, pv_uci_json FROM analysis_candidate WHERE fen=? ORDER BY rank",
        (START_FEN,),
    ).fetchall()

    replacement_profile = AnalysisProfile(
        profile_id="replacement",
        engine_binary_sha256="d" * 64,
        engine_name="Fakefish",
        engine_version="18-test",
        node_budget=100_000,
        options={"Clear Hash": True},
    )
    replacement = complete_result(
        replacement_profile,
        completed_at=datetime(2026, 8, 20, 13, 0, tzinfo=UTC).isoformat(),
    )
    connection.execute(
        "CREATE TRIGGER force_candidate_failure BEFORE INSERT ON analysis_candidate "
        "WHEN NEW.rank = 2 BEGIN SELECT RAISE(ABORT, 'forced candidate failure'); END"
    )
    connection.commit()

    with pytest.raises(sqlite3.IntegrityError, match="forced candidate failure"):
        repository.publish(replacement)

    assert (
        connection.execute(
            "SELECT profile_id, completed_at FROM analysis_result WHERE fen=?", (START_FEN,)
        ).fetchone()
        == before_parent
    )
    assert (
        connection.execute(
            "SELECT rank, score_value, pv_uci_json FROM analysis_candidate "
            "WHERE fen=? ORDER BY rank",
            (START_FEN,),
        ).fetchall()
        == before_candidates
    )
    assert repository.eligibility(START_FEN, profile) is ResultEligibility.ELIGIBLE
