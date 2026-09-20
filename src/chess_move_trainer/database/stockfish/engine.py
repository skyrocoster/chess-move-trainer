"""Finite, single-process Stockfish UCI control and normalization.

Thin compatibility shim. Implementation lives in engine_models,
engine_parsing, engine_runner, and engine_helpers.
"""

from __future__ import annotations

from .engine_helpers import (
    verify_stockfish_identity,
)
from .engine_models import (
    ANALYSIS_WATCHDOG_SECONDS,
    DEFAULT_STARTUP_TIMEOUT_SECONDS,
    ParsedUciInfo,
    SearchMetrics,
    StockfishAnalysis,
    StockfishError,
    StockfishIdentity,
    StockfishIdentityError,
    StockfishProcessError,
    StockfishProtocolError,
    StockfishStartupError,
    StockfishWatchdogError,
)
from .engine_parsing import normalize_score, normalize_wdl, parse_uci_info
from .engine_runner import StockfishEngine

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
