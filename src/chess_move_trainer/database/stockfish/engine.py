"""Finite, single-process Stockfish UCI control and normalization."""

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
from ..positions import CanonicalPosition, canonicalize_fen
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


class StockfishError(RuntimeError):
    """Base class for bounded Stockfish process or protocol failures."""


class StockfishStartupError(StockfishError):
    """The process did not complete the finite UCI startup handshake."""


class StockfishIdentityError(StockfishStartupError):
    """The executable did not identify itself as Stockfish 18."""


class StockfishProtocolError(StockfishError):
    """Stockfish returned malformed or incomplete UCI analysis data."""


class StockfishProcessError(StockfishError):
    """The Stockfish child process stopped or could not accept a command."""


class StockfishWatchdogError(StockfishError, TimeoutError):
    """The per-analysis watchdog expired before Stockfish returned bestmove."""


@dataclass(frozen=True, slots=True)
class StockfishIdentity:
    """The verified identity reported by the UCI startup handshake."""

    reported_name: str
    engine_name: str = STOCKFISH_NAME
    engine_version: str = STOCKFISH_VERSION


@dataclass(frozen=True, slots=True)
class ParsedUciInfo:
    """One complete normalized ``info`` payload for a MultiPV line."""

    multipv: int
    depth: int
    score_kind: AnalysisScoreKind
    score_value: int
    wdl_wins: int
    wdl_draws: int
    wdl_losses: int
    pv_uci: tuple[str, ...]
    nodes: int | None = None
    nps: int | None = None
    seldepth: int | None = None
    hashfull: int | None = None
    time_ms: int | None = None


@dataclass(frozen=True, slots=True)
class SearchMetrics:
    """Final engine-reported measurements retained by the benchmark."""

    nodes: int | None = None
    nps: int | None = None
    depth: int | None = None
    seldepth: int | None = None
    hashfull: int | None = None
    time_ms: int | None = None


@dataclass(frozen=True, slots=True)
class StockfishAnalysis:
    """A normalized result ready for the engine-independent DB-06 publisher."""

    profile: StockfishProfile
    result: AnalysisResultInput
    terminal_kind: AnalysisTerminalKind | None
    metrics: SearchMetrics | None = None

    @property
    def lines(self) -> tuple[AnalysisLine, ...]:
        """Expose candidate lines without requiring callers to unwrap the result."""

        return self.result.lines


def normalize_score(
    score_kind: AnalysisScoreKind | str,
    score_value: int,
    side_to_move: chess.Color,
) -> tuple[AnalysisScoreKind, int]:
    """Convert Stockfish's side-to-move score to signed White POV."""

    try:
        kind = AnalysisScoreKind(score_kind)
    except (TypeError, ValueError) as error:
        raise StockfishProtocolError("UCI score kind must be cp or mate") from error
    if type(score_value) is not int:
        raise StockfishProtocolError("UCI score value must be an integer")
    return kind, score_value if side_to_move == chess.WHITE else -score_value


def normalize_wdl(
    wdl_wins: int,
    wdl_draws: int,
    wdl_losses: int,
    side_to_move: chess.Color,
) -> tuple[int, int, int]:
    """Convert Stockfish's side-to-move WDL tuple to White POV."""

    values = (wdl_wins, wdl_draws, wdl_losses)
    if any(type(value) is not int or value < 0 for value in values):
        raise StockfishProtocolError("UCI WDL values must be non-negative integers")
    if side_to_move == chess.WHITE:
        return values
    return wdl_losses, wdl_draws, wdl_wins


def parse_uci_info(line: str, side_to_move: chess.Color) -> ParsedUciInfo | None:
    """Parse a complete candidate-line ``info`` record.

    Informational lines emitted before a score, WDL, or PV is available are
    deliberately ignored.  A final ``bestmove`` is accepted only when every
    requested MultiPV line has supplied a complete payload.
    """

    tokens = line.strip().split()
    if not tokens or tokens[0] != "info":
        return None

    multipv = 1
    depth: int | None = None
    score: tuple[AnalysisScoreKind, int] | None = None
    wdl: tuple[int, int, int] | None = None
    pv: tuple[str, ...] | None = None
    nodes: int | None = None
    nps: int | None = None
    seldepth: int | None = None
    hashfull: int | None = None
    time_ms: int | None = None
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "depth":
            depth = _parse_int(tokens, index + 1, "depth")
            index += 2
        elif token == "multipv":
            multipv = _parse_int(tokens, index + 1, "multipv")
            index += 2
        elif token == "score":
            if index + 2 >= len(tokens):
                raise StockfishProtocolError("UCI score payload is incomplete")
            try:
                kind = AnalysisScoreKind(tokens[index + 1])
            except ValueError as error:
                raise StockfishProtocolError("UCI score kind must be cp or mate") from error
            score_value = _parse_int(tokens, index + 2, "score value")
            score = normalize_score(kind, score_value, side_to_move)
            index += 3
        elif token == "wdl":
            wdl = (
                _parse_int(tokens, index + 1, "WDL wins"),
                _parse_int(tokens, index + 2, "WDL draws"),
                _parse_int(tokens, index + 3, "WDL losses"),
            )
            wdl = normalize_wdl(*wdl, side_to_move)
            index += 4
        elif token in {"nodes", "nps", "seldepth", "hashfull", "time"}:
            value = _parse_int(tokens, index + 1, token)
            if token == "nodes":
                nodes = value
            elif token == "nps":
                nps = value
            elif token == "seldepth":
                seldepth = value
            elif token == "hashfull":
                hashfull = value
            else:
                time_ms = value
            index += 2
        elif token == "pv":
            pv = tuple(tokens[index + 1 :])
            index = len(tokens)
        else:
            index += 1

    if multipv < 1 or depth is None or score is None or wdl is None or not pv:
        return None
    return ParsedUciInfo(
        multipv=multipv,
        depth=depth,
        score_kind=score[0],
        score_value=score[1],
        wdl_wins=wdl[0],
        wdl_draws=wdl[1],
        wdl_losses=wdl[2],
        pv_uci=pv,
        nodes=nodes,
        nps=nps,
        seldepth=seldepth,
        hashfull=hashfull,
        time_ms=time_ms,
    )


