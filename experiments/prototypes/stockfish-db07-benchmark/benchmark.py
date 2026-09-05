"""Isolated, checkpointed Stockfish benchmark experiment for DB-07.

This module deliberately has no dependency on the application.  The full runner is
configured by ``start.py``; ``smoke.py`` supplies a smaller, separate specification
for the authorized live proof.
"""

from __future__ import annotations

import csv
import ctypes
import hashlib
import json
import os
import platform
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable

import chess
import chess.engine


SCHEMA_VERSION = 1
KIND = "stockfish-db07-benchmark"
FULL_SEED = 20260905
MULTI_PV = 5
WARMUP_NODES = 200_000
ENGINE_STARTUP_TIMEOUT_SECONDS = 30.0
ENGINE_WATCHDOG_SECONDS = 120.0
NODE_BUDGETS = (100_000, 200_000, 400_000, 800_000, 1_600_000, 3_200_000, 6_400_000)
THREAD_VALUES = (1, 2, 4, 6)
HASH_VALUES_MB = (64, 256, 1_024)
ROUND_VALUES = (1, 2, 3)


class BenchmarkError(RuntimeError):
    """Base error for a safe benchmark stop."""


class ConfigurationError(BenchmarkError):
    """The requested run cannot safely use the existing state."""


class CheckpointError(BenchmarkError):
    """Checkpoint data is missing, malformed, or internally contradictory."""


class IncompleteRun(BenchmarkError):
    """A run finished its available work but has failed or unfinished jobs."""


class EngineWatchdogExpired(BenchmarkError):
    """A bounded engine operation exceeded its safety watchdog."""


@dataclass(frozen=True)
class Position:
    position_id: int
    fen: str


@dataclass(frozen=True)
class Profile:
    threads: int
    hash_mb: int

    def as_dict(self) -> dict[str, int]:
        return {"threads": self.threads, "hash_mb": self.hash_mb}


@dataclass(frozen=True)
class Job:
    round_number: int
    position_id: int
    nodes: int
    threads: int
    hash_mb: int

    @property
    def job_id(self) -> str:
        return (
            f"r{self.round_number}-p{self.position_id}-n{self.nodes}"
            f"-t{self.threads}-h{self.hash_mb}"
        )

    @property
    def profile(self) -> Profile:
        return Profile(self.threads, self.hash_mb)

    def as_dict(self) -> dict[str, int | str]:
        return {
            "job_id": self.job_id,
            "round": self.round_number,
            "position_id": self.position_id,
            "nodes": self.nodes,
            "threads": self.threads,
            "hash_mb": self.hash_mb,
        }


@dataclass(frozen=True)
class BenchmarkSpec:
    positions: tuple[Position, ...]
    node_budgets: tuple[int, ...]
    thread_values: tuple[int, ...]
    hash_values_mb: tuple[int, ...]
    rounds: tuple[int, ...]
    seed: int

    @property
    def profiles(self) -> tuple[Profile, ...]:
        return tuple(Profile(threads, hash_mb) for threads in self.thread_values for hash_mb in self.hash_values_mb)

    def ordered_jobs(self) -> tuple[Job, ...]:
        """Return the deterministic profile-block and in-block shuffle."""

        import random

        rng = random.Random(self.seed)
        blocks = list(self.profiles)
        rng.shuffle(blocks)
        jobs: list[Job] = []
        for profile in blocks:
            block = [
                Job(round_number, position.position_id, nodes, profile.threads, profile.hash_mb)
                for round_number in self.rounds
                for position in self.positions
                for nodes in self.node_budgets
            ]
            rng.shuffle(block)
            jobs.extend(block)
        return tuple(jobs)

    def profile_blocks(self) -> tuple[Profile, ...]:
        jobs = self.ordered_jobs()
        seen: list[Profile] = []
        for job in jobs:
            if job.profile not in seen:
                seen.append(job.profile)
        return tuple(seen)

    def matrix_dict(self) -> dict[str, Any]:
        return {
            "position_ids": [position.position_id for position in self.positions],
            "node_budgets": list(self.node_budgets),
            "thread_values": list(self.thread_values),
            "hash_values_mb": list(self.hash_values_mb),
            "rounds": list(self.rounds),
            "multipv": MULTI_PV,
            "warmup_nodes": WARMUP_NODES,
            "total_jobs": len(self.positions)
            * len(self.node_budgets)
            * len(self.thread_values)
            * len(self.hash_values_mb)
            * len(self.rounds),
        }


