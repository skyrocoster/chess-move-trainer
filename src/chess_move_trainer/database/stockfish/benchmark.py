"""A resumable, output-contained Stockfish benchmark service.

This module owns only benchmark preparation and evidence persistence.  It does
not select a node-budget winner, publish database analysis, or coordinate the
live analysis queue.
"""

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
DEFAULT_NODE_BUDGETS: Final[tuple[int, ...]] = (
    100_000,
    200_000,
    400_000,
    800_000,
    1_600_000,
    3_200_000,
    6_400_000,
)
DEFAULT_THREAD_COUNTS: Final[tuple[int, ...]] = (1, 2, 4, 6)
DEFAULT_HASH_SIZES_MB: Final[tuple[int, ...]] = (64, 256, 1024)
DEFAULT_REPETITIONS: Final[int] = 3
DEFAULT_SHUFFLE_SEED: Final[int] = 0
DEFAULT_ARTIFACT_WRITE_RETRIES: Final[int] = 3
_MAX_DIAGNOSTIC_LENGTH: Final[int] = 500


class BenchmarkError(RuntimeError):
    """Base class for bounded benchmark setup and execution failures."""


class BenchmarkInputError(BenchmarkError, ValueError):
    """The explicit input or matrix specification is invalid."""


class BenchmarkCompatibilityError(BenchmarkError):
    """Existing output state does not belong to the requested benchmark."""


class BenchmarkPersistenceError(BenchmarkError):
    """An artifact could not be persisted safely after bounded retries."""

    exit_code = 1


class BenchmarkInterrupted(BenchmarkError):
    """Reserved internal category for a controlled benchmark interruption."""

    exit_code = 130


@dataclass(frozen=True, slots=True)
class BenchmarkPosition:
    """One validated position from the explicit benchmark input file."""

    position_id: int
    fen: str

    def __post_init__(self) -> None:
        if type(self.position_id) is not int or self.position_id < 1:
            raise BenchmarkInputError("benchmark position id must be a positive integer")
        if not isinstance(self.fen, str):
            raise BenchmarkInputError("benchmark position FEN must be a string")
        try:
            canonicalize_fen(self.fen)
        except ValueError as error:
            raise BenchmarkInputError(
                f"benchmark position {self.position_id} has an invalid FEN"
            ) from error

    @property
    def canonical(self) -> CanonicalPosition:
        """Return the canonical four-field position consumed by the engine."""

        return canonicalize_fen(self.fen)


@dataclass(frozen=True, slots=True)
class BenchmarkJob:
    """A stable identity for one position/profile/round analysis."""

    position: BenchmarkPosition
    nodes: int
    threads: int
    hash_mb: int
    round_number: int

    @property
    def job_id(self) -> str:
        return (
            f"r{self.round_number}-p{self.position.position_id}-"
            f"n{self.nodes}-t{self.threads}-h{self.hash_mb}"
        )

    @property
    def profile(self) -> StockfishProfile:
        return StockfishProfile(
            AnalysisQuality.TOOL,
            self.nodes,
            threads=self.threads,
            hash_mb=self.hash_mb,
            multipv=MULTI_PV,
            configuration_version=CONFIGURATION_VERSION,
        )


