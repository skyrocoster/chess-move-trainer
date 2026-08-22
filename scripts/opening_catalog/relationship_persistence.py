"""Atomic SQLite publication for replay-derived opening relationships."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from .importer import (
    OpeningCatalogError,
    OpeningRecord,
    OpeningSourceChangedError,
    SourceManifest,
    load_source,
)
from .relationships import (
    RelationshipFacts,
    RelationshipImportResult,
    derive_relationships,
)
from .schema import RELATIONSHIP_SCHEMA_VERSION, ensure_relationship_schema

DETAILS = "deterministic replay-derived relationship publication"


def _run_id(manifest_hash: str) -> str:
    value = f"opening-relationships:{RELATIONSHIP_SCHEMA_VERSION}:{manifest_hash}"
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _catalog_row(record: OpeningRecord, manifest_hash: str) -> tuple[object, ...]:
    return (
        manifest_hash,
        record.source_file,
        record.source_row_ordinal,
        record.source_row_hash,
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


def _catalog_matches(connection: sqlite3.Connection, manifest: SourceManifest) -> bool:
    actual = connection.execute(
        "SELECT manifest_hash, source_file, source_row_ordinal, source_row_hash, eco, name, "
        "move_sequence, endpoint_fen, endpoint_placement, endpoint_side_to_move, "
        "endpoint_castling, endpoint_en_passant, endpoint_halfmove_clock, "
        "endpoint_fullmove_number FROM opening_catalog WHERE manifest_hash = ? "
        "ORDER BY source_file, source_row_ordinal",
        (manifest.manifest_hash,),
    ).fetchall()
    expected = [
        _catalog_row(record, manifest.manifest_hash)
        for record in sorted(
            manifest.records, key=lambda item: (item.source_file, item.source_row_ordinal)
        )
    ]
    return actual == expected


def _accepted_manifest(connection: sqlite3.Connection) -> str | None:
    try:
        row = connection.execute(
            "SELECT accepted_manifest_hash FROM opening_catalog_state WHERE id = 1"
        ).fetchone()
    except sqlite3.OperationalError as error:
        raise OpeningCatalogError("an accepted S1 catalog is required") from error
    return str(row[0]) if row else None


def _state_row(facts: RelationshipFacts) -> tuple[object, ...]:
    return (
        facts.manifest_hash,
        RELATIONSHIP_SCHEMA_VERSION,
        facts.record_count,
        facts.position_count,
        facts.membership_count,
        facts.parent_link_count,
        facts.transposition_link_count,
    )


def _run_row(facts: RelationshipFacts) -> tuple[object, ...]:
    return (
        _run_id(facts.manifest_hash),
        facts.manifest_hash,
        RELATIONSHIP_SCHEMA_VERSION,
        "success",
        facts.record_count,
        facts.position_count,
        facts.membership_count,
        facts.parent_link_count,
        facts.transposition_link_count,
        DETAILS,
    )


def _relationship_matches(connection: sqlite3.Connection, facts: RelationshipFacts) -> bool:
    state = connection.execute(
        "SELECT accepted_manifest_hash, accepted_schema_version, record_count, position_count, "
        "membership_count, parent_link_count, transposition_link_count "
        "FROM opening_relationship_state WHERE accepted_manifest_hash = ?",
        (facts.manifest_hash,),
    ).fetchone()
    run = connection.execute(
        "SELECT run_id, manifest_hash, schema_version, status, record_count, position_count, "
        "membership_count, parent_link_count, transposition_link_count, details "
        "FROM opening_relationship_run WHERE manifest_hash = ?",
        (facts.manifest_hash,),
    ).fetchone()
    if state != _state_row(facts) or run != _run_row(facts):
        return False

    expected_positions = [(facts.manifest_hash, *key) for key in facts.positions]
    actual_positions = connection.execute(
        "SELECT manifest_hash, placement, side_to_move, castling, en_passant "
        "FROM opening_relationship_position WHERE manifest_hash = ? "
        "ORDER BY placement, side_to_move, castling, en_passant",
        (facts.manifest_hash,),
    ).fetchall()
    if actual_positions != expected_positions:
        return False

    expected_memberships = [
        (
            facts.manifest_hash,
            item.source_file,
            item.source_row_ordinal,
            item.ply,
            *item.key,
            item.uci,
            item.san,
            item.uci_prefix,
        )
        for item in facts.memberships
    ]
    actual_memberships = connection.execute(
        "SELECT manifest_hash, source_file, source_row_ordinal, ply, placement, side_to_move, "
        "castling, en_passant, uci, san, uci_prefix FROM opening_position_membership "
        "WHERE manifest_hash = ? ORDER BY source_file, source_row_ordinal, ply",
        (facts.manifest_hash,),
    ).fetchall()
    if actual_memberships != expected_memberships:
        return False

    expected_parents = [
        (
            facts.manifest_hash,
            item.child_source_file,
            item.child_source_row_ordinal,
            item.child_ply,
            item.parent_source_file,
            item.parent_source_row_ordinal,
        )
        for item in facts.parents
    ]
    actual_parents = connection.execute(
        "SELECT manifest_hash, child_source_file, child_source_row_ordinal, child_ply, "
        "parent_source_file, parent_source_row_ordinal FROM opening_parent_link "
        "WHERE manifest_hash = ? ORDER BY child_source_file, child_source_row_ordinal, child_ply, "
        "parent_source_file, parent_source_row_ordinal",
        (facts.manifest_hash,),
    ).fetchall()
    if actual_parents != expected_parents:
        return False

    expected_transpositions = [
        (
            facts.manifest_hash,
            *item.key,
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
    ]
    actual_transpositions = connection.execute(
        "SELECT manifest_hash, placement, side_to_move, castling, en_passant, source_file_a, "
        "source_row_ordinal_a, ply_a, uci_prefix_a, source_file_b, source_row_ordinal_b, "
        "ply_b, uci_prefix_b FROM opening_transposition_link WHERE manifest_hash = ? "
        "ORDER BY placement, side_to_move, castling, en_passant, source_file_a, "
        "source_row_ordinal_a, ply_a, source_file_b, source_row_ordinal_b, ply_b",
        (facts.manifest_hash,),
    ).fetchall()
    return actual_transpositions == expected_transpositions


def publish_relationships(
    connection: sqlite3.Connection, facts: RelationshipFacts
) -> RelationshipImportResult:
    """Atomically replace one manifest's relationship facts and publication state."""

    connection.execute("PRAGMA foreign_keys = ON")
    accepted = _accepted_manifest(connection)
    if accepted is None:
        raise OpeningCatalogError("an accepted S1 catalog is required")
    if accepted != facts.manifest_hash:
        raise OpeningSourceChangedError(
            "relationship manifest does not match the accepted opening catalog manifest"
        )
    catalog_count = connection.execute(
        "SELECT COUNT(*) FROM opening_catalog WHERE manifest_hash = ?",
        (facts.manifest_hash,),
    ).fetchone()[0]
    if catalog_count != facts.record_count:
        raise OpeningCatalogError("accepted opening catalog does not match relationship facts")
    ensure_relationship_schema(connection)
    if _relationship_matches(connection, facts):
        return _result(facts, "unchanged")

    with connection:
        if _accepted_manifest(connection) != facts.manifest_hash:
            raise OpeningSourceChangedError(
                "accepted opening catalog manifest changed during relationship publication"
            )
        for table, column in (
            ("opening_transposition_link", "manifest_hash"),
            ("opening_parent_link", "manifest_hash"),
            ("opening_position_membership", "manifest_hash"),
            ("opening_relationship_position", "manifest_hash"),
            ("opening_relationship_state", "accepted_manifest_hash"),
            ("opening_relationship_run", "manifest_hash"),
        ):
            connection.execute(f"DELETE FROM {table} WHERE {column} = ?", (facts.manifest_hash,))
        connection.execute(
            "INSERT INTO opening_relationship_run ("
            "run_id, manifest_hash, schema_version, status, record_count, position_count, "
            "membership_count, parent_link_count, transposition_link_count, details) "
            "VALUES (?, ?, ?, 'running', ?, ?, ?, ?, ?, ?)",
            (
                _run_id(facts.manifest_hash),
                facts.manifest_hash,
                RELATIONSHIP_SCHEMA_VERSION,
                facts.record_count,
                facts.position_count,
                facts.membership_count,
                facts.parent_link_count,
                facts.transposition_link_count,
                DETAILS,
            ),
        )
        connection.executemany(
            "INSERT INTO opening_relationship_position ("
            "manifest_hash, placement, side_to_move, castling, en_passant) VALUES (?, ?, ?, ?, ?)",
            [(facts.manifest_hash, *key) for key in facts.positions],
        )
        connection.executemany(
            "INSERT INTO opening_position_membership ("
            "manifest_hash, source_file, source_row_ordinal, ply, placement, side_to_move, "
            "castling, en_passant, uci, san, uci_prefix) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    facts.manifest_hash,
                    item.source_file,
                    item.source_row_ordinal,
                    item.ply,
                    *item.key,
                    item.uci,
                    item.san,
                    item.uci_prefix,
                )
                for item in facts.memberships
            ],
        )
        connection.executemany(
            "INSERT INTO opening_parent_link ("
            "manifest_hash, child_source_file, child_source_row_ordinal, child_ply, "
            "parent_source_file, parent_source_row_ordinal) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    facts.manifest_hash,
                    item.child_source_file,
                    item.child_source_row_ordinal,
                    item.child_ply,
                    item.parent_source_file,
                    item.parent_source_row_ordinal,
                )
                for item in facts.parents
            ],
        )
        connection.executemany(
            "INSERT INTO opening_transposition_link ("
            "manifest_hash, placement, side_to_move, castling, en_passant, source_file_a, "
            "source_row_ordinal_a, ply_a, uci_prefix_a, source_file_b, source_row_ordinal_b, "
            "ply_b, uci_prefix_b) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    facts.manifest_hash,
                    *item.key,
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
            ],
        )
        connection.execute(
            "UPDATE opening_relationship_run SET status = 'success' WHERE run_id = ?",
            (_run_id(facts.manifest_hash),),
        )
        connection.execute(
            "INSERT INTO opening_relationship_state ("
            "accepted_manifest_hash, accepted_schema_version, record_count, position_count, "
            "membership_count, parent_link_count, transposition_link_count) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            _state_row(facts),
        )

    return _result(facts, "success")


def _result(facts: RelationshipFacts, status: str) -> RelationshipImportResult:
    return RelationshipImportResult(
        _run_id(facts.manifest_hash),
        facts.manifest_hash,
        status,
        facts.record_count,
        facts.position_count,
        facts.membership_count,
        facts.parent_link_count,
        facts.transposition_link_count,
    )


def import_relationships(
    connection: sqlite3.Connection, source_dir: Path
) -> RelationshipImportResult:
    """Derive relationships from the accepted source and publish them atomically."""

    manifest = load_source(source_dir)
    accepted = _accepted_manifest(connection)
    if accepted is None:
        raise OpeningCatalogError("an accepted S1 catalog is required")
    if accepted != manifest.manifest_hash:
        raise OpeningSourceChangedError(
            "source manifest changed; relationship publication requires the accepted source version"
        )
    if not _catalog_matches(connection, manifest):
        raise OpeningCatalogError("accepted opening catalog does not match its source manifest")
    return publish_relationships(connection, derive_relationships(manifest))
