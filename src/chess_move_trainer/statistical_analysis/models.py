"""Adjusted GEE marginal contrasts; fits are bounded in a disposable process."""

from __future__ import annotations

from contextlib import AbstractContextManager
import multiprocessing as mp
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit
import statsmodels.api as sm

from .registry import validate_question

CATEGORICAL = {"learner_color", "time_class", "calendar_period", "opening", "phase"}


def prepare_frame(records, question):
    validate_question(question)
    selected = []
    eligible = [0, 0]
    games = [set(), set()]
    for record in records:
        if record["population"] != question.population:
            continue
        value = (f"{record['piece']}:{record['captured_piece']}" if question.feature == "capture_pair"
                 else record.get(question.feature))
        # Capture-pair questions compare captures with other captures, not quiet moves.
        if question.feature == "capture_pair" and not record["capture"]:
            continue
        if value is None:
            continue
        exposure = int(value == question.value)
        eligible[exposure] += 1
        games[exposure].add(record["game_id"])
        if record.get(question.outcome) is None or any(record.get(k) is None for k in question.adjustment):
            continue
        selected.append({**{k: record[k] for k in question.adjustment},
                         "exposure": exposure, "outcome": float(record[question.outcome]),
                         "game_id": record["game_id"], "opponent_id": record["opponent_id"],
                         "position_id": record["position_id"], "opening": record.get("opening"),
                         "history_sensitive": record["history_sensitive"],
                         "ply": record["ply"]})
    frame = pd.DataFrame(selected)
    counts = [int((frame.exposure == i).sum()) if len(frame) else 0 for i in (0, 1)]
    return frame, {"eligible": eligible, "model_complete": counts,
                   "eligible_games": [len(s) for s in games],
                   "coverage": [counts[i] / eligible[i] if eligible[i] else 0 for i in (0, 1)]}


def design(frame, adjustment):
    pieces = [pd.DataFrame({"intercept": 1.0, "exposure": frame.exposure.astype(float)}, index=frame.index)]
    for key in adjustment:
        if key in CATEGORICAL:
            pieces.append(pd.get_dummies(frame[key].astype(str), prefix=key, drop_first=True, dtype=float))
        else:
            values = frame[key].astype(float)
            sd = values.std(ddof=0)
            if sd > 0:
                pieces.append(((values - values.mean()) / sd).to_frame(key))
    matrix = pd.concat(pieces, axis=1).to_numpy(dtype=float)
    if not np.isfinite(matrix).all() or np.linalg.matrix_rank(matrix) != matrix.shape[1]:
        raise ValueError("non_identifiable_design")
    if len(frame) <= matrix.shape[1] + 2:
        raise ValueError("insufficient_parameter_support")
    return matrix


def _gee(y, x, groups, family, weights, exchangeable):
    if len(np.unique(groups)) < 3:
        raise ValueError("too_few_independent_clusters")
    if np.ptp(y) == 0:
        raise ValueError("constant_outcome")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = sm.GEE(y, x, groups=groups, family=family, weights=weights,
                       cov_struct=sm.cov_struct.Exchangeable() if exchangeable else sm.cov_struct.Independence())
        result = model.fit(maxiter=100, ctol=1e-7)
    if not result.converged or not np.isfinite(result.params).all() or not np.isfinite(result.cov_params()).all():
        raise ValueError("model_did_not_converge")
    if any("separation" in str(w.message).lower() for w in caught) or np.max(np.abs(result.params)) > 25:
        raise ValueError("separation_or_unstable_coefficients")
    return result


