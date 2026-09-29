from typing import Literal

from pydantic import BaseModel, ConfigDict


class AnalysisHealthResponse(BaseModel):
    """Whole-database analysis backlog shown on the status page."""

    model_config = ConfigDict(extra="forbid")

    positions: int
    analyzed: int
    queued: int
    running: int
    remaining: int


class WorkerHealthResponse(BaseModel):
    """Observed state of one Docker analysis-worker container."""

    model_config = ConfigDict(extra="forbid")

    service: Literal["worker", "worker-six"]
    index: int
    running: bool


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    analysis: AnalysisHealthResponse | None
    workers: list[WorkerHealthResponse] | None
    last_game_at: str | None


__all__ = ["AnalysisHealthResponse", "HealthResponse", "WorkerHealthResponse"]