@dataclass(frozen=True)
class RunOutcome:
    artifact_dir: Path
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    unfinished_jobs: int
    interrupted: bool = False

    @property
    def complete(self) -> bool:
        return self.failed_jobs == 0 and self.unfinished_jobs == 0 and not self.interrupted

    @property
    def exit_code(self) -> int:
        return 0 if self.complete else (130 if self.interrupted else 1)


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_positions(path: Path) -> tuple[Position, ...]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Cannot read position input: {path}") from exc

    records = payload.get("positions") if isinstance(payload, dict) else None
    if not isinstance(records, list) or len(records) != 10:
        raise ConfigurationError("Position input must contain exactly ten positions")

    positions: list[Position] = []
    seen_ids: set[int] = set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), int):
            raise ConfigurationError("Every position must have an integer id")
        position_id = record["id"]
        fen = record.get("fen")
        if position_id in seen_ids or not isinstance(fen, str):
            raise ConfigurationError("Position ids must be unique and FENs must be strings")
        try:
            board = chess.Board(fen)
        except ValueError as exc:
            raise ConfigurationError(f"Invalid FEN for position {position_id}") from exc
        # python-chess marks an otherwise usable FEN with an unreachable
        # en-passant target as invalid.  The supplied position set preserves
        # that historical FEN field, so validate the board strictly after
        # disregarding only that non-position state.
        status = board.status()
        if status == chess.STATUS_INVALID_EP_SQUARE:
            board.ep_square = None
            status = board.status()
        if status != chess.STATUS_VALID or board.legal_moves.count() == 0:
            raise ConfigurationError(f"Invalid or immobile position {position_id}")
        seen_ids.add(position_id)
        positions.append(Position(position_id, fen))

    if sorted(seen_ids) != list(range(1, 11)):
        raise ConfigurationError("Position ids must be exactly 1 through 10")
    return tuple(positions)


def load_install_metadata(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Cannot read engine installation metadata: {path}") from exc
    required = ("binary_sha256", "reported_name", "version", "tag")
    if not isinstance(payload, dict) or any(key not in payload for key in required):
        raise ConfigurationError("Engine installation metadata is incomplete")
    return payload


def verify_engine_binary(engine_path: Path, install: dict[str, Any]) -> str:
    if not engine_path.is_file():
        raise ConfigurationError(f"Stockfish executable is missing: {engine_path}")
    actual = sha256_file(engine_path)
    if actual.lower() != str(install["binary_sha256"]).lower():
        raise ConfigurationError("Stockfish executable hash does not match install.json")
    return actual


def full_spec(positions: Iterable[Position]) -> BenchmarkSpec:
    return BenchmarkSpec(
        tuple(positions), NODE_BUDGETS, THREAD_VALUES, HASH_VALUES_MB, ROUND_VALUES, FULL_SEED
    )


def expected_manifest(
    spec: BenchmarkSpec,
    input_path: Path,
    engine_path: Path,
    install: dict[str, Any],
    input_sha256: str | None = None,
    engine_sha256: str | None = None,
) -> dict[str, Any]:
    jobs = spec.ordered_jobs()
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "created_at": utc_now(),
        "matrix": spec.matrix_dict(),
        "ordering": {
            "seed": spec.seed,
            "profile_blocks": [profile.as_dict() for profile in spec.profile_blocks()],
            "job_ids": [job.job_id for job in jobs],
        },
        "input": {
            "path": str(input_path),
            "sha256": input_sha256 or sha256_file(input_path),
            "position_ids": [position.position_id for position in spec.positions],
        },
        "engine": {
            "path": str(engine_path),
            "binary_sha256": engine_sha256 or str(install["binary_sha256"]),
            "reported_name": install["reported_name"],
            "version": install["version"],
            "tag": install["tag"],
        },
        "options": {
            "search_limit": "nodes",
            "multipv": MULTI_PV,
            "uci_show_wdl": True,
            "warmup_nodes": WARMUP_NODES,
            "clear_hash_before_measured": True,
            "engine_processes": "one per profile block, sequential",
        },
        "software": {
            "python": sys.version.split()[0],
            "python_chess": getattr(chess, "__version__", "unknown"),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
        },
        "dataset": {
            "state": "created",
            "total_jobs": len(jobs),
            "successful_jobs": 0,
            "failed_jobs": 0,
            "unfinished_jobs": len(jobs),
        },
    }


