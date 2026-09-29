"""Read-only live-database probes for the health endpoint.

The status page shows the whole-database analysis backlog and the most recent
game date. Both reads are best-effort: a missing, locked, or schema-incompatible
database must never make the backend itself look unhealthy, so every failure
resolves to ``None`` instead of raising.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

DB_PROBE_TIMEOUT_SECONDS = 1.5
_READ_ONLY_MMAP_SIZE_BYTES = 256 * 1024 * 1024


@dataclass(frozen=True)
class AnalysisBacklog:
    """Whole-database count of positions and their analysis progress."""

    positions: int
    analyzed: int
    queued: int
    running: int
    remaining: int


@dataclass(frozen=True)
class DatabaseHealth:
    """Analysis backlog plus the newest game timestamp."""

    analysis: AnalysisBacklog
    last_game_at: str | None


def _read_only_uri(database_path: str | Path) -> str:
    return f"file:{Path(database_path).resolve().as_posix()}?mode=ro"


def read_database_health(database_path: str | Path) -> DatabaseHealth | None:
    """Return the analysis backlog and last game date, or ``None`` if unreadable."""

    try:
        connection = sqlite3.connect(
            _read_only_uri(database_path),
            uri=True,
            timeout=DB_PROBE_TIMEOUT_SECONDS,
        )
    except (sqlite3.Error, OSError):
        return None

    try:
        connection.execute(f"PRAGMA mmap_size = {_READ_ONLY_MMAP_SIZE_BYTES}")
        row = connection.execute(
            "SELECT "
            "(SELECT COUNT(*) FROM derived_position), "
            "(SELECT COUNT(*) FROM derived_analysis_result), "
            "(SELECT COUNT(*) FROM derived_analysis_queue WHERE daq_state = 'queued'), "
            "(SELECT COUNT(*) FROM derived_analysis_queue WHERE daq_state = 'running'), "
            "(SELECT MAX(dg_started_at_utc) FROM datasource_game)"
        ).fetchone()
    except sqlite3.Error:
        return None
    finally:
        connection.close()

    if row is None:
        return None

    positions = int(row[0] or 0)
    analyzed = int(row[1] or 0)
    queued = int(row[2] or 0)
    running = int(row[3] or 0)
    return DatabaseHealth(
        analysis=AnalysisBacklog(
            positions=positions,
            analyzed=analyzed,
            queued=queued,
            running=running,
            remaining=max(0, positions - analyzed - queued - running),
        ),
        last_game_at=None if row[4] is None else str(row[4]),
    )


__all__ = ["AnalysisBacklog", "DatabaseHealth", "read_database_health"]
