from __future__ import annotations

import os
import re
from pathlib import Path

from chess_move_trainer.database.proof import (
    collect_direct_measurements,
    print_direct_measurements,
)
from chess_move_trainer.database.stockfish import TOOL_PROFILE

ROOT = Path(__file__).parents[3]
DIRECT_DATABASE = ROOT / "data/database/chess.db"


def _database() -> Path:
    return Path(os.environ.get("DIRECT_DATABASE", str(DIRECT_DATABASE)))


def test_real_direct_database_records_query_plans_and_timings() -> None:
    report = collect_direct_measurements(_database())

    assert report.database_path == _database().resolve()
    assert report.corpus.database_count == 1
    assert report.corpus.game_count > 0
    assert report.corpus.position_count > 0
    assert report.corpus.occurrence_count >= report.corpus.game_count
    assert report.corpus.analysis_result_count == 1
    assert report.corpus.analysis_line_count == TOOL_PROFILE.multipv

    operation_names = {measurement.name for measurement in report.measurements}
    assert "GameReadRepository.read" in operation_names
    assert {
        "PositionContextReader.read/all",
        "PositionContextReader.read/white",
        "PositionContextReader.read/black",
    } <= operation_names
    assert {
        "MoveResponseDistributionReader.read/all",
        "MoveResponseDistributionReader.read/white",
        "MoveResponseDistributionReader.read/black",
    } <= operation_names
    assert {
        "openings.recognition/routes",
        "openings.recognition/route-moves",
    } <= operation_names
    assert {
        "PreferredMoveRepository/find-position",
        "PreferredMoveRepository/load-schedule",
    } <= operation_names
    assert {
        "AnalysisReadRepository/read-result",
        "AnalysisReadRepository/read-lines",
    } <= operation_names
    assert {
        "BulkTargetSelector/load-route-moves",
        "BulkTargetSelector/load-game-page/first",
        "BulkTargetSelector/load-game-page/cursor",
        "BulkTargetSelector/check-eligibility",
    } <= operation_names

    assert len(report.measurements) == 17
    for measurement in report.measurements:
        assert measurement.repetitions == 3
        assert len(measurement.plan) > 0
        assert measurement.result_row_count >= 0
        assert all(elapsed >= 0 for elapsed in measurement.elapsed_seconds)

    assert report.index_decision in {"NO-INDEX", "INDEX-JUSTIFIED"}
    if report.index_decision == "INDEX-JUSTIFIED":
        assert report.index_table == "derived_game_position"
        assert report.index_columns == (
            "derived_position_id",
            "datasource_game_id",
            "dgp_ply",
        )
    else:
        assert report.index_table is None
        assert report.index_columns == ()
    assert "No timing threshold" in report.decision_reason

    print_direct_measurements(report)


def test_measurement_output_is_aggregate_only(capsys) -> None:
    report = collect_direct_measurements(_database())
    print_direct_measurements(report)
    output = capsys.readouterr().out

    for name, value in (
        ("games", report.corpus.game_count),
        ("positions", report.corpus.position_count),
        ("occurrences", report.corpus.occurrence_count),
        ("analysis_results", report.corpus.analysis_result_count),
        ("analysis_lines", report.corpus.analysis_line_count),
    ):
        assert f"{name}={value}" in output
    assert "repetitions=3" in output
    assert "elapsed_ms_min=" in output
    assert "elapsed_ms_median=" in output
    assert "elapsed_ms_max=" in output
    assert f"decision={report.index_decision}" in output

    assert not re.search(r"https?://|[0-9a-f]{8}-[0-9a-f-]{27,}", output, re.I)
    assert not re.search(r"\b(?:SELECT|INSERT|UPDATE|DELETE|PRAGMA)\b", output, re.I)
    assert "rnbqkbnr" not in output.lower()
    assert "fen" not in output.lower()
    assert "pgn" not in output.lower()
    assert "parameter" not in output.lower()
