"""Settled S4 identities and value contracts.

This module deliberately contains no derivation, counting formula, threshold, or
player policy.  It names the natural keys that later stages will use when they
copy accepted S3 and corpus facts into the additive recurrence namespace.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .classification_contract import CatalogIdentity, PositionKey

RECURRENCE_GAME_IDENTITY_FIELDS = ("corpus_id", "game_uuid")
RECURRENCE_OCCURRENCE_IDENTITY_FIELDS = ("corpus_id", "game_uuid", "ply")
RECURRENCE_ROUTE_IDENTITY_FIELDS = (
    "corpus_id",
    "game_uuid",
    "anchor_ply",
    "source_file",
    "source_row_ordinal",
    "route_ply",
)
RECURRENCE_BRANCH_IDENTITY_FIELDS = (
    "corpus_id",
    "game_uuid",
    "parent_ply",
    "branch_kind",
)

COLOR_SCOPES = ("overall", "white", "black")
GAME_COLORS = ("white", "black")
BRANCH_KINDS = ("move", "terminal")

GameIdentity = tuple[int, str]
OccurrenceIdentity = tuple[int, str, int]
RouteIdentity = tuple[int, str, int, str, int, int]
BranchIdentity = tuple[int, str, int, str]


@dataclass(frozen=True)
class RecurrenceGameFact:
    """One accepted game and neutral source context needed by projections."""

    manifest_hash: str
    corpus_id: int
    game_uuid: str
    source_fingerprint: str
    metadata_fingerprint: str
    game_sequence: int
    end_time: int | None
    year: int | None
    month: int | None
    time_control: str | None
    time_class: str | None
    white_rating: int | None
    black_rating: int | None
    white_result: str | None
    black_result: str | None
    game_color: str = "white"

    @property
    def color(self) -> str:
        """Return the source game's color context without retaining player identity."""

        return self.game_color


@dataclass(frozen=True)
class RecurrenceOccurrenceFact:
    """One raw accepted corpus occurrence, including the exact four-field key."""

    manifest_hash: str
    corpus_id: int
    game_uuid: str
    ply: int
    key: PositionKey
    san: str | None
    uci: str | None
    halfmove_clock: int
    fullmove_number: int


@dataclass(frozen=True)
class RecurrenceRouteFact:
    """One S3 route membership occurrence; memberships are never collapsed."""

    manifest_hash: str
    corpus_id: int
    game_uuid: str
    anchor_ply: int
    catalog: CatalogIdentity
    route_ply: int
    key: PositionKey
    san: str
    uci: str
    halfmove_clock: int
    fullmove_number: int


@dataclass(frozen=True)
class RecurrenceBranchFact:
    """One parent occurrence continuation or terminal observation."""

    manifest_hash: str
    corpus_id: int
    game_uuid: str
    parent_ply: int
    parent_key: PositionKey
    branch_kind: str
    child_ply: int
    child_key: PositionKey | None
    child_san: str | None
    child_uci: str | None
    terminal_outcome: str | None


def occurrence_identity(corpus_id: int, game_uuid: str, ply: int) -> OccurrenceIdentity:
    """Return the natural corpus game/ply identity; no SQLite row identifier is involved."""

    if ply < 0:
        raise ValueError("a corpus occurrence ply cannot be negative")
    return corpus_id, game_uuid, ply


def game_identity(corpus_id: int, game_uuid: str) -> GameIdentity:
    """Return the natural corpus game identity; no player identity is involved."""

    return corpus_id, game_uuid


def route_identity(
    corpus_id: int,
    game_uuid: str,
    anchor_ply: int,
    source_file: str,
    source_row_ordinal: int,
    route_ply: int,
) -> RouteIdentity:
    """Return the S3 membership-inclusive route occurrence identity."""

    if anchor_ply < 1 or route_ply < anchor_ply:
        raise ValueError("a route occurrence must be at or after its positive anchor ply")
    if source_row_ordinal < 1:
        raise ValueError("a catalog source row ordinal must be positive")
    return corpus_id, game_uuid, anchor_ply, source_file, source_row_ordinal, route_ply


def branch_identity(
    corpus_id: int, game_uuid: str, parent_ply: int, branch_kind: str
) -> BranchIdentity:
    """Return the natural parent-occurrence plus branch-kind identity."""

    if parent_ply < 0:
        raise ValueError("a branch parent ply cannot be negative")
    if branch_kind not in BRANCH_KINDS:
        raise ValueError(f"unsupported branch kind {branch_kind!r}")
    return corpus_id, game_uuid, parent_ply, branch_kind


