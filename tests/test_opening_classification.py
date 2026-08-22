from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import pytest

from scripts.chess_com import extract_corpus
from scripts.chess_com._schema import ensure_corpus_schema
from scripts.opening_catalog import (
    CLASSIFICATION_SCHEMA_VERSION,
    AnchorIdentity,
    ClassificationError,
    OpeningSchemaError,
    derive_classification,
    ensure_classification_schema,
    ensure_relationship_schema,
    ensure_schema,
    exact_endpoint_match,
    import_catalog,
    import_classification,
    import_relationships,
    suffix_plies,
    validate_route_plies,
)

MANIFEST = "manifest-s3-contract"
PLACEMENT = "8/8/8/8/8/8/8/K6k"
ROUTE_PLACEMENT = "8/8/8/8/8/8/8/k6K1"
POSITION_KEY = (PLACEMENT, "w", "-", "-")
ROUTE_KEY = (ROUTE_PLACEMENT, "b", "-", "-")

RICH_SOURCE_ROWS = {
    "a.tsv": ("C60", "Open Games / Ruy Lopez", "1. e4 e5 2. Nf3 Nc6 3. Bb5"),
    "b.tsv": (
        "C60",
        "Open Games / Ruy Lopez / Transposition",
        "1. Nf3 Nc6 2. e4 e5 3. Bb5",
    ),
    "c.tsv": ("A00", "Taxonomy / Knight Reversal", "1. Nf3 Nf6 2. Ng1 Ng8"),
    "d.tsv": (
        "A00",
        "Taxonomy / Neutral / e4",
        "1. Nf3 Nf6 2. Ng1 Ng8 3. e4",
    ),
    "e.tsv": (
        "A00",
        "Taxonomy / Neutral / e4 / Transposition",
        "1. e4 Nf6 2. Nf3 Ng8 3. Ng1",
    ),
}
RICH_GAME_PGNS = {
    "game-1": '[Event "fixture"]\n[Result "*"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *\n',
    "game-2": (
        '[Event "fixture"]\n[Result "*"]\n\n1. Nf3 Nf6 2. Ng1 Ng8 3. Nf3 Nf6 4. Ng1 Ng8 5. e4 *\n'
    ),
    "game-3": '[Event "fixture"]\n[Result "*"]\n\n1. e4 Nf6 2. Nf3 Ng8 3. Ng1 *\n',
}


