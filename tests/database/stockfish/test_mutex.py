from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

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
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
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


def _open_keeper(database_path: Path) -> tuple[Any, Any]:
    """Open one extra handle so the named mutex survives its crashed owner."""

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
    create = kernel32.CreateMutexW
    create.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    create.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_bool
    handle = create(None, False, mutex_name_for_database(database_path))
    assert handle
    return kernel32, handle


def test_mutex_name_uses_one_normalized_database_identity(tmp_path: Path) -> None:
    database_path = tmp_path / "db.sqlite"
    equivalent = tmp_path / "folder" / ".." / "db.sqlite"
    name = mutex_name_for_database(database_path)

    assert normalize_database_path(database_path) == normalize_database_path(equivalent)
    assert name == mutex_name_for_database(equivalent)
    assert name == mutex_name_for_database(tmp_path / "DB.SQLITE")
    assert name != mutex_name_for_database(tmp_path / "other.sqlite")
    assert name.startswith("Local\\ChessMoveTrainer.Stockfish.")


def test_clean_release_allows_the_next_owner(tmp_path: Path) -> None:
    database_path = tmp_path / "clean-release.db"
    first = DatabaseMutex(database_path)

    def acquire_on_another_thread() -> None:
        second = DatabaseMutex(database_path)
        try:
            assert second.acquire(timeout=0)
            assert second.owned
            assert not second.acquired_abandoned
        finally:
            second.release()
        assert not second.owned

    try:
        assert first.acquire(timeout=0)
        assert first.owned
        first.release()
        assert not first.owned
        # Same-thread acquisition is recursive on Windows and cannot prove release.
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(acquire_on_another_thread).result(timeout=5)
    finally:
        first.release()


def test_real_child_owner_is_busy_then_kernel_releases_on_process_death(tmp_path: Path) -> None:
    database_path = tmp_path / "child-owner.db"
    signal_path = tmp_path / "child-owner.signal"
    child = _child_process(database_path, signal_path, "hold")
    contender = DatabaseMutex(database_path)
    try:
        _wait_for_signal(signal_path, child)
        assert not contender.acquire(timeout=0)
        assert not contender.owned
        assert not contender.acquired_abandoned
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)
        contender.release()

    released = DatabaseMutex(database_path)
    try:
        assert released.acquire(timeout=0)
        assert released.owned
    finally:
        released.release()
    assert not released.owned


def test_abandoned_child_acquisition_is_reported_as_acquired(tmp_path: Path) -> None:
    database_path = tmp_path / "abandoned-owner.db"
    signal_path = tmp_path / "abandoned-owner.signal"
    child = _child_process(database_path, signal_path, "crash")
    try:
        _wait_for_signal(signal_path, child)
        keeper_api, keeper_handle = _open_keeper(database_path)
        try:
            child.kill()
            child.wait(timeout=5)

            recovered = DatabaseMutex(database_path)
            try:
                assert recovered.acquire(timeout=0)
                assert recovered.acquired_abandoned
                assert recovered.owned
            finally:
                recovered.release()
            assert not recovered.owned
            assert not recovered.acquired_abandoned
        finally:
            assert keeper_api.CloseHandle(keeper_handle), "Could not close keeper mutex handle"
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)
