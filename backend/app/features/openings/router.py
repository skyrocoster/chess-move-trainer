"""HTTP route for the production opening Line Library provider."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .api_schemas import LineLibraryErrorResponse, LineLibraryResponse
from .errors import OpeningLineLibraryUnavailableError, OpeningLineLibraryValidationError
from .service import get_opening_line_library

router = APIRouter(prefix="/api", tags=["openings"])


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    body = LineLibraryErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _handle(call):
    try:
        return call()
    except OpeningLineLibraryValidationError as error:
        return _error(422, error.code, error.message)
    except OpeningLineLibraryUnavailableError:
        return _error(503, "line_library_unavailable", "Opening Line Library unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to serve opening Line Library")


@router.get(
    "/openings/line-library",
    response_model=LineLibraryResponse,
    responses={
        422: {"model": LineLibraryErrorResponse},
        500: {"model": LineLibraryErrorResponse},
        503: {"model": LineLibraryErrorResponse},
    },
)
def opening_line_library(
    search: Annotated[str | None, Query()] = None,
    eco_from: Annotated[str | None, Query()] = None,
    eco_to: Annotated[str | None, Query()] = None,
    appears_in_my_games: Annotated[bool, Query()] = False,
    sort: Annotated[str | None, Query()] = None,
) -> LineLibraryResponse | JSONResponse:
    return _handle(
        lambda: get_opening_line_library(
            search,
            eco_from,
            eco_to,
            appears_in_my_games,
            sort,
        )
    )
