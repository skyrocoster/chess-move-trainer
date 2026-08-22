from __future__ import annotations

import json
import sqlite3
from collections import deque
from pathlib import Path

import chess
import pytest

from backend.app.features.analysis.benchmark import (
    canonical_write,
    freeze_report,
    load_frozen_report,
    validate_same_fixtures,
)
from backend.app.features.analysis.benchmark_fixtures import (
    BANDS,
    select_benchmark_fixtures,
)
from backend.app.features.analysis.benchmark_metrics import (
    CANDIDATE_BUDGETS,
    REFERENCE_BUDGET,
    RUBRIC_V1,
    RUBRIC_V2,
    evaluate_runs,
    nearest_rank,
    semantic_equivalence,
)
from backend.app.features.analysis.errors import AnalysisValidationError
from scripts.stockfish_analysis import benchmark_stockfish


def _positions(count: int) -> list[chess.Board]:
    queue = deque([chess.Board()])
    seen: set[str] = set()
    selected: list[chess.Board] = []
    while queue and len(selected) < count:
        board = queue.popleft()
        placement = board.board_fen()
        if placement not in seen and board.legal_moves.count() >= 5:
            seen.add(placement)
            selected.append(board)
        if len(board.move_stack) < 3:
            for move in list(board.legal_moves)[:8]:
                child = board.copy()
                child.push(move)
                queue.append(child)
    return selected


