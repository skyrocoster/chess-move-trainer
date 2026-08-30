"""Validation and orchestration for neutral position context."""

from __future__ import annotations

from backend.app.features.analysis.models import canonical_fen

from .api_schemas import PositionContextResponse
from .errors import PositionContextValidationError
from .repository import PositionContextRepository, open_read_connection

PositionKey = tuple[str, str, str, str]


def _validated_fen(value: str) -> tuple[str, PositionKey]:
    try:
        selected = canonical_fen(value)
    except (TypeError, ValueError) as error:
        raise PositionContextValidationError("invalid_fen", "FEN is invalid") from error
    fields = tuple(selected.split(" ")[:4])
    if len(fields) != 4:
        raise PositionContextValidationError("invalid_fen", "FEN is invalid")
    return selected, fields  # type: ignore[return-value]


def get_position_context(fen: str) -> PositionContextResponse:
    selected_fen, key = _validated_fen(fen)
    connection = open_read_connection()
    try:
        context = PositionContextRepository(connection).lookup(key)
        return PositionContextResponse(
            fen=selected_fen,
            overall_exists=context.overall_exists,
            white_count=context.white_count,
            black_count=context.black_count,
            white_total=context.white_total,
            black_total=context.black_total,
        )
    finally:
        connection.close()
