from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from scripts.opening_catalog import (
    EXPECTED_SOURCE_FILES,
    derive_relationships,
    import_catalog,
    import_relationships,
    load_source,
)

FIXTURE_ROWS = {
    "a.tsv": (
        ("A00", "Broad Base", "1. e4"),
        ("A01", "Named Branch", "1. e4 e5 2. Nf3"),
        ("A02", "Deep Branch", "1. e4 e5 2. Nf3 Nc6 3. Bb5"),
        ("A03", "", "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"),
    ),
    "b.tsv": (("B00", "Knight Order One", "1. Nf3 Nf6 2. Nc3 Nc6"),),
    "c.tsv": (("C00", "Knight Order Two", "1. Nc3 Nc6 2. Nf3 Nf6"),),
    "d.tsv": (("D00", "Knight Order Duplicate", "1. Nf3 Nf6 2. Nc3 Nc6"),),
    "e.tsv": (("E00", "Named Branch Tie", "1. e4 e5 2. Nf3"),),
}

A_E4 = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
    "b",
    "KQkq",
    "e3",
)
A_E5 = (
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR",
    "w",
    "KQkq",
    "e6",
)
A_NF3 = (
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R",
    "b",
    "KQkq",
    "-",
)
A_NC6 = (
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R",
    "w",
    "KQkq",
    "-",
)
A_BB5 = (
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R",
    "b",
    "KQkq",
    "-",
)
A_A6 = (
    "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R",
    "w",
    "KQkq",
    "-",
)
T_FINAL = (
    "r1bqkb1r/pppppppp/2n2n2/8/8/2N2N2/PPPPPPPP/R1BQKB1R",
    "w",
    "KQkq",
    "-",
)


def write_fixture_source(path: Path) -> Path:
    path.mkdir()
    for source_file in EXPECTED_SOURCE_FILES:
        with (path / source_file).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
            writer.writerow(("eco", "name", "pgn"))
            writer.writerows(FIXTURE_ROWS[source_file])
    return path


def open_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def expected_paths() -> tuple[
    tuple[str, int, tuple[tuple[tuple[str, str, str, str], str, str], ...]], ...
]:
    return (
        ("a.tsv", 1, ((A_E4, "e2e4", "e4"),)),
        (
            "a.tsv",
            2,
            ((A_E4, "e2e4", "e4"), (A_E5, "e7e5", "e5"), (A_NF3, "g1f3", "Nf3")),
        ),
        (
            "a.tsv",
            3,
            (
                (A_E4, "e2e4", "e4"),
                (A_E5, "e7e5", "e5"),
                (A_NF3, "g1f3", "Nf3"),
                (A_NC6, "b8c6", "Nc6"),
                (A_BB5, "f1b5", "Bb5"),
            ),
        ),
        (
            "a.tsv",
            4,
            (
                (A_E4, "e2e4", "e4"),
                (A_E5, "e7e5", "e5"),
                (A_NF3, "g1f3", "Nf3"),
                (A_NC6, "b8c6", "Nc6"),
                (A_BB5, "f1b5", "Bb5"),
                (A_A6, "a7a6", "a6"),
            ),
        ),
        (
            "b.tsv",
            1,
            (
                (
                    ("rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R", "b", "KQkq", "-"),
                    "g1f3",
                    "Nf3",
                ),
                (
                    ("rnbqkb1r/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKB1R", "w", "KQkq", "-"),
                    "g8f6",
                    "Nf6",
                ),
                (
                    ("rnbqkb1r/pppppppp/5n2/8/8/2N2N2/PPPPPPPP/R1BQKB1R", "b", "KQkq", "-"),
                    "b1c3",
                    "Nc3",
                ),
                (T_FINAL, "b8c6", "Nc6"),
            ),
        ),
        (
            "c.tsv",
            1,
            (
                (
                    ("rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR", "b", "KQkq", "-"),
                    "b1c3",
                    "Nc3",
                ),
                (
                    ("r1bqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/R1BQKBNR", "w", "KQkq", "-"),
                    "b8c6",
                    "Nc6",
                ),
                (
                    ("r1bqkbnr/pppppppp/2n5/8/8/2N2N2/PPPPPPPP/R1BQKB1R", "b", "KQkq", "-"),
                    "g1f3",
                    "Nf3",
                ),
                (T_FINAL, "g8f6", "Nf6"),
            ),
        ),
        (
            "d.tsv",
            1,
            (
                (
                    ("rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R", "b", "KQkq", "-"),
                    "g1f3",
                    "Nf3",
                ),
                (
                    ("rnbqkb1r/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKB1R", "w", "KQkq", "-"),
                    "g8f6",
                    "Nf6",
                ),
                (
                    ("rnbqkb1r/pppppppp/5n2/8/8/2N2N2/PPPPPPPP/R1BQKB1R", "b", "KQkq", "-"),
                    "b1c3",
                    "Nc3",
                ),
                (T_FINAL, "b8c6", "Nc6"),
            ),
        ),
        (
            "e.tsv",
            1,
            ((A_E4, "e2e4", "e4"), (A_E5, "e7e5", "e5"), (A_NF3, "g1f3", "Nf3")),
        ),
    )


