"""HTTP route for read-only move response distributions."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .api_schemas import (
    MoveResponseDistributionErrorResponse,
    MoveResponseDistributionResponse,
)
from .errors import (
    MoveResponseDistributionUnavailableError,
    MoveResponseDistributionValidationError,
)
from .service import get_move_response_distribution

router = APIRouter(prefix="/api", tags=["move-response-distribution"])


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    body = MoveResponseDistributionErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _handle(call):
    try:
        return call()
    except MoveResponseDistributionValidationError as error:
        return _error(422, error.code, error.message)
    except MoveResponseDistributionUnavailableError:
        return _error(
            503,
            "move_response_distribution_unavailable",
            "Move response distribution unavailable",
        )
    except Exception:
        return _error(500, "unexpected_failure", "Unable to serve move response distribution")


@router.get(
    "/move-response-distribution",
    response_model=MoveResponseDistributionResponse,
    responses={
        422: {"model": MoveResponseDistributionErrorResponse},
        500: {"model": MoveResponseDistributionErrorResponse},
        503: {"model": MoveResponseDistributionErrorResponse},
    },
)
def move_response_distribution(
    fen: Annotated[str, Query()],
    color: Annotated[str, Query()],
) -> MoveResponseDistributionResponse | JSONResponse:
    return _handle(lambda: get_move_response_distribution(fen, color))
