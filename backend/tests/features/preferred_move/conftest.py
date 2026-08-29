from __future__ import annotations

import sqlite3
from pathlib import Path

import chess
import pytest

from scripts.opening_catalog.preferred_move import ensure_preferred_move_schema

SUBJECT_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
OPPONENT_UUID = "02020202-ce8b-11ee-b2fd-e90263e5548c"
OTHER_UUID = "03030303-ce8b-11ee-b2fd-e90263e5548c"
START_FEN = chess.STARTING_FEN
COUNTER_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42"
AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
UNOBSERVED_FEN = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
UNKNOWN_FEN = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"


def create_base_database(path: Path) -> None:
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript(
            """
            CREATE TABLE players (
                uuid TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                profile_url TEXT
            );
            CREATE TABLE games (
                uuid TEXT PRIMARY KEY,
                white_player_uuid TEXT NOT NULL,
                black_player_uuid TEXT NOT NULL
            );
            CREATE TABLE position_state (
                state_id INTEGER PRIMARY KEY,
                placement TEXT NOT NULL,
                side_to_move TEXT NOT NULL,
                castling TEXT NOT NULL,
                en_passant TEXT NOT NULL,
                UNIQUE (placement, side_to_move, castling, en_passant)
            );
            CREATE TABLE position_occurrence (
                occurrence_id INTEGER PRIMARY KEY,
                game_uuid TEXT NOT NULL,
                ply INTEGER NOT NULL,
                state_id INTEGER NOT NULL,
                UNIQUE (game_uuid, ply),
                FOREIGN KEY (game_uuid) REFERENCES games(uuid),
                FOREIGN KEY (state_id) REFERENCES position_state(state_id)
            );
            INSERT INTO players VALUES
                ('0101b08a-ce8b-11ee-b2fd-e90263e5548c', 'Skyrocoster', NULL),
                ('02020202-ce8b-11ee-b2fd-e90263e5548c', 'Opponent', NULL),
                ('03030303-ce8b-11ee-b2fd-e90263e5548c', 'Other', NULL);
            INSERT INTO games VALUES
                ('game-one', '0101b08a-ce8b-11ee-b2fd-e90263e5548c',
                 '02020202-ce8b-11ee-b2fd-e90263e5548c'),
                ('game-two', '02020202-ce8b-11ee-b2fd-e90263e5548c',
                 '0101b08a-ce8b-11ee-b2fd-e90263e5548c');
            INSERT INTO position_state VALUES
                (1, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', 'w', 'KQkq', '-'),
                (2, 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR', 'b', 'KQkq', 'e3'),
                (3, 'rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR', 'w', 'KQkq', '-');
            INSERT INTO position_occurrence (game_uuid, ply, state_id) VALUES
                ('game-one', 0, 1), ('game-one', 1, 2), ('game-two', 0, 1);
            """
        )


def create_database(path: Path, *, preferred_schema: bool = True, version: int = 1) -> None:
    create_base_database(path)
    if preferred_schema:
        with sqlite3.connect(path) as db:
            ensure_preferred_move_schema(db)
            if version != 1:
                db.execute(
                    "UPDATE opening_preferred_move_schema SET version = ? WHERE id = 1",
                    (version,),
                )


@pytest.fixture
def api_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database = tmp_path / "preferred.db"
    create_database(database)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    from fastapi.testclient import TestClient

    from backend.app.main import app

    return TestClient(app), database
