"""Pure date-range behavior for the current preferred-move schedule."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Iterable

_DATE_LITERAL = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


class RangeValidationError(ValueError):
    """Raised when a date, range, or normalized schedule is invalid."""


class PreferenceState(Enum):
    """A state that can be stored for a configured period."""

    PREFERRED_MOVE = "preferred_move"
    NO_PREFERENCE = "no_preference"


@dataclass(frozen=True)
class Preference:
    """The immutable value stored in a configured schedule period."""

    state: PreferenceState
    move: str | None

    def __post_init__(self) -> None:
        if self.state is PreferenceState.PREFERRED_MOVE:
            if not isinstance(self.move, str) or not self.move:
                raise RangeValidationError("a preferred-move state requires a move")
        elif self.state is PreferenceState.NO_PREFERENCE:
            if self.move is not None:
                raise RangeValidationError("a no-preference state cannot contain a move")
        else:
            raise RangeValidationError("unknown preference state")

    @classmethod
    def preferred_move(cls, move: str) -> Preference:
        return cls(PreferenceState.PREFERRED_MOVE, move)

    @classmethod
    def no_preference(cls) -> Preference:
        return cls(PreferenceState.NO_PREFERENCE, None)


@dataclass(frozen=True)
class NormalizedPeriod:
    """One configured half-open period in a normalized schedule."""

    effective_from: date
    effective_until: date | None
    preference: Preference

    def __post_init__(self) -> None:
        _require_date(self.effective_from, "effective_from")
        if self.effective_until is not None:
            _require_date(self.effective_until, "effective_until")
            if self.effective_until <= self.effective_from:
                raise RangeValidationError(
                    "effective_until must be later than effective_from"
                )
        if not isinstance(self.preference, Preference):
            raise RangeValidationError("period preference must be a Preference")


class ResolutionState(Enum):
    """Every possible result of resolving a schedule date."""

    PREFERRED_MOVE = "preferred_move"
    NO_PREFERENCE = "no_preference"
    UNCONFIGURED = "unconfigured"


@dataclass(frozen=True)
class DateResolution:
    """The immutable result of resolving one date."""

    state: ResolutionState
    move: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, ResolutionState):
            raise RangeValidationError("unknown resolution state")
        if self.state is ResolutionState.PREFERRED_MOVE:
            if not isinstance(self.move, str) or not self.move:
                raise RangeValidationError("a preferred-move resolution requires a move")
        elif self.move is not None:
            raise RangeValidationError("only preferred-move resolution can contain a move")


def _require_date(value: object, field_name: str) -> date:
    if not isinstance(value, date) or isinstance(value, datetime):
        raise RangeValidationError(f"{field_name} must be a calendar date")
    return value


def parse_date_literal(value: str, *, field_name: str = "date") -> date:
    """Parse exactly one literal ``YYYY-MM-DD`` calendar date."""

    if not isinstance(value, str) or _DATE_LITERAL.fullmatch(value) is None:
        raise RangeValidationError(f"{field_name} must use literal YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RangeValidationError(f"{field_name} is not a valid calendar date") from exc


def period_from_literals(
    effective_from: str,
    effective_until: str | None,
    preference: Preference,
) -> NormalizedPeriod:
    """Build a validated period from explicit strict date literals."""

    start = parse_date_literal(effective_from, field_name="effective_from")
    end = (
        None
        if effective_until is None
        else parse_date_literal(effective_until, field_name="effective_until")
    )
    return NormalizedPeriod(start, end, preference)


def normalize_periods(periods: Iterable[NormalizedPeriod]) -> tuple[NormalizedPeriod, ...]:
    """Validate an ordered schedule and merge adjacent periods with equal values."""

    normalized: list[NormalizedPeriod] = []
    for period in periods:
        if not isinstance(period, NormalizedPeriod):
            raise RangeValidationError("schedule entries must be NormalizedPeriod values")
        if normalized:
            previous = normalized[-1]
            if previous.effective_until is None:
                raise RangeValidationError("an indefinite period must be final")
            if period.effective_from < previous.effective_until:
                raise RangeValidationError("schedule periods must be ordered and non-overlapping")
            if (
                period.effective_from == previous.effective_until
                and period.preference == previous.preference
            ):
                normalized[-1] = NormalizedPeriod(
                    previous.effective_from,
                    period.effective_until,
                    previous.preference,
                )
                continue
        normalized.append(period)
    return tuple(normalized)


def set_preference(
    periods: Iterable[NormalizedPeriod],
    effective_from: str,
    effective_until: str | None,
    preference: Preference,
) -> tuple[NormalizedPeriod, ...]:
    """Overlay one configured preference on an ordered current schedule."""

    amendment = period_from_literals(effective_from, effective_until, preference)
    return _overlay(periods, amendment, include_amendment=True)


def unset_preference(
    periods: Iterable[NormalizedPeriod],
    effective_from: str,
    effective_until: str | None,
) -> tuple[NormalizedPeriod, ...]:
    """Remove configuration from a half-open range."""

    amendment = period_from_literals(
        effective_from,
        effective_until,
        Preference.no_preference(),
    )
    return _overlay(periods, amendment, include_amendment=False)


def _overlay(
    periods: Iterable[NormalizedPeriod],
    amendment: NormalizedPeriod,
    *,
    include_amendment: bool,
) -> tuple[NormalizedPeriod, ...]:
    current = normalize_periods(periods)
    fragments: list[NormalizedPeriod] = []

    for period in current:
        if not _intersects(period, amendment):
            fragments.append(period)
            continue
        if period.effective_from < amendment.effective_from:
            fragments.append(
                NormalizedPeriod(
                    period.effective_from,
                    amendment.effective_from,
                    period.preference,
                )
            )
        if (
            amendment.effective_until is not None
            and (
                period.effective_until is None
                or amendment.effective_until < period.effective_until
            )
        ):
            fragments.append(
                NormalizedPeriod(
                    amendment.effective_until,
                    period.effective_until,
                    period.preference,
                )
            )

    if include_amendment:
        fragments.append(amendment)
    fragments.sort(key=lambda period: period.effective_from)
    return normalize_periods(fragments)


def _intersects(left: NormalizedPeriod, right: NormalizedPeriod) -> bool:
    left_before_right_end = (
        right.effective_until is None
        or left.effective_from < right.effective_until
    )
    right_before_left_end = (
        left.effective_until is None
        or right.effective_from < left.effective_until
    )
    return left_before_right_end and right_before_left_end


def resolve_date(
    periods: Iterable[NormalizedPeriod], date_literal: str
) -> DateResolution:
    """Resolve a strict date against a normalized half-open schedule."""

    requested_date = parse_date_literal(date_literal)
    for period in normalize_periods(periods):
        if requested_date < period.effective_from:
            break
        if period.effective_until is None or requested_date < period.effective_until:
            if period.preference.state is PreferenceState.PREFERRED_MOVE:
                return DateResolution(
                    ResolutionState.PREFERRED_MOVE,
                    period.preference.move,
                )
            return DateResolution(ResolutionState.NO_PREFERENCE)
    return DateResolution(ResolutionState.UNCONFIGURED)
