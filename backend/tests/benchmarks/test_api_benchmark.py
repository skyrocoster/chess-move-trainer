"""API response-time benchmarks.

What this file is:
  Small pytest suite that times the real HTTP routes in
  ``backend/app/main.py`` against small synthetic databases built in
  ``tmp_path``. Real-database benchmarks live in
  ``test_api_benchmark_real.py`` next to this file and run only when you
  opt in (see that file).

How to run (from the repository root):
  Git Bash:
    timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/benchmarks -v

Environment knobs (all optional):
  CHESS_API_BENCH_REPEATS        repeats per endpoint (default 5)
  CHESS_API_BENCH_TIMEOUT_S      per-request timeout in seconds (default 30)
  CHESS_API_BENCH_OUTPUT         report folder (default docs/benchmarks/API)
  CHESS_API_BENCH_MAX_MS         median limit for synthetic requests (default 2000)

Reports:
  Each test writes one timestamped JSON file to the output folder, for
  example ``20260914T120000Z-training-requirements-page.json``. The JSON
  holds aggregate timings only (min/median/mean/max plus the sample list);
  response bodies are not stored.
"""

from __future__ import annotations

import json
import os
import sqlite3
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from backend.app.caching import clear_caches
from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository

ROOT = Path(__file__).resolve().parents[3]

TRAIN_FEN = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
INSIGHT_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
AS_OF = "2026-01-15"


def _int_env(name: str, default: int) -> int:
    try:
        return max(1, int(os.environ.get(name, default)))
    except (TypeError, ValueError):
        return default


def _float_env(name: str, default: float) -> float:
    try:
        value = float(os.environ.get(name, default))
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default


def _output_dir() -> Path:
    raw = os.environ.get("CHESS_API_BENCH_OUTPUT", str(ROOT / "docs" / "benchmarks" / "API"))
    return Path(raw)


def _stats(samples_ms: list[float]) -> dict[str, float]:
    return {
        "count": len(samples_ms),
        "min_ms": min(samples_ms),
        "median_ms": statistics.median(samples_ms),
        "mean_ms": statistics.fmean(samples_ms),
        "max_ms": max(samples_ms),
    }


def _write_report(name: str, payload: dict[str, object]) -> Path:
    out_dir = _output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"{stamp}-{name}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    stats = payload.get("stats", {})
    print(f"benchmark {name} stats_ms={json.dumps(stats)} report={path.name}")
    return path


def _database_info(database: Path, kind: str) -> dict[str, object]:
    return {
        "kind": kind,
        "file_name": database.name,
        "size_bytes": database.stat().st_size,
    }


BENCH_GAME_UUIDS = (
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1",
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2",
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa3",
)
BENCH_TRAINER_UUID = "11111111-1111-4111-8111-111111111111"


