"""HTTP routes for the clean opening catalogue and legacy Line Library provider."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Path as FastAPIPath, Query
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_rebuilt_database_path
from chess_move_trainer.database.openings import (
    OpeningCatalogueQuery,
    OpeningCatalogueSchemaError,
    OpeningCatalogueStorageError,
    OpeningCatalogueValidationError,
    read_opening,
    read_openings,
)

from .api_schemas import LineLibraryErrorResponse, LineLibraryResponse
from .catalogue_api_schemas import (
    OpeningCatalogueErrorResponse,
    OpeningCatalogueItemResponse,
    OpeningCatalogueResponse,
    OpeningDetailErrorResponse,
)
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


def _catalogue_error(status_code: int, code: str, message: str) -> JSONResponse:
    body = OpeningCatalogueErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _opening_detail_error(status_code: int, code: str, message: str) -> JSONResponse:
    body = OpeningDetailErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _catalogue_item_response(item: object) -> OpeningCatalogueItemResponse:
    return OpeningCatalogueItemResponse(
        key=item.key,
        eco=item.eco,
        name=item.name,
        route_count=item.route_count,
        games_reached=item.games_reached,
        games_deepest=item.games_deepest,
    )


def _catalogue_page_response(page: object) -> OpeningCatalogueResponse:
    return OpeningCatalogueResponse(
        items=[
            _catalogue_item_response(item)
            for item in page.items
        ],
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        total_pages=page.total_pages,
        has_next=page.has_next,
    )


@router.get(
    "/openings",
    response_model=OpeningCatalogueResponse,
    operation_id="getOpenings",
    responses={
        422: {"model": OpeningCatalogueErrorResponse},
        500: {"model": OpeningCatalogueErrorResponse},
        503: {"model": OpeningCatalogueErrorResponse},
    },
)
def get_openings(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    page: Annotated[int, Query()] = 1,
    page_size: Annotated[int, Query()] = 50,
    search: Annotated[str | None, Query()] = None,
    eco_from: Annotated[str | None, Query()] = None,
    eco_to: Annotated[str | None, Query()] = None,
    sort: Annotated[str, Query()] = "eco_asc",
) -> OpeningCatalogueResponse | JSONResponse:
    try:
        result = read_openings(
            database_path,
            OpeningCatalogueQuery(
                page=page,
                page_size=page_size,
                search=search,
                eco_from=eco_from,
                eco_to=eco_to,
                sort=sort,
            ),
        )
        return _catalogue_page_response(result)
    except OpeningCatalogueValidationError:
        return _catalogue_error(422, "invalid_filter", "Invalid opening filter")
    except (OpeningCatalogueSchemaError, OpeningCatalogueStorageError):
        return _catalogue_error(503, "openings_unavailable", "Openings unavailable")
    except Exception:
        return _catalogue_error(500, "unexpected_failure", "Unable to load openings")


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


@router.get(
    "/openings/{opening_key}",
    response_model=OpeningCatalogueItemResponse,
    operation_id="getOpeningByKey",
    responses={
        404: {"model": OpeningDetailErrorResponse},
        422: {"model": OpeningDetailErrorResponse},
        500: {"model": OpeningDetailErrorResponse},
        503: {"model": OpeningDetailErrorResponse},
    },
)
def get_opening_by_key(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    opening_key: Annotated[str, FastAPIPath()],
) -> OpeningCatalogueItemResponse | JSONResponse:
    try:
        result = read_opening(database_path, opening_key)
        if result is None:
            return _opening_detail_error(
                404, "opening_not_found", "Opening not found"
            )
        return _catalogue_item_response(result)
    except OpeningCatalogueValidationError:
        return _opening_detail_error(
            422, "invalid_opening_key", "Invalid opening key"
        )
    except (OpeningCatalogueSchemaError, OpeningCatalogueStorageError):
        return _opening_detail_error(
            503, "openings_unavailable", "Openings unavailable"
        )
    except Exception:
        return _opening_detail_error(
            500, "unexpected_failure", "Unable to load opening"
        )
