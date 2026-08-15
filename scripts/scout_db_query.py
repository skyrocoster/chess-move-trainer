"""Read-only SQLite query helper for the scout subagent.

Opens the chess games database via a SQLite URI with `?mode=ro`, so any write
or schema mutation fails at the engine level with
`attempt to write a readonly database` regardless of the SQL text. The caller
never needs to judge whether a statement is a SELECT.

Usage:
    python scripts/scout_db_query.py "<SQL>"

Rows are printed one per line with pipe-separated columns.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "database" / "chess_games.db"


def main() -> int:
    if len(sys.argv) != 2:
        print('usage: python scripts/scout_db_query.py "<SQL>"', file=sys.stderr)
        return 2
    sql = sys.argv[1]
    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        rows = con.execute(sql).fetchall()
    finally:
        con.close()
    for row in rows:
        print(*row, sep="|")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
