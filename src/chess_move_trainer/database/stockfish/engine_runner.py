"""Single-process Stockfish UCI control."""

from __future__ import annotations

import math
import os
import queue
import re
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, TextIO

import chess

from ..analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisScoreKind,
    AnalysisTerminalKind,
    AnalysisValidationError,
    validate_analysis_position,
)
from ..positions import CanonicalPosition
from .configuration import (
    STOCKFISH_NAME,
    STOCKFISH_VERSION,
    StockfishProfile,
    profile_for,
)

DEFAULT_STARTUP_TIMEOUT_SECONDS: Final[float] = 10.0
ANALYSIS_WATCHDOG_SECONDS: Final[float] = 30.0
_TERMINATION_WAIT_SECONDS: Final[float] = 0.5
_READER_JOIN_SECONDS: Final[float] = 0.2
_QUEUE_END: Final[object] = object()


from .engine_models import ParsedUciInfo, SearchMetrics, StockfishAnalysis, StockfishError, StockfishIdentity, StockfishIdentityError, StockfishProcessError, StockfishProtocolError, StockfishStartupError, StockfishWatchdogError
from .engine_helpers import _board_for_position, _classify_terminal, _fen_for_position, _finite_timeout, _is_stockfish_18, _line_from_info, _metrics_for, _result_for
from .engine_parsing import parse_uci_info