def expected_memberships() -> tuple[tuple[object, ...], ...]:
    rows: list[tuple[object, ...]] = []
    for source_file, source_row, path in expected_paths():
        prefix: list[str] = []
        for ply, (key, uci, san) in enumerate(path, start=1):
            prefix.append(uci)
            rows.append((source_file, source_row, ply, *key, uci, san, " ".join(prefix)))
    return tuple(rows)


EXPECTED_POSITIONS = tuple(sorted({row[3:7] for row in expected_memberships()}))
EXPECTED_PARENTS = (
    ("a.tsv", 2, 1, "a.tsv", 1),
    ("a.tsv", 3, 3, "a.tsv", 2),
    ("a.tsv", 3, 3, "e.tsv", 1),
    ("a.tsv", 4, 5, "a.tsv", 3),
    ("e.tsv", 1, 1, "a.tsv", 1),
)
EXPECTED_TRANSPOSITIONS = (
    (
        T_FINAL,
        "b.tsv",
        1,
        4,
        "g1f3 g8f6 b1c3 b8c6",
        "c.tsv",
        1,
        4,
        "b1c3 b8c6 g1f3 g8f6",
    ),
    (
        T_FINAL,
        "c.tsv",
        1,
        4,
        "b1c3 b8c6 g1f3 g8f6",
        "d.tsv",
        1,
        4,
        "g1f3 g8f6 b1c3 b8c6",
    ),
)


def persisted_facts(connection: sqlite3.Connection) -> dict[str, list[tuple[object, ...]]]:
    return {
        "positions": connection.execute(
            "SELECT placement, side_to_move, castling, en_passant "
            "FROM opening_relationship_position "
            "ORDER BY placement, side_to_move, castling, en_passant"
        ).fetchall(),
        "memberships": connection.execute(
            "SELECT source_file, source_row_ordinal, ply, placement, side_to_move, castling, "
            "en_passant, uci, san, uci_prefix FROM opening_position_membership "
            "ORDER BY source_file, source_row_ordinal, ply"
        ).fetchall(),
        "parents": connection.execute(
            "SELECT child_source_file, child_source_row_ordinal, child_ply, "
            "parent_source_file, parent_source_row_ordinal FROM opening_parent_link "
            "ORDER BY child_source_file, child_source_row_ordinal, child_ply, "
            "parent_source_file, parent_source_row_ordinal"
        ).fetchall(),
        "transpositions": connection.execute(
            "SELECT placement, side_to_move, castling, en_passant, source_file_a, "
            "source_row_ordinal_a, ply_a, uci_prefix_a, source_file_b, "
            "source_row_ordinal_b, ply_b, uci_prefix_b FROM opening_transposition_link "
            "ORDER BY placement, side_to_move, castling, en_passant, source_file_a, "
            "source_row_ordinal_a, ply_a, source_file_b, source_row_ordinal_b, ply_b"
        ).fetchall(),
    }


