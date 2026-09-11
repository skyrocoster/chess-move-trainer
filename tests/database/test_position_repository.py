from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import (
    PositionRepository,
    PositionStorageError,
    PositionValidationError,
)
from chess_move_trainer.database.schema import SchemaIncompatibleError

STARTING_PLACEMENT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = f"{STARTING_PLACEMENT} w KQkq - 0 1"
LEGAL_EN_PASSANT_FEN = (
    "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"
)


def test_only_an_existing_compatible_v1_database_is_accepted(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.db"
    empty = tmp_path / "empty.db"
    sqlite3.connect(empty).close()

    nonempty_v0 = tmp_path / "nonempty-v0.db"
    with sqlite3.connect(nonempty_v0) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")

    mismatched_v1 = tmp_path / "mismatched-v1.db"
    with sqlite3.connect(mismatched_v1) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
        connection.execute("PRAGMA user_version = 1")

    malformed = tmp_path / "malformed.db"
    malformed.write_bytes(b"not a SQLite database")

    expected_errors = {
        missing: FileNotFoundError,
        empty: SchemaIncompatibleError,
        nonempty_v0: SchemaIncompatibleError,
        mismatched_v1: SchemaIncompatibleError,
        malformed: PositionStorageError,
    }
    original_bytes = {path: path.read_bytes() for path in expected_errors if path.exists()}

    for path, error_type in expected_errors.items():
        with pytest.raises(error_type):
            PositionRepository(path).resolve_fen(STARTING_FEN)

    assert not missing.exists()
    for path, before in original_bytes.items():
        assert path.read_bytes() == before


def test_repeated_resolution_and_reopen_return_one_stable_integer_id(tmp_path: Path) -> None:
    database_path = tmp_path / "positions.db"
    create_schema(database_path)
    repository = PositionRepository(database_path)

    first_id = repository.resolve_fen(STARTING_FEN)
    second_id = repository.resolve_fen(f"{STARTING_PLACEMENT} w KQkq - 99 120")
    reopened_id = PositionRepository(database_path).resolve_fen(STARTING_FEN)

    assert type(first_id) is int
    assert first_id == second_id == reopened_id
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1


def test_each_identity_field_distinguishes_rows(tmp_path: Path) -> None:
    database_path = tmp_path / "identity-fields.db"
    create_schema(database_path)
    repository = PositionRepository(database_path)

    ids = {
        "base": repository.resolve_fen(STARTING_FEN),
        "placement": repository.resolve_fen(
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        ),
        "side": repository.resolve_fen(f"{STARTING_PLACEMENT} b KQkq - 0 1"),
        "castling": repository.resolve_fen(f"{STARTING_PLACEMENT} w - - 0 1"),
        "en_passant": repository.resolve_fen(LEGAL_EN_PASSANT_FEN),
    }

    assert len(set(ids.values())) == 5
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 5


def test_invalid_input_reaches_no_write_path(tmp_path: Path) -> None:
    database_path = tmp_path / "invalid-input.db"
    create_schema(database_path)

    with pytest.raises(PositionValidationError):
        PositionRepository(database_path).resolve_fen("not a FEN")

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0


def test_repository_has_no_update_delete_or_raw_handle_contract(tmp_path: Path) -> None:
    database_path = tmp_path / "opaque.db"
    create_schema(database_path)
    repository = PositionRepository(database_path)

    assert not hasattr(repository, "connection")
    assert not hasattr(repository, "raw_connection")
    assert not hasattr(repository, "update")
    assert not hasattr(repository, "delete")
    assert not hasattr(repository, "cleanup")
