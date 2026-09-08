from __future__ import annotations

import sqlite3
from pathlib import Path

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.statistics import (
    MoveResponseDistributionReader,
    PositionContextReader,
)


def _database_with_synthetic_occurrences(tmp_path: Path) -> tuple[Path, int]:
    database = tmp_path / "statistics.db"
    create_schema(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_position (
                dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant
            ) VALUES (?, ?, ?, ?)
            """,
            (
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                "w",
                "KQkq",
                "-",
            ),
        )
        position_id = connection.execute(
            "SELECT dp_position_id FROM derived_position"
        ).fetchone()[0]
        connection.executemany(
            """
            INSERT INTO datasource_game (
                dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                dg_trainer_color, dg_trainer_chesscom_uuid
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                (
                    "00000000-0000-4000-8000-000000000001",
                    "https://example.test/one",
                    "1. e4 *",
                    "white",
                    "11111111-1111-4111-8111-111111111111",
                ),
                (
                    "00000000-0000-4000-8000-000000000002",
                    "https://example.test/two",
                    "1. d4 *",
                    "black",
                    "22222222-2222-4222-8222-222222222222",
                ),
            ),
        )
        game_ids = [
            row[0]
            for row in connection.execute(
                "SELECT dg_game_id FROM datasource_game ORDER BY dg_game_id"
            ).fetchall()
        ]
        connection.executemany(
            """
            INSERT INTO derived_game_position (
                datasource_game_id, dgp_ply, derived_position_id,
                dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                (game_ids[0], 0, position_id, "e2e4", 0, 1),
                (game_ids[0], 1, position_id, None, 0, 1),
                (game_ids[1], 0, position_id, "d2d4", 0, 1),
            ),
        )
    return database, position_id


def test_position_context_counts_distinct_games_and_test_actor(tmp_path: Path) -> None:
    database, position_id = _database_with_synthetic_occurrences(tmp_path)
    reader = PositionContextReader(database)

    all_games = reader.read(position_id)
    white_games = reader.read(position_id, "white")
    black_games = reader.read(position_id, "black")

    assert all_games.distinct_game_count == 2
    assert white_games.distinct_game_count == 1
    assert black_games.distinct_game_count == 1


def test_move_response_distribution_separates_trainer_and_opponent(tmp_path: Path) -> None:
    database, position_id = _database_with_synthetic_occurrences(tmp_path)

    distribution = MoveResponseDistributionReader(database).read(position_id)

    assert distribution.occurrence_count == 3
    assert distribution.played_occurrence_count == 2
    assert distribution.final_occurrence_count == 1
    assert distribution.outgoing_moves == {"d2d4": 1, "e2e4": 1}
    assert distribution.my_choices == {"e2e4": 1}
    assert distribution.opponent_responses == {"d2d4": 1}