def _compatibility_view(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": manifest.get("schema_version"),
        "kind": manifest.get("kind"),
        "matrix": manifest.get("matrix"),
        "ordering": manifest.get("ordering"),
        "input": manifest.get("input"),
        "engine": manifest.get("engine"),
        "options": manifest.get("options"),
    }


def _atomic_write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


class ArtifactStore:
    """Append-only attempt storage plus atomic derived state files."""

    def __init__(self, artifact_dir: Path):
        self.artifact_dir = artifact_dir
        self.manifest_path = artifact_dir / "manifest.json"
        self.attempts_path = artifact_dir / "attempts.jsonl"
        self.status_path = artifact_dir / "status.txt"
        self.summary_json_path = artifact_dir / "summary.json"
        self.summary_csv_path = artifact_dir / "summary.csv"
        self.manifest: dict[str, Any] | None = None

    def prepare(self, expected: dict[str, Any]) -> dict[str, Any]:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        if self.manifest_path.exists():
            try:
                actual = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise CheckpointError("Benchmark manifest is unreadable") from exc
            if _compatibility_view(actual) != _compatibility_view(expected):
                raise ConfigurationError(
                    "Existing benchmark manifest is incompatible; refusing to mix evidence"
                )
            self.manifest = actual
            return actual

        unexpected = [
            path
            for path in (self.attempts_path, self.status_path, self.summary_json_path, self.summary_csv_path)
            if path.exists()
        ]
        if unexpected:
            raise CheckpointError("Artifact directory has state but no manifest")
        self.manifest = expected
        _atomic_write_json(self.manifest_path, expected)
        self.write_status(f"CREATED {self.artifact_dir}\n0/{expected['matrix']['total_jobs']} successful")
        return expected

    def _require_manifest(self) -> dict[str, Any]:
        if self.manifest is None:
            raise CheckpointError("Artifact store has not been prepared")
        return self.manifest

    def attempts(self) -> list[dict[str, Any]]:
        if not self.attempts_path.exists():
            return []
        records: list[dict[str, Any]] = []
        try:
            with self.attempts_path.open(encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if not isinstance(record, dict) or record.get("type") != "attempt":
                        raise CheckpointError(f"Invalid attempt record at line {line_number}")
                    records.append(record)
        except (OSError, json.JSONDecodeError) as exc:
            raise CheckpointError("Benchmark attempt checkpoint is unreadable") from exc
        return records

    def successful_records(self) -> dict[str, dict[str, Any]]:
        successful: dict[str, dict[str, Any]] = {}
        for record in self.attempts():
            if record.get("status") != "success":
                continue
            job_id = record.get("job_id")
            if not isinstance(job_id, str) or job_id in successful:
                raise CheckpointError("Duplicate successful job identity in checkpoint")
            successful[job_id] = record
        return successful

    def next_attempt_number(self, job_id: str) -> int:
        numbers = [
            int(record["attempt"])
            for record in self.attempts()
            if record.get("job_id") == job_id and isinstance(record.get("attempt"), int)
        ]
        return max(numbers, default=0) + 1

    def append_attempt(self, record: dict[str, Any]) -> None:
        self._require_manifest()
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        with self.attempts_path.open("a", encoding="utf-8", newline="") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def update_dataset(self, *, state: str, total: int, successful: int, failed: int) -> None:
        manifest = self._require_manifest()
        manifest["dataset"] = {
            "state": state,
            "total_jobs": total,
            "successful_jobs": successful,
            "failed_jobs": failed,
            "unfinished_jobs": total - successful - failed,
            "updated_at": utc_now(),
        }
        _atomic_write_json(self.manifest_path, manifest)

    def write_status(self, text: str) -> None:
        _atomic_write_text(self.status_path, text.rstrip() + "\n")


def _bounded_error(exc: BaseException) -> dict[str, str]:
    message = str(exc).replace("\x00", " ").strip()
    return {
        "category": type(exc).__name__,
        "message": message[:500],
        "process_outcome": "watchdog_terminated" if isinstance(exc, EngineWatchdogExpired) else "failed",
        "safe_retry_state": "retryable_on_next_invocation",
    }


def _call_with_watchdog(
    operation: Callable[[], Any], timeout_seconds: float, abort: Callable[[], None]
) -> Any:
    result: list[Any] = []
    error: list[BaseException] = []
    complete = threading.Event()

    def invoke() -> None:
        try:
            result.append(operation())
        except BaseException as exc:  # Propagate engine errors without losing their category.
            error.append(exc)
        finally:
            complete.set()

    worker = threading.Thread(target=invoke, daemon=True)
    worker.start()
    if not complete.wait(timeout_seconds):
        try:
            abort()
        finally:
            raise EngineWatchdogExpired(f"engine operation exceeded {timeout_seconds:g}s watchdog")
    if error:
        raise error[0]
    return result[0] if result else None


class KeepAwake:
    """Request only system sleep prevention for the current Windows thread."""

    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self) -> None:
        self._active = False

    def __enter__(self) -> KeepAwake:
        if os.name == "nt":
            result = ctypes.windll.kernel32.SetThreadExecutionState(
                self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED
            )
            if result == 0:
                raise BenchmarkError("Windows refused the temporary keep-awake request")
            self._active = True
        return self

    def __exit__(self, _exc_type: Any, _exc: Any, _traceback: Any) -> None:
        if self._active:
            ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
            self._active = False


