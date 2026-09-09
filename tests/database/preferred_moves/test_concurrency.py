from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.preferred_moves import (
    PreferredMoveRemovalRequest,
    delete_preferred_move,
)
from chess_move_trainer.database.preferred_moves.ranges import Preference
from chess_move_trainer.database.preferred_moves.repository import (
    PreferredMoveLockError,
    PreferredMoveRepository,
)


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
STARTING_PUBLIC_FEN = f"{STARTING_FEN} 0 1"
MOVE_E4 = Preference.preferred_move("e2e4")
MOVE_D4 = Preference.preferred_move("d2d4")
WAIT_SECONDS = 3.0


def _period_values(service: PreferredMoveRepository) -> list[tuple[str, str | None, str | None]]:
    return [
        (
            period.effective_from.isoformat(),
            None if period.effective_until is None else period.effective_until.isoformat(),
            period.preference.move,
        )
        for period in service.list_periods(STARTING_FEN)
    ]


def _run_serialized_writers(
    database_path: Path,
    first_range: tuple[str, str | None],
    second_range: tuple[str, str | None],
) -> PreferredMoveRepository:
    first_locked = threading.Event()
    second_attempting = threading.Event()
    release_first = threading.Event()

    def first_checkpoint(name: str) -> None:
        if name == "locked":
            first_locked.set()
            if not release_first.wait(WAIT_SECONDS):
                raise RuntimeError("timed out waiting to release first writer")

    def second_checkpoint(name: str) -> None:
        if name == "before_lock":
            second_attempting.set()

    first = PreferredMoveRepository(
        database_path, lock_timeout=2.0, _checkpoint=first_checkpoint
    )
    second = PreferredMoveRepository(
        database_path, lock_timeout=2.0, _checkpoint=second_checkpoint
    )
    errors: list[BaseException] = []

    def write(
        service: PreferredMoveRepository,
        date_range: tuple[str, str | None],
        move: Preference,
    ) -> None:
        try:
            service.set(STARTING_FEN, date_range[0], date_range[1], move)
        except BaseException as error:
            errors.append(error)

    first_thread = threading.Thread(
        target=write, args=(first, first_range, MOVE_E4), daemon=True
    )
    second_thread = threading.Thread(
        target=write, args=(second, second_range, MOVE_D4), daemon=True
    )
    first_thread.start()
    try:
        assert first_locked.wait(WAIT_SECONDS), "first writer did not acquire its lock"
        second_thread.start()
        assert second_attempting.wait(WAIT_SECONDS), "second writer did not attempt its lock"
        release_first.set()
        first_thread.join(timeout=WAIT_SECONDS)
        second_thread.join(timeout=WAIT_SECONDS)
    finally:
        release_first.set()
    assert not first_thread.is_alive(), "first writer did not finish"
    assert not second_thread.is_alive(), "second writer did not finish"
    if errors:
        raise errors[0]
    return PreferredMoveRepository(database_path)


def _run_serialized_delete_and_put(
    database_path: Path, first_operation: str
) -> PreferredMoveRepository:
    first_locked = threading.Event()
    second_attempting = threading.Event()
    release_first = threading.Event()
    errors: list[BaseException] = []

    def first_checkpoint(name: str) -> None:
        if name == "locked":
            first_locked.set()
            if not release_first.wait(WAIT_SECONDS):
                raise RuntimeError("timed out waiting to release first writer")

    def second_checkpoint(name: str) -> None:
        if name == "before_lock":
            second_attempting.set()

    first = PreferredMoveRepository(
        database_path, lock_timeout=2.0, _checkpoint=first_checkpoint
    )
    second = PreferredMoveRepository(
        database_path, lock_timeout=2.0, _checkpoint=second_checkpoint
    )

    def delete_mutation(checkpoint: object) -> None:
        try:
            delete_preferred_move(
                database_path,
                PreferredMoveRemovalRequest(
                    STARTING_PUBLIC_FEN, "2026-02-01", "2026-04-01"
                ),
                lock_timeout=2.0,
                _checkpoint=checkpoint,
            )
        except BaseException as error:
            errors.append(error)

    def put_mutation(service: PreferredMoveRepository) -> None:
        try:
            service.set(STARTING_FEN, "2026-03-01", "2026-05-01", MOVE_D4)
        except BaseException as error:
            errors.append(error)

    if first_operation == "delete":
        first_target = lambda: delete_mutation(first_checkpoint)
        second_target = lambda: put_mutation(second)
    else:
        first_target = lambda: put_mutation(first)
        second_target = lambda: delete_mutation(second_checkpoint)

    first_thread = threading.Thread(target=first_target, daemon=True)
    second_thread = threading.Thread(target=second_target, daemon=True)
    first_thread.start()
    try:
        assert first_locked.wait(WAIT_SECONDS), "first writer did not acquire its lock"
        second_thread.start()
        assert second_attempting.wait(WAIT_SECONDS), "second writer did not attempt its lock"
        release_first.set()
        first_thread.join(timeout=WAIT_SECONDS)
        second_thread.join(timeout=WAIT_SECONDS)
    finally:
        release_first.set()
    assert not first_thread.is_alive(), "first writer did not finish"
    assert not second_thread.is_alive(), "second writer did not finish"
    if errors:
        raise errors[0]
    return PreferredMoveRepository(database_path)


def test_serialized_overlays_use_fresh_schedule_and_preserve_outer_effects(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "overlapping-writers.db"
    create_schema(database_path)

    service = _run_serialized_writers(
        database_path,
        ("2026-01-01", "2026-05-01"),
        ("2026-02-01", "2026-04-01"),
    )

    assert _period_values(service) == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-02-01", "2026-04-01", "d2d4"),
        ("2026-04-01", "2026-05-01", "e2e4"),
    ]


def test_serialized_nonintersecting_writers_both_survive(tmp_path: Path) -> None:
    database_path = tmp_path / "nonintersecting-writers.db"
    create_schema(database_path)

    service = _run_serialized_writers(
        database_path,
        ("2026-01-01", "2026-02-01"),
        ("2026-03-01", "2026-04-01"),
    )

    assert _period_values(service) == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-03-01", "2026-04-01", "d2d4"),
    ]


def test_writer_lock_failure_is_bounded_and_leaves_schedule_unchanged(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "bounded-lock.db"
    create_schema(database_path)
    blocker = sqlite3.connect(database_path, isolation_level=None, timeout=0.2)
    blocker.execute("PRAGMA busy_timeout = 200")
    blocker.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(PreferredMoveLockError):
            PreferredMoveRepository(database_path, lock_timeout=0.05).set(
                STARTING_FEN, "2026-01-01", None, MOVE_E4
            )
    finally:
        blocker.rollback()
        blocker.close()

    service = PreferredMoveRepository(database_path)
    assert service.list_periods(STARTING_FEN) == ()


@pytest.mark.parametrize("first_operation", ["delete", "put"])
def test_serialized_delete_and_put_use_the_latest_committed_schedule(
    tmp_path: Path, first_operation: str
) -> None:
    database_path = tmp_path / f"delete-put-{first_operation}.db"
    create_schema(database_path)
    PreferredMoveRepository(database_path).set(
        STARTING_FEN, "2026-01-01", "2026-05-01", MOVE_E4
    )

    service = _run_serialized_delete_and_put(database_path, first_operation)

    assert _period_values(service) == [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-03-01", "2026-05-01", "d2d4"),
    ] if first_operation == "delete" else [
        ("2026-01-01", "2026-02-01", "e2e4"),
        ("2026-04-01", "2026-05-01", "d2d4"),
    ]
