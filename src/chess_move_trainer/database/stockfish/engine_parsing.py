"""UCI info parsing and score normalization."""

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


from .engine_models import ParsedUciInfo


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


