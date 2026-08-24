# data

Runtime data: game archives, SQLite database, and Stockfish engine.

## Directory structure

```
data/
├── chess-com/               # Chess.com game data
│   ├── raw/games/<YYYY>/   # Monthly JSON archives (one file per month)
│   ├── raw/archives/       # Archive index JSON
│   ├── corpus/             # Extracted game corpus
│   └── logs/               # Fetch and extraction logs
├── database/               # SQLite database
│   ├── chess_games.db      # Main database file
│   ├── schema.txt          # AI-readable schema (generated, do not edit)
│   └── dump_schema.py      # Regenerates schema.txt
└── stockfish/              # Engine binary
    ├── stockfish-windows-x86-64-avx2.exe
    └── install.json
```

## Notes

- `chess_games.db` is shared by backend features, scripts, and analysis pipelines.
- `schema.txt` is auto-generated from DDL definitions scattered across `scripts/` and `backend/`. Run `dump_schema.py` to regenerate.
- A `.analysis.lock` file in `database/` indicates an active Stockfish analysis run.
