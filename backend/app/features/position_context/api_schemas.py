"""Strict HTTP contracts for the neutral position-context endpoint."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt, StrictStr

PositionContextErrorCode = Literal[
    "invalid_fen",
    "position_context_unavailable",
    "unexpected_failure",
]


class PositionContextErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: PositionContextErrorCode
    message: StrictStr


class PositionContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    overall_exists: StrictBool
    white_count: StrictInt
    black_count: StrictInt
    white_total: StrictInt
    black_total: StrictInt
