"""Benchmark loading and top-level invocation."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ..analysis import AnalysisQuality
from ..positions import CanonicalPosition, canonicalize_fen
from .benchmark_artifacts import _StoredAttempts
from .benchmark_models import (
    BENCHMARK_FORMAT_VERSION,
    DEFAULT_ARTIFACT_WRITE_RETRIES,
    DEFAULT_HASH_SIZES_MB,
    DEFAULT_NODE_BUDGETS,
    DEFAULT_REPETITIONS,
    DEFAULT_SHUFFLE_SEED,
    DEFAULT_THREAD_COUNTS,
    BenchmarkInputError,
    BenchmarkJob,
    BenchmarkPosition,
    BenchmarkSpec,
)
from .benchmark_records import (
    _checkpoint_payload,
    _current_job_sets,
    _expected_manifest,
    _job_fields,
    _load_attempts,
    _metrics_dict,
    _outcome,
    _profile_blocks,
    _records_for_job,
    _success_record,
    _summary_csv,
    _summary_payload,
    _validate_checkpoint,
)
from .engine import ANALYSIS_WATCHDOG_SECONDS, SearchMetrics, StockfishEngine
from .benchmark_runner import BenchmarkRunner
from .configuration import CONFIGURATION_VERSION, MULTI_PV, STOCKFISH_NAME, STOCKFISH_VERSION

def load_positions(position_input: str | Path) -> tuple[BenchmarkPosition, ...]:
    """Load and structurally validate explicit JSON benchmark positions."""

    path = Path(position_input)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise BenchmarkInputError(f"could not read benchmark position input: {path}") from error
    if not isinstance(payload, Mapping) or not isinstance(payload.get("positions"), list):
        raise BenchmarkInputError("benchmark position input must contain a positions list")
    positions: list[BenchmarkPosition] = []
    for item in payload["positions"]:
        if not isinstance(item, Mapping) or "id" not in item or "fen" not in item:
            raise BenchmarkInputError("each benchmark position needs id and fen")
        positions.append(BenchmarkPosition(position_id=item["id"], fen=item["fen"]))
    return tuple(sorted(positions, key=lambda position: position.position_id))


def run_benchmark(
    *,
    executable: str | Path,
    position_input: str | Path,
    output_dir: str | Path,
    node_budgets: Iterable[int] = DEFAULT_NODE_BUDGETS,
    thread_counts: Iterable[int] = DEFAULT_THREAD_COUNTS,
    hash_sizes_mb: Iterable[int] = DEFAULT_HASH_SIZES_MB,
    repetitions: int = DEFAULT_REPETITIONS,
    shuffle_seed: int = DEFAULT_SHUFFLE_SEED,
    watchdog_seconds: float = ANALYSIS_WATCHDOG_SECONDS,
    engine_factory: Callable[..., Any] | None = None,
    artifact_writer: ArtifactWriter | None = None,
    artifact_write_retries: int = DEFAULT_ARTIFACT_WRITE_RETRIES,
    retry_delay_seconds: float = 0.0,
    progress: Callable[[str], None] | None = None,
) -> BenchmarkOutcome:
    """Run one explicit matrix, resuming only compatible output state."""

    positions = load_positions(position_input)
    spec = BenchmarkSpec(
        positions=positions,
        node_budgets=tuple(node_budgets),
        thread_counts=tuple(thread_counts),
        hash_sizes_mb=tuple(hash_sizes_mb),
        repetitions=repetitions,
        shuffle_seed=shuffle_seed,
        watchdog_seconds=watchdog_seconds,
    )
    return BenchmarkRunner(
        spec,
        executable=executable,
        position_input=position_input,
        output_dir=output_dir,
        engine_factory=engine_factory,
        artifact_writer=artifact_writer,
        artifact_write_retries=artifact_write_retries,
        retry_delay_seconds=retry_delay_seconds,
        progress=progress,
    ).run()

