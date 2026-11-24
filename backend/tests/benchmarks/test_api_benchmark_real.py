"""Real-database API benchmarks (opt-in, read-only).

Covers the gaps named in the benchmark analysis: timings for insight,
games, openings, and analysis against the host export copy at
``data/database/chess-seed.db`` (never the live volume; export a fresh host seed
copy first,
see ``data/README.md``), plus a
global no-filter training load with a per-page breakdown.

Run from the repository root (Git Bash):

  timeout 500s env CHESS_RUN_API_BENCHMARK_REAL=1 \
    .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v

Git Bash, exporting the variable for the session:

  export CHESS_RUN_API_BENCHMARK_REAL=1
  timeout 500s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v
  unset CHESS_RUN_API_BENCHMARK_REAL

Extra knobs (see also backend/tests/benchmarks/test_api_benchmark.py):

  CHESS_API_BENCH_REAL_REPEATS    repeats per real single-request case (default 3)
  CHESS_API_BENCH_REAL_TIMEOUT_S  per-request timeout for real cases (default 60)
  CHESS_API_BENCH_MAX_MS_REAL     median limit for real single requests (default 60000)
  CHESS_API_BENCH_MAX_MS_REAL_LOAD  limit for the global load total (default 600000)

Every test verifies the database bytes are identical before and after, so a
passing run proves the benchmark never writes to the real database. Reports
go to docs/benchmarks/API/ next to the synthetic ones.
"""

from __future__ import annotations

import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.caching import clear_caches
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from backend.tests.benchmarks.test_api_benchmark import (
    _database_info,
    _float_env,
    _int_env,
    _run_case,
    _stats,
    _timed_get,
    _write_report,
)
from chess_move_trainer.database.lifecycle import HOST_SEED_DATABASE_PATH

REAL_AS_OF = datetime.now(timezone.utc).date().isoformat()
REAL_ALEKHINE_FEN = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
REAL_CARO_KEY = "B10:Caro-Kann Defense"
REAL_PAGE_SIZE = 100
REAL_FULL_LOAD_PAGE_CAP = 12

needs_real_database = pytest.mark.skipif(
    os.environ.get("CHESS_RUN_API_BENCHMARK_REAL") != "1",
    reason="opt-in: set CHESS_RUN_API_BENCHMARK_REAL=1 to time the real database",
)


def _real_database() -> Path:
    database = Path(os.environ.get("CHESS_REBUILT_DATABASE_PATH", str(HOST_SEED_DATABASE_PATH)))
    if not database.exists():
        pytest.skip(f"real database not found: {database}")
    return database


def _real_settings() -> tuple[int, float, float]:
    return (
        _int_env("CHESS_API_BENCH_REAL_REPEATS", 3),
        _float_env("CHESS_API_BENCH_REAL_TIMEOUT_S", 60),
        _float_env("CHESS_API_BENCH_MAX_MS_REAL", 60000),
    )


def _open_real_client(monkeypatch: pytest.MonkeyPatch, database: Path) -> TestClient:
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    app.dependency_overrides.clear()
    return TestClient(app)


@needs_real_database
def test_real_database_practice_caro(monkeypatch: pytest.MonkeyPatch) -> None:
    """Time the settled Practice Caro page 1 (per-page cost for a filtered load)."""
    database = _real_database()
    before = database.read_bytes()
    client = _open_real_client(monkeypatch, database)
    try:
        repeats, timeout_s, threshold_ms = _real_settings()
        payload = _run_case(
            client,
            name="real-practice-caro-page1",
            path="/api/positions/training-requirements",
            params={
                "as_of": REAL_AS_OF,
                "training_requirement_lt": 0,
                "opening_key": REAL_CARO_KEY,
                "opening_match": "reached",
                "page": 1,
                "page_size": REAL_PAGE_SIZE,
            },
            repeats=repeats,
            timeout_s=timeout_s,
            threshold_ms=threshold_ms,
            database=database,
            db_kind="real",
            cold=True,
            warm_repeats=repeats,
        )
        assert payload["total_reported"] is not None
    finally:
        app.dependency_overrides.clear()
    assert database.read_bytes() == before