class StockfishSession:
    """Small watchdog-backed wrapper around one real Stockfish process."""

    def __init__(self, engine_path: Path, watchdog_seconds: float = ENGINE_WATCHDOG_SECONDS):
        self._watchdog_seconds = watchdog_seconds
        self._engine = chess.engine.SimpleEngine.popen_uci(
            str(engine_path), timeout=ENGINE_STARTUP_TIMEOUT_SECONDS
        )
        self.identity = dict(self._engine.id)
        self._closed = False

    def configure(self, profile: Profile) -> None:
        self._call(
            lambda: self._engine.configure(
                {
                    "Threads": profile.threads,
                    "Hash": profile.hash_mb,
                    "UCI_ShowWDL": True,
                }
            )
        )

    def clear_hash(self) -> None:
        self._call(lambda: self._engine.configure({"Clear Hash": None}))

    def analyse(self, board: chess.Board, nodes: int, multipv: int) -> Any:
        return self._call(
            lambda: self._engine.analyse(
                board, chess.engine.Limit(nodes=nodes), multipv=multipv
            )
        )

    def _call(self, operation: Callable[[], Any]) -> Any:
        return _call_with_watchdog(operation, self._watchdog_seconds, self.close)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self._engine.close()


def _relative_score(score: Any, turn: chess.Color) -> Any:
    if score is None:
        return None
    if hasattr(score, "pov"):
        score = score.pov(turn)
    return getattr(score, "relative", score)


def normalize_score(score: Any, turn: chess.Color) -> dict[str, Any] | None:
    relative = _relative_score(score, turn)
    if relative is None:
        return None
    if hasattr(relative, "is_mate") and relative.is_mate():
        value = relative.mate()
        return {"kind": "mate", "value": int(value), "perspective": "side_to_move"}
    if hasattr(relative, "score"):
        value = relative.score(mate_score=None)
    else:
        value = relative
    if value is None:
        return None
    return {"kind": "cp", "value": int(value), "perspective": "side_to_move"}


