"""CRUD operations for chess_games.db."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "chess_games.db"


def connect(db: Path = DB_PATH, readonly: bool = False) -> sqlite3.Connection:
    if readonly:
        return sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# -- players -----------------------------------------------------------------


def get_player(conn: sqlite3.Connection, uuid: str) -> dict | None:
    row = conn.execute("SELECT * FROM players WHERE uuid = ?", (uuid,)).fetchone()
    return _row_to_dict(row, conn) if row else None


def get_player_by_username(conn: sqlite3.Connection, username: str) -> dict | None:
    row = conn.execute("SELECT * FROM players WHERE username = ?", (username,)).fetchone()
    return _row_to_dict(row, conn) if row else None


def upsert_player(
    conn: sqlite3.Connection, uuid: str, username: str, profile_url: str | None = None
) -> None:
    conn.execute(
        "INSERT INTO players VALUES (?, ?, ?) ON CONFLICT(uuid) "
        "DO UPDATE SET username=excluded.username, "
        "profile_url=excluded.profile_url",
        (uuid, username, profile_url),
    )


def list_players(conn: sqlite3.Connection) -> list[dict]:
    return [
        _row_to_dict(r, conn)
        for r in conn.execute("SELECT * FROM players ORDER BY username").fetchall()
    ]


# -- games -------------------------------------------------------------------


def get_game(conn: sqlite3.Connection, uuid: str) -> dict | None:
    row = conn.execute("SELECT * FROM games WHERE uuid = ?", (uuid,)).fetchone()
    return _row_to_dict(row, conn) if row else None


def list_games(
    conn: sqlite3.Connection, year: int | None = None, month: int | None = None
) -> list[dict]:
    if year is not None and month is not None:
        rows = conn.execute(
            "SELECT * FROM games WHERE year = ? AND month = ? ORDER BY end_time", (year, month)
        ).fetchall()
    elif year is not None:
        rows = conn.execute(
            "SELECT * FROM games WHERE year = ? ORDER BY end_time", (year,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM games ORDER BY end_time").fetchall()
    return [_row_to_dict(r, conn) for r in rows]


def upsert_game(conn: sqlite3.Connection, game: dict) -> None:
    conn.execute(
        """INSERT INTO games (
            uuid, url, pgn, time_control, end_time, rated, tcn, initial_setup, fen,
            time_class, rules, eco, white_player_uuid, black_player_uuid,
            white_rating, black_rating, white_result, black_result,
            white_accuracy, black_accuracy, tournament, match, year, month
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(uuid) DO UPDATE SET
            url=excluded.url, pgn=excluded.pgn, end_time=excluded.end_time,
            white_rating=excluded.white_rating, black_rating=excluded.black_rating,
            white_result=excluded.white_result, black_result=excluded.black_result,
            white_accuracy=excluded.white_accuracy, black_accuracy=excluded.black_accuracy""",
        (
            game["uuid"],
            game["url"],
            game["pgn"],
            game["time_control"],
            game["end_time"],
            game.get("rated"),
            game.get("tcn"),
            game.get("initial_setup"),
            game.get("fen"),
            game.get("time_class"),
            game.get("rules"),
            game.get("eco"),
            game["white_player_uuid"],
            game["black_player_uuid"],
            game.get("white_rating"),
            game.get("black_rating"),
            game.get("white_result"),
            game.get("black_result"),
            game.get("white_accuracy"),
            game.get("black_accuracy"),
            game.get("tournament"),
            game.get("match"),
            game["year"],
            game["month"],
        ),
    )


def delete_game(conn: sqlite3.Connection, uuid: str) -> bool:
    cur = conn.execute("DELETE FROM games WHERE uuid = ?", (uuid,))
    return cur.rowcount > 0


# -- fetch_state -------------------------------------------------------------


def get_fetch_state(conn: sqlite3.Connection, username: str, year: int, month: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM fetch_state WHERE username = ? AND year = ? AND month = ?",
        (username, year, month),
    ).fetchone()
    return _row_to_dict(row, conn) if row else None


def list_fetch_states(conn: sqlite3.Connection, username: str) -> list[dict]:
    return [
        _row_to_dict(r, conn)
        for r in conn.execute(
            "SELECT * FROM fetch_state WHERE username = ? ORDER BY year, month", (username,)
        ).fetchall()
    ]


# -- corpus ------------------------------------------------------------------


def get_corpus(conn: sqlite3.Connection, corpus_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM corpus WHERE corpus_id = ?", (corpus_id,)).fetchone()
    return _row_to_dict(row, conn) if row else None


def get_corpus_by_subject(conn: sqlite3.Connection, subject_uuid: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM corpus WHERE subject_player_uuid = ?", (subject_uuid,)
    ).fetchone()
    return _row_to_dict(row, conn) if row else None


def list_corpora(conn: sqlite3.Connection) -> list[dict]:
    return [
        _row_to_dict(r, conn)
        for r in conn.execute("SELECT * FROM corpus ORDER BY corpus_id").fetchall()
    ]


def create_corpus(conn: sqlite3.Connection, subject_uuid: str) -> int:
    cur = conn.execute("INSERT INTO corpus (subject_player_uuid) VALUES (?)", (subject_uuid,))
    return cur.lastrowid  # type: ignore[return-value]


# -- corpus_game -------------------------------------------------------------


def list_corpus_games(conn: sqlite3.Connection, corpus_id: int) -> list[dict]:
    return [
        _row_to_dict(r, conn)
        for r in conn.execute(
            "SELECT * FROM corpus_game WHERE corpus_id = ? ORDER BY game_uuid", (corpus_id,)
        ).fetchall()
    ]


def add_corpus_game(
    conn: sqlite3.Connection, corpus_id: int, game_uuid: str, rules: str, fingerprint: str
) -> None:
    conn.execute(
        "INSERT INTO corpus_game VALUES (?, ?, ?, ?)",
        (corpus_id, game_uuid, rules, fingerprint),
    )


def remove_corpus_game(conn: sqlite3.Connection, corpus_id: int, game_uuid: str) -> bool:
    cur = conn.execute(
        "DELETE FROM corpus_game WHERE corpus_id = ? AND game_uuid = ?", (corpus_id, game_uuid)
    )
    return cur.rowcount > 0


# -- position_state ----------------------------------------------------------


def get_position_state(conn: sqlite3.Connection, state_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM position_state WHERE state_id = ?", (state_id,)).fetchone()
    return _row_to_dict(row, conn) if row else None


def find_position_state(
    conn: sqlite3.Connection, placement: str, side_to_move: str, castling: str, en_passant: str
) -> dict | None:
    row = conn.execute(
        "SELECT * FROM position_state "
        "WHERE placement = ? AND side_to_move = ? "
        "AND castling = ? AND en_passant = ?",
        (placement, side_to_move, castling, en_passant),
    ).fetchone()
    return _row_to_dict(row, conn) if row else None


def upsert_position_state(conn: sqlite3.Connection, state: dict) -> int:
    existing = find_position_state(
        conn, state["placement"], state["side_to_move"], state["castling"], state["en_passant"]
    )
    if existing:
        return existing["state_id"]
    cur = conn.execute(
        "INSERT INTO position_state "
        "(placement, side_to_move, castling, en_passant) "
        "VALUES (?, ?, ?, ?)",
        (state["placement"], state["side_to_move"], state["castling"], state["en_passant"]),
    )
    return cur.lastrowid  # type: ignore[return-value]


# -- position_occurrence -----------------------------------------------------


def get_position_occurrence(conn: sqlite3.Connection, occurrence_id: int) -> dict | None:
    row = conn.execute(
        "SELECT * FROM position_occurrence WHERE occurrence_id = ?", (occurrence_id,)
    ).fetchone()
    return _row_to_dict(row, conn) if row else None


def list_position_occurrences(conn: sqlite3.Connection, game_uuid: str) -> list[dict]:
    return [
        _row_to_dict(r, conn)
        for r in conn.execute(
            "SELECT * FROM position_occurrence WHERE game_uuid = ? ORDER BY ply", (game_uuid,)
        ).fetchall()
    ]


def add_position_occurrence(conn: sqlite3.Connection, occ: dict) -> int:
    cur = conn.execute(
        """INSERT INTO position_occurrence
            (game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            occ["game_uuid"],
            occ["ply"],
            occ["state_id"],
            occ.get("san"),
            occ.get("uci"),
            occ["halfmove_clock"],
            occ["fullmove_number"],
        ),
    )
    return cur.lastrowid  # type: ignore[return-value]


