"""Typed errors for the MP-10 browser-evaluation service boundary."""

from __future__ import annotations


class EvaluationSchemaError(RuntimeError):
    """The independently versioned evaluation queue schema is absent or incompatible."""


class EvaluationValidationError(ValueError):
    """An evaluation request violates strict validation or the bounded size limits."""


class EvaluationQueueError(RuntimeError):
    """A queue state-machine transition is invalid for the current state."""


class EvaluationLockError(RuntimeError):
    """The evaluation worker session could not acquire the shared analysis lock."""
