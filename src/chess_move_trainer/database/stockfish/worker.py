"""Serial, mutex-guarded Stockfish queue draining with bounded recovery."""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text

from ..analysis import AnalysisResultInput
from ..connection import DEFAULT_LOCK_TIMEOUT_SECONDS, _open_existing_connection
from ..positions import CanonicalPosition
from ..schema import _assert_compatible_schema
from .engine import StockfishAnalysis, StockfishEngine
from .mutex import DatabaseMutex, MutexBusyError
from .queue import QueueClaim, QueueService

DEFAULT_RECOVERY_POLL_SECONDS = 1.0


class WorkerError(RuntimeError):
    """Base class for bounded queue-worker failures."""


class WorkerInputError(WorkerError, ValueError):
    """Raised when worker input is not an explicit supported value."""


@dataclass(frozen=True, slots=True)
class WorkerFailure:
    """One isolated request failure retained only in the launch outcome."""

    position_id: int | None
    message: str


@dataclass(frozen=True, slots=True)
class WorkerOutcome:
    """Observable result of one finite worker launch."""

    claimed_count: int
    completed_count: int
    not_saved_count: int
    failures: tuple[WorkerFailure, ...] = ()
    interrupted: bool = False
    drained: bool = True
    recovery_polls: int = 0

    @property
    def exit_code(self) -> int:
        """Return the later CLI-compatible status for this service outcome."""

        if self.interrupted:
            return 130
        return 1 if self.failures or not self.drained else 0

    @property
    def succeeded(self) -> bool:
        """Whether this finite launch completed without failures or interruption."""

        return self.exit_code == 0


