"""Errors raised while serving move response distributions."""

from __future__ import annotations


class MoveResponseDistributionValidationError(ValueError):
    """The request violates the public move response distribution contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class MoveResponseDistributionUnavailableError(RuntimeError):
    """The accepted recurrence data is unavailable or internally inconsistent."""
