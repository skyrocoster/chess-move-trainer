"""Game search validation and normalization."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import chess

from ..openings.keys import OpeningKeyError, opening_api_key, parse_opening_api_key
from ..positions import CanonicalPosition, PositionValidationError, canonicalize_fen
from ..validation import normalize_timestamp_value
from .search_errors import GameSearchStorageError, GameSearchValidationError

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


def _stored_position(fields: object) -> CanonicalPosition:
    try:
        values = tuple(fields)
        if len(values) != 4 or any(not isinstance(value, str) for value in values):
            raise ValueError("position fields")
        position = canonicalize_fen(" ".join((*values, "0", "1")))
        if position != CanonicalPosition(*values):
            raise ValueError("position is not canonical")
        return position
    except (TypeError, ValueError, PositionValidationError) as error:
        raise GameSearchStorageError("stored position is not canonical") from error


def _normalize_fen(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise GameSearchValidationError(f"{field_name} must be a complete legal FEN")
    try:
        position = canonicalize_fen(value)
    except (PositionValidationError, ValueError) as error:
        raise GameSearchValidationError(f"{field_name} is not a valid FEN") from error
    return " ".join(
        (
            position.placement,
            position.side_to_move,
            position.castling_rights,
            position.legal_en_passant,
            "0",
            "1",
        )
    )


def _validate_legal_move(position_fen: str, move_uci: str) -> None:
    if type(move_uci) is not str:
        raise GameSearchValidationError("move_uci must be a legal UCI move")
    try:
        board = chess.Board(position_fen)
        move = chess.Move.from_uci(move_uci)
    except (TypeError, ValueError) as error:
        raise GameSearchValidationError("move_uci must be a legal UCI move") from error
    if move.uci() != move_uci or move not in board.legal_moves:
        raise GameSearchValidationError("move_uci must be legal from move_fen")


def _normalize_timestamp(value: str | datetime | None, field_name: str) -> str | None:
    if value is None:
        return None
    try:
        return normalize_timestamp_value(value, field_name)
    except ValueError as error:
        raise GameSearchValidationError(str(error)) from error


def _in_datetime_bounds(value: str | None, lower: str | None, upper: str | None) -> bool:
    if lower is None and upper is None:
        return True
    if value is None:
        return False
    normalized = _stored_timestamp(value)
    return (lower is None or normalized >= lower) and (upper is None or normalized <= upper)


def _stored_timestamp(value: str) -> str:
    if value.endswith("Z"):
        return value[:-1] + ".000000Z" if "." not in value else value
    return value


def _in_numeric_bounds(value: int | None, lower: int | None, upper: int | None) -> bool:
    if lower is None and upper is None:
        return True
    if value is None:
        return False
    return (lower is None or value >= lower) and (upper is None or value <= upper)


def _require_positive_int(value: object, field_name: str) -> None:
    if type(value) is not int or value < 1:
        raise GameSearchValidationError(f"{field_name} must be a positive integer")


def _require_optional_non_negative_int(value: object, field_name: str) -> None:
    if value is not None and (type(value) is not int or value < 0):
        raise GameSearchValidationError(f"{field_name} must be a non-negative integer")


def _require_ordered_bounds(lower: object, upper: object, field_name: str) -> None:
    if lower is not None and upper is not None and lower > upper:
        raise GameSearchValidationError(f"{field_name} lower bound cannot exceed upper bound")


def _validate_optional_non_empty_text(value: object, field_name: str) -> None:
    if value is not None and (type(value) is not str or not value):
        raise GameSearchValidationError(f"{field_name} must be a non-empty string")


def _opening_api_key(eco: str, name: str) -> str:
    try:
        return opening_api_key(eco, name)
    except OpeningKeyError as error:
        raise ValueError("opening label is malformed") from error


def _parse_opening_key(value: str) -> tuple[str, str]:
    try:
        return parse_opening_api_key(value)
    except OpeningKeyError as error:
        raise ValueError("opening_key must be formatted as ECO:Name") from error
