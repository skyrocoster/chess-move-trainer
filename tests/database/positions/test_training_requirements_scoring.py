from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from chess_move_trainer.database.positions import (
    TrainingRequirementPolicy,
    TrainingRequirementValidationError,
    effective_training_balance,
    game_balance,
    minimum_additional_correct_answers,
    requirement,
    score_training_pair,
    training_adjustment,
    training_required,
)

DEFAULT_POLICY = TrainingRequirementPolicy(0.8, 30)


@pytest.mark.parametrize(
    ("target", "half_life"),
    [(0.5, 30), (1.0, 30), (math.inf, 30), (0.8, 0), (0.8, math.inf)],
)
def test_policy_rejects_non_finite_or_out_of_range_values(
    target: float,
    half_life: float,
) -> None:
    with pytest.raises(TrainingRequirementValidationError):
        TrainingRequirementPolicy(target, half_life)


def test_policy_is_immutable_and_exposes_parameterized_weights() -> None:
    policy = TrainingRequirementPolicy(0.75, 12.5)

    assert policy.game_hit_weight == 1.0
    assert policy.game_miss_weight == 3.0
    assert policy.training_curve == "squared"
    assert policy.training_credit_half_life_days == 12.5
    with pytest.raises(FrozenInstanceError):
        policy.target_success_rate = 0.8  # type: ignore[misc]


def test_default_scoring_formula_and_anchor_answer_count() -> None:
    assert game_balance(28, 58, DEFAULT_POLICY) == -204.0
    assert training_adjustment(3) == 9.0
    assert requirement(-204, 0) == -204.0
    assert training_required(-204) is True
    assert minimum_additional_correct_answers(-204, 0) == 15
    assert minimum_additional_correct_answers(-204, 15) == 0
    assert minimum_additional_correct_answers(1, -2) == 1


@pytest.mark.parametrize("stored", [2.0, -2.0])
def test_one_credit_half_life_halves_signed_adjustment_not_quarters_it(
    stored: float,
) -> None:
    effective = effective_training_balance(
        stored,
        "2026-01-01",
        "2026-01-31",
        DEFAULT_POLICY,
    )

    expected_adjustment = math.copysign(2.0, stored)
    assert training_adjustment(effective) == pytest.approx(expected_adjustment)
    assert effective == pytest.approx(math.copysign(math.sqrt(2.0), stored))


def test_scoring_preserves_signed_fractional_precision_and_supports_future_preview() -> None:
    result = score_training_pair(
        2,
        1,
        1.234567891,
        "2026-01-01",
        "2026-01-16",
        TrainingRequirementPolicy(0.7, 15),
    )

    assert result[0] == pytest.approx(2.0 - (0.7 / 0.3))
    assert math.isfinite(result[1])
    assert math.isfinite(result[2])


def test_decay_rejects_training_state_newer_than_as_of() -> None:
    with pytest.raises(TrainingRequirementValidationError):
        effective_training_balance(1, "2026-02-01", "2026-01-31", DEFAULT_POLICY)


@pytest.mark.parametrize(
    ("hits", "misses"),
    [(-1, 0), (0, -1), (1.0, 0), (0, True)],
)
def test_scoring_rejects_malformed_evidence_counts(hits: object, misses: object) -> None:
    with pytest.raises(TrainingRequirementValidationError):
        game_balance(hits, misses, DEFAULT_POLICY)  # type: ignore[arg-type]
