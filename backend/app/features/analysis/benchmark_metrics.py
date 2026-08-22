"""Versioned MP-09 Stockfish qualification calculations."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any

CANDIDATE_BUDGETS = (50_000, 100_000, 200_000, 400_000)
REFERENCE_BUDGET = 800_000
RUBRIC_V1 = "mp09-balanced-nodes-v1"
RUBRIC_V2 = "mp09-balanced-nodes-v2"
RUBRIC_VERSION = RUBRIC_V2
SUPPORTED_RUBRICS = (RUBRIC_V1, RUBRIC_V2)


def nearest_rank(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def _root_map(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {candidate["pv_uci"][0]: candidate for candidate in run["candidates"][:3]}


def _repeatable(first: dict[str, Any], second: dict[str, Any]) -> bool:
    first_roots = list(_root_map(first))
    second_roots = list(_root_map(second))
    return first_roots[0] == second_roots[0] and set(first_roots) == set(second_roots)


def _mate_winner(candidate: dict[str, Any]) -> int:
    if candidate["score_kind"] == "mate_given":
        return 1
    value = candidate["score_value"]
    return 1 if value > 0 else -1


def _score_drift(candidate: dict[str, Any], reference: dict[str, Any]) -> tuple[bool, int | None]:
    if candidate["score_kind"] != reference["score_kind"]:
        return False, None
    if candidate["score_kind"] == "cp":
        return True, abs(candidate["score_value"] - reference["score_value"])
    if _mate_winner(candidate) != _mate_winner(reference):
        return False, None
    return abs(abs(candidate["score_value"]) - abs(reference["score_value"])) <= 2, None


def _wdl_expectation(candidate: dict[str, Any]) -> float:
    return (candidate["wdl_wins"] + 0.5 * candidate["wdl_draws"]) / 1000


def _side_loss(best: float, selected: float, side_to_move: str) -> float:
    if side_to_move == "w":
        return best - selected
    if side_to_move == "b":
        return selected - best
    raise ValueError(f"invalid side to move: {side_to_move!r}")


def semantic_equivalence(
    candidate_best: dict[str, Any],
    reference_top3: dict[str, dict[str, Any]],
    side_to_move: str,
) -> dict[str, Any]:
    """Apply the frozen v2 gate using only reference evaluations for loss."""

    move = candidate_best["pv_uci"][0]
    reference_best = next(iter(reference_top3.values()))
    selected = reference_top3.get(move)
    detail: dict[str, Any] = {
        "candidate_move": move,
        "reference_rank": selected["rank"] if selected is not None else None,
        "side_to_move": side_to_move,
        "cp_loss": None,
        "wdl_expected_score_loss": None,
        "equivalent": False,
    }
    if selected is None or candidate_best["score_kind"] != selected["score_kind"]:
        return detail
    kind = selected["score_kind"]
    if kind == "cp":
        if reference_best["score_kind"] != "cp":
            return detail
        cp_loss = _side_loss(
            float(reference_best["score_value"]),
            float(selected["score_value"]),
            side_to_move,
        )
        wdl_loss = _side_loss(
            _wdl_expectation(reference_best), _wdl_expectation(selected), side_to_move
        )
        detail["cp_loss"] = cp_loss
        detail["wdl_expected_score_loss"] = wdl_loss
        detail["equivalent"] = cp_loss <= 20 and wdl_loss <= 0.020 + 1e-12
        return detail
    if reference_best["score_kind"] not in {"mate", "mate_given"}:
        return detail
    detail["equivalent"] = (
        _mate_winner(selected) == _mate_winner(reference_best)
        and abs(abs(selected["score_value"]) - abs(reference_best["score_value"])) <= 2
    )
    return detail


def duration_summary(runs: list[dict[str, Any]]) -> dict[str, float]:
    values = [run["wall_time_ms"] / 1000 for run in runs]
    return {
        "p50_seconds": statistics.median(values),
        "p95_seconds": nearest_rank(values, 0.95) or 0.0,
        "max_seconds": max(values),
    }


def evaluate_runs(
    runs: list[dict[str, Any]],
    *,
    rubric_version: str = RUBRIC_VERSION,
    fixtures: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if rubric_version not in SUPPORTED_RUBRICS:
        raise ValueError(f"unsupported benchmark rubric: {rubric_version}")
    if rubric_version == RUBRIC_V2 and (fixtures is None or len(fixtures) != 24):
        raise ValueError("mp09-balanced-nodes-v2 requires exactly 24 frozen fixtures")
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        grouped[(run["node_budget"], run["fixture_index"])].append(run)
    for pair in grouped.values():
        pair.sort(key=lambda item: item["repetition"])

    reference_repeatable = all(
        len(grouped[(REFERENCE_BUDGET, index)]) == 2
        and _repeatable(*grouped[(REFERENCE_BUDGET, index)])
        for index in range(24)
    )
    reference_runs = [run for run in runs if run["node_budget"] == REFERENCE_BUDGET]
    reference_runtime_ok = bool(reference_runs) and all(
        run["wall_time_ms"] <= 25_000 for run in reference_runs
    )
    budgets: dict[str, dict[str, Any]] = {}
    for budget in CANDIDATE_BUDGETS:
        repeatable = all(
            len(grouped[(budget, index)]) == 2 and _repeatable(*grouped[(budget, index)])
            for index in range(24)
        )
        top1 = 0
        overlaps: list[float] = []
        at_least_two = 0
        cp_drifts: list[float] = []
        wdl_drifts: list[float] = []
        score_shape_ok = True
        comparison_count = 0
        semantic_details: list[dict[str, Any]] = []
        for index in range(24):
            candidate_pair = grouped[(budget, index)]
            reference_pair = grouped[(REFERENCE_BUDGET, index)]
            if len(candidate_pair) != 2 or len(reference_pair) != 2:
                score_shape_ok = False
                continue
            candidate_roots = _root_map(candidate_pair[1])
            reference_roots = _root_map(reference_pair[1])
            if next(iter(candidate_roots)) == next(iter(reference_roots)):
                top1 += 1
            if rubric_version == RUBRIC_V2:
                assert fixtures is not None
                side = str(fixtures[index]["fen"]).split()[1]
                detail = semantic_equivalence(
                    next(iter(candidate_roots.values())), reference_roots, side
                )
                detail["fixture_index"] = index
                semantic_details.append(detail)
            common = set(candidate_roots) & set(reference_roots)
            overlaps.append(len(common) / 3)
            if len(common) >= 2:
                at_least_two += 1
            for move in common:
                comparison_count += 1
                score_ok, cp_drift = _score_drift(candidate_roots[move], reference_roots[move])
                score_shape_ok = score_shape_ok and score_ok
                if cp_drift is not None:
                    cp_drifts.append(float(cp_drift))
                wdl_drifts.append(
                    abs(
                        _wdl_expectation(candidate_roots[move])
                        - _wdl_expectation(reference_roots[move])
                    )
                )
        budget_runs = [run for run in runs if run["node_budget"] == budget]
        cp_median = statistics.median(cp_drifts) if cp_drifts else None
        cp_p90 = nearest_rank(cp_drifts, 0.90)
        wdl_median = statistics.median(wdl_drifts) if wdl_drifts else None
        wdl_p90 = nearest_rank(wdl_drifts, 0.90)
        mean_overlap = statistics.mean(overlaps) if len(overlaps) == 24 else 0.0
        runtime_ok = len(budget_runs) == 48 and all(
            run["wall_time_ms"] <= 15_000 for run in budget_runs
        )
        semantic_count = sum(bool(item["equivalent"]) for item in semantic_details)
        ranking_ok = top1 >= 21 if rubric_version == RUBRIC_V1 else semantic_count == 24
        qualifies = all(
            (
                reference_repeatable,
                reference_runtime_ok,
                repeatable,
                runtime_ok,
                ranking_ok,
                mean_overlap >= 0.80,
                at_least_two >= 22,
                score_shape_ok,
                comparison_count > 0,
                cp_median is not None and cp_median <= 25,
                cp_p90 is not None and cp_p90 <= 60,
                wdl_median is not None and wdl_median <= 0.025,
                wdl_p90 is not None and wdl_p90 <= 0.060,
            )
        )
        budget_result = {
            "qualifies": qualifies,
            "repeatable": repeatable,
            "runtime_ok": runtime_ok,
            "top1_agreement_count": top1,
            "mean_top3_overlap": mean_overlap,
            "at_least_two_common_count": at_least_two,
            "score_shape_ok": score_shape_ok,
            "matching_top3_comparison_count": comparison_count,
            "cp_comparison_count": len(cp_drifts),
            "cp_drift_median": cp_median,
            "cp_drift_p90_nearest_rank": cp_p90,
            "wdl_drift_median": wdl_median,
            "wdl_drift_p90_nearest_rank": wdl_p90,
            "duration": duration_summary(budget_runs),
        }
        if rubric_version == RUBRIC_V2:
            budget_result.update(
                {
                    "semantic_equivalence_count": semantic_count,
                    "semantic_equivalence": semantic_details,
                }
            )
        budgets[str(budget)] = budget_result
    selected = next(
        (budget for budget in CANDIDATE_BUDGETS if budgets[str(budget)]["qualifies"]), None
    )
    return {
        "reference_repeatable": reference_repeatable,
        "reference_runtime_ok": reference_runtime_ok,
        "reference_duration": duration_summary(reference_runs),
        "budgets": budgets,
        "selected_node_budget": selected,
    }
