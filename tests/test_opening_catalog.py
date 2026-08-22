from __future__ import annotations

import csv
import hashlib
import sqlite3
from pathlib import Path

import pytest

from scripts.opening_catalog import (
    EXPECTED_SOURCE_FILES,
    RELATIONSHIP_SCHEMA_VERSION,
    SCHEMA_VERSION,
    SOURCE_DATASET,
    OpeningCatalogError,
    OpeningReplayError,
    OpeningSchemaError,
    OpeningSourceChangedError,
    canonical_row_hash,
    ensure_relationship_schema,
    ensure_schema,
    import_catalog,
    import_relationships,
    load_source,
)

ROWS = {
    "a.tsv": ("A00", "Amar Opening", "1. a4"),
    "b.tsv": ("B10", "Caro-Kann Defense", "1. e4 c6"),
    "c.tsv": ("C20", "King's Pawn Game", "1. e4 e5"),
    "d.tsv": ("D00", "Queen's Pawn Game", "1. d4 d5"),
    "e.tsv": ("E00", "Indian Game", "1. d4 Nf6"),
}


def write_source(path: Path, rows: dict[str, tuple[str, str, str]] | None = None) -> Path:
    path.mkdir()
    values = rows or ROWS
    for name in EXPECTED_SOURCE_FILES:
        with (path / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerow(("eco", "name", "pgn"))
            writer.writerow(values[name])
    return path


def open_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def seed_existing_position_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE position_state (
            state_id INTEGER PRIMARY KEY,
            placement TEXT,
            side_to_move TEXT,
            castling TEXT,
            en_passant TEXT,
            UNIQUE (placement, side_to_move, castling, en_passant)
        );
        CREATE TABLE position_occurrence (
            occurrence_id INTEGER PRIMARY KEY,
            game_uuid TEXT NOT NULL,
            ply INTEGER NOT NULL,
            state_id INTEGER NOT NULL,
            FOREIGN KEY (state_id) REFERENCES position_state(state_id)
        );
        INSERT INTO position_state VALUES
            (1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-'),
            (2, 'rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR', 'b', 'KQkq', 'a3');
        INSERT INTO position_occurrence VALUES
            (1, 'game-1', 0, 1),
            (2, 'game-1', 1, 2);
        """
    )


def catalog_rows(connection: sqlite3.Connection) -> list[tuple[object, ...]]:
    return connection.execute(
        "SELECT manifest_hash, source_file, source_row_ordinal, source_row_hash, eco, name, "
        "move_sequence, endpoint_fen, endpoint_placement, endpoint_side_to_move, "
        "endpoint_castling, endpoint_en_passant, endpoint_halfmove_clock, "
        "endpoint_fullmove_number FROM opening_catalog "
        "ORDER BY source_file, source_row_ordinal"
    ).fetchall()


def test_load_source_replays_all_records_and_records_exact_endpoint_facts(tmp_path: Path) -> None:
    source = write_source(tmp_path / "source")

    manifest = load_source(source)

    assert manifest.source_dataset == "lichess-org/chess-openings"
    assert manifest.record_count == 5
    assert [item.name for item in manifest.files] == list(EXPECTED_SOURCE_FILES)
    assert all(item.record_count == 1 for item in manifest.files)
    assert all(len(record.endpoint_fen.split()) == 6 for record in manifest.records)
    assert all(record.source_row_ordinal == 1 for record in manifest.records)
    assert len({record.endpoint_key for record in manifest.records}) == 5
    a_record = next(record for record in manifest.records if record.source_file == "a.tsv")
    assert a_record.endpoint_en_passant == "a3"
    assert a_record.endpoint_key == (
        "rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR",
        "b",
        "KQkq",
        "a3",
    )


def test_catalog_persists_exact_identity_and_provenance(tmp_path: Path) -> None:
    source = write_source(tmp_path / "source")
    manifest = load_source(source)
    db_path = tmp_path / "provenance.db"

    with open_database(db_path) as connection:
        result = import_catalog(connection, source)

        assert result.manifest_hash == manifest.manifest_hash
        assert connection.execute(
            "SELECT manifest_hash, source_dataset, file_count, record_count "
            "FROM opening_source_manifest"
        ).fetchone() == (manifest.manifest_hash, SOURCE_DATASET, 5, 5)
        assert connection.execute(
            "SELECT source_file, source_file_hash, record_count FROM opening_source_file "
            "ORDER BY source_file"
        ).fetchall() == [
            (item.name, hashlib.sha256((source / item.name).read_bytes()).hexdigest(), 1)
            for item in manifest.files
        ]

        expected_rows = [
            (
                manifest.manifest_hash,
                record.source_file,
                record.source_row_ordinal,
                canonical_row_hash(record.eco, record.name, record.move_sequence),
                record.eco,
                record.name,
                record.move_sequence,
                record.endpoint_fen,
                record.endpoint_placement,
                record.endpoint_side_to_move,
                record.endpoint_castling,
                record.endpoint_en_passant,
                record.endpoint_halfmove_clock,
                record.endpoint_fullmove_number,
            )
            for record in manifest.records
        ]
        assert catalog_rows(connection) == expected_rows
        assert connection.execute(
            "SELECT schema_version, status, record_count FROM opening_import_run"
        ).fetchone() == (SCHEMA_VERSION, "success", manifest.record_count)
        assert connection.execute(
            "SELECT accepted_manifest_hash, accepted_schema_version, record_count "
            "FROM opening_catalog_state"
        ).fetchone() == (manifest.manifest_hash, SCHEMA_VERSION, manifest.record_count)


def test_initial_import_uses_opening_tables_and_preserves_game_position_rows(
    tmp_path: Path,
) -> None:
    source = write_source(tmp_path / "source")
    db_path = tmp_path / "catalog.db"
    with open_database(db_path) as connection:
        seed_existing_position_tables(connection)
        before_state = connection.execute("SELECT * FROM position_state").fetchall()
        before_occurrence = connection.execute("SELECT * FROM position_occurrence").fetchall()
        before_keys = set(
            connection.execute(
                "SELECT placement, side_to_move, castling, en_passant FROM position_state"
            ).fetchall()
        )

        result = import_catalog(connection, source)

        assert result.status == "success"
        assert result.record_count == 5
        assert connection.execute("SELECT version FROM opening_catalog_schema").fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM opening_catalog").fetchone() == (5,)
        assert connection.execute("SELECT COUNT(*) FROM opening_source_file").fetchone() == (5,)
        assert connection.execute(
            "SELECT status, record_count FROM opening_import_run"
        ).fetchone() == ("success", 5)
        assert connection.execute("SELECT COUNT(*) FROM opening_catalog_state").fetchone() == (1,)
        assert connection.execute("SELECT * FROM position_state").fetchall() == before_state
        assert (
            connection.execute("SELECT * FROM position_occurrence").fetchall() == before_occurrence
        )
        after_keys = set(
            connection.execute(
                "SELECT placement, side_to_move, castling, en_passant FROM position_state"
            ).fetchall()
        )
        opening_keys = set(
            connection.execute(
                "SELECT endpoint_placement, endpoint_side_to_move, endpoint_castling, "
                "endpoint_en_passant FROM opening_catalog"
            ).fetchall()
        )
        opening_only_keys = opening_keys - before_keys
        assert opening_only_keys
        assert after_keys == before_keys
        assert opening_keys & before_keys
        assert opening_only_keys.isdisjoint(after_keys)


def test_same_manifest_rerun_is_unchanged_and_catalog_rows_are_stable(tmp_path: Path) -> None:
    source = write_source(tmp_path / "source")
    db_path = tmp_path / "idempotent.db"
    with open_database(db_path) as connection:
        first = import_catalog(connection, source)
        before = catalog_rows(connection)

        second = import_catalog(connection, source)

        assert first.manifest_hash == second.manifest_hash
        assert second.status == "unchanged"
        assert catalog_rows(connection) == before
        assert connection.execute("SELECT COUNT(*) FROM opening_catalog").fetchone() == (5,)
        assert connection.execute("SELECT COUNT(*) FROM opening_source_manifest").fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM opening_source_file").fetchone() == (5,)
        assert connection.execute(
            "SELECT status, details FROM opening_import_run ORDER BY started_at"
        ).fetchall() == [
            ("success", "initial source publication"),
            ("success", "unchanged source manifest"),
        ]


def test_independent_imports_produce_identical_catalog_rows(tmp_path: Path) -> None:
    first_source = write_source(tmp_path / "first-source")
    second_source = write_source(tmp_path / "second-source")
    first_db = tmp_path / "first.db"
    second_db = tmp_path / "second.db"

    with open_database(first_db) as first, open_database(second_db) as second:
        first_result = import_catalog(first, first_source)
        second_result = import_catalog(second, second_source)

        assert first_result.manifest_hash == second_result.manifest_hash
        assert catalog_rows(first) == catalog_rows(second)
        assert (
            first.execute(
                "SELECT source_file, source_file_hash, record_count FROM opening_source_file "
                "ORDER BY source_file"
            ).fetchall()
            == second.execute(
                "SELECT source_file, source_file_hash, record_count FROM opening_source_file "
                "ORDER BY source_file"
            ).fetchall()
        )


def test_incompatible_schema_is_refused_without_opening_table_writes(tmp_path: Path) -> None:
    db_path = tmp_path / "incompatible.db"
    with open_database(db_path) as connection:
        connection.execute(
            "CREATE TABLE opening_catalog_schema ("
            "id INTEGER PRIMARY KEY CHECK (id = 1), "
            "version INTEGER NOT NULL, applied_at TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO opening_catalog_schema VALUES (1, 99, '2026-01-01T00:00:00Z')"
        )
        connection.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sentinel VALUES ('untouched')")
        connection.commit()

        with pytest.raises(OpeningSchemaError, match="version 99"):
            ensure_schema(connection)

        assert connection.execute("SELECT value FROM sentinel").fetchone() == ("untouched",)
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'opening_catalog'"
            ).fetchone()
            is None
        )


def test_changed_manifest_records_failure_without_replacing_accepted_catalog(
    tmp_path: Path,
) -> None:
    source = write_source(tmp_path / "source")
    db_path = tmp_path / "changed.db"
    with open_database(db_path) as connection:
        first = import_catalog(connection, source)
        before = catalog_rows(connection)
        before_state = connection.execute("SELECT * FROM opening_catalog_state").fetchall()

        changed_rows = dict(ROWS)
        changed_rows["c.tsv"] = ("C21", "Changed Source Record", "1. e4 c5")
        (source / "c.tsv").unlink()
        write_source(tmp_path / "changed-source", changed_rows)
        changed_source = tmp_path / "changed-source"
        changed_manifest = load_source(changed_source)

        with pytest.raises(OpeningSourceChangedError, match="manifest changed"):
            import_catalog(connection, changed_source)

        assert catalog_rows(connection) == before
        assert connection.execute("SELECT * FROM opening_catalog_state").fetchall() == before_state
        assert connection.execute(
            "SELECT manifest_hash, status, record_count, details FROM opening_import_run "
            "WHERE manifest_hash <> ?",
            (first.manifest_hash,),
        ).fetchone() == (
            changed_manifest.manifest_hash,
            "failed",
            changed_manifest.record_count,
            "source manifest changed; explicit approval is required for a new source version",
        )
        assert connection.execute(
            "SELECT accepted_manifest_hash FROM opening_catalog_state"
        ).fetchone() == (first.manifest_hash,)
        assert connection.execute(
            "SELECT COUNT(*) FROM opening_catalog WHERE manifest_hash = ?",
            (first.manifest_hash,),
        ).fetchone() == (5,)


def test_replay_failure_records_failed_run_without_catalog_rows(tmp_path: Path) -> None:
    invalid_rows = dict(ROWS)
    invalid_rows["d.tsv"] = ("D00", "Invalid", "1. e4 e5 2. e5")
    source = write_source(tmp_path / "source", invalid_rows)
    db_path = tmp_path / "replay-failure.db"
    with open_database(db_path) as connection:
        with pytest.raises(OpeningReplayError, match=r"d.tsv row 1"):
            import_catalog(connection, source)

        assert connection.execute("SELECT COUNT(*) FROM opening_catalog").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM opening_catalog_state").fetchone() == (0,)
        assert connection.execute("SELECT status FROM opening_import_run").fetchone() == ("failed",)


def test_storage_failure_rolls_back_catalog_and_records_failed_run(tmp_path: Path) -> None:
    source = write_source(tmp_path / "source")
    db_path = tmp_path / "storage-failure.db"
    with open_database(db_path) as connection:
        ensure_schema(connection)
        connection.execute(
            """
            CREATE TRIGGER fail_opening_insert
            BEFORE INSERT ON opening_catalog
            BEGIN
                SELECT RAISE(ABORT, 'forced storage failure');
            END
            """
        )
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError, match="forced storage failure"):
            import_catalog(connection, source)

        assert connection.execute("SELECT COUNT(*) FROM opening_catalog").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM opening_catalog_state").fetchone() == (0,)
        assert connection.execute("SELECT status, details FROM opening_import_run").fetchone() == (
            "failed",
            "forced storage failure",
        )


def test_source_directory_contract_rejects_extra_files(tmp_path: Path) -> None:
    source = write_source(tmp_path / "source")
    (source / "extra.tsv").write_text("eco\tname\tpgn\n", encoding="utf-8")

    with pytest.raises(OpeningCatalogError, match="expected source files"):
        load_source(source)


def relationship_rows(
    connection: sqlite3.Connection,
) -> tuple[tuple[str, list[tuple[object, ...]]], ...]:
    tables = (
        "opening_relationship_schema",
        "opening_relationship_state",
        "opening_relationship_run",
        "opening_relationship_position",
        "opening_position_membership",
        "opening_parent_link",
        "opening_transposition_link",
    )
    return tuple(
        (table, connection.execute(f"SELECT * FROM {table}").fetchall()) for table in tables
    )


def test_relationship_publication_is_deterministic_and_preserves_s1_and_game_rows(
    tmp_path: Path,
) -> None:
    source = write_source(tmp_path / "source")
    db_path = tmp_path / "relationships.db"

    with open_database(db_path) as connection:
        seed_existing_position_tables(connection)
        first = import_catalog(connection, source)
        s1_before = catalog_rows(connection)
        game_before = (
            connection.execute("SELECT * FROM position_state").fetchall(),
            connection.execute("SELECT * FROM position_occurrence").fetchall(),
        )

        result = import_relationships(connection, source)
        first_rows = relationship_rows(connection)

        assert result.status == "success"
        assert result.manifest_hash == first.manifest_hash
        assert result.record_count == 5
        assert result.membership_count == 9
        assert connection.execute(
            "SELECT accepted_manifest_hash, accepted_schema_version, record_count, "
            "position_count, membership_count, parent_link_count, transposition_link_count "
            "FROM opening_relationship_state"
        ).fetchone() == (
            first.manifest_hash,
            RELATIONSHIP_SCHEMA_VERSION,
            5,
            result.position_count,
            9,
            result.parent_link_count,
            result.transposition_link_count,
        )

        rerun = import_relationships(connection, source)

        assert rerun.status == "unchanged"
        assert relationship_rows(connection) == first_rows
        assert catalog_rows(connection) == s1_before
        assert (
            connection.execute("SELECT * FROM position_state").fetchall(),
            connection.execute("SELECT * FROM position_occurrence").fetchall(),
        ) == game_before

    other_db = tmp_path / "other.db"
    with open_database(other_db) as connection:
        import_catalog(connection, write_source(tmp_path / "other-source"))
        import_relationships(connection, tmp_path / "other-source")
        assert relationship_rows(connection) == first_rows


def test_relationship_publication_rolls_back_without_partial_facts(tmp_path: Path) -> None:
    source = write_source(tmp_path / "source")
    db_path = tmp_path / "rollback.db"

    with open_database(db_path) as connection:
        import_catalog(connection, source)
        s1_before = catalog_rows(connection)
        ensure_relationship_schema(connection)
        connection.execute(
            """
            CREATE TRIGGER fail_relationship_membership
            BEFORE INSERT ON opening_position_membership
            BEGIN
                SELECT RAISE(ABORT, 'forced relationship failure');
            END
            """
        )
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError, match="forced relationship failure"):
            import_relationships(connection, source)

        assert catalog_rows(connection) == s1_before
        for table in (
            "opening_relationship_state",
            "opening_relationship_run",
            "opening_relationship_position",
            "opening_position_membership",
            "opening_parent_link",
            "opening_transposition_link",
        ):
            assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone() == (0,)


def test_incompatible_relationship_schema_is_refused_without_relationship_writes(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "incompatible-relationships.db"
    with open_database(db_path) as connection:
        connection.execute(
            "CREATE TABLE opening_relationship_schema ("
            "id INTEGER PRIMARY KEY CHECK (id = 1), version INTEGER NOT NULL)"
        )
        connection.execute("INSERT INTO opening_relationship_schema VALUES (1, 99)")
        connection.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sentinel VALUES ('untouched')")
        connection.commit()

        with pytest.raises(OpeningSchemaError, match="relationship schema version 99"):
            ensure_relationship_schema(connection)

        assert connection.execute("SELECT value FROM sentinel").fetchone() == ("untouched",)
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'opening_relationship_position'"
            ).fetchone()
            is None
        )
