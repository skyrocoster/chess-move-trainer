# database

SQLite database and schema management.

## Files

| File | Purpose |
|------|---------|
| `chess_games.db` | Main SQLite database — shared by backend, scripts, and analysis |
| `schema.txt` | AI-readable schema documentation (generated, do not edit) |
| `dump_schema.py` | Regenerates `schema.txt` from live DDL |

## Schema sources

The schema is defined across multiple modules. Each owns its DDL via an `ensure_*_schema()` function:

- `scripts/chess_com/fetch_games.py` — corpus and corpus_game tables
- `scripts/chess_com/_schema.py` — corpus schema
- `scripts/opening_catalog/schema.py` — core opening tables and relationships
- `scripts/opening_catalog/classification_schema.py` — classification tables
- `scripts/opening_catalog/preferred_move_schema.py` — preferred move tables
- `scripts/opening_catalog/recurrence_schema.py` — recurrence tables
- `backend/app/features/analysis/schema.py` — analysis tables
- `backend/app/features/evaluation/schema.py` — evaluation tables

## Regenerating schema.txt

```bash
.venv\Scripts\python.exe data/database/dump_schema.py
```

## Lock file

`chess_games.db.analysis.lock` is created when a Stockfish analysis run is active. Remove it only if the analysis process has crashed.
