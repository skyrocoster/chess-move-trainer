"""In-memory aggregation helpers for one bounded row per selected game."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from statistics import median

from .models import (
    ActivityPeriod,
    ActivityStatistics,
    CategoryPerformance,
    DataQualityStatistics,
    GameStatistics,
    HourActivity,
    NumericSummary,
    OpeningPerformance,
    OpeningStatistics,
    OpponentPerformance,
    OpponentStatistics,
    OutcomeRecord,
    RatingProgression,
    RecentFormWindow,
    StreakStatistics,
    WeekdayActivity,
)

_WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


@dataclass(frozen=True, slots=True)
class _GameRow:
    game_id: int
    trainer_color: str
    opponent_uuid: str | None
    trainer_rating: int | None
    opponent_rating: int | None
    started_at_utc: str | None
    ended_at_utc: str | None
    outcome: str | None
    termination_reason: str | None
    time_control: str | None
    time_class: str | None
    length_plies: int


@dataclass(frozen=True, slots=True)
class _DatedGame:
    row: _GameRow
    started_at: datetime


def game_statistics(rows: tuple[_GameRow, ...]) -> GameStatistics:
    return GameStatistics(
        record=_outcome_record(rows),
        by_trainer_color=_categories(rows, lambda row: row.trainer_color),
        by_time_class=_categories(rows, lambda row: _category(row.time_class)),
        by_time_control=_categories(rows, lambda row: _category(row.time_control)),
        by_termination_reason=_categories(
            rows, lambda row: _normalized_category(row.termination_reason)
        ),
        by_rating_difference=_categories(rows, _rating_difference_category),
        by_length_plies=_categories(rows, _length_category),
        trainer_rating=_numeric_summary(
            [float(row.trainer_rating) for row in rows if row.trainer_rating is not None]
        ),
        opponent_rating=_numeric_summary(
            [float(row.opponent_rating) for row in rows if row.opponent_rating is not None]
        ),
        rating_difference=_numeric_summary(
            [
                float(row.trainer_rating - row.opponent_rating)
                for row in rows
                if row.trainer_rating is not None and row.opponent_rating is not None
            ]
        ),
        length_plies=_numeric_summary([float(row.length_plies) for row in rows]),
        duration_seconds=_numeric_summary(
            [duration for row in rows if (duration := _duration_seconds(row)) is not None]
        ),
        trainer_rating_progression=_rating_progression(rows),
    )


def activity_statistics(rows: tuple[_GameRow, ...]) -> ActivityStatistics:
    dated = tuple(
        _DatedGame(row, parsed)
        for row in rows
        if (parsed := _parse_utc(row.started_at_utc)) is not None
    )
    chronological = tuple(sorted(dated, key=lambda item: (item.started_at, item.row.game_id)))
    monthly: dict[str, list[_GameRow]] = defaultdict(list)
    weekdays: dict[int, list[_GameRow]] = defaultdict(list)
    hours: dict[int, list[_GameRow]] = defaultdict(list)
    for item in chronological:
        monthly[item.started_at.strftime("%Y-%m")].append(item.row)
        weekdays[item.started_at.weekday()].append(item.row)
        hours[item.started_at.hour].append(item.row)

    recent = tuple(
        RecentFormWindow(
            requested_game_count=size,
            dated_game_count=len(window),
            record=_outcome_record(window),
        )
        for size in (10, 25, 50)
        for window in (tuple(item.row for item in chronological[-size:]),)
    )
    return ActivityStatistics(
        first_game_at_utc=(None if not chronological else chronological[0].row.started_at_utc),
        last_game_at_utc=(None if not chronological else chronological[-1].row.started_at_utc),
        dated_game_count=len(chronological),
        by_month=tuple(
            ActivityPeriod(
                period=period,
                record=_outcome_record(tuple(period_rows)),
                average_trainer_rating=_average(
                    [
                        float(row.trainer_rating)
                        for row in period_rows
                        if row.trainer_rating is not None
                    ]
                ),
            )
            for period, period_rows in sorted(monthly.items())
        ),
        by_weekday_utc=tuple(
            WeekdayActivity(
                weekday=weekday,
                record=_outcome_record(tuple(weekdays.get(index, ()))),
            )
            for index, weekday in enumerate(_WEEKDAYS)
        ),
        by_hour_utc=tuple(
            HourActivity(
                hour_utc=hour,
                record=_outcome_record(tuple(hours.get(hour, ()))),
            )
            for hour in range(24)
        ),
        recent_form=recent,
        streaks=_streaks(tuple(item.row for item in chronological)),
    )


def opening_statistics(
    rows: tuple[_GameRow, ...],
    deepest_openings: dict[int, tuple[str, str, int]],
    *,
    limit: int = 25,
) -> OpeningStatistics:
    grouped: dict[tuple[str, str], list[_GameRow]] = defaultdict(list)
    deepest_ply: dict[tuple[str, str], int] = {}
    for row in rows:
        opening = deepest_openings.get(row.game_id)
        if opening is None:
            continue
        eco, name, ply = opening
        key = (eco, name)
        grouped[key].append(row)
        deepest_ply[key] = max(ply, deepest_ply.get(key, 0))
    ranked = sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
    returned = ranked[:limit]
    classified_count = sum(len(group_rows) for group_rows in grouped.values())
    return OpeningStatistics(
        classified_game_count=classified_count,
        unclassified_game_count=len(rows) - classified_count,
        distinct_opening_count=len(grouped),
        returned_opening_count=len(returned),
        openings=tuple(
            OpeningPerformance(
                key=f"{eco}:{name}",
                eco=eco,
                name=name,
                deepest_ply=deepest_ply[(eco, name)],
                record=_outcome_record(tuple(group_rows)),
                average_trainer_rating=_average(
                    [
                        float(row.trainer_rating)
                        for row in group_rows
                        if row.trainer_rating is not None
                    ]
                ),
                average_length_plies=_average([float(row.length_plies) for row in group_rows]),
            )
            for (eco, name), group_rows in returned
        ),
    )


def opponent_statistics(rows: tuple[_GameRow, ...], *, limit: int = 20) -> OpponentStatistics:
    grouped: dict[str, list[_GameRow]] = defaultdict(list)
    for row in rows:
        if row.opponent_uuid is not None:
            grouped[row.opponent_uuid].append(row)
    ranked = sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0]))
    returned = ranked[:limit]
    known_count = sum(len(group_rows) for group_rows in grouped.values())
    return OpponentStatistics(
        known_opponent_game_count=known_count,
        unknown_opponent_game_count=len(rows) - known_count,
        distinct_known_opponent_count=len(grouped),
        repeat_opponent_count=sum(1 for group_rows in grouped.values() if len(group_rows) > 1),
        returned_opponent_count=len(returned),
        opponents=tuple(
            OpponentPerformance(
                opponent_chesscom_uuid=opponent_uuid,
                record=_outcome_record(tuple(group_rows)),
                average_opponent_rating=_average(
                    [
                        float(row.opponent_rating)
                        for row in group_rows
                        if row.opponent_rating is not None
                    ]
                ),
                average_rating_difference=_average(
                    [
                        float(row.trainer_rating - row.opponent_rating)
                        for row in group_rows
                        if row.trainer_rating is not None and row.opponent_rating is not None
                    ]
                ),
            )
            for opponent_uuid, group_rows in returned
        ),
    )


def data_quality_statistics(rows: tuple[_GameRow, ...]) -> DataQualityStatistics:
    return DataQualityStatistics(
        missing_outcome_count=sum(row.outcome is None for row in rows),
        missing_trainer_rating_count=sum(row.trainer_rating is None for row in rows),
        missing_opponent_rating_count=sum(row.opponent_rating is None for row in rows),
        missing_started_at_count=sum(row.started_at_utc is None for row in rows),
        invalid_started_at_count=sum(
            row.started_at_utc is not None and _parse_utc(row.started_at_utc) is None
            for row in rows
        ),
        missing_ended_at_count=sum(row.ended_at_utc is None for row in rows),
        invalid_ended_at_count=sum(
            row.ended_at_utc is not None and _parse_utc(row.ended_at_utc) is None for row in rows
        ),
        negative_duration_count=sum(
            _raw_duration_seconds(row) is not None and _raw_duration_seconds(row) < 0
            for row in rows
        ),
        missing_time_class_count=sum(row.time_class is None for row in rows),
        missing_time_control_count=sum(row.time_control is None for row in rows),
        missing_termination_reason_count=sum(row.termination_reason is None for row in rows),
        missing_opponent_count=sum(row.opponent_uuid is None for row in rows),
    )


def _outcome_record(rows: tuple[_GameRow, ...]) -> OutcomeRecord:
    wins = sum(row.outcome == "win" for row in rows)
    losses = sum(row.outcome == "loss" for row in rows)
    draws = sum(row.outcome == "draw" for row in rows)
    known = wins + losses + draws
    return OutcomeRecord(
        total_count=len(rows),
        known_outcome_count=known,
        win_count=wins,
        loss_count=losses,
        draw_count=draws,
        unknown_count=len(rows) - known,
        score_rate=None if not known else _rounded((wins + draws * 0.5) / known),
    )


def _categories(rows: tuple[_GameRow, ...], classifier: object) -> tuple[CategoryPerformance, ...]:
    groups: dict[str, list[_GameRow]] = defaultdict(list)
    for row in rows:
        groups[classifier(row)].append(row)
    return tuple(
        CategoryPerformance(category=category, record=_outcome_record(tuple(group_rows)))
        for category, group_rows in sorted(
            groups.items(), key=lambda item: (-len(item[1]), item[0])
        )
    )


def _numeric_summary(values: list[float]) -> NumericSummary:
    if not values:
        return NumericSummary(0, None, None, None, None)
    return NumericSummary(
        count=len(values),
        minimum=_number(min(values)),
        maximum=_number(max(values)),
        average=_rounded(sum(values) / len(values)),
        median=_number(float(median(values))),
    )


def _rating_progression(rows: tuple[_GameRow, ...]) -> RatingProgression:
    ratings = [
        (parsed, row.game_id, row.trainer_rating)
        for row in rows
        if row.trainer_rating is not None and (parsed := _parse_utc(row.started_at_utc)) is not None
    ]
    ratings.sort(key=lambda item: (item[0], item[1]))
    if not ratings:
        return RatingProgression(0, None, None, None, None, None)
    values = [rating for _started, _game_id, rating in ratings]
    first = values[0]
    last = values[-1]
    return RatingProgression(
        dated_rating_count=len(values),
        first_rating=first,
        last_rating=last,
        change=last - first,
        peak_rating=max(values),
        lowest_rating=min(values),
    )


def _streaks(rows: tuple[_GameRow, ...]) -> StreakStatistics:
    outcomes = [row.outcome for row in rows if row.outcome in ("win", "loss", "draw")]
    current_kind = outcomes[-1] if outcomes else None
    current_count = 0
    longest = {"win": 0, "loss": 0, "draw": 0}
    run_kind: str | None = None
    run_count = 0
    unbeaten = winless = longest_unbeaten = longest_winless = 0
    for outcome in outcomes:
        if outcome == run_kind:
            run_count += 1
        else:
            run_kind = outcome
            run_count = 1
        longest[outcome] = max(longest[outcome], run_count)
        unbeaten = 0 if outcome == "loss" else unbeaten + 1
        winless = 0 if outcome == "win" else winless + 1
        longest_unbeaten = max(longest_unbeaten, unbeaten)
        longest_winless = max(longest_winless, winless)
    if current_kind is not None:
        for outcome in reversed(outcomes):
            if outcome != current_kind:
                break
            current_count += 1
    return StreakStatistics(
        current_kind=current_kind,
        current_count=current_count,
        longest_win_count=longest["win"],
        longest_loss_count=longest["loss"],
        longest_draw_count=longest["draw"],
        longest_unbeaten_count=longest_unbeaten,
        longest_winless_count=longest_winless,
    )


def _parse_utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _raw_duration_seconds(row: _GameRow) -> float | None:
    started = _parse_utc(row.started_at_utc)
    ended = _parse_utc(row.ended_at_utc)
    if started is None or ended is None:
        return None
    return (ended - started).total_seconds()


def _duration_seconds(row: _GameRow) -> float | None:
    duration = _raw_duration_seconds(row)
    return duration if duration is not None and duration >= 0 else None


def _average(values: list[float]) -> float | None:
    return None if not values else _rounded(sum(values) / len(values))


def _rounded(value: float) -> float:
    return round(value, 6)


def _number(value: float) -> int | float:
    return int(value) if value.is_integer() else _rounded(value)


def _category(value: str | None) -> str:
    return "unknown" if value is None or not value.strip() else value.strip()


def _normalized_category(value: str | None) -> str:
    return _category(value).casefold()


def _rating_difference_category(row: _GameRow) -> str:
    if row.trainer_rating is None or row.opponent_rating is None:
        return "unknown"
    difference = row.trainer_rating - row.opponent_rating
    if difference >= 200:
        return "trainer_200_plus_higher"
    if difference >= 50:
        return "trainer_50_to_199_higher"
    if difference > -50:
        return "within_49"
    if difference > -200:
        return "opponent_50_to_199_higher"
    return "opponent_200_plus_higher"


def _length_category(row: _GameRow) -> str:
    if row.length_plies < 20:
        return "0-19"
    if row.length_plies < 40:
        return "20-39"
    if row.length_plies < 60:
        return "40-59"
    return "60+"


__all__ = [
    "_GameRow",
    "activity_statistics",
    "data_quality_statistics",
    "game_statistics",
    "opening_statistics",
    "opponent_statistics",
]
