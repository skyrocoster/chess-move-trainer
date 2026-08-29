"""Validation and orchestration for one fixed-owner preferred move."""

from __future__ import annotations

from datetime import UTC, datetime

import chess
from pydantic import ValidationError

from backend.app.features.analysis.models import canonical_fen
from scripts.opening_catalog.preferred_move import PreferredMoveError, _normalise_utc

from .api_schemas import (
    PreferredMoveMutationResponse,
    PreferredMoveResponse,
    PreferredMoveValue,
)
from .errors import PreferredMoveValidationError
from .repository import (
    PositionKey,
    PreferredMoveRepository,
    open_read_connection,
    open_write_connection,
)


def _validated_fen(value: str) -> tuple[str, PositionKey]:
    try:
        selected = canonical_fen(value)
    except (TypeError, ValidationError, ValueError) as error:
        raise PreferredMoveValidationError("invalid_fen", "FEN is invalid") from error
    fields = tuple(selected.split(" ")[:4])
    if len(fields) != 4:
        raise PreferredMoveValidationError("invalid_fen", "FEN is invalid")
    return selected, fields  # type: ignore[return-value]


def _normalise_timestamp(value: str) -> tuple[str, datetime]:
    try:
        return _normalise_utc(value)
    except (PreferredMoveError, TypeError, ValueError) as error:
        raise PreferredMoveValidationError(
            "invalid_timestamp", "timestamp must be an ISO-8601 UTC datetime"
        ) from error


def _read_timestamp(value: str | None) -> str:
    if value is None or not value.strip():
        if value is not None:
            raise PreferredMoveValidationError("invalid_timestamp", "as_of cannot be blank")
        return _normalise_utc(datetime.now(UTC))[0]
    return _normalise_timestamp(value)[0]


def _mutation_timestamp(value: str | None) -> str:
    now = datetime.now(UTC)
    if value is None or not value.strip():
        return _normalise_utc(now)[0]
    selected, selected_value = _normalise_timestamp(value)
    if selected_value > now:
        raise PreferredMoveValidationError(
            "future_effective_time", "effective_at cannot be in the future"
        )
    return selected


def _canonical_move(fen: str, move_uci: str) -> str:
    try:
        board = chess.Board(fen)
        move = board.parse_uci(move_uci)
    except (TypeError, ValueError) as error:
        raise PreferredMoveValidationError(
            "invalid_move", "move_uci is not a legal UCI move"
        ) from error
    canonical = move.uci()
    if canonical != move_uci:
        raise PreferredMoveValidationError("invalid_move", "move_uci must be canonical UCI")
    return canonical


def _response(fen: str, state: object) -> PreferredMoveResponse:
    move_uci = state.move_uci
    move_san = state.move_san
    if (move_uci is None) != (move_san is None):
        raise RuntimeError("preferred-move event snapshot is incomplete")
    move = None if move_uci is None else PreferredMoveValue(uci=move_uci, san=move_san)
    return PreferredMoveResponse(
        fen=fen,
        state="unassigned" if move is None else "assigned",
        move=move,
    )


def get_preferred_move(fen: str, as_of: str | None) -> PreferredMoveResponse:
    selected_fen, key = _validated_fen(fen)
    effective_at = _read_timestamp(as_of)
    connection = open_read_connection()
    try:
        repository = PreferredMoveRepository(connection)
        position = repository.position(key)
        state = repository.state_at(position, effective_at)
        return _response(selected_fen, state)
    finally:
        connection.close()


def _mutate(fen: str, move_uci: str | None, effective_at: str | None):
    selected_fen, key = _validated_fen(fen)
    canonical_move = None if move_uci is None else _canonical_move(selected_fen, move_uci)
    selected_time = _mutation_timestamp(effective_at)
    connection = open_write_connection()
    try:
        repository = PreferredMoveRepository(connection)
        position = repository.position(key)
        result = repository.append(position, canonical_move, selected_time)
        return PreferredMoveMutationResponse(
            fen=selected_fen,
            changed=result.changed,
            effective_at=result.effective_at.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
        )
    finally:
        connection.close()


def set_preferred_move(fen: str, move_uci: str, effective_at: str | None):
    return _mutate(fen, move_uci, effective_at)


def remove_preferred_move(fen: str, effective_at: str | None):
    return _mutate(fen, None, effective_at)
