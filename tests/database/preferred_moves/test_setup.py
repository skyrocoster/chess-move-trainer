from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.preferred_moves.ranges import Preference
from chess_move_trainer.database.preferred_moves.repository import PreferredMoveRepository
from chess_move_trainer.database.preferred_moves.setup import (
    PreferredMoveSetupError,
    PreferredMoveSetupRefused,
    PreferredMoveSetupService,
    PreferredMoveSetupValidationError,
)

STARTING_PLACEMENT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_POSITION = (STARTING_PLACEMENT, "w", "KQkq", "-")
AFTER_E4_POSITION = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
    "b",
    "KQkq",
    "-",
)
STARTING_FEN = " ".join(STARTING_POSITION)
MOVE_E4 = "e2e4"
MOVE_D4 = "d2d4"
MOVE_E5 = "e7e5"


def _database(tmp_path: Path) -> Path:
    database = tmp_path / "setup.db"
    create_schema(database)
    return database


def _position(connection: sqlite3.Connection, fields: tuple[str, str, str, str]) -> int:
    connection.execute(
        """
        INSERT INTO derived_position (
            dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant
        ) VALUES (?, ?, ?, ?)
        """,
        fields,
    )
    return int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])


def _game(
    connection: sqlite3.Connection,
    game_id: int,
    position_id: int,
    move: str,
    *,
    started_at: str | None = "2026-01-01T00:00:00Z",
    trainer_color: str = "white",
    plies: tuple[int, ...] = (0,),
    time_class: str | None = None,
    trainer_rating: int | None = None,
    outcome: str | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO datasource_game (
            dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
            dg_trainer_color, dg_trainer_chesscom_uuid, dg_trainer_rating,
            dg_started_at_utc, dg_trainer_outcome, dg_time_class
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            game_id,
            f"00000000-0000-4000-8000-{game_id:012d}",
            f"https://example.test/{game_id}",
            "1. e4 *",
            trainer_color,
            "11111111-1111-4111-8111-111111111111",
            trainer_rating,
            started_at,
            outcome,
            time_class,
        ),
    )
    connection.executemany(
        """
        INSERT INTO derived_game_position (
            datasource_game_id, dgp_ply, derived_position_id,
            dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [(game_id, ply, position_id, move, 0, 1) for ply in plies],
    )


def _count_periods(database: Path) -> int:
    with sqlite3.connect(database) as connection:
        return int(
            connection.execute(
                "SELECT COUNT(*) FROM datasource_preferred_move_period"
            ).fetchone()[0]
        )


def test_setup_filters_trainer_side_and_includes_only_plies_zero_through_29(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        position_id = _position(connection, STARTING_POSITION)
        for game_id in range(1, 21):
            _game(connection, game_id, position_id, MOVE_E4)
        _game(connection, 21, position_id, MOVE_E4, plies=(29,))
        _game(connection, 22, position_id, MOVE_E4, plies=(30,))
        _game(connection, 23, position_id, MOVE_E4, trainer_color="black")

    result = PreferredMoveSetupService(database).run()

    assert result.examined_games == 23
    assert result.skipped_games == 0
    assert result.qualifying_positions == 1
    assert result.periods_applied == 1
    assert result.conflicting_positions == 0


def test_setup_skips_null_dates_and_counts_skipped_games_without_polluting_evidence(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        position_id = _position(connection, STARTING_POSITION)
        for game_id in range(1, 22):
            _game(connection, game_id, position_id, MOVE_E4)
        for game_id in range(22, 28):
            _game(connection, game_id, position_id, MOVE_D4, started_at=None)

    result = PreferredMoveSetupService(database).run()

    assert result.examined_games == 27
    assert result.skipped_games == 6
    assert result.qualifying_positions == 1
    assert result.periods_applied == 1
    assert _count_periods(database) == 1


def test_setup_fails_safely_on_malformed_non_null_start_timestamp(tmp_path: Path) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        position_id = _position(connection, STARTING_POSITION)
        for game_id in range(1, 22):
            _game(connection, game_id, position_id, MOVE_E4)
        _game(connection, 22, position_id, MOVE_E4, started_at="not-a-timestamp")

    with pytest.raises(PreferredMoveSetupValidationError):
        PreferredMoveSetupService(database).run()

    assert _count_periods(database) == 0


def test_setup_pools_metadata_groups_and_preserves_repeated_occurrences(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        position_id = _position(connection, STARTING_POSITION)
        for game_id in range(1, 8):
            _game(
                connection,
                game_id,
                position_id,
                MOVE_E4,
                plies=(0, 1, 2),
                time_class="blitz" if game_id % 2 else "rapid",
                trainer_rating=1200 + game_id,
                outcome=("win" if game_id % 2 else "draw"),
            )

    result = PreferredMoveSetupService(database).run()

    assert result.examined_games == 7
    assert result.qualifying_positions == 1
    assert result.periods_applied == 1


def test_setup_reports_distinct_conflicting_positions_from_overlapping_evidence(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        position_id = _position(connection, STARTING_POSITION)
        for game_id in range(1, 81):
            _game(connection, game_id, position_id, MOVE_E4)
        for game_id in range(81, 86):
            _game(
                connection,
                game_id,
                position_id,
                MOVE_E4,
                started_at="2026-02-01T00:00:00Z",
            )
        for game_id in range(86, 107):
            _game(
                connection,
                game_id,
                position_id,
                MOVE_D4,
                started_at="2026-02-01T00:00:00Z",
            )

    result = PreferredMoveSetupService(database).run()

    assert result.examined_games == 106
    assert result.qualifying_positions == 1
    assert result.periods_applied == 2
    assert result.conflicting_positions == 1


def test_zero_candidates_succeed_without_writing(tmp_path: Path) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        position_id = _position(connection, STARTING_POSITION)
        for game_id in range(1, 21):
            _game(connection, game_id, position_id, MOVE_E4)

    result = PreferredMoveSetupService(database).run()

    assert result == result.__class__(20, 0, 0, 0, 0)
    assert _count_periods(database) == 0


def test_nonempty_schedule_is_refused_before_mutation(tmp_path: Path) -> None:
    database = _database(tmp_path)
    repository = PreferredMoveRepository(database)
    repository.set(STARTING_FEN, "2026-01-01", None, Preference.preferred_move(MOVE_E4))

    with pytest.raises(PreferredMoveSetupRefused):
        PreferredMoveSetupService(database).run()

    assert _count_periods(database) == 1


def test_complete_result_validation_rejects_an_illegal_inferred_move_before_insert(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        position_id = _position(connection, STARTING_POSITION)
        for game_id in range(1, 22):
            _game(connection, game_id, position_id, "e2e5")

    with pytest.raises(PreferredMoveSetupValidationError):
        PreferredMoveSetupService(database).run()

    assert _count_periods(database) == 0


def test_successful_setup_inserts_all_periods_for_multiple_positions(tmp_path: Path) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        starting_id = _position(connection, STARTING_POSITION)
        after_e4_id = _position(connection, AFTER_E4_POSITION)
        for game_id in range(1, 22):
            _game(connection, game_id, starting_id, MOVE_E4)
        for game_id in range(22, 43):
            _game(
                connection,
                game_id,
                after_e4_id,
                MOVE_E5,
                trainer_color="black",
            )

    result = PreferredMoveSetupService(database).run()

    assert result.examined_games == 42
    assert result.skipped_games == 0
    assert result.qualifying_positions == 2
    assert result.periods_applied == 2
    assert result.conflicting_positions == 0
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM datasource_preferred_move_period"
        ).fetchone()[0] == 2
        assert {
            row[0]
            for row in connection.execute(
                "SELECT dpm_move_uci FROM datasource_preferred_move_period"
            )
        } == {MOVE_E4, MOVE_E5}


def test_later_insert_failure_rolls_back_the_complete_schedule(tmp_path: Path) -> None:
    database = _database(tmp_path)
    with sqlite3.connect(database) as connection:
        starting_id = _position(connection, STARTING_POSITION)
        after_e4_id = _position(connection, AFTER_E4_POSITION)
        for game_id in range(1, 22):
            _game(connection, game_id, starting_id, MOVE_E4)
        for game_id in range(22, 43):
            _game(connection, game_id, after_e4_id, MOVE_E5, trainer_color="black")

    inserted = 0

    def checkpoint(name: str) -> None:
        nonlocal inserted
        if name == "inserted":
            inserted += 1
            if inserted == 2:
                raise RuntimeError("injected later insert failure")

    with pytest.raises(PreferredMoveSetupError):
        PreferredMoveSetupService(database, _checkpoint=checkpoint).run()

    assert inserted == 2
    assert _count_periods(database) == 0
