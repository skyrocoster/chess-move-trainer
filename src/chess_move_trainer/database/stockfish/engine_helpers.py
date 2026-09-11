"""Stockfish identity and result helpers."""

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


from .engine_models import SearchMetrics


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
        return next(
            (getattr(info, name) for info in ordered if getattr(info, name) is not None),
            None,
        )

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
