"""HTTP route for neutral recurrence context."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .api_schemas import PositionContextErrorResponse, PositionContextResponse
from .errors import PositionContextUnavailableError, PositionContextValidationError
from .service import get_position_context

router = APIRouter(prefix="/api", tags=["position-context"])


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    body = PositionContextErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _handle(call):
    try:
        return call()
    except PositionContextValidationError as error:
        return _error(422, error.code, error.message)
    except PositionContextUnavailableError:
        return _error(503, "position_context_unavailable", "Position context unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to serve position context")


@router.get(
    "/position-context",
    response_model=PositionContextResponse,
    responses={
        422: {"model": PositionContextErrorResponse},
        500: {"model": PositionContextErrorResponse},
        503: {"model": PositionContextErrorResponse},
    },
)
def position_context(
    fen: Annotated[str, Query()],
) -> PositionContextResponse | JSONResponse:
    return _handle(lambda: get_position_context(fen))