def normalize_wdl(wdl: Any, turn: chess.Color) -> dict[str, Any] | None:
    if wdl is None:
        return None
    relative = _relative_score(wdl, turn)
    if relative is None:
        return None
    if hasattr(relative, "wins"):
        wins, draws, losses = relative.wins, relative.draws, relative.losses
    elif isinstance(relative, (tuple, list)) and len(relative) == 3:
        wins, draws, losses = relative
    else:
        return None
    return {
        "wins": int(wins),
        "draws": int(draws),
        "losses": int(losses),
        "perspective": "side_to_move",
    }


def _pv_uci(pv: Any) -> list[str]:
    if pv is None:
        return []
    moves: list[str] = []
    for move in pv:
        moves.append(move.uci() if hasattr(move, "uci") else str(move))
    return moves


def normalize_analysis(
    board: chess.Board,
    infos: Any,
    job: Job,
    attempt: int,
    wall_clock_seconds: float,
) -> dict[str, Any]:
    info_list = infos if isinstance(infos, list) else [infos]
    info_list = [info for info in info_list if isinstance(info, dict)]
    info_list.sort(key=lambda info: int(info.get("multipv", 0) or 0))
    expected_lines = min(MULTI_PV, board.legal_moves.count())
    if len(info_list) < expected_lines:
        raise BenchmarkError(
            f"Stockfish returned {len(info_list)} lines; expected at least {expected_lines}"
        )

    lines: list[dict[str, Any]] = []
    for index, info in enumerate(info_list[:MULTI_PV], start=1):
        lines.append(
            {
                "rank": int(info.get("multipv", index) or index),
                "score": normalize_score(info.get("score"), board.turn),
                "wdl": normalize_wdl(info.get("wdl"), board.turn),
                "pv": _pv_uci(info.get("pv")),
            }
        )

    def integer(name: str) -> int | None:
        value = info_list[0].get(name)
        return int(value) if value is not None else None

    def number(name: str) -> float | None:
        value = info_list[0].get(name)
        return float(value) if value is not None else None

    return {
        "job": job.as_dict(),
        "attempt": attempt,
        "completed_at": utc_now(),
        "wall_clock_seconds": round(wall_clock_seconds, 6),
        "engine_reported": {
            "nodes": integer("nodes"),
            "nps": integer("nps"),
            "depth": integer("depth"),
            "seldepth": integer("seldepth"),
            "hashfull": integer("hashfull"),
            "time_seconds": number("time"),
        },
        "lines": lines,
    }


def _record_with_job(record: dict[str, Any], job: Job, attempt: int) -> dict[str, Any]:
    record.setdefault("type", "attempt")
    record.setdefault("job_id", job.job_id)
    record.setdefault("attempt", attempt)
    record.setdefault("recorded_at", utc_now())
    return record


def _write_summaries(store: ArtifactStore, total_jobs: int, status: str) -> None:
    attempts = store.attempts()
    successful = [record["result"] for record in attempts if record.get("status") == "success"]
    failed = [record for record in attempts if record.get("status") == "failure"]
    successful_ids = {result["job"]["job_id"] for result in successful}
    failed_job_ids = {
        record.get("job_id") for record in failed if record.get("job_id") not in successful_ids
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "generated_at": utc_now(),
        "status": status,
        "counts": {
            "total_jobs": total_jobs,
            "successful_jobs": len(successful),
            "failed_jobs": len(failed_job_ids),
            "failed_attempts": len(failed),
            "attempt_records": len(attempts),
            "unfinished_jobs": total_jobs - len(successful) - len(failed_job_ids),
        },
        "results": successful,
        "failures": [
            {
                "job_id": record.get("job_id"),
                "attempt": record.get("attempt"),
                "error": record.get("error"),
            }
            for record in failed
        ],
    }
    _atomic_write_json(store.summary_json_path, summary)

    rows: list[dict[str, Any]] = []
    for result in successful:
        job = result["job"]
        performance = result["engine_reported"]
        rows.append(
            {
                "job_id": job["job_id"],
                "round": job["round"],
                "position_id": job["position_id"],
                "nodes": job["nodes"],
                "threads": job["threads"],
                "hash_mb": job["hash_mb"],
                "attempt": result["attempt"],
                "wall_clock_seconds": result["wall_clock_seconds"],
                "engine_nodes": performance.get("nodes"),
                "engine_nps": performance.get("nps"),
                "depth": performance.get("depth"),
                "seldepth": performance.get("seldepth"),
                "hashfull": performance.get("hashfull"),
                "line_count": len(result["lines"]),
            }
        )
    fields = list(rows[0]) if rows else [
        "job_id",
        "round",
        "position_id",
        "nodes",
        "threads",
        "hash_mb",
        "attempt",
        "wall_clock_seconds",
        "engine_nodes",
        "engine_nps",
        "depth",
        "seldepth",
        "hashfull",
        "line_count",
    ]
    from io import StringIO

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    _atomic_write_text(store.summary_csv_path, output.getvalue())


