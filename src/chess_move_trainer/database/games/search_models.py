"""Game search query models."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cmp_to_key
from pathlib import Path
from typing import Literal

import chess
from sqlalchemy import text

from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_connection
from ..openings.keys import OpeningKeyError, opening_api_key, parse_opening_api_key
from .search_validation import _in_datetime_bounds, _in_numeric_bounds, _normalize_fen, _normalize_timestamp, _parse_opening_key, _require_optional_non_negative_int, _require_ordered_bounds, _require_positive_int, _validate_legal_move, _validate_optional_non_empty_text
from ..positions import CanonicalPosition, PositionValidationError, canonicalize_fen
from ..schema import SchemaIncompatibleError, _assert_compatible_schema


TrainerColor = Literal["white", "black"]
TrainerOutcome = Literal["win", "loss", "draw"]
OpeningMatch = Literal["reached", "deepest"]
CoverageState = Literal["none", "partial", "complete"]
GameSearchSort = Literal[
    "started_at_desc",
    "started_at_asc",
    "length_desc",
    "length_asc",
    "trainer_rating_desc",
    "trainer_rating_asc",
    "opponent_rating_desc",
    "opponent_rating_asc",
    "opponent_uuid_asc",
    "opponent_uuid_desc",
    "game_uuid_asc",
    "game_uuid_desc",
]

_SORTS: tuple[GameSearchSort, ...] = (
    "started_at_desc",
    "started_at_asc",
    "length_desc",
    "length_asc",
    "trainer_rating_desc",
    "trainer_rating_asc",
    "opponent_rating_desc",
    "opponent_rating_asc",
    "opponent_uuid_asc",
    "opponent_uuid_desc",
    "game_uuid_asc",
    "game_uuid_desc",
)
_TIME_CLASSES = ("bullet", "blitz", "rapid", "daily")
_COVERAGE_STATES = ("none", "partial", "complete")
_RFC3339 = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    r"[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})\Z"
)

from .search_errors import GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError


@dataclass(frozen=True, slots=True)
class GameSearchQuery:
    """All approved collection filters and pagination controls."""

    page: int = 1
    page_size: int = 50
    started_at_from: str | datetime | None = None
    started_at_to: str | datetime | None = None
    ended_at_from: str | datetime | None = None
    ended_at_to: str | datetime | None = None
    trainer_color: TrainerColor | None = None
    trainer_outcome: TrainerOutcome | None = None
    termination_reason: str | None = None
    trainer_rating_min: int | None = None
    trainer_rating_max: int | None = None
    opponent_rating_min: int | None = None
    opponent_rating_max: int | None = None
    opponent_chesscom_uuid: str | None = None
    time_class: str | None = None
    time_control: str | None = None
    opening_key: str | None = None
    opening_match: OpeningMatch | None = None
    contains_fen: str | None = None
    move_fen: str | None = None
    move_uci: str | None = None
    min_length_plies: int | None = None
    max_length_plies: int | None = None
    analysis_coverage: CoverageState | None = None
    preferred_coverage: CoverageState | None = None
    sort: GameSearchSort = "started_at_desc"

    def __post_init__(self) -> None:
        _require_positive_int(self.page, "page")
        if type(self.page_size) is not int or not 1 <= self.page_size <= 100:
            raise GameSearchValidationError("page_size must be an integer from 1 through 100")

        for field_name, value, accepted in (
            ("trainer_color", self.trainer_color, ("white", "black")),
            ("trainer_outcome", self.trainer_outcome, ("win", "loss", "draw")),
            ("opening_match", self.opening_match, ("reached", "deepest")),
            ("analysis_coverage", self.analysis_coverage, _COVERAGE_STATES),
            ("preferred_coverage", self.preferred_coverage, _COVERAGE_STATES),
        ):
            if value is not None and value not in accepted:
                raise GameSearchValidationError(f"{field_name} has an unsupported value")
        if self.sort not in _SORTS:
            raise GameSearchValidationError("sort has an unsupported value")

        dates = (
            ("started_at_from", self.started_at_from),
            ("started_at_to", self.started_at_to),
            ("ended_at_from", self.ended_at_from),
            ("ended_at_to", self.ended_at_to),
        )
        normalized_dates = {
            field_name: _normalize_timestamp(value, field_name)
            for field_name, value in dates
        }
        _require_ordered_bounds(
            normalized_dates["started_at_from"],
            normalized_dates["started_at_to"],
            "started_at",
        )
        _require_ordered_bounds(
            normalized_dates["ended_at_from"],
            normalized_dates["ended_at_to"],
            "ended_at",
        )
        for field_name, value in normalized_dates.items():
            object.__setattr__(self, field_name, value)

        if self.termination_reason is not None:
            if type(self.termination_reason) is not str or not self.termination_reason.strip():
                raise GameSearchValidationError("termination_reason must be non-empty")
            object.__setattr__(self, "termination_reason", self.termination_reason.strip().casefold())
        _validate_optional_non_empty_text(self.opponent_chesscom_uuid, "opponent_chesscom_uuid")
        _validate_optional_non_empty_text(self.time_control, "time_control")
        if self.time_class is not None and (
            type(self.time_class) is not str or self.time_class not in _TIME_CLASSES
        ):
            raise GameSearchValidationError("time_class has an unsupported value")

        for field_name in (
            "trainer_rating_min",
            "trainer_rating_max",
            "opponent_rating_min",
            "opponent_rating_max",
        ):
            _require_optional_non_negative_int(getattr(self, field_name), field_name)
        _require_ordered_bounds(
            self.trainer_rating_min, self.trainer_rating_max, "trainer_rating"
        )
        _require_ordered_bounds(
            self.opponent_rating_min, self.opponent_rating_max, "opponent_rating"
        )

        if self.opening_key is None:
            if self.opening_match is not None:
                raise GameSearchValidationError(
                    "opening_match requires opening_key"
                )
        else:
            try:
                _parse_opening_key(self.opening_key)
            except ValueError as error:
                raise GameSearchValidationError(str(error)) from error
            if self.opening_match is None:
                raise GameSearchValidationError(
                    "opening_key requires opening_match"
                )

        contains_position = _normalize_fen(self.contains_fen, "contains_fen")
        move_position = _normalize_fen(self.move_fen, "move_fen")
        if (move_position is None) != (self.move_uci is None):
            raise GameSearchValidationError("move_fen and move_uci must be supplied together")
        if move_position is not None:
            assert self.move_uci is not None
            _validate_legal_move(move_position, self.move_uci)
        object.__setattr__(self, "contains_fen", contains_position)
        object.__setattr__(self, "move_fen", move_position)

        for field_name in ("min_length_plies", "max_length_plies"):
            _require_optional_non_negative_int(getattr(self, field_name), field_name)
        _require_ordered_bounds(
            self.min_length_plies, self.max_length_plies, "length_plies"
        )


@dataclass(frozen=True, slots=True)
class DeepestOpening:
    """The selected deepest opening classification for a game."""

    key: str
    eco: str
    name: str
    ply: int


@dataclass(frozen=True, slots=True)
class GameCoverage:
    """Analysis and preferred-move coverage over distinct game positions."""

    distinct_position_count: int
    analyzed_position_count: int
    preferred_position_count: int
    analysis_coverage: CoverageState
    preferred_coverage: CoverageState


@dataclass(frozen=True, slots=True)
class GameSummary:
    """A public game summary that deliberately contains no SQLite identifiers."""

    game_uuid: str
    source_url: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: str
    opponent_chesscom_uuid: str | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: TrainerOutcome | None
    termination_reason: str | None
    time_control: str | None
    time_class: str | None
    occurrence_count: int
    length_plies: int
    deepest_opening: DeepestOpening | None
    coverage: GameCoverage


@dataclass(frozen=True, slots=True)
class GameSearchPage:
    """One finite, deterministic page of public game summaries."""

    items: tuple[GameSummary, ...]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool


@dataclass(slots=True)
class _GameData:
    game_uuid: str
    source_url: str
    trainer_color: TrainerColor
    trainer_chesscom_uuid: str
    opponent_chesscom_uuid: str | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    trainer_outcome: TrainerOutcome | None
    termination_reason: str | None
    time_control: str | None
    time_class: str | None
    occurrences: list[tuple[int, int, str | None, CanonicalPosition]]
    opening_matches: dict[str, tuple[str, str, int]]

    @property
    def occurrence_count(self) -> int:
        return len(self.occurrences)

    @property
    def length_plies(self) -> int:
        return max((item[0] for item in self.occurrences), default=0)


