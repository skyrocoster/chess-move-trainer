# chess_com

Chess.com data pipeline scripts.

## Purpose

Fetches game archives from the Chess.com public API, extracts a position corpus, and loads data into the SQLite database.

## Entry point

`_cli.py` — CLI argument parsing, logging setup, and reporting. All other scripts are invoked through it or as standalone steps.

## Pipeline

1. `fetch_games.py` — downloads monthly game archives from Chess.com API
2. `extract_corpus.py` — parses PGN, extracts positions, loads into `corpus` and `corpus_game` tables
3. `_replay.py` — replays games to validate extracted data

## Naming conventions

- `_cli.py` — CLI helpers and shared utilities
- `_errors.py` — error types
- `_history.py` — run history tracking
- `_persistence.py` — database access layer
- `_schema.py` — DDL definitions (corpus tables)
- `config.yaml` — pipeline configuration (subject UUID, paths)

## Config

`config.yaml` holds the tracked player UUID and default paths. Override with `--subject` or `--db` CLI flags.
