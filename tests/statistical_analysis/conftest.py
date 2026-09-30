import json
import sqlite3
from pathlib import Path

import chess
import chess.pgn
import pytest

from chess_move_trainer.database.stockfish.configuration import profile_for


@pytest.fixture
def source_database(tmp_path):
    path = tmp_path / "source.db"
    with sqlite3.connect(path) as connection:
        connection.executescript(Path("src/chess_move_trainer/database/schema_v2.sql").read_text())
    return path


def add_game(path, number=1, uci="e2e4 e7e5 g1f3 b8c6 f1b5", *, color="white", analysis=True):
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Result"] = "*"
    node = game
    positions = []
    for text in uci.split():
        positions.append((board.copy(), text))
        move = chess.Move.from_uci(text)
        node = node.add_variation(move)
        board.push(move)
    positions.append((board, None))
    with sqlite3.connect(path) as connection:
        connection.execute(
            """INSERT INTO datasource_game
            (dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
             dg_trainer_color, dg_trainer_chesscom_uuid, dg_opponent_chesscom_uuid,
             dg_trainer_rating, dg_opponent_rating, dg_started_at_utc, dg_trainer_outcome,
             dg_time_control_source, dg_time_class)
            VALUES (?, ?, ?, ?, ?, 'learner', ?, 1200, 1250, ?, 'win', '600+5', 'rapid')""",
            (
                number,
                f"game-{number}",
                f"https://example.test/{number}",
                str(game),
                color,
                f"opponent-{number}",
                f"2026-09-{number:02d}T12:00:00Z",
            ),
        )
        for ply, (board, move) in enumerate(positions):
            fields = board.fen().split()
            connection.execute(
                """INSERT OR IGNORE INTO derived_position
                (dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant)
                VALUES (?, ?, ?, ?)""",
                fields[:4],
            )
            pid = connection.execute(
                """SELECT dp_position_id FROM derived_position
                WHERE dp_placement=? AND dp_side_to_move=? AND dp_castling_rights=?
                AND dp_legal_en_passant=?""",
                fields[:4],
            ).fetchone()[0]
            connection.execute(
                "INSERT INTO derived_game_position VALUES (?, ?, ?, ?, ?, ?)",
                (number, ply, pid, move, int(fields[4]), int(fields[5])),
            )
            if analysis and not board.is_game_over():
                quality = "tool" if ply % 2 else "browser"
                profile = profile_for(quality)
                connection.execute(
                    "INSERT OR IGNORE INTO derived_analysis_result "
                    "VALUES (?, ?, ?, ?, 'Stockfish', '19', NULL)",
                    (
                        pid,
                        quality,
                        profile.configuration_version,
                        json.dumps(dict(profile.settings)),
                    ),
                )
                for rank, candidate in enumerate(list(board.legal_moves)[: profile.multipv], 1):
                    wins = 500 if ply % 2 == 0 else 300
                    connection.execute(
                        "INSERT OR IGNORE INTO derived_analysis_line "
                        "VALUES (?, ?, 'cp', 0, ?, 0, ?, ?, 10)",
                        (pid, rank, wins, 1000 - wins, json.dumps([candidate.uci()])),
                    )
    return path
