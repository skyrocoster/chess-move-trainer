"""Thin HTTP translation layer for current analysis observation."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_rebuilt_database_path
from chess_move_trainer.database.analysis import (
    AnalysisObservation,
    AnalysisObservationResult,
    AnalysisObservationSchemaError,
    AnalysisObservationStorageError,
    AnalysisObservationValidationError,
    read_analysis_observation,
)

from .api_schemas import (
    AnalysisObservationErrorCode,
    AnalysisObservationErrorResponse,
    AnalysisObservationLineResponse,
    AnalysisObservationResponse,
    AnalysisObservationResultResponse,
)

router = APIRouter(prefix="/api", tags=["analysis"])


def _error(
    status_code: int,
    code: AnalysisObservationErrorCode,
    message: str,
) -> JSONResponse:
    body = AnalysisObservationErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _result_response(
    result: AnalysisObservationResult,
) -> AnalysisObservationResultResponse:
    return AnalysisObservationResultResponse(
        quality=result.quality.value,
        configuration_version=result.configuration_version,
        settings=dict(result.settings),
        engine_name=result.engine_name,
        engine_version=result.engine_version,
        terminal_kind=None if result.terminal_kind is None else result.terminal_kind.value,
        lines=[
            AnalysisObservationLineResponse(
                rank=line.rank,
                score_kind=line.score_kind.value,
                score_value=line.score_value,
                wdl_wins=line.wdl_wins,
                wdl_draws=line.wdl_draws,
                wdl_losses=line.wdl_losses,
                pv_uci=list(line.pv_uci),
                depth=line.depth,
            )
            for line in result.lines
        ],
    )


def _response(observation: AnalysisObservation) -> AnalysisObservationResponse:
    return AnalysisObservationResponse(
        fen=observation.fen,
        state=observation.state.value,
        result=(
            None
            if observation.result is None
            else _result_response(observation.result)
        ),
    )


@router.get(
    "/analysis",
    response_model=AnalysisObservationResponse,
    operation_id="getAnalysis",
    responses={
        422: {"model": AnalysisObservationErrorResponse},
        500: {"model": AnalysisObservationErrorResponse},
        503: {"model": AnalysisObservationErrorResponse},
    },
)
def get_analysis(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    fen: Annotated[str, Query()],
) -> AnalysisObservationResponse | JSONResponse:
    try:
        return _response(read_analysis_observation(database_path, fen))
    except AnalysisObservationValidationError:
        return _error(422, "invalid_fen", "FEN is invalid")
    except (AnalysisObservationSchemaError, AnalysisObservationStorageError):
        return _error(503, "analysis_unavailable", "Analysis data unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to observe analysis")


__all__ = ["get_analysis", "router"]