def create_benchmark_database(path: Path) -> Path:
    """Build one small database that serves every synthetic benchmark case."""
    create_schema(path)
    train_position_id = PositionRepository(path).resolve_fen(TRAIN_FEN)
    insight_position_id = PositionRepository(path).resolve_fen(INSIGHT_FEN)
    with sqlite3.connect(path) as connection:
        connection.executemany(
            """
            INSERT INTO datasource_game (
                dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                (1, BENCH_GAME_UUIDS[0], "https://example.test/bench-1", '[Result "*"]\n\n*',
                 "white", BENCH_TRAINER_UUID, "2026-01-01T00:00:00Z"),
                (2, BENCH_GAME_UUIDS[1], "https://example.test/bench-2", '[Result "*"]\n\n*',
                 "white", BENCH_TRAINER_UUID, "2026-01-02T00:00:00Z"),
                (3, BENCH_GAME_UUIDS[2], "https://example.test/bench-3", '[Result "*"]\n\n*',
                 "black", BENCH_TRAINER_UUID, "2026-01-03T00:00:00Z"),
            ),
        )
        connection.executemany(
            """
            INSERT INTO derived_game_position (
                datasource_game_id, dgp_ply, derived_position_id,
                dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
            ) VALUES (?, ?, ?, ?, 0, 1)
            """,
            (
                (1, 1, train_position_id, "a2a3"),
                (2, 1, train_position_id, "b2b3"),
                (3, 1, train_position_id, "a2a3"),
                (1, 2, insight_position_id, "a2a3"),
                (1, 4, insight_position_id, "a2a3"),
                (2, 2, insight_position_id, "b2b3"),
            ),
        )
        connection.execute(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_move_uci
            ) VALUES (?, '2026-01-01', 'a2a3')
            """,
            (train_position_id,),
        )
        connection.executemany(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_effective_until, dpm_move_uci
            ) VALUES (?, ?, ?, ?)
            """,
            (
                (insight_position_id, "2026-01-01", "2026-02-01", "a2a3"),
                (insight_position_id, "2026-03-01", None, "b2b3"),
            ),
        )
        opening_a = connection.execute(
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('A00', 'Bench Opening')"
            " RETURNING do_opening_id"
        ).fetchone()[0]
        opening_b = connection.execute(
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('C20', 'Bench Pawn Game')"
            " RETURNING do_opening_id"
        ).fetchone()[0]
        route_a_id = connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?) RETURNING dor_route_id
            """,
            (opening_a, train_position_id),
        ).fetchone()[0]
        route_b_id = connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?) RETURNING dor_route_id
            """,
            (opening_b, insight_position_id),
        ).fetchone()[0]
        connection.executemany(
            """
            INSERT INTO derived_opening_route_move
                (derived_opening_route_id, dorm_ply, dorm_move_uci)
            VALUES (?, ?, ?)
            """,
            (
                (route_a_id, 1, "e2e4"),
                (route_a_id, 2, "g8f6"),
                (route_b_id, 1, "e2e4"),
                (route_b_id, 2, "e7e5"),
            ),
        )
        result_id = connection.execute(
            """
            INSERT INTO derived_analysis_result (
                derived_position_id, dar_quality, dar_configuration_version,
                dar_settings_json, dar_engine_name, dar_engine_version, dar_terminal_kind
            ) VALUES (?, 'tool', 7, ?, 'Stockfish', '18', NULL)
            """,
            (insight_position_id, json.dumps({"Hash": 16})),
        ).lastrowid
        connection.executemany(
            """
            INSERT INTO derived_analysis_line (
                derived_analysis_result_id, dal_rank, dal_score_kind, dal_score_value,
                dal_wdl_wins, dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json, dal_depth
            ) VALUES (?, ?, 'cp', ?, 450, 300, 250, ?, 22)
            """,
            (
                (result_id, 1, 34, json.dumps(["a2a3"])),
                (result_id, 2, 35, json.dumps(["g1h3"])),
                (result_id, 3, 36, json.dumps(["g1f3"])),
                (result_id, 4, 37, json.dumps(["g1e2"])),
                (result_id, 5, 38, json.dumps(["f1a6"])),
            ),
        )
    return path


@pytest.fixture
def benchmark_client() -> TestClient:
    app.dependency_overrides.clear()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def benchmark_database(tmp_path: Path) -> Path:
    return create_benchmark_database(tmp_path / "api-benchmark.db")


def _use_database(monkeypatch: pytest.MonkeyPatch, database: Path) -> None:
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))


def _timed_get(
    client: TestClient,
    path: str,
    params: dict[str, object] | None,
    timeout_s: float,
) -> tuple[int, float, dict[str, object]]:
    started = time.perf_counter()
    response = client.get(path, params=params, timeout=timeout_s)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    try:
        body = response.json()
    except ValueError:
        body = {}
    if not isinstance(body, dict):
        body = {"items": body} if isinstance(body, list) else {}
    return response.status_code, elapsed_ms, body


def _run_case(
    client: TestClient,
    *,
    name: str,
    path: str,
    params: dict[str, object] | None,
    repeats: int,
    timeout_s: float,
    threshold_ms: float,
    database: Path,
    db_kind: str,
    extra: dict[str, object] | None = None,
    cold: bool = False,
    warm_repeats: int = 0,
) -> dict[str, object]:
    samples: list[float] = []
    status_code = 0
    last_body: dict[str, object] = {}
    for _ in range(repeats):
        if cold:
            clear_caches()
        status_code, elapsed_ms, last_body = _timed_get(client, path, params, timeout_s)
        assert status_code == 200, f"{name} returned {status_code}: {last_body}"
        samples.append(elapsed_ms)
    stats = _stats(samples)
    payload: dict[str, object] = {
        "name": name,
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": path,
        "params": params or {},
        "database": _database_info(database, db_kind),
        "repeats": repeats,
        "timeout_s": timeout_s,
        "samples_ms": [round(value, 3) for value in samples],
        "stats": {key: round(value, 3) if isinstance(value, float) else value for key, value in stats.items()},
        "threshold_median_ms": threshold_ms,
        "items_returned": len(last_body.get("items", [])) if isinstance(last_body.get("items"), list) else None,
        "total_reported": last_body.get("total"),
    }
    if cold:
        payload["cache_cleared_between_samples"] = True
    if warm_repeats:
        warm_samples: list[float] = []
        for _ in range(warm_repeats):
            status_code, elapsed_ms, _ = _timed_get(client, path, params, timeout_s)
            assert status_code == 200, f"{name} warm repeat returned {status_code}"
            warm_samples.append(elapsed_ms)
        payload["warm_repeats"] = warm_repeats
        payload["warm_samples_ms"] = [round(value, 3) for value in warm_samples]
        payload["warm_stats"] = {
            key: round(value, 3) if isinstance(value, float) else value
            for key, value in _stats(warm_samples).items()
        }
    if extra:
        payload.update(extra)
    _write_report(name, payload)
    assert stats["median_ms"] < threshold_ms, f"{name} median {stats['median_ms']:.1f}ms >= {threshold_ms}ms"
    return payload


def test_health_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_database(monkeypatch, benchmark_database)
    _run_case(
        benchmark_client,
        name="health",
        path="/api/health",
        params=None,
        repeats=_int_env("CHESS_API_BENCH_REPEATS", 5),
        timeout_s=_float_env("CHESS_API_BENCH_TIMEOUT_S", 30),
        threshold_ms=_float_env("CHESS_API_BENCH_MAX_MS", 2000),
        database=benchmark_database,
        db_kind="synthetic",
    )


def test_openings_catalogue_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_database(monkeypatch, benchmark_database)
    repeats = _int_env("CHESS_API_BENCH_REPEATS", 5)
    timeout_s = _float_env("CHESS_API_BENCH_TIMEOUT_S", 30)
    threshold_ms = _float_env("CHESS_API_BENCH_MAX_MS", 2000)
    _run_case(
        benchmark_client,
        name="openings-list",
        path="/api/openings",
        params={"page": 1, "page_size": 50},
        repeats=repeats,
        timeout_s=timeout_s,
        threshold_ms=threshold_ms,
        database=benchmark_database,
        db_kind="synthetic",
        cold=True,
        warm_repeats=repeats,
    )
    status_code, _, body = _timed_get(
        benchmark_client, "/api/openings", {"page": 1, "page_size": 50}, timeout_s
    )
    assert status_code == 200 and body.get("items")
    first_key = body["items"][0]["key"]
    _run_case(
        benchmark_client,
        name="openings-detail",
        path=f"/api/openings/{quote(first_key, safe='')}",
        params=None,
        repeats=repeats,
        timeout_s=timeout_s,
        threshold_ms=threshold_ms,
        database=benchmark_database,
        db_kind="synthetic",
        cold=True,
        warm_repeats=repeats,
    )


def test_games_search_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_database(monkeypatch, benchmark_database)
    repeats = _int_env("CHESS_API_BENCH_REPEATS", 5)
    timeout_s = _float_env("CHESS_API_BENCH_TIMEOUT_S", 30)
    threshold_ms = _float_env("CHESS_API_BENCH_MAX_MS", 2000)
    _run_case(
        benchmark_client,
        name="games-list",
        path="/api/games",
        params={"page": 1, "page_size": 50},
        repeats=repeats,
        timeout_s=timeout_s,
        threshold_ms=threshold_ms,
        database=benchmark_database,
        db_kind="synthetic",
        cold=True,
        warm_repeats=repeats,
    )
    status_code, _, body = _timed_get(
        benchmark_client, "/api/games", {"page": 1, "page_size": 50}, timeout_s
    )
    assert status_code == 200 and body.get("items")
    game_uuid = body["items"][0]["game_uuid"]
    _run_case(
        benchmark_client,
        name="games-detail",
        path=f"/api/games/{game_uuid}",
        params=None,
        repeats=repeats,
        timeout_s=timeout_s,
        threshold_ms=threshold_ms,
        database=benchmark_database,
        db_kind="synthetic",
    )


def test_training_requirements_page_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_database(monkeypatch, benchmark_database)
    before = benchmark_database.read_bytes()
    repeats = _int_env("CHESS_API_BENCH_REPEATS", 5)
    _run_case(
        benchmark_client,
        name="training-requirements-page",
        path="/api/positions/training-requirements",
        params={"as_of": AS_OF, "training_requirement_gte": -100, "page": 1, "page_size": 50},
        repeats=repeats,
        timeout_s=_float_env("CHESS_API_BENCH_TIMEOUT_S", 30),
        threshold_ms=_float_env("CHESS_API_BENCH_MAX_MS", 2000),
        database=benchmark_database,
        db_kind="synthetic",
        cold=True,
        warm_repeats=repeats,
    )
    assert benchmark_database.read_bytes() == before


def test_position_insight_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_database(monkeypatch, benchmark_database)
    _run_case(
        benchmark_client,
        name="position-insight",
        path="/api/positions/insight",
        params={"fen": INSIGHT_FEN, "trainer_color": "white", "as_of": AS_OF},
        repeats=_int_env("CHESS_API_BENCH_REPEATS", 5),
        timeout_s=_float_env("CHESS_API_BENCH_TIMEOUT_S", 30),
        threshold_ms=_float_env("CHESS_API_BENCH_MAX_MS", 2000),
        database=benchmark_database,
        db_kind="synthetic",
    )


def test_preferred_moves_timeline_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_database(monkeypatch, benchmark_database)
    _run_case(
        benchmark_client,
        name="preferred-moves-timeline",
        path="/api/preferred-moves",
        params={"fen": INSIGHT_FEN, "from": "2026-01-15", "until": "2026-05-15"},
        repeats=_int_env("CHESS_API_BENCH_REPEATS", 5),
        timeout_s=_float_env("CHESS_API_BENCH_TIMEOUT_S", 30),
        threshold_ms=_float_env("CHESS_API_BENCH_MAX_MS", 2000),
        database=benchmark_database,
        db_kind="synthetic",
    )


def test_analysis_observation_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _use_database(monkeypatch, benchmark_database)
    _run_case(
        benchmark_client,
        name="analysis-observation",
        path="/api/analysis",
        params={"fen": INSIGHT_FEN},
        repeats=_int_env("CHESS_API_BENCH_REPEATS", 5),
        timeout_s=_float_env("CHESS_API_BENCH_TIMEOUT_S", 30),
        threshold_ms=_float_env("CHESS_API_BENCH_MAX_MS", 2000),
        database=benchmark_database,
        db_kind="synthetic",
    )


def test_trainer_practice_full_load_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mirror the frontend Practice loader: read pages 1..N until total is reached."""
    _use_database(monkeypatch, benchmark_database)
    clear_caches()
    timeout_s = _float_env("CHESS_API_BENCH_TIMEOUT_S", 30)
    threshold_ms = _float_env("CHESS_API_BENCH_MAX_MS", 10000)
    page_times: list[float] = []
    started_total = time.perf_counter()
    page = 1
    total: int | None = None
    loaded = 0
    while True:
        status_code, elapsed_ms, body = _timed_get(
            benchmark_client,
            "/api/positions/training-requirements",
            {"as_of": AS_OF, "training_requirement_gte": -100, "page": page, "page_size": 50},
            timeout_s,
        )
        assert status_code == 200
        page_times.append(elapsed_ms)
        total = int(body.get("total", 0))
        loaded += len(body.get("items", []))
        if loaded >= total or not body.get("items"):
            break
        page += 1
        assert page <= 20, "practice loader paged past 20 pages on a 3-game database"
    total_ms = (time.perf_counter() - started_total) * 1000.0
    warm_status, warm_page1_ms, _ = _timed_get(
        benchmark_client,
        "/api/positions/training-requirements",
        {"as_of": AS_OF, "training_requirement_gte": -100, "page": 1, "page_size": 50},
        timeout_s,
    )
    assert warm_status == 200
    payload: dict[str, object] = {
        "name": "trainer-practice-full-load",
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": "/api/positions/training-requirements",
        "params": {"as_of": AS_OF, "page_size": 50},
        "database": _database_info(benchmark_database, "synthetic"),
        "repeats": 1,
        "timeout_s": timeout_s,
        "samples_ms": [round(value, 3) for value in page_times],
        "stats": {k: round(v, 3) if isinstance(v, float) else v for k, v in _stats(page_times).items()},
        "threshold_median_ms": threshold_ms,
        "pages_read": page,
        "total_reported": total,
        "full_load_total_ms": round(total_ms, 3),
        "cache_cleared_before_load": True,
        "warm_page1_ms": round(warm_page1_ms, 3),
    }
    _write_report("trainer-practice-full-load", payload)
    assert total_ms < threshold_ms


