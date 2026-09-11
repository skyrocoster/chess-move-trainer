"""Game search matching, sorting, and coverage."""

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
from .search_validation import _in_datetime_bounds, _in_numeric_bounds
from .search_models import CoverageState, GameSearchQuery, GameSearchSort, GameSummary, _GameData


def _matches(game: _GameData, summary: GameSummary, query: GameSearchQuery) -> bool:
    if not _in_datetime_bounds(game.started_at_utc, query.started_at_from, query.started_at_to):
        return False
    if not _in_datetime_bounds(game.ended_at_utc, query.ended_at_from, query.ended_at_to):
        return False
    if query.trainer_color is not None and game.trainer_color != query.trainer_color:
        return False
    if query.trainer_outcome is not None and game.trainer_outcome != query.trainer_outcome:
        return False
    if query.termination_reason is not None and (
        game.termination_reason is None
        or game.termination_reason.strip().casefold() != query.termination_reason
    ):
        return False
    if not _in_numeric_bounds(game.trainer_rating, query.trainer_rating_min, query.trainer_rating_max):
        return False
    if not _in_numeric_bounds(game.opponent_rating, query.opponent_rating_min, query.opponent_rating_max):
        return False
    if query.opponent_chesscom_uuid is not None and game.opponent_chesscom_uuid != query.opponent_chesscom_uuid:
        return False
    if query.time_class is not None and game.time_class != query.time_class:
        return False
    if query.time_control is not None and game.time_control != query.time_control:
        return False
    if query.opening_key is not None:
        assert query.opening_match is not None
        if query.opening_match == "reached":
            if query.opening_key not in game.opening_matches:
                return False
        elif summary.deepest_opening is None or summary.deepest_opening.key != query.opening_key:
            return False
    if query.contains_fen is not None:
        expected = canonicalize_fen(query.contains_fen)
        if not any(occurrence[3] == expected for occurrence in game.occurrences):
            return False
    if query.move_fen is not None:
        expected = canonicalize_fen(query.move_fen)
        if not any(
            occurrence[3] == expected and occurrence[2] == query.move_uci
            for occurrence in game.occurrences
        ):
            return False
    if query.min_length_plies is not None and summary.length_plies < query.min_length_plies:
        return False
    if query.max_length_plies is not None and summary.length_plies > query.max_length_plies:
        return False
    if query.analysis_coverage is not None and summary.coverage.analysis_coverage != query.analysis_coverage:
        return False
    if query.preferred_coverage is not None and summary.coverage.preferred_coverage != query.preferred_coverage:
        return False
    return True


def _compare_games(left: GameSummary, right: GameSummary, sort: GameSearchSort) -> int:
    if sort.startswith("started_at_"):
        field = "started_at_utc"
    elif sort.startswith("length_"):
        field = "length_plies"
    elif sort.startswith("trainer_rating_"):
        field = "trainer_rating"
    elif sort.startswith("opponent_rating_"):
        field = "opponent_rating"
    elif sort.startswith("opponent_uuid_"):
        field = "opponent_chesscom_uuid"
    else:
        field = "game_uuid"
    descending = sort.endswith("_desc")
    result = _compare_nullable(getattr(left, field), getattr(right, field), descending)
    if result:
        return result
    if field != "game_uuid":
        return _compare_nullable(left.game_uuid, right.game_uuid, False)
    return 0


def _compare_nullable(left: object, right: object, descending: bool) -> int:
    if left is None:
        return 0 if right is None else 1
    if right is None:
        return -1
    result = (left > right) - (left < right)
    return -result if descending else result


def _coverage_state(distinct_count: int, covered_count: int) -> CoverageState:
    if covered_count == 0:
        return "none"
    if covered_count == distinct_count:
        return "complete"
    return "partial"


