from __future__ import annotations

import io
import sqlite3
from datetime import UTC, datetime

from backend.app.features.analysis import (
    AnalysisProfile,
    AnalysisRepository,
    AnalysisResult,
    initialize_analysis_schema,
    require_analysis_schema,
)
from scripts.chess_com import extract_corpus

SUBJECT = extract_corpus.DEFAULT_SUBJECT
TERMINAL_FEN = "7k/5Q2/7K/8/8/8/8/8 b - - 0 1"
PGN = """[Event "fixture"]
[Result "*"]

1. e4 *
"""
FINAL_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"


def source_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE players (uuid TEXT PRIMARY KEY, username TEXT NOT NULL, profile_url TEXT);
        CREATE TABLE games (
            uuid TEXT PRIMARY KEY, url TEXT NOT NULL, pgn TEXT NOT NULL,
            time_control TEXT NOT NULL, end_time INTEGER NOT NULL, rated INTEGER,
            tcn TEXT, initial_setup TEXT, fen TEXT, time_class TEXT, rules TEXT,
            eco TEXT, white_player_uuid TEXT NOT NULL, black_player_uuid TEXT NOT NULL
        );
        CREATE TABLE fetch_state (
            username TEXT NOT NULL, year INTEGER NOT NULL, month INTEGER NOT NULL,
            etag TEXT, last_fetched TEXT, is_current INTEGER NOT NULL,
            PRIMARY KEY (username, year, month)
        );
        """
    )


def test_extraction_coexistence_preserves_analysis_schema_and_orphaned_fen(connection) -> None:
    source_schema(connection)
    connection.executemany(
        "INSERT INTO players VALUES (?, ?, NULL)",
        [(SUBJECT, "subject"), ("opponent", "opponent")],
    )
    connection.execute(
        "INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "game",
            "https://example.test/game",
            PGN,
            "600",
            0,
            0,
            None,
            None,
            FINAL_FEN,
            "rapid",
            "chess",
            "A00",
            SUBJECT,
            "opponent",
        ),
    )
    extract_corpus.ensure_corpus_schema(connection)
    connection.execute("INSERT INTO corpus (subject_player_uuid) VALUES (?)", (SUBJECT,))
    connection.commit()
    initialize_analysis_schema(connection)

    profile = AnalysisProfile(
        profile_id="coexistence",
        engine_binary_sha256="e" * 64,
        engine_name="Fakefish",
        engine_version="18-test",
        node_budget=50_000,
    )
    AnalysisRepository(connection).publish(
        AnalysisResult(
            fen=TERMINAL_FEN,
            profile=profile,
            candidates=(),
            terminal_kind="stalemate",
            completed_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC).isoformat(),
            wall_time_ms=0,
        )
    )

    extract_corpus.run_extraction(connection, output=io.StringIO())
    connection.execute("UPDATE games SET rules='oddschess' WHERE uuid='game'")
    connection.commit()
    extract_corpus.run_extraction(connection, output=io.StringIO())

    assert require_analysis_schema(connection) == 1
    assert connection.execute(
        "SELECT completed_at FROM analysis_result WHERE fen=?", (TERMINAL_FEN,)
    ).fetchone() == (datetime(2026, 8, 20, 12, 0, tzinfo=UTC).isoformat(),)
    assert connection.execute("SELECT COUNT(*) FROM position_occurrence").fetchone() == (0,)
