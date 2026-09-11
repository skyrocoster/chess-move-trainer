from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository, position_transaction

STARTING_PLACEMENT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
STARTING_FEN = f"{STARTING_PLACEMENT} w KQkq - 0 1"
BLACK_TO_MOVE_FEN = f"{STARTING_PLACEMENT} b KQkq - 0 1"


def test_grouped_resolution_rolls_back_when_later_work_fails(tmp_path: Path) -> None:
    database_path = tmp_path / "rollback.db"
    create_schema(database_path)

    with pytest.raises(RuntimeError, match="later producer work failed"):
        with position_transaction(database_path) as unit_of_work:
            unit_of_work.resolve_fen(STARTING_FEN)
            raise RuntimeError("later producer work failed")

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 0


def test_successful_multiple_resolution_composes_through_opaque_unit_of_work(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "composition.db"
    create_schema(database_path)

    with position_transaction(database_path) as unit_of_work:
        first_id = unit_of_work.resolve_fen(STARTING_FEN)
        second_id = unit_of_work.resolve_fen(BLACK_TO_MOVE_FEN)
        assert first_id != second_id
        assert not hasattr(unit_of_work, "connection")
        assert not hasattr(unit_of_work, "raw_connection")

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM derived_position").fetchone()[0] == 2


def test_position_remains_after_a_focused_reference_is_removed(tmp_path: Path) -> None:
    database_path = tmp_path / "permanent.db"
    create_schema(database_path)
    position_id = PositionRepository(database_path).resolve_fen(STARTING_FEN)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "INSERT INTO datasource_game "
            "(dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn, "
            "dg_trainer_color, dg_trainer_chesscom_uuid) "
            "VALUES (1, 'game-1', 'https://example.test/game-1', '*', 'white', 'trainer')"
        )
        connection.execute(
            "INSERT INTO derived_game_position "
            "(datasource_game_id, dgp_ply, derived_position_id, dgp_move_uci, "
            "dgp_halfmove_clock, dgp_fullmove_number) VALUES (1, 0, ?, NULL, 0, 1)",
            (position_id,),
        )
        connection.execute("DELETE FROM derived_game_position WHERE datasource_game_id = 1")
        connection.execute("DELETE FROM datasource_game WHERE dg_game_id = 1")

        assert connection.execute(
            "SELECT COUNT(*) FROM derived_position WHERE dp_position_id = ?", (position_id,)
        ).fetchone()[0] == 1