def _corpus_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE position_state (
            state_id INTEGER PRIMARY KEY, placement TEXT, side_to_move TEXT,
            castling TEXT, en_passant TEXT
        );
        CREATE TABLE position_occurrence (
            occurrence_id INTEGER PRIMARY KEY, game_uuid TEXT, ply INTEGER,
            state_id INTEGER, halfmove_clock INTEGER, fullmove_number INTEGER
        );
        CREATE TABLE corpus_game (corpus_id INTEGER, game_uuid TEXT);
        """
    )
    positions = _positions(24)
    for index, board in enumerate(positions):
        band = BANDS[index // 4]
        ply = band[0]
        fields = board.fen(en_passant="fen").split()
        game = f"game-{index:02d}"
        connection.execute(
            "INSERT INTO position_state VALUES (?, ?, ?, ?, ?)",
            (index + 1, fields[0], fields[1], fields[2], fields[3]),
        )
        connection.execute(
            "INSERT INTO position_occurrence VALUES (?, ?, ?, ?, ?, ?)",
            (index + 1, game, ply, index + 1, int(fields[4]), int(fields[5])),
        )
        connection.execute("INSERT INTO corpus_game VALUES (1, ?)", (game,))
    connection.commit()
    connection.close()


def test_fixture_selection_is_deterministic_read_only_and_band_complete(tmp_path: Path) -> None:
    database = tmp_path / "corpus.db"
    _corpus_database(database)
    before = database.stat().st_mtime_ns

    first, count = select_benchmark_fixtures(database)
    second, second_count = select_benchmark_fixtures(database)

    assert first == second
    assert count == second_count == 24
    assert len(first) == 24
    assert {fixture.band for fixture in first} == {f"{low}-{high}" for low, high in BANDS}
    assert all(sum(item.band == fixture.band for item in first) == 4 for fixture in first)
    assert len({fixture.fen.split()[0] for fixture in first}) == 24
    assert {fixture.fen.split()[1] for fixture in first} == {"w", "b"}
    assert database.stat().st_mtime_ns == before
    assert not Path(f"{database}-wal").exists()
    assert not Path(f"{database}-shm").exists()


def _candidate(move: str, *, cp: int, wins: int) -> dict[str, object]:
    return {
        "rank": 1,
        "score_kind": "cp",
        "score_value": cp,
        "wdl_wins": wins,
        "wdl_draws": 500,
        "wdl_losses": 500 - wins,
        "pv_uci": [move],
        "depth": 10,
        "seldepth": 12,
        "nodes": 50_000,
        "engine_time_ms": 10,
    }


def _run(budget: int, fixture: int, repetition: int) -> dict[str, object]:
    roots = ["a2a3", "b2b3", "c2c3"]
    if budget == 100_000 and fixture >= 20:
        roots = ["b2b3", "a2a3", "c2c3"]
    is_reference = budget == REFERENCE_BUDGET
    return {
        "fixture_index": fixture,
        "repetition": repetition,
        "node_budget": budget,
        "wall_time_ms": 25_000 if is_reference else 15_000,
        "completed_at": "2026-08-20T00:00:00+00:00",
        "candidates": [
            _candidate(move, cp=100 if is_reference else 125, wins=200 if is_reference else 225)
            for move in roots
        ],
    }


def test_frozen_rubric_selects_lowest_budget_at_inclusive_boundaries() -> None:
    runs = [
        _run(budget, fixture, repetition)
        for budget in (*CANDIDATE_BUDGETS, REFERENCE_BUDGET)
        for fixture in range(24)
        for repetition in (1, 2)
    ]

    result = evaluate_runs(runs, rubric_version=RUBRIC_V1)

    assert result["selected_node_budget"] == 50_000
    assert result["budgets"]["50000"]["qualifies"] is True
    assert result["budgets"]["50000"]["cp_drift_median"] == 25
    assert result["budgets"]["50000"]["wdl_drift_p90_nearest_rank"] == pytest.approx(0.025)
    assert result["budgets"]["100000"]["top1_agreement_count"] == 20
    assert result["budgets"]["100000"]["qualifies"] is False
    assert nearest_rank([1, 2, 3, 4, 100], 0.80) == 4


def _semantic_candidate(
    move: str,
    *,
    rank: int,
    kind: str = "cp",
    value: int,
    expected_thousandths: int = 500,
) -> dict[str, object]:
    return {
        "rank": rank,
        "score_kind": kind,
        "score_value": value,
        "wdl_wins": expected_thousandths,
        "wdl_draws": 0,
        "wdl_losses": 1000 - expected_thousandths,
        "pv_uci": [move],
    }


@pytest.mark.parametrize(
    ("side", "best_value", "selected_value", "best_wdl", "selected_wdl"),
    [("w", 100, 80, 600, 580), ("b", -100, -80, 400, 420)],
)
def test_v2_semantics_are_side_aware_and_boundaries_are_inclusive(
    side: str,
    best_value: int,
    selected_value: int,
    best_wdl: int,
    selected_wdl: int,
) -> None:
    best = _semantic_candidate("a2a3", rank=1, value=best_value, expected_thousandths=best_wdl)
    selected = _semantic_candidate(
        "b2b3", rank=2, value=selected_value, expected_thousandths=selected_wdl
    )
    reference = {"a2a3": best, "b2b3": selected}

    detail = semantic_equivalence(selected, reference, side)

    assert detail["equivalent"] is True
    assert detail["cp_loss"] == 20
    assert detail["wdl_expected_score_loss"] == pytest.approx(0.020)
    selected["score_value"] = selected_value - 1 if side == "w" else selected_value + 1
    assert semantic_equivalence(selected, reference, side)["equivalent"] is False


def test_v2_semantics_require_reference_top3_score_kind_and_mate_boundary() -> None:
    cp_best = _semantic_candidate("a2a3", rank=1, value=100)
    outside = _semantic_candidate("h2h3", rank=1, value=100)
    assert semantic_equivalence(outside, {"a2a3": cp_best}, "w")["equivalent"] is False

    wrong_kind = _semantic_candidate("a2a3", rank=1, kind="mate", value=3)
    assert semantic_equivalence(wrong_kind, {"a2a3": cp_best}, "w")["equivalent"] is False

    mate_best = _semantic_candidate("a2a3", rank=1, kind="mate", value=5)
    mate_close = _semantic_candidate("b2b3", rank=2, kind="mate", value=7)
    mate_far = _semantic_candidate("c2c3", rank=3, kind="mate", value=8)
    reference = {"a2a3": mate_best, "b2b3": mate_close, "c2c3": mate_far}
    assert semantic_equivalence(mate_close, reference, "w")["equivalent"] is True
    assert semantic_equivalence(mate_far, reference, "w")["equivalent"] is False


def test_v2_requires_semantic_equivalence_on_all_24_fixtures() -> None:
    runs = [
        _run(budget, fixture, repetition)
        for budget in (*CANDIDATE_BUDGETS, REFERENCE_BUDGET)
        for fixture in range(24)
        for repetition in (1, 2)
    ]
    fixtures = [{"fen": chess.STARTING_FEN} for _ in range(24)]
    passing = evaluate_runs(runs, rubric_version=RUBRIC_V2, fixtures=fixtures)
    assert passing["budgets"]["50000"]["semantic_equivalence_count"] == 24
    assert passing["budgets"]["50000"]["qualifies"] is True

    for run in runs:
        if run["node_budget"] == 50_000 and run["fixture_index"] == 0:
            run["candidates"][0]["pv_uci"] = ["h2h3"]
    failing = evaluate_runs(runs, rubric_version=RUBRIC_V2, fixtures=fixtures)
    assert failing["budgets"]["50000"]["semantic_equivalence_count"] == 23
    assert failing["budgets"]["50000"]["qualifies"] is False


def test_frozen_report_is_canonical_reproducible_and_cli_run_is_gated(tmp_path: Path) -> None:
    database = tmp_path / "corpus.db"
    report_path = tmp_path / "report.json"
    _corpus_database(database)
    fixtures, count = select_benchmark_fixtures(database)
    report = freeze_report(fixtures, count)

    canonical_write(report_path, report)
    first_bytes = report_path.read_bytes()
    canonical_write(report_path, report)

    assert report_path.read_bytes() == first_bytes
    assert load_frozen_report(report_path) == report
    assert (
        benchmark_stockfish.main(["--run", "--db", str(database), "--report", str(report_path)])
        == 1
    )
    assert json.loads(report_path.read_text(encoding="ascii"))["status"] == "fixtures_frozen"


def test_v2_freeze_records_and_enforces_v1_fixture_source_equality(tmp_path: Path) -> None:
    database = tmp_path / "corpus.db"
    _corpus_database(database)
    fixtures, count = select_benchmark_fixtures(database)
    frozen = freeze_report(
        fixtures,
        count,
        rubric_version=RUBRIC_V2,
        fixture_source_sha256="a" * 64,
    )

    validate_same_fixtures(frozen, fixtures, count)
    assert frozen["fixture_source"] == {
        "report": "mp09-stockfish-18-node-budget-v1.json",
        "sha256": "a" * 64,
        "fixtures_equal": True,
    }
    with pytest.raises(AnalysisValidationError, match="no longer matches v1"):
        validate_same_fixtures(frozen, fixtures[:-1], count)
