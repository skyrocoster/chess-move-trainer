from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[3]
EXECUTABLE = ROOT / "data" / "stockfish" / "stockfish-windows-x86-64-avx2.exe"
APPROVED_POSITIONS = ROOT / "data" / "stockfish" / "test_positions.json"
PROCESS_TIMEOUT_SECONDS = 170


def _smoke_arguments(position_input: Path, output_dir: Path) -> list[str]:
    return [
        "stockfish",
        "benchmark",
        "--executable",
        str(EXECUTABLE),
        "--position-input",
        str(position_input),
        "--output-dir",
        str(output_dir),
        "--node-budget",
        "100000",
        "--threads",
        "1",
        "--hash-mb",
        "64",
        "--repetitions",
        "1",
        "--shuffle-seed",
        "0",
    ]


def _run(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, "-m", "chess_move_trainer.database", *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        timeout=PROCESS_TIMEOUT_SECONDS,
    )


def test_one_position_real_benchmark_is_contained_and_completed_run_is_noop(
    tmp_path: Path,
) -> None:
    assert EXECUTABLE.is_file(), f"approved Stockfish executable is unavailable: {EXECUTABLE}"
    approved = json.loads(APPROVED_POSITIONS.read_text(encoding="utf-8"))
    first_position = approved["positions"][0]
    position_input = tmp_path / "one-position.json"
    position_input.write_text(
        json.dumps(
            {
                "positions": [
                    {"id": first_position["id"], "fen": first_position["fen"]}
                ]
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "benchmark-artifacts"
    arguments = _smoke_arguments(position_input, output_dir)

    first = _run(arguments)
    assert first.returncode == 0, first.stderr.decode("utf-8", errors="replace")
    first_files = {
        path.relative_to(output_dir)
        for path in output_dir.rglob("*")
        if path.is_file()
    }

    assert first_files == {
        Path("manifest.json"),
        Path("attempts.jsonl"),
        Path("checkpoint.json"),
        Path("summary.json"),
        Path("summary.csv"),
        Path("status.txt"),
    }
    assert len((output_dir / "attempts.jsonl").read_text(encoding="utf-8").splitlines()) == 1
    checkpoint = json.loads((output_dir / "checkpoint.json").read_text(encoding="utf-8"))
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert checkpoint["complete"] is True
    assert checkpoint["total_jobs"] == checkpoint["attempt_count"] == 1
    assert summary["dataset_state"] == "complete"
    assert summary["total_jobs"] == summary["successful_attempts"] == 1
    assert len((output_dir / "summary.csv").read_text(encoding="utf-8").splitlines()) == 2
    assert all(
        path.resolve().is_relative_to(output_dir.resolve())
        for path in output_dir.rglob("*")
    )

    second = _run(arguments)
    assert second.returncode == 0, second.stderr.decode("utf-8", errors="replace")
    assert len((output_dir / "attempts.jsonl").read_text(encoding="utf-8").splitlines()) == 1
    assert {
        path.relative_to(output_dir)
        for path in output_dir.rglob("*")
        if path.is_file()
    } == first_files
    second_checkpoint = json.loads((output_dir / "checkpoint.json").read_text(encoding="utf-8"))
    assert second_checkpoint["complete"] is True
    assert second_checkpoint["attempt_count"] == 1
