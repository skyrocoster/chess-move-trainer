"""Strict HTTP contracts for a preferred-move timeline."""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictStr


class ContractModel(BaseModel):
    """Base model that rejects fields outside the public HTTP contract."""

    model_config = ConfigDict(extra="forbid", strict=True, populate_by_name=True)


class MutationRequestModel(BaseModel):
    """Base model for mutation input whose forward-compatible extras are ignored."""

    model_config = ConfigDict(extra="ignore", strict=True, populate_by_name=True)


PreferredMovesErrorCode: TypeAlias = Literal[
    "invalid_fen",
    "invalid_from",
    "invalid_until",
    "invalid_window",
    "invalid_effective_from",
    "invalid_effective_until",
    "invalid_preference",
    "invalid_uci",
    "illegal_move",
    "preferred_moves_unavailable",
    "unexpected_failure",
]


class PreferredMovesErrorResponse(ContractModel):
    code: PreferredMovesErrorCode
    message: StrictStr


class MovePreferenceResponse(ContractModel):
    kind: Literal["move"]
    uci: StrictStr


class NoPreferenceResponse(ContractModel):
    kind: Literal["no_preference"]


class UnconfiguredPreferenceResponse(ContractModel):
    kind: Literal["unconfigured"]


PreferredMovesPreferenceResponse: TypeAlias = Annotated[
    MovePreferenceResponse | NoPreferenceResponse | UnconfiguredPreferenceResponse,
    Field(discriminator="kind"),
]


class MutationMovePreferenceRequest(MutationRequestModel):
    kind: Literal["move"]
    uci: StrictStr


class MutationNoPreferenceRequest(MutationRequestModel):
    kind: Literal["no_preference"]
    # This field lets the adapter reject the settled known invalid combination
    # while still ignoring all other forward-compatible nested fields.
    uci: StrictStr | None = None


PreferredMovesMutationPreferenceRequest: TypeAlias = Annotated[
    MutationMovePreferenceRequest | MutationNoPreferenceRequest,
    Field(discriminator="kind"),
]


class PreferredMovesMutationRequest(MutationRequestModel):
    fen: StrictStr
    effective_from: StrictStr
    effective_until: StrictStr | None = None
    preference: PreferredMovesMutationPreferenceRequest


PreferredMovesMutationPreferenceResponse: TypeAlias = Annotated[
    MovePreferenceResponse | NoPreferenceResponse,
    Field(discriminator="kind"),
]


class PreferredMovesRemovalRequest(MutationRequestModel):
    fen: StrictStr
    effective_from: StrictStr
    effective_until: StrictStr | None = None


class PreferredMovesPeriodResponse(ContractModel):
    effective_from: StrictStr
    effective_until: StrictStr | None
    preference: PreferredMovesMutationPreferenceResponse


class PreferredMovesMutationResponse(ContractModel):
    fen: StrictStr
    effective_from: StrictStr
    effective_until: StrictStr | None
    preference: PreferredMovesMutationPreferenceResponse
    periods: list[PreferredMovesPeriodResponse]


class PreferredMovesRemovalResponse(ContractModel):
    fen: StrictStr
    effective_from: StrictStr
    effective_until: StrictStr | None
    periods: list[PreferredMovesPeriodResponse]


class PreferredMovesSegmentResponse(ContractModel):
    from_date: StrictStr = Field(alias="from")
    until: StrictStr
    preference: PreferredMovesPreferenceResponse


class PreferredMovesResponse(ContractModel):
    fen: StrictStr
    from_date: StrictStr = Field(alias="from")
    until: StrictStr
    segments: list[PreferredMovesSegmentResponse]


__all__ = [
    "MovePreferenceResponse",
    "MutationMovePreferenceRequest",
    "MutationNoPreferenceRequest",
    "MutationRequestModel",
    "NoPreferenceResponse",
    "PreferredMovesErrorCode",
    "PreferredMovesErrorResponse",
    "PreferredMovesMutationPreferenceRequest",
    "PreferredMovesMutationPreferenceResponse",
    "PreferredMovesMutationRequest",
    "PreferredMovesMutationResponse",
    "PreferredMovesPeriodResponse",
    "PreferredMovesPreferenceResponse",
    "PreferredMovesRemovalRequest",
    "PreferredMovesRemovalResponse",
    "PreferredMovesResponse",
    "PreferredMovesSegmentResponse",
    "UnconfiguredPreferenceResponse",
]
