from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import (
    DEFAULT_LOCK_TIMEOUT_SECONDS,
    ConnectionProbe,
    probe_connection,
)
from chess_move_trainer.database.connection import _create_sqlite_connection, _open_connection


def test_read_write_probe_creates_an_explicit_database_with_safe_settings(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "trainer.db"

    probe = probe_connection(database_path, mode="read-write")

    assert database_path.is_file()
    assert isinstance(probe, ConnectionProbe)
    assert probe.database_path == database_path
    assert probe.access_mode == "read-write"
    assert probe.foreign_keys_enabled is True
    assert probe.busy_timeout_ms == 5000
    assert probe.journal_mode == "delete"


def test_read_only_access_never_creates_a_missing_target(tmp_path: Path) -> None:
    existing_path = tmp_path / "existing.db"
    with sqlite3.connect(existing_path) as connection:
        connection.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY)")

    probe = probe_connection(existing_path, mode="read-only")

    assert probe.access_mode == "read-only"
    assert probe.foreign_keys_enabled is True
    assert probe.busy_timeout_ms == 5000

    missing_path = tmp_path / "missing.db"
    with pytest.raises(FileNotFoundError):
        probe_connection(missing_path, mode="read-only")
    assert not missing_path.exists()


def test_parent_path_must_exist_and_be_a_directory(tmp_path: Path) -> None:
    missing_parent_path = tmp_path / "missing" / "trainer.db"
    with pytest.raises(FileNotFoundError):
        probe_connection(missing_parent_path)

    parent_file = tmp_path / "not-a-directory"
    parent_file.write_text("not a directory", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        probe_connection(parent_file / "trainer.db")


@pytest.mark.parametrize("lock_timeout", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_lock_timeout_override_must_be_finite_and_positive(
    tmp_path: Path,
    lock_timeout: float,
) -> None:
    with pytest.raises(ValueError):
        probe_connection(tmp_path / "trainer.db", lock_timeout=lock_timeout)


def test_default_lock_timeout_is_exactly_five_seconds() -> None:
    assert DEFAULT_LOCK_TIMEOUT_SECONDS == 5.0


def test_connection_probe_returns_only_ordinary_package_data(tmp_path: Path) -> None:
    probe = probe_connection(tmp_path / "trainer.db")

    assert isinstance(probe.database_path, Path)
    assert type(probe.access_mode) is str
    assert type(probe.foreign_keys_enabled) is bool
    assert type(probe.busy_timeout_ms) is int
    assert type(probe.journal_mode) is str
    assert not hasattr(probe, "exec_driver_sql")


def test_internal_factory_configures_before_yielding_a_clean_connection(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "factory.db"

    raw_connection = _create_sqlite_connection(
        database_path,
        "read-write",
        DEFAULT_LOCK_TIMEOUT_SECONDS,
    )
    try:
        assert raw_connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        raw_connection.close()

    with _open_connection(database_path, "read-write", DEFAULT_LOCK_TIMEOUT_SECONDS) as connection:
        assert connection.in_transaction() is False
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1


def test_internal_factory_preserves_an_existing_non_default_journal_mode(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "journal.db"
    with sqlite3.connect(database_path) as connection:
        journal_mode = connection.execute("PRAGMA journal_mode = WAL").fetchone()[0]
    assert journal_mode.lower() == "wal"

    probe = probe_connection(database_path)

    assert probe.journal_mode.lower() == "wal"
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
