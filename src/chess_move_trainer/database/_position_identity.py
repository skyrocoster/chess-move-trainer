"""Dependency-neutral immutable value for canonical position identity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CanonicalPosition:
    """The four-field immutable identity used by the app database."""

    placement: str
    side_to_move: str
    castling_rights: str
    legal_en_passant: str