@dataclass(frozen=True, slots=True)
class BenchmarkSpec:
    """Validated, deterministic matrix inputs for one benchmark run."""

    positions: tuple[BenchmarkPosition, ...]
    node_budgets: tuple[int, ...] = DEFAULT_NODE_BUDGETS
    thread_counts: tuple[int, ...] = DEFAULT_THREAD_COUNTS
    hash_sizes_mb: tuple[int, ...] = DEFAULT_HASH_SIZES_MB
    repetitions: int = DEFAULT_REPETITIONS
    shuffle_seed: int = DEFAULT_SHUFFLE_SEED
    multipv: int = MULTI_PV
    watchdog_seconds: float = ANALYSIS_WATCHDOG_SECONDS

    def __post_init__(self) -> None:
        positions = tuple(self.positions)
        if not positions:
            raise BenchmarkInputError("benchmark input must contain at least one position")
        if any(not isinstance(position, BenchmarkPosition) for position in positions):
            raise BenchmarkInputError("benchmark positions must be validated BenchmarkPosition values")
        if len({position.position_id for position in positions}) != len(positions):
            raise BenchmarkInputError("benchmark position ids must be unique")
        object.__setattr__(self, "positions", tuple(sorted(positions, key=lambda item: item.position_id)))
        for field_name in ("node_budgets", "thread_counts", "hash_sizes_mb"):
            values = _positive_int_tuple(getattr(self, field_name), field_name)
            object.__setattr__(self, field_name, values)
        if type(self.repetitions) is not int or self.repetitions < 1:
            raise BenchmarkInputError("repetitions must be a positive integer")
        if type(self.shuffle_seed) is not int:
            raise BenchmarkInputError("shuffle seed must be an integer")
        if self.multipv != MULTI_PV:
            raise BenchmarkInputError("MultiPV is fixed at 5 for the supported benchmark")
        if isinstance(self.watchdog_seconds, bool):
            raise BenchmarkInputError("watchdog must be finite and greater than zero")
        try:
            watchdog = float(self.watchdog_seconds)
        except (TypeError, ValueError) as error:
            raise BenchmarkInputError("watchdog must be finite and greater than zero") from error
        if not (0 < watchdog < float("inf")):
            raise BenchmarkInputError("watchdog must be finite and greater than zero")
        object.__setattr__(self, "watchdog_seconds", watchdog)

    @property
    def total_jobs(self) -> int:
        return (
            len(self.positions)
            * len(self.node_budgets)
            * len(self.thread_counts)
            * len(self.hash_sizes_mb)
            * self.repetitions
        )

    def jobs(self) -> tuple[BenchmarkJob, ...]:
        """Enumerate every job once in the recorded deterministic order."""

        rng = random.Random(self.shuffle_seed)
        blocks = [(threads, hash_mb) for threads in self.thread_counts for hash_mb in self.hash_sizes_mb]
        rng.shuffle(blocks)
        ordered: list[BenchmarkJob] = []
        for threads, hash_mb in blocks:
            block_jobs = [
                BenchmarkJob(position, nodes, threads, hash_mb, round_number)
                for round_number in range(1, self.repetitions + 1)
                for nodes in self.node_budgets
                for position in self.positions
            ]
            rng.shuffle(block_jobs)
            ordered.extend(block_jobs)
        return tuple(ordered)

    def as_manifest_dict(self) -> dict[str, Any]:
        return {
            "format_version": BENCHMARK_FORMAT_VERSION,
            "matrix": {
                "node_budgets": list(self.node_budgets),
                "thread_counts": list(self.thread_counts),
                "hash_sizes_mb": list(self.hash_sizes_mb),
                "repetitions": self.repetitions,
                "shuffle_seed": self.shuffle_seed,
                "multipv": self.multipv,
                "watchdog_seconds": self.watchdog_seconds,
            },
            "positions": [
                {"position_id": position.position_id, "fen": position.fen}
                for position in self.positions
            ],
            "total_jobs": self.total_jobs,
        }


BenchmarkSpecification = BenchmarkSpec


@dataclass(frozen=True, slots=True)
class BenchmarkOutcome:
    """Observable result of one bounded benchmark invocation."""

    artifact_dir: Path
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    attempts: int
    complete: bool
    interrupted: bool = False
    resumed: bool = False

    @property
    def exit_code(self) -> int:
        if self.interrupted:
            return 130
        return 0 if self.complete else 1


class ArtifactWriter(Protocol):
    """The small persistence seam used by the runner and focused tests."""

    def write_json(self, path: Path, payload: Mapping[str, Any]) -> None: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def append_jsonl(self, path: Path, payload: Mapping[str, Any]) -> None: ...


