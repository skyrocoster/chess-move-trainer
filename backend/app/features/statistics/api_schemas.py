"""Strict HTTP contracts for the statistics overview."""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr


class ContractModel(BaseModel):
    """Base model that rejects fields outside the settled HTTP contract."""

    model_config = ConfigDict(extra="forbid", strict=True)


NonNegativeInt: TypeAlias = Annotated[StrictInt, Field(ge=0)]
NumberOrNull: TypeAlias = StrictInt | float | None
RateOrNull: TypeAlias = Annotated[float | int | None, Field(ge=0, le=1)]

StatisticsErrorCode: TypeAlias = Literal[
    "invalid_filter",
    "statistics_unavailable",
    "unexpected_failure",
]


class StatisticsErrorResponse(ContractModel):
    code: StatisticsErrorCode
    message: StrictStr


class StatisticsFiltersResponse(ContractModel):
    started_on_or_after: StrictStr | None
    started_on_or_before: StrictStr | None
    trainer_color: Literal["white", "black"] | None
    time_class: Literal["bullet", "blitz", "rapid", "daily"] | None


class OutcomeRecordResponse(ContractModel):
    total_count: NonNegativeInt
    known_outcome_count: NonNegativeInt
    win_count: NonNegativeInt
    loss_count: NonNegativeInt
    draw_count: NonNegativeInt
    unknown_count: NonNegativeInt
    score_rate: RateOrNull


class CategoryPerformanceResponse(ContractModel):
    category: StrictStr
    record: OutcomeRecordResponse


class NumericSummaryResponse(ContractModel):
    count: NonNegativeInt
    minimum: NumberOrNull
    maximum: NumberOrNull
    average: NumberOrNull
    median: NumberOrNull


class RatingProgressionResponse(ContractModel):
    dated_rating_count: NonNegativeInt
    first_rating: StrictInt | None
    last_rating: StrictInt | None
    change: StrictInt | None
    peak_rating: StrictInt | None
    lowest_rating: StrictInt | None


class GameStatisticsResponse(ContractModel):
    record: OutcomeRecordResponse
    by_trainer_color: list[CategoryPerformanceResponse]
    by_time_class: list[CategoryPerformanceResponse]
    by_time_control: list[CategoryPerformanceResponse]
    by_termination_reason: list[CategoryPerformanceResponse]
    by_rating_difference: list[CategoryPerformanceResponse]
    by_length_plies: list[CategoryPerformanceResponse]
    trainer_rating: NumericSummaryResponse
    opponent_rating: NumericSummaryResponse
    rating_difference: NumericSummaryResponse
    length_plies: NumericSummaryResponse
    duration_seconds: NumericSummaryResponse
    trainer_rating_progression: RatingProgressionResponse


class ActivityPeriodResponse(ContractModel):
    period: StrictStr
    record: OutcomeRecordResponse
    average_trainer_rating: StrictInt | float | None


class WeekdayActivityResponse(ContractModel):
    weekday: Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    record: OutcomeRecordResponse


class RecentFormWindowResponse(ContractModel):
    requested_game_count: NonNegativeInt
    dated_game_count: NonNegativeInt
    record: OutcomeRecordResponse


class StreakStatisticsResponse(ContractModel):
    current_kind: Literal["win", "loss", "draw"] | None
    current_count: NonNegativeInt
    longest_win_count: NonNegativeInt
    longest_loss_count: NonNegativeInt
    longest_draw_count: NonNegativeInt
    longest_unbeaten_count: NonNegativeInt
    longest_winless_count: NonNegativeInt


class HourActivityResponse(ContractModel):
    hour_utc: Annotated[StrictInt, Field(ge=0, le=23)]
    record: OutcomeRecordResponse


class ActivityStatisticsResponse(ContractModel):
    first_game_at_utc: StrictStr | None
    last_game_at_utc: StrictStr | None
    dated_game_count: NonNegativeInt
    by_month: list[ActivityPeriodResponse]
    by_weekday_utc: list[WeekdayActivityResponse]
    by_hour_utc: list[HourActivityResponse]
    recent_form: list[RecentFormWindowResponse]
    streaks: StreakStatisticsResponse


class OpeningPerformanceResponse(ContractModel):
    key: StrictStr
    eco: StrictStr
    name: StrictStr
    deepest_ply: NonNegativeInt
    record: OutcomeRecordResponse
    average_trainer_rating: StrictInt | float | None
    average_length_plies: Annotated[StrictInt | float | None, Field(ge=0)]


class OpeningStatisticsResponse(ContractModel):
    classified_game_count: NonNegativeInt
    unclassified_game_count: NonNegativeInt
    distinct_opening_count: NonNegativeInt
    returned_opening_count: NonNegativeInt
    openings: list[OpeningPerformanceResponse]


class OpponentPerformanceResponse(ContractModel):
    opponent_chesscom_uuid: StrictStr
    record: OutcomeRecordResponse
    average_opponent_rating: StrictInt | float | None
    average_rating_difference: StrictInt | float | None


class OpponentStatisticsResponse(ContractModel):
    known_opponent_game_count: NonNegativeInt
    unknown_opponent_game_count: NonNegativeInt
    distinct_known_opponent_count: NonNegativeInt
    repeat_opponent_count: NonNegativeInt
    returned_opponent_count: NonNegativeInt
    opponents: list[OpponentPerformanceResponse]


