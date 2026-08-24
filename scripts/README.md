# scripts

Project scripts for data pipelines, analysis, and quality checks.

## Root scripts

| File | Purpose |
|------|---------|
| `check.py` | Full local quality suite (lint, typecheck, tests). Read-only by default; `--fix` runs formatters. |
| `check_size.py` | Enforces 500-line limit on handwritten source and 700-line limit on tests. |
| `dev.py` | Windows launcher: `backend`, `frontend`, or `all`. Kills processes on ports 5666/8444 first. |

## Domain subpackages

| Directory | Purpose |
|-----------|---------|
| `chess_com/` | Chess.com data pipeline: fetch games, extract corpus, replay PGN |
| `opening_catalog/` | Opening classification, preferred-move tracking, recurrence, relationships |
| `stockfish_analysis/` | Stockfish CLI: interactive menu, bulk analysis, benchmarking, setup verification |

## Running scripts

All scripts run under the project venv:

```bash
.venv\Scripts\python.exe scripts/<script>.py [args]
```

## Tests

Script-level tests live in `scripts/tests/`.
