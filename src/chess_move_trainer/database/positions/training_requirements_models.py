"""Validated models for read-only position training requirements."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

import chess

from ..openings.keys import parse_opening_api_key

TrainerColor = Literal["white", "black"]
OpeningMatch = Literal["reached", "deepest"]


class TrainingRequirementError(Exception):
    """Base class for bounded training-requirement failures."""


class TrainingRequirementValidationError(TrainingRequirementError, ValueError):
    """Raised when a policy or discovery request is invalid."""


class TrainingRequirementSchemaError(TrainingRequirementError, RuntimeError):
    """Raised when the selected database is not the exact supported schema."""


class TrainingRequirementStorageError(TrainingRequirementError, RuntimeError):
    """Raised when a compatible database contains unusable training data."""


class TrainingRequirementStaleError(TrainingRequirementError, RuntimeError):
    """Raised when persisted training state is newer than the requested date."""


@dataclass(frozen=True, slots=True)
class TrainingRequirementPolicy:
    """Immutable scoring inputs supplied by application configuration."""

    target_success_rate: float
    credit_half_life_days: float

    def __post_init__(self) -> None:
        target = _finite_number(self.target_success_rate, "target_success_rate")
        half_life = _finite_number(self.credit_half_life_days, "credit_half_life_days")
        if not 0.5 < target < 1.0:
            raise TrainingRequirementValidationError(
                "target_success_rate must be greater than 0.5 and less than 1"
            )
        if half_life <= 0:
            raise TrainingRequirementValidationError(
                "credit_half_life_days must be greater than zero"
            )
        object.__setattr__(self, "target_success_rate", target)
        object.__setattr__(self, "credit_half_life_days", half_life)

    @property
    def game_hit_weight(self) -> float:
        return 1.0

    @property
    def game_miss_weight(self) -> float:
        return float(
            Decimal(str(self.target_success_rate))
            / (Decimal("1") - Decimal(str(self.target_success_rate)))
        )

    @property
    def training_curve(self) -> str:
        return "squared"

    @property
    def training_credit_half_life_days(self) -> float:
        return self.credit_half_life_days


ScoringPolicy = TrainingRequirementPolicy
TrainingRequirementScoringPolicy = TrainingRequirementPolicy
TrainingScoringPolicy = TrainingRequirementPolicy


@dataclass(frozen=True, slots=True)
class TrainingRequirementRange:
    """A normalized inclusive/exclusive requirement range."""

    lower: float | None = None
    lower_inclusive: bool = True
    upper: float | None = None
    upper_inclusive: bool = True

    def contains(self, value: float) -> bool:
        if self.lower is not None and (
            value < self.lower or (not self.lower_inclusive and value == self.lower)
        ):
            return False
        if self.upper is not None and (
            value > self.upper or (not self.upper_inclusive and value == self.upper)
        ):
            return False
        return True


@dataclass(frozen=True, slots=True)
class TrainingRequirementQuery:
    """Validated read-only discovery controls."""

    as_of: str
    training_requirement_gt: float | None = None
    training_requirement_gte: float | None = None
    training_requirement_lt: float | None = None
    training_requirement_lte: float | None = None
    opening_key: str | None = None
    opening_match: OpeningMatch | None = None
    page: int = 1
    page_size: int = 50
    trainer_color: TrainerColor | None = None

    def __post_init__(self) -> None:
        parsed_as_of = _parse_date(self.as_of, "as_of")
        object.__setattr__(self, "as_of", parsed_as_of.isoformat())

        boundaries = {
            "training_requirement_gt": self.training_requirement_gt,
            "training_requirement_gte": self.training_requirement_gte,
            "training_requirement_lt": self.training_requirement_lt,
            "training_requirement_lte": self.training_requirement_lte,
        }
        normalized: dict[str, float | None] = {}
        for name, value in boundaries.items():
            normalized[name] = None if value is None else _finite_number(value, name)
            object.__setattr__(self, name, normalized[name])
        if not any(value is not None for value in normalized.values()):
            raise TrainingRequirementValidationError(
                "at least one training-requirement boundary is required"
            )

        range_ = _normalize_range(normalized)
        if range_.lower is not None and range_.upper is not None:
            if range_.lower > range_.upper or (
                range_.lower == range_.upper
                and not (range_.lower_inclusive and range_.upper_inclusive)
            ):
                raise TrainingRequirementValidationError(
                    "training-requirement boundaries describe an empty range"
                )

        if self.opening_key is None and self.opening_match is not None:
            raise TrainingRequirementValidationError("opening_match requires opening_key")
        if self.opening_key is not None and self.opening_match is None:
            raise TrainingRequirementValidationError("opening_key requires opening_match")
        if self.opening_key is not None:
            if not isinstance(self.opening_key, str):
                raise TrainingRequirementValidationError("opening_key is invalid")
            try:
                parse_opening_api_key(self.opening_key)
            except (TypeError, ValueError) as error:
                raise TrainingRequirementValidationError("opening_key is invalid") from error
        if self.opening_match not in (None, "reached", "deepest"):
            raise TrainingRequirementValidationError("opening_match must be 'reached' or 'deepest'")
        if self.trainer_color not in (None, "white", "black"):
            raise TrainingRequirementValidationError("trainer_color must be 'white' or 'black'")

        if type(self.page) is not int or self.page < 1:
            raise TrainingRequirementValidationError("page must be a positive integer")
        if type(self.page_size) is not int or not 1 <= self.page_size <= 100:
            raise TrainingRequirementValidationError(
                "page_size must be an integer between 1 and 100"
            )

    @property
    def requirement_range(self) -> TrainingRequirementRange:
        return _normalize_range(
            {
                "training_requirement_gt": self.training_requirement_gt,
                "training_requirement_gte": self.training_requirement_gte,
                "training_requirement_lt": self.training_requirement_lt,
                "training_requirement_lte": self.training_requirement_lte,
            }
        )


TrainingRequirementDiscoveryQuery = TrainingRequirementQuery


@dataclass(frozen=True, slots=True)
class TrainingRequirementItem:
    """One globally scored canonical-position/preferred-move pair."""

    fen: str
    trainer_color: TrainerColor
    preferred_move_uci: str
    encounters: int
    hits: int
    misses: int
    observed_success_rate: float
    game_balance: float
    effective_training_balance: float
    training_adjustment: float
    training_updated_on: str | None
    training_requirement: float
    training_required: bool
    correct_answers_needed: int

    def public_dict(self) -> dict[str, object]:
        """Return the compact adapter-ready shape with six-decimal derived numbers."""

        return {
            "fen": self.fen,
            "trainer_color": self.trainer_color,
            "preferred_move_uci": self.preferred_move_uci,
            "encounters": self.encounters,
            "hits": self.hits,
            "misses": self.misses,
            "observed_success_rate": _round_public(self.observed_success_rate),
            "game_balance": _round_public(self.game_balance),
            "effective_training_balance": _round_public(self.effective_training_balance),
            "training_adjustment": _round_public(self.training_adjustment),
            "training_updated_on": self.training_updated_on,
            "training_requirement": _round_public(self.training_requirement),
            "training_required": self.training_required,
            "correct_answers_needed": self.correct_answers_needed,
        }


@dataclass(frozen=True, slots=True)
class TrainingRequirementPage:
    """One deterministic page of scored training requirements."""

    as_of: str
    scoring_policy: TrainingRequirementPolicy
    items: tuple[TrainingRequirementItem, ...]
    page: int
    page_size: int
    total: int

    @property
    def total_count(self) -> int:
        return self.total

    def public_dict(self) -> dict[str, object]:
        return {
            "as_of": self.as_of,
            "scoring_policy": {
                "target_success_rate": _round_public(self.scoring_policy.target_success_rate),
                "game_hit_weight": _round_public(self.scoring_policy.game_hit_weight),
                "game_miss_weight": _round_public(self.scoring_policy.game_miss_weight),
                "training_curve": self.scoring_policy.training_curve,
                "training_credit_half_life_days": _round_public(
                    self.scoring_policy.credit_half_life_days
                ),
            },
            "items": [item.public_dict() for item in self.items],
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
        }


def parse_calendar_date(value: object, name: str) -> date:
    """Parse one strict calendar-date value for scoring and storage checks."""

    return _parse_date(value, name)


def _parse_date(value: object, name: str) -> date:
    if not isinstance(value, str):
        raise TrainingRequirementValidationError(f"{name} must be a literal YYYY-MM-DD date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise TrainingRequirementValidationError(
            f"{name} must be a literal YYYY-MM-DD date"
        ) from error
    if parsed.isoformat() != value:
        raise TrainingRequirementValidationError(f"{name} must be a literal YYYY-MM-DD date")
    return parsed


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise TrainingRequirementValidationError(f"{name} must be finite")
    try:
        normalized = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise TrainingRequirementValidationError(f"{name} must be finite") from error
    if not math.isfinite(normalized):
        raise TrainingRequirementValidationError(f"{name} must be finite")
    return normalized


def _normalize_range(boundaries: dict[str, float | None]) -> TrainingRequirementRange:
    lower_candidates: list[tuple[float, bool]] = []
    if boundaries["training_requirement_gt"] is not None:
        lower_candidates.append((boundaries["training_requirement_gt"], False))
    if boundaries["training_requirement_gte"] is not None:
        lower_candidates.append((boundaries["training_requirement_gte"], True))
    upper_candidates: list[tuple[float, bool]] = []
    if boundaries["training_requirement_lt"] is not None:
        upper_candidates.append((boundaries["training_requirement_lt"], False))
    if boundaries["training_requirement_lte"] is not None:
        upper_candidates.append((boundaries["training_requirement_lte"], True))

    lower = None
    lower_inclusive = True
    if lower_candidates:
        lower = max(value for value, _inclusive in lower_candidates)
        lower_inclusive = all(inclusive for value, inclusive in lower_candidates if value == lower)
    upper = None
    upper_inclusive = True
    if upper_candidates:
        upper = min(value for value, _inclusive in upper_candidates)
        upper_inclusive = all(inclusive for value, inclusive in upper_candidates if value == upper)
    return TrainingRequirementRange(lower, lower_inclusive, upper, upper_inclusive)


def _round_public(value: float) -> float:
    return round(value, 6)


def validate_uci(value: object, name: str = "move_uci") -> str:
    if not isinstance(value, str):
        raise TrainingRequirementStorageError(f"{name} is malformed")
    try:
        move = chess.Move.from_uci(value)
    except (TypeError, ValueError) as error:
        raise TrainingRequirementStorageError(f"{name} is malformed") from error
    if move.uci() != value:
        raise TrainingRequirementStorageError(f"{name} is not canonical")
    return value