@needs_real_database
def test_real_database_global_training_load(monkeypatch: pytest.MonkeyPatch) -> None:
    """Time the global train-everything load page by page (per-page breakdown).

    Page 1 reveals ``total``. When the load fits in REAL_FULL_LOAD_PAGE_CAP
    pages every page is read. Otherwise only the first 3 pages are read and
    the report is marked partial with a median-based extrapolation, so one
    run can never page through an unexpectedly huge result set without bound.
    """
    database = _real_database()
    before = database.read_bytes()
    client = _open_real_client(monkeypatch, database)
    try:
        _, timeout_s, _ = _real_settings()
        load_limit_ms = _float_env("CHESS_API_BENCH_MAX_MS_REAL_LOAD", 600000)
        clear_caches()
        base = {"as_of": REAL_AS_OF, "training_requirement_lt": 0, "page_size": REAL_PAGE_SIZE}
        page_times: list[float] = []
        page = 1
        total = 0
        loaded = 0
        started_total = time.perf_counter()
        status_code, elapsed_ms, body = _timed_get(
            client, "/api/positions/training-requirements", {**base, "page": 1}
        )
        assert status_code == 200
        page_times.append(elapsed_ms)
        total = int(body.get("total", 0))
        loaded += len(body.get("items", []))
        total_pages = max(1, math.ceil(total / REAL_PAGE_SIZE)) if total else 1
        partial = total_pages > REAL_FULL_LOAD_PAGE_CAP
        last_page = 3 if partial else total_pages
        while page < last_page:
            page += 1
            status_code, elapsed_ms, body = _timed_get(
                client, "/api/positions/training-requirements", {**base, "page": page}
            )
            assert status_code == 200
            page_times.append(elapsed_ms)
            loaded += len(body.get("items", []))
        total_ms = (time.perf_counter() - started_total) * 1000.0
        median_page = _stats(page_times)["median_ms"]
        warm_status, warm_page1_ms, _ = _timed_get(
            client, "/api/positions/training-requirements", {**base, "page": 1}
        )
        assert warm_status == 200
        payload: dict[str, object] = {
            "name": "real-global-training-load",
            "measured_at_utc": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/api/positions/training-requirements",
            "params": base,
            "database": _database_info(database, "real"),
            "repeats": 1,
            "timeout_s": timeout_s,
            "samples_ms": [round(value, 3) for value in page_times],
            "stats": {
                key: round(value, 3) if isinstance(value, float) else value
                for key, value in _stats(page_times).items()
            },
            "threshold_median_ms": load_limit_ms,
            "pages_read": len(page_times),
            "total_pages": total_pages,
            "total_reported": total,
            "items_loaded": loaded,
            "partial": partial,
            "extrapolated_full_load_ms": round(median_page * total_pages, 3),
            "full_load_total_ms": round(total_ms, 3),
            "cache_cleared_before_load": True,
            "warm_page1_ms": round(warm_page1_ms, 3),
        }
        _write_report("real-global-training-load", payload)
        assert total_ms < load_limit_ms
    finally:
        app.dependency_overrides.clear()
    assert database.read_bytes() == before


@needs_real_database
def test_real_database_position_insight(monkeypatch: pytest.MonkeyPatch) -> None:
    """Time one insight read for a known real position (Alekhine, white)."""
    database = _real_database()
    before = database.read_bytes()
    client = _open_real_client(monkeypatch, database)
    try:
        repeats, timeout_s, threshold_ms = _real_settings()
        _run_case(
            client,
            name="real-position-insight",
            path="/api/positions/insight",
            params={"fen": REAL_ALEKHINE_FEN, "trainer_color": "white", "as_of": REAL_AS_OF},
            repeats=repeats,
            timeout_s=timeout_s,
            threshold_ms=threshold_ms,
            database=database,
            db_kind="real",
        )
    finally:
        app.dependency_overrides.clear()
    assert database.read_bytes() == before


@needs_real_database
def test_real_database_games_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """Time games page 1 against the real game corpus."""
    database = _real_database()
    before = database.read_bytes()
    client = _open_real_client(monkeypatch, database)
    try:
        repeats, timeout_s, _ = _real_settings()
        # The games search answers from SQL aggregation (12,710 games on the
        # current database). This case proves COLD latency: the server cache
        # is cleared between repeats, and warm repeats are reported separately.
        threshold_ms = _float_env("CHESS_API_BENCH_MAX_MS_REAL_GAMES", 1500)
        payload = _run_case(
            client,
            name="real-games-list",
            path="/api/games",
            params={"page": 1, "page_size": 50},
            repeats=repeats,
            timeout_s=timeout_s,
            threshold_ms=threshold_ms,
            database=database,
            db_kind="real",
            cold=True,
            warm_repeats=repeats,
        )
        assert payload["total_reported"] is not None
    finally:
        app.dependency_overrides.clear()
    assert database.read_bytes() == before


@needs_real_database
def test_real_database_openings_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """Time openings page 1 against the real catalogue."""
    database = _real_database()
    before = database.read_bytes()
    client = _open_real_client(monkeypatch, database)
    try:
        repeats, timeout_s, threshold_ms = _real_settings()
        payload = _run_case(
            client,
            name="real-openings-list",
            path="/api/openings",
            params={"page": 1, "page_size": 50},
            repeats=repeats,
            timeout_s=timeout_s,
            threshold_ms=threshold_ms,
            database=database,
            db_kind="real",
            cold=True,
            warm_repeats=repeats,
        )
        assert payload["total_reported"] is not None
    finally:
        app.dependency_overrides.clear()
    assert database.read_bytes() == before


@needs_real_database
def test_real_database_analysis_observation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Time one analysis read for a known real position (any state returns 200)."""
    database = _real_database()
    before = database.read_bytes()
    client = _open_real_client(monkeypatch, database)
    try:
        repeats, timeout_s, threshold_ms = _real_settings()
        _run_case(
            client,
            name="real-analysis-observation",
            path="/api/analysis",
            params={"fen": REAL_ALEKHINE_FEN},
            repeats=repeats,
            timeout_s=timeout_s,
            threshold_ms=threshold_ms,
            database=database,
            db_kind="real",
        )
    finally:
        app.dependency_overrides.clear()
    assert database.read_bytes() == before
