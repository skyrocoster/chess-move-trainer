"""Benchmark dataclasses, errors, and defaults."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Protocol

from ..analysis import AnalysisQuality
from ..positions import CanonicalPosition, canonicalize_fen
from .configuration import (
    CONFIGURATION_VERSION,
    MULTI_PV,
    STOCKFISH_NAME,
    STOCKFISH_VERSION,
    StockfishProfile,
)
from .engine import ANALYSIS_WATCHDOG_SECONDS, SearchMetrics, StockfishEngine

BENCHMARK_FORMAT_VERSION: Final[int] = 1

DEFAULT_NODE_BUDGETS: Final[tuple[int, ...]] = (
    100_000,
    200_000,
    400_000,
    800_000,
    1_600_000,
    3_200_000,
    6_400_000,
)
DEFAULT_THREAD_COUNTS: Final[tuple[int, ...]] = (1, 2, 4, 6)
DEFAULT_HASH_SIZES_MB: Final[tuple[int, ...]] = (64, 256, 1024)
DEFAULT_REPETITIONS: Final[int] = 3
DEFAULT_SHUFFLE_SEED: Final[int] = 0
DEFAULT_ARTIFACT_WRITE_RETRIES: Final[int] = 3
_MAX_DIAGNOSTIC_LENGTH: Final[int] = 500


class BenchmarkError(RuntimeError):
    """Base class for bounded benchmark setup and execution failures."""


class BenchmarkInputError(BenchmarkError, ValueError):
    """The explicit input or matrix specification is invalid."""


class BenchmarkCompatibilityError(BenchmarkError):
    """Existing output state does not belong to the requested benchmark."""


class BenchmarkPersistenceError(BenchmarkError):
    """An artifact could not be persisted safely after bounded retries."""

    exit_code = 1


class BenchmarkInterrupted(BenchmarkError):
    """Reserved internal category for a controlled benchmark interruption."""

    exit_code = 130


@dataclass(frozen=True, slots=True)
class BenchmarkPosition:
    """One validated position from the explicit benchmark input file."""

    position_id: int
    fen: str

    def __post_init__(self) -> None:
        if type(self.position_id) is not int or self.position_id < 1:
            raise BenchmarkInputError("benchmark position id must be a positive integer")
        if not isinstance(self.fen, str):
            raise BenchmarkInputError("benchmark position FEN must be a string")
        try:
            canonicalize_fen(self.fen)
        except ValueError as error:
            raise BenchmarkInputError(
                f"benchmark position {self.position_id} has an invalid FEN"
            ) from error

    @property
    def canonical(self) -> CanonicalPosition:
        """Return the canonical four-field position consumed by the engine."""

        return canonicalize_fen(self.fen)


@dataclass(frozen=True, slots=True)
class BenchmarkJob:
    """A stable identity for one position/profile/round analysis."""

    position: BenchmarkPosition
    nodes: int
    threads: int
    hash_mb: int
    round_number: int

    @property
    def job_id(self) -> str:
        return (
            f"r{self.round_number}-p{self.position.position_id}-"
            f"n{self.nodes}-t{self.threads}-h{self.hash_mb}"
        )

    @property
    def profile(self) -> StockfishProfile:
        return StockfishProfile(
            AnalysisQuality.TOOL,
            self.nodes,
            threads=self.threads,
            hash_mb=self.hash_mb,
            multipv=MULTI_PV,
            configuration_version=CONFIGURATION_VERSION,
        )


@dataclass(frozen=True, slots=True)
class BenchmarkSpec:
    """Validated, deterministic matrix inputs for one benchmark run."""

    positions: tuple[BenchmarkPosition, ...]
    node_budgets: tuple[int, ...] = DEFAULT_NODE_BUDGETS
    thread_counts: tuple[int, ...] = DEFAULT_THREAD_COUNTS
    hash_sizes_mb: tuple[int, ...] = DEFAULT_HASH_SIZES_MB
    repetitions: int = DEFAULT_REPETITIONS
    shuffle_seed: int = DEFAULT_SHUFFLE_SEED
    multipv: int = MULTI_PV
    watchdog_seconds: float = ANALYSIS_WATCHDOG_SECONDS

    def __post_init__(self) -> None:
        positions = tuple(self.positions)
        if not positions:
            raise BenchmarkInputError("benchmark input must contain at least one position")
        if any(not isinstance(position, BenchmarkPosition) for position in positions):
            raise BenchmarkInputError(
                "benchmark positions must be validated BenchmarkPosition values"
            )
        if len({position.position_id for position in positions}) != len(positions):
            raise BenchmarkInputError("benchmark position ids must be unique")
        object.__setattr__(
            self, "positions", tuple(sorted(positions, key=lambda item: item.position_id))
        )
        for field_name in ("node_budgets", "thread_counts", "hash_sizes_mb"):
            values = _positive_int_tuple(getattr(self, field_name), field_name)
            object.__setattr__(self, field_name, values)
        if type(self.repetitions) is not int or self.repetitions < 1:
            raise BenchmarkInputError("repetitions must be a positive integer")
        if type(self.shuffle_seed) is not int:
            raise BenchmarkInputError("shuffle seed must be an integer")
        if self.multipv != MULTI_PV:
            raise BenchmarkInputError("MultiPV is fixed at 5 for the supported benchmark")
        if isinstance(self.watchdog_seconds, bool):
            raise BenchmarkInputError("watchdog must be finite and greater than zero")
        try:
            watchdog = float(self.watchdog_seconds)
        except (TypeError, ValueError) as error:
            raise BenchmarkInputError("watchdog must be finite and greater than zero") from error
        if not (0 < watchdog < float("inf")):
            raise BenchmarkInputError("watchdog must be finite and greater than zero")
        object.__setattr__(self, "watchdog_seconds", watchdog)

    @property
    def total_jobs(self) -> int:
        return (
            len(self.positions)
            * len(self.node_budgets)
            * len(self.thread_counts)
            * len(self.hash_sizes_mb)
            * self.repetitions
        )

    def jobs(self) -> tuple[BenchmarkJob, ...]:
        """Enumerate every job once in the recorded deterministic order."""

        rng = random.Random(self.shuffle_seed)
        blocks = [
            (threads, hash_mb) for threads in self.thread_counts for hash_mb in self.hash_sizes_mb
        ]
        rng.shuffle(blocks)
        ordered: list[BenchmarkJob] = []
        for threads, hash_mb in blocks:
            block_jobs = [
                BenchmarkJob(position, nodes, threads, hash_mb, round_number)
                for round_number in range(1, self.repetitions + 1)
                for nodes in self.node_budgets
                for position in self.positions
            ]
            rng.shuffle(block_jobs)
            ordered.extend(block_jobs)
        return tuple(ordered)

    def as_manifest_dict(self) -> dict[str, Any]:
        return {
            "format_version": BENCHMARK_FORMAT_VERSION,
            "matrix": {
                "node_budgets": list(self.node_budgets),
                "thread_counts": list(self.thread_counts),
                "hash_sizes_mb": list(self.hash_sizes_mb),
                "repetitions": self.repetitions,
                "shuffle_seed": self.shuffle_seed,
                "multipv": self.multipv,
                "watchdog_seconds": self.watchdog_seconds,
            },
            "positions": [
                {"position_id": position.position_id, "fen": position.fen}
                for position in self.positions
            ],
            "total_jobs": self.total_jobs,
        }


BenchmarkSpecification = BenchmarkSpec


@dataclass(frozen=True, slots=True)
class BenchmarkOutcome:
    """Observable result of one bounded benchmark invocation."""

    artifact_dir: Path
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    attempts: int
    complete: bool
    interrupted: bool = False
    resumed: bool = False

    @property
    def exit_code(self) -> int:
        if self.interrupted:
            return 130
        return 0 if self.complete else 1


def _positive_int_tuple(values, label):
    normalized = tuple(values)
    if not normalized or any(type(value) is not int or value <= 0 for value in normalized):
        raise BenchmarkInputError(f"{label} must contain positive integers")
    if len(set(normalized)) != len(normalized):
        raise BenchmarkInputError(f"{label} must not contain duplicates")
    return normalized
