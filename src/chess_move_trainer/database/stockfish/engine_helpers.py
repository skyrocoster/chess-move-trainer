"""Stockfish identity and result helpers."""

from __future__ import annotations

import math
import re
from pathlib import Path

import chess

from ..analysis import (
    AnalysisLine,
    AnalysisResultInput,
    AnalysisTerminalKind,
)
from ..positions import CanonicalPosition
from .configuration import (
    STOCKFISH_VERSION,
    StockfishProfile,
)
from .engine_models import (
    DEFAULT_STARTUP_TIMEOUT_SECONDS,
    ParsedUciInfo,
    SearchMetrics,
    StockfishIdentity,
    StockfishIdentityError,
    StockfishProtocolError,
)


def verify_stockfish_identity(
    executable: str | Path,
    *,
    timeout: float = DEFAULT_STARTUP_TIMEOUT_SECONDS,
) -> StockfishIdentity:
    """Verify one explicit executable and terminate it cleanly."""

    from .engine_runner import StockfishEngine

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


def _is_expected_stockfish(reported_name: str) -> bool:
    return (
        re.match(rf"^Stockfish\s+{re.escape(STOCKFISH_VERSION)}(?:\b|$)", reported_name) is not None
    )


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
