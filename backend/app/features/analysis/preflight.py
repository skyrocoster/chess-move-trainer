"""Strictly read-only corpus-wide selection and resource projection."""

from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .models import AnalysisProfile
from .selection import SelectionReport, select_all_positions

MAX_WORKERS = 6
DEFAULT_WATCHDOG_SECONDS = 30.0
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BENCHMARK_REPORT = (
    REPOSITORY_ROOT / "docs" / "benchmarks" / "mp09-stockfish-18-node-budget-v2.json"
)


@dataclass(frozen=True)
class ProjectionBasis:
    source: Path
    corpus_exact_fens: int
    mean_seconds_per_fen: float
    mean_payload_bytes: float


@dataclass(frozen=True)
class CorpusPreflight:
    database: Path
    report: SelectionReport
    profile: AnalysisProfile
    workers: int
    watchdog_seconds: float
    total_hash_memory_mib: int
    projected_duration_seconds: float
    projected_pending_duration_seconds: float
    projected_disk_bytes: int
    projected_pending_disk_bytes: int
    projection_basis: ProjectionBasis

    @property
    def lock_path(self) -> Path:
        return Path(f"{self.database.resolve()}.analysis.lock")

    def as_dict(self) -> dict[str, object]:
        return {
            "database": str(self.database),
            **self.report.as_dict(),
            "active_engine": {
                "name": self.profile.engine_name,
                "version": self.profile.engine_version,
                "binary_sha256": self.profile.engine_binary_sha256,
            },
            "active_profile": self.profile.profile_id,
            "active_settings": json.loads(self.profile.settings_json),
            "workers": self.workers,
            "total_hash_memory_mib": self.total_hash_memory_mib,
            "disk_projection": {
                "bytes": self.projected_disk_bytes,
                "mib": self.projected_disk_bytes / (1024 * 1024),
                "pending_bytes": self.projected_pending_disk_bytes,
                "pending_mib": self.projected_pending_disk_bytes / (1024 * 1024),
            },
            "projected_duration": {
                "seconds": self.projected_duration_seconds,
                "hours": self.projected_duration_seconds / 3600,
                "pending_seconds": self.projected_pending_duration_seconds,
                "pending_hours": self.projected_pending_duration_seconds / 3600,
            },
            "watchdog_seconds": self.watchdog_seconds,
            "lock": {
                "path": str(self.lock_path),
                "implication": (
                    "a confirmed corpus run acquires one top-level lock; this preflight does not "
                    "create or acquire it"
                ),
            },
            "projection_basis": {
                "source": str(self.projection_basis.source),
                "corpus_exact_fens": self.projection_basis.corpus_exact_fens,
                "mean_seconds_per_fen": self.projection_basis.mean_seconds_per_fen,
                "mean_payload_bytes": self.projection_basis.mean_payload_bytes,
            },
        }


def load_projection_basis(path: Path = DEFAULT_BENCHMARK_REPORT) -> ProjectionBasis:
    """Load and validate the accepted v2 benchmark's immutable projection evidence."""

    try:
        report = json.loads(path.read_text(encoding="ascii"))
        projections = report["projections"]
        corpus_count = int(report["corpus"]["eligible_exact_fen_count"])
        one_worker_seconds = float(projections["one_worker_seconds"])
        mean_payload_bytes = float(projections["mean_payload_bytes"])
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(f"accepted benchmark projection is unavailable: {error}") from error
    if (
        report.get("status") != "qualified"
        or report.get("qualification", {}).get("selected_node_budget") != 200_000
        or corpus_count < 1
        or not math.isfinite(one_worker_seconds)
        or one_worker_seconds <= 0
        or not math.isfinite(mean_payload_bytes)
        or mean_payload_bytes <= 0
    ):
        raise ValueError("accepted benchmark projection is not a qualified 200,000-node report")
    return ProjectionBasis(
        path,
        corpus_count,
        one_worker_seconds / corpus_count,
        mean_payload_bytes,
    )


def build_preflight(
    connection: sqlite3.Connection,
    database: Path,
    profile: AnalysisProfile,
    *,
    workers: int,
    watchdog_seconds: float = DEFAULT_WATCHDOG_SECONDS,
    projection_basis: ProjectionBasis | None = None,
) -> CorpusPreflight:
    """Inspect the corpus and analysis rows without opening a writer transaction."""

    if not 1 <= workers <= MAX_WORKERS:
        raise ValueError(f"workers must be between 1 and {MAX_WORKERS}")
    if watchdog_seconds <= 0:
        raise ValueError("watchdog must be positive")
    report = select_all_positions(connection, profile)
    basis = projection_basis or load_projection_basis()
    total_positions = len(report.positions)
    pending_positions = len(report.positions_to_process)
    seconds = basis.mean_seconds_per_fen * total_positions / workers
    pending_seconds = basis.mean_seconds_per_fen * pending_positions / workers
    disk_bytes = round(basis.mean_payload_bytes * total_positions)
    pending_disk_bytes = round(basis.mean_payload_bytes * pending_positions)
    return CorpusPreflight(
        database=database,
        report=report,
        profile=profile,
        workers=workers,
        watchdog_seconds=watchdog_seconds,
        total_hash_memory_mib=profile.hash_mb * workers,
        projected_duration_seconds=seconds,
        projected_pending_duration_seconds=pending_seconds,
        projected_disk_bytes=disk_bytes,
        projected_pending_disk_bytes=pending_disk_bytes,
        projection_basis=basis,
    )


def run_read_only_preflight(
    database: Path,
    profile: AnalysisProfile,
    *,
    workers: int,
    watchdog_seconds: float = DEFAULT_WATCHDOG_SECONDS,
    projection_basis: ProjectionBasis | None = None,
) -> CorpusPreflight:
    """Open a database with SQLite's read-only immutable URI and perform no locking or writes."""

    if not database.is_file():
        raise ValueError(f"database does not exist: {database}")
    uri = f"file:{database.resolve().as_posix()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as error:
        raise ValueError(f"database cannot be opened read-only: {database}") from error
    try:
        return build_preflight(
            connection,
            database,
            profile,
            workers=workers,
            watchdog_seconds=watchdog_seconds,
            projection_basis=projection_basis,
        )
    finally:
        connection.close()
