from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

SubjectColor = Literal["white", "black"]
PositionErrorCode = Literal[
    "position_not_found",
    "corpus_unavailable",
    "stored_position_invalid",
    "unexpected_failure",
]


class PositionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    game_uuid: UUID
    ply: int
    fen: str
    subject_color: SubjectColor


class PositionErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: PositionErrorCode
    message: str
