"""Thin HTTP translation layer for one clean position insight."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_rebuilt_database_path
from chess_move_trainer.database.positions import (
    PositionInsight,
    PositionInsightResult,
    PositionInsightStorageError,
    PositionInsightSchemaError,
    PositionInsightValidationError,
    read_position_insight,
)

from .api_schemas import (
    MovePreferenceResponse,
    NoPreferenceResponse,
    PositionInsightAnalysisResponse,
    PositionInsightErrorResponse,
    PositionInsightExperienceResponse,
    PositionInsightLineResponse,
    PositionInsightObservedMoveResponse,
    PositionInsightObservedMoveTotalsResponse,
    PositionInsightOpeningResponse,
    PositionInsightResponse,
    PositionInsightResultResponse,
    PositionInsightTerminalTotalsResponse,
    UnconfiguredPreferenceResponse,
)

router = APIRouter(prefix="/api", tags=["position-insight"])


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    body = PositionInsightErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _result_response(result: PositionInsightResult) -> PositionInsightResultResponse:
    return PositionInsightResultResponse(
        quality=result.quality.value,
        configuration_version=result.configuration_version,
        settings=dict(result.settings),
        engine_name=result.engine_name,
        engine_version=result.engine_version,
        terminal_kind=None if result.terminal_kind is None else result.terminal_kind.value,
        lines=[
            PositionInsightLineResponse(
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


def _response(insight: PositionInsight) -> PositionInsightResponse:
    opening = insight.opening
    opening_response = (
        None
        if opening is None
        else PositionInsightOpeningResponse(
            key=opening.key,
            eco=opening.eco,
            name=opening.name,
            ply=opening.ply,
            match=opening.match,
        )
    )
    preference = insight.preference
    if preference.kind == "move":
        preference_response = MovePreferenceResponse(kind="move", uci=preference.uci)
    elif preference.kind == "no_preference":
        preference_response = NoPreferenceResponse(kind="no_preference")
    else:
        preference_response = UnconfiguredPreferenceResponse(kind="unconfigured")
    return PositionInsightResponse(
        fen=insight.fen,
        trainer_color=insight.trainer_color,
        as_of=insight.as_of,
        observed_in_games=insight.observed_in_games,
        opening=opening_response,
        experience=PositionInsightExperienceResponse(
            distinct_game_count=insight.experience.distinct_game_count,
            occurrence_count=insight.experience.occurrence_count,
            total_game_count=insight.experience.total_game_count,
        ),
        observed_moves=[
            PositionInsightObservedMoveResponse(
                move_uci=move.move_uci,
                distinct_game_count=move.distinct_game_count,
                occurrence_count=move.occurrence_count,
            )
            for move in insight.observed_moves
        ],
        observed_move_totals=PositionInsightObservedMoveTotalsResponse(
            distinct_game_count=insight.observed_move_totals.distinct_game_count,
            occurrence_count=insight.observed_move_totals.occurrence_count,
            terminal=PositionInsightTerminalTotalsResponse(
                distinct_game_count=insight.observed_move_totals.terminal.distinct_game_count,
                occurrence_count=insight.observed_move_totals.terminal.occurrence_count,
            ),
        ),
        analysis=PositionInsightAnalysisResponse(
            state=insight.analysis.state,
            result=(
                None
                if insight.analysis.result is None
                else _result_response(insight.analysis.result)
            ),
        ),
        preference=preference_response,
    )


def _validation_error(error: PositionInsightValidationError) -> JSONResponse:
    message = str(error)
    if "trainer_color" in message:
        return _error(422, "invalid_trainer_color", "trainer_color must be 'white' or 'black'")
    if "as_of" in message:
        return _error(422, "invalid_as_of", "as_of must be a literal YYYY-MM-DD date")
    return _error(422, "invalid_fen", "FEN is invalid")


@router.get(
    "/positions/insight",
    response_model=PositionInsightResponse,
    operation_id="getPositionInsight",
    responses={
        422: {"model": PositionInsightErrorResponse},
        500: {"model": PositionInsightErrorResponse},
        503: {"model": PositionInsightErrorResponse},
    },
)
def get_position_insight(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    fen: Annotated[str, Query()],
    trainer_color: Annotated[str, Query()],
    as_of: Annotated[str, Query()],
) -> PositionInsightResponse | JSONResponse:
    try:
        insight = read_position_insight(database_path, fen, trainer_color, as_of)
        return _response(insight)
    except PositionInsightValidationError as error:
        return _validation_error(error)
    except (PositionInsightSchemaError, PositionInsightStorageError):
        return _error(
            503,
            "position_insight_unavailable",
            "Position insight unavailable",
        )
    except Exception:
        return _error(500, "unexpected_failure", "Unable to serve position insight")


__all__ = ["get_position_insight", "router"]
