"""Strict HTTP contracts for the preferred-move lifecycle."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictBool, StrictStr

PreferredMoveState = Literal["assigned", "unassigned"]
PreferredMoveErrorCode = Literal[
    "invalid_fen",
    "invalid_move",
    "invalid_timestamp",
    "future_effective_time",
    "position_not_found",
    "preferred_move_unavailable",
    "unexpected_failure",
]


class PreferredMoveErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: PreferredMoveErrorCode
    message: StrictStr


class PreferredMoveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    move_uci: StrictStr
    effective_at: StrictStr | None = None


class PreferredMoveValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uci: StrictStr
    san: StrictStr


class PreferredMoveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    state: PreferredMoveState
    move: PreferredMoveValue | None


class PreferredMoveMutationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fen: StrictStr
    changed: StrictBool
    effective_at: StrictStr
