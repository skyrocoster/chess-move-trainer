from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.preferred_moves import (
    Preference,
    PreferredMoveLockError,
    PreferredMoveMutationRequest,
    PreferredMoveRemovalRequest,
    PreferredMoveRepository,
    PreferredMoveStorageError,
    PreferredMoveValidationError,
    delete_preferred_move,
    put_preferred_move,
)

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
STARTING_WITH_COUNTERS = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 73 42"
)
AFTER_E4_WITH_UNUSED_EP = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 17 8"
)
AFTER_E4_CANONICAL = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
)
MOVE_E4 = Preference.preferred_move("e2e4")
MOVE_D4 = Preference.preferred_move("d2d4")
NO_PREFERENCE = Preference.no_preference()


def _database(tmp_path: Path) -> Path:
    database = tmp_path / "mutation.db"
    create_schema(database)
    return database


def _request(
    fen: str = STARTING_FEN,
    effective_from: str = "2026-01-01",
    effective_until: str | None = None,
    preference: Preference = MOVE_E4,
) -> PreferredMoveMutationRequest:
    return PreferredMoveMutationRequest(
        fen, effective_from, effective_until, preference
    )


def _removal_request(
    fen: str = STARTING_FEN,
    effective_from: str = "2026-01-01",
    effective_until: str | None = None,
) -> PreferredMoveRemovalRequest:
    return PreferredMoveRemovalRequest(fen, effective_from, effective_until)


def _period_values(repository: PreferredMoveRepository) -> list[tuple[str, str | None, str | None]]:
    return [
        (
            period.effective_from.isoformat(),
            None if period.effective_until is None else period.effective_until.isoformat(),
            period.preference.move,
        )
        for period in repository.list_periods(STARTING_FEN[:-4])
    ]


def test_put_canonicalizes_counters_and_legal_en_passant_and_creates_parent(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)

    result = put_preferred_move(
        database,
        _request(STARTING_WITH_COUNTERS, "2026-01-01", "2026-02-01"),
    )

    assert result.fen == STARTING_FEN
    assert result.effective_from == "2026-01-01"
    assert result.effective_until == "2026-02-01"
    assert result.preference == MOVE_E4
    assert len(result.periods) == 1
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1

    ep_result = put_preferred_move(
        database,
        _request(AFTER_E4_WITH_UNUSED_EP, "2026-02-01", "2026-03-01", NO_PREFERENCE),
    )
    assert ep_result.fen == AFTER_E4_CANONICAL
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 2


def test_no_preference_is_a_configured_null_period(tmp_path: Path) -> None:
    database = _database(tmp_path)

    result = put_preferred_move(
        database,
        _request(
            effective_from="2026-01-01",
            effective_until="2026-02-01",
            preference=NO_PREFERENCE,
        ),
    )

    assert result.periods[0].preference == NO_PREFERENCE
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT dpm_move_uci FROM datasource_preferred_move_period"
        ).fetchone()[0] is None


def test_delete_canonicalizes_and_creates_an_unseen_parent_without_a_period(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)

    result = delete_preferred_move(
        database,
        _removal_request(AFTER_E4_WITH_UNUSED_EP, "2026-01-01", "2026-02-01"),
    )
    repeated = delete_preferred_move(
        database,
        _removal_request(AFTER_E4_CANONICAL, "2026-01-01", "2026-02-01"),
    )

    assert result.fen == AFTER_E4_CANONICAL
    assert result.effective_from == "2026-01-01"
    assert result.effective_until == "2026-02-01"
    assert result.periods == ()
    assert repeated == result
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 0


def test_delete_removes_move_and_no_preference_coverage_with_split_fragments(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    put_preferred_move(
        database,
        _request(
            effective_from="2026-01-01",
            effective_until="2026-04-01",
            preference=MOVE_E4,
        ),
    )
    put_preferred_move(
        database,
        _request(
            effective_from="2026-04-01",
            effective_until="2026-06-01",
            preference=NO_PREFERENCE,
        ),
    )
    put_preferred_move(
        database,
        _request(
            effective_from="2026-06-01",
            preference=MOVE_D4,
        ),
    )

    result = delete_preferred_move(
        database,
        _removal_request(effective_from="2026-02-01", effective_until="2026-05-01"),
    )

    assert [
        (
            period.effective_from.isoformat(),
            None if period.effective_until is None else period.effective_until.isoformat(),
            period.preference.move,
        )
        for period in result.periods
    ] == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-05-01", "2026-06-01", None),
        ("2026-06-01", None, "d2d4"),
    ]
    assert (
        PreferredMoveRepository(database).resolve(STARTING_FEN[:-4], "2026-04-15").state.value
        == "unconfigured"
    )


