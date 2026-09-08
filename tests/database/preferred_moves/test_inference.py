from __future__ import annotations

from datetime import date

from chess_move_trainer.database.positions import CanonicalPosition
from chess_move_trainer.database.preferred_moves.inference import (
    PreferredMoveObservation,
    infer_preferred_moves,
)
from chess_move_trainer.database.preferred_moves.ranges import (
    NormalizedPeriod,
    Preference,
    PreferenceState,
)


MOVE_A = "e2e4"
MOVE_B = "d2d4"
POSITION = CanonicalPosition("8/8/8/8/8/8/8/8", "w", "-", "-")


def observation(day: str, move: str, count: int = 1) -> list[PreferredMoveObservation]:
    return [
        PreferredMoveObservation(POSITION, date.fromisoformat(day), move)
        for _ in range(count)
    ]


def periods_for(observations: list[PreferredMoveObservation]) -> tuple[NormalizedPeriod, ...]:
    return infer_preferred_moves(observations).periods_by_position.get(POSITION, ())


def expected_period(start: str, end: str | None, move: str) -> NormalizedPeriod:
    return NormalizedPeriod(
        date.fromisoformat(start),
        None if end is None else date.fromisoformat(end),
        Preference.preferred_move(move),
    )


def test_every_eligible_occurrence_is_counted_including_same_date_duplicates() -> None:
    result = infer_preferred_moves(observation("2026-01-01", MOVE_A, 21))

    assert periods_for(observation("2026-01-01", MOVE_A, 21)) == (
        expected_period("2026-01-01", None, MOVE_A),
    )
    assert result.summaries[0].periods[-1].effective_until is None


def test_exact_21_match_boundary_qualifies_but_20_does_not() -> None:
    assert periods_for(
        observation("2026-01-01", MOVE_A, 20)
        + observation("2026-01-01", MOVE_B, 5)
    ) == ()
    assert periods_for(observation("2026-01-01", MOVE_A, 21)) == (
        expected_period("2026-01-01", None, MOVE_A),
    )


def test_exact_80_percent_boundary_is_inclusive() -> None:
    assert periods_for(
        observation("2026-01-01", MOVE_A, 24)
        + observation("2026-01-01", MOVE_B, 6)
    ) == (expected_period("2026-01-01", None, MOVE_A),)
    assert periods_for(
        observation("2026-01-01", MOVE_A, 23)
        + observation("2026-01-01", MOVE_B, 6)
    ) == ()


def test_rolling_window_includes_day_89_but_not_day_90() -> None:
    assert periods_for(
        observation("2026-01-01", MOVE_A, 21)
        + observation("2026-03-31", MOVE_B, 6)
    ) == ()
    assert periods_for(
        observation("2026-01-01", MOVE_A, 21)
        + observation("2026-04-01", MOVE_B, 6)
    ) == (expected_period("2026-01-01", None, MOVE_A),)


def test_candidate_period_starts_on_first_matching_date_not_21st_match() -> None:
    periods = periods_for(
        observation("2026-01-01", MOVE_B)
        + observation("2026-01-10", MOVE_A)
        + observation("2026-01-20", MOVE_A, 20)
    )

    assert periods == (expected_period("2026-01-10", None, MOVE_A),)


def test_unsupported_dates_are_carried_without_an_unconfigured_period() -> None:
    periods = periods_for(observation("2026-01-01", MOVE_A, 21))

    assert periods == (expected_period("2026-01-01", None, MOVE_A),)
    assert all(period.preference.state is PreferenceState.PREFERRED_MOVE for period in periods)


def test_later_qualifying_different_move_replaces_the_incumbent() -> None:
    periods = periods_for(
        observation("2026-01-01", MOVE_A, 21)
        + observation("2026-05-01", MOVE_B, 21)
    )

    assert periods == (
        expected_period("2026-01-01", "2026-05-01", MOVE_A),
        expected_period("2026-05-01", None, MOVE_B),
    )


def test_overlapping_qualifying_evidence_chooses_the_larger_raw_overlap_count() -> None:
    periods = periods_for(
        observation("2026-01-01", MOVE_A, 100)
        + observation("2026-02-01", MOVE_A, 5)
        + observation("2026-02-01", MOVE_B, 21)
    )

    assert periods == (
        expected_period("2026-01-01", "2026-02-01", MOVE_A),
        expected_period("2026-02-01", None, MOVE_B),
    )


def test_overlapping_exact_tie_preserves_the_active_move() -> None:
    periods = periods_for(
        observation("2026-01-01", MOVE_A, 84)
        + observation("2026-02-01", MOVE_A, 21)
        + observation("2026-02-01", MOVE_B, 21)
        + observation("2026-04-01", MOVE_B, 84)
    )

    assert periods == (
        expected_period("2026-01-01", "2026-04-01", MOVE_A),
        expected_period("2026-04-01", None, MOVE_B),
    )


def test_repeated_qualifying_signals_for_one_move_do_not_create_periods() -> None:
    periods = periods_for(
        observation("2026-01-01", MOVE_A, 21)
        + observation("2026-04-02", MOVE_A, 21)
    )

    assert periods == (expected_period("2026-01-01", None, MOVE_A),)


def test_dates_before_first_signal_remain_unconfigured_and_no_no_preference_is_inferred() -> None:
    periods = periods_for(
        observation("2026-01-01", MOVE_A, 20)
        + observation("2026-01-02", MOVE_B, 5)
    )

    assert periods == ()
    assert infer_preferred_moves(
        observation("2026-01-01", MOVE_A, 20)
        + observation("2026-01-02", MOVE_B, 5)
    ).summaries == ()


def test_zero_candidates_produce_an_empty_result() -> None:
    result = infer_preferred_moves(
        observation("2026-01-01", MOVE_A, 10)
        + observation("2026-06-01", MOVE_B, 10)
    )

    assert result.summaries == ()
    assert dict(result.periods_by_position) == {}
