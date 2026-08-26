from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scripts.chess_com._schema import ensure_corpus_schema
from scripts.opening_catalog import (
    BRANCH_KINDS,
    CLASSIFICATION_SCHEMA_VERSION,
    COLOR_SCOPES,
    RECURRENCE_SCHEMA_VERSION,
    OpeningSchemaError,
    branch_identity,
    branch_projection_key,
    derive_recurrence,
    ensure_classification_schema,
    ensure_recurrence_schema,
    ensure_relationship_schema,
    ensure_schema,
    game_identity,
    import_recurrence,
    occurrence_identity,
    position_projection_key,
    project_recurrence,
    publish_recurrence,
    route_identity,
    route_projection_key,
)
from scripts.opening_catalog.recurrence_persistence import RecurrencePublicationError, _matches
from scripts.opening_catalog.recurrence_schema import RECURRENCE_SCHEMA_TABLES

MANIFEST = "manifest-stage1"
CORPUS_ID = 7
POSITION_A = ("8/8/8/8/8/8/8/K6k", "w", "-", "-")
POSITION_B = ("8/8/8/8/8/8/8/k6K1", "b", "-", "-")
CATALOG_A = (MANIFEST, "a.tsv", 1)
CATALOG_B = (MANIFEST, "b.tsv", 1)


