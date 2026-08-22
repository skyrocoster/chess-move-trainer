from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from backend.app.features.analysis import AnalysisCandidate, AnalysisProfile


@pytest.fixture
def connection(tmp_path: Path):
    database = tmp_path / "analysis.db"
    db = sqlite3.connect(database)
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def profile() -> AnalysisProfile:
    return AnalysisProfile(
        profile_id="test-profile-v1",
        engine_binary_sha256="a" * 64,
        engine_name="Fakefish",
        engine_version="18-test",
        node_budget=50_000,
        options={"Clear Hash": True, "Skill Level": 20},
    )


def candidate(rank: int, root_move: str) -> AnalysisCandidate:
    return AnalysisCandidate(
        rank=rank,
        score_kind="cp" if rank != 5 else "mate_given",
        score_value=20 - rank if rank != 5 else 0,
        wdl_wins=300,
        wdl_draws=500,
        wdl_losses=200,
        pv_uci=(root_move,),
        depth=10,
        seldepth=14,
        nodes=50_000,
        engine_time_ms=25,
    )


def completed_at() -> str:
    return datetime(2026, 8, 20, 12, 0, tzinfo=UTC).isoformat()
