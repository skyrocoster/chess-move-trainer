from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_concurrent_writers_resolve_one_stable_id_and_one_row(tmp_path: Path) -> None:
    database_path = tmp_path / "concurrent.db"
    create_schema(database_path)

    def resolve() -> int:
        return PositionRepository(database_path).resolve_fen(STARTING_FEN)

    with ThreadPoolExecutor(max_workers=6) as executor:
        ids = list(executor.map(lambda _: resolve(), range(6)))

    assert all(type(position_id) is int for position_id in ids)
    assert len(set(ids)) == 1
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_position WHERE "
            "dp_placement = ? AND dp_side_to_move = ? AND "
            "dp_castling_rights = ? AND dp_legal_en_passant = ?",
            ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "w", "KQkq", "-"),
        ).fetchone()[0] == 1
