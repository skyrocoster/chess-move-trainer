"""Strict HTTP contracts for one clean position insight."""

from __future__ import annotations

from typing import Annotated, Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr


class ContractModel(BaseModel):
    """Base model that rejects fields outside the settled HTTP contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


PositionInsightErrorCode: TypeAlias = Literal[
    "invalid_fen",
    "invalid_trainer_color",
    "invalid_as_of",
    "position_insight_unavailable",
    "unexpected_failure",
]


class PositionInsightErrorResponse(ContractModel):
    code: PositionInsightErrorCode
    message: StrictStr


class PositionInsightOpeningResponse(ContractModel):
    key: StrictStr
    eco: StrictStr
    name: StrictStr
    ply: StrictInt = Field(ge=0)
    match: Literal["route", "transposition"]


class PositionInsightExperienceResponse(ContractModel):
    distinct_game_count: StrictInt = Field(ge=0)
    occurrence_count: StrictInt = Field(ge=0)


class PositionInsightObservedMoveResponse(ContractModel):
    move_uci: StrictStr
    distinct_game_count: StrictInt = Field(ge=0)
    occurrence_count: StrictInt = Field(ge=0)


class PositionInsightLineResponse(ContractModel):
    rank: StrictInt = Field(ge=1)
    score_kind: Literal["cp", "mate"]
    score_value: StrictInt
    wdl_wins: StrictInt = Field(ge=0)
    wdl_draws: StrictInt = Field(ge=0)
    wdl_losses: StrictInt = Field(ge=0)
    pv_uci: list[StrictStr]
    depth: StrictInt = Field(ge=0)


class PositionInsightResultResponse(ContractModel):
    quality: Literal["browser", "tool"]
    configuration_version: StrictInt = Field(ge=1)
    settings: dict[StrictStr, Any]
    engine_name: StrictStr
    engine_version: StrictStr
    terminal_kind: Literal["checkmate", "stalemate", "insufficient_material"] | None
    lines: list[PositionInsightLineResponse]


class PositionInsightAnalysisResponse(ContractModel):
    state: Literal["not_requested", "queued", "running", "ready"]
    result: PositionInsightResultResponse | None


class MovePreferenceResponse(ContractModel):
    kind: Literal["move"]
    uci: StrictStr


class NoPreferenceResponse(ContractModel):
    kind: Literal["no_preference"]


class UnconfiguredPreferenceResponse(ContractModel):
    kind: Literal["unconfigured"]


PositionInsightPreferenceResponse: TypeAlias = Annotated[
    MovePreferenceResponse | NoPreferenceResponse | UnconfiguredPreferenceResponse,
    Field(discriminator="kind"),
]


class PositionInsightResponse(ContractModel):
    fen: StrictStr
    trainer_color: Literal["white", "black"]
    as_of: StrictStr
    opening: PositionInsightOpeningResponse | None
    experience: PositionInsightExperienceResponse
    observed_moves: list[PositionInsightObservedMoveResponse]
    analysis: PositionInsightAnalysisResponse
    preference: PositionInsightPreferenceResponse


__all__ = [
    "MovePreferenceResponse",
    "NoPreferenceResponse",
    "PositionInsightAnalysisResponse",
    "PositionInsightErrorCode",
    "PositionInsightErrorResponse",
    "PositionInsightExperienceResponse",
    "PositionInsightLineResponse",
    "PositionInsightObservedMoveResponse",
    "PositionInsightOpeningResponse",
    "PositionInsightPreferenceResponse",
    "PositionInsightResponse",
    "PositionInsightResultResponse",
    "UnconfiguredPreferenceResponse",
]
