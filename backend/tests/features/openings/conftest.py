from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.features.positions.repository import SUBJECT_PLAYER_UUID

MANIFEST = "accepted-manifest"
OTHER_SUBJECT_UUID = "02020202-ce8b-11ee-b2fd-e90263e5548c"


def create_openings_database(
    path: Path,
    *,
    catalog_schema_version: int = 1,
    relationship_schema_version: int = 1,
    recurrence_schema_version: int = 1,
    corpus_schema_version: int = 1,
) -> None:
    with sqlite3.connect(path) as db:
        db.executescript(
            """
            CREATE TABLE corpus_schema (id INTEGER PRIMARY KEY, version INTEGER NOT NULL);
            CREATE TABLE corpus (
                corpus_id INTEGER PRIMARY KEY,
                subject_player_uuid TEXT NOT NULL
            );
            CREATE TABLE opening_catalog_schema (
                id INTEGER PRIMARY KEY,
                version INTEGER NOT NULL
            );
            CREATE TABLE opening_catalog_state (
                id INTEGER PRIMARY KEY,
                accepted_manifest_hash TEXT NOT NULL,
                accepted_schema_version INTEGER NOT NULL,
                record_count INTEGER NOT NULL
            );
            CREATE TABLE opening_catalog (
                manifest_hash TEXT NOT NULL,
                source_file TEXT NOT NULL,
                source_row_ordinal INTEGER NOT NULL,
                eco TEXT NOT NULL,
                name TEXT NOT NULL,
                move_sequence TEXT NOT NULL,
                PRIMARY KEY (manifest_hash, source_file, source_row_ordinal)
            );
            CREATE TABLE opening_relationship_schema (
                id INTEGER PRIMARY KEY,
                version INTEGER NOT NULL
            );
            CREATE TABLE opening_relationship_state (
                accepted_manifest_hash TEXT PRIMARY KEY,
                accepted_schema_version INTEGER NOT NULL
            );
            CREATE TABLE opening_parent_link (
                manifest_hash TEXT NOT NULL,
                child_source_file TEXT NOT NULL,
                child_source_row_ordinal INTEGER NOT NULL,
                child_ply INTEGER NOT NULL,
                parent_source_file TEXT NOT NULL,
                parent_source_row_ordinal INTEGER NOT NULL
            );
            CREATE TABLE opening_position_membership (
                manifest_hash TEXT NOT NULL,
                source_file TEXT NOT NULL,
                source_row_ordinal INTEGER NOT NULL,
                ply INTEGER NOT NULL,
                placement TEXT NOT NULL,
                side_to_move TEXT NOT NULL,
                castling TEXT NOT NULL,
                en_passant TEXT NOT NULL,
                uci_prefix TEXT NOT NULL
            );
            CREATE TABLE opening_transposition_link (
                manifest_hash TEXT NOT NULL,
                placement TEXT NOT NULL,
                side_to_move TEXT NOT NULL,
                castling TEXT NOT NULL,
                en_passant TEXT NOT NULL,
                source_file_a TEXT NOT NULL,
                source_row_ordinal_a INTEGER NOT NULL,
                ply_a INTEGER NOT NULL,
                uci_prefix_a TEXT NOT NULL,
                source_file_b TEXT NOT NULL,
                source_row_ordinal_b INTEGER NOT NULL,
                ply_b INTEGER NOT NULL,
                uci_prefix_b TEXT NOT NULL
            );
            CREATE TABLE opening_recurrence_schema (
                id INTEGER PRIMARY KEY,
                version INTEGER NOT NULL
            );
            CREATE TABLE opening_recurrence_state (
                accepted_manifest_hash TEXT NOT NULL,
                corpus_id INTEGER NOT NULL,
                accepted_schema_version INTEGER NOT NULL,
                accepted_classification_schema_version INTEGER NOT NULL,
                accepted_catalog_schema_version INTEGER NOT NULL,
                accepted_relationship_schema_version INTEGER NOT NULL,
                accepted_corpus_schema_version INTEGER NOT NULL
            );
            CREATE TABLE opening_recurrence_route_projection (
                manifest_hash TEXT NOT NULL,
                corpus_id INTEGER NOT NULL,
                source_file TEXT NOT NULL,
                source_row_ordinal INTEGER NOT NULL,
                color_scope TEXT NOT NULL,
                distinct_game_count INTEGER NOT NULL
            );
            """
        )
        db.executemany(
            "INSERT INTO corpus_schema VALUES (1, ?)",
            [(corpus_schema_version,)],
        )
        db.executemany(
            "INSERT INTO corpus VALUES (?, ?)",
            [(1, SUBJECT_PLAYER_UUID), (2, OTHER_SUBJECT_UUID)],
        )
        db.execute("INSERT INTO opening_catalog_schema VALUES (1, ?)", (catalog_schema_version,))
        db.execute(
            "INSERT INTO opening_catalog_state VALUES (1, ?, ?, ?)",
            (MANIFEST, catalog_schema_version, 5),
        )
        db.execute(
            "INSERT INTO opening_relationship_schema VALUES (1, ?)",
            (relationship_schema_version,),
        )
        db.execute(
            "INSERT INTO opening_relationship_state VALUES (?, ?)",
            (MANIFEST, relationship_schema_version),
        )
        db.execute(
            "INSERT INTO opening_recurrence_schema VALUES (1, ?)",
            (recurrence_schema_version,),
        )
        db.execute(
            "INSERT INTO opening_recurrence_state VALUES (?, ?, ?, ?, ?, ?, ?)",
            (MANIFEST, 1, recurrence_schema_version, 1, 1, 1, 1),
        )
        db.executemany(
            "INSERT INTO opening_catalog VALUES (?, ?, ?, ?, ?, ?)",
            [
                (MANIFEST, "a.tsv", 1, "A00", "Root Opening", "e4"),
                (MANIFEST, "a.tsv", 2, "A01", "Family Opening", "e4 e5"),
                (MANIFEST, "a.tsv", 3, "A02", "Leaf Opening", "e4 e5 Nf3"),
                (MANIFEST, "b.tsv", 1, "B01", "Other Opening", "d4"),
                (MANIFEST, "c.tsv", 1, "C01", "Not Mine Opening", "c4"),
            ],
        )
        db.executemany(
            "INSERT INTO opening_parent_link VALUES (?, ?, ?, ?, ?, ?)",
            [
                (MANIFEST, "a.tsv", 2, 1, "a.tsv", 1),
                (MANIFEST, "a.tsv", 3, 3, "a.tsv", 2),
                (MANIFEST, "a.tsv", 3, 5, "a.tsv", 1),
                (MANIFEST, "b.tsv", 1, 4, "a.tsv", 1),
                (MANIFEST, "b.tsv", 1, 6, "a.tsv", 2),
            ],
        )
        db.executemany(
            "INSERT INTO opening_position_membership VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (MANIFEST, "a.tsv", 2, 1, "position-family", "w", "-", "-", "e4"),
                (
                    MANIFEST,
                    "a.tsv",
                    3,
                    3,
                    "position-one",
                    "w",
                    "-",
                    "-",
                    "e4 e5 Nf3",
                ),
                (
                    MANIFEST,
                    "a.tsv",
                    3,
                    5,
                    "position-two",
                    "w",
                    "-",
                    "-",
                    "e4 e5 Nf3 Nc6",
                ),
                (
                    MANIFEST,
                    "b.tsv",
                    1,
                    4,
                    "position-one",
                    "w",
                    "-",
                    "-",
                    "d4 d5",
                ),
                (
                    MANIFEST,
                    "b.tsv",
                    1,
                    6,
                    "position-two",
                    "w",
                    "-",
                    "-",
                    "d4 d5 c6",
                ),
            ],
        )
        db.executemany(
            "INSERT INTO opening_transposition_link VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    MANIFEST,
                    "position-one",
                    "w",
                    "-",
                    "-",
                    "a.tsv",
                    3,
                    3,
                    "e4 e5 Nf3",
                    "b.tsv",
                    1,
                    4,
                    "d4 d5",
                ),
                (
                    MANIFEST,
                    "position-two",
                    "w",
                    "-",
                    "-",
                    "a.tsv",
                    3,
                    5,
                    "e4 e5 Nf3 Nc6",
                    "b.tsv",
                    1,
                    6,
                    "d4 d5 c6",
                ),
            ],
        )
        db.executemany(
            "INSERT INTO opening_recurrence_route_projection VALUES (?, ?, ?, ?, ?, ?)",
            [
                (MANIFEST, 1, "a.tsv", 3, "overall", 2),
                (MANIFEST, 1, "b.tsv", 1, "overall", 1),
                (MANIFEST, 2, "c.tsv", 1, "overall", 9),
            ],
        )


@pytest.fixture
def api_context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, Path]:
    database = tmp_path / "openings.db"
    create_openings_database(database)
    monkeypatch.setenv("CHESS_DATABASE_PATH", str(database))
    from backend.app.main import app

    return TestClient(app), database
