from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import DEFAULT_LOCK_TIMEOUT_SECONDS
from chess_move_trainer.database import schema as schema_service
from chess_move_trainer.database.connection import _open_existing_connection
from chess_move_trainer.database.schema import (
    SchemaIncompatibleError,
    _assert_compatible_schema,
    create_schema,
)


def test_fresh_creation_and_exact_compatible_repeat_are_byte_preserving(tmp_path: Path) -> None:
    database_path = tmp_path / "fresh.db"

    first = create_schema(database_path)
    first_bytes = database_path.read_bytes()
    second = create_schema(database_path)

    assert first.created is True
    assert second.created is False
    assert database_path.read_bytes() == first_bytes


def test_compatible_target_does_not_read_all_existing_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "large-compatible.db"
    create_schema(database_path)
    original_read_bytes = Path.read_bytes

    def reject_target_read(path: Path) -> bytes:
        if path == database_path:
            raise AssertionError("compatible target was read in full")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", reject_target_read)

    result = create_schema(database_path)

    assert result.created is False


def test_an_existing_truly_empty_database_is_initialized(tmp_path: Path) -> None:
    database_path = tmp_path / "empty.db"
    sqlite3.connect(database_path).close()

    result = create_schema(database_path)

    assert result.created is True
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1


@pytest.mark.parametrize("version", [1, 2])
def test_nonempty_or_other_version_targets_are_rejected_unchanged(
    tmp_path: Path,
    version: int,
) -> None:
    database_path = tmp_path / f"version-{version}.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE existing (id INTEGER PRIMARY KEY)")
        connection.execute(f"PRAGMA user_version = {version}")
    original_bytes = database_path.read_bytes()

    with pytest.raises(SchemaIncompatibleError):
        create_schema(database_path)

    assert database_path.read_bytes() == original_bytes


def test_mismatched_v1_target_is_rejected_unchanged(tmp_path: Path) -> None:
    database_path = tmp_path / "mismatch.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
        connection.execute("PRAGMA user_version = 1")
    original_bytes = database_path.read_bytes()

    with pytest.raises(SchemaIncompatibleError):
        create_schema(database_path)

    assert database_path.read_bytes() == original_bytes


def test_malformed_target_is_rejected_unchanged(tmp_path: Path) -> None:
    database_path = tmp_path / "malformed.db"
    original_bytes = b"not a SQLite database"
    database_path.write_bytes(original_bytes)

    with pytest.raises(Exception):
        create_schema(database_path)

    assert database_path.read_bytes() == original_bytes


def test_interrupted_new_creation_removes_only_its_new_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "interrupted-new.db"
    original_execute = schema_service._execute_schema_statement
    statements_seen = 0

    def fail_after_first_statement(connection: object, statement: str) -> None:
        nonlocal statements_seen
        if statements_seen == 0:
            original_execute(connection, statement)
            statements_seen += 1
            return
        raise RuntimeError(f"interrupted at {statement[:20]}")

    monkeypatch.setattr(schema_service, "_execute_schema_statement", fail_after_first_statement)

    with pytest.raises(RuntimeError):
        create_schema(database_path)

    assert statements_seen == 1
    assert not database_path.exists()


def test_interrupted_existing_empty_creation_preserves_the_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "interrupted-existing.db"
    sqlite3.connect(database_path).close()
    original_bytes = database_path.read_bytes()
    original_execute = schema_service._execute_schema_statement
    statements_seen = 0

    def fail_after_first_statement(connection: object, statement: str) -> None:
        nonlocal statements_seen
        if statements_seen == 0:
            original_execute(connection, statement)
            statements_seen += 1
            return
        raise RuntimeError("interrupted")

    monkeypatch.setattr(schema_service, "_execute_schema_statement", fail_after_first_statement)

    with pytest.raises(RuntimeError):
        create_schema(database_path)

    assert statements_seen == 1
    assert database_path.read_bytes() == original_bytes
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall() == []


def test_internal_compatibility_assertion_accepts_v1_and_leaves_connection_clean(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "compatible-existing.db"
    create_schema(database_path)

    with _open_existing_connection(database_path, DEFAULT_LOCK_TIMEOUT_SECONDS) as connection:
        _assert_compatible_schema(connection)

        assert connection.in_transaction() is False
        with connection.begin():
            assert connection.exec_driver_sql("SELECT 1").scalar_one() == 1


def test_internal_compatibility_assertion_rejects_empty_target_without_modification(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "empty-existing.db"
    sqlite3.connect(database_path).close()
    original_bytes = database_path.read_bytes()

    with _open_existing_connection(database_path, DEFAULT_LOCK_TIMEOUT_SECONDS) as connection:
        with pytest.raises(SchemaIncompatibleError):
            _assert_compatible_schema(connection)

    assert database_path.read_bytes() == original_bytes
