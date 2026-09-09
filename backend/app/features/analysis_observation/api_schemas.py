"""Strict HTTP contracts for one current analysis observation."""

from __future__ import annotations

from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr


class ContractModel(BaseModel):
    """Base model that rejects fields outside the public HTTP contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


AnalysisObservationErrorCode: TypeAlias = Literal[
    "invalid_fen",
    "analysis_unavailable",
    "unexpected_failure",
]


class AnalysisObservationErrorResponse(ContractModel):
    code: AnalysisObservationErrorCode
    message: StrictStr


class AnalysisObservationLineResponse(ContractModel):
    rank: StrictInt = Field(ge=1)
    score_kind: Literal["cp", "mate"]
    score_value: StrictInt
    wdl_wins: StrictInt = Field(ge=0)
    wdl_draws: StrictInt = Field(ge=0)
    wdl_losses: StrictInt = Field(ge=0)
    pv_uci: list[StrictStr]
    depth: StrictInt = Field(ge=0)


class AnalysisObservationResultResponse(ContractModel):
    quality: Literal["browser", "tool"]
    configuration_version: StrictInt = Field(ge=1)
    settings: dict[StrictStr, Any]
    engine_name: StrictStr
    engine_version: StrictStr
    terminal_kind: Literal["checkmate", "stalemate", "insufficient_material"] | None
    lines: list[AnalysisObservationLineResponse]


class AnalysisObservationResponse(ContractModel):
    fen: StrictStr
    state: Literal["not_requested", "queued", "running", "ready"]
    result: AnalysisObservationResultResponse | None


__all__ = [
    "AnalysisObservationErrorCode",
    "AnalysisObservationErrorResponse",
    "AnalysisObservationLineResponse",
    "AnalysisObservationResponse",
    "AnalysisObservationResultResponse",
]
