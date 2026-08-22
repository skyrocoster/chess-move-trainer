"""HTTP boundary for read-only observation and deliberate evaluation enqueueing."""

from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.app.features.analysis import (
    AnalysisBusyError,
    AnalysisProfile,
    AnalysisSchemaError,
)
from backend.app.features.positions.repository import (
    CorpusUnavailableError,
    database_path,
    open_read_only_connection,
)

from .api_schemas import (
    EvaluationActionRequest,
    EvaluationCandidateResponse,
    EvaluationEnqueueResponse,
    EvaluationErrorCode,
    EvaluationErrorResponse,
    EvaluationObservationResponse,
    EvaluationPollResponse,
    EvaluationResultResponse,
    EvaluationStatusResponse,
)
from .errors import EvaluationQueueError, EvaluationSchemaError, EvaluationValidationError
from .models import EvaluationQueueItem, InspectResult, RequestResult
from .service import inspect, request

router = APIRouter(prefix="/api", tags=["evaluation"])

QUALIFIED_ENGINE_SHA256 = "c86215fa1977d53b82ed854540a4c7b025be4cd042276c85ba3de53fb9118911"


def active_profile() -> AnalysisProfile:
    """Return the fixed MP-09 profile; browser requests cannot select settings."""

    return AnalysisProfile(
        profile_id="mp09-balanced-nodes-v2-200000",
        engine_binary_sha256=QUALIFIED_ENGINE_SHA256,
        engine_name="Stockfish 18",
        engine_version="18",
        node_budget=200_000,
        options={"UCI_ShowWDL": True},
    )


def _error(status_code: int, code: EvaluationErrorCode, message: str) -> JSONResponse:
    body = EvaluationErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _validation_error(error: EvaluationValidationError) -> JSONResponse:
    message = str(error)
    if "longer than" in message or "size bound" in message:
        code: EvaluationErrorCode = "request_too_large"
    elif "action" in message:
        code = "invalid_action"
    else:
        code = "invalid_fen"
    return _error(422, code, message)


def _status(item: EvaluationQueueItem) -> EvaluationStatusResponse:
    return EvaluationStatusResponse(
        state=item.state,
        position=item.position,
        attempts=item.attempts,
        enqueued_at=item.enqueued_at,
        started_at=item.started_at,
        completed_at=item.finished_at,
        error_code=item.last_error_code,
    )


def _result(result: object) -> EvaluationResultResponse:
    analysis = result
    return EvaluationResultResponse(
        fen=analysis.fen,
        profile_id=analysis.profile.profile_id,
        candidates=[
            EvaluationCandidateResponse(
                rank=candidate.rank,
                score_kind=candidate.score_kind,
                score_value=candidate.score_value,
                wdl_wins=candidate.wdl_wins,
                wdl_draws=candidate.wdl_draws,
                wdl_losses=candidate.wdl_losses,
                pv_uci=list(candidate.pv_uci),
                depth=candidate.depth,
                seldepth=candidate.seldepth,
                nodes=candidate.nodes,
                engine_time_ms=candidate.engine_time_ms,
            )
            for candidate in analysis.candidates
        ],
        terminal_kind=analysis.terminal_kind,
        completed_at=analysis.completed_at,
        wall_time_ms=analysis.wall_time_ms,
    )


def _observation(observed: InspectResult) -> EvaluationObservationResponse:
    return EvaluationObservationResponse(
        fen=observed.fen,
        eligibility=observed.eligibility.value,
        result=None if observed.result is None else _result(observed.result),
        status=None if observed.item is None else _status(observed.item),
        terminal=observed.terminal,
    )


def _open_write_connection() -> sqlite3.Connection:
    path = database_path().expanduser().resolve()
    if not path.is_file():
        raise CorpusUnavailableError
    try:
        return sqlite3.connect(path, timeout=0)
    except sqlite3.Error as error:
        raise CorpusUnavailableError from error


def _handle_read(fen: str) -> EvaluationObservationResponse | JSONResponse:
    try:
        connection = open_read_only_connection()
        try:
            return _observation(inspect(connection, fen, active_profile()))
        finally:
            connection.close()
    except EvaluationValidationError as error:
        return _validation_error(error)
    except (CorpusUnavailableError, EvaluationSchemaError, AnalysisSchemaError):
        return _error(503, "evaluation_unavailable", "Evaluation data unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to observe evaluation")


@router.get(
    "/evaluation",
    response_model=EvaluationObservationResponse,
    responses={
        422: {"model": EvaluationErrorResponse},
        500: {"model": EvaluationErrorResponse},
        503: {"model": EvaluationErrorResponse},
    },
)
def evaluation(fen: Annotated[str, Query()]) -> EvaluationObservationResponse | JSONResponse:
    """Observe one displayed FEN; this path is strictly read-only."""

    return _handle_read(fen)


@router.post(
    "/evaluation",
    response_model=EvaluationEnqueueResponse,
    status_code=202,
    responses={
        409: {"model": EvaluationErrorResponse},
        422: {"model": EvaluationErrorResponse},
        500: {"model": EvaluationErrorResponse},
        503: {"model": EvaluationErrorResponse},
    },
)
def enqueue_evaluation(
    payload: EvaluationActionRequest,
) -> EvaluationEnqueueResponse | JSONResponse:
    """Enqueue only after an explicit Analyze, Update, or Retry request."""

    try:
        connection = _open_write_connection()
        try:
            outcome = request(connection, payload.fen, active_profile(), payload.action)
        finally:
            connection.close()
    except EvaluationValidationError as error:
        return _validation_error(error)
    except EvaluationQueueError:
        return _error(
            409,
            "invalid_transition",
            "Evaluation action is not valid for the current queue state",
        )
    except AnalysisBusyError:
        return _error(503, "evaluation_busy", "Evaluation database is busy")
    except (CorpusUnavailableError, EvaluationSchemaError, AnalysisSchemaError):
        return _error(503, "evaluation_unavailable", "Evaluation data unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to enqueue evaluation")

    assert isinstance(outcome, RequestResult)
    assert outcome.item is not None
    return EvaluationEnqueueResponse(
        fen=outcome.fen,
        action=payload.action,
        outcome=outcome.outcome,
        eligibility=outcome.eligibility.value,
        status=_status(outcome.item),
    )


@router.get(
    "/evaluation/status",
    response_model=EvaluationPollResponse,
    responses={
        422: {"model": EvaluationErrorResponse},
        500: {"model": EvaluationErrorResponse},
        503: {"model": EvaluationErrorResponse},
    },
)
def evaluation_status(fen: Annotated[str, Query()]) -> EvaluationPollResponse | JSONResponse:
    """Read queue progress and completion for already accepted work."""

    try:
        connection = open_read_only_connection()
        try:
            observed = inspect(connection, fen, active_profile())
        finally:
            connection.close()
    except EvaluationValidationError as error:
        return _validation_error(error)
    except (CorpusUnavailableError, EvaluationSchemaError, AnalysisSchemaError):
        return _error(503, "evaluation_unavailable", "Evaluation data unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to observe evaluation status")

    item = observed.item
    return EvaluationPollResponse(
        fen=observed.fen,
        state=None if item is None else item.state,
        completed_at=None if item is None else item.finished_at,
        error_code=None if item is None else item.last_error_code,
    )
