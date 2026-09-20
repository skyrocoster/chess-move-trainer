"""Public values returned by the aggregate statistics reader."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

TrainerColor = Literal["white", "black"]
TimeClass = Literal["bullet", "blitz", "rapid", "daily"]
StreakKind = Literal["win", "loss", "draw"]


class StatisticsOverviewError(Exception):
    """Base class for bounded statistics-overview failures."""


class StatisticsOverviewValidationError(StatisticsOverviewError, ValueError):
    """Raised when a statistics-overview request is invalid."""


class StatisticsOverviewSchemaError(StatisticsOverviewError, RuntimeError):
    """Raised when the selected database schema is incompatible."""


class StatisticsOverviewStorageError(StatisticsOverviewError, RuntimeError):
    """Raised when stored reporting data cannot be read safely."""


@dataclass(frozen=True, slots=True)
class StatisticsOverviewQuery:
    """Deterministic date context and optional filters for one report."""

    as_of: str
    started_on_or_after: str | None = None
    started_on_or_before: str | None = None
    trainer_color: TrainerColor | None = None
    time_class: TimeClass | None = None

    def __post_init__(self) -> None:
        _validate_date(self.as_of, "as_of")
        if self.started_on_or_after is not None:
            _validate_date(self.started_on_or_after, "started_on_or_after")
        if self.started_on_or_before is not None:
            _validate_date(self.started_on_or_before, "started_on_or_before")
        if (
            self.started_on_or_after is not None
            and self.started_on_or_before is not None
            and self.started_on_or_after > self.started_on_or_before
        ):
            raise StatisticsOverviewValidationError(
                "started_on_or_after must not be later than started_on_or_before"
            )
        if self.trainer_color not in (None, "white", "black"):
            raise StatisticsOverviewValidationError(
                "trainer_color must be white, black, or omitted"
            )
        if self.time_class not in (None, "bullet", "blitz", "rapid", "daily"):
            raise StatisticsOverviewValidationError(
                "time_class must be bullet, blitz, rapid, daily, or omitted"
            )


@dataclass(frozen=True, slots=True)
class OutcomeRecord:
    total_count: int
    known_outcome_count: int
    win_count: int
    loss_count: int
    draw_count: int
    unknown_count: int
    score_rate: float | None


@dataclass(frozen=True, slots=True)
class CategoryPerformance:
    category: str
    record: OutcomeRecord


@dataclass(frozen=True, slots=True)
class NumericSummary:
    count: int
    minimum: float | None
    maximum: float | None
    average: float | None
    median: float | None


@dataclass(frozen=True, slots=True)
class RatingProgression:
    dated_rating_count: int
    first_rating: int | None
    last_rating: int | None
    change: int | None
    peak_rating: int | None
    lowest_rating: int | None


@dataclass(frozen=True, slots=True)
class GameStatistics:
    record: OutcomeRecord
    by_trainer_color: tuple[CategoryPerformance, ...]
    by_time_class: tuple[CategoryPerformance, ...]
    by_time_control: tuple[CategoryPerformance, ...]
    by_termination_reason: tuple[CategoryPerformance, ...]
    by_rating_difference: tuple[CategoryPerformance, ...]
    by_length_plies: tuple[CategoryPerformance, ...]
    trainer_rating: NumericSummary
    opponent_rating: NumericSummary
    rating_difference: NumericSummary
    length_plies: NumericSummary
    duration_seconds: NumericSummary
    trainer_rating_progression: RatingProgression


@dataclass(frozen=True, slots=True)
class ActivityPeriod:
    period: str
    record: OutcomeRecord
    average_trainer_rating: float | None


@dataclass(frozen=True, slots=True)
class WeekdayActivity:
    weekday: Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    record: OutcomeRecord


@dataclass(frozen=True, slots=True)
class HourActivity:
    hour_utc: int
    record: OutcomeRecord


@dataclass(frozen=True, slots=True)
class RecentFormWindow:
    requested_game_count: int
    dated_game_count: int
    record: OutcomeRecord


@dataclass(frozen=True, slots=True)
class StreakStatistics:
    current_kind: StreakKind | None
    current_count: int
    longest_win_count: int
    longest_loss_count: int
    longest_draw_count: int
    longest_unbeaten_count: int
    longest_winless_count: int


@dataclass(frozen=True, slots=True)
class ActivityStatistics:
    first_game_at_utc: str | None
    last_game_at_utc: str | None
    dated_game_count: int
    by_month: tuple[ActivityPeriod, ...]
    by_weekday_utc: tuple[WeekdayActivity, ...]
    by_hour_utc: tuple[HourActivity, ...]
    recent_form: tuple[RecentFormWindow, ...]
    streaks: StreakStatistics


@dataclass(frozen=True, slots=True)
class OpeningPerformance:
    key: str
    eco: str
    name: str
    deepest_ply: int
    record: OutcomeRecord
    average_trainer_rating: float | None
    average_length_plies: float | None


@dataclass(frozen=True, slots=True)
class OpeningStatistics:
    classified_game_count: int
    unclassified_game_count: int
    distinct_opening_count: int
    returned_opening_count: int
    openings: tuple[OpeningPerformance, ...]


@dataclass(frozen=True, slots=True)
class OpponentPerformance:
    opponent_chesscom_uuid: str
    record: OutcomeRecord
    average_opponent_rating: float | None
    average_rating_difference: float | None


@dataclass(frozen=True, slots=True)
class OpponentStatistics:
    known_opponent_game_count: int
    unknown_opponent_game_count: int
    distinct_known_opponent_count: int
    repeat_opponent_count: int
    returned_opponent_count: int
    opponents: tuple[OpponentPerformance, ...]


@dataclass(frozen=True, slots=True)
class PlyBucket:
    label: str
    minimum_ply: int
    maximum_ply: int | None
    occurrence_count: int
    distinct_game_count: int
    distinct_position_count: int


@dataclass(frozen=True, slots=True)
class RecurringPosition:
    fen: str
    distinct_game_count: int
    occurrence_count: int
    outgoing_occurrence_count: int
    terminal_occurrence_count: int


@dataclass(frozen=True, slots=True)
class PositionStatistics:
    database_position_count: int
    observed_position_count: int
    distinct_game_count: int
    occurrence_count: int
    outgoing_occurrence_count: int
    terminal_occurrence_count: int
    trainer_turn_occurrence_count: int
    opponent_turn_occurrence_count: int
    distinct_outgoing_move_count: int
    repeated_position_count: int
    average_occurrences_per_observed_position: float | None
    ply_buckets: tuple[PlyBucket, ...]
    recurring_positions: tuple[RecurringPosition, ...]


@dataclass(frozen=True, slots=True)
class AnalysisStatistics:
    scoped_position_count: int
    ready_position_count: int
    browser_quality_count: int
    tool_quality_count: int
    terminal_result_count: int
    queued_position_count: int
    running_position_count: int
    not_requested_position_count: int
    line_count: int
    centipawn_line_count: int
    mate_line_count: int
    multi_pv_result_count: int
    average_depth: float | None
    ready_coverage_rate: float | None


@dataclass(frozen=True, slots=True)
class TrainingBalanceStatistics:
    count: int
    negative_count: int
    zero_count: int
    positive_count: int
    updated_count: int
    missing_count: int
    summary: NumericSummary


@dataclass(frozen=True, slots=True)
class RepertoireStatistics:
    trainer_turn_position_count: int
    move_preference_position_count: int
    no_preference_position_count: int
    unconfigured_position_count: int
    preference_coverage_rate: float | None
    preference_observed_position_count: int
    preferred_move_opportunity_count: int
    preferred_move_played_count: int
    preferred_move_adherence_rate: float | None
    training_balances: TrainingBalanceStatistics


@dataclass(frozen=True, slots=True)
class DataQualityStatistics:
    missing_outcome_count: int
    missing_trainer_rating_count: int
    missing_opponent_rating_count: int
    missing_started_at_count: int
    invalid_started_at_count: int
    missing_ended_at_count: int
    invalid_ended_at_count: int
    negative_duration_count: int
    missing_time_class_count: int
    missing_time_control_count: int
    missing_termination_reason_count: int
    missing_opponent_count: int


@dataclass(frozen=True, slots=True)
class StatisticsOverview:
    query: StatisticsOverviewQuery
    games: GameStatistics
    activity: ActivityStatistics
    openings: OpeningStatistics
    opponents: OpponentStatistics
    positions: PositionStatistics
    analysis: AnalysisStatistics
    repertoire: RepertoireStatistics
    data_quality: DataQualityStatistics


def _validate_date(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise StatisticsOverviewValidationError(f"{name} must be a literal YYYY-MM-DD date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise StatisticsOverviewValidationError(
            f"{name} must be a literal YYYY-MM-DD date"
        ) from error
    if parsed.isoformat() != value:
        raise StatisticsOverviewValidationError(f"{name} must be a literal YYYY-MM-DD date")
