"""Typed HTTP contracts for browser evaluation observation and enqueueing."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictStr

EvaluationErrorCode = Literal[
    "evaluation_unavailable",
    "invalid_fen",
    "request_too_large",
    "invalid_action",
    "invalid_transition",
    "evaluation_busy",
    "unexpected_failure",
]
Eligibility = Literal["missing", "eligible", "stale"]
QueueState = Literal["queued", "running", "done", "failed"]
ScoreKind = Literal["cp", "mate", "mate_given"]


class EvaluationErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: EvaluationErrorCode
    message: StrictStr


class EvaluationActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    action: StrictStr


class EvaluationCandidateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int
    score_kind: ScoreKind
    score_value: int
    wdl_wins: int
    wdl_draws: int
    wdl_losses: int
    pv_uci: list[StrictStr]
    depth: int
    seldepth: int
    nodes: int
    engine_time_ms: int


class EvaluationResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    profile_id: StrictStr
    candidates: list[EvaluationCandidateResponse]
    terminal_kind: StrictStr | None
    completed_at: StrictStr
    wall_time_ms: int


class EvaluationStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: QueueState
    position: int
    attempts: int
    enqueued_at: StrictStr
    started_at: StrictStr | None
    completed_at: StrictStr | None
    error_code: StrictStr | None


class EvaluationObservationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    eligibility: Eligibility
    result: EvaluationResultResponse | None
    status: EvaluationStatusResponse | None
    terminal: bool


class EvaluationEnqueueResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    action: StrictStr
    outcome: StrictStr
    eligibility: Eligibility
    status: EvaluationStatusResponse


class EvaluationPollResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    state: QueueState | None
    completed_at: StrictStr | None
    error_code: StrictStr | None
