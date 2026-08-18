"""CLI helpers: reporting, logging setup, and argument parsing."""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path
from typing import TextIO

import yaml

DEFAULT_CONFIG = Path(__file__).with_name("config.yaml")
DEFAULT_DATABASE = Path(__file__).resolve().parents[2] / "data/database/chess_games.db"
DEFAULT_LOG = Path(__file__).resolve().parents[2] / "data/chess-com/corpus/logs/extract.log"
DEFAULT_SUBJECT = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"


def _read_only_connection(database: Path) -> sqlite3.Connection:
    if not database.exists():
        raise RuntimeError(f"Database does not exist: {database}")
    return sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)


def _table_exists(connection: sqlite3.Connection, name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def report(database: Path, output: TextIO = sys.stdout) -> None:
    """Print the last run summary without changing the database."""

    connection = _read_only_connection(database)
    try:
        if not _table_exists(connection, "corpus_run"):
            print("No corpus schema initialized.", file=output)
            return
        row = connection.execute(
            "SELECT status, accepted_games, excluded_games, new_games, changed_games, "
            "removed_games, unchanged_games, ordered_positions, unique_states, validation, details "
            "FROM corpus_run ORDER BY run_id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            print("No corpus runs.", file=output)
            return
        labels = (
            "status",
            "accepted_games",
            "excluded_games",
            "new_games",
            "changed_games",
            "removed_games",
            "unchanged_games",
            "ordered_positions",
            "unique_states",
            "validation",
            "details",
        )
        for label, value in zip(labels, row):
            print(f"{label}: {value}", file=output)
    finally:
        connection.close()


def _subject_from_config(path: Path) -> str:
    values = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return str(values.get("subject_uuid", DEFAULT_SUBJECT))


def configure_logging(path: Path) -> logging.Logger:
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("chess_com_corpus")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the Chess.com position corpus.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--subject", help="Subject player UUID; overrides config.yaml")
    parser.add_argument("--init", action="store_true", help="Initialize the Stage 1 corpus schema")
    parser.add_argument("--report", action="store_true", help="Read-only last-run summary")
    return parser