def test_delete_shortens_fully_removes_and_repeats_as_a_no_op(tmp_path: Path) -> None:
    database = _database(tmp_path)
    put_preferred_move(
        database,
        _request(
            effective_from="2026-01-01",
            effective_until="2026-04-01",
            preference=MOVE_E4,
        ),
    )

    shortened = delete_preferred_move(
        database,
        _removal_request(effective_from="2026-01-01", effective_until="2026-02-01"),
    )
    empty = delete_preferred_move(
        database,
        _removal_request(effective_from="2026-02-01", effective_until="2026-04-01"),
    )
    repeated = delete_preferred_move(
        database,
        _removal_request(effective_from="2026-02-01", effective_until="2026-04-01"),
    )
    nonintersecting = delete_preferred_move(
        database,
        _removal_request(effective_from="2027-01-01", effective_until="2027-02-01"),
    )

    assert [
        (period.effective_from.isoformat(), period.effective_until.isoformat())
        for period in shortened.periods
    ] == [("2026-02-01", "2026-04-01")]
    assert empty.periods == ()
    assert repeated == empty
    assert nonintersecting.periods == ()
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 0


def test_delete_open_end_shortens_an_indefinite_period(tmp_path: Path) -> None:
    database = _database(tmp_path)
    put_preferred_move(
        database,
        _request(effective_from="2026-01-01", preference=MOVE_E4),
    )

    result = delete_preferred_move(
        database,
        _removal_request(effective_from="2026-03-01"),
    )

    assert [
        (
            period.effective_from.isoformat(),
            None if period.effective_until is None else period.effective_until.isoformat(),
            period.preference.move,
        )
        for period in result.periods
    ] == [("2026-01-01", "2026-03-01", "e2e4")]


@pytest.mark.parametrize(
    ("fen", "effective_from", "effective_until"),
    [
        (STARTING_FEN[:-4], "2026-01-01", "2026-02-01"),
        ("not a FEN", "2026-01-01", "2026-02-01"),
        (STARTING_FEN, "2026-1-01", "2026-02-01"),
        (STARTING_FEN, "2026-01-01", "2026-02-30"),
        (STARTING_FEN, "2026-02-01", "2026-01-01"),
    ],
)
def test_delete_request_rejects_invalid_fen_and_interval_before_storage(
    tmp_path: Path,
    fen: str,
    effective_from: str,
    effective_until: str,
) -> None:
    database = _database(tmp_path)

    with pytest.raises(PreferredMoveValidationError):
        delete_preferred_move(
            database,
            _removal_request(fen, effective_from, effective_until),
        )

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0


@pytest.mark.parametrize(
    ("effective_from", "effective_until"),
    [
        ("2026-1-01", "2026-02-01"),
        ("2026-02-30", "2026-03-01"),
        ("2026-01-01T00:00:00Z", "2026-02-01"),
        ("2026-01-01", "2026-1-02"),
        ("2026-01-01", "2026-01-01"),
        ("2026-02-01", "2026-01-01"),
    ],
)
def test_strict_dates_are_rejected_before_any_write(
    tmp_path: Path,
    effective_from: str,
    effective_until: str,
) -> None:
    database = _database(tmp_path)
    with pytest.raises(PreferredMoveValidationError):
        put_preferred_move(
            database,
            _request(
                effective_from=effective_from,
                effective_until=effective_until,
            ),
        )

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 0


@pytest.mark.parametrize(
    ("move", "message"),
    [("not-uci", "UCI move is invalid"), ("e2e5", "Move is illegal from the parent FEN")],
)
def test_invalid_uci_and_illegal_move_are_distinct_and_do_not_write(
    tmp_path: Path,
    move: str,
    message: str,
) -> None:
    database = _database(tmp_path)
    with pytest.raises(PreferredMoveValidationError, match=message):
        put_preferred_move(database, _request(preference=Preference.preferred_move(move)))

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0


def test_overlay_returns_complete_normalized_schedule_and_repeats_are_idempotent(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)

    put_preferred_move(
        database,
        _request(
            effective_from="2026-01-01",
            effective_until="2026-04-01",
            preference=MOVE_E4,
        ),
    )
    result = put_preferred_move(
        database,
        _request(effective_from="2026-02-01", effective_until="2026-03-01", preference=MOVE_D4),
    )
    repeated = put_preferred_move(
        database,
        _request(effective_from="2026-02-01", effective_until="2026-03-01", preference=MOVE_D4),
    )

    assert [
        (
            period.effective_from.isoformat(),
            None if period.effective_until is None else period.effective_until.isoformat(),
            period.preference.move,
        )
        for period in result.periods
    ] == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-02-01", "2026-03-01", "d2d4"),
        ("2026-03-01", "2026-04-01", "e2e4"),
    ]
    assert repeated == result


def test_failure_after_replacement_rolls_back_the_schedule(tmp_path: Path) -> None:
    database = _database(tmp_path)
    original = put_preferred_move(
        database,
        _request(effective_from="2026-01-01", preference=MOVE_E4),
    )

    def checkpoint(name: str) -> None:
        if name == "replaced":
            raise RuntimeError("injected after replacement")

    with pytest.raises(PreferredMoveStorageError):
        put_preferred_move(
            database,
            _request(effective_from="2026-02-01", effective_until="2026-03-01", preference=MOVE_D4),
            _checkpoint=checkpoint,
        )

    assert PreferredMoveRepository(database).list_periods(STARTING_FEN[:-4]) == original.periods