def position_projection_key(
    manifest_hash: str, corpus_id: int, key: PositionKey, color_scope: str
) -> tuple[str, int, *tuple[str, str, str, str], str]:
    """Return a deterministic global projection key for one exact state and color scope."""

    _validate_color_scope(color_scope)
    return manifest_hash, corpus_id, *key, color_scope


def route_projection_key(
    manifest_hash: str,
    corpus_id: int,
    catalog: CatalogIdentity,
    anchor_ply: int,
    key: PositionKey,
    color_scope: str,
) -> tuple[str, int, str, int, int, str, str, str, str, str]:
    """Return a deterministic membership-inclusive route projection key."""

    _validate_color_scope(color_scope)
    source_manifest, source_file, source_row_ordinal = catalog
    if source_manifest != manifest_hash:
        raise ValueError("route catalog identity must use the accepted S4 manifest")
    if anchor_ply < 1 or source_row_ordinal < 1:
        raise ValueError("route anchor and catalog row ordinal must be positive")
    return (
        manifest_hash,
        corpus_id,
        source_file,
        anchor_ply,
        source_row_ordinal,
        *key,
        color_scope,
    )


def branch_projection_key(
    manifest_hash: str,
    corpus_id: int,
    parent_key: PositionKey,
    branch_kind: str,
    child_uci: str | None,
    color_scope: str,
) -> tuple[str, int, str, str, str, str, str, str, str]:
    """Return a global parent-state/child-move projection key.

    A terminal branch has no child move.  The projection key uses the empty
    string only in that structural slot; the authoritative event retains the
    nullable child move and terminal outcome without losing either fact.
    """

    if branch_kind not in BRANCH_KINDS:
        raise ValueError(f"unsupported branch kind {branch_kind!r}")
    _validate_color_scope(color_scope)
    if branch_kind == "move" and not child_uci:
        raise ValueError("a move branch projection requires a child UCI move")
    if branch_kind == "terminal" and child_uci is not None:
        raise ValueError("a terminal branch projection cannot have a child UCI move")
    return manifest_hash, corpus_id, *parent_key, branch_kind, child_uci or "", color_scope


def _validate_color_scope(color_scope: str) -> None:
    if color_scope not in COLOR_SCOPES:
        raise ValueError(f"unsupported color scope {color_scope!r}")


@dataclass(frozen=True)
class PositionProjectionFact:
    manifest_hash: str
    corpus_id: int
    key: PositionKey
    color_scope: str
    raw_occurrence_count: int
    distinct_game_count: int
    first_game_sequence: int
    first_game_uuid: str
    first_ply: int
    last_game_sequence: int
    last_game_uuid: str
    last_ply: int


@dataclass(frozen=True)
class RouteProjectionFact:
    manifest_hash: str
    corpus_id: int
    anchor_ply: int
    catalog: CatalogIdentity
    key: PositionKey
    color_scope: str
    raw_occurrence_count: int
    distinct_game_count: int
    first_game_sequence: int
    first_game_uuid: str
    first_route_ply: int
    last_game_sequence: int
    last_game_uuid: str
    last_route_ply: int


@dataclass(frozen=True)
class BranchProjectionFact:
    manifest_hash: str
    corpus_id: int
    parent_key: PositionKey
    branch_kind: str
    child_uci: str
    color_scope: str
    raw_event_count: int
    distinct_game_count: int
    first_game_sequence: int
    first_game_uuid: str
    first_parent_ply: int
    last_game_sequence: int
    last_game_uuid: str
    last_parent_ply: int


@dataclass(frozen=True)
class RouteBranchProjectionFact:
    manifest_hash: str
    corpus_id: int
    anchor_ply: int
    catalog: CatalogIdentity
    parent_key: PositionKey
    branch_kind: str
    child_uci: str
    color_scope: str
    raw_event_count: int
    distinct_game_count: int
    first_game_sequence: int
    first_game_uuid: str
    first_parent_ply: int
    last_game_sequence: int
    last_game_uuid: str
    last_parent_ply: int


@dataclass(frozen=True)
class RecurrenceProjections:
    positions: tuple[PositionProjectionFact, ...]
    routes: tuple[RouteProjectionFact, ...]
    branches: tuple[BranchProjectionFact, ...]
    route_branches: tuple[RouteBranchProjectionFact, ...]


