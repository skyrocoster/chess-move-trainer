from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.preferred_moves.ranges import (
    DateResolution,
    Preference,
    ResolutionState,
)
from chess_move_trainer.database.preferred_moves.repository import (
    PreferredMoveRepository,
    PreferredMoveSchemaError,
    PreferredMoveStorageError,
    PreferredMoveValidationError,
)

STARTING_PLACEMENT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = f"{STARTING_PLACEMENT} w KQkq -"
AFTER_E4_WITH_UNUSED_EP = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3"
)
AFTER_E4_WITHOUT_EP = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -"
)
MOVE_E4 = Preference.preferred_move("e2e4")
MOVE_D4 = Preference.preferred_move("d2d4")
NO_PREFERENCE = Preference.no_preference()


def repository(tmp_path: Path, name: str = "preferred.db") -> PreferredMoveRepository:
    database_path = tmp_path / name
    create_schema(database_path)
    return PreferredMoveRepository(database_path)


def test_only_explicit_existing_exact_v1_database_is_accepted(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    incompatible = tmp_path / "incompatible.db"
    malformed = tmp_path / "malformed.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
        connection.execute("PRAGMA user_version = 1")
    malformed.write_bytes(b"not a SQLite database")

    with pytest.raises(PreferredMoveStorageError):
        PreferredMoveRepository(missing).list_periods(STARTING_FEN)
    with pytest.raises(PreferredMoveSchemaError):
        PreferredMoveRepository(incompatible).list_periods(STARTING_FEN)
    with pytest.raises(PreferredMoveStorageError):
        PreferredMoveRepository(malformed).list_periods(STARTING_FEN)

    assert not missing.exists()


@pytest.mark.parametrize(
    "fen",
    [
        f"{STARTING_FEN} 0 1",
        STARTING_PLACEMENT,
        "not a FEN input",
        f"{STARTING_PLACEMENT} w KQkq impossible",
    ],
)
def test_boundary_requires_exactly_four_valid_fen_fields(
    tmp_path: Path, fen: str
) -> None:
    service = repository(tmp_path, "four-fields.db")
    with pytest.raises(PreferredMoveValidationError):
        service.list_periods(fen)


def test_unknown_reads_are_empty_and_unconfigured_without_creating_rows(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "read-only-behavior.db"
    service = repository(tmp_path, database_path.name)

    assert service.list_periods(STARTING_FEN) == ()
    assert service.resolve(STARTING_FEN, "2026-01-01") == DateResolution(
        ResolutionState.UNCONFIGURED
    )

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 0


def test_standalone_write_creates_position_and_schedule_together(tmp_path: Path) -> None:
    database_path = tmp_path / "standalone.db"
    service = repository(tmp_path, database_path.name)

    result = service.set(STARTING_FEN, "2026-01-01", None, MOVE_E4)

    assert result == service.list_periods(STARTING_FEN)
    assert service.resolve(STARTING_FEN, "2099-01-01") == DateResolution(
        ResolutionState.PREFERRED_MOVE, "e2e4"
    )
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 1


def test_legal_only_en_passant_canonicalization_reuses_one_position(tmp_path: Path) -> None:
    database_path = tmp_path / "canonical-ep.db"
    service = repository(tmp_path, database_path.name)

    service.set(AFTER_E4_WITH_UNUSED_EP, "2026-01-01", None, NO_PREFERENCE)

    assert service.list_periods(AFTER_E4_WITHOUT_EP) == service.list_periods(
        AFTER_E4_WITH_UNUSED_EP
    )
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1
        assert connection.execute(
            "SELECT dp_legal_en_passant FROM derived_position"
        ).fetchone()[0] == "-"


@pytest.mark.parametrize("move", ["e2e5", "not-uci", "e7e5"])
def test_non_null_move_must_be_valid_uci_and_legal(
    tmp_path: Path, move: str
) -> None:
    database_path = tmp_path / f"illegal-{move}.db"
    service = repository(tmp_path, database_path.name)

    with pytest.raises(PreferredMoveValidationError):
        service.set(
            STARTING_FEN,
            "2026-01-01",
            None,
            Preference.preferred_move(move),
        )

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0


def test_persisted_amendments_reload_as_one_normalized_current_schedule(
    tmp_path: Path,
) -> None:
    service = repository(tmp_path, "amendments.db")

    service.set(STARTING_FEN, "2026-02-01", "2026-04-01", MOVE_E4)
    service.set(STARTING_FEN, "2026-01-01", "2026-03-01", MOVE_E4)
    service.set(STARTING_FEN, "2026-02-01", "2026-03-01", MOVE_D4)
    service.set(STARTING_FEN, "2026-02-15", "2026-02-20", NO_PREFERENCE)
    service.unset(STARTING_FEN, "2026-02-16", "2026-02-19")
    service.set(STARTING_FEN, "2026-04-01", None, MOVE_E4)

    assert [
        (
            item.effective_from.isoformat(),
            None if item.effective_until is None else item.effective_until.isoformat(),
            item.preference.move,
        )
        for item in service.list_periods(STARTING_FEN)
    ] == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-02-01", "2026-02-15", "d2d4"),
        ("2026-02-15", "2026-02-16", None),
        ("2026-02-19", "2026-02-20", None),
        ("2026-02-20", "2026-03-01", "d2d4"),
        ("2026-03-01", None, "e2e4"),
    ]


@pytest.mark.parametrize("failure", [RuntimeError("injected"), KeyboardInterrupt()])
def test_failure_or_interruption_rolls_back_standalone_position_and_period(
    tmp_path: Path, failure: BaseException
) -> None:
    database_path = tmp_path / f"rollback-{type(failure).__name__}.db"
    create_schema(database_path)

    def checkpoint(name: str) -> None:
        if name == "position":
            raise failure

    service = PreferredMoveRepository(database_path, _checkpoint=checkpoint)
    if isinstance(failure, KeyboardInterrupt):
        expected = KeyboardInterrupt
    else:
        expected = PreferredMoveStorageError
    with pytest.raises(expected):
        service.set(STARTING_FEN, "2026-01-01", None, MOVE_E4)

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 0


def test_failed_replacement_restores_the_preexisting_schedule(tmp_path: Path) -> None:
    database_path = tmp_path / "replacement-rollback.db"
    service = repository(tmp_path, database_path.name)
    original = service.set(STARTING_FEN, "2026-01-01", None, MOVE_E4)

    def checkpoint(name: str) -> None:
        if name == "replaced":
            raise RuntimeError("injected after replacement")

    failing = PreferredMoveRepository(database_path, _checkpoint=checkpoint)
    with pytest.raises(PreferredMoveStorageError):
        failing.set(STARTING_FEN, "2026-02-01", "2026-03-01", MOVE_D4)

    assert service.list_periods(STARTING_FEN) == original


def test_repository_exposes_no_connection_handle(tmp_path: Path) -> None:
    service = repository(tmp_path, "opaque.db")
    assert not hasattr(service, "connection")
    assert not hasattr(service, "raw_connection")