class StockfishEngine:
    """Reuse one Stockfish process sequentially, replacing it after failure."""

    def __init__(
        self,
        executable: str | Path,
        *,
        startup_timeout: float = DEFAULT_STARTUP_TIMEOUT_SECONDS,
        watchdog_seconds: float = ANALYSIS_WATCHDOG_SECONDS,
        popen_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.executable = Path(executable)
        self.startup_timeout = _finite_timeout(startup_timeout, "startup_timeout")
        self.watchdog_seconds = _finite_timeout(watchdog_seconds, "watchdog_seconds")
        self._popen_factory = popen_factory or subprocess.Popen
        self._process: Any | None = None
        self._reader: threading.Thread | None = None
        self._output: queue.Queue[object] = queue.Queue()
        self._identity: StockfishIdentity | None = None
        self._lock = threading.RLock()

    @property
    def identity(self) -> StockfishIdentity | None:
        """Return the verified identity, or ``None`` before startup."""

        return self._identity

    @property
    def is_running(self) -> bool:
        """Whether the wrapped process is still available for sequential work."""

        process = self._process
        return process is not None and process.poll() is None

    def start(self) -> StockfishIdentity:
        """Start and verify Stockfish 18 with a finite UCI handshake."""

        with self._lock:
            if self._identity is not None and self.is_running:
                return self._identity
            if self._process is not None:
                self._terminate_process()
            try:
                self._spawn_process()
                self._send("uci")
                reported_name: str | None = None
                deadline = time.monotonic() + self.startup_timeout
                while True:
                    line = self._next_line(deadline, "Stockfish startup")
                    if line.startswith("id name "):
                        reported_name = line[8:].strip()
                    elif line == "uciok":
                        break
                if not reported_name or not _is_stockfish_18(reported_name):
                    raise StockfishIdentityError(
                        f"Stockfish identity must be Stockfish 18, got {reported_name!r}"
                    )
                self._identity = StockfishIdentity(reported_name=reported_name)
                return self._identity
            except StockfishError:
                self._terminate_process()
                raise
            except BaseException as error:
                self._terminate_process()
                raise StockfishStartupError("Stockfish startup failed") from error

    def analyze(
        self,
        position: CanonicalPosition,
        profile: StockfishProfile | AnalysisQuality | str = "tool",
    ) -> StockfishAnalysis:
        """Analyze one canonical position with a fixed-node profile.

        The only chess search limit sent to Stockfish is ``go nodes``.  The
        watchdog is process protection and is never sent as a chess limit.
        """

        if not isinstance(position, CanonicalPosition):
            raise ValueError("position must be a canonical position value")
        selected_profile = profile_for(profile)
        board = _board_for_position(position)

        with self._lock:
            try:
                self.start()
                terminal_kind = _classify_terminal(board)
                if terminal_kind is not None:
                    return StockfishAnalysis(
                        profile=selected_profile,
                        result=_result_for(
                            selected_profile,
                            engine_name=self._verified_identity().engine_name,
                            engine_version=self._verified_identity().engine_version,
                            lines=(),
                        ),
                        terminal_kind=terminal_kind,
                        metrics=None,
                    )

                self._configure(selected_profile)
                self._send(f"position fen {_fen_for_position(position)}")
                self._send(f"go nodes {selected_profile.nodes}")
                infos: dict[int, ParsedUciInfo] = {}
                deadline = time.monotonic() + self.watchdog_seconds
                while True:
                    line = self._next_line(deadline, "Stockfish analysis")
                    if line.startswith("info "):
                        parsed = parse_uci_info(line, board.turn)
                        if parsed is not None:
                            infos[parsed.multipv] = parsed
                    elif line.startswith("bestmove "):
                        break

                expected_lines = min(selected_profile.multipv, board.legal_moves.count())
                if tuple(sorted(infos)) != tuple(range(1, expected_lines + 1)):
                    raise StockfishProtocolError(
                        "Stockfish did not return every requested MultiPV line"
                    )
                lines = tuple(_line_from_info(rank, infos[rank]) for rank in sorted(infos))
                result = _result_for(
                    selected_profile,
                    engine_name=self._verified_identity().engine_name,
                    engine_version=self._verified_identity().engine_version,
                    lines=lines,
                )
                try:
                    validate_analysis_position(position, result)
                except AnalysisValidationError as error:
                    raise StockfishProtocolError(
                        f"Stockfish returned an incomplete or illegal principal variation: {error}"
                    ) from error
                return StockfishAnalysis(
                    profile=selected_profile,
                    result=result,
                    terminal_kind=None,
                    metrics=_metrics_for(infos),
                )
            except BaseException:
                # A failed or watchdog-expired process is never left available
                # for replacement work.
                self._terminate_process()
                raise

    def close(self) -> None:
        """Terminate the child and close its pipes within finite bounds."""

        with self._lock:
            self._terminate_process()

    def __enter__(self) -> StockfishEngine:
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _spawn_process(self) -> None:
        kwargs: dict[str, Any] = {
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.DEVNULL,
            "text": True,
            "bufsize": 1,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self._process = self._popen_factory(str(self.executable), **kwargs)
        except OSError as error:
            raise StockfishStartupError(f"could not start Stockfish: {error}") from error
        stdout = getattr(self._process, "stdout", None)
        if stdout is None:
            raise StockfishStartupError("Stockfish process has no stdout pipe")
        self._output = queue.Queue()
        self._reader = threading.Thread(
            target=self._read_output,
            args=(stdout,),
            name="stockfish-output",
            daemon=True,
        )
        self._reader.start()

    def _read_output(self, stdout: TextIO) -> None:
        try:
            while True:
                line = stdout.readline()
                if line == "":
                    self._output.put(_QUEUE_END)
                    return
                self._output.put(line.rstrip("\r\n"))
        except BaseException as error:
            self._output.put(error)

    def _next_line(self, deadline: float, operation: str) -> str:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise StockfishWatchdogError(f"{operation} exceeded its finite timeout")
        try:
            item = self._output.get(timeout=remaining)
        except queue.Empty as error:
            raise StockfishWatchdogError(f"{operation} exceeded its finite timeout") from error
        if item is _QUEUE_END:
            raise StockfishProcessError(f"Stockfish exited during {operation.lower()}")
        if isinstance(item, BaseException):
            raise StockfishProcessError(
                f"Stockfish output failed during {operation.lower()}"
            ) from item
        return str(item)

    def _send(self, command: str) -> None:
        process = self._process
        stdin = getattr(process, "stdin", None)
        if process is None or process.poll() is not None or stdin is None:
            raise StockfishProcessError("Stockfish process is not running")
        try:
            stdin.write(f"{command}\n")
            stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise StockfishProcessError(f"Stockfish rejected command {command!r}") from error

    def _configure(self, profile: StockfishProfile) -> None:
        for name, value in profile.uci_options.items():
            rendered = "true" if value is True else str(value)
            self._send(f"setoption name {name} value {rendered}")
        # Clear Hash is intentionally sent for every analysis, including when
        # the same process and profile are reused for the next position.
        self._send("setoption name Clear Hash")
        self._ready("Stockfish option setup")

    def _ready(self, operation: str) -> None:
        self._send("isready")
        deadline = time.monotonic() + self.startup_timeout
        while True:
            if self._next_line(deadline, operation) == "readyok":
                return

    def _verified_identity(self) -> StockfishIdentity:
        if self._identity is None:
            raise StockfishStartupError("Stockfish identity was not verified")
        return self._identity

    def _terminate_process(self) -> None:
        process = self._process
        reader = self._reader
        self._process = None
        self._reader = None
        self._identity = None
        if process is None:
            return
        stdin = getattr(process, "stdin", None)
        if stdin is not None:
            try:
                stdin.close()
            except OSError:
                pass
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=_TERMINATION_WAIT_SECONDS)
        except (OSError, subprocess.TimeoutExpired):
            try:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=_TERMINATION_WAIT_SECONDS)
            except (OSError, subprocess.TimeoutExpired):
                pass
        for stream_name in ("stdout", "stderr"):
            stream = getattr(process, stream_name, None)
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass
        if reader is not None:
            reader.join(timeout=_READER_JOIN_SECONDS)


