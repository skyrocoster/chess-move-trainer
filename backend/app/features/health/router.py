from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_rebuilt_database_path

from .database_probe import read_database_health
from .docker_probe import probe_workers
from .schemas import AnalysisHealthResponse, HealthResponse, WorkerHealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse, operation_id="getHealth")
def health(
    database_path: Annotated[Path, Depends(get_rebuilt_database_path)],
) -> HealthResponse:
    """Report backend liveness plus best-effort analysis and per-worker status."""

    database = read_database_health(database_path)
    analysis = (
        None
        if database is None
        else AnalysisHealthResponse(
            positions=database.analysis.positions,
            analyzed=database.analysis.analyzed,
            queued=database.analysis.queued,
            running=database.analysis.running,
            remaining=database.analysis.remaining,
        )
    )
    workers = probe_workers()
    return HealthResponse(
        status="ok",
        analysis=analysis,
        workers=(
            None
            if workers is None
            else [
                WorkerHealthResponse(
                    service=worker.service,
                    index=worker.index,
                    running=worker.running,
                )
                for worker in workers
            ]
        ),
        last_game_at=None if database is None else database.last_game_at,
    )
