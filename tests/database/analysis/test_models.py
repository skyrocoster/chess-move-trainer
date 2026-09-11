from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import pytest

from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisScoreKind,
    AnalysisValidationError,
    NotSavedReason,
    PublicationOutcome,
    validate_analysis_line,
    validate_analysis_result,
    validate_settings_object,
)


def _line(**changes: object) -> AnalysisLine:
    values: dict[str, object] = {
        "rank": 1,
        "score_kind": AnalysisScoreKind.CP,
        "score_value": 34,
        "wdl_wins": 420,
        "wdl_draws": 300,
        "wdl_losses": 280,
        "pv_uci": ("e2e4", "e7e5"),
        "depth": 18,
    }
    values.update(changes)
    return validate_analysis_line(**values)


def _result(**changes: object) -> AnalysisResultInput:
    values: dict[str, object] = {
        "quality": AnalysisQuality.BROWSER,
        "configuration_version": 1,
        "settings": {"Hash": 16, "Threads": 1, "Nested": [True, None]},
        "engine_name": "engine-independent-test-double",
        "engine_version": "v1",
        "lines": (_line(),),
    }
    values.update(changes)
    return validate_analysis_result(**values)


def test_normalized_line_and_result_values_are_immutable() -> None:
    line = _line(pv_uci=["e2e4", "e7e5"])
    result = _result(lines=[line])

    assert line.pv_uci == ("e2e4", "e7e5")
    assert result.lines == (line,)
    assert json.loads(json.dumps(result.settings)) == {
        "Hash": 16,
        "Threads": 1,
        "Nested": [True, None],
    }
    with pytest.raises(FrozenInstanceError):
        line.rank = 2  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.quality = AnalysisQuality.TOOL  # type: ignore[misc]
    with pytest.raises(TypeError, match="immutable"):
        result.settings["new_key"] = "not allowed"  # type: ignore[index]
    with pytest.raises(TypeError, match="immutable"):
        result.settings["Nested"] += (False,)  # type: ignore[operator]


@pytest.mark.parametrize("settings", [[], "{}", 1, None, {"bad": object()}, {"bad": float("nan")}])
def test_settings_must_be_a_json_object_with_json_serializable_values(settings: object) -> None:
    with pytest.raises(AnalysisValidationError):
        validate_settings_object(settings)


def test_settings_accept_an_empty_or_arbitrary_json_object_without_required_keys() -> None:
    assert json.loads(json.dumps(validate_settings_object({}))) == {}
    assert json.loads(json.dumps(validate_settings_object({"future_setting": {"value": 1}}))) == {
        "future_setting": {"value": 1}
    }


@pytest.mark.parametrize(
    "quality", [AnalysisQuality.BROWSER, AnalysisQuality.TOOL, "browser", "tool"]
)
def test_quality_domain_accepts_only_the_two_settled_levels(quality: object) -> None:
    assert _result(quality=quality).quality in (AnalysisQuality.BROWSER, AnalysisQuality.TOOL)


@pytest.mark.parametrize("quality", ["cloud", "", None, 1])
def test_quality_domain_rejects_unsettled_levels(quality: object) -> None:
    with pytest.raises(AnalysisValidationError):
        _result(quality=quality)


@pytest.mark.parametrize("version", [0, -1, True, "1"])
def test_configuration_version_must_be_an_integer_at_least_one(version: object) -> None:
    with pytest.raises(AnalysisValidationError):
        _result(configuration_version=version)


def test_signed_score_domains_preserve_white_point_of_view_without_new_bounds() -> None:
    assert _line(score_kind="cp", score_value=-250000).score_value == -250000
    assert _line(score_kind="mate", score_value=3).score_value == 3
    assert _line(score_kind="mate", score_value=-2).score_value == -2
    assert _line(score_kind="mate", score_value=0).score_value == 0

    with pytest.raises(AnalysisValidationError):
        _line(score_kind="centipawn")


@pytest.mark.parametrize("rank", [0, 6, True, "1"])
def test_rank_domain_is_one_through_five(rank: object) -> None:
    with pytest.raises(AnalysisValidationError):
        _line(rank=rank)


@pytest.mark.parametrize("depth", [-1, True, "18"])
def test_depth_must_be_a_nonnegative_integer(depth: object) -> None:
    with pytest.raises(AnalysisValidationError):
        _line(depth=depth)


@pytest.mark.parametrize(
    "wdl",
    [
        (-1, 1001, 0),
        (400, 300, 299),
        (400, True, 599),
    ],
)
def test_wdl_values_must_be_nonnegative_integers_summing_to_1000(
    wdl: tuple[object, object, object],
) -> None:
    with pytest.raises(AnalysisValidationError):
        _line(wdl_wins=wdl[0], wdl_draws=wdl[1], wdl_losses=wdl[2])


@pytest.mark.parametrize("pv", [[], "e2e4", [""], [1], None])
def test_pv_representation_must_be_nonempty_ordered_strings(pv: object) -> None:
    with pytest.raises(AnalysisValidationError):
        _line(pv_uci=pv)


def test_result_can_carry_no_lines_without_stage_two_terminal_or_legality_rules() -> None:
    result = _result(lines=[])

    assert result.lines == ()


def test_public_validation_outcomes_distinguish_expected_not_saved_reasons() -> None:
    assert PublicationOutcome.saved_result() == PublicationOutcome(saved=True)
    duplicate = PublicationOutcome.not_saved(NotSavedReason.DUPLICATE)
    stale = PublicationOutcome.not_saved("stale_or_outdated")
    lower = PublicationOutcome.not_saved("lower_quality")

    assert duplicate.saved is False
    assert duplicate.reason is NotSavedReason.DUPLICATE
    assert stale.reason is NotSavedReason.STALE_OR_OUTDATED
    assert lower.reason is NotSavedReason.LOWER_QUALITY

    with pytest.raises(AnalysisValidationError):
        PublicationOutcome(saved=True, reason=NotSavedReason.DUPLICATE)
    with pytest.raises(AnalysisValidationError):
        PublicationOutcome(saved=False)
