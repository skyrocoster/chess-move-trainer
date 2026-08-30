"""Stable transport identities and transposition presentation rules.

This module contains no database access.  It only turns accepted composite
opening identities and already-derived transposition facts into stable opaque
transport identifiers and deterministic presentation instructions.
"""

from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass

from backend.app.features.positions.repository import SUBJECT_PLAYER_UUID

APPEARS_IN_MY_GAMES_FILTER_KEY = "appears_in_my_games"
FIXED_CORPUS_SUBJECT_PLAYER_UUID = SUBJECT_PLAYER_UUID


def _require_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


@dataclass(frozen=True, order=True)
class CatalogIdentity:
    """The accepted opening row identity; no surrogate or SQLite rowid."""

    manifest_hash: str
    source_file: str
    source_row_ordinal: int

    def __post_init__(self) -> None:
        _require_text(self.manifest_hash, "manifest_hash")
        _require_text(self.source_file, "source_file")
        if (
            isinstance(self.source_row_ordinal, bool)
            or not isinstance(self.source_row_ordinal, int)
            or self.source_row_ordinal <= 0
        ):
            raise ValueError("source_row_ordinal must be a positive integer")


@dataclass(frozen=True, order=True)
class PositionIdentity:
    """The established exact four-field chess position identity."""

    placement: str
    side_to_move: str
    castling: str
    en_passant: str

    def __post_init__(self) -> None:
        _require_text(self.placement, "placement")
        if self.side_to_move not in {"w", "b"}:
            raise ValueError("side_to_move must be 'w' or 'b'")
        _require_text(self.castling, "castling")
        _require_text(self.en_passant, "en_passant")


@dataclass(frozen=True, order=True)
class TranspositionAppearance:
    """One accepted source-row appearance in an existing transposition link."""

    identity: CatalogIdentity
    position: PositionIdentity
    ply: int
    uci_prefix: str

    def __post_init__(self) -> None:
        if isinstance(self.ply, bool) or not isinstance(self.ply, int) or self.ply <= 0:
            raise ValueError("ply must be a positive integer")
        _require_text(self.uci_prefix, "uci_prefix")


@dataclass(frozen=True)
class TranspositionLink:
    """A pair copied from an accepted opening_transposition_link row."""

    first: TranspositionAppearance
    second: TranspositionAppearance

    def __post_init__(self) -> None:
        if self.first.identity.manifest_hash != self.second.identity.manifest_hash:
            raise ValueError("transposition endpoints must share a manifest")
        if self.first.position != self.second.position:
            raise ValueError("transposition endpoints must share a position")
        if self.first == self.second:
            raise ValueError("transposition endpoints must be distinct")
        if self.first.uci_prefix == self.second.uci_prefix:
            raise ValueError("transposition endpoints must have different UCI prefixes")


@dataclass(frozen=True)
class TranspositionReference:
    """A non-selectable appearance pointing at one canonical line node."""

    node_id: str
    appearance: TranspositionAppearance
    target_id: str


@dataclass(frozen=True)
class TranspositionPresentation:
    """Deterministic canonical appearance and reference instructions."""

    canonical_by_identity: tuple[tuple[CatalogIdentity, TranspositionAppearance], ...]
    references: tuple[TranspositionReference, ...]


def _encoded(parts: list[object]) -> str:
    payload = json.dumps(parts, ensure_ascii=True, separators=(",", ":"))
    token = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")
    return f"ol1_{token}"


def _decoded(value: str) -> list[object]:
    if not isinstance(value, str) or not value.startswith("ol1_"):
        raise ValueError("invalid opening Line Library ID")
    token = value[4:]
    if not token:
        raise ValueError("invalid opening Line Library ID")
    try:
        padded = token + "=" * (-len(token) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
        parts = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError) as error:
        raise ValueError("invalid opening Line Library ID") from error
    if not isinstance(parts, list):
        raise ValueError("invalid opening Line Library ID")
    return parts


def encode_catalog_node_id(identity: CatalogIdentity) -> str:
    """Encode one accepted catalog identity as an opaque stable node ID."""

    return _encoded(
        ["catalog", identity.manifest_hash, identity.source_file, identity.source_row_ordinal]
    )


def decode_catalog_node_id(value: str) -> CatalogIdentity:
    """Decode a backend ID for contract tests and backend-side joins."""

    parts = _decoded(value)
    if len(parts) != 4 or parts[0] != "catalog":
        raise ValueError("not a catalog node ID")
    return CatalogIdentity(
        manifest_hash=parts[1],
        source_file=parts[2],
        source_row_ordinal=parts[3],
    )


def encode_reference_node_id(
    appearance: TranspositionAppearance,
    target_id: str,
) -> str:
    """Encode one non-canonical appearance without creating a selectable ID."""

    _require_text(target_id, "target_id")
    return _encoded(
        [
            "reference",
            appearance.identity.manifest_hash,
            appearance.identity.source_file,
            appearance.identity.source_row_ordinal,
            appearance.position.placement,
            appearance.position.side_to_move,
            appearance.position.castling,
            appearance.position.en_passant,
            appearance.ply,
            appearance.uci_prefix,
            target_id,
        ]
    )


def _appearance_key(appearance: TranspositionAppearance) -> tuple[object, ...]:
    return (
        appearance.ply,
        appearance.uci_prefix,
        appearance.position.placement,
        appearance.position.side_to_move,
        appearance.position.castling,
        appearance.position.en_passant,
    )


def canonical_transposition_presentation(
    links: tuple[TranspositionLink, ...] | list[TranspositionLink],
) -> TranspositionPresentation:
    """Choose one location per source identity and reference other appearances.

    The input is authoritative.  This function emits no new relationship.  For
    each source-row identity appearing in accepted transposition links, the
    lexicographically smallest existing appearance by ply, UCI prefix, and
    exact position is its sole canonical location.  Every other existing
    appearance becomes a reference to that source-row's one catalog node.
    """

    appearances: dict[CatalogIdentity, set[TranspositionAppearance]] = {}
    for link in links:
        for appearance in (link.first, link.second):
            appearances.setdefault(appearance.identity, set()).add(appearance)

    canonical_by_identity = tuple(
        (identity, min(values, key=_appearance_key))
        for identity, values in sorted(appearances.items())
    )
    canonical_lookup = dict(canonical_by_identity)

    references_by_key: dict[tuple[object, ...], TranspositionReference] = {}
    for identity, values in sorted(appearances.items()):
        target_id = encode_catalog_node_id(identity)
        canonical = canonical_lookup[identity]
        for appearance in sorted(values):
            if appearance == canonical:
                continue
            node_id = encode_reference_node_id(appearance, target_id)
            key = (node_id, target_id)
            references_by_key[key] = TranspositionReference(
                node_id=node_id,
                appearance=appearance,
                target_id=target_id,
            )

    references = tuple(
        references_by_key[key] for key in sorted(references_by_key, key=lambda item: item[0])
    )
    return TranspositionPresentation(
        canonical_by_identity=canonical_by_identity,
        references=references,
    )
