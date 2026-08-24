"""Bounded selected-game orchestration with coordinator-only SQLite writes."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from collections.abc import Callable, Sequence
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from .errors import AnalysisBusyError, AnalysisLockError, EngineLifecycleError
from .locking import AnalysisRunLock
from .models import AnalysisProfile, AnalysisResult
from .repository import AnalysisRepository, FinalPositionFailure
from .selection import (
    SelectedPosition,
    SelectionReport,
    select_all_positions,
    select_positions,
    work_positions,
)

MAX_WORKERS = 6
DEFAULT_WORKERS = 1
MAX_ATTEMPTS = 2
MAX_CONSECUTIVE_FAILURES = 3


class AnalysisEngine(Protocol):
    def analyse(self, fen: str) -> AnalysisResult: ...

    def close(self) -> None: ...


EngineFactory = Callable[[], AnalysisEngine]


class InterruptController:
    """Convert the first two SIGINT events into bounded drain and force levels."""

    def __init__(self) -> None:
        self.stop_dispatch = threading.Event()
        self.hard_stop = threading.Event()
        self._count = 0
        self._guard = threading.Lock()
        self._force_callback: Callable[[], None] | None = None

    def bind_force_callback(self, callback: Callable[[], None]) -> None:
        with self._guard:
            self._force_callback = callback
            already_hard = self.hard_stop.is_set()
        if already_hard:
            callback()

    def request_interrupt(self) -> int:
        with self._guard:
            self._count += 1
            level = self._count
            callback = self._force_callback
        if level == 1:
            self.stop_dispatch.set()
        else:
            self.stop_dispatch.set()
            self.hard_stop.set()
            if callback:
                callback()
        return level


@dataclass(frozen=True)
class BatchRunResult:
    run_id: int
    status: str
    report: SelectionReport
    completed_positions: int
    failures: tuple[FinalPositionFailure, ...]
    circuit_breaker_tripped: bool


class _ForcedInterruption(RuntimeError):
    pass


@dataclass(frozen=True)
class _WorkerFailure(Exception):
    attempts: int
    error_code: str
    details: str


class _EngineRegistry:
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

    def close_all(self, *, force: bool) -> None:
        with self._guard:
            engines = tuple(self._engines.values())
        for engine in engines:
            _close_engine(engine, force=force)


def _close_engine(engine: AnalysisEngine, *, force: bool) -> None:
    if force:
        if hasattr(engine, "force_terminate"):
            getattr(engine, "force_terminate")()
            return
        if hasattr(engine, "terminate"):
            getattr(engine, "terminate")()
            return
        raise EngineLifecycleError("tracked analysis engine has no forced-termination boundary")
    try:
        engine.close()
    except Exception:
        if hasattr(engine, "terminate"):
            getattr(engine, "terminate")()
        else:
            raise


def _error_code(error: BaseException) -> str:
    name = type(error).__name__.lower()
    if "timeout" in name:
        return "timeout"
    if "lifecycle" in name:
        return "engine_lifecycle"
    if "validation" in name:
        return "invalid_result"
    return "engine_failure"


def _analyse_one(
    position: SelectedPosition,
    profile: AnalysisProfile,
    registry: _EngineRegistry,
    controller: InterruptController,
) -> tuple[AnalysisResult, int]:
    last_error: BaseException | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if controller.hard_stop.is_set():
            raise _ForcedInterruption
        try:
            result = registry.current().analyse(position.fen)
            if controller.hard_stop.is_set():
                raise _ForcedInterruption
            if result.fen != position.fen:
                raise ValueError("engine returned a result for a different exact FEN")
            if result.profile.fingerprint != profile.fingerprint:
                raise ValueError("engine result profile does not match the active profile")
            return result, attempt
        except _ForcedInterruption:
            raise
        except Exception as error:
            last_error = error
            registry.discard_current()
            if controller.hard_stop.is_set():
                raise _ForcedInterruption from error
    assert last_error is not None
    raise _WorkerFailure(MAX_ATTEMPTS, _error_code(last_error), str(last_error)[:500])


def _persist_with_busy_retry(repository: AnalysisRepository, result: AnalysisResult) -> None:
    for attempt in range(3):
        try:
            repository.publish(result)
            return
        except AnalysisBusyError:
            if attempt == 2:
                raise
            time.sleep(0.02 * (attempt + 1))


ProgressCallback = Callable[[int, int], None]


def run_batch(
    connection: sqlite3.Connection,
    report: SelectionReport,
    profile: AnalysisProfile,
    engine_factory: EngineFactory,
    *,
    workers: int = DEFAULT_WORKERS,
    controller: InterruptController | None = None,
    progress: ProgressCallback | None = None,
) -> BatchRunResult:
    """Run only missing/stale positions; worker threads never receive SQLite."""

    if not 1 <= workers <= MAX_WORKERS:
        raise ValueError(f"workers must be between 1 and {MAX_WORKERS}")
    active_controller = controller or InterruptController()
    registry = _EngineRegistry(engine_factory)
    active_controller.bind_force_callback(lambda: registry.close_all(force=True))
    pending = iter(work_positions(connection, report, profile))
    inflight: dict[Future[tuple[AnalysisResult, int]], SelectedPosition] = {}
    failures: list[FinalPositionFailure] = []
    completed = 0
    consecutive_failures = 0
    circuit_breaker = False
    started_at = datetime.now(UTC).isoformat()
    executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="mp09-analysis")

    def dispatch() -> None:
        if active_controller.stop_dispatch.is_set() or circuit_breaker:
            return
        while len(inflight) < workers:
            try:
                position = next(pending)
            except StopIteration:
                return
            future = executor.submit(_analyse_one, position, profile, registry, active_controller)
            inflight[future] = position

    try:
        dispatch()
        while inflight:
            done, _ = wait(tuple(inflight), return_when=FIRST_COMPLETED)
            for future in done:
                position = inflight.pop(future)
                try:
                    result, _attempts = future.result()
                    _persist_with_busy_retry(AnalysisRepository(connection), result)
                except _ForcedInterruption:
                    continue
                except _WorkerFailure as error:
                    consecutive_failures += 1
                    failures.append(
                        FinalPositionFailure(
                            position.fen,
                            error.attempts,
                            error.error_code,
                            error.details,
                            datetime.now(UTC).isoformat(),
                        )
                    )
                except EngineLifecycleError:
                    raise
                except AnalysisBusyError as error:
                    consecutive_failures += 1
                    failures.append(
                        FinalPositionFailure(
                            position.fen,
                            1,
                            "sqlite_busy",
                            str(error)[:500],
                            datetime.now(UTC).isoformat(),
                        )
                    )
                except Exception as error:
                    consecutive_failures += 1
                    failures.append(
                        FinalPositionFailure(
                            position.fen,
                            1,
                            "persistence_failure",
                            str(error)[:500],
                            datetime.now(UTC).isoformat(),
                        )
                    )
                else:
                    completed += 1
                    consecutive_failures = 0
                    if progress:
                        progress(completed, len(report.positions_to_process))
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    circuit_breaker = True
            dispatch()
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
        registry.close_all(force=active_controller.hard_stop.is_set())

    interrupted = active_controller.stop_dispatch.is_set()
    status = "interrupted" if interrupted else ("failed" if failures else "success")
    details = json.dumps(
        {
            "circuit_breaker_tripped": circuit_breaker,
            "interrupted": interrupted,
            "hard_stop": active_controller.hard_stop.is_set(),
            "report": report.as_dict(),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    repository = AnalysisRepository(connection)
    run_id = _append_batch_with_busy_retry(
        repository,
        status=status,
        selection_json=json.dumps(report.game_uuids, separators=(",", ":")),
        settings_fingerprint=profile.fingerprint,
        started_at=started_at,
        finished_at=datetime.now(UTC).isoformat(),
        selected_positions=len(report.positions),
        eligible_positions=report.already_done,
        completed_positions=completed,
        failed_positions=len(failures),
        details=details,
        failures=failures,
    )
    return BatchRunResult(run_id, status, report, completed, tuple(failures), circuit_breaker)


def _append_batch_with_busy_retry(repository: AnalysisRepository, **values: object) -> int:
    for attempt in range(3):
        try:
            return repository.append_batch(**values)  # type: ignore[arg-type]
        except AnalysisBusyError:
            if attempt == 2:
                raise
            time.sleep(0.02 * (attempt + 1))
    raise AssertionError("unreachable")


def run_selected_games(
    database: Path,
    game_uuids: Sequence[str],
    profile: AnalysisProfile,
    engine_factory: EngineFactory,
    *,
    workers: int = DEFAULT_WORKERS,
    controller: InterruptController | None = None,
    lock_path: Path | None = None,
    progress: ProgressCallback | None = None,
) -> BatchRunResult:
    """Own the top-level lock, read selected games, then coordinate safe writes."""

    if not database.is_file():
        raise AnalysisLockError(f"database does not exist: {database}")
    with AnalysisRunLock(database, lock_path):
        read_uri = f"file:{database.resolve().as_posix()}?mode=ro"
        read_connection = sqlite3.connect(read_uri, uri=True)
        try:
            report = select_positions(read_connection, list(game_uuids), profile)
        finally:
            read_connection.close()
        connection = sqlite3.connect(database, timeout=0)
        try:
            return run_batch(
                connection,
                report,
                profile,
                engine_factory,
                workers=workers,
                controller=controller,
                progress=progress,
            )
        finally:
            connection.close()


def run_all_positions(
    database: Path,
    profile: AnalysisProfile,
    engine_factory: EngineFactory,
    *,
    workers: int = DEFAULT_WORKERS,
    controller: InterruptController | None = None,
    lock_path: Path | None = None,
    progress: ProgressCallback | None = None,
) -> BatchRunResult:
    """Run the complete accepted-corpus queue after a separately confirmed preflight."""

    if not database.is_file():
        raise AnalysisLockError(f"database does not exist: {database}")
    with AnalysisRunLock(database, lock_path):
        read_uri = f"file:{database.resolve().as_posix()}?mode=ro"
        read_connection = sqlite3.connect(read_uri, uri=True)
        try:
            report = select_all_positions(read_connection, profile)
        finally:
            read_connection.close()
        connection = sqlite3.connect(database, timeout=0)
        try:
            return run_batch(
                connection,
                report,
                profile,
                engine_factory,
                workers=workers,
                controller=controller,
                progress=progress,
            )
        finally:
            connection.close()
