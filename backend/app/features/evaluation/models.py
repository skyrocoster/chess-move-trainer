"""Value objects for the durable evaluation queue and evaluation service."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.features.analysis import AnalysisResult, ResultEligibility

QUEUE_STATES = ("queued", "running", "done", "failed")


@dataclass(frozen=True)
class EvaluationQueueItem:
    fen: str
    state: str
    position: int
    attempts: int
    enqueued_at: str
    started_at: str | None
    finished_at: str | None
    last_error_code: str | None
    last_error_details: str | None


@dataclass(frozen=True)
class InspectResult:
    """A read-only view of one position; never triggers computation."""

    fen: str
    eligibility: ResultEligibility
    result: AnalysisResult | None
    item: EvaluationQueueItem | None
    terminal: bool


@dataclass(frozen=True)
class RequestResult:
    """The outcome of one deliberate Analyze, Update, or Retry action."""

    fen: str
    outcome: str
    eligibility: ResultEligibility
    item: EvaluationQueueItem | None


@dataclass(frozen=True)
class SessionResult:
    """One bounded worker session over the durable queue."""

    completed: int
    failed: int
    requeued: int
    left_queued: int