def test_relationship_fixture_pins_replay_semantics_and_complete_deterministic_facts(
    tmp_path: Path,
) -> None:
    source = write_fixture_source(tmp_path / "source")
    manifest = load_source(source)
    facts = derive_relationships(manifest)

    assert facts.record_count == 8
    assert facts.position_count == 13
    assert facts.membership_count == 30
    assert facts.parent_link_count == 5
    assert facts.transposition_link_count == 2
    assert facts.positions == EXPECTED_POSITIONS
    assert (
        tuple(
            (
                item.source_file,
                item.source_row_ordinal,
                item.ply,
                *item.key,
                item.uci,
                item.san,
                item.uci_prefix,
            )
            for item in facts.memberships
        )
        == expected_memberships()
    )
    assert (
        tuple(
            (
                item.child_source_file,
                item.child_source_row_ordinal,
                item.child_ply,
                item.parent_source_file,
                item.parent_source_row_ordinal,
            )
            for item in facts.parents
        )
        == EXPECTED_PARENTS
    )
    assert (
        tuple(
            (
                item.key,
                item.source_file_a,
                item.source_row_ordinal_a,
                item.ply_a,
                item.uci_prefix_a,
                item.source_file_b,
                item.source_row_ordinal_b,
                item.ply_b,
                item.uci_prefix_b,
            )
            for item in facts.transpositions
        )
        == EXPECTED_TRANSPOSITIONS
    )

    # The shorter broad path, nested endpoints, deepest parent chain, and tied parents are explicit.
    assert EXPECTED_PARENTS == (
        ("a.tsv", 2, 1, "a.tsv", 1),
        ("a.tsv", 3, 3, "a.tsv", 2),
        ("a.tsv", 3, 3, "e.tsv", 1),
        ("a.tsv", 4, 5, "a.tsv", 3),
        ("e.tsv", 1, 1, "a.tsv", 1),
    )
    assert ("a.tsv", 4, 6, *A_A6, "a7a6", "a6", "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6") in (
        *expected_memberships(),
    )

    # Three records share the exact endpoint and all four records retain the Nf3 membership.
    assert [
        (item.source_file, item.source_row_ordinal, item.ply)
        for item in facts.memberships
        if item.key == A_NF3
    ] == [("a.tsv", 2, 3), ("a.tsv", 3, 3), ("a.tsv", 4, 3), ("e.tsv", 1, 3)]
    assert [
        (item.source_file_a, item.source_file_b, item.uci_prefix_a, item.uci_prefix_b)
        for item in facts.transpositions
    ] == [
        ("b.tsv", "c.tsv", "g1f3 g8f6 b1c3 b8c6", "b1c3 b8c6 g1f3 g8f6"),
        ("c.tsv", "d.tsv", "b1c3 b8c6 g1f3 g8f6", "g1f3 g8f6 b1c3 b8c6"),
    ]

    db_path = tmp_path / "relationships.db"
    with open_database(db_path) as connection:
        import_catalog(connection, source)
        s1_before = connection.execute(
            "SELECT manifest_hash, source_file, source_row_ordinal, source_row_hash, eco, name, "
            "move_sequence, endpoint_fen FROM opening_catalog "
            "ORDER BY source_file, source_row_ordinal"
        ).fetchall()

        result = import_relationships(connection, source)

        assert (
            result.record_count,
            result.position_count,
            result.membership_count,
            result.parent_link_count,
            result.transposition_link_count,
        ) == (8, 13, 30, 5, 2)
        persisted = persisted_facts(connection)
        assert persisted == {
            "positions": list(EXPECTED_POSITIONS),
            "memberships": list(expected_memberships()),
            "parents": list(EXPECTED_PARENTS),
            "transpositions": [(*item[0], *item[1:]) for item in EXPECTED_TRANSPOSITIONS],
        }
        assert connection.execute(
            "SELECT source_file, source_row_ordinal, name FROM opening_catalog "
            "WHERE source_file = 'a.tsv' AND source_row_ordinal = 4"
        ).fetchone() == ("a.tsv", 4, "")
        assert (
            connection.execute(
                "SELECT manifest_hash, source_file, source_row_ordinal, source_row_hash, "
                "eco, name, move_sequence, endpoint_fen FROM opening_catalog "
                "ORDER BY source_file, source_row_ordinal"
            ).fetchall()
            == s1_before
        )

        assert import_relationships(connection, source).status == "unchanged"
        assert persisted_facts(connection) == persisted
