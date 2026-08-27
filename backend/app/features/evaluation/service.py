"""Bounded five-worker evaluation service over the durable queue and MP-09 storage."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

import chess

from backend.app.features.analysis import (
    AnalysisBusyError,
    AnalysisCandidate,
    AnalysisLockError,
    AnalysisProfile,
    AnalysisRepository,
    AnalysisResult,
    AnalysisRunLock,
    AnalysisValidationError,
    ResultEligibility,
    canonical_fen,
    position_key_from_fen,
)
from backend.app.features.analysis.runner import AnalysisEngine
from backend.app.features.analysis.schema import require_analysis_schema

from .errors import EvaluationQueueError, EvaluationValidationError
from .models import EvaluationQueueItem, InspectResult, RequestResult, SessionResult
from .queue import (
    MAX_FEN_LENGTH,
    claim_next,
    complete,
    enqueue,
    fail,
    observe,
    pending_count,
    requeue_running,
)
from .schema import require_evaluation_schema

QUALIFIED_PROFILE_ID = "mp09-balanced-nodes-v2-200000"
EVALUATION_WORKERS = 5
MAX_WORKERS = 5
ACTIONS = ("analyze", "update", "retry")

EngineFactory = Callable[[], AnalysisEngine]


class _WorkerFailure(Exception):
    """A worker item failed permanently; no automatic retry is performed."""

    def __init__(self, error_code: str, details: str) -> None:
        super().__init__(f"{error_code}: {details}")
        self.error_code = error_code
        self.details = details


def _worker_error_code(error: BaseException) -> str:
    name = type(error).__name__.lower()
    if "timeout" in name:
        return "timeout"
    if "lifecycle" in name:
        return "engine_lifecycle"
    if "validation" in name:
        return "invalid_result"
    return "engine_failure"


class _EngineRegistry:
    """One engine per worker thread; workers never receive the SQLite connection."""

    def __init__(self, factory: EngineFactory) -> None:
        self._factory = factory
        self._local = threading.local()
        self._guard = threading.Lock()
        self._engines: dict[int, AnalysisEngine] = {}

    def current(self) -> AnalysisEngine:
        engine = getattr(self._local, "engine", None)
        if engine is None:
            engine = self._factory()
            thread_id = threading.get_ident()
            with self._guard:
                self._engines[thread_id] = engine
            self._local.engine = engine
        return engine

    def discard_current(self) -> None:
        engine = getattr(self._local, "engine", None)
        if engine is None:
            return
        self._local.engine = None
        with self._guard:
            self._engines.pop(threading.get_ident(), None)
        _close_engine(engine, force=True)

    def close_all(self) -> None:
        with self._guard:
            engines = tuple(self._engines.values())
        for engine in engines:
            _close_engine(engine, force=False)


def _close_engine(engine: AnalysisEngine, *, force: bool) -> None:
    if force:
        if hasattr(engine, "force_terminate"):
            getattr(engine, "force_terminate")()
            return
        if hasattr(engine, "terminate"):
            getattr(engine, "terminate")()
            return
        raise RuntimeError("tracked evaluation engine has no forced-termination boundary")
    engine.close()


def _canonical(fen: object) -> str:
    if not isinstance(fen, str) or len(fen) > 128:
        raise EvaluationValidationError(
            f"FEN must be a string no longer than {MAX_FEN_LENGTH} characters"
        )
    try:
        return canonical_fen(fen)
    except AnalysisValidationError as error:
        raise EvaluationValidationError(str(error)) from error


def read_result(
    connection: sqlite3.Connection, fen: str, profile: AnalysisProfile
) -> AnalysisResult | None:
    """Read and fully validate a persisted result; never computes."""

    require_analysis_schema(connection)
    selected = _canonical(fen)
    position_key = position_key_from_fen(selected)
    row = connection.execute(
        "SELECT schema_version, profile_id, settings_json, settings_fingerprint, "
        "engine_binary_sha256, engine_name, engine_version, terminal_kind, candidate_count, "
        "completed_at, wall_time_ms FROM analysis_result WHERE position_key = ?",
        (position_key,),
    ).fetchone()
    if row is None:
        return None
    candidate_rows = connection.execute(
        "SELECT rank, score_kind, score_value, wdl_wins, wdl_draws, wdl_losses, "
        "pv_uci_json, depth, seldepth, nodes, engine_time_ms "
        "FROM analysis_candidate WHERE position_key = ? ORDER BY rank",
        (position_key,),
    ).fetchall()
    candidates = tuple(
        AnalysisCandidate(
            rank=int(candidate[0]),
            score_kind=str(candidate[1]),
            score_value=int(candidate[2]),
            wdl_wins=int(candidate[3]),
            wdl_draws=int(candidate[4]),
            wdl_losses=int(candidate[5]),
            pv_uci=tuple(json.loads(candidate[6])),
            depth=int(candidate[7]),
            seldepth=int(candidate[8]),
            nodes=int(candidate[9]),
            engine_time_ms=int(candidate[10]),
        )
        for candidate in candidate_rows
    )
    return AnalysisResult(
        fen=selected,
        profile=profile,
        candidates=candidates,
        terminal_kind=None if row[7] is None else str(row[7]),
        completed_at=str(row[9]),
        wall_time_ms=int(row[10]),
    )


def inspect(connection: sqlite3.Connection, fen: object, profile: AnalysisProfile) -> InspectResult:
    """Return eligibility, persisted result, and queue state without computing."""

    require_evaluation_schema(connection)
    selected = _canonical(fen)
    eligibility = AnalysisRepository(connection).eligibility(selected, profile)
    result = None
    if eligibility in (ResultEligibility.ELIGIBLE, ResultEligibility.STALE):
        result = read_result(connection, selected, profile)
    item = observe(connection, selected)
    terminal = chess.Board(selected).outcome(claim_draw=True) is not None
    return InspectResult(
        fen=selected,
        eligibility=eligibility,
        result=result,
        item=item,
        terminal=terminal,
    )


def request(
    connection: sqlite3.Connection,
    fen: object,
    profile: AnalysisProfile,
    action: str,
) -> RequestResult:
    """Perform one deliberate Analyze, Update, or Retry action."""

    require_evaluation_schema(connection)
    if action not in ACTIONS:
        raise EvaluationValidationError(f"action must be one of {', '.join(ACTIONS)}")
    selected = _canonical(fen)
    item = observe(connection, selected)
    state = item.state if item is not None else None
    if action == "analyze":
        if item is not None and state != "failed":
            raise EvaluationQueueError(
                "position is already queued, running, or done; use update or retry"
            )
    elif action == "update":
        if item is None or state != "done":
            raise EvaluationQueueError("nothing to update; analyze or retry first")
    else:  # retry
        if item is None or state != "failed":
            raise EvaluationQueueError("nothing to retry; analyze or update first")
    outcome, item = enqueue(connection, selected)
    eligibility = AnalysisRepository(connection).eligibility(selected, profile)
    return RequestResult(
        fen=selected,
        outcome=outcome,
        eligibility=eligibility,
        item=item,
    )


def _evaluate_one(
    item: EvaluationQueueItem, profile: AnalysisProfile, registry: _EngineRegistry
) -> AnalysisResult:
    fen = item.fen
    board = chess.Board(fen)
    outcome = board.outcome(claim_draw=True)
    if outcome is not None:
        return AnalysisResult(
            fen=fen,
            profile=profile,
            candidates=(),
            terminal_kind=outcome.termination.name.lower(),
            completed_at=datetime.now(UTC).isoformat(),
            wall_time_ms=0,
        )
    try:
        result = registry.current().analyse(fen)
    except Exception as error:
        registry.discard_current()
        raise _WorkerFailure(_worker_error_code(error), str(error)[:500]) from error
    if result.position_key != item.position_key:
        registry.discard_current()
        raise _WorkerFailure(
            "invalid_result", "engine returned a result for a different PositionKey"
        )
    if result.profile.fingerprint != profile.fingerprint:
        registry.discard_current()
        raise _WorkerFailure(
            "invalid_result", "engine result profile does not match the active profile"
        )
    return result


def _persist_with_busy_retry(repository: AnalysisRepository, result: AnalysisResult) -> None:
    for attempt in range(3):
        try:
            repository.publish(result)
            return
        except AnalysisBusyError:
            if attempt == 2:
                raise
            time.sleep(0.02 * (attempt + 1))


def _drain(
    connection: sqlite3.Connection,
    profile: AnalysisProfile,
    engine_factory: EngineFactory,
    workers: int,
    requeued: int,
) -> SessionResult:
    registry = _EngineRegistry(engine_factory)
    inflight: dict[Future[AnalysisResult], EvaluationQueueItem] = {}
    completed = 0
    failed = 0
    executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="mp10-eval")

    def dispatch() -> None:
        while len(inflight) < workers:
            item = claim_next(connection)
            if item is None:
                return
            future = executor.submit(_evaluate_one, item, profile, registry)
            inflight[future] = item

    try:
        dispatch()
        while inflight:
            done, _ = wait(tuple(inflight), return_when=FIRST_COMPLETED)
            for future in done:
                item = inflight.pop(future)
                try:
                    result = future.result()
                    _persist_with_busy_retry(AnalysisRepository(connection), result)
                    complete(connection, item.fen, result.fen)
                    completed += 1
                except _WorkerFailure as error:
                    failed += 1
                    fail(connection, item.fen, error.error_code, error.details)
                except Exception as error:
                    failed += 1
                    fail(connection, item.fen, "persistence_failure", str(error)[:2000])
            dispatch()
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
        registry.close_all()

    queued, running = pending_count(connection)
    return SessionResult(
        completed=completed,
        failed=failed,
        requeued=requeued,
        left_queued=queued + running,
    )


def run_session(
    database: Path,
    profile: AnalysisProfile,
    engine_factory: EngineFactory,
    *,
    workers: int = EVALUATION_WORKERS,
    lock_path: Path | None = None,
) -> SessionResult:
    """Own the shared analysis lock, requeue interrupted work, then drain the queue.

    The corpus-fill holds the same top-level lock; if it is active, AnalysisLockError
    is raised and nothing is written.
    """

    if not 1 <= workers <= MAX_WORKERS:
        raise ValueError(f"workers must be between 1 and {MAX_WORKERS}")
    if profile.profile_id != QUALIFIED_PROFILE_ID:
        raise EvaluationValidationError("the evaluation service uses the fixed MP-09 profile only")
    database_path = Path(database)
    if not database_path.is_file():
        raise AnalysisLockError(f"database does not exist: {database_path}")
    with AnalysisRunLock(database_path, lock_path):
        connection = sqlite3.connect(database_path, timeout=0)
        try:
            require_evaluation_schema(connection)
            require_analysis_schema(connection)
            requeued = requeue_running(connection)
            return _drain(connection, profile, engine_factory, workers, requeued)
        finally:
            connection.close()
