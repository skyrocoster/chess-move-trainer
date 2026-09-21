"""Blunder discovery error types."""

from __future__ import annotations


class BlunderError(Exception):
    """Base class for bounded blunder-discovery failures."""


class BlunderValidationError(BlunderError, ValueError):
    """Raised when a blunder query or policy value is invalid."""


class BlunderSchemaError(BlunderError, RuntimeError):
    """Raised when the selected database is not the exact supported schema."""


class BlunderStorageError(BlunderError, RuntimeError):
    """Raised when a compatible blunder database cannot be read safely."""
