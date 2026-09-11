from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import AnalysisQuality
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.stockfish import DatabaseMutex, QueueService

ROOT = Path(__file__).parents[3]
EXECUTABLE = ROOT / "data" / "stockfish" / "stockfish-windows-x86-64-avx2.exe"
APPROVED_POSITIONS = ROOT / "data" / "stockfish" / "test_positions.json"
PROCESS_TIMEOUT_SECONDS = 170


def _run_worker(database: Path) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "chess_move_trainer.database",
            "stockfish",
            "worker",
            "--database",
            str(database),
            "--executable",
            str(EXECUTABLE),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        timeout=PROCESS_TIMEOUT_SECONDS,
    )


def test_one_position_real_worker_publishes_fixed_tool_profile_and_exits(
    tmp_path: Path,
) -> None:
    assert EXECUTABLE.is_file(), f"approved Stockfish executable is unavailable: {EXECUTABLE}"
    approved = json.loads(APPROVED_POSITIONS.read_text(encoding="utf-8"))
    fen = approved["positions"][0]["fen"]
    database = tmp_path / "worker.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(fen)
    QueueService(database).enqueue(position_id, AnalysisQuality.TOOL)

    result = _run_worker(database)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")

    with sqlite3.connect(database) as connection:
        parent = connection.execute(
            """
            SELECT dar_quality, dar_configuration_version, dar_settings_json,
                   dar_engine_name, dar_engine_version, dar_terminal_kind
            FROM derived_analysis_result
            WHERE derived_position_id = ?
            """,
            (position_id,),
        ).fetchone()
        line_count = connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_line WHERE derived_analysis_result_id = ?",
            (position_id,),
        ).fetchone()[0]
        ranks = connection.execute(
            """
            SELECT dal_rank FROM derived_analysis_line
            WHERE derived_analysis_result_id = ? ORDER BY dal_rank
            """,
            (position_id,),
        ).fetchall()
        queue_count = connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_queue"
        ).fetchone()[0]

    assert parent is not None
    assert parent[0:2] == ("tool", 1)
    assert json.loads(parent[2]) == {
        "Hash": 1024,
        "MultiPV": 5,
        "Nodes": 6_400_000,
        "Threads": 6,
        "UCI_ShowWDL": True,
    }
    assert parent[3:6] == ("Stockfish", "18", None)
    assert line_count == 5
    assert ranks == [(1,), (2,), (3,), (4,), (5,)]
    assert queue_count == 0

    released = DatabaseMutex(database)
    assert released.acquire(timeout=0)
    released.release()
