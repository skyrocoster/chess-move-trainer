"""Dump the SQLite schema for chess_games.db to a readable text file."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "chess_games.db"
OUT_PATH = Path(__file__).parent / "schema.txt"


def dump_schema() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name")
    statements = [row[0] for row in cur.fetchall()]

    conn.close()

    OUT_PATH.write_text("\n\n".join(statements) + "\n", encoding="utf-8")
    print(f"Wrote schema to {OUT_PATH}")


if __name__ == "__main__":
    dump_schema()
