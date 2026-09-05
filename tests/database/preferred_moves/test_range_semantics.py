from __future__ import annotations

from datetime import date, datetime

import pytest

from chess_move_trainer.database.preferred_moves.ranges import (
    DateResolution,
    NormalizedPeriod,
    Preference,
    RangeValidationError,
    ResolutionState,
    normalize_periods,
    parse_date_literal,
    period_from_literals,
    resolve_date,
    set_preference,
    unset_preference,
)


MOVE_A = Preference.preferred_move("e2e4")
MOVE_B = Preference.preferred_move("d2d4")
NO_PREFERENCE = Preference.no_preference()


def period(start: str, end: str | None, preference: Preference) -> NormalizedPeriod:
    return period_from_literals(start, end, preference)


def test_strict_date_parser_accepts_literal_calendar_dates() -> None:
    assert parse_date_literal("2024-02-29") == date(2024, 2, 29)


@pytest.mark.parametrize(
    "invalid",
    [
        "2023-02-29",
        "2026-13-01",
        "2026-09-31",
        "2026-9-05",
        "05-09-2026",
        "2026-09-05T00:00:00Z",
        "2026-09-05 00:00:00",
        "today",
        "+1 day",
        "",
    ],
)
def test_strict_date_parser_rejects_impossible_nonliteral_and_relative_values(
    invalid: str,
) -> None:
    with pytest.raises(RangeValidationError):
        parse_date_literal(invalid)


def test_date_values_reject_timestamp_precision() -> None:
    with pytest.raises(RangeValidationError):
        NormalizedPeriod(datetime(2026, 1, 1), None, MOVE_A)


def test_date_resolution_rejects_unknown_state_values() -> None:
    with pytest.raises(RangeValidationError):
        DateResolution("unknown")  # type: ignore[arg-type]


def test_ranges_require_explicit_start_and_a_strictly_later_finite_end() -> None:
    with pytest.raises(TypeError):
        period_from_literals(effective_until=None, preference=MOVE_A)  # type: ignore[call-arg]
    with pytest.raises(RangeValidationError):
        period("2026-01-01", "2026-01-01", MOVE_A)
    with pytest.raises(RangeValidationError):
        period("2026-01-02", "2026-01-01", MOVE_A)
    assert period("2026-01-01", None, MOVE_A).effective_until is None


def test_normalization_rejects_out_of_order_overlap_and_nonfinal_indefinite() -> None:
    with pytest.raises(RangeValidationError):
        normalize_periods(
            [period("2026-02-01", "2026-03-01", MOVE_A), period("2026-01-01", "2026-02-01", MOVE_B)]
        )
    with pytest.raises(RangeValidationError):
        normalize_periods(
            [period("2026-01-01", "2026-03-01", MOVE_A), period("2026-02-01", "2026-04-01", MOVE_B)]
        )
    with pytest.raises(RangeValidationError):
        normalize_periods(
            [period("2026-01-01", None, MOVE_A), period("2026-02-01", None, MOVE_B)]
        )


def test_insertion_into_empty_schedule_is_exact() -> None:
    assert set_preference([], "2026-01-01", "2026-02-01", MOVE_A) == (
        period("2026-01-01", "2026-02-01", MOVE_A),
    )


def test_overlay_splits_and_preserves_both_outside_fragments_exactly() -> None:
    original = period("2026-01-01", "2026-04-01", MOVE_A)

    result = set_preference([original], "2026-02-01", "2026-03-01", MOVE_B)

    assert result == (
        period("2026-01-01", "2026-02-01", MOVE_A),
        period("2026-02-01", "2026-03-01", MOVE_B),
        period("2026-03-01", "2026-04-01", MOVE_A),
    )


def test_overlay_shortens_existing_period_at_its_start() -> None:
    result = set_preference(
        [period("2026-01-01", "2026-04-01", MOVE_A)],
        "2026-01-01",
        "2026-02-01",
        MOVE_B,
    )
    assert result == (
        period("2026-01-01", "2026-02-01", MOVE_B),
        period("2026-02-01", "2026-04-01", MOVE_A),
    )


def test_equal_overlay_extends_and_merges_across_an_existing_boundary() -> None:
    result = set_preference(
        [period("2026-02-01", "2026-04-01", MOVE_A)],
        "2026-01-01",
        "2026-03-01",
        MOVE_A,
    )
    assert result == (period("2026-01-01", "2026-04-01", MOVE_A),)


def test_overlay_replaces_exact_period_and_can_be_indefinite() -> None:
    replaced = set_preference(
        [period("2026-01-01", "2026-02-01", MOVE_A)],
        "2026-01-01",
        "2026-02-01",
        MOVE_B,
    )
    indefinite = set_preference(replaced, "2026-02-01", None, MOVE_B)

    assert replaced == (period("2026-01-01", "2026-02-01", MOVE_B),)
    assert indefinite == (period("2026-01-01", None, MOVE_B),)


def test_unset_with_no_intersection_is_a_semantic_no_op() -> None:
    schedule = (period("2026-02-01", "2026-03-01", MOVE_A),)
    assert unset_preference(schedule, "2026-04-01", "2026-05-01") == schedule


