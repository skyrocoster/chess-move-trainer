"""Thin HTTP translation layer for desired current analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_rebuilt_database_path
from backend.app.features.analysis_observation.router import _response
from chess_move_trainer.database.analysis import (
    AnalysisRequestDisposition,
    AnalysisRequestSchemaError,
    AnalysisRequestStorageError,
    AnalysisRequestValidationError,
    request_analysis,
)

from .api_schemas import (
    AnalysisObservationResponse,
    AnalysisRequestBody,
    AnalysisRequestErrorCode,
    AnalysisRequestErrorResponse,
)

router = APIRouter(prefix="/api", tags=["analysis"])


def _error(
    status_code: int,
    code: AnalysisRequestErrorCode,
    message: str,
) -> JSONResponse:
    body = AnalysisRequestErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


@router.post(
    "/analysis-requests",
    response_model=AnalysisObservationResponse,
    operation_id="requestAnalysis",
    responses={
        202: {"model": AnalysisObservationResponse},
        422: {"model": AnalysisRequestErrorResponse},
        500: {"model": AnalysisRequestErrorResponse},
        503: {"model": AnalysisRequestErrorResponse},
    },
)
def post_analysis_request(
    body: AnalysisRequestBody,
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
) -> JSONResponse:
    try:
        outcome = request_analysis(database_path, body.fen, body.quality)
        status_code = (
            200
            if outcome.disposition is AnalysisRequestDisposition.RESULT_REUSED
            else 202
        )
        response = _response(outcome.observation)
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump(mode="json"),
        )
    except AnalysisRequestValidationError as error:
        if "quality" in str(error).lower():
            return _error(422, "invalid_quality", "Quality is invalid")
        return _error(422, "invalid_fen", "FEN is invalid")
    except (AnalysisRequestSchemaError, AnalysisRequestStorageError):
        return _error(503, "analysis_unavailable", "Analysis data unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to request analysis")


__all__ = ["post_analysis_request", "router"]