class BenchmarkRunner:
    def __init__(
        self,
        spec: BenchmarkSpec,
        manifest: dict[str, Any],
        store: ArtifactStore,
        engine_factory: Callable[[Profile], Any],
        power_factory: Callable[[], Any] = KeepAwake,
        validate_engine_identity: bool = True,
    ):
        self.spec = spec
        self.manifest = manifest
        self.store = store
        self.engine_factory = engine_factory
        self.power_factory = power_factory
        self.validate_engine_identity = validate_engine_identity
        self.positions = {position.position_id: position for position in spec.positions}

    def _check_identity(self, session: Any) -> None:
        if not self.validate_engine_identity:
            return
        identity = getattr(session, "identity", {})
        name = str(identity.get("name", "")) if isinstance(identity, dict) else str(identity)
        expected = self.manifest["engine"]
        if expected["reported_name"].lower() not in name.lower() or str(expected["version"]) not in name:
            raise ConfigurationError(
                f"Engine identity {name!r} does not match {expected['reported_name']} {expected['version']}"
            )
        if self.manifest.get("runtime_engine") is None:
            self.manifest["runtime_engine"] = {"id": identity, "recorded_at": utc_now()}
            _atomic_write_json(self.store.manifest_path, self.manifest)

    def _record_failure(self, job: Job, exc: BaseException) -> None:
        attempt = self.store.next_attempt_number(job.job_id)
        self.store.append_attempt(
            _record_with_job(
                {
                    "status": "failure",
                    "error": _bounded_error(exc),
                },
                job,
                attempt,
            )
        )

    def _record_success(self, job: Job, result: dict[str, Any]) -> None:
        self.store.append_attempt(
            _record_with_job(
                {
                    "status": "success",
                    "result": result,
                },
                job,
                result["attempt"],
            )
        )

    def _counts(self, jobs: tuple[Job, ...]) -> tuple[dict[str, dict[str, Any]], int, int]:
        successful = self.store.successful_records()
        failed_ids = {
            record.get("job_id")
            for record in self.store.attempts()
            if record.get("status") == "failure" and record.get("job_id") not in successful
        }
        unfinished = len(jobs) - len(successful) - len(failed_ids)
        return successful, len(failed_ids), unfinished

    def run(self) -> RunOutcome:
        jobs = self.spec.ordered_jobs()
        self.store.prepare(self.manifest)
        successful, failed_jobs, unfinished = self._counts(jobs)
        if failed_jobs == 0 and unfinished == 0:
            _write_summaries(self.store, len(jobs), "complete")
            self.store.update_dataset(
                state="complete", total=len(jobs), successful=len(successful), failed=failed_jobs
            )
            self.store.write_status(
                f"COMPLETE {self.store.artifact_dir}\n{len(successful)}/{len(jobs)} successful"
            )
            return RunOutcome(self.store.artifact_dir, len(jobs), len(successful), 0, 0)

        interrupted = False
        attempted_this_invocation: set[str] = set()
        try:
            with self.power_factory():
                self.store.write_status(
                    f"RUNNING {self.store.artifact_dir}\n{len(successful)}/{len(jobs)} successful"
                )
                for profile in self.spec.profile_blocks():
                    pending = [
                        job
                        for job in jobs
                        if job.profile == profile and job.job_id not in successful
                    ]
                    if not pending:
                        continue

                    session = None
                    try:
                        session = self.engine_factory(profile)
                        self._check_identity(session)
                        session.configure(profile)
                        warmup_position = self.positions[self.spec.positions[0].position_id]
                        session.analyse(
                            chess.Board(warmup_position.fen), WARMUP_NODES, multipv=1
                        )
                        session.clear_hash()
                        for job in pending:
                            if job.job_id in successful:
                                continue
                            attempted_this_invocation.add(job.job_id)
                            board = chess.Board(self.positions[job.position_id].fen)
                            attempt = self.store.next_attempt_number(job.job_id)
                            started = time.perf_counter()
                            try:
                                session.clear_hash()
                                infos = session.analyse(board, job.nodes, multipv=MULTI_PV)
                                result = normalize_analysis(
                                    board,
                                    infos,
                                    job,
                                    attempt,
                                    time.perf_counter() - started,
                                )
                                self._record_success(job, result)
                                successful[job.job_id] = {
                                    "status": "success",
                                    "job_id": job.job_id,
                                    "attempt": attempt,
                                    "result": result,
                                }
                            except KeyboardInterrupt:
                                self._record_failure(job, KeyboardInterrupt("interrupted"))
                                raise
                            except Exception as exc:  # A failed job must not stop the matrix.
                                self._record_failure(job, exc)
                            finally:
                                current_failed = sum(
                                    1
                                    for record in self.store.attempts()
                                    if record.get("status") == "failure"
                                    and record.get("job_id") not in successful
                                )
                                self.store.update_dataset(
                                    state="running",
                                    total=len(jobs),
                                    successful=len(successful),
                                    failed=current_failed,
                                )
                    except KeyboardInterrupt:
                        interrupted = True
                        raise
                    except Exception as exc:
                        for job in pending:
                            if job.job_id not in successful and job.job_id not in attempted_this_invocation:
                                # Startup/configuration/warm-up failures apply to every job
                                # not already attempted in this invocation.  The unique job
                                # order means each receives one retryable record.
                                attempted_this_invocation.add(job.job_id)
                                self._record_failure(job, exc)
                    finally:
                        if session is not None:
                            try:
                                session.close()
                            except Exception:
                                pass
        except KeyboardInterrupt:
            interrupted = True
        finally:
            successful, failed_jobs, unfinished = self._counts(jobs)
            state = "complete" if unfinished == 0 and failed_jobs == 0 and not interrupted else "incomplete"
            _write_summaries(self.store, len(jobs), state)
            self.store.update_dataset(
                state=state,
                total=len(jobs),
                successful=len(successful),
                failed=failed_jobs,
            )
            self.store.write_status(
                f"{state.upper()} {self.store.artifact_dir}\n"
                f"{len(successful)}/{len(jobs)} successful; "
                f"{failed_jobs} failed jobs; {unfinished} unfinished"
            )

        return RunOutcome(
            self.store.artifact_dir,
            len(jobs),
            len(successful),
            failed_jobs,
            unfinished,
            interrupted,
        )


def build_runner(
    spec: BenchmarkSpec,
    manifest: dict[str, Any],
    artifact_dir: Path,
    engine_path: Path,
    *,
    engine_factory: Callable[[Profile], Any] | None = None,
    power_factory: Callable[[], Any] = KeepAwake,
    validate_engine_identity: bool = True,
) -> BenchmarkRunner:
    store = ArtifactStore(artifact_dir)
    if engine_factory is None:
        engine_factory = lambda _profile: StockfishSession(engine_path)
    return BenchmarkRunner(
        spec,
        manifest,
        store,
        engine_factory,
        power_factory,
        validate_engine_identity,
    )