class AtomicArtifactWriter:
    """Write benchmark artifacts atomically, keeping temporary files local."""

    def write_json(self, path: Path, payload: Mapping[str, Any]) -> None:
        self.write_text(
            path,
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n",
        )

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, path)
        except BaseException:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except OSError:
                    pass
            raise

    def append_jsonl(self, path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = (
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        starting_size: int | None = None
        try:
            with path.open("ab") as stream:
                starting_size = stream.tell()
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            if starting_size is not None:
                try:
                    with path.open("r+b") as stream:
                        stream.truncate(starting_size)
                except OSError:
                    pass
            raise


@dataclass(frozen=True, slots=True)
class _ArtifactPaths:
    directory: Path
    manifest: Path
    attempts: Path
    checkpoint: Path
    summary_json: Path
    summary_csv: Path
    status: Path


@dataclass(frozen=True, slots=True)
class _StoredAttempts:
    records: tuple[dict[str, Any], ...]
    successful_job_ids: frozenset[str]
    failed_job_ids: frozenset[str]


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
            raise BenchmarkInputError("artifact retry delay must be finite and non-negative") from error
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
                self.progress(f"benchmark profile: Threads={threads} Hash={hash_mb} MiB ({len(pending)} pending)")
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
                        record = self._failure_record(job, len(_records_for_job(records, job.job_id)) + 1, error)
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
        self._finish_artifacts(paths, stored.records, jobs_by_id, interrupted=False, complete=complete)
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
                raise BenchmarkCompatibilityError("existing benchmark manifest is unreadable") from error
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
        self._write_json(paths.summary_json, _summary_payload(records, len(jobs_by_id), is_complete))
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
        self._artifact_operation("JSONL checkpoint", path, self.artifact_writer.append_jsonl, payload)

    def _artifact_operation(self, kind: str, path: Path, operation: Callable[..., None], *args: Any) -> None:
        if not _is_within(path, self._artifact_paths().directory):
            raise BenchmarkPersistenceError(f"{kind} escaped the explicit output directory")
        last_error: OSError | None = None
        for attempt in range(self.artifact_write_retries + 1):
            try:
                operation(path, *args)
                return
            except OSError as error:
                last_error = error
                if not _is_transient_artifact_error(error) or attempt >= self.artifact_write_retries:
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


def load_positions(position_input: str | Path) -> tuple[BenchmarkPosition, ...]:
    """Load and structurally validate explicit JSON benchmark positions."""

    path = Path(position_input)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise BenchmarkInputError(f"could not read benchmark position input: {path}") from error
    if not isinstance(payload, Mapping) or not isinstance(payload.get("positions"), list):
        raise BenchmarkInputError("benchmark position input must contain a positions list")
    positions: list[BenchmarkPosition] = []
    for item in payload["positions"]:
        if not isinstance(item, Mapping) or "id" not in item or "fen" not in item:
            raise BenchmarkInputError("each benchmark position needs id and fen")
        positions.append(BenchmarkPosition(position_id=item["id"], fen=item["fen"]))
    return tuple(sorted(positions, key=lambda position: position.position_id))


def run_benchmark(
    *,
    executable: str | Path,
    position_input: str | Path,
    output_dir: str | Path,
    node_budgets: Iterable[int] = DEFAULT_NODE_BUDGETS,
    thread_counts: Iterable[int] = DEFAULT_THREAD_COUNTS,
    hash_sizes_mb: Iterable[int] = DEFAULT_HASH_SIZES_MB,
    repetitions: int = DEFAULT_REPETITIONS,
    shuffle_seed: int = DEFAULT_SHUFFLE_SEED,
    watchdog_seconds: float = ANALYSIS_WATCHDOG_SECONDS,
    engine_factory: Callable[..., Any] | None = None,
    artifact_writer: ArtifactWriter | None = None,
    artifact_write_retries: int = DEFAULT_ARTIFACT_WRITE_RETRIES,
    retry_delay_seconds: float = 0.0,
    progress: Callable[[str], None] | None = None,
) -> BenchmarkOutcome:
    """Run one explicit matrix, resuming only compatible output state."""

    positions = load_positions(position_input)
    spec = BenchmarkSpec(
        positions=positions,
        node_budgets=tuple(node_budgets),
        thread_counts=tuple(thread_counts),
        hash_sizes_mb=tuple(hash_sizes_mb),
        repetitions=repetitions,
        shuffle_seed=shuffle_seed,
        watchdog_seconds=watchdog_seconds,
    )
    return BenchmarkRunner(
        spec,
        executable=executable,
        position_input=position_input,
        output_dir=output_dir,
        engine_factory=engine_factory,
        artifact_writer=artifact_writer,
        artifact_write_retries=artifact_write_retries,
        retry_delay_seconds=retry_delay_seconds,
        progress=progress,
    ).run()


def _expected_manifest(spec: BenchmarkSpec, executable: Path, position_input: Path) -> dict[str, Any]:
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
    blocks = [(threads, hash_mb) for threads in spec.thread_counts for hash_mb in spec.hash_sizes_mb]
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


def _success_record(job: BenchmarkJob, attempt: int, analysis: Any, elapsed: float) -> dict[str, Any]:
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
        raise BenchmarkCompatibilityError("existing benchmark checkpoint is unreadable") from error
    if not isinstance(payload, Mapping) or payload.get("format_version") != BENCHMARK_FORMAT_VERSION:
        raise BenchmarkCompatibilityError("existing benchmark checkpoint has an incompatible format")
    successful = frozenset(payload.get("successful_job_ids", ()))
    failed = frozenset(payload.get("failed_job_ids", ()))
    if not successful <= jobs_by_id.keys() or not failed <= jobs_by_id.keys():
        raise BenchmarkCompatibilityError("existing benchmark checkpoint contains unknown jobs")
    if successful != stored.successful_job_ids or not failed <= stored.failed_job_ids:
        raise BenchmarkCompatibilityError("existing benchmark checkpoint disagrees with attempts")


def _records_for_job(records: Sequence[Mapping[str, Any]], job_id: str) -> tuple[Mapping[str, Any], ...]:
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


def _positive_int_tuple(values: Iterable[int], label: str) -> tuple[int, ...]:
    normalized = tuple(values)
    if not normalized or any(type(value) is not int or value <= 0 for value in normalized):
        raise BenchmarkInputError(f"{label} must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise BenchmarkInputError(f"{label} must not contain duplicates")
    return normalized


def _normalized_directory(path: Path) -> Path:
    try:
        return path.expanduser().resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise BenchmarkInputError("output directory could not be normalized") from error


def _normalized_file_path(path: Path) -> Path:
    try:
        return path.expanduser().resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise BenchmarkInputError(f"path could not be normalized: {path}") from error


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(directory.resolve(strict=False))
    except ValueError:
        return False
    return True


def _sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    if not path.is_file():
        raise BenchmarkInputError(f"explicit input path is not a file: {path}")
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise BenchmarkInputError(f"could not read explicit input path: {path}") from error
    return digest.hexdigest()


def _is_transient_artifact_error(error: OSError) -> bool:
    if isinstance(error, PermissionError):
        return True
    return getattr(error, "winerror", None) in {5, 32, 33}


def _bounded_message(error: BaseException) -> str:
    message = str(error).replace("\r", " ").replace("\n", " ").strip()
    return message[:_MAX_DIAGNOSTIC_LENGTH] or error.__class__.__name__


__all__ = [
    "ArtifactWriter",
    "AtomicArtifactWriter",
    "BENCHMARK_FORMAT_VERSION",
    "BenchmarkCompatibilityError",
    "BenchmarkError",
    "BenchmarkInputError",
    "BenchmarkInterrupted",
    "BenchmarkJob",
    "BenchmarkOutcome",
    "BenchmarkPersistenceError",
    "BenchmarkPosition",
    "BenchmarkRunner",
    "BenchmarkSpec",
    "BenchmarkSpecification",
    "DEFAULT_ARTIFACT_WRITE_RETRIES",
    "DEFAULT_HASH_SIZES_MB",
    "DEFAULT_NODE_BUDGETS",
    "DEFAULT_REPETITIONS",
    "DEFAULT_SHUFFLE_SEED",
    "DEFAULT_THREAD_COUNTS",
    "load_positions",
    "run_benchmark",
]
