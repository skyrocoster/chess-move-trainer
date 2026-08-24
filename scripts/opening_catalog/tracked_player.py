"""Deterministic personal facts derived from accepted neutral S3/S4 rows."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from .classification_schema import CLASSIFICATION_SCHEMA_VERSION
from .recurrence_schema import RECURRENCE_SCHEMA_VERSION
from .tracked_player_contract import (
    TrackedPlayerContractError,
    TrackedPlayerIdentity,
    _resolved_tracked_player,
    resolve_tracked_player,
)


class TrackedPlayerDerivationError(TrackedPlayerContractError):
    """Accepted inputs cannot produce a safe personal projection."""


@dataclass(frozen=True)
class TrackedPlayerFacts:
    """Bounded publication metadata for one accepted input identity."""

    identity: TrackedPlayerIdentity
    counts: tuple[int, int, int, int, int]


_PROJECTION_TABLES = (
    "opening_recurrence_position_projection",
    "opening_recurrence_route_projection",
    "opening_recurrence_branch_projection",
    "opening_recurrence_route_branch_projection",
)


def accepted_tracked_player_counts(
    connection: sqlite3.Connection, identity: TrackedPlayerIdentity
) -> tuple[int, int, int, int, int]:
    """Count accepted output in SQLite without returning any fact rows."""

    classification_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM opening_classification_game AS cg "
            "JOIN corpus_game AS member ON member.corpus_id = cg.corpus_id "
            "AND member.game_uuid = cg.game_uuid "
            "JOIN games AS game ON game.uuid = cg.game_uuid "
            "WHERE cg.manifest_hash = ? AND cg.corpus_id = ? "
            "AND (game.white_player_uuid = ? OR game.black_player_uuid = ?)",
            (
                identity.manifest_hash,
                identity.corpus_id,
                identity.player_uuid,
                identity.player_uuid,
            ),
        ).fetchone()[0]
    )
    projection_counts = tuple(
        int(
            connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE manifest_hash = ? AND corpus_id = ?",
                (identity.manifest_hash, identity.corpus_id),
            ).fetchone()[0]
        )
        for table in _PROJECTION_TABLES
    )
    return (
        classification_count,
        projection_counts[0],
        projection_counts[1],
        projection_counts[2],
        projection_counts[3],
    )


def derive_tracked_player(
    connection: sqlite3.Connection,
    configured_name: str,
    corpus_id: int | None = None,
    *,
    _identity: TrackedPlayerIdentity | None = None,
) -> TrackedPlayerFacts:
    """Resolve the configured player once and derive only accepted S3/S4 output."""

    identity = _identity or resolve_tracked_player(connection, configured_name, corpus_id)
    if (
        identity.classification_schema_version != CLASSIFICATION_SCHEMA_VERSION
        or identity.recurrence_schema_version != RECURRENCE_SCHEMA_VERSION
    ):
        raise TrackedPlayerDerivationError("accepted S3/S4 schema versions are incompatible")
    facts = TrackedPlayerFacts(identity, accepted_tracked_player_counts(connection, identity))
    if _resolved_tracked_player(connection, identity.player_uuid, identity.corpus_id) != identity:
        raise TrackedPlayerDerivationError("accepted S3/S4 inputs changed during derivation")
    return facts
