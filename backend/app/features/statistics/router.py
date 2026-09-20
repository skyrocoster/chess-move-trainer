"""Thin HTTP translation layer for the statistics overview."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.app.caching import (
    get_or_compute,
    json_response,
    read_namespace,
    serialize_response_body,
    statistics_overview_key,
)
from backend.app.dependencies import get_rebuilt_database_path
from chess_move_trainer.database.reporting import (
    StatisticsOverview,
    StatisticsOverviewQuery,
    StatisticsOverviewSchemaError,
    StatisticsOverviewStorageError,
    StatisticsOverviewValidationError,
    read_statistics_overview,
)

from .api_schemas import (
    ActivityPeriodResponse,
    ActivityStatisticsResponse,
    AnalysisStatisticsResponse,
    CategoryPerformanceResponse,
    DataQualityStatisticsResponse,
    GameStatisticsResponse,
    HourActivityResponse,
    NumericSummaryResponse,
    OpeningPerformanceResponse,
    OpeningStatisticsResponse,
    OpponentPerformanceResponse,
    OpponentStatisticsResponse,
    OutcomeRecordResponse,
    PlyBucketResponse,
    PositionStatisticsResponse,
    RatingProgressionResponse,
    RecentFormWindowResponse,
    RecurringPositionResponse,
    RepertoireStatisticsResponse,
    StatisticsErrorResponse,
    StatisticsFiltersResponse,
    StatisticsOverviewResponse,
    StreakStatisticsResponse,
    TrainingBalanceStatisticsResponse,
    WeekdayActivityResponse,
)

router = APIRouter(prefix="/api", tags=["statistics"])


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    body = StatisticsErrorResponse(code=code, message=message)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def _outcome(record: object) -> OutcomeRecordResponse:
    return OutcomeRecordResponse(
        total_count=record.total_count,
        known_outcome_count=record.known_outcome_count,
        win_count=record.win_count,
        loss_count=record.loss_count,
        draw_count=record.draw_count,
        unknown_count=record.unknown_count,
        score_rate=record.score_rate,
    )


def _category(performance: object) -> CategoryPerformanceResponse:
    return CategoryPerformanceResponse(
        category=performance.category,
        record=_outcome(performance.record),
    )


def _numeric(summary: object) -> NumericSummaryResponse:
    return NumericSummaryResponse(
        count=summary.count,
        minimum=summary.minimum,
        maximum=summary.maximum,
        average=summary.average,
        median=summary.median,
    )


def _games(games: object) -> GameStatisticsResponse:
    return GameStatisticsResponse(
        record=_outcome(games.record),
        by_trainer_color=[_category(item) for item in games.by_trainer_color],
        by_time_class=[_category(item) for item in games.by_time_class],
        by_time_control=[_category(item) for item in games.by_time_control],
        by_termination_reason=[_category(item) for item in games.by_termination_reason],
        by_rating_difference=[_category(item) for item in games.by_rating_difference],
        by_length_plies=[_category(item) for item in games.by_length_plies],
        trainer_rating=_numeric(games.trainer_rating),
        opponent_rating=_numeric(games.opponent_rating),
        rating_difference=_numeric(games.rating_difference),
        length_plies=_numeric(games.length_plies),
        duration_seconds=_numeric(games.duration_seconds),
        trainer_rating_progression=RatingProgressionResponse(
            dated_rating_count=games.trainer_rating_progression.dated_rating_count,
            first_rating=games.trainer_rating_progression.first_rating,
            last_rating=games.trainer_rating_progression.last_rating,
            change=games.trainer_rating_progression.change,
            peak_rating=games.trainer_rating_progression.peak_rating,
            lowest_rating=games.trainer_rating_progression.lowest_rating,
        ),
    )


def _activity(activity: object) -> ActivityStatisticsResponse:
    return ActivityStatisticsResponse(
        first_game_at_utc=activity.first_game_at_utc,
        last_game_at_utc=activity.last_game_at_utc,
        dated_game_count=activity.dated_game_count,
        by_month=[
            ActivityPeriodResponse(
                period=period.period,
                record=_outcome(period.record),
                average_trainer_rating=period.average_trainer_rating,
            )
            for period in activity.by_month
        ],
        by_weekday_utc=[
            WeekdayActivityResponse(weekday=day.weekday, record=_outcome(day.record))
            for day in activity.by_weekday_utc
        ],
        by_hour_utc=[
            HourActivityResponse(hour_utc=hour.hour_utc, record=_outcome(hour.record))
            for hour in activity.by_hour_utc
        ],
        recent_form=[
            RecentFormWindowResponse(
                requested_game_count=window.requested_game_count,
                dated_game_count=window.dated_game_count,
                record=_outcome(window.record),
            )
            for window in activity.recent_form
        ],
        streaks=StreakStatisticsResponse(
            current_kind=activity.streaks.current_kind,
            current_count=activity.streaks.current_count,
            longest_win_count=activity.streaks.longest_win_count,
            longest_loss_count=activity.streaks.longest_loss_count,
            longest_draw_count=activity.streaks.longest_draw_count,
            longest_unbeaten_count=activity.streaks.longest_unbeaten_count,
            longest_winless_count=activity.streaks.longest_winless_count,
        ),
    )


def _openings(openings: object) -> OpeningStatisticsResponse:
    return OpeningStatisticsResponse(
        classified_game_count=openings.classified_game_count,
        unclassified_game_count=openings.unclassified_game_count,
        distinct_opening_count=openings.distinct_opening_count,
        returned_opening_count=openings.returned_opening_count,
        openings=[
            OpeningPerformanceResponse(
                key=opening.key,
                eco=opening.eco,
                name=opening.name,
                deepest_ply=opening.deepest_ply,
                record=_outcome(opening.record),
                average_trainer_rating=opening.average_trainer_rating,
                average_length_plies=opening.average_length_plies,
            )
            for opening in openings.openings
        ],
    )


def _opponents(opponents: object) -> OpponentStatisticsResponse:
    return OpponentStatisticsResponse(
        known_opponent_game_count=opponents.known_opponent_game_count,
        unknown_opponent_game_count=opponents.unknown_opponent_game_count,
        distinct_known_opponent_count=opponents.distinct_known_opponent_count,
        repeat_opponent_count=opponents.repeat_opponent_count,
        returned_opponent_count=opponents.returned_opponent_count,
        opponents=[
            OpponentPerformanceResponse(
                opponent_chesscom_uuid=opponent.opponent_chesscom_uuid,
                record=_outcome(opponent.record),
                average_opponent_rating=opponent.average_opponent_rating,
                average_rating_difference=opponent.average_rating_difference,
            )
            for opponent in opponents.opponents
        ],
    )


def _positions(positions: object) -> PositionStatisticsResponse:
    return PositionStatisticsResponse(
        database_position_count=positions.database_position_count,
        observed_position_count=positions.observed_position_count,
        distinct_game_count=positions.distinct_game_count,
        occurrence_count=positions.occurrence_count,
        outgoing_occurrence_count=positions.outgoing_occurrence_count,
        terminal_occurrence_count=positions.terminal_occurrence_count,
        trainer_turn_occurrence_count=positions.trainer_turn_occurrence_count,
        opponent_turn_occurrence_count=positions.opponent_turn_occurrence_count,
        distinct_outgoing_move_count=positions.distinct_outgoing_move_count,
        repeated_position_count=positions.repeated_position_count,
        average_occurrences_per_observed_position=(
            positions.average_occurrences_per_observed_position
        ),
        ply_buckets=[
            PlyBucketResponse(
                label=bucket.label,
                minimum_ply=bucket.minimum_ply,
                maximum_ply=bucket.maximum_ply,
                occurrence_count=bucket.occurrence_count,
                distinct_game_count=bucket.distinct_game_count,
                distinct_position_count=bucket.distinct_position_count,
            )
            for bucket in positions.ply_buckets
        ],
        recurring_positions=[
            RecurringPositionResponse(
                fen=position.fen,
                distinct_game_count=position.distinct_game_count,
                occurrence_count=position.occurrence_count,
                outgoing_occurrence_count=position.outgoing_occurrence_count,
                terminal_occurrence_count=position.terminal_occurrence_count,
            )
            for position in positions.recurring_positions
        ],
    )


def _analysis(analysis: object) -> AnalysisStatisticsResponse:
    return AnalysisStatisticsResponse(
        scoped_position_count=analysis.scoped_position_count,
        ready_position_count=analysis.ready_position_count,
        browser_quality_count=analysis.browser_quality_count,
        tool_quality_count=analysis.tool_quality_count,
        terminal_result_count=analysis.terminal_result_count,
        queued_position_count=analysis.queued_position_count,
        running_position_count=analysis.running_position_count,
        not_requested_position_count=analysis.not_requested_position_count,
        line_count=analysis.line_count,
        centipawn_line_count=analysis.centipawn_line_count,
        mate_line_count=analysis.mate_line_count,
        multi_pv_result_count=analysis.multi_pv_result_count,
        average_depth=analysis.average_depth,
        ready_coverage_rate=analysis.ready_coverage_rate,
    )


def _repertoire(repertoire: object) -> RepertoireStatisticsResponse:
    return RepertoireStatisticsResponse(
        trainer_turn_position_count=repertoire.trainer_turn_position_count,
        move_preference_position_count=repertoire.move_preference_position_count,
        no_preference_position_count=repertoire.no_preference_position_count,
        unconfigured_position_count=repertoire.unconfigured_position_count,
        preference_coverage_rate=repertoire.preference_coverage_rate,
        preference_observed_position_count=repertoire.preference_observed_position_count,
        preferred_move_opportunity_count=repertoire.preferred_move_opportunity_count,
        preferred_move_played_count=repertoire.preferred_move_played_count,
        preferred_move_adherence_rate=repertoire.preferred_move_adherence_rate,
        training_balances=TrainingBalanceStatisticsResponse(
            count=repertoire.training_balances.count,
            negative_count=repertoire.training_balances.negative_count,
            zero_count=repertoire.training_balances.zero_count,
            positive_count=repertoire.training_balances.positive_count,
            updated_count=repertoire.training_balances.updated_count,
            missing_count=repertoire.training_balances.missing_count,
            summary=_numeric(repertoire.training_balances.summary),
        ),
    )


def _data_quality(data_quality: object) -> DataQualityStatisticsResponse:
    return DataQualityStatisticsResponse(
        missing_outcome_count=data_quality.missing_outcome_count,
        missing_trainer_rating_count=data_quality.missing_trainer_rating_count,
        missing_opponent_rating_count=data_quality.missing_opponent_rating_count,
        missing_started_at_count=data_quality.missing_started_at_count,
        invalid_started_at_count=data_quality.invalid_started_at_count,
        missing_ended_at_count=data_quality.missing_ended_at_count,
        invalid_ended_at_count=data_quality.invalid_ended_at_count,
        negative_duration_count=data_quality.negative_duration_count,
        missing_time_class_count=data_quality.missing_time_class_count,
        missing_time_control_count=data_quality.missing_time_control_count,
        missing_termination_reason_count=data_quality.missing_termination_reason_count,
        missing_opponent_count=data_quality.missing_opponent_count,
    )


def _response(overview: StatisticsOverview) -> StatisticsOverviewResponse:
    return StatisticsOverviewResponse(
        as_of=overview.query.as_of,
        filters=StatisticsFiltersResponse(
            started_on_or_after=overview.query.started_on_or_after,
            started_on_or_before=overview.query.started_on_or_before,
            trainer_color=overview.query.trainer_color,
            time_class=overview.query.time_class,
        ),
        games=_games(overview.games),
        activity=_activity(overview.activity),
        openings=_openings(overview.openings),
        opponents=_opponents(overview.opponents),
        positions=_positions(overview.positions),
        analysis=_analysis(overview.analysis),
        repertoire=_repertoire(overview.repertoire),
        data_quality=_data_quality(overview.data_quality),
    )


@router.get(
    "/statistics/overview",
    response_model=StatisticsOverviewResponse,
    operation_id="getStatisticsOverview",
    responses={
        422: {"model": StatisticsErrorResponse},
        500: {"model": StatisticsErrorResponse},
        503: {"model": StatisticsErrorResponse},
    },
)
def get_statistics_overview(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
    as_of: Annotated[str, Query()],
    started_on_or_after: Annotated[str | None, Query()] = None,
    started_on_or_before: Annotated[str | None, Query()] = None,
    trainer_color: Annotated[str | None, Query()] = None,
    time_class: Annotated[str | None, Query()] = None,
) -> StatisticsOverviewResponse | JSONResponse:
    try:
        query = StatisticsOverviewQuery(
            as_of=as_of,
            started_on_or_after=started_on_or_after,
            started_on_or_before=started_on_or_before,
            trainer_color=trainer_color,
            time_class=time_class,
        )
    except StatisticsOverviewValidationError:
        return _error(422, "invalid_filter", "Invalid statistics filter")
    key = statistics_overview_key(database_path, query)
    try:
        payload = get_or_compute(
            read_namespace,
            key,
            database_path,
            lambda: serialize_response_body(
                _response(read_statistics_overview(database_path, query))
            ),
        )
    except (StatisticsOverviewSchemaError, StatisticsOverviewStorageError):
        return _error(503, "statistics_unavailable", "Statistics unavailable")
    except Exception:
        return _error(500, "unexpected_failure", "Unable to load statistics")
    assert payload is not None
    return json_response(payload)


__all__ = ["get_statistics_overview", "router"]
