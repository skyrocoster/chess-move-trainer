"""Deterministic neutral classification facts from accepted SQLite rows."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from dataclasses import dataclass

from scripts.chess_com._schema import SCHEMA_VERSION as CORPUS_SCHEMA_VERSION

from .classification_schema import CLASSIFICATION_SCHEMA_VERSION
from .importer import OpeningCatalogError
from .schema import RELATIONSHIP_SCHEMA_VERSION
from .schema import SCHEMA_VERSION as CATALOG_SCHEMA_VERSION

PositionKey = tuple[str, str, str, str]


class ClassificationError(OpeningCatalogError):
    """The accepted catalog, relationships, or corpus cannot be classified safely."""


@dataclass(frozen=True)
class ClassificationGameFact:
    """One accepted corpus game and its immutable corpus-source fingerprint."""

    game_uuid: str
    source_fingerprint: str


@dataclass(frozen=True)
class ClassificationAnchorFact:
    """One catalog membership reached at one exact accepted game occurrence."""

    game_uuid: str
    anchor_ply: int
    source_file: str
    source_row_ordinal: int
    anchor_placement: str
    anchor_side_to_move: str
    anchor_castling: str
    anchor_en_passant: str
    anchor_san: str
    anchor_uci: str

    @property
    def key(self) -> PositionKey:
        return (
            self.anchor_placement,
            self.anchor_side_to_move,
            self.anchor_castling,
            self.anchor_en_passant,
        )


@dataclass(frozen=True)
class ClassificationRouteFact:
    """One observed occurrence in the inclusive suffix after an anchor."""

    game_uuid: str
    anchor_ply: int
    source_file: str
    source_row_ordinal: int
    route_ply: int
    route_placement: str
    route_side_to_move: str
    route_castling: str
    route_en_passant: str
    route_san: str
    route_uci: str
    route_halfmove_clock: int
    route_fullmove_number: int

    @property
    def key(self) -> PositionKey:
        return (
            self.route_placement,
            self.route_side_to_move,
            self.route_castling,
            self.route_en_passant,
        )


@dataclass(frozen=True)
class ClassificationFacts:
    """Complete deterministic facts for one accepted manifest and corpus."""

    manifest_hash: str
    corpus_id: int
    schema_version: int
    catalog_schema_version: int
    relationship_schema_version: int
    games: tuple[ClassificationGameFact, ...]
    anchors: tuple[ClassificationAnchorFact, ...]
    routes: tuple[ClassificationRouteFact, ...]

    @property
    def game_count(self) -> int:
        return len(self.games)

    @property
    def anchor_count(self) -> int:
        return len(self.anchors)

    @property
    def route_count(self) -> int:
        return len(self.routes)


@dataclass(frozen=True)
class _CatalogEndpoint:
    source_file: str
    source_row_ordinal: int
    key: PositionKey


@dataclass(frozen=True)
class _Occurrence:
    game_uuid: str
    ply: int
    key: PositionKey
    san: str | None
    uci: str | None
    halfmove_clock: int
    fullmove_number: int


def _query_error(error: sqlite3.Error, message: str) -> ClassificationError:
    return ClassificationError(f"{message}: {error}")


def _version(connection: sqlite3.Connection, table: str) -> int:
    try:
        row = connection.execute(f"SELECT version FROM {table} WHERE id = 1").fetchone()
    except sqlite3.Error as error:
        raise _query_error(error, f"required schema table {table!r} is unavailable") from error
    if row is None:
        raise ClassificationError(f"required schema table {table!r} has no singleton version row")
    return int(row[0])


def _corpus_id(connection: sqlite3.Connection, requested: int | None) -> int:
    try:
        if requested is None:
            rows = connection.execute("SELECT corpus_id FROM corpus ORDER BY corpus_id").fetchall()
            if len(rows) != 1:
                raise ClassificationError(
                    "one accepted corpus is required when corpus_id is not supplied"
                )
            requested = int(rows[0][0])
        exists = connection.execute(
            "SELECT 1 FROM corpus WHERE corpus_id = ?", (requested,)
        ).fetchone()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted corpus metadata is unavailable") from error
    if exists is None:
        raise ClassificationError(f"accepted corpus {requested} is missing")
    return int(requested)


def _accepted_context(
    connection: sqlite3.Connection, requested_corpus_id: int | None
) -> tuple[str, int, int, int]:
    """Validate the accepted S1/S2/corpus boundary and return its identities."""

    connection.execute("PRAGMA foreign_keys = ON")
    try:
        catalog_state = connection.execute(
            "SELECT accepted_manifest_hash, accepted_schema_version, record_count "
            "FROM opening_catalog_state WHERE id = 1"
        ).fetchone()
        relationship_state = connection.execute(
            "SELECT accepted_manifest_hash, accepted_schema_version, record_count, "
            "position_count, membership_count, parent_link_count, transposition_link_count "
            "FROM opening_relationship_state"
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted S1/S2 state is unavailable") from error
    if catalog_state is None:
        raise ClassificationError("an accepted S1 catalog is required")
    manifest_hash = str(catalog_state[0])
    catalog_schema_version = _version(connection, "opening_catalog_schema")
    if (
        catalog_schema_version != CATALOG_SCHEMA_VERSION
        or int(catalog_state[1]) != CATALOG_SCHEMA_VERSION
    ):
        raise ClassificationError("accepted S1 catalog schema version is incompatible")
    matching_relationships = [row for row in relationship_state if row[0] == manifest_hash]
    if len(matching_relationships) != 1:
        raise ClassificationError(
            "an accepted S2 relationship state for the S1 manifest is required"
        )
    relationship = matching_relationships[0]
    relationship_schema_version = _version(connection, "opening_relationship_schema")
    if (
        relationship_schema_version != RELATIONSHIP_SCHEMA_VERSION
        or int(relationship[1]) != RELATIONSHIP_SCHEMA_VERSION
    ):
        raise ClassificationError("accepted S2 relationship schema version is incompatible")
    corpus_id = _corpus_id(connection, requested_corpus_id)
    if _version(connection, "corpus_schema") != CORPUS_SCHEMA_VERSION:
        raise ClassificationError("accepted corpus schema version is incompatible")

    try:
        catalog_count = connection.execute(
            "SELECT COUNT(*) FROM opening_catalog WHERE manifest_hash = ?", (manifest_hash,)
        ).fetchone()[0]
        if catalog_count != int(catalog_state[2]) or catalog_count != int(relationship[2]):
            raise ClassificationError("accepted S1/S2 catalog record counts are inconsistent")
        relationship_counts = (
            connection.execute(
                "SELECT COUNT(*) FROM opening_relationship_position WHERE manifest_hash = ?",
                (manifest_hash,),
            ).fetchone()[0],
            connection.execute(
                "SELECT COUNT(*) FROM opening_position_membership WHERE manifest_hash = ?",
                (manifest_hash,),
            ).fetchone()[0],
            connection.execute(
                "SELECT COUNT(*) FROM opening_parent_link WHERE manifest_hash = ?", (manifest_hash,)
            ).fetchone()[0],
            connection.execute(
                "SELECT COUNT(*) FROM opening_transposition_link WHERE manifest_hash = ?",
                (manifest_hash,),
            ).fetchone()[0],
        )
    except sqlite3.Error as error:
        raise _query_error(error, "accepted S2 facts are unavailable") from error
    if relationship_counts != tuple(int(value) for value in relationship[3:]):
        raise ClassificationError("accepted S2 relationship counts are inconsistent")
    return manifest_hash, corpus_id, catalog_schema_version, relationship_schema_version


def _catalog_endpoints(
    connection: sqlite3.Connection, manifest_hash: str
) -> tuple[_CatalogEndpoint, ...]:
    try:
        rows = connection.execute(
            "SELECT source_file, source_row_ordinal, endpoint_placement, "
            "endpoint_side_to_move, endpoint_castling, endpoint_en_passant "
            "FROM opening_catalog WHERE manifest_hash = ? "
            "ORDER BY source_file, source_row_ordinal",
            (manifest_hash,),
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted S1 catalog rows are unavailable") from error
    return tuple(_CatalogEndpoint(row[0], int(row[1]), tuple(row[2:6])) for row in rows)  # type: ignore[arg-type]


def _validate_s2_endpoint_memberships(
    connection: sqlite3.Connection,
    manifest_hash: str,
    catalog: tuple[_CatalogEndpoint, ...],
) -> None:
    try:
        rows = connection.execute(
            "SELECT source_file, source_row_ordinal, ply, placement, side_to_move, castling, "
            "en_passant FROM opening_position_membership WHERE manifest_hash = ? "
            "ORDER BY source_file, source_row_ordinal, ply",
            (manifest_hash,),
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted S2 memberships are unavailable") from error
    by_source: defaultdict[tuple[str, int], list[tuple[int, PositionKey]]] = defaultdict(list)
    for row in rows:
        by_source[(row[0], int(row[1]))].append((int(row[2]), tuple(row[3:7])))  # type: ignore[arg-type]
    for endpoint in catalog:
        memberships = by_source[(endpoint.source_file, endpoint.source_row_ordinal)]
        if not memberships:
            raise ClassificationError("accepted S2 membership is missing for an S1 catalog row")
        final_ply, final_key = memberships[-1]
        if final_key != endpoint.key:
            raise ClassificationError(
                f"S2 membership endpoint differs for {endpoint.source_file} row "
                f"{endpoint.source_row_ordinal} at ply {final_ply}"
            )


def _game_occurrences(
    connection: sqlite3.Connection, corpus_id: int, game_uuid: str
) -> tuple[_Occurrence, ...]:
    try:
        rows = connection.execute(
            "SELECT o.ply, s.placement, s.side_to_move, s.castling, s.en_passant, "
            "o.san, o.uci, o.halfmove_clock, o.fullmove_number "
            "FROM position_occurrence AS o JOIN position_state AS s ON s.state_id = o.state_id "
            "JOIN corpus_game AS cg ON cg.game_uuid = o.game_uuid "
            "WHERE cg.corpus_id = ? AND o.game_uuid = ? ORDER BY o.ply",
            (corpus_id, game_uuid),
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(
            error, f"accepted occurrences for game {game_uuid!r} are unavailable"
        ) from error
    try:
        raw_count = connection.execute(
            "SELECT COUNT(*) FROM position_occurrence WHERE game_uuid = ?", (game_uuid,)
        ).fetchone()[0]
    except sqlite3.Error as error:
        raise _query_error(
            error, f"raw occurrence coverage for game {game_uuid!r} is unavailable"
        ) from error
    if raw_count != len(rows):
        raise ClassificationError(f"accepted game {game_uuid!r} has an unresolved state reference")
    if not rows:
        raise ClassificationError(f"accepted game {game_uuid!r} has no position occurrences")
    plies = tuple(int(row[0]) for row in rows)
    first_ply = plies[0]
    if first_ply not in (0, 1) or plies != tuple(range(first_ply, plies[-1] + 1)) or plies[-1] < 1:
        raise ClassificationError(f"accepted game {game_uuid!r} has incomplete ordered occurrences")
    occurrences = tuple(
        _Occurrence(
            game_uuid,
            int(row[0]),
            tuple(row[1:5]),  # type: ignore[arg-type]
            row[5],
            row[6],
            int(row[7]),
            int(row[8]),
        )
        for row in rows
    )
    if any(any(value is None for value in item.key) for item in occurrences):
        raise ClassificationError(f"accepted game {game_uuid!r} has an incomplete position key")
    if any(item.ply > 0 and (item.san is None or item.uci is None) for item in occurrences):
        raise ClassificationError(f"accepted game {game_uuid!r} has missing move provenance")
    return occurrences


def derive_classification(
    connection: sqlite3.Connection, corpus_id: int | None = None
) -> ClassificationFacts:
    """Derive every exact endpoint anchor and inclusive route from accepted rows."""

    manifest_hash, accepted_corpus_id, catalog_version, relationship_version = _accepted_context(
        connection, corpus_id
    )
    catalog = _catalog_endpoints(connection, manifest_hash)
    _validate_s2_endpoint_memberships(connection, manifest_hash, catalog)
    endpoints: defaultdict[PositionKey, list[_CatalogEndpoint]] = defaultdict(list)
    for item in catalog:
        endpoints[item.key].append(item)

    try:
        game_rows = connection.execute(
            "SELECT game_uuid, fingerprint FROM corpus_game WHERE corpus_id = ? ORDER BY game_uuid",
            (accepted_corpus_id,),
        ).fetchall()
    except sqlite3.Error as error:
        raise _query_error(error, "accepted corpus games are unavailable") from error
    games = tuple(ClassificationGameFact(row[0], row[1]) for row in game_rows)
    anchors: list[ClassificationAnchorFact] = []
    routes: list[ClassificationRouteFact] = []
    for game in games:
        occurrences = _game_occurrences(connection, accepted_corpus_id, game.game_uuid)
        for occurrence_index, occurrence in enumerate(occurrences):
            if occurrence.ply == 0:
                continue
            for endpoint in endpoints[occurrence.key]:
                anchor = ClassificationAnchorFact(
                    game.game_uuid,
                    occurrence.ply,
                    endpoint.source_file,
                    endpoint.source_row_ordinal,
                    *occurrence.key,
                    occurrence.san,  # type: ignore[arg-type]
                    occurrence.uci,  # type: ignore[arg-type]
                )
                anchors.append(anchor)
                routes.extend(
                    ClassificationRouteFact(
                        game.game_uuid,
                        occurrence.ply,
                        endpoint.source_file,
                        endpoint.source_row_ordinal,
                        route.ply,
                        *route.key,
                        route.san,  # type: ignore[arg-type]
                        route.uci,  # type: ignore[arg-type]
                        route.halfmove_clock,
                        route.fullmove_number,
                    )
                    for route in occurrences[occurrence_index:]
                )
    return ClassificationFacts(
        manifest_hash,
        accepted_corpus_id,
        CLASSIFICATION_SCHEMA_VERSION,
        catalog_version,
        relationship_version,
        games,
        tuple(anchors),
        tuple(routes),
    )


GameFact = ClassificationGameFact
AnchorFact = ClassificationAnchorFact
RouteFact = ClassificationRouteFact
derive_classifications = derive_classification
