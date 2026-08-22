"""Managed, per-owner Stockfish process and result-conversion boundary."""

from __future__ import annotations

import hashlib
import re
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

import chess
import chess.engine

from .errors import AnalysisTimeoutError, AnalysisValidationError, EngineLifecycleError
from .models import AnalysisCandidate, AnalysisProfile, AnalysisResult, canonical_fen

EXPECTED_ENGINE_PATTERN = re.compile(r"^Stockfish 18(?:\s|$)", re.IGNORECASE)


@dataclass(frozen=True)
class EngineIdentity:
    reported_name: str
    version: str
    binary_sha256: str


class EngineProcess(Protocol):
    """Only the process operations the managed boundary is allowed to use."""

    identity: EngineIdentity
    pid: int

    def configure(self, options: Mapping[str, object]) -> None: ...

    def analyse(
        self, board: chess.Board, limit: chess.engine.Limit, **kwargs: object
    ) -> object: ...

    def quit(self) -> None: ...

    def terminate(self) -> None: ...

    def wait_exited(self, timeout: float) -> bool: ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _identity(reported_name: object, checksum: str) -> EngineIdentity:
    name = str(reported_name).strip()
    if not EXPECTED_ENGINE_PATTERN.match(name):
        raise EngineLifecycleError(f"expected reported Stockfish 18 identity, got {name!r}")
    return EngineIdentity(name, "18", checksum)


def _engine_shutdown_poll(engine: chess.engine.SimpleEngine, timeout: float) -> bool:
    """Bounded synchronous proof that a python-chess child is shut down and exited.

    python-chess exposes shutdown_event as an asyncio.Event, whose wait() is an
    awaitable with no timeout argument, so lifecycle code must never await it.
    This polls the shutdown flag and the tracked transport's return code instead.
    """
    deadline = time.monotonic() + timeout
    while True:
        if engine.shutdown_event.is_set() and engine.transport.get_returncode() is not None:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.01)


class PythonChessProcess:
    """A tracked python-chess process; termination is limited to its own transport."""

    def __init__(self, engine: chess.engine.SimpleEngine, identity: EngineIdentity) -> None:
        self._engine = engine
        self.identity = identity
        self.pid = int(engine.transport.get_pid())

    @classmethod
    def launch(cls, executable: Path, *, timeout: float = 10.0) -> PythonChessProcess:
        if not executable.is_file():
            raise EngineLifecycleError(f"engine executable does not exist: {executable}")
        checksum = sha256_file(executable)
        try:
            engine = chess.engine.SimpleEngine.popen_uci(str(executable), timeout=timeout)
            process = cls(engine, EngineIdentity("unverified", "unverified", checksum))
            process.identity = _identity(engine.id.get("name"), checksum)
            return process
        except Exception as error:
            if "process" in locals():
                close_process(process, timeout)
            elif "engine" in locals():
                engine.close()
                if not _engine_shutdown_poll(engine, timeout):
                    raise EngineLifecycleError(
                        "failed engine launch did not leave a provably closed child"
                    ) from error
            raise EngineLifecycleError(f"Stockfish 18 verification failed: {error}") from error

    def configure(self, options: Mapping[str, object]) -> None:
        self._engine.configure(options)

    def analyse(self, board: chess.Board, limit: chess.engine.Limit, **kwargs: object) -> object:
        return self._engine.analyse(board, limit, **kwargs)

    def quit(self) -> None:
        self._engine.quit()

    def terminate(self) -> None:
        # SimpleEngine.close() schedules transport.close(); asyncio then kills only this child.
        self._engine.close()

    def wait_exited(self, timeout: float) -> bool:
        return _engine_shutdown_poll(self._engine, timeout)


def _bounded_call(call: Callable[[], object], timeout: float) -> tuple[bool, object | None]:
    completed = threading.Event()
    result: list[object] = []

    def invoke() -> None:
        try:
            result.append(call())
        except BaseException as error:  # Propagated on the owning thread.
            result.append(error)
        finally:
            completed.set()

    threading.Thread(target=invoke, daemon=True).start()
    if not completed.wait(timeout):
        return False, None
    value = result[0]
    if isinstance(value, BaseException):
        raise value
    return True, value


def close_process(process: EngineProcess, timeout: float = 5.0) -> None:
    """Bounded, idempotent graceful quit with a tracked-process-only fallback."""

    if process.wait_exited(0):
        return
    graceful = False
    try:
        graceful, _ = _bounded_call(process.quit, timeout)
    except BaseException:
        graceful = False
    if graceful and process.wait_exited(timeout):
        return
    process.terminate()
    if not process.wait_exited(timeout):
        raise EngineLifecycleError(f"tracked engine PID {process.pid} did not exit")


def inspect_stockfish_executable(path: Path, *, timeout: float = 10.0) -> EngineIdentity:
    process = PythonChessProcess.launch(path, timeout=timeout)
    try:
        return process.identity
    finally:
        close_process(process, timeout)