def test_board_navigation_benchmark(
    benchmark_client: TestClient,
    benchmark_database: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mirror stepping through 10 board positions (two insight addresses alternating)."""
    _use_database(monkeypatch, benchmark_database)
    timeout_s = _float_env("CHESS_API_BENCH_TIMEOUT_S", 30)
    threshold_ms = _float_env("CHESS_API_BENCH_MAX_MS", 10000)
    addresses = [
        {"fen": INSIGHT_FEN, "trainer_color": "white", "as_of": AS_OF},
        {"fen": TRAIN_FEN, "trainer_color": "white", "as_of": AS_OF},
    ]
    samples: list[float] = []
    started_total = time.perf_counter()
    for index in range(10):
        status_code, elapsed_ms, _ = _timed_get(
            benchmark_client, "/api/positions/insight", addresses[index % 2], timeout_s
        )
        assert status_code == 200
        samples.append(elapsed_ms)
    total_ms = (time.perf_counter() - started_total) * 1000.0
    payload: dict[str, object] = {
        "name": "board-navigation-10-insights",
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": "/api/positions/insight",
        "params": {"moves": 10, "pattern": "alternate-two-positions"},
        "database": _database_info(benchmark_database, "synthetic"),
        "repeats": 10,
        "timeout_s": timeout_s,
        "samples_ms": [round(value, 3) for value in samples],
        "stats": {k: round(v, 3) if isinstance(v, float) else v for k, v in _stats(samples).items()},
        "threshold_median_ms": threshold_ms,
        "full_load_total_ms": round(total_ms, 3),
    }
    _write_report("board-navigation-10-insights", payload)
    assert total_ms < threshold_ms
