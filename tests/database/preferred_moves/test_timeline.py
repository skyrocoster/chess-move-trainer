from __future__ import annotations

import sqlite3
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.preferred_moves import (
    PreferredMoveTimeline,
    PreferredMoveTimelinePreference,
    PreferredMoveTimelineRepository,
    PreferredMoveTimelineRequest,
    PreferredMoveTimelineSegment,
    PreferredMoveRemovalRequest,
    delete_preferred_move,
    read_preferred_moves,
)
from chess_move_trainer.database.preferred_moves.ranges import Preference
from chess_move_trainer.database.preferred_moves.repository import (
    PreferredMoveLockError,
    PreferredMoveSchemaError,
    PreferredMoveStorageError,
    PreferredMoveValidationError,
    PreferredMoveRepository,
)


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
STARTING_FEN_WITH_COUNTERS = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 73 42"
)
AFTER_E4_WITH_EP = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 17 8"
)
MOVE_E4 = Preference.preferred_move("e2e4")
MOVE_D4 = Preference.preferred_move("d2d4")
NO_PREFERENCE = Preference.no_preference()


def _database(tmp_path: Path, name: str = "timeline.db") -> Path:
    database = tmp_path / name
    create_schema(database)
    return database


def _configured_database(tmp_path: Path) -> Path:
    database = _database(tmp_path)
    repository = PreferredMoveRepository(database)
    repository.set(STARTING_FEN[:-4], "2026-01-01", "2026-02-01", MOVE_E4)
    repository.set(STARTING_FEN[:-4], "2026-03-01", "2026-04-01", NO_PREFERENCE)
    repository.set(STARTING_FEN[:-4], "2026-04-01", "2026-05-01", NO_PREFERENCE)
    repository.set(STARTING_FEN[:-4], "2026-05-01", None, MOVE_D4)
    return database


def _request(
    from_date: str = "2025-12-01", until: str = "2026-06-01"
) -> PreferredMoveTimelineRequest:
    return PreferredMoveTimelineRequest(STARTING_FEN, from_date, until)


def _segment_values(timeline: PreferredMoveTimeline) -> list[tuple[str, str, str, str | None]]:
    return [
        (
            segment.from_date,
            segment.until,
            segment.preference.kind,
            segment.preference.uci,
        )
        for segment in timeline.segments
    ]


def test_request_canonicalizes_counters_and_legal_en_passant_identity() -> None:
    request = PreferredMoveTimelineRequest(STARTING_FEN_WITH_COUNTERS, "2026-01-01", "2026-02-01")
    assert request.fen == STARTING_FEN

    ep_request = PreferredMoveTimelineRequest(AFTER_E4_WITH_EP, "2026-01-01", "2026-02-01")
    assert ep_request.fen.endswith(" b KQkq - 0 1")


@pytest.mark.parametrize(
    ("fen", "from_date", "until"),
    [
        ("not a FEN", "2026-01-01", "2026-02-01"),
        (STARTING_FEN, "2026-1-01", "2026-02-01"),
        (STARTING_FEN, "2026-02-01", "2026-02-30"),
        (STARTING_FEN, "2026-02-01", "2026-02-01"),
        (STARTING_FEN, "2026-03-01", "2026-02-01"),
        (STARTING_FEN, "2026-01-01T00:00:00Z", "2026-02-01"),
    ],
)
def test_request_rejects_invalid_fen_dates_and_window(
    fen: str, from_date: str, until: str
) -> None:
    with pytest.raises(PreferredMoveValidationError):
        PreferredMoveTimelineRequest(fen, from_date, until)


def test_timeline_clips_gaps_merges_adjacent_equal_values_and_covers_window(
    tmp_path: Path,
) -> None:
    timeline = read_preferred_moves(_configured_database(tmp_path), _request())

    assert _segment_values(timeline) == [
        ("2025-12-01", "2026-01-01", "unconfigured", None),
        ("2026-01-01", "2026-02-01", "move", "e2e4"),
        ("2026-02-01", "2026-03-01", "unconfigured", None),
        ("2026-03-01", "2026-05-01", "no_preference", None),
        ("2026-05-01", "2026-06-01", "move", "d2d4"),
    ]
    assert timeline.fen == STARTING_FEN
    assert timeline.from_date == "2025-12-01"
    assert timeline.until == "2026-06-01"
    assert timeline.segments[0].from_ == timeline.from_date
    assert timeline.segments[-1].until_date == timeline.until


