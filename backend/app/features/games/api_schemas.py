"""Strict HTTP models for the clean games collection."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GamesModel(BaseModel):
    """Base model that rejects response fields outside the approved contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


TrainerColor = Literal["white", "black"]
TrainerOutcome = Literal["win", "loss", "draw"]
TimeClass = Literal["bullet", "blitz", "rapid", "daily"]
CoverageState = Literal["none", "partial", "complete"]
GamesErrorCode = Literal[
    "invalid_filter",
    "game_not_found",
    "games_unavailable",
    "unexpected_failure",
]


class OpeningSummaryResponse(GamesModel):
    key: str
    eco: str
    name: str
    ply: int


class GameCoverageResponse(GamesModel):
    distinct_position_count: int
    analyzed_position_count: int
    preferred_position_count: int
    analysis_coverage: CoverageState
    preferred_coverage: CoverageState


class GameSummaryResponse(GamesModel):
    game_uuid: UUID
    source_url: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: UUID
    opponent_chesscom_uuid: UUID | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: TrainerOutcome | None
    termination_reason: str | None
    time_control: str | None
    time_class: TimeClass | None
    occurrence_count: int
    length_plies: int
    deepest_opening: OpeningSummaryResponse | None
    coverage: GameCoverageResponse


class GameDetailOccurrenceResponse(GamesModel):
    ply: int
    fen: str
    move_uci: str | None


class GameDetailResponse(GamesModel):
    game_uuid: UUID
    source_url: str
    original_pgn: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: UUID
    opponent_chesscom_uuid: UUID | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: TrainerOutcome | None
    termination_reason: str | None
    time_control: str | None
    time_class: TimeClass | None
    occurrences: list[GameDetailOccurrenceResponse]


class GamesResponse(GamesModel):
    items: list[GameSummaryResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool


class GamesErrorResponse(GamesModel):
    code: GamesErrorCode
    message: str


__all__ = [
    "CoverageState",
    "GameCoverageResponse",
    "GameDetailOccurrenceResponse",
    "GameDetailResponse",
    "GameSummaryResponse",
    "GamesErrorCode",
    "GamesErrorResponse",
    "GamesResponse",
    "OpeningSummaryResponse",
    "TimeClass",
    "TrainerColor",
    "TrainerOutcome",
]
