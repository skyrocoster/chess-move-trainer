# analysis

Stockfish analysis pipeline backend feature.

## Scope

Runs Stockfish engine analysis on chess positions, persists results to SQLite, and manages concurrent access through file locking.

## Key responsibilities

- Engine wrapper — manages Stockfish process lifecycle
- Benchmark harness — measures engine performance under controlled conditions
- Position selection — identifies positions in the corpus that need analysis
- Preflight checks — validates corpus state before committing to a run
- Provisioning — ensures analysis schema and tables exist
- File locking — prevents concurrent analysis runs on the same database
- SQLite persistence — stores analysis results, batch runs, candidates, and failures

## Schema

`schema.py` (singular) initializes the analysis tables. Run via the backend health startup or `--init-schema` from the CLI.

## Relationship to evaluation

`evaluation/` handles single-position evaluation requests from the browser. `analysis/` handles bulk, long-running analysis across the entire corpus.