# -- corpus_run --------------------------------------------------------------


def get_corpus_run(conn: sqlite3.Connection, run_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM corpus_run WHERE run_id = ?", (run_id,)).fetchone()
    return _row_to_dict(row, conn) if row else None


def list_corpus_runs(conn: sqlite3.Connection, corpus_id: int) -> list[dict]:
    return [
        _row_to_dict(r, conn)
        for r in conn.execute(
            "SELECT * FROM corpus_run WHERE corpus_id = ? ORDER BY run_id", (corpus_id,)
        ).fetchall()
    ]


def create_corpus_run(
    conn: sqlite3.Connection, corpus_id: int, unique_states: int, validation: str
) -> int:
    cur = conn.execute(
        "INSERT INTO corpus_run "
        "(corpus_id, status, unique_states, validation) "
        "VALUES (?, 'running', ?, ?)",
        (corpus_id, unique_states, validation),
    )
    return cur.lastrowid  # type: ignore[return-value]


def finish_corpus_run(
    conn: sqlite3.Connection, run_id: int, status: str, **kwargs: int | str | None
) -> None:
    sets = ["status = ?"]
    params: list[int | str | None] = [status]
    for key in (
        "finished_at",
        "accepted_games",
        "excluded_games",
        "new_games",
        "changed_games",
        "removed_games",
        "unchanged_games",
        "ordered_positions",
        "unique_states",
        "details",
    ):
        if key in kwargs:
            sets.append(f"{key} = ?")
            params.append(kwargs[key])
    params.append(run_id)
    conn.execute(f"UPDATE corpus_run SET {', '.join(sets)} WHERE run_id = ?", params)


# -- helpers -----------------------------------------------------------------


def _row_to_dict(row: sqlite3.Row, _conn: sqlite3.Connection) -> dict:
    return dict(row)


def with_row_factory(conn: sqlite3.Connection) -> sqlite3.Connection:
    conn.row_factory = sqlite3.Row
    return conn
