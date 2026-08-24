"""Atomic temporary SQLite publication for one tracked-player projection."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime

from .tracked_player import TrackedPlayerFacts, accepted_tracked_player_counts
from .tracked_player_contract import (
    TrackedPlayerIdentity,
    _resolved_tracked_player,
    resolve_tracked_player,
)
from .tracked_player_schema import TRACKED_PLAYER_SCHEMA_VERSION, ensure_tracked_player_schema

DETAILS = "deterministic tracked-player projection publication"


class TrackedPlayerPublicationError(ValueError):
    """Personal facts cannot be published without violating the accepted boundary."""


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _run_id(identity: TrackedPlayerIdentity) -> str:
    payload = json.dumps(
        (
            "opening-tracked-player",
            TRACKED_PLAYER_SCHEMA_VERSION,
            identity.player_uuid,
            identity.manifest_hash,
            identity.corpus_id,
            identity.classification_schema_version,
            identity.recurrence_schema_version,
            identity.classification_input_signature,
            identity.recurrence_input_signature,
        ),
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stable_identity(identity: TrackedPlayerIdentity) -> tuple[object, ...]:
    return (
        identity.player_uuid,
        identity.manifest_hash,
        identity.corpus_id,
        TRACKED_PLAYER_SCHEMA_VERSION,
        identity.classification_schema_version,
        identity.recurrence_schema_version,
        identity.classification_input_signature,
        identity.recurrence_input_signature,
    )


_PERSONAL_TABLES = (
    "opening_player_classification_game",
    "opening_player_position_projection",
    "opening_player_route_projection",
    "opening_player_branch_projection",
    "opening_player_route_branch_projection",
)
_PROJECTION_SOURCES = (
    "opening_recurrence_position_projection",
    "opening_recurrence_route_projection",
    "opening_recurrence_branch_projection",
    "opening_recurrence_route_branch_projection",
)


def _matching_counts(
    connection: sqlite3.Connection, identity: TrackedPlayerIdentity
) -> tuple[int, int, int, int, int] | None:
    state = connection.execute(
        "SELECT player_uuid, accepted_manifest_hash, corpus_id, accepted_schema_version, "
        "accepted_classification_schema_version, accepted_recurrence_schema_version, "
        "classification_input_signature, recurrence_input_signature, "
        "classification_game_count, position_projection_count, route_projection_count, "
        "branch_projection_count, route_branch_projection_count "
        "FROM opening_tracked_player_state WHERE player_uuid = ? "
        "AND accepted_manifest_hash = ? AND corpus_id = ?",
        (identity.player_uuid, identity.manifest_hash, identity.corpus_id),
    ).fetchone()
    if state is None or tuple(state[:8]) != _stable_identity(identity):
        return None
    counts = tuple(int(value) for value in state[8:])
    run = connection.execute(
        "SELECT run_id, status, details FROM opening_tracked_player_run WHERE run_id = ?",
        (_run_id(identity),),
    ).fetchone()
    if run != (_run_id(identity), "success", DETAILS):
        return None
    return counts[0], counts[1], counts[2], counts[3], counts[4]


def _assert_existing_state_compatible(
    connection: sqlite3.Connection, identity: TrackedPlayerIdentity
) -> None:
    expected = _stable_identity(identity)
    states = connection.execute(
        "SELECT player_uuid, accepted_manifest_hash, corpus_id, accepted_schema_version, "
        "accepted_classification_schema_version, accepted_recurrence_schema_version, "
        "classification_input_signature, recurrence_input_signature "
        "FROM opening_tracked_player_state WHERE player_uuid = ? "
        "ORDER BY accepted_manifest_hash, corpus_id",
        (identity.player_uuid,),
    ).fetchall()
    if any(tuple(state) != expected for state in states):
        raise TrackedPlayerPublicationError(
            "existing tracked-player state has incompatible accepted inputs"
        )


def _insert_accepted_rows(connection: sqlite3.Connection, identity: TrackedPlayerIdentity) -> None:
    parameters = (
        identity.player_uuid,
        identity.manifest_hash,
        identity.corpus_id,
        identity.player_uuid,
        identity.player_uuid,
    )
    connection.execute(
        "INSERT INTO opening_player_classification_game "
        "SELECT ?, cg.manifest_hash, cg.corpus_id, cg.game_uuid "
        "FROM opening_classification_game AS cg "
        "JOIN corpus_game AS member ON member.corpus_id = cg.corpus_id "
        "AND member.game_uuid = cg.game_uuid "
        "JOIN games AS game ON game.uuid = cg.game_uuid "
        "WHERE cg.manifest_hash = ? AND cg.corpus_id = ? "
        "AND (game.white_player_uuid = ? OR game.black_player_uuid = ?)",
        parameters,
    )
    for destination, source in zip(_PERSONAL_TABLES[1:], _PROJECTION_SOURCES):
        connection.execute(
            f"INSERT INTO {destination} SELECT ?, source.* FROM {source} AS source "
            "WHERE source.manifest_hash = ? AND source.corpus_id = ?",
            (identity.player_uuid, identity.manifest_hash, identity.corpus_id),
        )


@dataclass(frozen=True)
class TrackedPlayerImportResult:
    run_id: str
    player_uuid: str
    manifest_hash: str
    corpus_id: int
    status: str
    classification_game_count: int
    position_projection_count: int
    route_projection_count: int
    branch_projection_count: int
    route_branch_projection_count: int


def _identity_result(
    identity: TrackedPlayerIdentity, counts: tuple[int, int, int, int, int], status: str
) -> TrackedPlayerImportResult:
    return TrackedPlayerImportResult(
        _run_id(identity),
        identity.player_uuid,
        identity.manifest_hash,
        identity.corpus_id,
        status,
        *counts,
    )


def publish_tracked_player(
    connection: sqlite3.Connection, facts: TrackedPlayerFacts
) -> TrackedPlayerImportResult:
    """Publish one complete personal state atomically or retain the prior state."""

    return _publish_identity(connection, facts.identity, facts.counts)


def _publish_identity(
    connection: sqlite3.Connection,
    identity: TrackedPlayerIdentity,
    expected_counts: tuple[int, int, int, int, int] | None = None,
) -> TrackedPlayerImportResult:
    """Publish accepted personal rows in SQLite without materializing them in Python."""

    ensure_tracked_player_schema(connection)
    if _resolved_tracked_player(connection, identity.player_uuid, identity.corpus_id) != identity:
        raise TrackedPlayerPublicationError("accepted S3/S4 inputs changed before publication")
    _assert_existing_state_compatible(connection, identity)
    matching_counts = _matching_counts(connection, identity)
    if matching_counts is not None and (
        expected_counts is None or matching_counts == expected_counts
    ):
        return _identity_result(identity, matching_counts, "unchanged")
    try:
        with connection:
            current_identity = _resolved_tracked_player(
                connection, identity.player_uuid, identity.corpus_id
            )
            if current_identity != identity:
                raise TrackedPlayerPublicationError(
                    "accepted S3/S4 inputs changed during publication"
                )
            counts = accepted_tracked_player_counts(connection, identity)
            if expected_counts is not None and counts != expected_counts:
                raise TrackedPlayerPublicationError(
                    "materialized tracked-player facts do not match accepted S3/S4 counts"
                )
            scope = (identity.player_uuid, identity.manifest_hash, identity.corpus_id)
            connection.execute(
                "INSERT OR IGNORE INTO opening_tracked_player (player_uuid) VALUES (?)",
                (identity.player_uuid,),
            )
            for table in reversed(_PERSONAL_TABLES):
                connection.execute(
                    f"DELETE FROM {table} WHERE player_uuid = ? AND manifest_hash = ? "
                    "AND corpus_id = ?",
                    scope,
                )
            connection.execute(
                "DELETE FROM opening_tracked_player_state WHERE player_uuid = ? "
                "AND accepted_manifest_hash = ? AND corpus_id = ?",
                scope,
            )
            connection.execute(
                "DELETE FROM opening_tracked_player_run WHERE player_uuid = ? "
                "AND manifest_hash = ? AND corpus_id = ?",
                scope,
            )
            now = _timestamp()
            connection.execute(
                "INSERT INTO opening_tracked_player_run VALUES "
                f"({', '.join('?' for _ in range(18))})",
                (
                    _run_id(identity),
                    *_stable_identity(identity),
                    "running",
                    now,
                    None,
                    *counts,
                    DETAILS,
                ),
            )
            connection.execute(
                "INSERT INTO opening_tracked_player_state VALUES "
                f"({', '.join('?' for _ in range(14))})",
                (*_stable_identity(identity), now, *counts),
            )
            _insert_accepted_rows(connection, identity)
            connection.execute(
                "UPDATE opening_tracked_player_run SET status = 'success', finished_at = ? "
                "WHERE run_id = ?",
                (_timestamp(), _run_id(identity)),
            )
    except sqlite3.Error as error:
        message = f"tracked-player publication failed: {error}"
        raise TrackedPlayerPublicationError(message) from error
    return _identity_result(identity, counts, "success")


def import_tracked_player(
    connection: sqlite3.Connection, configured_name: str, corpus_id: int | None = None
) -> TrackedPlayerImportResult:
    """Derive and atomically publish one configured tracked player."""

    identity = resolve_tracked_player(connection, configured_name, corpus_id)
    ensure_tracked_player_schema(connection)
    _assert_existing_state_compatible(connection, identity)
    matching_counts = _matching_counts(connection, identity)
    if matching_counts is not None:
        return _identity_result(identity, matching_counts, "unchanged")
    return _publish_identity(connection, identity)
