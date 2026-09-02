"""Strict HTTP contracts for move response distributions."""

from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, model_validator

MoveResponseDistributionErrorCode: TypeAlias = Literal[
    "invalid_fen",
    "invalid_color",
    "move_response_distribution_unavailable",
    "unexpected_failure",
]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class MoveResponseDistributionErrorResponse(ContractModel):
    code: MoveResponseDistributionErrorCode
    message: StrictStr


class MoveResponseReply(ContractModel):
    rank: StrictInt = Field(ge=1)
    child_uci: StrictStr
    san: StrictStr
    distinct_game_count: StrictInt = Field(ge=0)
    opening_name: StrictStr | None = None


class MoveResponseDistributionResponse(ContractModel):
    fen: StrictStr
    color: Literal["white", "black"]
    matching_game_count: StrictInt = Field(ge=0)
    replies: list[MoveResponseReply] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_ranked_replies(self) -> "MoveResponseDistributionResponse":
        expected_ranks = list(range(1, len(self.replies) + 1))
        if [reply.rank for reply in self.replies] != expected_ranks:
            raise ValueError("reply ranks must be contiguous from one")
        if len({reply.child_uci for reply in self.replies}) != len(self.replies):
            raise ValueError("reply child UCI moves must be unique")
        return self
