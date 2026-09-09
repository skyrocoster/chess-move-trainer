"""Thin HTTP translation layer for package-owned game search."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.app.dependencies import get_rebuilt_database_path
from backend.app.features.games.api_schemas import (
    GameCoverageResponse,
    GameDetailOccurrenceResponse,
    GameDetailResponse,
    GameSummaryResponse,
    GamesErrorResponse,
    GamesResponse,
    OpeningSummaryResponse,
)
from chess_move_trainer.database.games import (
    GameSearchQuery,
    GameSearchSchemaError,
    GameSearchStorageError,
    GameSearchValidationError,
    read_game,
    search_games,
)
from chess_move_trainer.database.games.reading import GameReadError
from chess_move_trainer.database.schema import SchemaIncompatibleError


router = APIRouter(prefix="/api", tags=["games"])


def _games_error(status_code: int, code: str, message: str) -> JSONResponse:
    body = GamesErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _summary_response(summary: object) -> GameSummaryResponse:
    deepest = summary.deepest_opening
    deepest_response = (
        None
        if deepest is None
        else OpeningSummaryResponse(
            key=deepest.key,
            eco=deepest.eco,
            name=deepest.name,
            ply=deepest.ply,
        )
    )
    coverage = summary.coverage
    return GameSummaryResponse(
        game_uuid=UUID(summary.game_uuid),
        source_url=summary.source_url,
        trainer_color=summary.trainer_color,
        trainer_chesscom_uuid=UUID(summary.trainer_chesscom_uuid),
        opponent_chesscom_uuid=(
            None
            if summary.opponent_chesscom_uuid is None
            else UUID(summary.opponent_chesscom_uuid)
        ),
        trainer_rating=summary.trainer_rating,
        opponent_rating=summary.opponent_rating,
        started_at_utc=summary.started_at_utc,
        ended_at_utc=summary.ended_at_utc,
        trainer_outcome=summary.trainer_outcome,
        termination_reason=summary.termination_reason,
        time_control=summary.time_control,
        time_class=summary.time_class,
        occurrence_count=summary.occurrence_count,
        length_plies=summary.length_plies,
        deepest_opening=deepest_response,
        coverage=GameCoverageResponse(
            distinct_position_count=coverage.distinct_position_count,
            analyzed_position_count=coverage.analyzed_position_count,
            preferred_position_count=coverage.preferred_position_count,
            analysis_coverage=coverage.analysis_coverage,
            preferred_coverage=coverage.preferred_coverage,
        ),
    )


def _page_response(page: object) -> GamesResponse:
    return GamesResponse(
        items=[_summary_response(summary) for summary in page.items],
        page=page.page,
        page_size=page.page_size,
        total=page.total,
        total_pages=page.total_pages,
        has_next=page.has_next,
    )


def _detail_response(detail: object) -> GameDetailResponse:
    return GameDetailResponse(
        game_uuid=UUID(detail.game_uuid),
        source_url=detail.source_url,
        original_pgn=detail.original_pgn,
        trainer_color=detail.trainer_color,
        trainer_chesscom_uuid=UUID(detail.trainer_chesscom_uuid),
        opponent_chesscom_uuid=(
            None
            if detail.opponent_chesscom_uuid is None
            else UUID(detail.opponent_chesscom_uuid)
        ),
        trainer_rating=detail.trainer_rating,
        opponent_rating=detail.opponent_rating,
        started_at_utc=detail.started_at_utc,
        ended_at_utc=detail.ended_at_utc,
        trainer_outcome=detail.trainer_outcome,
        termination_reason=detail.termination_reason,
        time_control=detail.time_control,
        time_class=detail.time_class,
        occurrences=[
            GameDetailOccurrenceResponse(
                ply=occurrence.ply,
                fen=occurrence.fen,
                move_uci=occurrence.move_uci,
            )
            for occurrence in detail.occurrences
        ],
    )


@router.get(
    "/games",
    response_model=GamesResponse,
    operation_id="getGames",
    responses={
        422: {"model": GamesErrorResponse},
        500: {"model": GamesErrorResponse},
        503: {"model": GamesErrorResponse},
    },
)
def get_games(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    page: Annotated[int, Query()] = 1,
    page_size: Annotated[int, Query()] = 50,
    started_at_from: Annotated[str | None, Query()] = None,
    started_at_to: Annotated[str | None, Query()] = None,
    ended_at_from: Annotated[str | None, Query()] = None,
    ended_at_to: Annotated[str | None, Query()] = None,
    trainer_color: Annotated[str | None, Query()] = None,
    trainer_outcome: Annotated[str | None, Query()] = None,
    termination_reason: Annotated[str | None, Query()] = None,
    trainer_rating_min: Annotated[int | None, Query()] = None,
    trainer_rating_max: Annotated[int | None, Query()] = None,
    opponent_rating_min: Annotated[int | None, Query()] = None,
    opponent_rating_max: Annotated[int | None, Query()] = None,
    opponent_chesscom_uuid: Annotated[str | None, Query()] = None,
    time_class: Annotated[str | None, Query()] = None,
    time_control: Annotated[str | None, Query()] = None,
    opening_key: Annotated[str | None, Query()] = None,
    opening_match: Annotated[str | None, Query()] = None,
    contains_fen: Annotated[str | None, Query()] = None,
    move_fen: Annotated[str | None, Query()] = None,
    move_uci: Annotated[str | None, Query()] = None,
    min_length_plies: Annotated[int | None, Query()] = None,
    max_length_plies: Annotated[int | None, Query()] = None,
    analysis_coverage: Annotated[str | None, Query()] = None,
    preferred_coverage: Annotated[str | None, Query()] = None,
    sort: Annotated[str, Query()] = "started_at_desc",
) -> GamesResponse | JSONResponse:
    try:
        page_result = search_games(
            database_path,
            GameSearchQuery(
                page=page,
                page_size=page_size,
                started_at_from=started_at_from,
                started_at_to=started_at_to,
                ended_at_from=ended_at_from,
                ended_at_to=ended_at_to,
                trainer_color=trainer_color,
                trainer_outcome=trainer_outcome,
                termination_reason=termination_reason,
                trainer_rating_min=trainer_rating_min,
                trainer_rating_max=trainer_rating_max,
                opponent_rating_min=opponent_rating_min,
                opponent_rating_max=opponent_rating_max,
                opponent_chesscom_uuid=opponent_chesscom_uuid,
                time_class=time_class,
                time_control=time_control,
                opening_key=opening_key,
                opening_match=opening_match,
                contains_fen=contains_fen,
                move_fen=move_fen,
                move_uci=move_uci,
                min_length_plies=min_length_plies,
                max_length_plies=max_length_plies,
                analysis_coverage=analysis_coverage,
                preferred_coverage=preferred_coverage,
                sort=sort,
            ),
        )
    except GameSearchValidationError:
        return _games_error(422, "invalid_filter", "Invalid game filter")
    except (GameSearchSchemaError, GameSearchStorageError):
        return _games_error(503, "games_unavailable", "Games unavailable")
    except Exception:
        return _games_error(500, "unexpected_failure", "Unable to load games")
    return _page_response(page_result)


@router.get(
    "/games/{game_uuid}",
    response_model=GameDetailResponse,
    operation_id="getGame",
    responses={
        404: {"model": GamesErrorResponse},
        500: {"model": GamesErrorResponse},
        503: {"model": GamesErrorResponse},
    },
)
def get_game(
    game_uuid: UUID,
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
) -> GameDetailResponse | JSONResponse:
    try:
        detail = read_game(database_path, str(game_uuid))
        if detail is None:
            return _games_error(404, "game_not_found", "Game not found")
        return _detail_response(detail)
    except (GameReadError, SchemaIncompatibleError):
        return _games_error(503, "games_unavailable", "Games unavailable")
    except Exception:
        return _games_error(500, "unexpected_failure", "Unable to load game")


__all__ = ["get_game", "get_games", "router"]
