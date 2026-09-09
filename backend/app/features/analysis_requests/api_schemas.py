"""HTTP contracts for one desired current analysis request."""

from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictStr

from backend.app.features.analysis_observation.api_schemas import (
    AnalysisObservationResponse,
)


class AnalysisRequestBody(BaseModel):
    """Strict known request fields while tolerating future client fields."""

    model_config = ConfigDict(extra="ignore", strict=True)

    fen: StrictStr
    quality: StrictStr = Field(
        default="browser",
        json_schema_extra={"enum": ["browser", "tool"]},
    )


AnalysisRequestErrorCode: TypeAlias = Literal[
    "invalid_fen",
    "invalid_quality",
    "analysis_unavailable",
    "unexpected_failure",
]


class AnalysisRequestErrorResponse(BaseModel):
    """Stable error body for the desired-analysis operation."""

    model_config = ConfigDict(extra="forbid", strict=True)

    code: AnalysisRequestErrorCode
    message: StrictStr


__all__ = [
    "AnalysisObservationResponse",
    "AnalysisRequestBody",
    "AnalysisRequestErrorCode",
    "AnalysisRequestErrorResponse",
]
