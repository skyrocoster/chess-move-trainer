"""Errors raised while serving the opening Line Library."""

from __future__ import annotations


class OpeningLineLibraryValidationError(ValueError):
    """The request violates the opening Line Library contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class OpeningLineLibraryUnavailableError(RuntimeError):
    """The existing accepted opening data is missing or incompatible."""
