"""Read-only adapter for the accepted opening Line Library facts."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from backend.app.features.positions.repository import (
    SUBJECT_PLAYER_UUID,
    database_path,
)
from scripts.opening_catalog.classification_schema import CLASSIFICATION_SCHEMA_VERSION
from scripts.opening_catalog.recurrence_schema import RECURRENCE_SCHEMA_VERSION
from scripts.opening_catalog.schema import RELATIONSHIP_SCHEMA_VERSION, SCHEMA_VERSION

from .api_schemas import (
    FilterDeclaration,
    GroupNode,
    LineLibraryResponse,
    LineNode,
    ReferenceNode,
    SortDeclaration,
)
from .contract import (
    APPEARS_IN_MY_GAMES_FILTER_KEY,
    CatalogIdentity,
    PositionIdentity,
    TranspositionAppearance,
    TranspositionLink,
    canonical_transposition_presentation,
    encode_catalog_node_id,
    encode_reference_node_id,
)
from .errors import OpeningLineLibraryUnavailableError
from .schema_validation import CORPUS_SCHEMA_VERSION, require_schema


@dataclass(frozen=True)
class OpeningLineLibraryQuery:
    search: str | None = None
    eco_from: str | None = None
    eco_to: str | None = None
    appears_in_my_games: bool = False
    sort: str = "default"


@dataclass(frozen=True)
class _AcceptedScope:
    manifest_hash: str
    corpus_id: int
    record_count: int


@dataclass(frozen=True)
class _CatalogRecord:
    identity: CatalogIdentity
    eco: str
    name: str
    move_sequence: str


@dataclass(frozen=True)
class _ParentEdge:
    parent: CatalogIdentity
    child: CatalogIdentity
    appearance: TranspositionAppearance


def _database_uri(path: Path, mode: str) -> str:
    return f"{path.expanduser().resolve().as_uri()}?mode={mode}"


def open_read_connection() -> sqlite3.Connection:
    """Open an existing supported database without schema creation or writes."""

    path = database_path().expanduser().resolve()
    if not path.is_file():
        raise OpeningLineLibraryUnavailableError

    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(_database_uri(path, "ro"), uri=True, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        require_schema(connection)
        return connection
    except OpeningLineLibraryUnavailableError:
        if connection is not None:
            connection.close()
        raise
    except sqlite3.Error as error:
        if connection is not None:
            connection.close()
        raise OpeningLineLibraryUnavailableError from error


class OpeningLineLibraryRepository:
    """Translate accepted catalog relationships into one normalized response."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def fetch(self, query: OpeningLineLibraryQuery) -> LineLibraryResponse:
        scope = self._accepted_scope()
        all_records = self._catalog_records(scope, None)
        if len(all_records) != scope.record_count:
            raise OpeningLineLibraryUnavailableError
        matching_records = self._catalog_records(scope, query)
        records_by_identity = {record.identity: record for record in all_records}
        selected = {record.identity for record in matching_records}

        parent_edges = self._parent_edges(scope)
        parents_by_child: dict[CatalogIdentity, set[CatalogIdentity]] = {}
        children_by_parent: dict[CatalogIdentity, list[_ParentEdge]] = {}
        for edge in parent_edges:
            parents_by_child.setdefault(edge.child, set()).add(edge.parent)
            children_by_parent.setdefault(edge.parent, []).append(edge)

        selected.update(self._ancestors(selected, parents_by_child))
        transposition_links = self._transposition_links(scope)
        presentation = canonical_transposition_presentation(transposition_links)
        canonical_by_identity = dict(presentation.canonical_by_identity)
        transposition_appearances = {
            appearance for link in transposition_links for appearance in (link.first, link.second)
        }

        children_by_selected_parent: dict[CatalogIdentity, set[str]] = {}
        reference_nodes: dict[str, ReferenceNode] = {}
        for edge in parent_edges:
            if edge.parent not in selected or edge.child not in selected:
                continue
            child_id = encode_catalog_node_id(edge.child)
            canonical = canonical_by_identity.get(edge.child)
            if (
                canonical is not None
                and edge.appearance in transposition_appearances
                and edge.appearance != canonical
            ):
                child_id = encode_reference_node_id(edge.appearance, child_id)
                reference_nodes[child_id] = ReferenceNode(
                    id=child_id,
                    kind="reference",
                    target_id=encode_catalog_node_id(edge.child),
                    metadata={"label": "Transposition reference"},
                )
            children_by_selected_parent.setdefault(edge.parent, set()).add(child_id)

        nodes: dict[str, GroupNode | LineNode | ReferenceNode] = {}
        for identity in sorted(selected):
            record = records_by_identity.get(identity)
            if record is None:
                raise OpeningLineLibraryUnavailableError
            node_id = encode_catalog_node_id(identity)
            child_ids = sorted(children_by_selected_parent.get(identity, set()))
            metadata = {
                "eco": record.eco,
                "name": record.name,
                "move_sequence": record.move_sequence,
            }
            if identity in children_by_parent:
                nodes[node_id] = GroupNode(
                    id=node_id,
                    kind="group",
                    selectable=bool(child_ids),
                    child_ids=child_ids,
                    metadata=metadata,
                )
            else:
                nodes[node_id] = LineNode(
                    id=node_id,
                    kind="line",
                    metadata=metadata,
                )
        nodes.update(reference_nodes)

        roots = [
            encode_catalog_node_id(identity)
            for identity in sorted(selected)
            if not any(parent in selected for parent in parents_by_child.get(identity, set()))
        ]
        roots.sort()
        return LineLibraryResponse(
            roots=roots,
            nodes=nodes,
            filters=self._filters(),
            filter_apply_mode="immediate",
            sorts=[SortDeclaration(key="default", label="Default", default=True)],
            selection_limit=None,
        )

    def _accepted_scope(self) -> _AcceptedScope:
        try:
            rows = self._connection.execute(
                """
                SELECT r.accepted_manifest_hash, r.corpus_id,
                       r.accepted_schema_version,
                       r.accepted_classification_schema_version,
                       r.accepted_catalog_schema_version,
                       r.accepted_relationship_schema_version,
                       r.accepted_corpus_schema_version,
                       c.accepted_manifest_hash AS catalog_manifest,
                       c.accepted_schema_version AS catalog_version,
                       c.record_count,
                       l.accepted_manifest_hash AS relationship_manifest,
                       l.accepted_schema_version AS relationship_version
                FROM opening_recurrence_state AS r
                JOIN corpus AS p ON p.corpus_id = r.corpus_id
                JOIN opening_catalog_state AS c ON c.id = 1
                JOIN opening_relationship_state AS l
                  ON l.accepted_manifest_hash = r.accepted_manifest_hash
                WHERE p.subject_player_uuid = ?
                  AND r.accepted_schema_version = ?
                  AND r.accepted_classification_schema_version = ?
                  AND r.accepted_catalog_schema_version = ?
                  AND r.accepted_relationship_schema_version = ?
                  AND r.accepted_corpus_schema_version = ?
                LIMIT 2
                """,
                (
                    SUBJECT_PLAYER_UUID,
                    RECURRENCE_SCHEMA_VERSION,
                    CLASSIFICATION_SCHEMA_VERSION,
                    SCHEMA_VERSION,
                    RELATIONSHIP_SCHEMA_VERSION,
                    CORPUS_SCHEMA_VERSION,
                ),
            ).fetchall()
        except sqlite3.Error as error:
            raise OpeningLineLibraryUnavailableError from error

        if len(rows) != 1:
            raise OpeningLineLibraryUnavailableError
        row = rows[0]
        manifest_hash = row["accepted_manifest_hash"]
        corpus_id = row["corpus_id"]
        record_count = row["record_count"]
        if (
            not isinstance(manifest_hash, str)
            or not manifest_hash
            or isinstance(corpus_id, bool)
            or not isinstance(corpus_id, int)
            or isinstance(record_count, bool)
            or not isinstance(record_count, int)
            or record_count < 0
            or row["catalog_manifest"] != manifest_hash
            or row["relationship_manifest"] != manifest_hash
            or row["catalog_version"] != SCHEMA_VERSION
            or row["relationship_version"] != RELATIONSHIP_SCHEMA_VERSION
        ):
            raise OpeningLineLibraryUnavailableError
        return _AcceptedScope(manifest_hash, corpus_id, record_count)

    def _catalog_records(
        self,
        scope: _AcceptedScope,
        query: OpeningLineLibraryQuery | None,
    ) -> list[_CatalogRecord]:
        clauses = ["manifest_hash = ?"]
        parameters: list[object] = [scope.manifest_hash]
        if query is not None:
            if query.search:
                clauses.append(
                    "(LOWER(eco) LIKE ? OR LOWER(name) LIKE ? OR LOWER(move_sequence) LIKE ?)"
                )
                needle = f"%{query.search.lower()}%"
                parameters.extend((needle, needle, needle))
            if query.eco_from is not None:
                clauses.append("eco >= ?")
                parameters.append(query.eco_from)
            if query.eco_to is not None:
                clauses.append("eco <= ?")
                parameters.append(query.eco_to)
            if query.appears_in_my_games:
                clauses.append(
                    "EXISTS ("
                    "SELECT 1 FROM opening_recurrence_route_projection AS rp "
                    "WHERE rp.manifest_hash = opening_catalog.manifest_hash "
                    "AND rp.corpus_id = ? "
                    "AND rp.source_file = opening_catalog.source_file "
                    "AND rp.source_row_ordinal = opening_catalog.source_row_ordinal "
                    "AND rp.color_scope = 'overall' "
                    "AND rp.distinct_game_count > 0"
                    ")"
                )
                parameters.append(scope.corpus_id)
        statement = (
            "SELECT manifest_hash, source_file, source_row_ordinal, eco, name, move_sequence "
            "FROM opening_catalog WHERE "
            + " AND ".join(clauses)
            + " ORDER BY source_file, source_row_ordinal"
        )
        try:
            rows = self._connection.execute(statement, parameters).fetchall()
        except sqlite3.Error as error:
            raise OpeningLineLibraryUnavailableError from error

        records: list[_CatalogRecord] = []
        try:
            for row in rows:
                records.append(
                    _CatalogRecord(
                        identity=CatalogIdentity(
                            manifest_hash=row["manifest_hash"],
                            source_file=row["source_file"],
                            source_row_ordinal=row["source_row_ordinal"],
                        ),
                        eco=self._text(row["eco"]),
                        name=self._text(row["name"]),
                        move_sequence=self._text(row["move_sequence"]),
                    )
                )
        except (TypeError, ValueError) as error:
            raise OpeningLineLibraryUnavailableError from error
        return records

    def _parent_edges(self, scope: _AcceptedScope) -> list[_ParentEdge]:
        try:
            rows = self._connection.execute(
                """
                SELECT pl.child_source_file, pl.child_source_row_ordinal, pl.child_ply,
                       pl.parent_source_file, pl.parent_source_row_ordinal,
                       pm.placement, pm.side_to_move, pm.castling, pm.en_passant,
                       pm.uci_prefix
                FROM opening_parent_link AS pl
                JOIN opening_position_membership AS pm
                  ON pm.manifest_hash = pl.manifest_hash
                 AND pm.source_file = pl.child_source_file
                 AND pm.source_row_ordinal = pl.child_source_row_ordinal
                 AND pm.ply = pl.child_ply
                WHERE pl.manifest_hash = ?
                ORDER BY pl.parent_source_file, pl.parent_source_row_ordinal,
                         pl.child_source_file, pl.child_source_row_ordinal, pl.child_ply
                """,
                (scope.manifest_hash,),
            ).fetchall()
        except sqlite3.Error as error:
            raise OpeningLineLibraryUnavailableError from error

        edges: list[_ParentEdge] = []
        try:
            for row in rows:
                child = CatalogIdentity(
                    scope.manifest_hash,
                    row["child_source_file"],
                    row["child_source_row_ordinal"],
                )
                parent = CatalogIdentity(
                    scope.manifest_hash,
                    row["parent_source_file"],
                    row["parent_source_row_ordinal"],
                )
                position = PositionIdentity(
                    self._text(row["placement"]),
                    self._text(row["side_to_move"]),
                    self._text(row["castling"]),
                    self._text(row["en_passant"]),
                )
                edges.append(
                    _ParentEdge(
                        parent=parent,
                        child=child,
                        appearance=TranspositionAppearance(
                            identity=child,
                            position=position,
                            ply=row["child_ply"],
                            uci_prefix=self._text(row["uci_prefix"]),
                        ),
                    )
                )
        except (TypeError, ValueError) as error:
            raise OpeningLineLibraryUnavailableError from error
        return edges

    def _transposition_links(self, scope: _AcceptedScope) -> list[TranspositionLink]:
        try:
            rows = self._connection.execute(
                """
                SELECT placement, side_to_move, castling, en_passant,
                       source_file_a, source_row_ordinal_a, ply_a, uci_prefix_a,
                       source_file_b, source_row_ordinal_b, ply_b, uci_prefix_b
                FROM opening_transposition_link
                WHERE manifest_hash = ?
                ORDER BY source_file_a, source_row_ordinal_a, ply_a,
                         source_file_b, source_row_ordinal_b, ply_b
                """,
                (scope.manifest_hash,),
            ).fetchall()
        except sqlite3.Error as error:
            raise OpeningLineLibraryUnavailableError from error

        links: list[TranspositionLink] = []
        try:
            for row in rows:
                position = PositionIdentity(
                    self._text(row["placement"]),
                    self._text(row["side_to_move"]),
                    self._text(row["castling"]),
                    self._text(row["en_passant"]),
                )
                links.append(
                    TranspositionLink(
                        first=TranspositionAppearance(
                            identity=CatalogIdentity(
                                scope.manifest_hash,
                                row["source_file_a"],
                                row["source_row_ordinal_a"],
                            ),
                            position=position,
                            ply=row["ply_a"],
                            uci_prefix=self._text(row["uci_prefix_a"]),
                        ),
                        second=TranspositionAppearance(
                            identity=CatalogIdentity(
                                scope.manifest_hash,
                                row["source_file_b"],
                                row["source_row_ordinal_b"],
                            ),
                            position=position,
                            ply=row["ply_b"],
                            uci_prefix=self._text(row["uci_prefix_b"]),
                        ),
                    )
                )
        except (TypeError, ValueError) as error:
            raise OpeningLineLibraryUnavailableError from error
        return links

    @staticmethod
    def _ancestors(
        selected: set[CatalogIdentity],
        parents_by_child: dict[CatalogIdentity, set[CatalogIdentity]],
    ) -> set[CatalogIdentity]:
        ancestors: set[CatalogIdentity] = set()
        pending = list(selected)
        while pending:
            child = pending.pop()
            for parent in parents_by_child.get(child, set()):
                if parent not in selected and parent not in ancestors:
                    ancestors.add(parent)
                    pending.append(parent)
        return ancestors

    @staticmethod
    def _filters() -> list[FilterDeclaration]:
        return [
            FilterDeclaration(key="search", label="Search", type="search"),
            FilterDeclaration(
                key="eco",
                label="ECO code/range",
                type="range",
                range_start="A00",
                range_end="E99",
                metadata={"value_kind": "eco"},
            ),
            FilterDeclaration(
                key=APPEARS_IN_MY_GAMES_FILTER_KEY,
                label="Appears in my games",
                type="toggle",
                metadata={"scope": "fixed accepted corpus"},
            ),
        ]

    @staticmethod
    def _text(value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("expected text")
        return value
