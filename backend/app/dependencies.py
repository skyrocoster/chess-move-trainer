"""Application dependencies for database capabilities."""

from __future__ import annotations

import os
from pathlib import Path

from chess_move_trainer.database.blunders import BlunderPolicy, BlunderValidationError
from chess_move_trainer.database.lifecycle import DEFAULT_DATABASE_PATH
from chess_move_trainer.database.positions import (
    TrainingRequirementPolicy,
    TrainingRequirementValidationError,
)

REBUILT_DATABASE_PATH_ENV = "CHESS_REBUILT_DATABASE_PATH"
TRAINING_TARGET_SUCCESS_RATE_ENV = "CHESS_TRAINING_TARGET_SUCCESS_RATE"
TRAINING_CREDIT_HALF_LIFE_DAYS_ENV = "CHESS_TRAINING_CREDIT_HALF_LIFE_DAYS"
BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV = "CHESS_BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS"
DEFAULT_TRAINING_TARGET_SUCCESS_RATE = 0.8
DEFAULT_TRAINING_CREDIT_HALF_LIFE_DAYS = 30.0
DEFAULT_BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS = 0.2


def get_rebuilt_database_path() -> Path:
    """Return the explicit clean database path for the current application process."""

    return Path(os.environ.get(REBUILT_DATABASE_PATH_ENV, str(DEFAULT_DATABASE_PATH)))


def get_training_requirement_policy() -> TrainingRequirementPolicy | None:
    """Return the configured policy, or ``None`` when the capability is unavailable."""

    try:
        target_success_rate = _configured_float(
            TRAINING_TARGET_SUCCESS_RATE_ENV,
            DEFAULT_TRAINING_TARGET_SUCCESS_RATE,
        )
        credit_half_life_days = _configured_float(
            TRAINING_CREDIT_HALF_LIFE_DAYS_ENV,
            DEFAULT_TRAINING_CREDIT_HALF_LIFE_DAYS,
        )
        return TrainingRequirementPolicy(target_success_rate, credit_half_life_days)
    except (TypeError, ValueError, OverflowError, TrainingRequirementValidationError):
        return None


def get_blunder_policy() -> BlunderPolicy | None:
    """Return the configured blunder threshold, or ``None`` when invalid."""

    try:
        minimum_loss = _configured_float(
            BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV,
            DEFAULT_BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS,
        )
        return BlunderPolicy(minimum_loss)
    except (TypeError, ValueError, OverflowError, BlunderValidationError):
        return None


def _configured_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    return default if raw is None else float(raw)


__all__ = [
    "BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV",
    "DEFAULT_BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS",
    "DEFAULT_TRAINING_CREDIT_HALF_LIFE_DAYS",
    "DEFAULT_TRAINING_TARGET_SUCCESS_RATE",
    "REBUILT_DATABASE_PATH_ENV",
    "TRAINING_CREDIT_HALF_LIFE_DAYS_ENV",
    "TRAINING_TARGET_SUCCESS_RATE_ENV",
    "get_blunder_policy",
    "get_rebuilt_database_path",
    "get_training_requirement_policy",
]
