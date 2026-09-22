"""Seeded method checks with known truth. Not a certificate for the full pipeline."""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import beta

from .artifacts import Budget, digest, write_json
from .models import fit_once
from .protocol import DEFAULT_PROTOCOL as P
from .registry import Question

SCENARIOS = ("null", "effect", "unequal_games", "confounding", "zero_heavy", "rare",
             "repeated_opponents", "missing_not_at_random")


def simulate_frame(rng, scenario, *, games=120, effect=0.0):
    lengths = rng.integers(2, 24, games) if scenario == "unequal_games" else np.repeat(10, games)
    game_ids = np.repeat(np.arange(games), lengths)
    context = rng.normal(size=len(game_ids))
    opponent_ids = game_ids // 4
    # A game-shared Bernoulli probability makes within-game observations dependent.
    cluster = rng.normal(0, .8, games)
    if scenario == "repeated_opponents":
        cluster += np.repeat(rng.normal(0, 1.2, (games+3)//4), 4)[:games]
    exposure = rng.binomial(1, expit(context) if scenario == "confounding" else .45, len(game_ids))
    probability = expit(-2.0 + .5*context + cluster[game_ids] + effect*exposure)
    if scenario == "rare":
        probability *= .02
    y = rng.binomial(1, probability)
    if scenario == "zero_heavy":
        y = y * rng.beta(2, 8, len(y))
    frame = pd.DataFrame({"game_id": game_ids, "opponent_id": opponent_ids,
                          "position_id": np.arange(len(y)), "opening": game_ids % 5,
                          "exposure": exposure,
                          "outcome": y, "before_material": context, "history_sensitive": False})
    # Exact conditional standardized truth for this simulated covariate/cluster population.
    true0 = expit(-2 + .5*context + cluster[game_ids])
    true1 = expit(-2 + .5*context + cluster[game_ids] + effect)
    truth = float(np.mean(true1-true0))
    if scenario == "zero_heavy":
        truth *= .2
    if scenario == "rare":
        truth *= .02
    if scenario == "missing_not_at_random":
        keep = rng.random(len(y)) > np.where((exposure == 1) & (y == 1), .8, .05)
        frame = frame.loc[keep].reset_index(drop=True)
    return frame, truth


def binomial_interval(successes, total):
    if total == 0:
        return [0.0, 1.0]
    return [0.0 if successes == 0 else float(beta.ppf(.025, successes, total-successes+1)),
            1.0 if successes == total else float(beta.ppf(.975, successes+1, total-successes))]


def calibrate(output: Path, *, scenario="null", repetitions=1000, seconds=300, seed=P.seed):
    if scenario not in SCENARIOS or not 1 <= repetitions <= 10000:
        raise ValueError("unknown scenario or repetitions outside 1..10000")
    if output.exists():
        raise FileExistsError("calibration report is immutable")
    budget, rng = Budget(seconds), np.random.default_rng(seed)
    outcome = "loss" if scenario == "zero_heavy" else "severe"
    q = Question("simulation", "simulation", "learner", "exposure", 1, outcome,
                 adjustment=("before_material",))
    counts = {"fitted": 0, "failed": 0, "rejected": 0, "covered": 0, "sign_errors": 0}
    estimates, errors = [], {}
    report = {"status": "run_incomplete", "scenario": scenario, "seed": seed,
              "requested": repetitions, "protocol_sha256": P.identity,
              "scope": "base_gee_only_not_bootstrap_or_complete_promotion_calibration",
              "promotion_accepted": False}
    try:
        for index in range(repetitions):
            budget.check()
            effect = .8 if scenario == "effect" else 0.
            frame, truth = simulate_frame(rng, scenario, effect=effect)
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    fit = fit_once(frame, q)
                estimate, se = fit["effect"], fit["robust_se"]
                if not np.isfinite(se) or se <= 0:
                    raise ValueError("invalid standard error")
                counts["fitted"] += 1
                counts["rejected"] += abs(estimate / se) > 1.96
                counts["covered"] += estimate-1.96*se <= truth <= estimate+1.96*se
                counts["sign_errors"] += truth != 0 and estimate*truth < 0
                estimates.append(estimate-truth)
            except (ValueError, np.linalg.LinAlgError) as error:
                counts["failed"] += 1
                errors[str(error)] = errors.get(str(error), 0) + 1
            if (index + 1) % 50 == 0:
                write_json(output.with_suffix(".checkpoint.json"), {**report, "counts": counts})
        fitted = counts["fitted"]
        rejection = binomial_interval(counts["rejected"], fitted)
        coverage = binomial_interval(counts["covered"], fitted)
        report.update(status="complete", counts=counts, failures=errors,
                      mean_bias=float(np.mean(estimates)) if estimates else None,
                      rejection_rate=counts["rejected"]/fitted if fitted else None,
                      coverage_rate=counts["covered"]/fitted if fitted else None,
                      rejection_mc_interval=rejection, coverage_mc_interval=coverage,
                      base_method_checks_pass=(repetitions >= 1000 and fitted/repetitions >= .99
                                               and coverage[0] >= .925
                                               and (scenario == "effect" or rejection[1] <= .075)))
        report["identity"] = digest(report)
        write_json(output, report)
        return report
    except BaseException as error:
        write_json(output.with_suffix(".checkpoint.json"), {**report, "counts": counts, "error": str(error)})
        raise
