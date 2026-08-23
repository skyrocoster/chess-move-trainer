"""Atomic temporary SQLite publication for authoritative S4 recurrence facts."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from .recurrence import (
    RecurrenceError,
    RecurrenceFacts,
    RecurrenceProjections,
    derive_recurrence,
    input_signatures,
    project_recurrence,
)
from .recurrence_schema import RECURRENCE_SCHEMA_VERSION, ensure_recurrence_schema

DETAILS = "deterministic neutral recurrence publication"


class RecurrencePublicationError(RecurrenceError):
    """Recurrence facts cannot be published without violating the accepted boundary."""


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _run_id(facts: RecurrenceFacts) -> str:
    value = json.dumps(
        (
            "opening-recurrence",
            facts.schema_version,
            facts.classification_schema_version,
            facts.catalog_schema_version,
            facts.relationship_schema_version,
            facts.corpus_schema_version,
            facts.manifest_hash,
            facts.corpus_id,
            facts.classification_input_signature,
            facts.corpus_input_signature,
            facts.game_metadata_input_signature,
        ),
        separators=(",", ":"),
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _game_rows(facts: RecurrenceFacts) -> list[tuple[object, ...]]:
    return [
        (
            item.manifest_hash,
            item.corpus_id,
            item.game_uuid,
            item.source_fingerprint,
            item.metadata_fingerprint,
            item.game_sequence,
            item.game_color,
            item.end_time,
            item.year,
            item.month,
            item.time_control,
            item.time_class,
            item.white_rating,
            item.black_rating,
            item.white_result,
            item.black_result,
        )
        for item in facts.games
    ]


def _occurrence_rows(facts: RecurrenceFacts) -> list[tuple[object, ...]]:
    return [
        (
            item.manifest_hash,
            item.corpus_id,
            item.game_uuid,
            item.ply,
            *item.key,
            item.san,
            item.uci,
            item.halfmove_clock,
            item.fullmove_number,
        )
        for item in facts.occurrences
    ]


def _route_rows(facts: RecurrenceFacts) -> list[tuple[object, ...]]:
    return [
        (
            item.manifest_hash,
            item.corpus_id,
            item.game_uuid,
            item.anchor_ply,
            item.catalog[1],
            item.catalog[2],
            item.route_ply,
            *item.key,
            item.san,
            item.uci,
            item.halfmove_clock,
            item.fullmove_number,
        )
        for item in facts.routes
    ]


def _branch_rows(facts: RecurrenceFacts) -> list[tuple[object, ...]]:
    return [
        (
            item.manifest_hash,
            item.corpus_id,
            item.game_uuid,
            item.parent_ply,
            *item.parent_key,
            item.branch_kind,
            item.child_ply,
            *(item.child_key or (None, None, None, None)),
            item.child_san,
            item.child_uci,
            item.terminal_outcome,
        )
        for item in facts.branches
    ]


def _state_row(facts: RecurrenceFacts) -> tuple[object, ...]:
    return (
        facts.manifest_hash,
        facts.corpus_id,
        facts.schema_version,
        facts.classification_schema_version,
        facts.catalog_schema_version,
        facts.relationship_schema_version,
        facts.corpus_schema_version,
        facts.classification_input_signature,
        facts.corpus_input_signature,
        facts.game_metadata_input_signature,
        facts.game_count,
        facts.occurrence_count,
        facts.route_event_count,
        facts.branch_event_count,
    )


def _projection_rows(projections: RecurrenceProjections) -> tuple[list[tuple[object, ...]], ...]:
    positions = [
        (
            item.manifest_hash,
            item.corpus_id,
            *item.key,
            item.color_scope,
            item.raw_occurrence_count,
            item.distinct_game_count,
            item.first_game_sequence,
            item.first_game_uuid,
            item.first_ply,
            item.last_game_sequence,
            item.last_game_uuid,
            item.last_ply,
        )
        for item in projections.positions
    ]
    routes = [
        (
            item.manifest_hash,
            item.corpus_id,
            item.anchor_ply,
            item.catalog[1],
            item.catalog[2],
            *item.key,
            item.color_scope,
            item.raw_occurrence_count,
            item.distinct_game_count,
            item.first_game_sequence,
            item.first_game_uuid,
            item.first_route_ply,
            item.last_game_sequence,
            item.last_game_uuid,
            item.last_route_ply,
        )
        for item in projections.routes
    ]
    branches = [
        (
            item.manifest_hash,
            item.corpus_id,
            *item.parent_key,
            item.branch_kind,
            item.child_uci,
            item.color_scope,
            item.raw_event_count,
            item.distinct_game_count,
            item.first_game_sequence,
            item.first_game_uuid,
            item.first_parent_ply,
            item.last_game_sequence,
            item.last_game_uuid,
            item.last_parent_ply,
        )
        for item in projections.branches
    ]
    route_branches = [
        (
            item.manifest_hash,
            item.corpus_id,
            item.anchor_ply,
            item.catalog[1],
            item.catalog[2],
            *item.parent_key,
            item.branch_kind,
            item.child_uci,
            item.color_scope,
            item.raw_event_count,
            item.distinct_game_count,
            item.first_game_sequence,
            item.first_game_uuid,
            item.first_parent_ply,
            item.last_game_sequence,
            item.last_game_uuid,
            item.last_parent_ply,
        )
        for item in projections.route_branches
    ]
    return positions, routes, branches, route_branches


def _insert_rows(
    connection: sqlite3.Connection, table: str, rows: list[tuple[object, ...]]
) -> None:
    if rows:
        placeholders = ", ".join("?" for _ in rows[0])
        connection.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)


def _matches(
    connection: sqlite3.Connection, facts: RecurrenceFacts, projections: RecurrenceProjections
) -> bool:
    state = connection.execute(
        "SELECT accepted_manifest_hash, corpus_id, accepted_schema_version, "
        "accepted_classification_schema_version, accepted_catalog_schema_version, "
        "accepted_relationship_schema_version, accepted_corpus_schema_version, "
        "classification_input_signature, corpus_input_signature, game_metadata_input_signature, "
        "game_count, occurrence_count, route_event_count, branch_event_count "
        "FROM opening_recurrence_state WHERE accepted_manifest_hash = ? AND corpus_id = ?",
        (facts.manifest_hash, facts.corpus_id),
    ).fetchone()
    expected_state = _state_row(facts)
    if state != expected_state:
        return False
    run = connection.execute(
        "SELECT run_id, manifest_hash, corpus_id, schema_version, classification_schema_version, "
        "catalog_schema_version, relationship_schema_version, corpus_schema_version, status, "
        "game_count, occurrence_count, route_event_count, branch_event_count, details "
        "FROM opening_recurrence_run WHERE run_id = ?",
        (_run_id(facts),),
    ).fetchone()
    expected_run = (
        _run_id(facts),
        facts.manifest_hash,
        facts.corpus_id,
        facts.schema_version,
        facts.classification_schema_version,
        facts.catalog_schema_version,
        facts.relationship_schema_version,
        facts.corpus_schema_version,
        "success",
        facts.game_count,
        facts.occurrence_count,
        facts.route_event_count,
        facts.branch_event_count,
        DETAILS,
    )
    if run != expected_run:
        return False
    queries = (
        "SELECT * FROM opening_recurrence_game WHERE manifest_hash = ? AND corpus_id = ? "
        "ORDER BY game_sequence",
        "SELECT * FROM opening_recurrence_occurrence WHERE manifest_hash = ? AND corpus_id = ? "
        "ORDER BY game_uuid, ply",
        "SELECT * FROM opening_recurrence_route_event WHERE manifest_hash = ? AND corpus_id = ? "
        "ORDER BY game_uuid, anchor_ply, source_file, source_row_ordinal, route_ply",
        "SELECT * FROM opening_recurrence_branch_event WHERE manifest_hash = ? AND corpus_id = ? "
        "ORDER BY game_uuid, parent_ply",
    )
    expected_events = tuple(
        function(facts) for function in (_game_rows, _occurrence_rows, _route_rows, _branch_rows)
    )
    for query, expected in zip(queries, expected_events):
        if connection.execute(query, (facts.manifest_hash, facts.corpus_id)).fetchall() != expected:
            return False
    projection_queries = (
        "SELECT * FROM opening_recurrence_position_projection WHERE manifest_hash = ? "
        "AND corpus_id = ? "
        "ORDER BY placement, side_to_move, castling, en_passant, color_scope",
        "SELECT * FROM opening_recurrence_route_projection WHERE manifest_hash = ? "
        "AND corpus_id = ? "
        "ORDER BY anchor_ply, source_file, source_row_ordinal, placement, side_to_move, castling, "
        "en_passant, color_scope",
        "SELECT * FROM opening_recurrence_branch_projection WHERE manifest_hash = ? "
        "AND corpus_id = ? "
        "ORDER BY parent_placement, parent_side_to_move, parent_castling, parent_en_passant, "
        "branch_kind, child_uci, color_scope",
        "SELECT * FROM opening_recurrence_route_branch_projection WHERE manifest_hash = ? "
        "AND corpus_id = ? ORDER BY anchor_ply, source_file, source_row_ordinal, parent_placement, "
        "parent_side_to_move, parent_castling, parent_en_passant, branch_kind, child_uci, "
        "color_scope",
    )
    for query, expected in zip(projection_queries, _projection_rows(projections)):
        if connection.execute(query, (facts.manifest_hash, facts.corpus_id)).fetchall() != expected:
            return False
    return True


def _delete_scope(connection: sqlite3.Connection, facts: RecurrenceFacts) -> None:
    for table in (
        "opening_recurrence_route_branch_projection",
        "opening_recurrence_branch_projection",
        "opening_recurrence_route_projection",
        "opening_recurrence_position_projection",
        "opening_recurrence_branch_event",
        "opening_recurrence_route_event",
        "opening_recurrence_occurrence",
        "opening_recurrence_game",
        "opening_recurrence_state",
    ):
        column = (
            "accepted_manifest_hash" if table == "opening_recurrence_state" else "manifest_hash"
        )
        connection.execute(
            f"DELETE FROM {table} WHERE {column} = ? AND corpus_id = ?",
            (facts.manifest_hash, facts.corpus_id),
        )


def _validate_current_inputs(connection: sqlite3.Connection, facts: RecurrenceFacts) -> None:
    current = input_signatures(connection, facts.corpus_id)
    expected = (
        facts.manifest_hash,
        facts.corpus_id,
        facts.classification_input_signature,
        facts.corpus_input_signature,
        facts.game_metadata_input_signature,
        facts.classification_schema_version,
        facts.catalog_schema_version,
        facts.relationship_schema_version,
        facts.corpus_schema_version,
    )
    if current != expected:
        raise RecurrencePublicationError(
            "accepted S3/corpus/game inputs changed during publication"
        )


@dataclass(frozen=True)
class RecurrenceImportResult:
    run_id: str
    manifest_hash: str
    corpus_id: int
    status: str
    game_count: int
    occurrence_count: int
    route_event_count: int
    branch_event_count: int
    position_projection_count: int
    route_projection_count: int
    branch_projection_count: int
    route_branch_projection_count: int

    @property
    def games(self) -> int:
        return self.game_count

    @property
    def occurrences(self) -> int:
        return self.occurrence_count


def _result(
    facts: RecurrenceFacts, projections: RecurrenceProjections, status: str
) -> RecurrenceImportResult:
    return RecurrenceImportResult(
        _run_id(facts),
        facts.manifest_hash,
        facts.corpus_id,
        status,
        facts.game_count,
        facts.occurrence_count,
        facts.route_event_count,
        facts.branch_event_count,
        len(projections.positions),
        len(projections.routes),
        len(projections.branches),
        len(projections.route_branches),
    )


def publish_recurrence(
    connection: sqlite3.Connection, facts: RecurrenceFacts
) -> RecurrenceImportResult:
    """Publish one complete S4 build atomically, or retain the prior build."""

    connection.execute("PRAGMA foreign_keys = ON")
    if facts.schema_version != RECURRENCE_SCHEMA_VERSION:
        raise RecurrencePublicationError("recurrence facts use an incompatible schema version")
    current = input_signatures(connection, facts.corpus_id)
    expected = (
        facts.manifest_hash,
        facts.corpus_id,
        facts.classification_input_signature,
        facts.corpus_input_signature,
        facts.game_metadata_input_signature,
        facts.classification_schema_version,
        facts.catalog_schema_version,
        facts.relationship_schema_version,
        facts.corpus_schema_version,
    )
    if current != expected:
        raise RecurrencePublicationError("recurrence facts do not match accepted inputs")
    ensure_recurrence_schema(connection)
    projections = project_recurrence(facts)
    if _matches(connection, facts, projections):
        return _result(facts, projections, "unchanged")
    with connection:
        _validate_current_inputs(connection, facts)
        if _matches(connection, facts, projections):
            return _result(facts, projections, "unchanged")
        _delete_scope(connection, facts)
        connection.execute(
            "INSERT INTO opening_recurrence_run ("
            "run_id, manifest_hash, corpus_id, schema_version, classification_schema_version, "
            "catalog_schema_version, relationship_schema_version, corpus_schema_version, "
            "classification_input_signature, corpus_input_signature, "
            "game_metadata_input_signature, status, started_at, game_count, occurrence_count, "
            "route_event_count, branch_event_count, details) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'running', ?, ?, ?, ?, ?, ?)",
            (
                _run_id(facts),
                facts.manifest_hash,
                facts.corpus_id,
                facts.schema_version,
                facts.classification_schema_version,
                facts.catalog_schema_version,
                facts.relationship_schema_version,
                facts.corpus_schema_version,
                facts.classification_input_signature,
                facts.corpus_input_signature,
                facts.game_metadata_input_signature,
                _timestamp(),
                facts.game_count,
                facts.occurrence_count,
                facts.route_event_count,
                facts.branch_event_count,
                DETAILS,
            ),
        )
        _insert_rows(connection, "opening_recurrence_game", _game_rows(facts))
        _insert_rows(connection, "opening_recurrence_occurrence", _occurrence_rows(facts))
        _insert_rows(connection, "opening_recurrence_route_event", _route_rows(facts))
        _insert_rows(connection, "opening_recurrence_branch_event", _branch_rows(facts))
        position_rows, route_rows, branch_rows, route_branch_rows = _projection_rows(projections)
        _insert_rows(connection, "opening_recurrence_position_projection", position_rows)
        _insert_rows(connection, "opening_recurrence_route_projection", route_rows)
        _insert_rows(connection, "opening_recurrence_branch_projection", branch_rows)
        _insert_rows(connection, "opening_recurrence_route_branch_projection", route_branch_rows)
        connection.execute(
            "UPDATE opening_recurrence_run SET status = 'success', finished_at = ? "
            "WHERE run_id = ?",
            (_timestamp(), _run_id(facts)),
        )
        connection.execute(
            "INSERT INTO opening_recurrence_state (accepted_manifest_hash, corpus_id, "
            "accepted_schema_version, accepted_classification_schema_version, "
            "accepted_catalog_schema_version, "
            "accepted_relationship_schema_version, accepted_corpus_schema_version, "
            "classification_input_signature, corpus_input_signature, "
            "game_metadata_input_signature, accepted_at, "
            "game_count, occurrence_count, route_event_count, branch_event_count) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (*_state_row(facts)[:10], _timestamp(), *_state_row(facts)[10:]),
        )
    return _result(facts, projections, "success")


def import_recurrence(
    connection: sqlite3.Connection, corpus_id: int | None = None
) -> RecurrenceImportResult:
    """Derive accepted S4 facts and publish them atomically."""

    return publish_recurrence(connection, derive_recurrence(connection, corpus_id))


derive_recurrences = derive_recurrence
import_recurrences = import_recurrence
publish_recurrences = publish_recurrence
