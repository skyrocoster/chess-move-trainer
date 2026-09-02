"""Validation and orchestration for move response distributions."""

from __future__ import annotations

import chess

from backend.app.features.analysis.models import canonical_fen

from .api_schemas import MoveResponseDistributionResponse, MoveResponseReply
from .errors import (
    MoveResponseDistributionUnavailableError,
    MoveResponseDistributionValidationError,
)
from .repository import (
    MoveResponseBranch,
    MoveResponseDistributionRepository,
    open_read_connection,
)

PositionKey = tuple[str, str, str, str]


def _validated_fen(value: str) -> tuple[str, PositionKey]:
    try:
        selected = canonical_fen(value)
    except (TypeError, ValueError) as error:
        raise MoveResponseDistributionValidationError("invalid_fen", "FEN is invalid") from error
    fields = tuple(selected.split(" ")[:4])
    if len(fields) != 4:
        raise MoveResponseDistributionValidationError("invalid_fen", "FEN is invalid")
    return selected, fields  # type: ignore[return-value]


def _validated_color(value: str) -> str:
    if value not in {"white", "black"}:
        raise MoveResponseDistributionValidationError(
            "invalid_color", "color must be 'white' or 'black'"
        )
    return value


def _normalised_replies(
    fen: str,
    branches: tuple[MoveResponseBranch, ...],
) -> list[tuple[str, str, int]]:
    board = chess.Board(fen)
    normalised: list[tuple[str, str, int]] = []
    seen: set[str] = set()
    for branch in branches:
        child_uci = branch.child_uci
        distinct_game_count = branch.distinct_game_count
        if (
            not isinstance(child_uci, str)
            or not child_uci
            or isinstance(distinct_game_count, bool)
            or not isinstance(distinct_game_count, int)
            or distinct_game_count < 0
        ):
            raise MoveResponseDistributionUnavailableError
        try:
            move = board.parse_uci(child_uci)
            canonical_uci = move.uci()
            if canonical_uci != child_uci:
                raise ValueError("child UCI is not canonical")
            san = board.san(move)
        except (TypeError, ValueError) as error:
            raise MoveResponseDistributionUnavailableError from error
        if canonical_uci in seen:
            raise MoveResponseDistributionUnavailableError
        seen.add(canonical_uci)
        normalised.append((canonical_uci, san, distinct_game_count))
    return sorted(normalised, key=lambda item: (-item[2], item[0]))


def get_move_response_distribution(
    fen: str,
    color: str,
) -> MoveResponseDistributionResponse:
    selected_fen, key = _validated_fen(fen)
    selected_color = _validated_color(color)
    connection = open_read_connection()
    try:
        read = MoveResponseDistributionRepository(connection).lookup(key, selected_color)
        matching_game_count = read.matching_game_count
        if (
            matching_game_count is None
            or isinstance(matching_game_count, bool)
            or not isinstance(matching_game_count, int)
            or matching_game_count < 0
        ):
            matching_game_count = 0 if matching_game_count is None else matching_game_count
        if (
            isinstance(matching_game_count, bool)
            or not isinstance(matching_game_count, int)
            or matching_game_count < 0
        ):
            raise MoveResponseDistributionUnavailableError

        replies = [
            MoveResponseReply(
                rank=rank,
                child_uci=child_uci,
                san=san,
                distinct_game_count=distinct_game_count,
                opening_name=None,
            )
            for rank, (child_uci, san, distinct_game_count) in enumerate(
                _normalised_replies(selected_fen, read.branches), start=1
            )
        ]
        return MoveResponseDistributionResponse(
            fen=selected_fen,
            color=selected_color,
            matching_game_count=matching_game_count,
            replies=replies,
        )
    finally:
        connection.close()