def test_timeline_respects_half_open_edges_and_clips_open_ended_period(
    tmp_path: Path,
) -> None:
    database = _configured_database(tmp_path)
    repository = PreferredMoveTimelineRepository(database)

    at_boundary = repository.read(_request("2026-02-01", "2026-03-01"))
    assert _segment_values(at_boundary) == [
        ("2026-02-01", "2026-03-01", "unconfigured", None)
    ]

    open_ended = repository.read(_request("2026-05-01", "2026-05-15"))
    assert _segment_values(open_ended) == [
        ("2026-05-01", "2026-05-15", "move", "d2d4")
    ]


def test_delete_is_immediately_visible_as_unconfigured_in_the_timeline(
    tmp_path: Path,
) -> None:
    database = _configured_database(tmp_path)

    delete_preferred_move(
        database,
        PreferredMoveRemovalRequest(STARTING_FEN, "2026-01-01", "2026-02-01"),
    )

    timeline = PreferredMoveTimelineRepository(database).read(
        _request("2026-01-01", "2026-03-01")
    )
    assert _segment_values(timeline) == [
        ("2026-01-01", "2026-03-01", "unconfigured", None)
    ]


def test_empty_and_unseen_schedules_are_one_read_only_unconfigured_segment(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    before = database.read_bytes()

    timeline = PreferredMoveTimelineRepository(database).read(_request())

    assert _segment_values(timeline) == [
        ("2025-12-01", "2026-06-01", "unconfigured", None)
    ]
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("timeline.db-*"))
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 0

    unseen = PreferredMoveTimelineRepository(database).read(
        PreferredMoveTimelineRequest(
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 17 8",
            "2026-01-01",
            "2026-02-01",
        )
    )
    assert _segment_values(unseen) == [
        ("2026-01-01", "2026-02-01", "unconfigured", None)
    ]
    assert database.read_bytes() == before


def test_read_values_are_ordinary_immutable_dataclasses(tmp_path: Path) -> None:
    timeline = PreferredMoveTimelineRepository(_configured_database(tmp_path)).read(_request())

    with pytest.raises(FrozenInstanceError):
        timeline.fen = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        timeline.segments[0] = timeline.segments[0]  # type: ignore[index]
    assert isinstance(timeline.segments[0], PreferredMoveTimelineSegment)
    assert isinstance(timeline.segments[0].preference, PreferredMoveTimelinePreference)


@pytest.mark.parametrize(
    "mutation",
    [
        "UPDATE datasource_preferred_move_period SET dpm_effective_from = '2026-02-30' WHERE dpm_effective_from = '2026-01-01'",
        "UPDATE datasource_preferred_move_period SET dpm_move_uci = 'e2e5'",
    ],
)
def test_malformed_persisted_schedule_is_unavailable(
    tmp_path: Path, mutation: str
) -> None:
    database = _configured_database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(mutation)

    with pytest.raises(PreferredMoveStorageError):
        PreferredMoveTimelineRepository(database).read(_request())


def test_missing_incompatible_and_unreadable_storage_are_typed_failures(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.db"
    with pytest.raises(PreferredMoveStorageError):
        PreferredMoveTimelineRepository(missing).read(_request())
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    with pytest.raises(PreferredMoveSchemaError):
        PreferredMoveTimelineRepository(incompatible).read(_request())

    unreadable = tmp_path / "unreadable.db"
    unreadable.write_bytes(b"not a SQLite database")
    with pytest.raises(PreferredMoveStorageError):
        PreferredMoveTimelineRepository(unreadable).read(_request())


def test_locked_storage_fails_with_the_finite_read_timeout(tmp_path: Path) -> None:
    database = _database(tmp_path)
    blocker = sqlite3.connect(database, isolation_level=None, timeout=0.2)
    blocker.execute("PRAGMA busy_timeout = 200")
    blocker.execute("BEGIN EXCLUSIVE")
    try:
        with pytest.raises(PreferredMoveLockError):
            PreferredMoveTimelineRepository(database, lock_timeout=0.05).read(_request())
    finally:
        blocker.rollback()
        blocker.close()
