"""A resumable, output-contained Stockfish benchmark service.

Thin compatibility shim. Implementation lives in benchmark_models,
benchmark_artifacts, benchmark_runner, and benchmark_io.
"""

from __future__ import annotations

from .benchmark_artifacts import (
    ArtifactWriter,
    AtomicArtifactWriter,
)
from .benchmark_io import (
    load_positions,
    run_benchmark,
)
from .benchmark_models import (
    BENCHMARK_FORMAT_VERSION,
    DEFAULT_ARTIFACT_WRITE_RETRIES,
    DEFAULT_HASH_SIZES_MB,
    DEFAULT_NODE_BUDGETS,
    DEFAULT_REPETITIONS,
    DEFAULT_SHUFFLE_SEED,
    DEFAULT_THREAD_COUNTS,
    BenchmarkCompatibilityError,
    BenchmarkError,
    BenchmarkInputError,
    BenchmarkInterrupted,
    BenchmarkJob,
    BenchmarkOutcome,
    BenchmarkPersistenceError,
    BenchmarkPosition,
    BenchmarkSpec,
    BenchmarkSpecification,
)
from .benchmark_runner import BenchmarkRunner

__all__ = [
    "BENCHMARK_FORMAT_VERSION",
    "DEFAULT_ARTIFACT_WRITE_RETRIES",
    "DEFAULT_HASH_SIZES_MB",
    "DEFAULT_NODE_BUDGETS",
    "DEFAULT_REPETITIONS",
    "DEFAULT_SHUFFLE_SEED",
    "DEFAULT_THREAD_COUNTS",
    "ArtifactWriter",
    "AtomicArtifactWriter",
    "BenchmarkCompatibilityError",
    "BenchmarkError",
    "BenchmarkInputError",
    "BenchmarkInterrupted",
    "BenchmarkJob",
    "BenchmarkOutcome",
    "BenchmarkPersistenceError",
    "BenchmarkPosition",
    "BenchmarkRunner",
    "BenchmarkSpec",
    "BenchmarkSpecification",
    "load_positions",
    "run_benchmark",
]
