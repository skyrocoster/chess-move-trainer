"""Resumable benchmark execution."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Protocol

from ..analysis import AnalysisQuality
from ..positions import CanonicalPosition, canonicalize_fen
from .configuration import (
    CONFIGURATION_VERSION,
    MULTI_PV,
    STOCKFISH_NAME,
    STOCKFISH_VERSION,
    StockfishProfile,
)
from .engine import ANALYSIS_WATCHDOG_SECONDS, SearchMetrics, StockfishEngine

BENCHMARK_FORMAT_VERSION: Final[int] = 1
from .benchmark_models import BENCHMARK_FORMAT_VERSION, DEFAULT_ARTIFACT_WRITE_RETRIES, DEFAULT_HASH_SIZES_MB, DEFAULT_NODE_BUDGETS, DEFAULT_REPETITIONS, DEFAULT_SHUFFLE_SEED, DEFAULT_THREAD_COUNTS, _MAX_DIAGNOSTIC_LENGTH, BenchmarkCompatibilityError, BenchmarkError, BenchmarkInputError, BenchmarkInterrupted, BenchmarkJob, BenchmarkOutcome, BenchmarkPersistenceError, BenchmarkPosition, BenchmarkSpec
from .benchmark_records import _checkpoint_payload, _current_job_sets, _expected_manifest, _job_fields, _load_attempts, _outcome, _profile_blocks, _records_for_job, _success_record, _summary_csv, _summary_payload, _validate_checkpoint
from .benchmark_artifacts import _ArtifactPaths, _StoredAttempts, ArtifactWriter, AtomicArtifactWriter, _bounded_message, _is_transient_artifact_error, _is_within, _normalized_directory, _normalized_file_path, _sha256_file


class BenchmarkRunner:
    """Run and resume one deterministic benchmark matrix."""

    def __init__(
        self,
        spec: BenchmarkSpec,
        *,
        executable: str | Path,
        position_input: str | Path,
        output_dir: str | Path,
        engine_factory: Callable[..., Any] | None = None,
        artifact_writer: ArtifactWriter | None = None,
        artifact_write_retries: int = DEFAULT_ARTIFACT_WRITE_RETRIES,
        retry_delay_seconds: float = 0.0,
        progress: Callable[[str], None] | None = None,
    ) -> None:
        if type(artifact_write_retries) is not int or artifact_write_retries < 0:
            raise BenchmarkInputError("artifact write retries must be a non-negative integer")
        if isinstance(retry_delay_seconds, bool):
            raise BenchmarkInputError("artifact retry delay must be finite and non-negative")
        try:
            retry_delay = float(retry_delay_seconds)
        except (TypeError, ValueError) as error:
            raise BenchmarkInputError(
                "artifact retry delay must be finite and non-negative"
            ) from error
        if retry_delay < 0 or not math.isfinite(retry_delay):
            raise BenchmarkInputError("artifact retry delay must be finite and non-negative")
        self.spec = spec
        self.executable = Path(executable)
        self.position_input = Path(position_input)
        self.output_dir = Path(output_dir)
        self.engine_factory = engine_factory or StockfishEngine
        self.artifact_writer = artifact_writer or AtomicArtifactWriter()
        self.artifact_write_retries = artifact_write_retries
        self.retry_delay_seconds = retry_delay
        self.progress = progress or (lambda message: print(message, flush=True))

    def run(self) -> BenchmarkOutcome:
        paths = self._artifact_paths()
        paths.directory.mkdir(parents=True, exist_ok=True)
        expected_manifest = _expected_manifest(self.spec, self.executable, self.position_input)
        resumed = self._prepare_artifacts(paths, expected_manifest)
        jobs = self.spec.jobs()
        jobs_by_id = {job.job_id: job for job in jobs}
        stored = _load_attempts(paths.attempts, jobs_by_id)
        if paths.checkpoint.exists():
            _validate_checkpoint(paths.checkpoint, stored, jobs_by_id)

        if stored.successful_job_ids == jobs_by_id.keys():
            self._finish_artifacts(paths, stored.records, jobs_by_id, interrupted=False)
            self.progress(f"benchmark complete: {paths.directory}")
            return _outcome(paths.directory, jobs_by_id, stored, resumed=resumed)

        records = list(stored.records)
        successful = set(stored.successful_job_ids)
        failed = set(stored.failed_job_ids)
        interrupted = False
        try:
            for threads, hash_mb in _profile_blocks(self.spec):
                pending = [
                    job
                    for job in jobs
                    if job.threads == threads
                    and job.hash_mb == hash_mb
                    and job.job_id not in successful
                ]
                if not pending:
                    continue
                self.progress(
                    f"benchmark profile: Threads={threads} Hash={hash_mb} MiB"
                    f" ({len(pending)} pending)"
                )
                engine: Any | None = None
                try:
                    engine = self.engine_factory(
                        self.executable,
                        watchdog_seconds=self.spec.watchdog_seconds,
                    )
                    self._start_engine(engine)
                    warmup = StockfishProfile(
                        AnalysisQuality.TOOL,
                        200_000,
                        threads=threads,
                        hash_mb=hash_mb,
                        multipv=MULTI_PV,
                        configuration_version=CONFIGURATION_VERSION,
                    )
                    engine.analyze(self.spec.positions[0].canonical, warmup)
                except KeyboardInterrupt:
                    self._close_engine(engine)
                    interrupted = True
                    break
                except Exception as error:
                    self._close_engine(engine)
                    for job in pending:
                        record = self._failure_record(
                            job, len(_records_for_job(records, job.job_id)) + 1, error
                        )
                        self._persist_record(paths, record, records, successful, failed)
                        records.append(record)
                        failed.add(job.job_id)
                    continue

                try:
                    for job in pending:
                        if job.job_id in successful:
                            continue
                        attempt_number = len(_records_for_job(records, job.job_id)) + 1
                        started = time.perf_counter()
                        try:
                            analysis = engine.analyze(job.position.canonical, job.profile)
                        except KeyboardInterrupt:
                            interrupted = True
                            break
                        except Exception as error:
                            record = self._failure_record(job, attempt_number, error)
                        else:
                            elapsed = time.perf_counter() - started
                            record = _success_record(job, attempt_number, analysis, elapsed)
                        self._persist_record(paths, record, records, successful, failed)
                        records.append(record)
                        if record["status"] == "success":
                            successful.add(job.job_id)
                            failed.discard(job.job_id)
                        else:
                            failed.add(job.job_id)
                        self.progress(
                            f"benchmark {len(successful) + len(failed)}/{len(jobs)}: "
                            f"{job.job_id} {record['status']}"
                        )
                    if interrupted:
                        break
                finally:
                    self._close_engine(engine)
        except KeyboardInterrupt:
            interrupted = True
        finally:
            if interrupted:
                self._finish_artifacts(paths, tuple(records), jobs_by_id, interrupted=True)

        if interrupted:
            return BenchmarkOutcome(
                artifact_dir=paths.directory,
                total_jobs=len(jobs),
                successful_jobs=len(successful),
                failed_jobs=len(failed),
                attempts=len(records),
                complete=False,
                interrupted=True,
                resumed=resumed,
            )

        stored = _StoredAttempts(tuple(records), frozenset(successful), frozenset(failed))
        complete = len(successful) == len(jobs)
        self._finish_artifacts(
            paths, stored.records, jobs_by_id, interrupted=False, complete=complete
        )
        self.progress(
            f"benchmark {'complete' if complete else 'incomplete'}: "
            f"{len(successful)}/{len(jobs)} successful; artifacts={paths.directory}"
        )
        return _outcome(paths.directory, jobs_by_id, stored, resumed=resumed)

    def _artifact_paths(self) -> _ArtifactPaths:
        directory = _normalized_directory(self.output_dir)
        return _ArtifactPaths(
            directory=directory,
            manifest=directory / "manifest.json",
            attempts=directory / "attempts.jsonl",
            checkpoint=directory / "checkpoint.json",
            summary_json=directory / "summary.json",
            summary_csv=directory / "summary.csv",
            status=directory / "status.txt",
        )

    def _prepare_artifacts(self, paths: _ArtifactPaths, expected: dict[str, Any]) -> bool:
        artifact_files = (
            paths.attempts,
            paths.checkpoint,
            paths.summary_json,
            paths.summary_csv,
            paths.status,
        )
        if paths.manifest.exists():
            try:
                actual = json.loads(paths.manifest.read_text(encoding="utf-8"))
            except (OSError, ValueError) as error:
                raise BenchmarkCompatibilityError(
                    "existing benchmark manifest is unreadable"
                ) from error
            if actual != expected:
                raise BenchmarkCompatibilityError(
                    "existing benchmark manifest is incompatible with the requested inputs"
                )
            return True
        if any(path.exists() for path in artifact_files):
            raise BenchmarkCompatibilityError(
                "benchmark artifacts exist without a compatible manifest; refusing to mix state"
            )
        self._write_json(paths.manifest, expected)
        self._write_text(paths.attempts, "")
        self._write_text(paths.status, "INCOMPLETE\n")
        return False

    def _persist_record(
        self,
        paths: _ArtifactPaths,
        record: dict[str, Any],
        records: list[dict[str, Any]],
        successful: set[str],
        failed: set[str],
    ) -> None:
        self._append_jsonl(paths.attempts, record)
        prospective_successful = set(successful)
        prospective_failed = set(failed)
        if record["status"] == "success":
            prospective_successful.add(record["job_id"])
            prospective_failed.discard(record["job_id"])
        else:
            prospective_failed.add(record["job_id"])
        self._write_json(
            paths.checkpoint,
            _checkpoint_payload(
                records=(*records, record),
                successful=prospective_successful,
                failed=prospective_failed,
                total_jobs=self.spec.total_jobs,
                complete=False,
                interrupted=False,
            ),
        )

    def _finish_artifacts(
        self,
        paths: _ArtifactPaths,
        records: Sequence[dict[str, Any]],
        jobs_by_id: Mapping[str, BenchmarkJob],
        *,
        interrupted: bool,
        complete: bool | None = None,
    ) -> None:
        successful, failed = _current_job_sets(records)
        is_complete = len(successful) == len(jobs_by_id) if complete is None else complete
        self._write_json(
            paths.summary_json, _summary_payload(records, len(jobs_by_id), is_complete)
        )
        self._write_text(paths.summary_csv, _summary_csv(records))
        self._write_json(
            paths.checkpoint,
            _checkpoint_payload(
                records=records,
                successful=successful,
                failed=failed,
                total_jobs=len(jobs_by_id),
                complete=is_complete,
                interrupted=interrupted,
            ),
        )
        state = "COMPLETE" if is_complete else "INTERRUPTED" if interrupted else "INCOMPLETE"
        self._write_text(
            paths.status,
            f"{state}\n{len(successful)}/{len(jobs_by_id)} successful\n{paths.directory}\n",
        )

    def _write_json(self, path: Path, payload: Mapping[str, Any]) -> None:
        self._artifact_operation("JSON artifact", path, self.artifact_writer.write_json, payload)

    def _write_text(self, path: Path, content: str) -> None:
        self._artifact_operation("text artifact", path, self.artifact_writer.write_text, content)

    def _append_jsonl(self, path: Path, payload: Mapping[str, Any]) -> None:
        self._artifact_operation(
            "JSONL checkpoint", path, self.artifact_writer.append_jsonl, payload
        )

    def _artifact_operation(
        self, kind: str, path: Path, operation: Callable[..., None], *args: Any
    ) -> None:
        if not _is_within(path, self._artifact_paths().directory):
            raise BenchmarkPersistenceError(f"{kind} escaped the explicit output directory")
        last_error: OSError | None = None
        for attempt in range(self.artifact_write_retries + 1):
            try:
                operation(path, *args)
                return
            except OSError as error:
                last_error = error
                if (
                    not _is_transient_artifact_error(error)
                    or attempt >= self.artifact_write_retries
                ):
                    break
                if self.retry_delay_seconds:
                    time.sleep(self.retry_delay_seconds)
        detail = "" if last_error is None else f": {last_error}"
        raise BenchmarkPersistenceError(f"{kind} failed for {path.name}{detail}") from last_error

    @staticmethod
    def _start_engine(engine: Any) -> None:
        start = getattr(engine, "start", None)
        if callable(start):
            start()

    @staticmethod
    def _close_engine(engine: Any | None) -> None:
        if engine is None:
            return
        close = getattr(engine, "close", None)
        if callable(close):
            close()

    @staticmethod
    def _failure_record(job: BenchmarkJob, attempt: int, error: BaseException) -> dict[str, Any]:
        category = "engine"
        return {
            "record_type": "benchmark_attempt",
            "status": "failure",
            "job_id": job.job_id,
            "attempt": attempt,
            **_job_fields(job),
            "engine": {"name": STOCKFISH_NAME, "version": STOCKFISH_VERSION},
            "failure": {
                "category": category,
                "message": _bounded_message(error),
            },
        }


