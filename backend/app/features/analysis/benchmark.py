"""Execution and durable reporting for the frozen Stockfish qualification benchmark."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from .benchmark_fixtures import FIXTURE_ORDER_VERSION, BenchmarkFixture
from .benchmark_metrics import (
    CANDIDATE_BUDGETS,
    REFERENCE_BUDGET,
    RUBRIC_V1,
    RUBRIC_V2,
    RUBRIC_VERSION,
    evaluate_runs,
)
from .engine import ManagedStockfish, PythonChessProcess, close_process
from .errors import AnalysisValidationError
from .models import AnalysisProfile, AnalysisResult
from .provisioning import STOCKFISH_ARCHIVE_SHA256, STOCKFISH_ASSET, STOCKFISH_TAG

WATCHDOG_SECONDS = 30.0


def canonical_write(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="ascii",
    )
    os.replace(temporary, path)


def freeze_report(
    fixtures: list[BenchmarkFixture],
    exact_fen_count: int,
    *,
    rubric_version: str = RUBRIC_VERSION,
    fixture_source_sha256: str | None = None,
) -> dict[str, Any]:
    thresholds = {
        "mean_top3_overlap_minimum": 0.80,
        "at_least_two_common_minimum_count": 22,
        "cp_drift_median_maximum": 25,
        "cp_drift_p90_maximum": 60,
        "wdl_drift_median_maximum": 0.025,
        "wdl_drift_p90_maximum": 0.060,
        "candidate_seconds_maximum": 15,
        "reference_seconds_maximum": 25,
        "watchdog_seconds": WATCHDOG_SECONDS,
    }
    if rubric_version == RUBRIC_V1:
        thresholds["top1_minimum_count"] = 21
    elif rubric_version == RUBRIC_V2:
        thresholds.update(
            {
                "semantic_equivalence_minimum_count": 24,
                "semantic_cp_loss_maximum": 20,
                "semantic_wdl_expected_score_loss_maximum": 0.020,
                "semantic_reference_top_n": 3,
                "semantic_mate_distance_plies_maximum": 2,
            }
        )
    else:
        raise AnalysisValidationError(f"unsupported benchmark rubric: {rubric_version}")
    return {
        "report_schema_version": 1 if rubric_version == RUBRIC_V1 else 2,
        "status": "fixtures_frozen",
        "rubric": {
            "version": rubric_version,
            "fixture_order_version": FIXTURE_ORDER_VERSION,
            "candidate_node_budgets": list(CANDIDATE_BUDGETS),
            "reference_node_budget": REFERENCE_BUDGET,
            "repetitions": 2,
            "multipv": 5,
            "thresholds": thresholds,
            "percentile_method": "nearest-rank: sorted[ceil(p*n)-1]",
        },
        "fixtures": [fixture.as_dict() for fixture in fixtures],
        "corpus": {"eligible_exact_fen_count": exact_fen_count},
        **(
            {
                "fixture_source": {
                    "report": "mp09-stockfish-18-node-budget-v1.json",
                    "sha256": fixture_source_sha256,
                    "fixtures_equal": True,
                }
            }
            if fixture_source_sha256 is not None
            else {}
        ),
    }


def load_frozen_report(path: Path) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise AnalysisValidationError(f"frozen fixture report is unavailable: {error}") from error
    if report.get("status") != "fixtures_frozen" or len(report.get("fixtures", [])) != 24:
        raise AnalysisValidationError("benchmark requires the untouched frozen 24-position report")
    expected = freeze_report(
        [BenchmarkFixture(**fixture) for fixture in report["fixtures"]],
        report["corpus"]["eligible_exact_fen_count"],
    )
    if report != expected:
        raise AnalysisValidationError("frozen fixture/rubric report is not canonical")
    return report


def _profile(identity: Any, budget: int, rubric_version: str) -> AnalysisProfile:
    return AnalysisProfile(
        profile_id=f"{rubric_version}-{budget}",
        engine_binary_sha256=identity.binary_sha256,
        engine_name=identity.reported_name,
        engine_version=identity.version,
        node_budget=budget,
        options={
            "Clear Hash": "before_each_run",
            "new_game": "fresh_token_each_run",
        },
    )


def _serialize_result(
    result: AnalysisResult, fixture_index: int, repetition: int, budget: int
) -> dict[str, Any]:
    return {
        "fixture_index": fixture_index,
        "repetition": repetition,
        "node_budget": budget,
        "wall_time_ms": result.wall_time_ms,
        "completed_at": result.completed_at,
        "candidates": [
            {
                "rank": candidate.rank,
                "score_kind": candidate.score_kind,
                "score_value": candidate.score_value,
                "wdl_wins": candidate.wdl_wins,
                "wdl_draws": candidate.wdl_draws,
                "wdl_losses": candidate.wdl_losses,
                "pv_uci": list(candidate.pv_uci),
                "depth": candidate.depth,
                "seldepth": candidate.seldepth,
                "nodes": candidate.nodes,
                "engine_time_ms": candidate.engine_time_ms,
            }
            for candidate in result.candidates
        ],
    }


def _run_budget(
    executable: Path, fixtures: list[dict[str, Any]], budget: int, rubric_version: str
) -> tuple[list[dict[str, Any]], AnalysisProfile, int]:
    process = PythonChessProcess.launch(executable)
    profile = _profile(process.identity, budget, rubric_version)
    pid = process.pid
    adapter = ManagedStockfish(
        process, profile, watchdog_seconds=WATCHDOG_SECONDS, shutdown_seconds=5.0
    )
    runs: list[dict[str, Any]] = []
    try:
        for fixture_index, fixture in enumerate(fixtures):
            for repetition in (1, 2):
                result = adapter.analyse(fixture["fen"])
                runs.append(_serialize_result(result, fixture_index, repetition, budget))
    finally:
        adapter.close()
    if not process.wait_exited(0):
        raise AnalysisValidationError(f"gracefully closed benchmark PID {pid} remains alive")
    return runs, profile, pid


def _cleanup_proof(executable: Path) -> dict[str, Any]:
    graceful = PythonChessProcess.launch(executable)
    graceful_pid = graceful.pid
    close_process(graceful, 5.0)
    if not graceful.wait_exited(0):
        raise AnalysisValidationError("graceful cleanup proof left its tracked child alive")
    forced = PythonChessProcess.launch(executable)
    forced_pid = forced.pid
    forced.terminate()
    if not forced.wait_exited(5.0):
        raise AnalysisValidationError("forced cleanup proof left its tracked child alive")
    return {
        "graceful_pid": graceful_pid,
        "graceful_exited": True,
        "forced_pid": forced_pid,
        "forced_exited": True,
    }


def _install_metadata(executable: Path) -> dict[str, Any]:
    try:
        metadata = json.loads((executable.parent / "install.json").read_text(encoding="ascii"))
    except (OSError, ValueError) as error:
        raise AnalysisValidationError(
            f"verified install metadata is unavailable: {error}"
        ) from error
    if (
        metadata.get("tag") != STOCKFISH_TAG
        or metadata.get("asset") != STOCKFISH_ASSET
        or metadata.get("archive_sha256") != STOCKFISH_ARCHIVE_SHA256
    ):
        raise AnalysisValidationError("installed engine does not match the pinned official archive")
    return metadata


def execute_benchmark(executable: Path, frozen: dict[str, Any]) -> dict[str, Any]:
    rubric_version = frozen["rubric"]["version"]
    metadata = _install_metadata(executable)
    started = time.monotonic()
    all_runs: list[dict[str, Any]] = []
    profiles: dict[str, dict[str, Any]] = {}
    graceful_pids: list[int] = []
    for budget in (*CANDIDATE_BUDGETS, REFERENCE_BUDGET):
        runs, profile, pid = _run_budget(executable, frozen["fixtures"], budget, rubric_version)
        all_runs.extend(runs)
        graceful_pids.append(pid)
        profiles[str(budget)] = {
            "profile_id": profile.profile_id,
            "settings_fingerprint": profile.fingerprint,
            "settings": json.loads(profile.settings_json),
        }
    metrics = evaluate_runs(all_runs, rubric_version=rubric_version, fixtures=frozen["fixtures"])
    selected = metrics["selected_node_budget"]
    elapsed = time.monotonic() - started
    cleanup = _cleanup_proof(executable)
    selected_runs = [run for run in all_runs if run["node_budget"] == selected]
    average_seconds = (
        sum(run["wall_time_ms"] for run in selected_runs) / len(selected_runs) / 1000
        if selected_runs
        else 0
    )
    count = frozen["corpus"]["eligible_exact_fen_count"]
    selected_payloads = [
        len(json.dumps(run, sort_keys=True, separators=(",", ":")).encode("ascii"))
        for run in selected_runs
        if run["repetition"] == 2
    ]
    average_payload = sum(selected_payloads) / len(selected_payloads) if selected_payloads else 0
    report = dict(frozen)
    report.update(
        {
            "status": "qualified" if selected is not None else "qualification_failed",
            "engine": {
                "tag": metadata["tag"],
                "asset": metadata["asset"],
                "archive_sha256": metadata["archive_sha256"],
                "binary_sha256": metadata["binary_sha256"],
                "reported_name": metadata["reported_name"],
                "version": metadata["version"],
            },
            "profiles": profiles,
            "runs": all_runs,
            "qualification": metrics,
            "benchmark_elapsed_seconds": elapsed,
            "projections": {
                "method": "selected-budget mean observed wall seconds times exact-FEN count",
                "one_worker_seconds": average_seconds * count,
                "five_worker_seconds": average_seconds * count / 5,
                "hash_memory_mib_one_worker": 128,
                "hash_memory_mib_five_workers": 640,
                "disk_method": "mean canonical selected second-run JSON payload bytes times count",
                "mean_payload_bytes": average_payload,
                "projected_payload_bytes": average_payload * count,
            },
            "watchdog": {
                "seconds": WATCHDOG_SECONDS,
                "maximum_observed_seconds": max(run["wall_time_ms"] for run in all_runs) / 1000,
                "margin_seconds": WATCHDOG_SECONDS
                - max(run["wall_time_ms"] for run in all_runs) / 1000,
            },
            "cleanup": {
                "benchmark_graceful_pids": graceful_pids,
                **cleanup,
            },
        }
    )
    if (
        evaluate_runs(report["runs"], rubric_version=rubric_version, fixtures=report["fixtures"])
        != report["qualification"]
    ):
        raise AnalysisValidationError("durable benchmark report is not recomputable")
    return report


def freeze_from_v1_report(path: Path) -> dict[str, Any]:
    """Validate historical v1 evidence and derive the predeclared v2 fixture freeze."""

    raw = path.read_bytes()
    try:
        report = json.loads(raw)
    except ValueError as error:
        raise AnalysisValidationError(f"version-1 report is invalid: {error}") from error
    if (
        report.get("rubric", {}).get("version") != RUBRIC_V1
        or report.get("status") != "qualification_failed"
        or len(report.get("fixtures", [])) != 24
        or len(report.get("runs", [])) != 240
    ):
        raise AnalysisValidationError(
            "version-1 report is not the complete failed benchmark evidence"
        )
    if evaluate_runs(report["runs"], rubric_version=RUBRIC_V1) != report["qualification"]:
        raise AnalysisValidationError("version-1 report qualification does not recompute")
    fixtures = [BenchmarkFixture(**fixture) for fixture in report["fixtures"]]
    return freeze_report(
        fixtures,
        report["corpus"]["eligible_exact_fen_count"],
        rubric_version=RUBRIC_V2,
        fixture_source_sha256=hashlib.sha256(raw).hexdigest(),
    )


def validate_same_fixtures(
    frozen: dict[str, Any], fixtures: list[BenchmarkFixture], exact_fen_count: int
) -> None:
    if [fixture.as_dict() for fixture in fixtures] != frozen.get(
        "fixtures"
    ) or exact_fen_count != frozen.get("corpus", {}).get("eligible_exact_fen_count"):
        raise AnalysisValidationError("live read-only fixture selection no longer matches v1")
