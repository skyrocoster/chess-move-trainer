"""Thin HTTP translation layer for finite preferred-move timelines."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_rebuilt_database_path
from chess_move_trainer.database.preferred_moves import (
    NormalizedPeriod,
    Preference,
    PreferenceState,
    PreferredMoveMutationRequest,
    PreferredMoveMutationResult,
    PreferredMoveRemovalRequest,
    PreferredMoveRemovalResult,
    PreferredMoveSchemaError,
    PreferredMoveStorageError,
    PreferredMoveTimeline,
    PreferredMoveTimelinePreference,
    PreferredMoveTimelineSegment,
    PreferredMoveValidationError,
    delete_preferred_move,
    put_preferred_move,
    read_preferred_moves,
)

from .api_schemas import (
    MovePreferenceResponse,
    MutationMovePreferenceRequest,
    NoPreferenceResponse,
    PreferredMovesErrorCode,
    PreferredMovesErrorResponse,
    PreferredMovesMutationRequest,
    PreferredMovesMutationResponse,
    PreferredMovesPeriodResponse,
    PreferredMovesPreferenceResponse,
    PreferredMovesRemovalRequest,
    PreferredMovesRemovalResponse,
    PreferredMovesResponse,
    PreferredMovesSegmentResponse,
    UnconfiguredPreferenceResponse,
)

router = APIRouter(prefix="/api", tags=["preferred-moves"])


def _error(
    status_code: int,
    code: PreferredMovesErrorCode,
    message: str,
) -> JSONResponse:
    body = PreferredMovesErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _preference_response(
    preference: PreferredMoveTimelinePreference,
) -> PreferredMovesPreferenceResponse:
    if preference.kind == "move":
        return MovePreferenceResponse(kind="move", uci=preference.uci or "")
    if preference.kind == "no_preference":
        return NoPreferenceResponse(kind="no_preference")
    return UnconfiguredPreferenceResponse(kind="unconfigured")


def _segment_response(
    segment: PreferredMoveTimelineSegment,
) -> PreferredMovesSegmentResponse:
    return PreferredMovesSegmentResponse(
        from_date=segment.from_date,
        until=segment.until,
        preference=_preference_response(segment.preference),
    )


def _response(timeline: PreferredMoveTimeline) -> PreferredMovesResponse:
    return PreferredMovesResponse(
        fen=timeline.fen,
        from_date=timeline.from_date,
        until=timeline.until,
        segments=[_segment_response(segment) for segment in timeline.segments],
    )


def _mutation_preference(payload: PreferredMovesMutationRequest) -> Preference:
    preference = payload.preference
    if isinstance(preference, MutationMovePreferenceRequest):
        try:
            return Preference.preferred_move(preference.uci)
        except ValueError as error:
            raise PreferredMoveValidationError("UCI move is invalid") from error
    if "uci" in preference.model_fields_set:
        raise PreferredMoveValidationError("Preference is invalid")
    return Preference.no_preference()


def _mutation_preference_response(preference: Preference):
    if preference.state is PreferenceState.PREFERRED_MOVE:
        return MovePreferenceResponse(kind="move", uci=preference.move or "")
    return NoPreferenceResponse(kind="no_preference")


def _mutation_period_response(period: NormalizedPeriod) -> PreferredMovesPeriodResponse:
    return PreferredMovesPeriodResponse(
        effective_from=period.effective_from.isoformat(),
        effective_until=(
            None
            if period.effective_until is None
            else period.effective_until.isoformat()
        ),
        preference=_mutation_preference_response(period.preference),
    )


def _mutation_response(result: PreferredMoveMutationResult) -> PreferredMovesMutationResponse:
    return PreferredMovesMutationResponse(
        fen=result.fen,
        effective_from=result.effective_from,
        effective_until=result.effective_until,
        preference=_mutation_preference_response(result.preference),
        periods=[_mutation_period_response(period) for period in result.periods],
    )


def _removal_response(result: PreferredMoveRemovalResult) -> PreferredMovesRemovalResponse:
    return PreferredMovesRemovalResponse(
        fen=result.fen,
        effective_from=result.effective_from,
        effective_until=result.effective_until,
        periods=[_mutation_period_response(period) for period in result.periods],
    )


def _validation_error(error: PreferredMoveValidationError) -> JSONResponse:
    message = str(error)
    if message.startswith("fen "):
        return _error(422, "invalid_fen", "FEN is invalid")
    if message.startswith("from must be earlier"):
        return _error(422, "invalid_window", "from must be earlier than until")
    if message.startswith("from "):
        return _error(422, "invalid_from", "from must be a literal YYYY-MM-DD date")
    if message.startswith("until "):
        return _error(422, "invalid_until", "until must be a literal YYYY-MM-DD date")
    return _error(422, "invalid_window", "The preferred-move window is invalid")


def _mutation_validation_error(error: PreferredMoveValidationError) -> JSONResponse:
    message = str(error)
    mapping = {
        "FEN is invalid": ("invalid_fen", "FEN is invalid"),
        "effective_from must be a literal YYYY-MM-DD date": (
            "invalid_effective_from",
            "effective_from must be a literal YYYY-MM-DD date",
        ),
        "effective_until must be a literal YYYY-MM-DD date": (
            "invalid_effective_until",
            "effective_until must be a literal YYYY-MM-DD date",
        ),
        "effective_until must be later than effective_from": (
            "invalid_window",
            "effective_until must be later than effective_from",
        ),
        "Preference is invalid": ("invalid_preference", "Preference is invalid"),
        "UCI move is invalid": ("invalid_uci", "UCI move is invalid"),
        "Move is illegal from the parent FEN": (
            "illegal_move",
            "Move is illegal from the parent FEN",
        ),
    }
    code, stable_message = mapping.get(
        message, ("invalid_preference", "Preference is invalid")
    )
    return _error(422, code, stable_message)


def _removal_validation_error(error: PreferredMoveValidationError) -> JSONResponse:
    mapping = {
        "FEN is invalid": ("invalid_fen", "FEN is invalid"),
        "effective_from must be a literal YYYY-MM-DD date": (
            "invalid_effective_from",
            "effective_from must be a literal YYYY-MM-DD date",
        ),
        "effective_until must be a literal YYYY-MM-DD date": (
            "invalid_effective_until",
            "effective_until must be a literal YYYY-MM-DD date",
        ),
        "effective_until must be later than effective_from": (
            "invalid_window",
            "effective_until must be later than effective_from",
        ),
    }
    code, message = mapping[str(error)]
    return _error(422, code, message)


@router.get(
    "/preferred-moves",
    response_model=PreferredMovesResponse,
    operation_id="getPreferredMoves",
    responses={
        422: {"model": PreferredMovesErrorResponse},
        500: {"model": PreferredMovesErrorResponse},
        503: {"model": PreferredMovesErrorResponse},
    },
)
def get_preferred_moves(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    fen: Annotated[str, Query(alias="fen")],
    from_date: Annotated[str, Query(alias="from")],
    until: Annotated[str, Query(alias="until")],
) -> PreferredMovesResponse | JSONResponse:
    try:
        timeline = read_preferred_moves(database_path, fen, from_date, until)
        return _response(timeline)
    except PreferredMoveValidationError as error:
        return _validation_error(error)
    except (PreferredMoveSchemaError, PreferredMoveStorageError):
        return _error(
            503,
            "preferred_moves_unavailable",
            "Preferred moves unavailable",
        )
    except Exception:
        return _error(500, "unexpected_failure", "Unable to serve preferred moves")


@router.put(
    "/preferred-moves",
    response_model=PreferredMovesMutationResponse,
    operation_id="putPreferredMoves",
    responses={
        422: {"model": PreferredMovesErrorResponse},
        500: {"model": PreferredMovesErrorResponse},
        503: {"model": PreferredMovesErrorResponse},
    },
)
def put_preferred_moves(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    payload: PreferredMovesMutationRequest,
) -> PreferredMovesMutationResponse | JSONResponse:
    try:
        request = PreferredMoveMutationRequest(
            fen=payload.fen,
            effective_from=payload.effective_from,
            effective_until=payload.effective_until,
            preference=_mutation_preference(payload),
        )
        return _mutation_response(put_preferred_move(database_path, request))
    except PreferredMoveValidationError as error:
        return _mutation_validation_error(error)
    except (PreferredMoveSchemaError, PreferredMoveStorageError):
        return _error(
            503,
            "preferred_moves_unavailable",
            "Preferred moves unavailable",
        )
    except Exception:
        return _error(500, "unexpected_failure", "Unable to update preferred moves")


@router.delete(
    "/preferred-moves",
    response_model=PreferredMovesRemovalResponse,
    operation_id="deletePreferredMoves",
    responses={
        422: {"model": PreferredMovesErrorResponse},
        500: {"model": PreferredMovesErrorResponse},
        503: {"model": PreferredMovesErrorResponse},
    },
)
def delete_preferred_moves(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    payload: PreferredMovesRemovalRequest,
) -> PreferredMovesRemovalResponse | JSONResponse:
    try:
        request = PreferredMoveRemovalRequest(
            fen=payload.fen,
            effective_from=payload.effective_from,
            effective_until=payload.effective_until,
        )
        return _removal_response(delete_preferred_move(database_path, request))
    except PreferredMoveValidationError as error:
        return _removal_validation_error(error)
    except (PreferredMoveSchemaError, PreferredMoveStorageError):
        return _error(
            503,
            "preferred_moves_unavailable",
            "Preferred moves unavailable",
        )
    except Exception:
        return _error(500, "unexpected_failure", "Unable to delete preferred moves")


__all__ = ["delete_preferred_moves", "get_preferred_moves", "put_preferred_moves", "router"]