class WorkerRunner:
    """Drain queued requests with one sequential engine process at a time."""

    def __init__(
        self,
        database_path: str | Path,
        executable: str | Path,
        *,
        lock_timeout: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
        mutex_acquire_timeout: float = 0.0,
        recovery_poll_seconds: float = DEFAULT_RECOVERY_POLL_SECONDS,
        _clock: Callable[[], datetime] | None = None,
        _sleep: Callable[[float], None] | None = None,
        _queue_factory: Callable[[str | Path, float], Any] | None = None,
        _engine_factory: Callable[[], Any] | None = None,
        _mutex_factory: Callable[[str | Path], Any] | None = None,
        _position_loader: Callable[[int], CanonicalPosition] | None = None,
    ) -> None:
        if not isinstance(executable, (str, Path)) or not str(executable):
            raise WorkerInputError("executable must be an explicit path")
        self._database_path = database_path
        self._executable = executable
        self._lock_timeout = lock_timeout
        self._mutex_acquire_timeout = _finite_non_negative(
            mutex_acquire_timeout, "mutex_acquire_timeout"
        )
        self._recovery_poll_seconds = _finite_positive(
            recovery_poll_seconds, "recovery_poll_seconds"
        )
        self._clock = _clock or (lambda: datetime.now(UTC))
        self._sleep = _sleep or time.sleep
        self._queue_factory = _queue_factory or (
            lambda path, timeout: QueueService(path, lock_timeout=timeout)
        )
        self._engine_factory = _engine_factory or (
            lambda: StockfishEngine(self._executable)
        )
        self._mutex_factory = _mutex_factory or (lambda path: DatabaseMutex(path))
        self._position_loader = _position_loader or self._load_position

    def run(self) -> WorkerOutcome:
        """Drain current queued/reclaimable work and then exit."""

        queue = self._queue_factory(self._database_path, self._lock_timeout)
        mutex = self._mutex_factory(self._database_path)
        if not mutex.acquire(timeout=self._mutex_acquire_timeout):
            raise MutexBusyError(
                f"Stockfish analysis is already running for {self._database_path}"
            )

        engine: Any | None = None
        current_claim: QueueClaim | None = None
        failures: list[WorkerFailure] = []
        failed_position_ids: set[int] = set()
        claimed_count = 0
        completed_count = 0
        not_saved_count = 0
        interrupted = False
        drained = True
        recovery_polls = 0

        try:
            while True:
                try:
                    claim = queue.claim(
                        now=self._clock(),
                        exclude_position_ids=failed_position_ids,
                    )
                except KeyboardInterrupt:
                    interrupted = True
                    break
                except Exception as error:
                    failures.append(WorkerFailure(None, str(error)))
                    drained = False
                    break

                if claim is None and getattr(mutex, "acquired_abandoned", False):
                    try:
                        claim, polls = self._recover_young_claim(
                            queue,
                            failed_position_ids,
                            failures,
                        )
                    except KeyboardInterrupt:
                        interrupted = True
                        break
                    except Exception as error:
                        failures.append(WorkerFailure(None, str(error)))
                        drained = False
                        break
                    recovery_polls += polls
                    if claim is None and failures and failures[-1].position_id is None:
                        drained = False

                if claim is None:
                    break

                claimed_count += 1
                current_claim = claim

                try:
                    position = self._position_loader(claim.position_id)
                except KeyboardInterrupt:
                    interrupted = True
                    if self._release_claim(queue, claim, failures):
                        current_claim = None
                    break
                except Exception as error:
                    failures.append(WorkerFailure(claim.position_id, str(error)))
                    failed_position_ids.add(claim.position_id)
                    self._fail_claim(queue, claim, failures)
                    current_claim = None
                    continue

                if engine is None:
                    try:
                        engine = self._engine_factory()
                    except KeyboardInterrupt:
                        interrupted = True
                        if self._release_claim(queue, claim, failures):
                            current_claim = None
                        break
                    except Exception as error:
                        failures.append(WorkerFailure(claim.position_id, str(error)))
                        failed_position_ids.add(claim.position_id)
                        self._fail_claim(queue, claim, failures)
                        current_claim = None
                        continue

                try:
                    analysis = engine.analyze(position, claim.claimed_quality)
                    result = _analysis_result(analysis)
                except KeyboardInterrupt:
                    self._close_engine(engine)
                    engine = None
                    interrupted = True
                    if self._release_claim(queue, claim, failures):
                        current_claim = None
                    break
                except Exception as error:
                    # StockfishEngine has already terminated a failed process;
                    # close the wrapper too before a replacement is created.
                    self._close_engine(engine)
                    engine = None
                    failures.append(WorkerFailure(claim.position_id, str(error)))
                    failed_position_ids.add(claim.position_id)
                    self._fail_claim(queue, claim, failures)
                    current_claim = None
                    continue

                try:
                    completion = queue.complete(claim, result)
                except KeyboardInterrupt:
                    interrupted = True
                    if self._release_claim(queue, claim, failures):
                        current_claim = None
                    break
                except Exception as error:
                    failures.append(WorkerFailure(claim.position_id, str(error)))
                    failed_position_ids.add(claim.position_id)
                    self._fail_claim(queue, claim, failures)
                    current_claim = None
                    continue

                current_claim = None
                if completion.applied:
                    completed_count += 1
                    if completion.publication is not None and not completion.publication.saved:
                        not_saved_count += 1

        finally:
            if current_claim is not None:
                self._release_claim(queue, current_claim, failures)
            if engine is not None:
                self._close_engine(engine)
            try:
                mutex.release()
            except Exception as error:
                failures.append(WorkerFailure(None, str(error)))
                drained = False

        return WorkerOutcome(
            claimed_count=claimed_count,
            completed_count=completed_count,
            not_saved_count=not_saved_count,
            failures=tuple(failures),
            interrupted=interrupted,
            drained=drained,
            recovery_polls=recovery_polls,
        )

    def _recover_young_claim(
        self,
        queue: Any,
        failed_position_ids: set[int],
        failures: list[WorkerFailure],
    ) -> tuple[QueueClaim | None, int]:
        now = self._clock()
        deadline = queue.young_running_claim_deadline(now=now)
        if deadline is None:
            return None, 0

        remaining = (deadline - now).total_seconds()
        max_polls = max(1, math.ceil(max(remaining, 0.0) / self._recovery_poll_seconds) + 1)
        polls = 0
        while True:
            current = self._clock()
            remaining = (deadline - current).total_seconds()
            if remaining <= 0:
                claim = queue.claim(
                    now=current,
                    exclude_position_ids=failed_position_ids,
                )
                if claim is not None:
                    return claim, polls
                failures.append(
                    WorkerFailure(
                        None,
                        "young running queue claim remained unreclaimable at its stale boundary",
                    )
                )
                return None, polls
            if polls >= max_polls:
                failures.append(
                    WorkerFailure(
                        None,
                        "young running queue claim could not be polled to its stale boundary",
                    )
                )
                return None, polls

            self._sleep(min(self._recovery_poll_seconds, remaining))
            polls += 1
            try:
                claim = queue.claim(
                    now=self._clock(),
                    exclude_position_ids=failed_position_ids,
                )
            except KeyboardInterrupt:
                raise
            if claim is not None:
                return claim, polls

    def _load_position(self, position_id: int) -> CanonicalPosition:
        with _open_existing_connection(self._database_path, self._lock_timeout) as connection:
            _assert_compatible_schema(connection, self._lock_timeout)
            row = connection.execute(
                text(
                    """
                    SELECT dp_placement, dp_side_to_move, dp_castling_rights,
                           dp_legal_en_passant
                    FROM derived_position
                    WHERE dp_position_id = :position_id
                    """
                ),
                {"position_id": position_id},
            ).first()
        if row is None:
            raise WorkerError(f"canonical position {position_id} does not exist")
        return CanonicalPosition(
            placement=row[0],
            side_to_move=row[1],
            castling_rights=row[2],
            legal_en_passant=row[3],
        )

    @staticmethod
    def _close_engine(engine: Any) -> None:
        try:
            engine.close()
        except Exception:
            pass

    @staticmethod
    def _release_claim(
        queue: Any,
        claim: QueueClaim,
        failures: list[WorkerFailure],
    ) -> bool:
        try:
            return bool(queue.release(claim))
        except Exception as error:
            failures.append(WorkerFailure(claim.position_id, str(error)))
            return False

    @staticmethod
    def _fail_claim(
        queue: Any,
        claim: QueueClaim,
        failures: list[WorkerFailure],
    ) -> None:
        try:
            queue.fail(claim)
        except Exception as error:
            failures.append(WorkerFailure(claim.position_id, str(error)))