def fit_once(frame, question, *, game_weighted=False, exchangeable=False):
    frame = frame.reset_index(drop=True)
    x = design(frame, question.adjustment)
    y = frame.outcome.to_numpy(dtype=float)
    if not set(frame.exposure.unique()) == {0, 1}:
        raise ValueError("missing_comparison_group")
    if np.any(y < 0) or np.any(y > 1):
        raise ValueError("outcome_outside_unit_interval")
    groups = frame.game_id.to_numpy()
    weights = (1 / frame.groupby("game_id").game_id.transform("size")).to_numpy() if game_weighted else np.ones(len(frame))
    average_weights = weights / weights.sum()
    x0, x1 = x.copy(), x.copy()
    x0[:, 1], x1[:, 1] = 0, 1
    if question.outcome == "severe":
        if not set(np.unique(y)).issubset({0, 1}):
            raise ValueError("binary_outcome_required")
        fit = _gee(y, x, groups, sm.families.Binomial(), weights, exchangeable)
        p0, p1 = expit(x0 @ fit.params), expit(x1 @ fit.params)
        gradient = ((p1 * (1-p1) * average_weights) @ x1
                    - (p0 * (1-p0) * average_weights) @ x0)
        variance = float(gradient @ fit.cov_params() @ gradient)
        se = np.sqrt(max(0, variance))
    else:
        positive = y > 0
        binary = _gee(positive.astype(float), x, groups, sm.families.Binomial(), weights, exchangeable)
        if positive.sum() <= x.shape[1] + 2:
            raise ValueError("insufficient_positive_losses")
        magnitude = _gee(y[positive], x[positive], groups[positive],
                         sm.families.Gamma(sm.families.links.Log()), weights[positive], exchangeable)
        b0, b1 = expit(x0 @ binary.params), expit(x1 @ binary.params)
        m0, m1 = np.exp(x0 @ magnitude.params), np.exp(x1 @ magnitude.params)
        if max(m0.max(), m1.max()) > 1:
            raise ValueError("gamma_prediction_outside_loss_bounds")
        p0, p1 = b0*m0, b1*m1
        gb = ((m1*b1*(1-b1)*average_weights) @ x1 - (m0*b0*(1-b0)*average_weights) @ x0)
        gm = ((p1*average_weights) @ x1 - (p0*average_weights) @ x0)
        # Conservative covariance upper bound; bootstrap refits both parts jointly.
        se = np.sqrt(max(0, float(gb @ binary.cov_params() @ gb))) + np.sqrt(max(0, float(gm @ magnitude.cov_params() @ gm)))
    return {"effect": float(average_weights @ (p1-p0)),
            "adjusted_reference": float(average_weights @ p0),
            "adjusted_exposed": float(average_weights @ p1), "robust_se": float(se),
            "parameters": x.shape[1], "games": int(frame.game_id.nunique())}


def _worker(pipe, frame, question, maximum_calls):
    try:
        for _ in range(maximum_calls):
            request = pipe.recv()
            if request is None:
                break
            indices, clusters, options = request
            try:
                sample = frame if indices is None else frame.iloc[indices].copy()
                if clusters is not None:
                    sample["game_id"] = clusters
                pipe.send((True, fit_once(sample, question, **options)))
            except Exception as error:
                pipe.send((False, f"{type(error).__name__}: {error}"))
    except (EOFError, BrokenPipeError):
        pass
    finally:
        pipe.close()


class FitWorker(AbstractContextManager):
    """Persistent isolated fitter, with a hard deadline for every requested fit."""
    def __init__(self, frame, question, *, fit_seconds=30, maximum_calls=10020):
        from .artifacts import Budget
        Budget(fit_seconds)
        if maximum_calls < 1 or maximum_calls > 20000:
            raise ValueError("maximum_calls must be 1..20000")
        self.fit_seconds = fit_seconds
        context = mp.get_context("spawn")
        self.parent, child = context.Pipe()
        self.process = context.Process(target=_worker, args=(child, frame, question, maximum_calls), daemon=True)
        self.process.start()
        child.close()

    def fit(self, indices=None, clusters=None, **options):
        if not self.process.is_alive():
            raise RuntimeError("fit worker stopped")
        self.parent.send((indices, clusters, options))
        if not self.parent.poll(self.fit_seconds):
            self.process.terminate()
            self.process.join(timeout=5)
            raise TimeoutError("individual model fit exceeded its deadline")
        ok, value = self.parent.recv()
        if not ok:
            raise ValueError(value)
        return value

    def __exit__(self, *args):
        if self.process.is_alive():
            try:
                self.parent.send(None)
            except (BrokenPipeError, EOFError, OSError):
                pass
            self.process.join(timeout=2)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=5)
        self.parent.close()