def open_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def seed_stage1_dependencies(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE players (uuid TEXT PRIMARY KEY, username TEXT NOT NULL, profile_url TEXT);
        CREATE TABLE games (
            uuid TEXT PRIMARY KEY, url TEXT NOT NULL, pgn TEXT NOT NULL,
            time_control TEXT NOT NULL, end_time INTEGER NOT NULL, rated INTEGER,
            tcn TEXT, initial_setup TEXT, fen TEXT, time_class TEXT, rules TEXT, eco TEXT,
            white_player_uuid TEXT NOT NULL, black_player_uuid TEXT NOT NULL,
            white_rating INTEGER, black_rating INTEGER, white_result TEXT, black_result TEXT,
            year INTEGER NOT NULL, month INTEGER NOT NULL,
            FOREIGN KEY (white_player_uuid) REFERENCES players(uuid),
            FOREIGN KEY (black_player_uuid) REFERENCES players(uuid)
        );
        INSERT INTO players VALUES ('subject', 'subject', NULL), ('opponent', 'opponent', NULL);
        INSERT INTO games VALUES
            ('game-1', 'url-1', 'pgn-1', '600', 1700000000, 1, NULL, NULL, NULL,
             'rapid', 'chess', 'A00', 'subject', 'opponent', 1800, 1790, 'win', 'loss', 2023, 11),
            ('game-2', 'url-2', 'pgn-2', '600', 1700000001, 1, NULL, NULL, NULL,
             'rapid', 'chess', 'A00', 'opponent', 'subject', 1795, 1810, 'loss', 'win', 2023, 11);
        """
    )
    ensure_schema(connection)
    ensure_relationship_schema(connection)
    ensure_corpus_schema(connection)
    ensure_classification_schema(connection)
    connection.executescript(
        """
        INSERT INTO opening_source_manifest
            (manifest_hash, source_dataset, file_count, record_count, created_at)
        VALUES ('manifest-stage1', 'test', 5, 2, 'now');
        INSERT INTO opening_source_file
            (manifest_hash, source_file, source_file_hash, record_count)
        VALUES ('manifest-stage1', 'a.tsv', 'file-a', 1),
               ('manifest-stage1', 'b.tsv', 'file-b', 1);
        INSERT INTO opening_catalog
            (manifest_hash, source_file, source_row_ordinal, source_row_hash, eco, name,
             move_sequence, endpoint_fen, endpoint_placement, endpoint_side_to_move,
             endpoint_castling, endpoint_en_passant, endpoint_halfmove_clock,
             endpoint_fullmove_number)
        VALUES
            ('manifest-stage1', 'a.tsv', 1, 'row-a', 'A00', 'First', '1. a4',
             'fen-a', '8/8/8/8/8/8/8/K6k', 'w', '-', '-', 0, 1),
            ('manifest-stage1', 'b.tsv', 1, 'row-b', 'A00', 'Second', '1. a4',
             'fen-a', '8/8/8/8/8/8/8/K6k', 'w', '-', '-', 0, 1);
        INSERT INTO opening_catalog_state
            (id, accepted_manifest_hash, accepted_schema_version, accepted_at, record_count)
        VALUES (1, 'manifest-stage1', 1, 'now', 2);
        INSERT INTO opening_relationship_state
            (accepted_manifest_hash, accepted_schema_version, record_count, position_count,
             membership_count, parent_link_count, transposition_link_count)
        VALUES ('manifest-stage1', 1, 2, 2, 2, 0, 0);
        INSERT INTO opening_relationship_position
            (manifest_hash, placement, side_to_move, castling, en_passant)
        VALUES ('manifest-stage1', '8/8/8/8/8/8/8/K6k', 'w', '-', '-');
        INSERT INTO opening_position_membership
            (manifest_hash, source_file, source_row_ordinal, ply, placement, side_to_move,
             castling, en_passant, uci, san, uci_prefix)
        VALUES
            ('manifest-stage1', 'a.tsv', 1, 1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-',
             'a2a4', 'a4', 'a2a4'),
            ('manifest-stage1', 'b.tsv', 1, 1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-',
             'a2a4', 'a4', 'a2a4');
        INSERT INTO corpus (corpus_id, subject_player_uuid) VALUES (7, 'subject');
        INSERT INTO corpus_game (corpus_id, game_uuid, rules, fingerprint)
        VALUES (7, 'game-1', 'chess', 'fingerprint-1'),
               (7, 'game-2', 'chess', 'fingerprint-2');
        INSERT INTO position_state
            (state_id, placement, side_to_move, castling, en_passant)
        VALUES (1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-'),
               (2, '8/8/8/8/8/8/8/k6K1', 'b', '-', '-');
        INSERT INTO position_occurrence
            (game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number)
        VALUES
            ('game-1', 0, 1, NULL, NULL, 0, 1),
            ('game-1', 1, 2, 'Kh1', 'g1h1', 1, 1),
            ('game-1', 2, 1, 'Ka1', 'h1a1', 2, 2),
            ('game-2', 0, 1, NULL, NULL, 0, 1),
            ('game-2', 1, 2, 'Kh1', 'g1h1', 1, 1);
        INSERT INTO opening_classification_state
            (accepted_manifest_hash, corpus_id, accepted_schema_version,
             accepted_catalog_schema_version, accepted_relationship_schema_version, accepted_at)
        VALUES ('manifest-stage1', 7, 1, 1, 1, 'now');
        INSERT INTO opening_classification_game
            (manifest_hash, corpus_id, game_uuid, source_fingerprint)
        VALUES ('manifest-stage1', 7, 'game-1', 'fingerprint-1'),
               ('manifest-stage1', 7, 'game-2', 'fingerprint-2');
        INSERT INTO opening_classification_anchor
            (manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal,
             anchor_placement, anchor_side_to_move, anchor_castling, anchor_en_passant,
             anchor_san, anchor_uci)
        VALUES
            ('manifest-stage1', 7, 'game-1', 1, 'a.tsv', 1, '8/8/8/8/8/8/8/K6k',
             'w', '-', '-', 'a4', 'a2a4'),
            ('manifest-stage1', 7, 'game-1', 1, 'b.tsv', 1, '8/8/8/8/8/8/8/K6k',
             'w', '-', '-', 'a4', 'a2a4');
        INSERT INTO opening_classification_route
            (manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal,
             route_ply, route_placement, route_side_to_move, route_castling, route_en_passant,
             route_san, route_uci, route_halfmove_clock, route_fullmove_number)
        VALUES
            ('manifest-stage1', 7, 'game-1', 1, 'a.tsv', 1, 1, '8/8/8/8/8/8/8/K6k',
             'w', '-', '-', 'a4', 'a2a4', 0, 1),
            ('manifest-stage1', 7, 'game-1', 1, 'a.tsv', 1, 2, '8/8/8/8/8/8/8/k6K1',
             'b', '-', '-', 'Kh1', 'g1h1', 1, 1),
            ('manifest-stage1', 7, 'game-1', 1, 'b.tsv', 1, 1, '8/8/8/8/8/8/8/K6k',
             'w', '-', '-', 'a4', 'a2a4', 0, 1);
        """
    )
    connection.commit()


def seed_stage2_dependencies(connection: sqlite3.Connection) -> None:
    """Make the compact Stage 1 boundary fixture internally route-consistent."""

    seed_stage1_dependencies(connection)
    connection.execute(
        "UPDATE position_occurrence SET state_id = CASE ply WHEN 1 THEN 1 WHEN 2 THEN 2 "
        "ELSE state_id END, san = CASE ply WHEN 1 THEN 'a4' WHEN 2 THEN 'Kh1' ELSE san END, "
        "uci = CASE ply WHEN 1 THEN 'a2a4' WHEN 2 THEN 'g1h1' ELSE uci END "
        "WHERE game_uuid = 'game-1'"
    )
    connection.commit()


def seed_stage3_dependencies(connection: sqlite3.Connection) -> None:
    """Extend the compact fixture with a tied, black-side repeated game."""

    seed_stage2_dependencies(connection)
    connection.execute("UPDATE games SET end_time = 1700000000 WHERE uuid = 'game-2'")
    connection.execute(
        "INSERT INTO position_occurrence "
        "(game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number) "
        "VALUES ('game-2', 2, 1, 'Ka1', 'h1a1', 2, 2)"
    )
    connection.executemany(
        "INSERT INTO opening_classification_anchor "
        "(manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal, "
        "anchor_placement, anchor_side_to_move, anchor_castling, anchor_en_passant, "
        "anchor_san, anchor_uci) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (MANIFEST, CORPUS_ID, "game-2", 2, "a.tsv", 1, *POSITION_A, "Ka1", "h1a1"),
            (MANIFEST, CORPUS_ID, "game-2", 2, "b.tsv", 1, *POSITION_A, "Ka1", "h1a1"),
        ],
    )
    connection.executemany(
        "INSERT INTO opening_classification_route "
        "(manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal, "
        "route_ply, route_placement, route_side_to_move, route_castling, route_en_passant, "
        "route_san, route_uci, route_halfmove_clock, route_fullmove_number) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (MANIFEST, CORPUS_ID, "game-2", 2, "a.tsv", 1, 2, *POSITION_A, "Ka1", "h1a1", 2, 2),
            (MANIFEST, CORPUS_ID, "game-2", 2, "b.tsv", 1, 2, *POSITION_A, "Ka1", "h1a1", 2, 2),
        ],
    )
    connection.commit()


def upstream_signature(connection: sqlite3.Connection) -> tuple[tuple[str, list[tuple]], ...]:
    tables = (
        "opening_source_manifest",
        "opening_source_file",
        "opening_catalog",
        "opening_catalog_state",
        "opening_relationship_state",
        "opening_relationship_position",
        "opening_position_membership",
        "opening_classification_state",
        "opening_classification_game",
        "opening_classification_anchor",
        "opening_classification_route",
        "corpus",
        "corpus_game",
        "position_state",
        "position_occurrence",
    )
    return tuple(
        (table, connection.execute(f"SELECT * FROM {table}").fetchall()) for table in tables
    )


def test_stage1_identities_are_natural_stable_and_policy_neutral() -> None:
    assert game_identity(CORPUS_ID, "game-1") == (CORPUS_ID, "game-1")
    assert occurrence_identity(CORPUS_ID, "game-1", 2) != occurrence_identity(
        CORPUS_ID, "game-1", 0
    )
    assert occurrence_identity(CORPUS_ID, "game-1", 0) != occurrence_identity(
        CORPUS_ID, "game-2", 0
    )
    assert route_identity(CORPUS_ID, "game-1", 1, "a.tsv", 1, 1) != route_identity(
        CORPUS_ID, "game-1", 1, "b.tsv", 1, 1
    )
    assert branch_identity(CORPUS_ID, "game-1", 1, "move") != branch_identity(
        CORPUS_ID, "game-1", 1, "terminal"
    )

    assert position_projection_key(MANIFEST, CORPUS_ID, POSITION_A, "overall") == (
        MANIFEST,
        CORPUS_ID,
        *POSITION_A,
        "overall",
    )
    assert route_projection_key(MANIFEST, CORPUS_ID, CATALOG_A, 1, POSITION_A, "white") != (
        route_projection_key(MANIFEST, CORPUS_ID, CATALOG_B, 1, POSITION_A, "white")
    )
    assert branch_projection_key(MANIFEST, CORPUS_ID, POSITION_A, "terminal", None, "black")[
        -3:
    ] == ("terminal", "", "black")
    assert set(COLOR_SCOPES) == {"overall", "white", "black"}
    assert set(BRANCH_KINDS) == {"move", "terminal"}
    with pytest.raises(ValueError, match="unsupported color scope"):
        position_projection_key(MANIFEST, CORPUS_ID, POSITION_A, "formula")


def test_stage1_schema_is_additive_and_retains_repeated_memberships_and_context(
    tmp_path: Path,
) -> None:
    with open_database(tmp_path / "recurrence-contract.db") as connection:
        seed_stage1_dependencies(connection)
        before = upstream_signature(connection)

        ensure_recurrence_schema(connection)

        assert upstream_signature(connection) == before
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND name LIKE 'opening_recurrence_%'"
            )
        }
        assert names == RECURRENCE_SCHEMA_TABLES
        assert connection.execute(
            "SELECT version FROM opening_recurrence_schema WHERE id = 1"
        ).fetchone() == (RECURRENCE_SCHEMA_VERSION,)
        for table in RECURRENCE_SCHEMA_TABLES:
            sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE name = ?", (table,)
            ).fetchone()[0]
            assert "WITHOUT ROWID" in sql
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            assert not columns & {"player_id", "player_uuid", "username", "rowid"}
            assert not columns & {"formula", "threshold", "weight", "priority", "frontier"}

        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(opening_recurrence_position_projection)"
            )
        } >= {"raw_occurrence_count", "distinct_game_count"}

        connection.execute(
            "INSERT INTO opening_recurrence_state VALUES "
            "(?, ?, 1, ?, ?, ?, 1, ?, ?, ?, 'now', 2, 5, 3, 2)",
            (
                MANIFEST,
                CORPUS_ID,
                CLASSIFICATION_SCHEMA_VERSION,
                1,
                1,
                "classification-sig",
                "corpus-sig",
                "games-sig",
            ),
        )
        connection.executemany(
            "INSERT INTO opening_recurrence_game "
            "(manifest_hash, corpus_id, game_uuid, source_fingerprint, metadata_fingerprint, "
            "game_sequence, end_time, year, month, time_control, time_class, white_rating, "
            "black_rating, white_result, black_result) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    MANIFEST,
                    CORPUS_ID,
                    "game-1",
                    "fingerprint-1",
                    "meta-1",
                    1,
                    1700000000,
                    2023,
                    11,
                    "600",
                    "rapid",
                    1800,
                    1790,
                    "win",
                    "loss",
                ),
                (
                    MANIFEST,
                    CORPUS_ID,
                    "game-2",
                    "fingerprint-2",
                    "meta-2",
                    2,
                    1700000001,
                    2023,
                    11,
                    "600",
                    "rapid",
                    1795,
                    1810,
                    "loss",
                    "win",
                ),
            ],
        )
        occurrence_rows = [
            (MANIFEST, CORPUS_ID, "game-1", 0, *POSITION_A, None, None, 0, 1),
            (MANIFEST, CORPUS_ID, "game-1", 1, *POSITION_B, "Kh1", "g1h1", 1, 1),
            (MANIFEST, CORPUS_ID, "game-1", 2, *POSITION_A, "Ka1", "h1a1", 2, 2),
            (MANIFEST, CORPUS_ID, "game-2", 0, *POSITION_A, None, None, 0, 1),
            (MANIFEST, CORPUS_ID, "game-2", 1, *POSITION_B, "Kh1", "g1h1", 1, 1),
        ]
        connection.executemany(
            "INSERT INTO opening_recurrence_occurrence "
            "(manifest_hash, corpus_id, game_uuid, ply, placement, side_to_move, castling, "
            "en_passant, san, uci, halfmove_clock, fullmove_number) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            occurrence_rows,
        )
        route_rows = [
            (MANIFEST, CORPUS_ID, "game-1", 1, "a.tsv", 1, 1, *POSITION_A, "a4", "a2a4", 0, 1),
            (MANIFEST, CORPUS_ID, "game-1", 1, "a.tsv", 1, 2, *POSITION_B, "Kh1", "g1h1", 1, 1),
            (MANIFEST, CORPUS_ID, "game-1", 1, "b.tsv", 1, 1, *POSITION_A, "a4", "a2a4", 0, 1),
        ]
        connection.executemany(
            "INSERT INTO opening_recurrence_route_event "
            "(manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal, "
            "route_ply, placement, side_to_move, castling, en_passant, san, uci, "
            "halfmove_clock, fullmove_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            route_rows,
        )
        connection.executemany(
            "INSERT INTO opening_recurrence_branch_event "
            "(manifest_hash, corpus_id, game_uuid, parent_ply, parent_placement, "
            "parent_side_to_move, parent_castling, parent_en_passant, branch_kind, child_ply, "
            "child_placement, child_side_to_move, child_castling, child_en_passant, child_san, "
            "child_uci, terminal_outcome) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    MANIFEST,
                    CORPUS_ID,
                    "game-1",
                    0,
                    *POSITION_A,
                    "move",
                    1,
                    *POSITION_B,
                    "Kh1",
                    "g1h1",
                    None,
                ),
                (
                    MANIFEST,
                    CORPUS_ID,
                    "game-1",
                    2,
                    *POSITION_A,
                    "terminal",
                    2,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    "checkmate",
                ),
            ],
        )
        connection.commit()

        assert connection.execute(
            "SELECT COUNT(*) FROM opening_recurrence_occurrence WHERE placement = ?",
            (POSITION_A[0],),
        ).fetchone() == (3,)
        assert connection.execute(
            "SELECT COUNT(*) FROM opening_recurrence_route_event"
        ).fetchone() == (3,)
        assert connection.execute(
            "SELECT source_file FROM opening_recurrence_route_event ORDER BY source_file, route_ply"
        ).fetchall() == [("a.tsv",), ("a.tsv",), ("b.tsv",)]
        assert connection.execute(
            "SELECT branch_kind, child_uci, terminal_outcome "
            "FROM opening_recurrence_branch_event ORDER BY parent_ply"
        ).fetchall() == [("move", "g1h1", None), ("terminal", None, "checkmate")]
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_stage1_schema_refuses_missing_prerequisite_and_incompatible_version(
    tmp_path: Path,
) -> None:
    with open_database(tmp_path / "missing-prerequisite.db") as connection:
        with pytest.raises(OpeningSchemaError, match="accepted corpus schemas"):
            ensure_recurrence_schema(connection)
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name LIKE 'opening_recurrence_%'"
            ).fetchall()
            == []
        )

    with open_database(tmp_path / "incompatible-version.db") as connection:
        seed_stage1_dependencies(connection)
        connection.execute(
            "CREATE TABLE opening_recurrence_schema "
            "(id INTEGER PRIMARY KEY CHECK (id = 1), version INTEGER NOT NULL) WITHOUT ROWID"
        )
        connection.execute("INSERT INTO opening_recurrence_schema VALUES (1, 99)")
        connection.commit()

        with pytest.raises(OpeningSchemaError, match="recurrence schema version 99"):
            ensure_recurrence_schema(connection)
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'opening_recurrence_game'"
            ).fetchone()
            is None
        )


def test_stage2_derives_events_and_rebuildable_projections_without_upstream_mutation(
    tmp_path: Path,
) -> None:
    with open_database(tmp_path / "recurrence-derivation.db") as connection:
        seed_stage2_dependencies(connection)
        before = upstream_signature(connection)

        facts = derive_recurrence(connection, CORPUS_ID)
        projections = project_recurrence(facts)

        assert facts.game_count == 2
        assert facts.occurrence_count == 5
        assert facts.route_event_count == 3
        assert facts.branch_event_count == 5
        assert [item.game_color for item in facts.games] == ["white", "black"]
        assert [item.branch_kind for item in facts.branches].count("terminal") == 2
        assert projections == facts.projections
        position_a = [item for item in projections.positions if item.key == POSITION_A]
        assert {
            (item.color_scope, item.raw_occurrence_count, item.distinct_game_count)
            for item in position_a
        } == {
            ("overall", 3, 2),
            ("white", 2, 1),
            ("black", 1, 1),
        }

        result = import_recurrence(connection, CORPUS_ID)
        assert result.status == "success"
        assert result.run_id
        assert result.position_projection_count == len(projections.positions)
        assert result.route_branch_projection_count == len(projections.route_branches)
        assert upstream_signature(connection) == before
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_stage3_independent_builds_and_unchanged_rerun_are_exact(tmp_path: Path) -> None:
    def build(path: Path) -> tuple[sqlite3.Connection, object, tuple[tuple[str, list[tuple]], ...]]:
        connection = open_database(path)
        seed_stage3_dependencies(connection)
        first = import_recurrence(connection, CORPUS_ID)
        second = import_recurrence(connection, CORPUS_ID)
        assert first.status == "success"
        assert second.status == "unchanged"
        assert second.run_id == first.run_id
        tables = (
            "opening_recurrence_game",
            "opening_recurrence_occurrence",
            "opening_recurrence_route_event",
            "opening_recurrence_branch_event",
            "opening_recurrence_position_projection",
            "opening_recurrence_route_projection",
            "opening_recurrence_branch_projection",
            "opening_recurrence_route_branch_projection",
        )
        snapshot = tuple(
            (table, connection.execute(f"SELECT * FROM {table} ORDER BY 1, 2, 3").fetchall())
            for table in tables
        )
        return connection, first, snapshot

    first_connection, first_result, first_snapshot = build(tmp_path / "first.db")
    second_connection, second_result, second_snapshot = build(tmp_path / "second.db")
    try:
        assert first_result.run_id == second_result.run_id
        assert first_snapshot == second_snapshot
    finally:
        first_connection.close()
        second_connection.close()


def test_stage2_metadata_change_refusal_and_storage_failure_rollback(tmp_path: Path) -> None:
    with open_database(tmp_path / "recurrence-rollback.db") as connection:
        seed_stage2_dependencies(connection)
        facts = derive_recurrence(connection, CORPUS_ID)
        connection.execute("UPDATE games SET end_time = end_time + 1 WHERE uuid = 'game-1'")
        connection.commit()
        with pytest.raises(RecurrencePublicationError, match="inputs"):
            publish_recurrence(connection, facts)
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name LIKE 'opening_recurrence_%'"
            ).fetchall()
            == []
        )

        connection.execute("UPDATE games SET end_time = end_time - 1 WHERE uuid = 'game-1'")
        connection.commit()
        facts = derive_recurrence(connection, CORPUS_ID)
        ensure_recurrence_schema(connection)
        connection.execute(
            "CREATE TRIGGER fail_recurrence_route INSERT ON opening_recurrence_route_event "
            "BEGIN SELECT RAISE(ABORT, 'injected S4 storage failure'); END"
        )
        connection.commit()
        with pytest.raises(sqlite3.IntegrityError, match="injected S4 storage failure"):
            publish_recurrence(connection, facts)
        for table in (
            "opening_recurrence_state",
            "opening_recurrence_run",
            "opening_recurrence_game",
            "opening_recurrence_occurrence",
            "opening_recurrence_route_event",
            "opening_recurrence_branch_event",
            "opening_recurrence_position_projection",
            "opening_recurrence_route_projection",
            "opening_recurrence_branch_projection",
            "opening_recurrence_route_branch_projection",
        ):
            assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone() == (0,)


def test_stage3_expected_recurrence_branch_and_preservation_facts(tmp_path: Path) -> None:
    with open_database(tmp_path / "recurrence-stage3.db") as connection:
        seed_stage3_dependencies(connection)
        before = upstream_signature(connection)
        facts = derive_recurrence(connection, CORPUS_ID)

        assert [(item.game_uuid, item.game_sequence, item.game_color) for item in facts.games] == [
            ("game-1", 1, "white"),
            ("game-2", 2, "black"),
        ]
        assert [
            (
                item.end_time,
                item.white_rating,
                item.black_rating,
                item.white_result,
                item.black_result,
            )
            for item in facts.games
        ] == [(1700000000, 1800, 1790, "win", "loss"), (1700000000, 1795, 1810, "loss", "win")]
        assert facts.occurrence_count == 6
        assert facts.route_event_count == 5
        assert [
            (item.game_uuid, item.ply) for item in facts.occurrences if item.key == POSITION_A
        ] == [("game-1", 0), ("game-1", 1), ("game-2", 0), ("game-2", 2)]
        assert [
            (item.game_uuid, item.anchor_ply, item.catalog[1], item.route_ply, item.key)
            for item in facts.routes
        ] == [
            ("game-1", 1, "a.tsv", 1, POSITION_A),
            ("game-1", 1, "a.tsv", 2, POSITION_B),
            ("game-1", 1, "b.tsv", 1, POSITION_A),
            ("game-2", 2, "a.tsv", 2, POSITION_A),
            ("game-2", 2, "b.tsv", 2, POSITION_A),
        ]
        assert {
            (item.game_uuid, item.parent_ply, item.child_ply, item.child_uci)
            for item in facts.branches
            if item.branch_kind == "move"
        } == {
            ("game-1", 0, 1, "a2a4"),
            ("game-1", 1, 2, "g1h1"),
            ("game-2", 0, 1, "g1h1"),
            ("game-2", 1, 2, "h1a1"),
        }
        assert {
            (item.game_uuid, item.parent_ply, item.terminal_outcome)
            for item in facts.branches
            if item.branch_kind == "terminal"
        } == {("game-1", 2, "white_win"), ("game-2", 2, "white_loss")}

        projections = project_recurrence(facts)
        assert {
            (
                item.color_scope,
                item.raw_occurrence_count,
                item.distinct_game_count,
                item.first_game_uuid,
                item.first_ply,
                item.last_game_uuid,
                item.last_ply,
            )
            for item in projections.positions
            if item.key == POSITION_A
        } == {
            ("overall", 4, 2, "game-1", 0, "game-2", 2),
            ("white", 2, 1, "game-1", 0, "game-1", 1),
            ("black", 2, 1, "game-2", 0, "game-2", 2),
        }
        assert [
            (item.color_scope, item.raw_occurrence_count, item.distinct_game_count)
            for item in projections.routes
            if item.catalog == CATALOG_A and item.anchor_ply == 1 and item.key == POSITION_A
        ] == [("overall", 1, 1), ("white", 1, 1)]
        assert {
            (item.color_scope, item.raw_event_count, item.distinct_game_count)
            for item in projections.branches
            if (
                item.parent_key == POSITION_A
                and item.branch_kind == "move"
                and item.child_uci == "g1h1"
            )
        } == {("overall", 2, 2), ("white", 1, 1), ("black", 1, 1)}
        assert len(projections.route_branches) == 10
        assert {
            (item.catalog[1], item.anchor_ply, item.branch_kind, item.child_uci, item.color_scope)
            for item in projections.route_branches
            if item.catalog == CATALOG_B
        } == {
            ("b.tsv", 1, "move", "g1h1", "overall"),
            ("b.tsv", 1, "move", "g1h1", "white"),
            ("b.tsv", 2, "terminal", "", "overall"),
            ("b.tsv", 2, "terminal", "", "black"),
        }

        result = import_recurrence(connection, CORPUS_ID)
        assert result.status == "success"
        assert result.route_event_count == len(facts.routes)
        assert result.position_projection_count == len(projections.positions)
        assert upstream_signature(connection) == before
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []

        connection.execute("UPDATE games SET pgn = 'changed-pgn' WHERE uuid = 'game-1'")
        connection.commit()
        with pytest.raises(RecurrencePublicationError, match="inputs"):
            publish_recurrence(connection, facts)
        connection.execute("UPDATE games SET pgn = 'pgn-1' WHERE uuid = 'game-1'")
        connection.execute(
            "UPDATE opening_recurrence_route_event SET san = 'tampered' "
            "WHERE game_uuid = 'game-1' AND source_file = 'a.tsv' AND route_ply = 1"
        )
        connection.commit()
        assert not _matches(connection, facts, projections)
