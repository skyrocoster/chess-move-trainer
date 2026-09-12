from __future__ import annotations

from datetime import date
import math
from pathlib import Path
import sqlite3
import time

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import (
    PositionRepository,
    TrainingAnswerLockError,
    TrainingAnswerNotFoundError,
    TrainingAnswerRepository,
    TrainingAnswerRequest,
    TrainingAnswerStaleError,
    TrainingAnswerValidationError,
    TrainingRequirementPolicy,
    TrainingRequirementStorageError,
)


POLICY = TrainingRequirementPolicy(0.8, 30)
FEN = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"


def _game(connection: sqlite3.Connection, game_id: int, started: str) -> None:
    connection.execute(
        """
        INSERT INTO datasource_game (
            dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
            dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc
        ) VALUES (?, ?, ?, ?, 'white', ?, ?)
        """,
        (
            game_id,
            f"answer-game-{game_id}",
            f"https://example.test/answer-game-{game_id}",
            "[Result \"*\"]\n\n*",
            f"trainer-{game_id}",
            started,
        ),
    )


def _occurrence(
    connection: sqlite3.Connection,
    game_id: int,
    position_id: int,
    move_uci: str,
) -> None:
    connection.execute(
        """
        INSERT INTO derived_game_position (
            datasource_game_id, dgp_ply, derived_position_id,
            dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
        ) VALUES (?, 1, ?, ?, 0, 1)
        """,
        (game_id, position_id, move_uci),
    )


def _fixture(tmp_path: Path) -> tuple[Path, int]:
    database = tmp_path / "answers.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(FEN)
    with sqlite3.connect(database) as connection:
        _game(connection, 1, "2026-01-01T00:00:00Z")
        _game(connection, 2, "2026-01-02T00:00:00Z")
        _occurrence(connection, 1, position_id, "a2a3")
        _occurrence(connection, 2, position_id, "b2b3")
        connection.execute(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_move_uci
            ) VALUES (?, '2026-01-01', 'a2a3')
            """,
            (position_id,),
        )
    return database, position_id


def _request(as_of: str, move: str = "a2a3") -> TrainingAnswerRequest:
    return TrainingAnswerRequest(FEN, "white", as_of, move)


def _balance(database: Path, position_id: int) -> tuple[float, str | None]:
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            """
            SELECT dpta_training_balance, dpta_updated_on
            FROM derived_position_training_aggregate
            WHERE derived_position_id = ? AND dpta_preferred_move_uci = 'a2a3'
            """,
            (position_id,),
        ).fetchone()
    return (0.0, None) if row is None else (float(row[0]), row[1])


def test_correct_wrong_and_same_day_answers_move_credit_by_one(tmp_path: Path) -> None:
    database, position_id = _fixture(tmp_path)
    repository = TrainingAnswerRepository(database, clock=lambda: date(2026, 1, 5))

    wrong = repository.submit(_request("2026-01-05", "b2b3"), POLICY)
    assert wrong.correct is False
    assert wrong.item.effective_training_balance == -1.0
    assert _balance(database, position_id) == (-1.0, "2026-01-05")

    correct = repository.submit(_request("2026-01-05"), POLICY)
    assert correct.correct is True
    assert correct.item.effective_training_balance == 0.0
    assert _balance(database, position_id) == (0.0, "2026-01-05")


@pytest.mark.parametrize("stored", [2.0, -2.0])
def test_answer_decays_signed_credit_before_applying_one(
    tmp_path: Path,
    stored: float,
) -> None:
    database, position_id = _fixture(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_position_training_aggregate (
                derived_position_id, dpta_preferred_move_uci,
                dpta_training_balance, dpta_updated_on
            ) VALUES (?, 'a2a3', ?, '2026-01-01')
            """,
            (position_id, stored),
        )

    result = TrainingAnswerRepository(
        database,
        clock=lambda: date(2026, 1, 31),
    ).submit(_request("2026-01-31"), POLICY)
    expected = math.copysign(math.sqrt(2.0), stored) + 1.0
    assert result.item.effective_training_balance == pytest.approx(expected)
    balance, updated_on = _balance(database, position_id)
    assert balance == pytest.approx(expected)
    assert updated_on == "2026-01-31"


def test_future_stale_invalid_and_ineligible_answers_do_not_write(tmp_path: Path) -> None:
    database, position_id = _fixture(tmp_path)
    before = database.read_bytes()
    repository = TrainingAnswerRepository(database, clock=lambda: date(2026, 1, 5))

    with pytest.raises(TrainingAnswerValidationError):
        repository.submit(_request("2026-01-06"), POLICY)
    assert database.read_bytes() == before

    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_position_training_aggregate (
                derived_position_id, dpta_preferred_move_uci,
                dpta_training_balance, dpta_updated_on
            ) VALUES (?, 'a2a3', 2.0, '2026-01-06')
            """,
            (position_id,),
        )
    with pytest.raises(TrainingAnswerStaleError):
        repository.submit(_request("2026-01-05"), POLICY)
    assert _balance(database, position_id) == (2.0, "2026-01-06")

    with pytest.raises(TrainingAnswerValidationError):
        TrainingAnswerRequest(FEN, "black", "2026-01-05", "a2a3")

    no_preference_database = tmp_path / "no-preference.db"
    create_schema(no_preference_database)
    no_preference_id = PositionRepository(no_preference_database).resolve_fen(FEN)
    with sqlite3.connect(no_preference_database) as connection:
        _game(connection, 1, "2026-01-01T00:00:00Z")
        _occurrence(connection, 1, no_preference_id, "a2a3")
    with pytest.raises(TrainingAnswerNotFoundError):
        TrainingAnswerRepository(
            no_preference_database,
            clock=lambda: date(2026, 1, 5),
        ).submit(_request("2026-01-05"), POLICY)
    assert _balance(no_preference_database, no_preference_id) == (0.0, None)


def test_failed_submission_rolls_back_the_upsert(tmp_path: Path) -> None:
    database, position_id = _fixture(tmp_path)
    repository = TrainingAnswerRepository(database, clock=lambda: date(2026, 1, 5))
    original = repository._submit_connection

    def fail_after_write(connection, request, answer_date, policy):
        original(connection, request, answer_date, policy)
        raise RuntimeError("forced failure")

    repository._submit_connection = fail_after_write  # type: ignore[method-assign]
    with pytest.raises(TrainingRequirementStorageError):
        repository.submit(_request("2026-01-05"), POLICY)
    assert _balance(database, position_id) == (0.0, None)


def test_lock_failure_is_bounded_and_translated(tmp_path: Path) -> None:
    database, _position_id = _fixture(tmp_path)
    holder = sqlite3.connect(database, timeout=1.0)
    holder.execute("BEGIN IMMEDIATE")
    started = time.monotonic()
    try:
        with pytest.raises(TrainingAnswerLockError):
            TrainingAnswerRepository(
                database,
                lock_timeout=0.05,
                clock=lambda: date(2026, 1, 5),
            ).submit(_request("2026-01-05"), POLICY)
    finally:
        holder.rollback()
        holder.close()
    assert time.monotonic() - started < 2.0
