"""Thin HTTP translation layer for trainer blunder discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.app.caching import (
    get_or_compute,
    json_response,
    read_namespace,
    serialize_response_body,
    trainer_blunders_key,
)
from backend.app.dependencies import get_blunder_policy, get_rebuilt_database_path
from chess_move_trainer.database.blunders import (
    BlunderItem,
    BlunderPage,
    BlunderPolicy,
    BlunderQuery,
    BlunderSchemaError,
    BlunderStorageError,
    BlunderValidationError,
    discover_blunders,
)

from .api_schemas import (
    BlunderCoverageResponse,
    BlunderErrorCode,
    BlunderErrorResponse,
    BlunderPolicyResponse,
    BlunderTimeframeResponse,
    TrainerBlunderItemResponse,
    TrainerBlundersResponse,
)

router = APIRouter(prefix="/api", tags=["trainer"])


def _error(status_code: int, code: BlunderErrorCode, message: str) -> JSONResponse:
    body = BlunderErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _item_response(item: BlunderItem) -> TrainerBlunderItemResponse:
    return TrainerBlunderItemResponse(
        game_uuid=UUID(item.game_uuid),
        source_url=item.source_url,
        started_at_utc=item.started_at_utc,
        trainer_color=item.trainer_color,
        ply=item.ply,
        fen=item.fen,
        played_move_uci=item.played_move_uci,
        preferred_move_uci=item.preferred_move_uci,
        expected_score_before=item.expected_score_before,
        expected_score_after=item.expected_score_after,
        expected_score_loss=item.expected_score_loss,
        before_analysis_quality=item.before_analysis_quality,
        after_analysis_quality=item.after_analysis_quality,
    )


def _page_response(page: BlunderPage) -> TrainerBlundersResponse:
    return TrainerBlundersResponse(
        timeframe=BlunderTimeframeResponse(
            started_at_from=page.started_at_from,
            started_at_to=page.started_at_to,
        ),
        policy=BlunderPolicyResponse(
            minimum_expected_score_loss=page.policy.minimum_expected_score_loss,
            evaluation_basis="wdl_expected_score",
            score_perspective="trainer",
        ),
        coverage=BlunderCoverageResponse(
            examined_game_count=page.examined_game_count,
            excluded_game_count=page.excluded_game_count,
            in_scope_game_count=page.in_scope_game_count,
            trainer_move_count=page.trainer_move_count,
            comparable_move_count=page.comparable_move_count,
            skipped_missing_analysis_count=page.skipped_missing_analysis_count,
        ),
        items=[_item_response(item) for item in page.items],
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        total_pages=page.total_pages,
        has_next=page.has_next,
    )


def _unavailable() -> JSONResponse:
    return _error(
        503,
        "trainer_blunders_unavailable",
        "Trainer blunders unavailable",
    )


@router.get(
    "/trainer/blunders",
    response_model=TrainerBlundersResponse,
    operation_id="getTrainerBlunders",
    responses={
        422: {"model": BlunderErrorResponse},
        500: {"model": BlunderErrorResponse},
        503: {"model": BlunderErrorResponse},
    },
)
def get_trainer_blunders(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    policy: Annotated[BlunderPolicy | None, Depends(get_blunder_policy)],
    started_at_from: Annotated[str, Query()],
    started_at_to: Annotated[str, Query()],
    trainer_color: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 1,
    page_size: Annotated[int, Query()] = 50,
) -> TrainerBlundersResponse | JSONResponse:
    if policy is None:
        return _unavailable()
    try:
        query = BlunderQuery(
            started_at_from=started_at_from,
            started_at_to=started_at_to,
            trainer_color=trainer_color,
            page=page,
            page_size=page_size,
        )
    except BlunderValidationError:
        return _error(422, "invalid_filter", "Invalid blunder timeframe or filter")

    key = trainer_blunders_key(database_path, query, policy)
    try:
        payload = get_or_compute(
            read_namespace,
            key,
            database_path,
            lambda: serialize_response_body(
                _page_response(discover_blunders(database_path, query, policy))
            ),
        )
    except (BlunderSchemaError, BlunderStorageError):
        return _unavailable()
    except Exception:
        return _error(500, "unexpected_failure", "Unable to load trainer blunders")
    assert payload is not None
    return json_response(payload)


__all__ = ["get_trainer_blunders", "router"]