def _projection_scopes(game_color: str) -> tuple[str, ...]:
    return ("overall", game_color)


def _projection_bounds(
    items: list[tuple[int, str, int]],
) -> tuple[int, str, int, int, str, int]:
    ordered = sorted(items)
    return (*ordered[0], *ordered[-1])


def project_recurrence(facts: object) -> RecurrenceProjections:
    """Rebuild projections from an object exposing the authoritative S4 events."""

    games = {item.game_uuid: item for item in facts.games}
    position_groups: defaultdict[tuple[object, ...], list[tuple[int, str, int]]] = defaultdict(list)
    route_groups: defaultdict[tuple[object, ...], list[tuple[int, str, int]]] = defaultdict(list)
    branch_groups: defaultdict[tuple[object, ...], list[tuple[int, str, int]]] = defaultdict(list)
    route_branch_groups: defaultdict[tuple[object, ...], list[tuple[int, str, int]]] = defaultdict(
        list
    )
    branch_by_parent = {(item.game_uuid, item.parent_ply): item for item in facts.branches}
    for item in facts.occurrences:
        game = games[item.game_uuid]
        for scope in _projection_scopes(game.game_color):
            position_groups[(facts.manifest_hash, facts.corpus_id, *item.key, scope)].append(
                (game.game_sequence, item.game_uuid, item.ply)
            )
    for item in facts.routes:
        game = games[item.game_uuid]
        catalog = item.catalog
        for scope in _projection_scopes(game.game_color):
            route_groups[
                (
                    facts.manifest_hash,
                    facts.corpus_id,
                    item.anchor_ply,
                    catalog[1],
                    catalog[2],
                    *item.key,
                    scope,
                )
            ].append((game.game_sequence, item.game_uuid, item.route_ply))
            branch = branch_by_parent[(item.game_uuid, item.route_ply)]
            route_branch_groups[
                (
                    facts.manifest_hash,
                    facts.corpus_id,
                    item.anchor_ply,
                    catalog[1],
                    catalog[2],
                    *branch.parent_key,
                    branch.branch_kind,
                    branch.child_uci or "",
                    scope,
                )
            ].append((game.game_sequence, item.game_uuid, item.route_ply))
    for item in facts.branches:
        game = games[item.game_uuid]
        for scope in _projection_scopes(game.game_color):
            branch_groups[
                (
                    facts.manifest_hash,
                    facts.corpus_id,
                    *item.parent_key,
                    item.branch_kind,
                    item.child_uci or "",
                    scope,
                )
            ].append((game.game_sequence, item.game_uuid, item.parent_ply))

    positions = tuple(
        PositionProjectionFact(
            facts.manifest_hash,
            facts.corpus_id,
            tuple(key[2:6]),  # type: ignore[arg-type]
            key[6],
            len(items),
            len({item[1] for item in items}),
            *_projection_bounds(items),
        )
        for key, items in sorted(position_groups.items())
    )
    routes = tuple(
        RouteProjectionFact(
            facts.manifest_hash,
            facts.corpus_id,
            int(key[2]),
            (facts.manifest_hash, key[3], int(key[4])),
            tuple(key[5:9]),  # type: ignore[arg-type]
            key[9],
            len(items),
            len({item[1] for item in items}),
            *_projection_bounds(items),
        )
        for key, items in sorted(route_groups.items())
    )
    branches = tuple(
        BranchProjectionFact(
            facts.manifest_hash,
            facts.corpus_id,
            tuple(key[2:6]),  # type: ignore[arg-type]
            key[6],
            key[7],
            key[8],
            len(items),
            len({item[1] for item in items}),
            *_projection_bounds(items),
        )
        for key, items in sorted(branch_groups.items())
    )
    route_branches = tuple(
        RouteBranchProjectionFact(
            facts.manifest_hash,
            facts.corpus_id,
            int(key[2]),
            (facts.manifest_hash, key[3], int(key[4])),
            tuple(key[5:9]),  # type: ignore[arg-type]
            key[9],
            key[10],
            key[11],
            len(items),
            len({item[1] for item in items}),
            *_projection_bounds(items),
        )
        for key, items in sorted(route_branch_groups.items())
    )
    return RecurrenceProjections(positions, routes, branches, route_branches)