def open_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def seed_contract_dependencies(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE players (uuid TEXT PRIMARY KEY);
        CREATE TABLE games (uuid TEXT PRIMARY KEY);
        INSERT INTO players VALUES ('subject');
        INSERT INTO games VALUES ('game-1');
        """
    )
    ensure_schema(connection)
    ensure_relationship_schema(connection)
    ensure_corpus_schema(connection)
    connection.executescript(
        """
        INSERT INTO opening_source_manifest
            (manifest_hash, source_dataset, file_count, record_count, created_at)
        VALUES ('manifest-s3-contract', 'test', 5, 2, 'now');
        INSERT INTO opening_source_file
            (manifest_hash, source_file, source_file_hash, record_count)
        VALUES
            ('manifest-s3-contract', 'a.tsv', 'file-a', 1),
            ('manifest-s3-contract', 'b.tsv', 'file-b', 1);
        INSERT INTO opening_catalog
            (manifest_hash, source_file, source_row_ordinal, source_row_hash, eco, name,
             move_sequence, endpoint_fen, endpoint_placement, endpoint_side_to_move,
             endpoint_castling, endpoint_en_passant, endpoint_halfmove_clock,
             endpoint_fullmove_number)
        VALUES
            ('manifest-s3-contract', 'a.tsv', 1, 'row-a', 'A00', 'First', '1. a4',
             '8/8/8/8/8/8/8/K6k w - - 0 1', '8/8/8/8/8/8/8/K6k', 'w', '-', '-', 0, 1),
            ('manifest-s3-contract', 'b.tsv', 1, 'row-b', 'A00', 'Second', '1. a4',
             '8/8/8/8/8/8/8/K6k w - - 0 1', '8/8/8/8/8/8/8/K6k', 'w', '-', '-', 0, 1);
        INSERT INTO opening_catalog_state
            (id, accepted_manifest_hash, accepted_schema_version, accepted_at, record_count)
        VALUES (1, 'manifest-s3-contract', 1, 'now', 2);
        INSERT INTO opening_relationship_state
            (accepted_manifest_hash, accepted_schema_version, record_count, position_count,
             membership_count, parent_link_count, transposition_link_count)
        VALUES ('manifest-s3-contract', 1, 2, 1, 2, 0, 0);
        INSERT INTO opening_relationship_position
            (manifest_hash, placement, side_to_move, castling, en_passant)
        VALUES ('manifest-s3-contract', '8/8/8/8/8/8/8/K6k', 'w', '-', '-');
        INSERT INTO opening_position_membership
            (manifest_hash, source_file, source_row_ordinal, ply, placement, side_to_move,
             castling, en_passant, uci, san, uci_prefix)
        VALUES
            ('manifest-s3-contract', 'a.tsv', 1, 1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-',
             'a2a4', 'a4', 'a2a4'),
            ('manifest-s3-contract', 'b.tsv', 1, 1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-',
             'a2a4', 'a4', 'a2a4');
        INSERT INTO corpus (corpus_id, subject_player_uuid) VALUES (1, 'subject');
        INSERT INTO corpus_game (corpus_id, game_uuid, rules, fingerprint)
        VALUES (1, 'game-1', 'chess', 'game-fingerprint');
        INSERT INTO position_state
            (state_id, placement, side_to_move, castling, en_passant)
        VALUES
            (1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-'),
            (2, '8/8/8/8/8/8/8/k6K1', 'b', '-', '-');
        INSERT INTO position_occurrence
            (game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number)
        VALUES
            ('game-1', 1, 1, 'a4', 'a2a4', 0, 1),
            ('game-1', 2, 2, 'Kh1', 'g1h1', 1, 1);
        """
    )


def write_rich_source(path: Path) -> Path:
    path.mkdir()
    for source_file, (eco, name, move_sequence) in RICH_SOURCE_ROWS.items():
        with (path / source_file).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerow(("eco", "name", "pgn"))
            writer.writerow((eco, name, move_sequence))
    return path


def seed_rich_fixture(
    connection: sqlite3.Connection, source: Path, subject_uuid: str = "subject"
) -> int:
    connection.executescript(
        """
        CREATE TABLE players (uuid TEXT PRIMARY KEY, username TEXT NOT NULL, profile_url TEXT);
        CREATE TABLE games (uuid TEXT PRIMARY KEY, url TEXT NOT NULL, pgn TEXT NOT NULL,
            time_control TEXT NOT NULL, end_time INTEGER NOT NULL, rated INTEGER, tcn TEXT,
            initial_setup TEXT, fen TEXT, time_class TEXT, rules TEXT, eco TEXT,
            white_player_uuid TEXT NOT NULL, black_player_uuid TEXT NOT NULL,
            FOREIGN KEY (white_player_uuid) REFERENCES players(uuid),
            FOREIGN KEY (black_player_uuid) REFERENCES players(uuid));
        """
    )
    connection.executemany(
        "INSERT INTO players (uuid, username, profile_url) VALUES (?, ?, ?)",
        [(subject_uuid, subject_uuid, None), ("opponent", "opponent", None)],
    )
    ensure_schema(connection)
    ensure_relationship_schema(connection)
    ensure_corpus_schema(connection)
    corpus_id = connection.execute(
        "INSERT INTO corpus (subject_player_uuid) VALUES (?)", (subject_uuid,)
    ).lastrowid
    connection.executemany(
        "INSERT INTO games (uuid, url, pgn, time_control, end_time, time_class, rules, "
        "white_player_uuid, black_player_uuid) VALUES (?, ?, ?, '600', 0, 'rapid', 'chess', ?, ?)",
        [
            (game_uuid, f"https://example.test/{game_uuid}", pgn, subject_uuid, "opponent")
            for game_uuid, pgn in RICH_GAME_PGNS.items()
        ],
    )
    connection.commit()
    assert corpus_id is not None
    extract_corpus.persist_fixture(connection, int(corpus_id), RICH_GAME_PGNS)
    import_catalog(connection, source)
    import_relationships(connection, source)
    return int(corpus_id)


def boundary_signature(connection: sqlite3.Connection) -> tuple[object, ...]:
    return (
        connection.execute(
            "SELECT * FROM opening_catalog ORDER BY source_file, source_row_ordinal"
        ).fetchall(),
        connection.execute(
            "SELECT * FROM opening_position_membership "
            "ORDER BY source_file, source_row_ordinal, ply"
        ).fetchall(),
        connection.execute("SELECT * FROM corpus_game ORDER BY corpus_id, game_uuid").fetchall(),
        connection.execute("SELECT * FROM position_state ORDER BY state_id").fetchall(),
        connection.execute("SELECT * FROM position_occurrence ORDER BY game_uuid, ply").fetchall(),
    )


def test_contract_schema_is_additive_and_preserves_natural_identities(tmp_path: Path) -> None:
    db_path = tmp_path / "classification-contract.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        before_positions = connection.execute(
            "SELECT * FROM position_state ORDER BY state_id"
        ).fetchall()
        before_occurrences = connection.execute(
            "SELECT * FROM position_occurrence ORDER BY game_uuid, ply"
        ).fetchall()
        before_catalog = connection.execute(
            "SELECT * FROM opening_catalog ORDER BY source_file, source_row_ordinal"
        ).fetchall()
        before_memberships = connection.execute(
            "SELECT * FROM opening_position_membership "
            "ORDER BY source_file, source_row_ordinal, ply"
        ).fetchall()

        ensure_classification_schema(connection)

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name LIKE 'opening_classification_%'"
            )
        }
        assert tables == {
            "opening_classification_schema",
            "opening_classification_state",
            "opening_classification_run",
            "opening_classification_game",
            "opening_classification_anchor",
            "opening_classification_route",
        }
        assert connection.execute(
            "SELECT version FROM opening_classification_schema WHERE id = 1"
        ).fetchone() == (CLASSIFICATION_SCHEMA_VERSION,)
        assert connection.execute("SELECT * FROM position_state ORDER BY state_id").fetchall() == (
            before_positions
        )
        assert (
            connection.execute(
                "SELECT * FROM position_occurrence ORDER BY game_uuid, ply"
            ).fetchall()
            == before_occurrences
        )
        assert (
            connection.execute(
                "SELECT * FROM opening_catalog ORDER BY source_file, source_row_ordinal"
            ).fetchall()
            == before_catalog
        )
        assert (
            connection.execute(
                "SELECT * FROM opening_position_membership "
                "ORDER BY source_file, source_row_ordinal, ply"
            ).fetchall()
            == before_memberships
        )

        for table in tables:
            columns = {
                row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            assert not columns & {"player_id", "player_uuid", "username", "rowid"}
            sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE name = ?", (table,)
            ).fetchone()[0]
            assert "WITHOUT ROWID" in sql

        anchor_pk = [
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(opening_classification_anchor)"
            ).fetchall()
            if row[5]
        ]
        assert anchor_pk == [
            "manifest_hash",
            "corpus_id",
            "game_uuid",
            "anchor_ply",
            "source_file",
            "source_row_ordinal",
        ]


def test_contract_retains_each_membership_and_inclusive_route_suffix(tmp_path: Path) -> None:
    db_path = tmp_path / "classification-facts.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        ensure_classification_schema(connection)
        connection.execute(
            "INSERT INTO opening_classification_game "
            "(manifest_hash, corpus_id, game_uuid, source_fingerprint) VALUES (?, ?, ?, ?)",
            (MANIFEST, 1, "game-1", "game-fingerprint"),
        )
        for source_file in ("a.tsv", "b.tsv"):
            connection.execute(
                "INSERT INTO opening_classification_anchor "
                "(manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
                "source_row_ordinal, anchor_placement, anchor_side_to_move, "
                "anchor_castling, anchor_en_passant, anchor_san, anchor_uci) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (MANIFEST, 1, "game-1", 1, source_file, 1, *POSITION_KEY, "a4", "a2a4"),
            )
            for route_ply, route_key, san, uci, halfmove, fullmove in (
                (1, POSITION_KEY, "a4", "a2a4", 0, 1),
                (2, ROUTE_KEY, "Kh1", "g1h1", 1, 1),
            ):
                connection.execute(
                    "INSERT INTO opening_classification_route "
                    "(manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
                    "source_row_ordinal, route_ply, route_placement, route_side_to_move, "
                    "route_castling, route_en_passant, route_san, route_uci, "
                    "route_halfmove_clock, route_fullmove_number) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        MANIFEST,
                        1,
                        "game-1",
                        1,
                        source_file,
                        1,
                        route_ply,
                        *route_key,
                        san,
                        uci,
                        halfmove,
                        fullmove,
                    ),
                )

        assert connection.execute(
            "SELECT source_file, source_row_ordinal, anchor_ply "
            "FROM opening_classification_anchor ORDER BY source_file"
        ).fetchall() == [("a.tsv", 1, 1), ("b.tsv", 1, 1)]
        assert connection.execute(
            "SELECT COUNT(*) FROM opening_classification_route"
        ).fetchone() == (4,)
        assert exact_endpoint_match(POSITION_KEY, POSITION_KEY)
        assert not exact_endpoint_match(POSITION_KEY, ROUTE_KEY)
        assert suffix_plies(1, 2) == (1, 2)
        validate_route_plies(1, 2, (1, 2))
        with pytest.raises(ValueError, match="expected suffix"):
            validate_route_plies(1, 2, (2,))
        assert AnchorIdentity((MANIFEST, "a.tsv", 1), (1, "game-1", 1)) != AnchorIdentity(
            (MANIFEST, "b.tsv", 1), (1, "game-1", 1)
        )


def test_contract_schema_refuses_incompatible_version_without_additive_tables(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "classification-version.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        connection.execute(
            "CREATE TABLE opening_classification_schema ("
            "id INTEGER PRIMARY KEY CHECK (id = 1), version INTEGER NOT NULL) WITHOUT ROWID"
        )
        connection.execute("INSERT INTO opening_classification_schema VALUES (1, 99)")
        connection.commit()

        with pytest.raises(OpeningSchemaError, match="classification schema version 99"):
            ensure_classification_schema(connection)

        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'opening_classification_anchor'"
            ).fetchone()
            is None
        )


def classification_rows(connection: sqlite3.Connection) -> dict[str, list[tuple[object, ...]]]:
    return {
        "state": connection.execute(
            "SELECT accepted_manifest_hash, corpus_id, accepted_schema_version, "
            "accepted_catalog_schema_version, accepted_relationship_schema_version "
            "FROM opening_classification_state"
        ).fetchall(),
        "run": connection.execute(
            "SELECT run_id, manifest_hash, corpus_id, schema_version, catalog_schema_version, "
            "relationship_schema_version, status, details FROM opening_classification_run"
        ).fetchall(),
        "games": connection.execute(
            "SELECT manifest_hash, corpus_id, game_uuid, source_fingerprint "
            "FROM opening_classification_game ORDER BY game_uuid"
        ).fetchall(),
        "anchors": connection.execute(
            "SELECT manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
            "source_row_ordinal, anchor_placement, anchor_side_to_move, anchor_castling, "
            "anchor_en_passant, anchor_san, anchor_uci FROM opening_classification_anchor "
            "ORDER BY game_uuid, anchor_ply, source_file, source_row_ordinal"
        ).fetchall(),
        "routes": connection.execute(
            "SELECT manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
            "source_row_ordinal, route_ply, route_placement, route_side_to_move, route_castling, "
            "route_en_passant, route_san, route_uci, route_halfmove_clock, route_fullmove_number "
            "FROM opening_classification_route ORDER BY game_uuid, anchor_ply, source_file, "
            "source_row_ordinal, route_ply"
        ).fetchall(),
    }


def test_stage2_derives_all_memberships_and_inclusive_routes_deterministically(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "classification-publication.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        facts = derive_classification(connection)

        assert facts.manifest_hash == MANIFEST
        assert facts.corpus_id == 1
        assert (facts.game_count, facts.anchor_count, facts.route_count) == (1, 2, 4)
        assert [
            (item.game_uuid, item.anchor_ply, item.source_file, item.source_row_ordinal)
            for item in facts.anchors
        ] == [
            ("game-1", 1, "a.tsv", 1),
            ("game-1", 1, "b.tsv", 1),
        ]
        assert [item.route_ply for item in facts.routes] == [1, 2, 1, 2]
        assert all(item.route_ply >= item.anchor_ply for item in facts.routes)
        assert all(item.route_placement in {PLACEMENT, ROUTE_PLACEMENT} for item in facts.routes)

        result = import_classification(connection)
        assert result.status == "success"
        assert (result.game_count, result.anchor_count, result.route_count) == (1, 2, 4)
        first_rows = classification_rows(connection)
        assert first_rows["state"] == [(MANIFEST, 1, 1, 1, 1)]
        assert first_rows["games"] == [(MANIFEST, 1, "game-1", "game-fingerprint")]
        assert connection.execute(
            "SELECT COUNT(*) FROM opening_classification_anchor"
        ).fetchone() == (2,)
        assert connection.execute(
            "SELECT COUNT(*) FROM opening_classification_route"
        ).fetchone() == (4,)

        rerun = import_classification(connection)
        assert rerun.status == "unchanged"
        assert rerun.run_id == result.run_id
        assert classification_rows(connection) == first_rows


def test_stage2_preserves_s1_s2_and_corpus_rows_and_independent_facts_match(
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "first.db"
    second_path = tmp_path / "second.db"
    signatures: list[tuple[dict[str, list[tuple[object, ...]]], dict[str, object]]] = []
    for db_path in (first_path, second_path):
        with open_database(db_path) as connection:
            seed_contract_dependencies(connection)
            before = {
                "catalog": connection.execute("SELECT * FROM opening_catalog").fetchall(),
                "memberships": connection.execute(
                    "SELECT * FROM opening_position_membership"
                ).fetchall(),
                "positions": connection.execute("SELECT * FROM position_state").fetchall(),
                "occurrences": connection.execute("SELECT * FROM position_occurrence").fetchall(),
            }
            result = import_classification(connection)
            after = {
                "catalog": connection.execute("SELECT * FROM opening_catalog").fetchall(),
                "memberships": connection.execute(
                    "SELECT * FROM opening_position_membership"
                ).fetchall(),
                "positions": connection.execute("SELECT * FROM position_state").fetchall(),
                "occurrences": connection.execute("SELECT * FROM position_occurrence").fetchall(),
            }
            assert after == before
            signatures.append(
                (
                    classification_rows(connection),
                    {
                        "run_id": result.run_id,
                        "manifest_hash": result.manifest_hash,
                        "corpus_id": result.corpus_id,
                        "counts": (result.game_count, result.anchor_count, result.route_count),
                    },
                )
            )

    assert signatures[0][0] == signatures[1][0]
    assert signatures[0][1] == signatures[1][1]


def test_stage2_derivation_failure_leaves_no_classification_state_or_facts(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "classification-derivation-failure.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        connection.execute("DELETE FROM position_occurrence WHERE game_uuid = 'game-1' AND ply = 2")
        connection.execute(
            "INSERT INTO position_occurrence "
            "(game_uuid, ply, state_id, san, uci, halfmove_clock, fullmove_number) "
            "VALUES ('game-1', 3, 2, 'Kh1', 'g1h1', 1, 1)"
        )
        connection.commit()

        with pytest.raises(ClassificationError, match="incomplete ordered occurrences"):
            import_classification(connection)

        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'opening_classification_run'"
            ).fetchone()
            is None
        )


def test_stage2_storage_failure_rolls_back_every_classification_fact(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "classification-storage-failure.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        ensure_classification_schema(connection)
        connection.execute(
            """
            CREATE TRIGGER fail_classification_anchor
            BEFORE INSERT ON opening_classification_anchor
            BEGIN
                SELECT RAISE(ABORT, 'forced classification failure');
            END
            """
        )
        connection.commit()

        with pytest.raises(sqlite3.IntegrityError, match="forced classification failure"):
            import_classification(connection)

        for table in (
            "opening_classification_state",
            "opening_classification_run",
            "opening_classification_game",
            "opening_classification_anchor",
            "opening_classification_route",
        ):
            assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone() == (0,)


def test_stage2_refuses_incompatible_version_without_classification_publication(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "classification-version-refusal.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        connection.execute(
            "CREATE TABLE opening_classification_schema ("
            "id INTEGER PRIMARY KEY CHECK (id = 1), version INTEGER NOT NULL) WITHOUT ROWID"
        )
        connection.execute("INSERT INTO opening_classification_schema VALUES (1, 99)")
        connection.commit()

        with pytest.raises(OpeningSchemaError, match="classification schema version 99"):
            import_classification(connection)

        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'opening_classification_anchor'"
            ).fetchone()
            is None
        )


def test_stage2_refuses_manifest_mismatch_without_classification_publication(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "classification-manifest-refusal.db"
    with open_database(db_path) as connection:
        seed_contract_dependencies(connection)
        connection.execute(
            "INSERT INTO opening_source_manifest "
            "(manifest_hash, source_dataset, file_count, record_count, created_at) "
            "VALUES ('different-manifest', 'test', 5, 2, 'now')"
        )
        connection.execute(
            "UPDATE opening_relationship_state SET accepted_manifest_hash = 'different-manifest' "
            "WHERE accepted_manifest_hash = ?",
            (MANIFEST,),
        )
        connection.commit()

        with pytest.raises(ClassificationError, match="relationship state"):
            import_classification(connection)

        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'opening_classification_run'"
            ).fetchone()
            is None
        )


def test_stage3_rich_fixture_covers_routes_memberships_and_neutral_determinism(
    tmp_path: Path,
) -> None:
    expected_anchors = [
        ("game-1", 1, "d.tsv", 1),
        ("game-1", 5, "a.tsv", 1),
        ("game-1", 5, "b.tsv", 1),
        ("game-2", 4, "c.tsv", 1),
        ("game-2", 8, "c.tsv", 1),
        ("game-2", 9, "d.tsv", 1),
        ("game-3", 1, "d.tsv", 1),
        ("game-3", 5, "e.tsv", 1),
    ]
    route_specs = (
        ("game-1", 1, "d.tsv", range(1, 7)),
        ("game-1", 5, "a.tsv", (5, 6)),
        ("game-1", 5, "b.tsv", (5, 6)),
        ("game-2", 4, "c.tsv", range(4, 10)),
        ("game-2", 8, "c.tsv", (8, 9)),
        ("game-2", 9, "d.tsv", (9,)),
        ("game-3", 1, "d.tsv", range(1, 6)),
        ("game-3", 5, "e.tsv", (5,)),
    )
    expected_routes = [
        (game_uuid, anchor_ply, source_file, 1, route_ply)
        for game_uuid, anchor_ply, source_file, plies in route_specs
        for route_ply in plies
    ]
    signatures = []
    for subject_uuid in ("subject-a", "subject-b"):
        db_path = tmp_path / f"{subject_uuid}.db"
        source = write_rich_source(tmp_path / f"{subject_uuid}-source")
        with open_database(db_path) as connection:
            seed_rich_fixture(connection, source, subject_uuid)
            before = boundary_signature(connection)
            facts = derive_classification(connection)

            assert facts.anchor_count == 8
            assert facts.route_count == 25
            assert {item.game_uuid for item in facts.games} == set(RICH_GAME_PGNS)
            assert [
                (item.game_uuid, item.anchor_ply, item.source_file, item.source_row_ordinal)
                for item in facts.anchors
            ] == expected_anchors
            assert [
                (
                    item.game_uuid,
                    item.anchor_ply,
                    item.source_file,
                    item.source_row_ordinal,
                    item.route_ply,
                )
                for item in facts.routes
            ] == expected_routes

            final_plies = dict(
                connection.execute(
                    "SELECT game_uuid, MAX(ply) FROM position_occurrence GROUP BY game_uuid"
                ).fetchall()
            )
            assert final_plies == {"game-1": 6, "game-2": 9, "game-3": 5}
            assert all(
                any(
                    route.game_uuid == game_uuid and route.route_ply == final_ply
                    for route in facts.routes
                )
                for game_uuid, final_ply in final_plies.items()
            )
            assert [
                route.route_ply
                for route in facts.routes
                if route.game_uuid == "game-2" and route.source_file == "d.tsv"
            ] == [9]
            assert [
                route.route_ply
                for route in facts.routes
                if route.game_uuid == "game-3" and route.source_file == "e.tsv"
            ] == [5]
            assert connection.execute(
                "SELECT source_file, name FROM opening_catalog ORDER BY source_file"
            ).fetchall() == [
                (source_file, values[1]) for source_file, values in RICH_SOURCE_ROWS.items()
            ]
            transpositions = set(
                connection.execute(
                    "SELECT source_file_a, source_file_b FROM opening_transposition_link"
                ).fetchall()
            )
            assert {("a.tsv", "b.tsv"), ("d.tsv", "e.tsv")} <= transpositions

            result = import_classification(connection)
            assert (result.game_count, result.anchor_count, result.route_count) == (3, 8, 25)
            rows = classification_rows(connection)
            assert boundary_signature(connection) == before

            rerun = import_classification(connection)
            assert rerun.status == "unchanged"
            assert classification_rows(connection) == rows
            signatures.append(rows)

    assert signatures[0] == signatures[1]
