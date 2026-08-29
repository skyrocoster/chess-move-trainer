from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SUBJECT_UUID = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
COUNTER_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42"
AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
UNKNOWN_FEN = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"


def _position_key(fen: str) -> tuple[str, str, str, str]:
    return tuple(fen.split(" ")[:4])  # type: ignore[return-value]


def create_context_database(path: Path, *, schema_version: int = 1) -> None:
    start_key = _position_key(START_FEN)
    after_e4_key = _position_key(AFTER_E4_FEN)
    with sqlite3.connect(path) as db:
        db.executescript(
            """
            CREATE TABLE corpus (
                corpus_id INTEGER PRIMARY KEY,
                subject_player_uuid TEXT NOT NULL
            );
            CREATE TABLE opening_recurrence_schema (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL
            );
            CREATE TABLE opening_recurrence_state (
                accepted_manifest_hash TEXT NOT NULL,
                corpus_id INTEGER NOT NULL,
                accepted_schema_version INTEGER NOT NULL
            );
            CREATE TABLE opening_recurrence_position_projection (
                manifest_hash TEXT NOT NULL,
                corpus_id INTEGER NOT NULL,
                placement TEXT NOT NULL,
                side_to_move TEXT NOT NULL,
                castling TEXT NOT NULL,
                en_passant TEXT NOT NULL,
                color_scope TEXT NOT NULL,
                distinct_game_count INTEGER NOT NULL
            );
            """
        )
        db.execute("INSERT INTO corpus VALUES (1, ?)", (SUBJECT_UUID,))
        db.execute("INSERT INTO opening_recurrence_schema VALUES (1, ?)", (schema_version,))
        db.execute("INSERT INTO opening_recurrence_state VALUES ('accepted-manifest', 1, 1)")
        db.executemany(
            "INSERT INTO opening_recurrence_position_projection VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                ("accepted-manifest", 1, *start_key, "overall", 3),
                ("accepted-manifest", 1, *start_key, "white", 2),
                ("accepted-manifest", 1, *start_key, "black", 1),
                ("accepted-manifest", 1, *after_e4_key, "overall", 2),
                ("accepted-manifest", 1, *after_e4_key, "white", 2),
            ),
        )


@pytest.fixture
def api_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, Path]:
    database = tmp_path / "position-context.db"
    create_context_database(database)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    from backend.app.main import app

    return TestClient(app), database