SerialWorkerRunner = WorkerRunner


def _analysis_result(analysis: StockfishAnalysis | AnalysisResultInput) -> AnalysisResultInput:
    if isinstance(analysis, StockfishAnalysis):
        return analysis.result
    if isinstance(analysis, AnalysisResultInput):
        return analysis
    candidate = getattr(analysis, "result", None)
    if isinstance(candidate, AnalysisResultInput):
        return candidate
    raise WorkerError("engine did not return a normalized analysis result")


def _finite_positive(value: float, label: str) -> float:
    if isinstance(value, bool):
        raise WorkerInputError(f"{label} must be finite and greater than zero")
    try:
        normalized = float(value)
    except (TypeError, ValueError) as error:
        raise WorkerInputError(f"{label} must be finite and greater than zero") from error
    if not math.isfinite(normalized) or normalized <= 0:
        raise WorkerInputError(f"{label} must be finite and greater than zero")
    return normalized


def _finite_non_negative(value: float, label: str) -> float:
    if isinstance(value, bool):
        raise WorkerInputError(f"{label} must be finite and non-negative")
    try:
        normalized = float(value)
    except (TypeError, ValueError) as error:
        raise WorkerInputError(f"{label} must be finite and non-negative") from error
    if not math.isfinite(normalized) or normalized < 0:
        raise WorkerInputError(f"{label} must be finite and non-negative")
    return normalized


__all__ = [
    "DEFAULT_RECOVERY_POLL_SECONDS",
    "SerialWorkerRunner",
    "WorkerError",
    "WorkerFailure",
    "WorkerInputError",
    "WorkerOutcome",
    "WorkerRunner",
]
