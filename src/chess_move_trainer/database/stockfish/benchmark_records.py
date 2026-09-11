"""Benchmark record, checkpoint, and manifest helpers."""

from __future__ import annotations

import csv
import random
import time
import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ..analysis import AnalysisQuality
from .engine import SearchMetrics
from ..positions import CanonicalPosition, canonicalize_fen
from .benchmark_artifacts import _StoredAttempts, _is_within, _normalized_directory, _normalized_file_path, _sha256_file
from .benchmark_models import BENCHMARK_FORMAT_VERSION, BenchmarkCompatibilityError, BenchmarkInputError, BenchmarkJob, BenchmarkOutcome, BenchmarkPersistenceError, BenchmarkSpec, _positive_int_tuple
from .configuration import CONFIGURATION_VERSION, MULTI_PV, STOCKFISH_NAME, STOCKFISH_VERSION

def _expected_manifest(
    spec: BenchmarkSpec, executable: Path, position_input: Path
) -> dict[str, Any]:
    return {
        **spec.as_manifest_dict(),
        "input": {
            "path": str(_normalized_file_path(position_input)),
            "sha256": _sha256_file(position_input),
        },
        "engine": {
            "name": STOCKFISH_NAME,
            "version": STOCKFISH_VERSION,
            "executable": str(_normalized_file_path(executable)),
            "sha256": _sha256_file(executable) if executable.exists() else None,
        },
        "options": {
            "multipv": MULTI_PV,
            "configuration_version": CONFIGURATION_VERSION,
            "search_limit": "nodes",
        },
    }


def _profile_blocks(spec: BenchmarkSpec) -> tuple[tuple[int, int], ...]:
    blocks = [
        (threads, hash_mb) for threads in spec.thread_counts for hash_mb in spec.hash_sizes_mb
    ]
    random.Random(spec.shuffle_seed).shuffle(blocks)
    return tuple(blocks)


def _job_fields(job: BenchmarkJob) -> dict[str, Any]:
    return {
        "position_id": job.position.position_id,
        "fen": job.position.fen,
        "round": job.round_number,
        "nodes_requested": job.nodes,
        "threads": job.threads,
        "hash_mb": job.hash_mb,
        "multipv": MULTI_PV,
        "configuration_version": CONFIGURATION_VERSION,
    }


def _success_record(
    job: BenchmarkJob, attempt: int, analysis: Any, elapsed: float
) -> dict[str, Any]:
    lines = [
        {
            "rank": line.rank,
            "score_kind": line.score_kind.value,
            "score_value": line.score_value,
            "score_perspective": "white",
            "wdl": {
                "wins": line.wdl_wins,
                "draws": line.wdl_draws,
                "losses": line.wdl_losses,
            },
            "pv_uci": list(line.pv_uci),
            "depth": line.depth,
        }
        for line in analysis.lines
    ]
    metrics = getattr(analysis, "metrics", None)
    return {
        "record_type": "benchmark_attempt",
        "status": "success",
        "job_id": job.job_id,
        "attempt": attempt,
        **_job_fields(job),
        "engine": {"name": STOCKFISH_NAME, "version": STOCKFISH_VERSION},
        "wall_clock_seconds": elapsed,
        "metrics": _metrics_dict(metrics),
        "terminal_kind": None if analysis.terminal_kind is None else analysis.terminal_kind.value,
        "lines": lines,
    }


def _metrics_dict(metrics: SearchMetrics | None) -> dict[str, int | None]:
    if metrics is None:
        return {
            "engine_nodes": None,
            "engine_nps": None,
            "depth": None,
            "seldepth": None,
            "hashfull": None,
            "time_ms": None,
        }
    return {
        "engine_nodes": metrics.nodes,
        "engine_nps": metrics.nps,
        "depth": metrics.depth,
        "seldepth": metrics.seldepth,
        "hashfull": metrics.hashfull,
        "time_ms": metrics.time_ms,
    }


def _checkpoint_payload(
    *,
    records: Sequence[Mapping[str, Any]],
    successful: Iterable[str],
    failed: Iterable[str],
    total_jobs: int,
    complete: bool,
    interrupted: bool,
) -> dict[str, Any]:
    return {
        "format_version": BENCHMARK_FORMAT_VERSION,
        "dataset_state": "complete" if complete else "incomplete",
        "complete": complete,
        "interrupted": interrupted,
        "total_jobs": total_jobs,
        "attempt_count": len(records),
        "successful_job_ids": sorted(successful),
        "failed_job_ids": sorted(failed),
    }


def _summary_payload(
    records: Sequence[Mapping[str, Any]], total_jobs: int, complete: bool
) -> dict[str, Any]:
    successful = sum(record.get("status") == "success" for record in records)
    failed = sum(record.get("status") == "failure" for record in records)
    return {
        "format_version": BENCHMARK_FORMAT_VERSION,
        "dataset_state": "complete" if complete else "incomplete",
        "total_jobs": total_jobs,
        "successful_attempts": successful,
        "failed_attempts": failed,
        "attempt_count": len(records),
        "records": list(records),
    }


