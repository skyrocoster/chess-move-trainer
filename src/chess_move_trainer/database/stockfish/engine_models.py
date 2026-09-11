"""Stockfish error types and result dataclasses."""

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


