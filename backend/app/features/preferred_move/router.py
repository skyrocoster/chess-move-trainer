"""HTTP routes for the fixed-owner preferred-move lifecycle."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .api_schemas import (
    PreferredMoveErrorResponse,
    PreferredMoveMutationResponse,
    PreferredMoveRequest,
    PreferredMoveResponse,
)
from .errors import (
    PreferredMovePositionNotFoundError,
    PreferredMoveUnavailableError,
    PreferredMoveValidationError,
)
from .service import get_preferred_move, remove_preferred_move, set_preferred_move

router = APIRouter(prefix="/api", tags=["preferred-move"])


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    body = PreferredMoveErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _handle(call):
    try:
        return call()
    except PreferredMoveValidationError as error:
        return _error(422, error.code, error.message)
    except PreferredMovePositionNotFoundError:
        return _error(404, "position_not_found", "Position not found")
    except PreferredMoveUnavailableError:
        return _error(503, "preferred_move_unavailable", "Preferred-move data unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to serve preferred move")


@router.get(
    "/preferred-move",
    response_model=PreferredMoveResponse,
    responses={
        404: {"model": PreferredMoveErrorResponse},
        422: {"model": PreferredMoveErrorResponse},
        500: {"model": PreferredMoveErrorResponse},
        503: {"model": PreferredMoveErrorResponse},
    },
)
def preferred_move(
    fen: Annotated[str, Query()],
    as_of: Annotated[str | None, Query()] = None,
) -> PreferredMoveResponse | JSONResponse:
    return _handle(lambda: get_preferred_move(fen, as_of))


@router.put(
    "/preferred-move",
    response_model=PreferredMoveMutationResponse,
    responses={
        404: {"model": PreferredMoveErrorResponse},
        422: {"model": PreferredMoveErrorResponse},
        500: {"model": PreferredMoveErrorResponse},
        503: {"model": PreferredMoveErrorResponse},
    },
)
def put_preferred_move(
    payload: PreferredMoveRequest,
) -> PreferredMoveMutationResponse | JSONResponse:
    return _handle(lambda: set_preferred_move(payload.fen, payload.move_uci, payload.effective_at))


@router.delete(
    "/preferred-move",
    response_model=PreferredMoveMutationResponse,
    responses={
        404: {"model": PreferredMoveErrorResponse},
        422: {"model": PreferredMoveErrorResponse},
        500: {"model": PreferredMoveErrorResponse},
        503: {"model": PreferredMoveErrorResponse},
    },
)
def delete_preferred_move(
    fen: Annotated[str, Query()],
    effective_at: Annotated[str | None, Query()] = None,
) -> PreferredMoveMutationResponse | JSONResponse:
    return _handle(lambda: remove_preferred_move(fen, effective_at))
