"""Thin HTTP translation layer for scored position training requirements."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.app.dependencies import (
    get_rebuilt_database_path,
    get_training_requirement_policy,
)
from chess_move_trainer.database.positions import (
    TrainingAnswerNotFoundError,
    TrainingAnswerRepository,
    TrainingAnswerRequest as DomainTrainingAnswerRequest,
    TrainingAnswerResult,
    TrainingRequirementItem,
    TrainingRequirementPage,
    TrainingRequirementPolicy,
    TrainingRequirementQuery,
    TrainingRequirementSchemaError,
    TrainingRequirementStaleError,
    TrainingRequirementStorageError,
    TrainingRequirementValidationError,
    discover_training_requirements,
)

from .api_schemas import (
    TrainingAnswerRequest,
    TrainingAnswerResponse,
    TrainingRequirementErrorCode,
    TrainingRequirementErrorResponse,
    TrainingRequirementItemResponse,
    TrainingRequirementPolicyResponse,
    TrainingRequirementResponse,
)

router = APIRouter(prefix="/api", tags=["position-training-requirements"])


def _error(
    status_code: int,
    code: TrainingRequirementErrorCode,
    message: str,
) -> JSONResponse:
    body = TrainingRequirementErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _item_response(item: TrainingRequirementItem) -> TrainingRequirementItemResponse:
    return TrainingRequirementItemResponse(
        fen=item.fen,
        trainer_color=item.trainer_color,
        preferred_move_uci=item.preferred_move_uci,
        encounters=item.encounters,
        hits=item.hits,
        misses=item.misses,
        observed_success_rate=item.public_dict()["observed_success_rate"],
        game_balance=item.public_dict()["game_balance"],
        effective_training_balance=item.public_dict()["effective_training_balance"],
        training_adjustment=item.public_dict()["training_adjustment"],
        training_updated_on=item.training_updated_on,
        training_requirement=item.public_dict()["training_requirement"],
        training_required=item.training_required,
        correct_answers_needed=item.correct_answers_needed,
    )


def _page_response(page: TrainingRequirementPage) -> TrainingRequirementResponse:
    policy = page.scoring_policy
    return TrainingRequirementResponse(
        as_of=page.as_of,
        scoring_policy=TrainingRequirementPolicyResponse(
            target_success_rate=round(policy.target_success_rate, 6),
            game_hit_weight=round(policy.game_hit_weight, 6),
            game_miss_weight=round(policy.game_miss_weight, 6),
            training_curve=policy.training_curve,
            training_credit_half_life_days=round(policy.credit_half_life_days, 6),
        ),
        items=[_item_response(item) for item in page.items],
        page=page.page,
        page_size=page.page_size,
        total=page.total,
    )


def _answer_response(result: TrainingAnswerResult) -> TrainingAnswerResponse:
    return TrainingAnswerResponse(
        as_of=result.as_of,
        correct=result.correct,
        item=_item_response(result.item),
    )


def _validation_error(error: TrainingRequirementValidationError) -> JSONResponse:
    message = str(error)
    if "trainer_color" in message:
        return _error(422, "invalid_trainer_color", "trainer_color must be 'white' or 'black'")
    if "as_of" in message:
        return _error(422, "invalid_as_of", "as_of must be a literal YYYY-MM-DD date")
    if "fen" in message.lower():
        return _error(422, "invalid_fen", "FEN is invalid")
    if "played_move_uci" in message or "uci" in message:
        return _error(422, "invalid_played_move_uci", "played_move_uci is invalid")
    if "opening" in message:
        return _error(422, "invalid_opening_filter", "The opening filter is invalid")
    if "page" in message:
        return _error(422, "invalid_pagination", "The page controls are invalid")
    return _error(
        422,
        "invalid_requirement_range",
        "At least one finite training-requirement boundary is required",
    )


def _unavailable() -> JSONResponse:
    return _error(
        503,
        "position_training_requirements_unavailable",
        "Position training requirements unavailable",
    )


@router.get(
    "/positions/training-requirements",
    response_model=TrainingRequirementResponse,
    operation_id="getPositionTrainingRequirements",
    responses={
        422: {"model": TrainingRequirementErrorResponse},
        409: {"model": TrainingRequirementErrorResponse},
        500: {"model": TrainingRequirementErrorResponse},
        503: {"model": TrainingRequirementErrorResponse},
    },
)
def get_position_training_requirements(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    policy: Annotated[TrainingRequirementPolicy | None, Depends(get_training_requirement_policy)],
    as_of: Annotated[str, Query()],
    training_requirement_gt: Annotated[float | None, Query()] = None,
    training_requirement_gte: Annotated[float | None, Query()] = None,
    training_requirement_lt: Annotated[float | None, Query()] = None,
    training_requirement_lte: Annotated[float | None, Query()] = None,
    opening_key: Annotated[str | None, Query()] = None,
    opening_match: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query()] = 1,
    page_size: Annotated[int, Query()] = 50,
) -> TrainingRequirementResponse | JSONResponse:
    if policy is None:
        return _unavailable()
    try:
        query = TrainingRequirementQuery(
            as_of=as_of,
            training_requirement_gt=training_requirement_gt,
            training_requirement_gte=training_requirement_gte,
            training_requirement_lt=training_requirement_lt,
            training_requirement_lte=training_requirement_lte,
            opening_key=opening_key,
            opening_match=opening_match,
            page=page,
            page_size=page_size,
        )
        return _page_response(discover_training_requirements(database_path, query, policy))
    except TrainingRequirementValidationError as error:
        return _validation_error(error)
    except TrainingRequirementStaleError:
        return _error(
            409,
            "training_requirements_stale",
            "Training requirement state is newer than as_of",
        )
    except (TrainingRequirementSchemaError, TrainingRequirementStorageError):
        return _unavailable()
    except Exception:
        return _error(
            500,
            "unexpected_failure",
            "Unable to serve position training requirements",
        )


@router.post(
    "/positions/training-requirements/answers",
    response_model=TrainingAnswerResponse,
    operation_id="submitPositionTrainingAnswer",
    responses={
        404: {"model": TrainingRequirementErrorResponse},
        409: {"model": TrainingRequirementErrorResponse},
        422: {"model": TrainingRequirementErrorResponse},
        500: {"model": TrainingRequirementErrorResponse},
        503: {"model": TrainingRequirementErrorResponse},
    },
)
def submit_position_training_answer(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    policy: Annotated[TrainingRequirementPolicy | None, Depends(get_training_requirement_policy)],
    payload: TrainingAnswerRequest,
) -> TrainingAnswerResponse | JSONResponse:
    if policy is None:
        return _unavailable()
    try:
        request = DomainTrainingAnswerRequest(
            fen=payload.fen,
            trainer_color=payload.trainer_color,
            as_of=payload.as_of,
            played_move_uci=payload.played_move_uci,
        )
        result = TrainingAnswerRepository(database_path).submit(request, policy)
        return _answer_response(result)
    except TrainingRequirementValidationError as error:
        return _validation_error(error)
    except TrainingAnswerNotFoundError:
        return _error(
            404,
            "training_requirement_not_found",
            "Current training requirement not found",
        )
    except TrainingRequirementStaleError:
        return _error(
            409,
            "training_requirements_stale",
            "Training requirement state is newer than as_of",
        )
    except (TrainingRequirementSchemaError, TrainingRequirementStorageError):
        return _unavailable()
    except Exception:
        return _error(
            500,
            "unexpected_failure",
            "Unable to submit position training answer",
        )


__all__ = [
    "get_position_training_requirements",
    "router",
    "submit_position_training_answer",
]
