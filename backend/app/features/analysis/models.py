"""Validated value objects for persisted Stockfish analysis."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

import chess

from .errors import AnalysisValidationError

PROFILE_CONTRACT_VERSION = 1
MAX_CANDIDATES = 5
SCORE_KINDS = {"cp", "mate", "mate_given"}


class ResultEligibility(StrEnum):
    MISSING = "missing"
    ELIGIBLE = "eligible"
    STALE = "stale"


def canonical_fen(value: str) -> str:
    """Return a strict canonical six-field FEN or reject it."""

    if not isinstance(value, str) or value != value.strip() or " ".join(value.split()) != value:
        raise AnalysisValidationError("FEN must have canonical single-space formatting")
    if len(value.split(" ")) != 6:
        raise AnalysisValidationError("analysis identity requires an exact six-field FEN")
    try:
        board = chess.Board(value)
    except (TypeError, ValueError) as error:
        raise AnalysisValidationError("FEN is invalid") from error
    if not board.is_valid() or board.fen(en_passant="fen") != value:
        raise AnalysisValidationError("FEN is not canonical or is not a valid position")
    return value


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as error:
        raise AnalysisValidationError("settings must be JSON-serializable") from error


@dataclass(frozen=True)
class AnalysisProfile:
    profile_id: str
    engine_binary_sha256: str
    engine_name: str
    engine_version: str
    node_budget: int
    multipv: int = MAX_CANDIDATES
    threads: int = 1
    hash_mb: int = 128
    uci_show_wdl: bool = True
    options: Mapping[str, str | int | bool | None] = field(default_factory=dict)
    contract_version: int = PROFILE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.profile_id or not self.engine_name or not self.engine_version:
            raise AnalysisValidationError("profile and engine identity fields are required")
        checksum = self.engine_binary_sha256.lower()
        if len(checksum) != 64 or any(char not in "0123456789abcdef" for char in checksum):
            raise AnalysisValidationError(
                "engine binary SHA-256 must be 64 lowercase hex characters"
            )
        if self.contract_version != PROFILE_CONTRACT_VERSION:
            raise AnalysisValidationError("unsupported profile contract version")
        if self.node_budget < 1 or self.multipv != MAX_CANDIDATES:
            raise AnalysisValidationError("profile requires positive fixed nodes and MultiPV 5")
        if self.threads != 1 or self.hash_mb != 128 or self.uci_show_wdl is not True:
            raise AnalysisValidationError("profile requires Threads 1, Hash 128, and engine WDL")
        canonical_options = json.loads(_canonical_json(dict(self.options)))
        if not isinstance(canonical_options, dict):
            raise AnalysisValidationError("profile options must be an object")
        object.__setattr__(self, "engine_binary_sha256", checksum)
        object.__setattr__(self, "options", MappingProxyType(canonical_options))

    @property
    def settings_json(self) -> str:
        return _canonical_json(
            {
                "contract_version": self.contract_version,
                "engine": {
                    "binary_sha256": self.engine_binary_sha256,
                    "name": self.engine_name,
                    "version": self.engine_version,
                },
                "hash_mb": self.hash_mb,
                "multipv": self.multipv,
                "node_budget": self.node_budget,
                "options": dict(self.options),
                "profile_id": self.profile_id,
                "threads": self.threads,
                "uci_show_wdl": self.uci_show_wdl,
            }
        )

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.settings_json.encode("ascii")).hexdigest()


@dataclass(frozen=True)
class AnalysisCandidate:
    rank: int
    score_kind: str
    score_value: int
    wdl_wins: int
    wdl_draws: int
    wdl_losses: int
    pv_uci: tuple[str, ...]
    depth: int
    seldepth: int
    nodes: int
    engine_time_ms: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.rank, bool)
            or not isinstance(self.rank, int)
            or not 1 <= self.rank <= MAX_CANDIDATES
            or self.score_kind not in SCORE_KINDS
            or isinstance(self.score_value, bool)
            or not isinstance(self.score_value, int)
        ):
            raise AnalysisValidationError("candidate score must be typed cp, mate, or mate_given")
        if self.score_kind == "mate_given" and self.score_value != 0:
            raise AnalysisValidationError("mate_given score value must be zero")
        wdl = (self.wdl_wins, self.wdl_draws, self.wdl_losses)
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in wdl):
            raise AnalysisValidationError("WDL values must be non-negative integer permille")
        if sum(wdl) != 1000:
            raise AnalysisValidationError("WDL values must sum to 1000")
        proof = (self.depth, self.seldepth, self.nodes, self.engine_time_ms)
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in proof
        ):
            raise AnalysisValidationError("candidate proof metadata must be non-negative integers")
        if not isinstance(self.pv_uci, tuple) or self.nodes < 1 or not self.pv_uci:
            raise AnalysisValidationError("nonterminal candidates require nodes and a complete PV")


@dataclass(frozen=True)
class AnalysisResult:
    fen: str
    profile: AnalysisProfile
    candidates: tuple[AnalysisCandidate, ...]
    completed_at: str
    wall_time_ms: int
    terminal_kind: str | None = None

    def __post_init__(self) -> None:
        fen = canonical_fen(self.fen)
        try:
            completed = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as error:
            raise AnalysisValidationError(
                "completion time must be an ISO-8601 timestamp"
            ) from error
        if (
            completed.tzinfo is None
            or isinstance(self.wall_time_ms, bool)
            or not isinstance(self.wall_time_ms, int)
            or self.wall_time_ms < 0
        ):
            raise AnalysisValidationError(
                "completion time and non-negative wall timing are required"
            )
        if not isinstance(self.candidates, tuple):
            raise AnalysisValidationError("candidates must be an immutable complete tuple")
        board = chess.Board(fen)
        outcome = board.outcome(claim_draw=True)
        expected_terminal = outcome.termination.name.lower() if outcome is not None else None
        if self.terminal_kind != expected_terminal:
            raise AnalysisValidationError(
                "terminal classification must exactly match the FEN outcome"
            )
        legal_count = board.legal_moves.count()
        expected_candidates = 0 if expected_terminal else min(MAX_CANDIDATES, legal_count)
        if len(self.candidates) != expected_candidates:
            raise AnalysisValidationError("candidate count is incomplete for the legal root moves")
        if [candidate.rank for candidate in self.candidates] != list(
            range(1, expected_candidates + 1)
        ):
            raise AnalysisValidationError("candidate ranks must be contiguous from one")
        first_moves: set[str] = set()
        for candidate in self.candidates:
            replay = board.copy(stack=False)
            for index, uci in enumerate(candidate.pv_uci):
                try:
                    move = chess.Move.from_uci(uci)
                except ValueError as error:
                    raise AnalysisValidationError("PV contains malformed UCI") from error
                if move not in replay.legal_moves:
                    raise AnalysisValidationError(
                        "PV contains an illegal or incomplete continuation"
                    )
                if index == 0:
                    if uci in first_moves:
                        raise AnalysisValidationError("candidate root moves must be distinct")
                    first_moves.add(uci)
                replay.push(move)
