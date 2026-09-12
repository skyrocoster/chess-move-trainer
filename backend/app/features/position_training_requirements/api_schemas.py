"""Strict HTTP contracts for position training requirements."""

from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr


class ContractModel(BaseModel):
    """Base model that rejects fields outside the public contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


class MutationRequestModel(BaseModel):
    """Base model for forward-compatible mutation input."""

    model_config = ConfigDict(extra="ignore", strict=True)


TrainingRequirementErrorCode: TypeAlias = Literal[
    "invalid_as_of",
    "invalid_fen",
    "invalid_opening_filter",
    "invalid_played_move_uci",
    "invalid_requirement_range",
    "invalid_trainer_color",
    "invalid_pagination",
    "training_requirement_not_found",
    "training_requirements_stale",
    "position_training_requirements_unavailable",
    "unexpected_failure",
]


class TrainingRequirementErrorResponse(ContractModel):
    code: TrainingRequirementErrorCode
    message: StrictStr


class TrainingRequirementPolicyResponse(ContractModel):
    target_success_rate: StrictFloat
    game_hit_weight: StrictFloat
    game_miss_weight: StrictFloat
    training_curve: StrictStr
    training_credit_half_life_days: StrictFloat


class TrainingRequirementItemResponse(ContractModel):
    fen: StrictStr
    trainer_color: Literal["white", "black"]
    preferred_move_uci: StrictStr
    encounters: StrictInt = Field(ge=0)
    hits: StrictInt = Field(ge=0)
    misses: StrictInt = Field(ge=0)
    observed_success_rate: StrictFloat
    game_balance: StrictFloat
    effective_training_balance: StrictFloat
    training_adjustment: StrictFloat
    training_updated_on: StrictStr | None
    training_requirement: StrictFloat
    training_required: StrictBool
    correct_answers_needed: StrictInt = Field(ge=0)


class TrainingRequirementResponse(ContractModel):
    as_of: StrictStr
    scoring_policy: TrainingRequirementPolicyResponse
    items: list[TrainingRequirementItemResponse]
    page: StrictInt = Field(ge=1)
    page_size: StrictInt = Field(ge=1, le=100)
    total: StrictInt = Field(ge=0)


class TrainingAnswerRequest(MutationRequestModel):
    fen: StrictStr
    trainer_color: Literal["white", "black"]
    as_of: StrictStr
    played_move_uci: StrictStr


class TrainingAnswerResponse(ContractModel):
    as_of: StrictStr
    correct: StrictBool
    item: TrainingRequirementItemResponse


__all__ = [
    "TrainingAnswerRequest",
    "TrainingAnswerResponse",
    "TrainingRequirementErrorCode",
    "TrainingRequirementErrorResponse",
    "TrainingRequirementItemResponse",
    "TrainingRequirementPolicyResponse",
    "TrainingRequirementResponse",
]
