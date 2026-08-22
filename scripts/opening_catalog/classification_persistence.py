"""Atomic temporary SQLite publication for neutral classification facts."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from .classification import (
    ClassificationError,
    ClassificationFacts,
    _accepted_context,
    derive_classification,
)
from .classification_schema import CLASSIFICATION_SCHEMA_VERSION, ensure_classification_schema

DETAILS = "deterministic neutral classification publication"


class ClassificationPublicationError(ClassificationError):
    """Classification facts cannot be published without violating the accepted boundary."""


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _run_id(facts: ClassificationFacts) -> str:
    value = (
        f"opening-classification:{facts.schema_version}:{facts.catalog_schema_version}:"
        f"{facts.relationship_schema_version}:{facts.manifest_hash}:{facts.corpus_id}"
    )
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _state_stable_row(facts: ClassificationFacts) -> tuple[object, ...]:
    return (
        facts.manifest_hash,
        facts.corpus_id,
        facts.schema_version,
        facts.catalog_schema_version,
        facts.relationship_schema_version,
    )


def _run_stable_row(facts: ClassificationFacts) -> tuple[object, ...]:
    return (
        _run_id(facts),
        facts.manifest_hash,
        facts.corpus_id,
        facts.schema_version,
        facts.catalog_schema_version,
        facts.relationship_schema_version,
        "success",
        DETAILS,
    )


def _game_rows(facts: ClassificationFacts) -> list[tuple[object, ...]]:
    return [
        (facts.manifest_hash, facts.corpus_id, item.game_uuid, item.source_fingerprint)
        for item in facts.games
    ]


def _anchor_rows(facts: ClassificationFacts) -> list[tuple[object, ...]]:
    return [
        (
            facts.manifest_hash,
            facts.corpus_id,
            item.game_uuid,
            item.anchor_ply,
            item.source_file,
            item.source_row_ordinal,
            item.anchor_placement,
            item.anchor_side_to_move,
            item.anchor_castling,
            item.anchor_en_passant,
            item.anchor_san,
            item.anchor_uci,
        )
        for item in facts.anchors
    ]


def _route_rows(facts: ClassificationFacts) -> list[tuple[object, ...]]:
    return [
        (
            facts.manifest_hash,
            facts.corpus_id,
            item.game_uuid,
            item.anchor_ply,
            item.source_file,
            item.source_row_ordinal,
            item.route_ply,
            item.route_placement,
            item.route_side_to_move,
            item.route_castling,
            item.route_en_passant,
            item.route_san,
            item.route_uci,
            item.route_halfmove_clock,
            item.route_fullmove_number,
        )
        for item in facts.routes
    ]


def _classification_matches(connection: sqlite3.Connection, facts: ClassificationFacts) -> bool:
    state = connection.execute(
        "SELECT accepted_manifest_hash, corpus_id, accepted_schema_version, "
        "accepted_catalog_schema_version, accepted_relationship_schema_version "
        "FROM opening_classification_state WHERE accepted_manifest_hash = ? AND corpus_id = ?",
        (facts.manifest_hash, facts.corpus_id),
    ).fetchone()
    run = connection.execute(
        "SELECT run_id, manifest_hash, corpus_id, schema_version, catalog_schema_version, "
        "relationship_schema_version, status, details FROM opening_classification_run "
        "WHERE manifest_hash = ? AND corpus_id = ?",
        (facts.manifest_hash, facts.corpus_id),
    ).fetchone()
    if state != _state_stable_row(facts) or run != _run_stable_row(facts):
        return False
    actual_games = connection.execute(
        "SELECT manifest_hash, corpus_id, game_uuid, source_fingerprint "
        "FROM opening_classification_game WHERE manifest_hash = ? AND corpus_id = ? "
        "ORDER BY game_uuid",
        (facts.manifest_hash, facts.corpus_id),
    ).fetchall()
    if actual_games != _game_rows(facts):
        return False
    actual_anchors = connection.execute(
        "SELECT manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
        "source_row_ordinal, anchor_placement, anchor_side_to_move, anchor_castling, "
        "anchor_en_passant, anchor_san, anchor_uci FROM opening_classification_anchor "
        "WHERE manifest_hash = ? AND corpus_id = ? ORDER BY game_uuid, anchor_ply, "
        "source_file, source_row_ordinal",
        (facts.manifest_hash, facts.corpus_id),
    ).fetchall()
    if actual_anchors != _anchor_rows(facts):
        return False
    actual_routes = connection.execute(
        "SELECT manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, "
        "source_row_ordinal, route_ply, route_placement, route_side_to_move, route_castling, "
        "route_en_passant, route_san, route_uci, route_halfmove_clock, route_fullmove_number "
        "FROM opening_classification_route WHERE manifest_hash = ? AND corpus_id = ? "
        "ORDER BY game_uuid, anchor_ply, source_file, source_row_ordinal, route_ply",
        (facts.manifest_hash, facts.corpus_id),
    ).fetchall()
    return actual_routes == _route_rows(facts)


def publish_classification(
    connection: sqlite3.Connection, facts: ClassificationFacts
) -> "ClassificationImportResult":
    """Publish one complete classification atomically, or leave the prior state intact."""

    connection.execute("PRAGMA foreign_keys = ON")
    if facts.schema_version != CLASSIFICATION_SCHEMA_VERSION:
        raise ClassificationPublicationError(
            "classification facts use an incompatible schema version"
        )
    context = _accepted_context(connection, facts.corpus_id)
    if context != (
        facts.manifest_hash,
        facts.corpus_id,
        facts.catalog_schema_version,
        facts.relationship_schema_version,
    ):
        raise ClassificationPublicationError("classification facts do not match accepted inputs")
    ensure_classification_schema(connection)
    if _classification_matches(connection, facts):
        return _result(facts, "unchanged")
    with connection:
        context = _accepted_context(connection, facts.corpus_id)
        if context != (
            facts.manifest_hash,
            facts.corpus_id,
            facts.catalog_schema_version,
            facts.relationship_schema_version,
        ):
            raise ClassificationPublicationError(
                "accepted inputs changed during classification publication"
            )
        if _classification_matches(connection, facts):
            return _result(facts, "unchanged")
        for table, column in (
            ("opening_classification_route", "manifest_hash"),
            ("opening_classification_anchor", "manifest_hash"),
            ("opening_classification_game", "manifest_hash"),
            ("opening_classification_state", "accepted_manifest_hash"),
            ("opening_classification_run", "manifest_hash"),
        ):
            connection.execute(
                f"DELETE FROM {table} WHERE {column} = ? AND corpus_id = ?",
                (facts.manifest_hash, facts.corpus_id),
            )
        connection.execute(
            "INSERT INTO opening_classification_run ("
            "run_id, manifest_hash, corpus_id, schema_version, catalog_schema_version, "
            "relationship_schema_version, status, started_at, details) "
            "VALUES (?, ?, ?, ?, ?, ?, 'running', ?, ?)",
            (
                _run_id(facts),
                facts.manifest_hash,
                facts.corpus_id,
                facts.schema_version,
                facts.catalog_schema_version,
                facts.relationship_schema_version,
                _timestamp(),
                DETAILS,
            ),
        )
        connection.executemany(
            "INSERT INTO opening_classification_game ("
            "manifest_hash, corpus_id, game_uuid, source_fingerprint) VALUES (?, ?, ?, ?)",
            _game_rows(facts),
        )
        connection.executemany(
            "INSERT INTO opening_classification_anchor ("
            "manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal, "
            "anchor_placement, anchor_side_to_move, anchor_castling, anchor_en_passant, "
            "anchor_san, anchor_uci) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            _anchor_rows(facts),
        )
        connection.executemany(
            "INSERT INTO opening_classification_route ("
            "manifest_hash, corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal, "
            "route_ply, route_placement, route_side_to_move, route_castling, route_en_passant, "
            "route_san, route_uci, route_halfmove_clock, route_fullmove_number) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            _route_rows(facts),
        )
        connection.execute(
            "UPDATE opening_classification_run SET status = 'success', finished_at = ? "
            "WHERE run_id = ?",
            (_timestamp(), _run_id(facts)),
        )
        connection.execute(
            "INSERT INTO opening_classification_state ("
            "accepted_manifest_hash, corpus_id, accepted_schema_version, "
            "accepted_catalog_schema_version, accepted_relationship_schema_version, accepted_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (*_state_stable_row(facts), _timestamp()),
        )
    return _result(facts, "success")


def _result(facts: ClassificationFacts, status: str) -> "ClassificationImportResult":
    return ClassificationImportResult(
        _run_id(facts),
        facts.manifest_hash,
        facts.corpus_id,
        status,
        facts.game_count,
        facts.anchor_count,
        facts.route_count,
    )


@dataclass(frozen=True)
class ClassificationImportResult:
    """Stable receipt for a classification derivation/publication."""

    run_id: str
    manifest_hash: str
    corpus_id: int
    status: str
    game_count: int
    anchor_count: int
    route_count: int

    @property
    def accepted_games(self) -> int:
        return self.game_count

    @property
    def anchors(self) -> int:
        return self.anchor_count

    @property
    def routes(self) -> int:
        return self.route_count


def import_classification(
    connection: sqlite3.Connection, corpus_id: int | None = None
) -> ClassificationImportResult:
    """Derive from accepted S1/S2/corpus rows and publish atomically."""

    return publish_classification(connection, derive_classification(connection, corpus_id))


derive_classifications = derive_classification
import_classifications = import_classification
publish_classifications = publish_classification
