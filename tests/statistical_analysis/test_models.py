import numpy as np
import pandas as pd
import pytest

from chess_move_trainer.statistical_analysis.calibration import simulate_frame, calibrate
from chess_move_trainer.statistical_analysis.models import FitWorker, fit_once
from chess_move_trainer.statistical_analysis.inference import cluster_draw, correct_and_gate, fit_contrast
from chess_move_trainer.statistical_analysis.registry import Question


def question(outcome="severe"):
    return Question("test", "Q01", "learner", "exposure", 1, outcome, adjustment=("before_material",))


def test_gee_reports_marginal_risk_and_real_cluster_support():
    frame, truth = simulate_frame(np.random.default_rng(5), "effect", games=300, effect=1.)
    fit = fit_once(frame, question())
    assert fit["effect"] == pytest.approx(truth, abs=.05)
    assert fit["effect"] == pytest.approx(fit["adjusted_exposed"] - fit["adjusted_reference"])
    assert fit["games"] == 300
    assert fit["robust_se"] > 0


def test_two_part_loss_and_degenerate_failure():
    frame, _ = simulate_frame(np.random.default_rng(2), "zero_heavy", games=200)
    fit = fit_once(frame, question("loss"))
    assert abs(fit["effect"]) < .03
    assert 0 < fit["adjusted_exposed"] < 1
    frame["outcome"] = 0
    with pytest.raises(ValueError, match="constant_outcome"):
        fit_once(frame, question())


def test_whole_game_draw_assigns_new_ids_to_repeated_games():
    frame = pd.DataFrame({"game_id": ["a", "a", "b", "b", "b", "c"]})
    indices, groups = cluster_draw(frame, np.random.default_rng(0))
    for group in set(groups):
        sampled = frame.iloc[indices[groups == group]]
        assert sampled.game_id.nunique() == 1
        assert len(sampled) == (frame.game_id == sampled.game_id.iloc[0]).sum()
    assert len(set(groups)) == 3


def test_isolated_fit_and_bootstrap_are_finite_and_fail_closed():
    frame, _ = simulate_frame(np.random.default_rng(5), "effect", games=120, effect=1.)
    with FitWorker(frame, question(), fit_seconds=20, maximum_calls=1) as worker:
        assert worker.fit()["effect"] > 0
    result = fit_contrast(frame, question(), family_size=100, replicates=8, seconds=60, fit_seconds=20)
    assert result["bootstrap_success"] > 0
    assert "diagnostic_bootstrap_budget" in result["gate_failures"]
    assert "calibration_not_validated" in result["gate_failures"]
    assert result["simultaneous_interval"][0] < result["ordinary_interval"][0]


def test_complete_family_includes_failed_and_unexecuted_slots():
    results = {"a": {"p_value": .03, "simultaneous_interval": [.04, .2],
                     "meaningful_effect": .02, "gate_failures": []},
               "b": {"status": "model_failed", "gate_failures": ["model_failed"]}}
    corrected = correct_and_gate(results, ["a", "b", "c"], complete=False)
    assert corrected["a"]["holm_p"] == pytest.approx(.09)
    assert corrected["b"]["holm_p"] is None
    assert corrected["c"]["status"] == "run_incomplete"
    assert "family_incomplete" in corrected["a"]["gate_failures"]


def test_reproducible_calibration_smoke_does_not_certify(tmp_path):
    a = calibrate(tmp_path / "a.json", repetitions=5, seconds=30)
    b = calibrate(tmp_path / "b.json", repetitions=5, seconds=30)
    assert a == b
    assert not a["promotion_accepted"] and not a["base_method_checks_pass"]
