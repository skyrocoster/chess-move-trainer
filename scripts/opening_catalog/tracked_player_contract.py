"""Settled S5 tracked-player identity and neutral-input contracts."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import yaml

from .classification_schema import CLASSIFICATION_SCHEMA_TABLES
from .recurrence_schema import RECURRENCE_SCHEMA_TABLES
from .schema import RELATIONSHIP_SCHEMA_TABLES, SCHEMA_TABLES

TRACKED_PLAYER_CLASSIFICATION_IDENTITY_FIELDS = (
    "player_uuid",
    "manifest_hash",
    "corpus_id",
    "game_uuid",
)
TRACKED_PLAYER_POSITION_IDENTITY_FIELDS = (
    "player_uuid",
    "manifest_hash",
    "corpus_id",
    "placement",
    "side_to_move",
    "castling",
    "en_passant",
    "color_scope",
)
TRACKED_PLAYER_ROUTE_IDENTITY_FIELDS = (
    "player_uuid",
    "manifest_hash",
    "corpus_id",
    "anchor_ply",
    "source_file",
    "source_row_ordinal",
    "placement",
    "side_to_move",
    "castling",
    "en_passant",
    "color_scope",
)
TRACKED_PLAYER_BRANCH_IDENTITY_FIELDS = (
    "player_uuid",
    "manifest_hash",
    "corpus_id",
    "parent_placement",
    "parent_side_to_move",
    "parent_castling",
    "parent_en_passant",
    "branch_kind",
    "child_uci",
    "color_scope",
)
TRACKED_PLAYER_ROUTE_BRANCH_IDENTITY_FIELDS = (
    "player_uuid",
    "manifest_hash",
    "corpus_id",
    "anchor_ply",
    "source_file",
    "source_row_ordinal",
    "parent_placement",
    "parent_side_to_move",
    "parent_castling",
    "parent_en_passant",
    "branch_kind",
    "child_uci",
    "color_scope",
)

CLASSIFICATION_INPUT_TABLES = tuple(
    sorted(CLASSIFICATION_SCHEMA_TABLES - {"opening_classification_run"})
)
RECURRENCE_INPUT_TABLES = tuple(sorted(RECURRENCE_SCHEMA_TABLES - {"opening_recurrence_run"}))
_CLASSIFICATION_FACT_TABLES = (
    "opening_classification_game",
    "opening_classification_anchor",
    "opening_classification_route",
)
UPSTREAM_PRESERVATION_TABLES = (
    "players",
    "games",
    "corpus_schema",
    "corpus",
    "corpus_game",
    "corpus_run",
    "position_state",
    "position_occurrence",
    *tuple(sorted(SCHEMA_TABLES)),
    *tuple(sorted(RELATIONSHIP_SCHEMA_TABLES)),
    *tuple(sorted(CLASSIFICATION_SCHEMA_TABLES)),
    *tuple(sorted(RECURRENCE_SCHEMA_TABLES)),
)


class TrackedPlayerContractError(ValueError):
    """The configured player cannot safely own an S5 projection."""


@dataclass(frozen=True)
class TableSignature:
    """A deterministic read-only signature for one preserved table."""

    table: str
    row_count: int
    digest: str


@dataclass(frozen=True)
class TrackedPlayerIdentity:
    """Durable S5 identity after the configured username has been discarded."""

    player_uuid: str
    manifest_hash: str
    corpus_id: int
    classification_schema_version: int
    recurrence_schema_version: int
    classification_input_signature: str
    recurrence_input_signature: str


def configured_username(config_path: Path) -> str:
    """Read the one setup-boundary username without treating its text as identity."""

    values = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(values, dict):
        raise TrackedPlayerContractError("tracked-player configuration must be a mapping")
    username = values.get("username")
    if not isinstance(username, str) or not username.strip():
        raise TrackedPlayerContractError("tracked-player configuration requires one username")
    return username.strip()


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def table_signature(connection: sqlite3.Connection, table: str) -> TableSignature:
    """Stream a deterministic signature without relying on SQLite ``rowid``."""

    return _table_signature(connection, table)


def _table_signature(
    connection: sqlite3.Connection,
    table: str,
    where: str = "",
    parameters: tuple[object, ...] = (),
    excluded_columns: frozenset[str] = frozenset(),
) -> TableSignature:
    columns = connection.execute(f"PRAGMA table_info({_quote_identifier(table)})").fetchall()
    if not columns:
        raise TrackedPlayerContractError(f"required table {table!r} is unavailable")
    names = [str(row[1]) for row in columns if str(row[1]) not in excluded_columns]
    primary_key = [str(row[1]) for row in sorted(columns, key=lambda row: int(row[5])) if row[5]]
    ordering = primary_key or names
    selected = ", ".join(_quote_identifier(name) for name in names)
    ordered = ", ".join(_quote_identifier(name) for name in ordering)
    digest = hashlib.sha256()
    count = 0
    for row in connection.execute(
        f"SELECT {selected} FROM {_quote_identifier(table)}{where} ORDER BY {ordered}", parameters
    ):
        digest.update(json.dumps(tuple(row), separators=(",", ":")).encode("utf-8"))
        digest.update(b"\n")
        count += 1
    return TableSignature(table, count, digest.hexdigest())


def _group_signature(
    connection: sqlite3.Connection,
    tables: tuple[str, ...],
    manifest_hash: str | None = None,
    corpus_id: int | None = None,
) -> str:
    digest = hashlib.sha256()
    signatures = []
    for table in tables:
        columns = {
            str(row[1])
            for row in connection.execute(f"PRAGMA table_info({_quote_identifier(table)})")
        }
        filters = []
        parameters: list[object] = []
        manifest_column = next(
            (name for name in ("manifest_hash", "accepted_manifest_hash") if name in columns),
            None,
        )
        if manifest_hash is not None and manifest_column is not None:
            filters.append(f"{_quote_identifier(manifest_column)} = ?")
            parameters.append(manifest_hash)
        if corpus_id is not None and "corpus_id" in columns:
            filters.append('"corpus_id" = ?')
            parameters.append(corpus_id)
        if filters:
            signatures.append(
                _table_signature(
                    connection,
                    table,
                    " WHERE " + " AND ".join(filters),
                    tuple(parameters),
                    frozenset({"accepted_at"}),
                )
            )
        else:
            signatures.append(table_signature(connection, table))
    for signature in signatures:
        digest.update(
            json.dumps(
                (signature.table, signature.row_count, signature.digest), separators=(",", ":")
            ).encode("utf-8")
        )
        digest.update(b"\n")
    return digest.hexdigest()


def upstream_preservation_signatures(
    connection: sqlite3.Connection,
) -> tuple[TableSignature, ...]:
    """Capture the player/corpus and neutral S3/S4 tables S5 must not mutate."""

    return tuple(table_signature(connection, table) for table in UPSTREAM_PRESERVATION_TABLES)


def resolve_tracked_player(
    connection: sqlite3.Connection, configured_name: str, corpus_id: int | None = None
) -> TrackedPlayerIdentity:
    """Resolve one configured username and validate accepted corpus/S3/S4 agreement."""

    connection.execute("PRAGMA foreign_keys = ON")
    player_rows = connection.execute(
        "SELECT uuid FROM players WHERE username = ? COLLATE NOCASE ORDER BY uuid",
        (configured_name,),
    ).fetchall()
    if len(player_rows) != 1:
        raise TrackedPlayerContractError(
            f"configured username must resolve to exactly one player; found {len(player_rows)}"
        )
    player_uuid = str(player_rows[0][0])
    return _resolved_tracked_player(connection, player_uuid, corpus_id)


def _resolved_tracked_player(
    connection: sqlite3.Connection, player_uuid: str, corpus_id: int | None = None
) -> TrackedPlayerIdentity:
    """Refresh an already-resolved UUID without returning to username identity."""

    corpus_parameters: tuple[object, ...] = () if corpus_id is None else (corpus_id,)
    corpus_filter = "" if corpus_id is None else " WHERE corpus_id = ?"
    corpus_rows = connection.execute(
        "SELECT corpus_id, subject_player_uuid FROM corpus" + corpus_filter + " ORDER BY corpus_id",
        corpus_parameters,
    ).fetchall()
    if len(corpus_rows) != 1:
        raise TrackedPlayerContractError(
            f"configured player requires exactly one accepted corpus; found {len(corpus_rows)}"
        )
    accepted_corpus_id, subject_uuid = corpus_rows[0]
    rows = connection.execute(
        "SELECT r.accepted_manifest_hash, cs.accepted_schema_version, "
        "r.accepted_schema_version, catalog.accepted_schema_version, "
        "catalog.record_count, corpus_schema.version, classification_schema.version, "
        "recurrence_schema.version, cs.accepted_catalog_schema_version, "
        "cs.accepted_relationship_schema_version, classification_run.run_id, "
        "classification_run.schema_version, classification_run.catalog_schema_version, "
        "classification_run.relationship_schema_version, classification_run.status, "
        "classification_run.details, r.accepted_classification_schema_version, "
        "r.accepted_catalog_schema_version, r.accepted_relationship_schema_version, "
        "r.accepted_corpus_schema_version, r.classification_input_signature, "
        "r.corpus_input_signature, r.game_metadata_input_signature, r.game_count, "
        "r.occurrence_count, r.route_event_count, r.branch_event_count, "
        "recurrence_run.run_id, recurrence_run.schema_version, "
        "recurrence_run.classification_schema_version, "
        "recurrence_run.catalog_schema_version, recurrence_run.relationship_schema_version, "
        "recurrence_run.corpus_schema_version, recurrence_run.classification_input_signature, "
        "recurrence_run.corpus_input_signature, recurrence_run.game_metadata_input_signature, "
        "recurrence_run.status, recurrence_run.game_count, recurrence_run.occurrence_count, "
        "recurrence_run.route_event_count, recurrence_run.branch_event_count, "
        "recurrence_run.details "
        "FROM opening_catalog_state AS catalog JOIN opening_classification_state AS cs "
        "ON cs.accepted_manifest_hash = catalog.accepted_manifest_hash "
        "JOIN opening_classification_run AS classification_run "
        "ON classification_run.manifest_hash = cs.accepted_manifest_hash "
        "AND classification_run.corpus_id = cs.corpus_id "
        "JOIN opening_recurrence_state AS r "
        "ON r.accepted_manifest_hash = cs.accepted_manifest_hash "
        "AND r.corpus_id = cs.corpus_id "
        "AND r.accepted_classification_schema_version = cs.accepted_schema_version "
        "JOIN opening_recurrence_run AS recurrence_run "
        "ON recurrence_run.manifest_hash = r.accepted_manifest_hash "
        "AND recurrence_run.corpus_id = r.corpus_id "
        "JOIN corpus_schema ON corpus_schema.id = 1 "
        "JOIN opening_classification_schema AS classification_schema "
        "ON classification_schema.id = 1 "
        "JOIN opening_recurrence_schema AS recurrence_schema ON recurrence_schema.id = 1 "
        "WHERE catalog.id = 1 AND cs.corpus_id = ?",
        (accepted_corpus_id,),
    ).fetchall()
    if len(rows) != 1:
        raise TrackedPlayerContractError(
            "configured player requires exactly one current accepted S3/S4 state; "
            f"found {len(rows)}"
        )
    row = tuple(rows[0])
    manifest_hash, class_version, recurrence_version = row[:3]
    if str(subject_uuid) != player_uuid:
        raise TrackedPlayerContractError(
            "configured player UUID does not match accepted corpus ownership"
        )
    classification_counts = tuple(
        int(
            connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE manifest_hash = ? AND corpus_id = ?",
                (manifest_hash, accepted_corpus_id),
            ).fetchone()[0]
        )
        for table in _CLASSIFICATION_FACT_TABLES
    )
    classification_token = _accepted_state_token(
        "s3",
        (
            player_uuid,
            int(accepted_corpus_id),
            *row[3:15],
            *classification_counts,
        ),
    )
    recurrence_token = _accepted_state_token(
        "s4",
        (
            classification_token,
            *row[16:-1],
        ),
    )
    return TrackedPlayerIdentity(
        player_uuid,
        str(manifest_hash),
        int(accepted_corpus_id),
        int(class_version),
        int(recurrence_version),
        classification_token,
        recurrence_token,
    )


def _accepted_state_token(stage: str, values: tuple[object, ...]) -> str:
    """Hash stable accepted publication authority without reading fact-row contents."""

    payload = json.dumps((stage, values), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
