"""Errors raised while serving neutral position context."""

from __future__ import annotations


class PositionContextValidationError(ValueError):
    """The request violates the public position-context contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class PositionContextUnavailableError(RuntimeError):
    """The existing database or its supported recurrence projection is unavailable."""