_SUMMARY_COLUMNS: Final[tuple[str, ...]] = (
    "job_id",
    "attempt",
    "status",
    "position_id",
    "round",
    "nodes_requested",
    "threads",
    "hash_mb",
    "wall_clock_seconds",
    "engine_nodes",
    "engine_nps",
    "depth",
    "seldepth",
    "hashfull",
    "time_ms",
    "failure_category",
    "failure_message",
    "lines_json",
)


def _summary_csv(records: Sequence[Mapping[str, Any]]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=_SUMMARY_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for record in records:
        metrics = record.get("metrics", {})
        failure = record.get("failure", {})
        writer.writerow(
            {
                "job_id": record.get("job_id"),
                "attempt": record.get("attempt"),
                "status": record.get("status"),
                "position_id": record.get("position_id"),
                "round": record.get("round"),
                "nodes_requested": record.get("nodes_requested"),
                "threads": record.get("threads"),
                "hash_mb": record.get("hash_mb"),
                "wall_clock_seconds": record.get("wall_clock_seconds"),
                "engine_nodes": metrics.get("engine_nodes"),
                "engine_nps": metrics.get("engine_nps"),
                "depth": metrics.get("depth"),
                "seldepth": metrics.get("seldepth"),
                "hashfull": metrics.get("hashfull"),
                "time_ms": metrics.get("time_ms"),
                "failure_category": failure.get("category"),
                "failure_message": failure.get("message"),
                "lines_json": json.dumps(record.get("lines", []), separators=(",", ":")),
            }
        )
    return output.getvalue()


def _load_attempts(path: Path, jobs_by_id: Mapping[str, BenchmarkJob]) -> _StoredAttempts:
    if not path.exists():
        return _StoredAttempts((), frozenset(), frozenset())
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError("attempt record is not an object")
                job_id = record.get("job_id")
                if job_id not in jobs_by_id:
                    raise BenchmarkCompatibilityError(
                        f"attempt record line {line_number} belongs to an incompatible job"
                    )
                if record.get("record_type") != "benchmark_attempt" or record.get("status") not in (
                    "success",
                    "failure",
                ):
                    raise ValueError("attempt record has an invalid type or status")
                records.append(record)
    except BenchmarkCompatibilityError:
        raise
    except (OSError, ValueError) as error:
        raise BenchmarkCompatibilityError("existing benchmark attempts are unreadable") from error
    successful, failed = _current_job_sets(records)
    return _StoredAttempts(tuple(records), successful, failed)


def _current_job_sets(
    records: Sequence[Mapping[str, Any]],
) -> tuple[frozenset[str], frozenset[str]]:
    """Return the latest status for each job, not the historical attempt mix."""

    latest: dict[str, str] = {}
    for record in records:
        latest[str(record["job_id"])] = str(record["status"])
    return (
        frozenset(job_id for job_id, status in latest.items() if status == "success"),
        frozenset(job_id for job_id, status in latest.items() if status == "failure"),
    )


def _validate_checkpoint(
    path: Path,
    stored: _StoredAttempts,
    jobs_by_id: Mapping[str, BenchmarkJob],
) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise BenchmarkCompatibilityError(
            "existing benchmark checkpoint is unreadable"
        ) from error
    if (
        not isinstance(payload, Mapping)
        or payload.get("format_version") != BENCHMARK_FORMAT_VERSION
    ):
        raise BenchmarkCompatibilityError(
            "existing benchmark checkpoint has an incompatible format"
        )
    successful = frozenset(payload.get("successful_job_ids", ()))
    failed = frozenset(payload.get("failed_job_ids", ()))
    if not successful <= jobs_by_id.keys() or not failed <= jobs_by_id.keys():
        raise BenchmarkCompatibilityError("existing benchmark checkpoint contains unknown jobs")
    if successful != stored.successful_job_ids or not failed <= stored.failed_job_ids:
        raise BenchmarkCompatibilityError("existing benchmark checkpoint disagrees with attempts")


def _records_for_job(
    records: Sequence[Mapping[str, Any]], job_id: str
) -> tuple[Mapping[str, Any], ...]:
    return tuple(record for record in records if record.get("job_id") == job_id)


def _outcome(
    artifact_dir: Path,
    jobs_by_id: Mapping[str, BenchmarkJob],
    stored: _StoredAttempts,
    *,
    resumed: bool,
) -> BenchmarkOutcome:
    return BenchmarkOutcome(
        artifact_dir=artifact_dir,
        total_jobs=len(jobs_by_id),
        successful_jobs=len(stored.successful_job_ids),
        failed_jobs=len(stored.failed_job_ids),
        attempts=len(stored.records),
        complete=len(stored.successful_job_ids) == len(jobs_by_id),
        resumed=resumed,
    )

