"""Whole-cluster resampling, corrected uncertainty, and fail-closed evidence gates."""

from collections import Counter

import numpy as np
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests

from .artifacts import Budget
from .models import FitWorker
from .protocol import DEFAULT_PROTOCOL as P


def cluster_draw(frame, rng, key="game_id"):
    labels = frame[key].astype(str).to_numpy()
    if key == "opponent_id" and frame[key].isna().any():
        raise ValueError("missing_opponent_identity")
    members = [np.flatnonzero(labels == label) for label in sorted(set(labels))]
    selected = rng.integers(0, len(members), len(members))
    indices = np.concatenate([members[i] for i in selected])
    # Distinct draw IDs are essential when the same game is sampled twice.
    clusters = np.concatenate([np.repeat(draw, len(members[i])) for draw, i in enumerate(selected)])
    return indices, clusters


def support_failures(frame, counts):
    failures = []
    if len(frame) == 0:
        return ["no_comparable_records"]
    if frame.game_id.nunique() < P.minimum_games:
        failures.append("underpowered_games")
    for value in (0, 1):
        if frame.loc[frame.exposure == value, "game_id"].nunique() < P.minimum_group_games:
            failures.append(f"underpowered_group_{value}")
    if (
        min(counts["coverage"]) < P.minimum_coverage
        or abs(counts["coverage"][0] - counts["coverage"][1]) > P.maximum_coverage_gap
    ):
        failures.append("coverage_blocked")
    for event in (False, True):
        if frame.loc[(frame.outcome > 0) == event, "game_id"].nunique() < P.minimum_event_games:
            failures.append("rare_outcome_games")
    return sorted(set(failures))


def fit_contrast(
    frame,
    question,
    family_size,
    *,
    replicates=P.bootstrap_replicates,
    seconds=300,
    fit_seconds=30,
    seed=P.seed,
):
    if not 2 <= replicates <= P.bootstrap_cap:
        raise ValueError("replicates must be 2..10000")
    budget = Budget(seconds)
    rng = np.random.default_rng(seed)
    errors, draws, sensitivities = Counter(), [], {}
    with FitWorker(
        frame, question, fit_seconds=fit_seconds, maximum_calls=replicates + 20
    ) as worker:
        base = worker.fit()
        for _ in range(replicates):
            budget.check()
            indices, clusters = cluster_draw(frame, rng)
            try:
                draws.append(worker.fit(indices, clusters)["effect"])
            except ValueError as error:
                errors[str(error)] += 1
        for key, options in (
            ("game_weighted", {"game_weighted": True}),
            ("exchangeable", {"exchangeable": True}),
        ):
            budget.check()
            try:
                sensitivities[key] = worker.fit(**options)["effect"]
            except ValueError as error:
                sensitivities[key] = {"failure": str(error)}
        for group in ("game_id", "opponent_id", "opening", "position_id"):
            budget.check()
            if group not in frame.columns:
                sensitivities["without_dominant_" + group] = {"failure": "unavailable_column"}
                continue
            largest = frame[group].value_counts().index[0] if frame[group].notna().any() else None
            if largest is None:
                sensitivities["without_dominant_" + group] = {"failure": "unknown cluster"}
                continue
            indices = np.flatnonzero((frame[group] != largest).to_numpy())
            try:
                sensitivities["without_dominant_" + group] = worker.fit(indices)["effect"]
            except ValueError as error:
                sensitivities["without_dominant_" + group] = {"failure": str(error)}
    if len(draws) < 2:
        raise ValueError("insufficient_successful_bootstraps")
    se = max(base["robust_se"], float(np.std(draws, ddof=1)))
    if not np.isfinite(se) or se <= 0:
        raise ValueError("invalid_uncertainty")
    z = float(norm.ppf(1 - P.alpha / (2 * family_size)))
    effect = base["effect"]
    interval = [max(-1.0, effect - z * se), min(1.0, effect + z * se)]
    failures = []
    if len(draws) / replicates < P.minimum_fit_success:
        failures.append("bootstrap_fit_failures")
    if replicates < P.bootstrap_replicates:
        failures.append("diagnostic_bootstrap_budget")
    threshold = P.meaningful_risk if question.outcome == "severe" else P.meaningful_loss
    for value in sensitivities.values():
        if isinstance(value, dict) or value * effect < 0 or abs(value - effect) > threshold:
            failures.append("sensitivity_unstable")
    concentration = {}
    for group in ("game_id", "opponent_id", "opening", "position_id"):
        if group not in frame.columns:
            concentration[group] = None
        else:
            concentration[group] = (
                float(frame[group].value_counts(normalize=True).max())
                if frame[group].notna().any()
                else None
            )
    if any(
        concentration[k] is None or concentration[k] > P.maximum_cluster_share
        for k in ("game_id", "opponent_id", "position_id")
    ):
        failures.append("cluster_concentration")
    if frame.history_sensitive.any():
        failures.append("history_sensitivity_not_validated")
    # No automatic promotion from incomplete calibration or missing registered stresses.
    failures.extend(
        [
            "calibration_not_validated",
            "registered_sensitivity_suite_incomplete",
            "crossed_dependence_not_validated",
            "overlap_not_validated",
        ]
    )
    return {
        **base,
        "standard_error": se,
        "simultaneous_interval": interval,
        "ordinary_interval": [effect - 1.96 * se, effect + 1.96 * se],
        "p_value": float(2 * norm.sf(abs(effect / se))),
        "bootstrap_success": len(draws),
        "bootstrap_requested": replicates,
        "bootstrap_errors": dict(errors),
        "bootstrap_quantiles": [float(v) for v in np.quantile(draws, [0.025, 0.5, 0.975])],
        "seed": seed,
        "sensitivities": sensitivities,
        "concentration": concentration,
        "gate_failures": sorted(set(failures)),
        "meaningful_effect": threshold,
    }


def correct_and_gate(results, family_ids, *, complete=False):
    if len(set(family_ids)) != len(family_ids):
        raise ValueError("duplicate hypothesis IDs")
    if set(results) - set(family_ids):
        raise ValueError("unregistered hypotheses")
    pvalues = []
    for identifier in family_ids:
        p = results.get(identifier, {}).get("p_value")
        if p is not None and (not np.isfinite(p) or not 0 <= p <= 1):
            raise ValueError("invalid p-value")
        pvalues.append(p if p is not None else 1.0)
    holm = multipletests(pvalues, alpha=P.alpha, method="holm")[1]
    bh = multipletests(pvalues, alpha=P.alpha, method="fdr_bh")[1]
    for i, identifier in enumerate(family_ids):
        result = results.setdefault(
            identifier, {"status": "run_incomplete", "gate_failures": ["not_executed"]}
        )
        failures = set(result.get("gate_failures", []))
        if not complete:
            failures.add("family_incomplete")
        if result.get("p_value") is not None:
            result["holm_p"] = float(holm[i])
            result["bh_q_diagnostic"] = float(bh[i])
            if holm[i] > P.alpha:
                failures.add("multiplicity_gate")
            lo, hi = result["simultaneous_interval"]
            threshold = result["meaningful_effect"]
            if not (lo > threshold or hi < -threshold):
                failures.add("meaningful_effect_interval_gate")
            result["status"] = "supported" if not failures else "diagnostic_only"
        else:
            result["holm_p"] = result["bh_q_diagnostic"] = None
        result["gate_failures"] = sorted(failures)
    return results