def test_delete_failure_after_replacement_rolls_back_the_schedule(tmp_path: Path) -> None:
    database = _database(tmp_path)
    original = put_preferred_move(
        database,
        _request(effective_from="2026-01-01", preference=MOVE_E4),
    )

    def checkpoint(name: str) -> None:
        if name == "replaced":
            raise RuntimeError("injected after replacement")

    with pytest.raises(PreferredMoveStorageError):
        delete_preferred_move(
            database,
            _removal_request(effective_from="2026-02-01", effective_until="2026-03-01"),
            _checkpoint=checkpoint,
        )

    assert PreferredMoveRepository(database).list_periods(STARTING_FEN[:-4]) == original.periods


def test_delete_rejects_malformed_persisted_move_before_replacement(tmp_path: Path) -> None:
    database = _database(tmp_path)
    put_preferred_move(database, _request(effective_from="2026-01-01", preference=MOVE_E4))
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            "UPDATE datasource_preferred_move_period SET dpm_move_uci = 'e2e5'"
        )

    with pytest.raises(PreferredMoveStorageError):
        delete_preferred_move(
            database,
            _removal_request(effective_from="2026-02-01", effective_until="2026-03-01"),
        )

    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT dpm_move_uci FROM datasource_preferred_move_period"
        ).fetchone()[0] == "e2e5"


def test_delete_writer_lock_failure_is_bounded_and_does_not_create_parent(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    blocker = sqlite3.connect(database, isolation_level=None, timeout=0.2)
    blocker.execute("PRAGMA busy_timeout = 200")
    blocker.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(PreferredMoveLockError):
            delete_preferred_move(
                database,
                _removal_request(effective_from="2026-01-01", effective_until="2026-02-01"),
                lock_timeout=0.05,
            )
    finally:
        blocker.rollback()
        blocker.close()

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0


def test_malformed_persisted_move_is_rejected_before_replacement(tmp_path: Path) -> None:
    database = _database(tmp_path)
    put_preferred_move(
        database,
        _request(effective_from="2026-01-01", preference=MOVE_E4),
    )
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            "UPDATE datasource_preferred_move_period SET dpm_move_uci = 'e2e5'"
        )

    with pytest.raises(PreferredMoveStorageError):
        put_preferred_move(
            database,
            _request(effective_from="2026-02-01", preference=MOVE_D4),
        )

    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT dpm_move_uci FROM datasource_preferred_move_period"
        ).fetchone()[0] == "e2e5"


def test_writer_lock_failure_is_bounded_and_does_not_create_parent(tmp_path: Path) -> None:
    database = _database(tmp_path)
    blocker = sqlite3.connect(database, isolation_level=None, timeout=0.2)
    blocker.execute("PRAGMA busy_timeout = 200")
    blocker.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(PreferredMoveLockError):
            put_preferred_move(
                database,
                _request(effective_from="2026-01-01", preference=MOVE_E4),
                lock_timeout=0.05,
            )
    finally:
        blocker.rollback()
        blocker.close()

    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0


def _run_concurrent_mutations(
    database: Path,
    first_range: tuple[str, str | None],
    second_range: tuple[str, str | None],
) -> PreferredMoveRepository:
    first_locked = threading.Event()
    release_first = threading.Event()
    errors: list[BaseException] = []

    def first_checkpoint(name: str) -> None:
        if name == "locked":
            first_locked.set()
            if not release_first.wait(3.0):
                raise RuntimeError("timed out waiting for first writer")

    def write(
        date_range: tuple[str, str | None],
        preference: Preference,
        checkpoint: object | None,
    ) -> None:
        try:
            put_preferred_move(
                database,
                _request(
                    effective_from=date_range[0],
                    effective_until=date_range[1],
                    preference=preference,
                ),
                lock_timeout=2.0,
                _checkpoint=checkpoint,
            )
        except BaseException as error:
            errors.append(error)

    first = threading.Thread(
        target=write,
        args=(first_range, MOVE_E4, first_checkpoint),
        daemon=True,
    )
    second = threading.Thread(
        target=write,
        args=(second_range, MOVE_D4, None),
        daemon=True,
    )
    first.start()
    assert first_locked.wait(3.0)
    second.start()
    release_first.set()
    first.join(timeout=3.0)
    second.join(timeout=3.0)
    assert not first.is_alive()
    assert not second.is_alive()
    assert not errors
    return PreferredMoveRepository(database)


def test_concurrent_overlapping_mutations_use_the_latest_schedule(tmp_path: Path) -> None:
    database = _database(tmp_path)
    repository = _run_concurrent_mutations(
        database,
        ("2026-01-01", "2026-05-01"),
        ("2026-02-01", "2026-04-01"),
    )

    assert _period_values(repository) == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-02-01", "2026-04-01", "d2d4"),
        ("2026-04-01", "2026-05-01", "e2e4"),
    ]


def test_concurrent_non_overlapping_mutations_both_survive(tmp_path: Path) -> None:
    database = _database(tmp_path)
    repository = _run_concurrent_mutations(
        database,
        ("2026-01-01", "2026-02-01"),
        ("2026-03-01", "2026-04-01"),
    )

    assert _period_values(repository) == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-03-01", "2026-04-01", "d2d4"),
    ]
