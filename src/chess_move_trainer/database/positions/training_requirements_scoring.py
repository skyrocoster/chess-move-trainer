"""Pure scoring and signed training-credit decay calculations."""

from __future__ import annotations

import math
from datetime import date

from .training_requirements_models import (
    TrainingRequirementPolicy,
    TrainingRequirementValidationError,
    parse_calendar_date,
)


def game_balance(
    hits: int,
    misses: int,
    policy: TrainingRequirementPolicy,
) -> float:
    """Calculate normalized live-game evidence balance ``G``."""

    _validate_counts(hits, misses)
    _validate_policy(policy)
    result = hits * policy.game_hit_weight - misses * policy.game_miss_weight
    return _finite_result(result, "game balance")


def training_adjustment(training_balance: float) -> float:
    """Calculate the signed-square training adjustment ``F(T)``."""

    value = _finite_float(training_balance, "training balance")
    return _finite_result(value * abs(value), "training adjustment")


def requirement(
    game_balance_value: float,
    effective_training_balance: float,
) -> float:
    """Calculate ``R = G + F(T)`` from finite balances."""

    game_value = _finite_float(game_balance_value, "game balance")
    training_value = _finite_float(effective_training_balance, "training balance")
    return _finite_result(game_value + training_adjustment(training_value), "training requirement")


def training_required(training_requirement: float) -> bool:
    """Return true exactly when the unrounded requirement is below zero."""

    return _finite_float(training_requirement, "training requirement") < 0.0


def effective_training_balance(
    stored_training_balance: float,
    training_updated_on: str | date | None,
    as_of: str | date,
    policy: TrainingRequirementPolicy,
) -> float:
    """Decay signed credit by whole calendar days and invert signed square.

    The configured half-life applies to ``F(T)``.  In particular, one half-life
    halves the signed adjustment and therefore halves neither ``T`` nor quarters
    the adjustment.
    """

    stored = _finite_float(stored_training_balance, "stored training balance")
    _validate_policy(policy)
    scoring_date = _coerce_date(as_of, "as_of")
    if training_updated_on is None:
        return stored
    updated_date = _coerce_date(training_updated_on, "training_updated_on")
    elapsed_days = (scoring_date - updated_date).days
    if elapsed_days < 0:
        raise TrainingRequirementValidationError("training_updated_on cannot be later than as_of")

    stored_adjustment = training_adjustment(stored)
    decay_factor = 2.0 ** (-elapsed_days / policy.credit_half_life_days)
    effective_adjustment = _finite_result(
        stored_adjustment * decay_factor, "effective training adjustment"
    )
    if effective_adjustment == 0.0:
        return 0.0
    result = math.copysign(math.sqrt(abs(effective_adjustment)), effective_adjustment)
    return _finite_result(result, "effective training balance")


def minimum_additional_correct_answers(
    game_balance_value: float,
    effective_training_balance_value: float,
) -> int:
    """Find the smallest whole number of same-date correct answers for ``R >= 0``."""

    game_value = _finite_float(game_balance_value, "game balance")
    effective_value = _finite_float(effective_training_balance_value, "effective training balance")
    current_requirement = requirement(game_value, effective_value)
    if current_requirement >= 0.0:
        return 0

    target_adjustment = -game_value
    target_balance = (
        0.0
        if target_adjustment == 0.0
        else math.copysign(math.sqrt(abs(target_adjustment)), target_adjustment)
    )
    candidate = max(0, math.ceil(target_balance - effective_value))
    while requirement(game_value, effective_value + candidate) < 0.0:
        candidate += 1
    while candidate > 0 and requirement(game_value, effective_value + candidate - 1) >= 0.0:
        candidate -= 1
    return candidate


def score_training_pair(
    hits: int,
    misses: int,
    stored_training_balance: float,
    training_updated_on: str | date | None,
    as_of: str | date,
    policy: TrainingRequirementPolicy,
) -> tuple[float, float, float, bool, int]:
    """Return game balance, effective T, R, required state, and answer count."""

    game_value = game_balance(hits, misses, policy)
    effective_value = effective_training_balance(
        stored_training_balance,
        training_updated_on,
        as_of,
        policy,
    )
    result = requirement(game_value, effective_value)
    return (
        game_value,
        effective_value,
        result,
        training_required(result),
        minimum_additional_correct_answers(game_value, effective_value),
    )


def _validate_counts(hits: object, misses: object) -> None:
    if type(hits) is not int or hits < 0:
        raise TrainingRequirementValidationError("hits must be a non-negative integer")
    if type(misses) is not int or misses < 0:
        raise TrainingRequirementValidationError("misses must be a non-negative integer")


def _validate_policy(policy: object) -> None:
    if not isinstance(policy, TrainingRequirementPolicy):
        raise TrainingRequirementValidationError("policy must be a TrainingRequirementPolicy")


def _finite_float(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise TrainingRequirementValidationError(f"{name} must be finite")
    try:
        normalized = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise TrainingRequirementValidationError(f"{name} must be finite") from error
    if not math.isfinite(normalized):
        raise TrainingRequirementValidationError(f"{name} must be finite")
    return normalized


def _finite_result(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise TrainingRequirementValidationError(f"{name} is not finite")
    return value


def _coerce_date(value: str | date, name: str) -> date:
    if isinstance(value, date):
        return value
    return parse_calendar_date(value, name)


calculate_game_balance = game_balance
calculate_training_adjustment = training_adjustment
calculate_training_requirement = requirement
decay_training_balance = effective_training_balance
