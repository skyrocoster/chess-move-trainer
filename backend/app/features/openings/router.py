"""HTTP routes for the opening catalogue."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi import Path as FastAPIPath
from fastapi.responses import JSONResponse

from backend.app.caching import (
    get_or_compute,
    json_response,
    opening_detail_key,
    openings_key,
    openings_namespace,
    serialize_response_body,
)
from backend.app.dependencies import get_rebuilt_database_path
from chess_move_trainer.database.openings import (
    OpeningCatalogueQuery,
    OpeningCatalogueSchemaError,
    OpeningCatalogueStorageError,
    OpeningCatalogueValidationError,
    read_opening,
    read_openings,
)

from .catalogue_api_schemas import (
    OpeningCatalogueErrorResponse,
    OpeningCatalogueItemResponse,
    OpeningCatalogueResponse,
    OpeningDetailErrorResponse,
)

router = APIRouter(prefix="/api", tags=["openings"])


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


def _detail_payload(database_path: Path, opening_key: str) -> bytes | None:
    result = read_opening(database_path, opening_key)
    if result is None:
        return None
    return serialize_response_body(_catalogue_item_response(result))


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
        query = OpeningCatalogueQuery(
            page=page,
            page_size=page_size,
            search=search,
            eco_from=eco_from,
            eco_to=eco_to,
            sort=sort,
        )
    except OpeningCatalogueValidationError:
        return _catalogue_error(422, "invalid_filter", "Invalid opening filter")
    key = openings_key(database_path, query)
    try:
        payload = get_or_compute(
            openings_namespace,
            key,
            database_path,
            lambda: serialize_response_body(
                _catalogue_page_response(read_openings(database_path, query))
            ),
        )
    except (OpeningCatalogueSchemaError, OpeningCatalogueStorageError):
        return _catalogue_error(503, "openings_unavailable", "Openings unavailable")
    except Exception:
        return _catalogue_error(500, "unexpected_failure", "Unable to load openings")
    assert payload is not None
    return json_response(payload)


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
    key = opening_detail_key(database_path, opening_key)
    try:
        payload = get_or_compute(
            openings_namespace,
            key,
            database_path,
            lambda: _detail_payload(database_path, opening_key),
        )
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
    if payload is None:
        return _opening_detail_error(
            404, "opening_not_found", "Opening not found"
        )
    return json_response(payload)
