"""Errors raised while serving the preferred-move API."""

from __future__ import annotations


class PreferredMoveValidationError(ValueError):
    """The request violates the public preferred-move contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class PreferredMovePositionNotFoundError(LookupError):
    """The valid four-field identity is not present in a game occurrence."""


class PreferredMoveUnavailableError(RuntimeError):
    """The existing database or its supported preferred-move schema is unavailable."""
