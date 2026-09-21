"""Strict HTTP contracts for trainer blunder discovery."""

from __future__ import annotations

from typing import Literal, TypeAlias
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr


class ContractModel(BaseModel):
    """Base model that rejects fields outside the public contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


BlunderErrorCode: TypeAlias = Literal[
    "invalid_filter",
    "trainer_blunders_unavailable",
    "unexpected_failure",
]


class BlunderErrorResponse(ContractModel):
    code: BlunderErrorCode
    message: StrictStr


class BlunderTimeframeResponse(ContractModel):
    started_at_from: StrictStr
    started_at_to: StrictStr


class BlunderPolicyResponse(ContractModel):
    minimum_expected_score_loss: StrictFloat = Field(gt=0, le=1)
    evaluation_basis: Literal["wdl_expected_score"]
    score_perspective: Literal["trainer"]


class BlunderCoverageResponse(ContractModel):
    examined_game_count: StrictInt = Field(ge=0)
    excluded_game_count: StrictInt = Field(ge=0)
    in_scope_game_count: StrictInt = Field(ge=0)
    trainer_move_count: StrictInt = Field(ge=0)
    comparable_move_count: StrictInt = Field(ge=0)
    skipped_missing_analysis_count: StrictInt = Field(ge=0)


class TrainerBlunderItemResponse(ContractModel):
    game_uuid: UUID
    source_url: StrictStr
    started_at_utc: StrictStr
    trainer_color: Literal["white", "black"]
    ply: StrictInt = Field(ge=0)
    fen: StrictStr
    played_move_uci: StrictStr
    preferred_move_uci: StrictStr
    expected_score_before: StrictFloat = Field(ge=0, le=1)
    expected_score_after: StrictFloat = Field(ge=0, le=1)
    expected_score_loss: StrictFloat = Field(ge=0, le=1)
    before_analysis_quality: Literal["browser", "tool"]
    after_analysis_quality: Literal["browser", "tool"]


class TrainerBlundersResponse(ContractModel):
    timeframe: BlunderTimeframeResponse
    policy: BlunderPolicyResponse
    coverage: BlunderCoverageResponse
    items: list[TrainerBlunderItemResponse]
    page: StrictInt = Field(ge=1)
    page_size: StrictInt = Field(ge=1, le=100)
    total: StrictInt = Field(ge=0)
    total_pages: StrictInt = Field(ge=0)
    has_next: bool


__all__ = [
    "BlunderCoverageResponse",
    "BlunderErrorCode",
    "BlunderErrorResponse",
    "BlunderPolicyResponse",
    "BlunderTimeframeResponse",
    "TrainerBlunderItemResponse",
    "TrainerBlundersResponse",
]
