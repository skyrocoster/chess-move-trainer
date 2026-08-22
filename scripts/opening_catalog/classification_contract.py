"""Identity and route contracts for neutral opening classification.

This module contains only the settled S3 value contracts. Derivation and publication
belong to later Plan stages.
"""

from __future__ import annotations

from dataclasses import dataclass

PositionKey = tuple[str, str, str, str]
CatalogIdentity = tuple[str, str, int]
GameOccurrenceIdentity = tuple[int, str, int]

CATALOG_IDENTITY_FIELDS = ("manifest_hash", "source_file", "source_row_ordinal")
GAME_OCCURRENCE_IDENTITY_FIELDS = ("corpus_id", "game_uuid", "ply")


@dataclass(frozen=True)
class AnchorIdentity:
    """One catalog membership reached at one accepted game occurrence."""

    catalog: CatalogIdentity
    occurrence: GameOccurrenceIdentity


def exact_endpoint_match(catalog_key: PositionKey, occurrence_key: PositionKey) -> bool:
    """Return whether a game occurrence exactly reaches a catalog endpoint."""

    return catalog_key == occurrence_key


def suffix_plies(anchor_ply: int, final_ply: int) -> tuple[int, ...]:
    """Return the inclusive observed route suffix from anchor through game end."""

    if anchor_ply < 1:
        raise ValueError("an opening endpoint anchor must be after the initial position")
    if final_ply < anchor_ply:
        raise ValueError("the accepted final occurrence cannot precede the anchor")
    return tuple(range(anchor_ply, final_ply + 1))


def validate_route_plies(anchor_ply: int, final_ply: int, route_plies: tuple[int, ...]) -> None:
    """Reject a route that omits, reorders, or adds occurrences in the observed suffix."""

    expected = suffix_plies(anchor_ply, final_ply)
    if route_plies != expected:
        raise ValueError(f"route plies {route_plies!r} do not equal expected suffix {expected!r}")