class PlyBucketResponse(ContractModel):
    label: StrictStr
    minimum_ply: NonNegativeInt
    maximum_ply: NonNegativeInt | None
    occurrence_count: NonNegativeInt
    distinct_game_count: NonNegativeInt
    distinct_position_count: NonNegativeInt


class RecurringPositionResponse(ContractModel):
    fen: StrictStr
    distinct_game_count: NonNegativeInt
    occurrence_count: NonNegativeInt
    outgoing_occurrence_count: NonNegativeInt
    terminal_occurrence_count: NonNegativeInt


class PositionStatisticsResponse(ContractModel):
    database_position_count: NonNegativeInt
    observed_position_count: NonNegativeInt
    distinct_game_count: NonNegativeInt
    occurrence_count: NonNegativeInt
    outgoing_occurrence_count: NonNegativeInt
    terminal_occurrence_count: NonNegativeInt
    trainer_turn_occurrence_count: NonNegativeInt
    opponent_turn_occurrence_count: NonNegativeInt
    distinct_outgoing_move_count: NonNegativeInt
    repeated_position_count: NonNegativeInt
    average_occurrences_per_observed_position: Annotated[StrictInt | float | None, Field(ge=0)]
    ply_buckets: list[PlyBucketResponse]
    recurring_positions: list[RecurringPositionResponse]


class AnalysisStatisticsResponse(ContractModel):
    scoped_position_count: NonNegativeInt
    ready_position_count: NonNegativeInt
    browser_quality_count: NonNegativeInt
    tool_quality_count: NonNegativeInt
    terminal_result_count: NonNegativeInt
    queued_position_count: NonNegativeInt
    running_position_count: NonNegativeInt
    not_requested_position_count: NonNegativeInt
    line_count: NonNegativeInt
    centipawn_line_count: NonNegativeInt
    mate_line_count: NonNegativeInt
    multi_pv_result_count: NonNegativeInt
    average_depth: Annotated[StrictInt | float | None, Field(ge=0)]
    ready_coverage_rate: RateOrNull


class TrainingBalanceStatisticsResponse(ContractModel):
    count: NonNegativeInt
    negative_count: NonNegativeInt
    zero_count: NonNegativeInt
    positive_count: NonNegativeInt
    updated_count: NonNegativeInt
    missing_count: NonNegativeInt
    summary: NumericSummaryResponse


class RepertoireStatisticsResponse(ContractModel):
    trainer_turn_position_count: NonNegativeInt
    move_preference_position_count: NonNegativeInt
    no_preference_position_count: NonNegativeInt
    unconfigured_position_count: NonNegativeInt
    preference_coverage_rate: RateOrNull
    preference_observed_position_count: NonNegativeInt
    preferred_move_opportunity_count: NonNegativeInt
    preferred_move_played_count: NonNegativeInt
    preferred_move_adherence_rate: RateOrNull
    training_balances: TrainingBalanceStatisticsResponse


class DataQualityStatisticsResponse(ContractModel):
    missing_outcome_count: NonNegativeInt
    missing_trainer_rating_count: NonNegativeInt
    missing_opponent_rating_count: NonNegativeInt
    missing_started_at_count: NonNegativeInt
    invalid_started_at_count: NonNegativeInt
    missing_ended_at_count: NonNegativeInt
    invalid_ended_at_count: NonNegativeInt
    negative_duration_count: NonNegativeInt
    missing_time_class_count: NonNegativeInt
    missing_time_control_count: NonNegativeInt
    missing_termination_reason_count: NonNegativeInt
    missing_opponent_count: NonNegativeInt


class StatisticsOverviewResponse(ContractModel):
    as_of: StrictStr
    filters: StatisticsFiltersResponse
    games: GameStatisticsResponse
    activity: ActivityStatisticsResponse
    openings: OpeningStatisticsResponse
    opponents: OpponentStatisticsResponse
    positions: PositionStatisticsResponse
    analysis: AnalysisStatisticsResponse
    repertoire: RepertoireStatisticsResponse
    data_quality: DataQualityStatisticsResponse


__all__ = [
    "ActivityPeriodResponse",
    "ActivityStatisticsResponse",
    "AnalysisStatisticsResponse",
    "CategoryPerformanceResponse",
    "DataQualityStatisticsResponse",
    "GameStatisticsResponse",
    "HourActivityResponse",
    "NonNegativeInt",
    "NumberOrNull",
    "NumericSummaryResponse",
    "OpeningPerformanceResponse",
    "OpeningStatisticsResponse",
    "OpponentPerformanceResponse",
    "OpponentStatisticsResponse",
    "OutcomeRecordResponse",
    "PlyBucketResponse",
    "PositionStatisticsResponse",
    "RateOrNull",
    "RatingProgressionResponse",
    "RecentFormWindowResponse",
    "RecurringPositionResponse",
    "RepertoireStatisticsResponse",
    "StatisticsErrorCode",
    "StatisticsErrorResponse",
    "StatisticsFiltersResponse",
    "StatisticsOverviewResponse",
    "StreakStatisticsResponse",
    "TrainingBalanceStatisticsResponse",
    "WeekdayActivityResponse",
]
