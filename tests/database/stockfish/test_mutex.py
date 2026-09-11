from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from chess_move_trainer.database.stockfish import (
    DatabaseMutex,
    mutex_name_for_database,
    normalize_database_path,
)

pytestmark = pytest.mark.skipif(os.name != "nt", reason="the DB-07 mutex is Windows-only")


ROOT = Path(__file__).parents[3]


def _child_process(database_path: Path, signal_path: Path, action: str) -> subprocess.Popen[str]:
    code = """
import os
import sys
import time
from pathlib import Path
sys.path.insert(0, sys.argv[3])
from chess_move_trainer.database.stockfish import DatabaseMutex

mutex = DatabaseMutex(sys.argv[1], acquire_timeout=5)
if not mutex.acquire():
    raise SystemExit(2)
Path(sys.argv[2]).write_text("acquired", encoding="ascii")
if sys.argv[4] == "crash":
    time.sleep(10)
try:
    time.sleep(10)
finally:
    mutex.release()
"""
    return subprocess.Popen(
        [sys.executable, "-c", code, str(database_path), str(signal_path), str(ROOT), action],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _wait_for_signal(signal_path: Path, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if signal_path.exists():
            return
        if process.poll() is not None:
            break
        time.sleep(0.01)
    process.kill()
    process.wait(timeout=5)
    raise AssertionError("mutex child did not acquire within the finite test timeout")


def test_mutex_name_uses_one_normalized_database_identity(tmp_path: Path) -> None:
    database_path = tmp_path / "db.sqlite"
    equivalent = tmp_path / "folder" / ".." / "db.sqlite"

    assert normalize_database_path(database_path) == normalize_database_path(equivalent)
    assert mutex_name_for_database(database_path) == mutex_name_for_database(equivalent)
    assert mutex_name_for_database(database_path).startswith("Local\\ChessMoveTrainer.Stockfish.")


def test_clean_release_allows_the_next_owner(tmp_path: Path) -> None:
    database_path = tmp_path / "clean-release.db"
    first = DatabaseMutex(database_path)
    second = DatabaseMutex(database_path)

    assert first.acquire(timeout=0)
    first.release()
    assert second.acquire(timeout=1)
    second.release()


def test_real_child_owner_is_busy_then_kernel_releases_on_process_death(tmp_path: Path) -> None:
    database_path = tmp_path / "child-owner.db"
    signal_path = tmp_path / "child-owner.signal"
    child = _child_process(database_path, signal_path, "hold")
    _wait_for_signal(signal_path, child)
    try:
        assert not DatabaseMutex(database_path).acquire(timeout=0.05)
    finally:
        child.kill()
        child.wait(timeout=5)

    released = DatabaseMutex(database_path)
    assert released.acquire(timeout=1)
    released.release()


def test_abandoned_child_acquisition_is_reported_as_acquired(tmp_path: Path) -> None:
    database_path = tmp_path / "abandoned-owner.db"
    signal_path = tmp_path / "abandoned-owner.signal"
    child = _child_process(database_path, signal_path, "crash")
    _wait_for_signal(signal_path, child)
    child.kill()
    child.wait(timeout=5)

    recovered = DatabaseMutex(database_path)
    assert recovered.acquire(timeout=1)
    assert recovered.acquired_abandoned
    assert recovered.owned
    recovered.release()