class ManagedStockfish:
    """One non-shareable engine instance intended to be owned by one future worker."""

    def __init__(
        self,
        process: EngineProcess,
        profile: AnalysisProfile,
        *,
        watchdog_seconds: float = 30.0,
        shutdown_seconds: float = 5.0,
    ) -> None:
        if watchdog_seconds <= 0 or shutdown_seconds <= 0:
            raise ValueError("watchdog and shutdown bounds must be positive")
        if process.identity.binary_sha256 != profile.engine_binary_sha256:
            raise AnalysisValidationError("engine checksum does not match the active profile")
        if process.identity.version != profile.engine_version:
            raise AnalysisValidationError(
                "reported engine version does not match the active profile"
            )
        self._process = process
        self._profile = profile
        self._watchdog = watchdog_seconds
        self._shutdown = shutdown_seconds
        self._use_lock = threading.Lock()
        self._closed = False
        process.configure({"Threads": 1, "Hash": 128, "UCI_ShowWDL": True})

    def analyse(self, fen: str) -> AnalysisResult:
        if self._closed:
            raise EngineLifecycleError("engine instance is closed")
        if not self._use_lock.acquire(blocking=False):
            raise EngineLifecycleError("engine instance cannot be shared across workers")
        try:
            board = chess.Board(canonical_fen(fen))
            outcome = board.outcome(claim_draw=True)
            if outcome is not None:
                return AnalysisResult(
                    fen=fen,
                    profile=self._profile,
                    candidates=(),
                    terminal_kind=outcome.termination.name.lower(),
                    completed_at=datetime.now(UTC).isoformat(),
                    wall_time_ms=0,
                )
            self._process.configure({"Clear Hash": None})
            token = object()
            started = time.monotonic()
            completed, raw = _bounded_call(
                lambda: self._process.analyse(
                    board,
                    chess.engine.Limit(nodes=self._profile.node_budget),
                    multipv=5,
                    game=token,
                    info=chess.engine.INFO_ALL,
                ),
                self._watchdog,
            )
            wall_ms = int(round((time.monotonic() - started) * 1000))
            if not completed:
                self._closed = True
                self._process.terminate()
                if not self._process.wait_exited(self._shutdown):
                    raise EngineLifecycleError(
                        f"timed-out tracked engine PID {self._process.pid} did not exit"
                    )
                raise AnalysisTimeoutError(
                    f"engine PID {self._process.pid} exceeded {self._watchdog:g}s watchdog"
                )
            return _convert_result(board, self._profile, raw, wall_ms)
        finally:
            self._use_lock.release()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        close_process(self._process, self._shutdown)

    def force_terminate(self) -> None:
        """Immediately terminate this tracked child for the second Ctrl+C level."""

        if self._closed:
            return
        self._closed = True
        self._process.terminate()
        if not self._process.wait_exited(self._shutdown):
            raise EngineLifecycleError(f"tracked engine PID {self._process.pid} did not exit")

    def __enter__(self) -> ManagedStockfish:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def _required_int(info: Mapping[str, Any], field: str, *, positive: bool = False) -> int:
    value = info.get(field)
    minimum = 1 if positive else 0
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise AnalysisValidationError(f"engine output requires valid {field}")
    return value


def _score(score: object) -> tuple[str, int]:
    if not isinstance(score, chess.engine.PovScore):
        raise AnalysisValidationError("engine output requires a POV score")
    white = score.white()
    if white is chess.engine.MateGiven:
        return "mate_given", 0
    if isinstance(white, chess.engine.Mate):
        mate = white.mate()
        if mate is None:
            raise AnalysisValidationError("engine mate score is malformed")
        return "mate", mate
    if isinstance(white, chess.engine.Cp):
        cp = white.score()
        if cp is None:
            raise AnalysisValidationError("engine centipawn score is malformed")
        return "cp", cp
    raise AnalysisValidationError("engine score kind is unsupported")


def _candidate(rank: int, info: object) -> AnalysisCandidate:
    if not isinstance(info, Mapping):
        raise AnalysisValidationError("engine candidate output must be a mapping")
    kind, value = _score(info.get("score"))
    wdl = info.get("wdl")
    if not isinstance(wdl, chess.engine.PovWdl):
        raise AnalysisValidationError("engine output requires engine-emitted POV WDL")
    white_wdl = wdl.white()
    pv = info.get("pv")
    if not isinstance(pv, list) or not pv or any(not isinstance(move, chess.Move) for move in pv):
        raise AnalysisValidationError("engine output requires a complete UCI PV")
    engine_time = info.get("time")
    if (
        isinstance(engine_time, bool)
        or not isinstance(engine_time, (int, float))
        or engine_time < 0
    ):
        raise AnalysisValidationError("engine output requires valid engine timing")
    return AnalysisCandidate(
        rank=rank,
        score_kind=kind,
        score_value=value,
        wdl_wins=white_wdl.wins,
        wdl_draws=white_wdl.draws,
        wdl_losses=white_wdl.losses,
        pv_uci=tuple(move.uci() for move in pv),
        depth=_required_int(info, "depth"),
        seldepth=_required_int(info, "seldepth"),
        nodes=_required_int(info, "nodes", positive=True),
        engine_time_ms=int(round(engine_time * 1000)),
    )


def _convert_result(
    board: chess.Board, profile: AnalysisProfile, raw: object, wall_time_ms: int
) -> AnalysisResult:
    entries = raw if isinstance(raw, list) else [raw]
    expected = min(5, board.legal_moves.count())
    if len(entries) != expected:
        raise AnalysisValidationError("engine returned an incomplete MultiPV result")
    candidates = tuple(_candidate(rank, info) for rank, info in enumerate(entries, 1))
    return AnalysisResult(
        fen=board.fen(en_passant="fen"),
        profile=profile,
        candidates=candidates,
        terminal_kind=None,
        completed_at=datetime.now(UTC).isoformat(),
        wall_time_ms=wall_time_ms,
    )