def _parse_int(tokens: list[str], index: int, label: str) -> int:
    if index >= len(tokens):
        raise StockfishProtocolError(f"UCI {label} is missing")
    try:
        return int(tokens[index])
    except ValueError as error:
        raise StockfishProtocolError(f"UCI {label} must be an integer") from error


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
            raise StockfishProcessError(f"Stockfish output failed during {operation.lower()}") from item
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


def verify_stockfish_identity(
    executable: str | Path,
    *,
    timeout: float = DEFAULT_STARTUP_TIMEOUT_SECONDS,
) -> StockfishIdentity:
    """Verify one explicit executable and terminate it cleanly."""

    with StockfishEngine(executable, startup_timeout=timeout) as engine:
        identity = engine.identity
        if identity is None:  # pragma: no cover - start() guarantees this
            raise StockfishIdentityError("Stockfish identity was not reported")
        return identity


def _line_from_info(rank: int, info: ParsedUciInfo) -> AnalysisLine:
    return AnalysisLine(
        rank=rank,
        score_kind=info.score_kind,
        score_value=info.score_value,
        wdl_wins=info.wdl_wins,
        wdl_draws=info.wdl_draws,
        wdl_losses=info.wdl_losses,
        pv_uci=info.pv_uci,
        depth=info.depth,
    )


def _metrics_for(infos: dict[int, ParsedUciInfo]) -> SearchMetrics:
    """Select one final, bounded metrics record from the final MultiPV lines."""

    ordered = tuple(infos[rank] for rank in sorted(infos))

    def first_value(name: str) -> int | None:
        return next((getattr(info, name) for info in ordered if getattr(info, name) is not None), None)

    return SearchMetrics(
        nodes=first_value("nodes"),
        nps=first_value("nps"),
        depth=max(info.depth for info in ordered),
        seldepth=first_value("seldepth"),
        hashfull=first_value("hashfull"),
        time_ms=first_value("time_ms"),
    )


def _result_for(
    profile: StockfishProfile,
    *,
    engine_name: str,
    engine_version: str,
    lines: tuple[AnalysisLine, ...],
) -> AnalysisResultInput:
    return AnalysisResultInput(
        quality=profile.quality,
        configuration_version=profile.configuration_version,
        settings=profile.settings,
        engine_name=engine_name,
        engine_version=engine_version,
        lines=lines,
    )


def _board_for_position(position: CanonicalPosition) -> chess.Board:
    try:
        return chess.Board(_fen_for_position(position))
    except (TypeError, ValueError) as error:
        raise StockfishProtocolError("canonical position could not form a chess root") from error


def _fen_for_position(position: CanonicalPosition) -> str:
    return " ".join(
        (
            position.placement,
            position.side_to_move,
            position.castling_rights,
            position.legal_en_passant,
            "0",
            "1",
        )
    )


def _classify_terminal(board: chess.Board) -> AnalysisTerminalKind | None:
    if board.is_checkmate():
        return AnalysisTerminalKind.CHECKMATE
    if board.is_stalemate():
        return AnalysisTerminalKind.STALEMATE
    if board.is_insufficient_material():
        return AnalysisTerminalKind.INSUFFICIENT_MATERIAL
    return None


def _is_stockfish_18(reported_name: str) -> bool:
    return re.match(r"^Stockfish\s+18(?:\b|$)", reported_name) is not None


def _finite_timeout(value: float, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be finite and greater than zero")
    try:
        normalized = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be finite and greater than zero") from error
    if not math.isfinite(normalized) or normalized <= 0:
        raise ValueError(f"{label} must be finite and greater than zero")
    return normalized


__all__ = [
    "ANALYSIS_WATCHDOG_SECONDS",
    "DEFAULT_STARTUP_TIMEOUT_SECONDS",
    "ParsedUciInfo",
    "SearchMetrics",
    "StockfishAnalysis",
    "StockfishEngine",
    "StockfishError",
    "StockfishIdentity",
    "StockfishIdentityError",
    "StockfishProcessError",
    "StockfishProtocolError",
    "StockfishStartupError",
    "StockfishWatchdogError",
    "normalize_score",
    "normalize_wdl",
    "parse_uci_info",
    "verify_stockfish_identity",
]
