"""Validated blunder discovery query, policy, item, and page models."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from ..validation import normalize_timestamp_value
from .errors import BlunderValidationError

TrainerColor = Literal["white", "black"]


def _normalize_timestamp(value: str | datetime | None, field_name: str) -> str:
    """Normalize one mandatory RFC3339 bound to UTC exactly as game search does."""

    try:
        return normalize_timestamp_value(value, field_name)
    except ValueError as error:
        raise BlunderValidationError(str(error)) from error


@dataclass(frozen=True, slots=True)
class BlunderQuery:
    """Mandatory inclusive timeframe, optional trainer color, and pagination."""

    started_at_from: str | datetime
    started_at_to: str | datetime
    trainer_color: TrainerColor | None = None
    page: int = 1
    page_size: int = 50

    def __post_init__(self) -> None:
        if type(self.page) is not int or self.page < 1:
            raise BlunderValidationError("page must be a positive integer")
        if type(self.page_size) is not int or not 1 <= self.page_size <= 100:
            raise BlunderValidationError("page_size must be an integer from 1 through 100")
        if self.trainer_color is not None and self.trainer_color not in ("white", "black"):
            raise BlunderValidationError("trainer_color has an unsupported value")
        normalized_from = _normalize_timestamp(self.started_at_from, "started_at_from")
        normalized_to = _normalize_timestamp(self.started_at_to, "started_at_to")
        if normalized_from > normalized_to:
            raise BlunderValidationError("started_at lower bound cannot exceed upper bound")
        object.__setattr__(self, "started_at_from", normalized_from)
        object.__setattr__(self, "started_at_to", normalized_to)


@dataclass(frozen=True, slots=True)
class BlunderPolicy:
    """Caller-supplied blunder threshold with no hard-coded default in this domain."""

    minimum_expected_score_loss: float

    def __post_init__(self) -> None:
        value = self.minimum_expected_score_loss
        if isinstance(value, bool):
            raise BlunderValidationError(
                "minimum_expected_score_loss must be finite and within (0, 1]"
            )
        try:
            normalized = float(value)
        except (TypeError, ValueError, OverflowError) as error:
            raise BlunderValidationError(
                "minimum_expected_score_loss must be finite and within (0, 1]"
            ) from error
        if not math.isfinite(normalized) or not 0 < normalized <= 1:
            raise BlunderValidationError(
                "minimum_expected_score_loss must be finite and within (0, 1]"
            )
        object.__setattr__(self, "minimum_expected_score_loss", normalized)


@dataclass(frozen=True, slots=True)
class BlunderItem:
    """One public trainer blunder occurrence without SQLite identifiers."""

    game_uuid: str
    source_url: str
    started_at_utc: str
    trainer_color: TrainerColor
    ply: int
    fen: str
    played_move_uci: str
    preferred_move_uci: str
    expected_score_before: float
    expected_score_after: float
    expected_score_loss: float
    before_analysis_quality: str
    after_analysis_quality: str


@dataclass(frozen=True, slots=True)
class BlunderPage:
    """One finite, deterministic page of trainer blunders with coverage counts.

    Counting is precise and non-overlapping: every candidate trainer move is
    either comparable or skipped, so ``comparable_move_count`` plus
    ``skipped_missing_analysis_count`` always equals ``trainer_move_count``.
    Games whose stored start timestamp is missing or malformed are excluded
    before move counting and tallied separately in ``excluded_game_count``.
    """

    started_at_from: str
    started_at_to: str
    policy: BlunderPolicy
    items: tuple[BlunderItem, ...]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    trainer_move_count: int
    comparable_move_count: int
    skipped_missing_analysis_count: int
    examined_game_count: int
    excluded_game_count: int
    in_scope_game_count: int


def _round_public(value: float) -> float:
    """Round one exposed float deterministically to six places."""

    return round(value, 6)


__all__ = [
    "BlunderItem",
    "BlunderPage",
    "BlunderPolicy",
    "BlunderQuery",
    "TrainerColor",
]