def test_unset_creates_an_unconfigured_gap_and_preserves_outside_dates() -> None:
    result = unset_preference(
        [period("2026-01-01", "2026-04-01", MOVE_A)],
        "2026-02-01",
        "2026-03-01",
    )
    assert result == (
        period("2026-01-01", "2026-02-01", MOVE_A),
        period("2026-03-01", "2026-04-01", MOVE_A),
    )
    assert resolve_date(result, "2026-02-15") == DateResolution(
        ResolutionState.UNCONFIGURED
    )


def test_adjacent_equal_move_and_no_preference_states_merge() -> None:
    assert normalize_periods(
        [
            period("2026-01-01", "2026-02-01", MOVE_A),
            period("2026-02-01", "2026-03-01", MOVE_A),
            period("2026-03-01", "2026-04-01", NO_PREFERENCE),
            period("2026-04-01", None, NO_PREFERENCE),
        ]
    ) == (
        period("2026-01-01", "2026-03-01", MOVE_A),
        period("2026-03-01", None, NO_PREFERENCE),
    )


def test_return_to_earlier_move_remains_separate_across_state_or_gap() -> None:
    across_state = normalize_periods(
        [
            period("2026-01-01", "2026-02-01", MOVE_A),
            period("2026-02-01", "2026-03-01", MOVE_B),
            period("2026-03-01", None, MOVE_A),
        ]
    )
    across_gap = unset_preference(across_state, "2026-02-01", "2026-03-01")

    assert len(across_state) == 3
    assert across_gap == (
        period("2026-01-01", "2026-02-01", MOVE_A),
        period("2026-03-01", None, MOVE_A),
    )


def test_overlay_preserves_unaffected_periods_and_only_amends_intersection() -> None:
    schedule = (
        period("2025-01-01", "2025-02-01", NO_PREFERENCE),
        period("2026-01-01", "2026-04-01", MOVE_A),
        period("2027-01-01", None, MOVE_B),
    )

    result = set_preference(schedule, "2026-02-01", "2026-03-01", NO_PREFERENCE)

    assert result[0] == schedule[0]
    assert result[-1] == schedule[-1]
    assert result[1:4] == (
        period("2026-01-01", "2026-02-01", MOVE_A),
        period("2026-02-01", "2026-03-01", NO_PREFERENCE),
        period("2026-03-01", "2026-04-01", MOVE_A),
    )


def test_set_overlay_crosses_multiple_periods_and_merges_equal_left_edge() -> None:
    schedule = (
        period("2026-01-01", "2026-02-01", MOVE_A),
        period("2026-02-01", "2026-03-01", MOVE_B),
        period("2026-03-01", "2026-04-01", NO_PREFERENCE),
        period("2026-04-01", "2026-05-01", MOVE_B),
    )

    result = set_preference(schedule, "2026-01-15", "2026-04-15", MOVE_A)

    assert result == (
        period("2026-01-01", "2026-04-15", MOVE_A),
        period("2026-04-15", "2026-05-01", MOVE_B),
    )


def test_unset_crosses_multiple_periods_and_preserves_both_edge_fragments() -> None:
    schedule = (
        period("2026-01-01", "2026-02-01", MOVE_A),
        period("2026-02-01", "2026-03-01", MOVE_B),
        period("2026-03-01", "2026-04-01", NO_PREFERENCE),
        period("2026-04-01", "2026-05-01", MOVE_B),
    )

    result = unset_preference(schedule, "2026-01-15", "2026-04-15")

    assert result == (
        period("2026-01-01", "2026-01-15", MOVE_A),
        period("2026-04-15", "2026-05-01", MOVE_B),
    )


def test_resolution_distinguishes_all_three_states_at_half_open_boundaries() -> None:
    schedule = (
        period("2026-01-01", "2026-02-01", MOVE_A),
        period("2026-02-01", "2026-03-01", NO_PREFERENCE),
        period("2026-04-01", None, MOVE_B),
    )

    assert resolve_date(schedule, "2025-12-31") == DateResolution(
        ResolutionState.UNCONFIGURED
    )
    assert resolve_date(schedule, "2026-01-01") == DateResolution(
        ResolutionState.PREFERRED_MOVE, "e2e4"
    )
    assert resolve_date(schedule, "2026-02-01") == DateResolution(
        ResolutionState.NO_PREFERENCE
    )
    assert resolve_date(schedule, "2026-03-01") == DateResolution(
        ResolutionState.UNCONFIGURED
    )
    assert resolve_date(schedule, "2026-04-01") == DateResolution(
        ResolutionState.PREFERRED_MOVE, "d2d4"
    )
    assert resolve_date(schedule, "9999-12-31") == DateResolution(
        ResolutionState.PREFERRED_MOVE, "d2d4"
    )


def test_empty_schedule_always_resolves_unconfigured() -> None:
    assert resolve_date([], "2026-01-01") == DateResolution(
        ResolutionState.UNCONFIGURED
    )
