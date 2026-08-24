# stockfish_analysis

Stockfish analysis CLI helpers.

## Purpose

Provides command-line tools for running Stockfish engine analysis on positions in the SQLite database.

## Files

| File | Purpose |
|------|---------|
| `analyze_menu.py` | Interactive menu — main entry point for human use |
| `analyze_positions.py` | Bulk analysis engine — worker processes, preflight, schema init |
| `benchmark_stockfish.py` | Runs controlled benchmarks against the engine |
| `setup_stockfish.py` | Verifies Stockfish binary is installed and working |

## Running

```bash
# Interactive menu (recommended for ad-hoc work):
.venv\Scripts\python.exe scripts/stockfish_analysis/analyze_menu.py

# Bulk analysis (non-interactive):
.venv\Scripts\python.exe scripts/stockfish_analysis/analyze_positions.py --db <path> --engine <path> --profile-id <id> --all
```

## Defaults

- Database: `data/database/chess_games.db`
- Engine: `data/stockfish/stockfish-windows-x86-64-avx2.exe`
- These are resolved relative to the repository root from the script's location.
