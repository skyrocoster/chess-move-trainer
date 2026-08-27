from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

SubjectColor = Literal["white", "black"]
GameErrorCode = Literal[
    "game_not_found",
    "position_not_found",
    "corpus_unavailable",
    "game_unavailable",
    "unexpected_failure",
]


class GamePositionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ply: int
    fen: str
    san: str | None


class GameResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    game_uuid: UUID
    initial_ply: int
    subject_color: SubjectColor
    source_url: str | None
    positions: list[GamePositionResponse]


class GameErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: GameErrorCode
    message: str
