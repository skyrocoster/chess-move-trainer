"""Dependency-neutral value validation for database packages."""

from __future__ import annotations

import re
from datetime import UTC, datetime

_RFC3339_PATTERN = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    r"[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})\Z"
)


def normalize_timestamp_value(value: str | datetime | None, field_name: str) -> str:
    """Normalize one RFC3339 bound to UTC with microseconds and a ``Z`` suffix."""

    if isinstance(value, datetime):
        parsed = value
    elif type(value) is str and _RFC3339_PATTERN.fullmatch(value):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError(f"{field_name} must be RFC3339 UTC") from error
    else:
        raise ValueError(f"{field_name} must be RFC3339 UTC")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    return parsed.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def require_text(value: object, field_name: str) -> str:
    """Return a non-empty string or raise a field-named ``ValueError``."""

    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def require_int(value: object, field_name: str) -> int:
    """Return an exact integer or raise a field-named ``ValueError``."""

    if type(value) is not int:
        raise ValueError(f"{field_name} must be an integer")
    return value


def require_positive_int(value: object, field_name: str) -> int:
    """Return a positive integer or raise a field-named ``ValueError``."""

    if type(value) is not int or value < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def require_non_negative_int(value: object, field_name: str) -> int:
    """Return a non-negative integer or raise a field-named ``ValueError``."""

    if type(value) is not int or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def optional_text(value: object) -> str | None:
    """Return an optional string or raise a generic ``ValueError``."""

    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional text value is malformed")
    return value


def optional_int(value: object) -> int | None:
    """Return an optional integer or raise a generic ``ValueError``."""

    if value is None:
        return None
    if type(value) is not int:
        raise ValueError("optional integer value is malformed")
    return value


def comparable_timestamp(value: object) -> str | None:
    """Return the UTC-normalized form of a stored timestamp, or ``None``."""

    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    try:
        return parsed.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    except (OverflowError, ValueError):
        return None


__all__ = [
    "comparable_timestamp",
    "normalize_timestamp_value",
    "optional_int",
    "optional_text",
    "require_int",
    "require_non_negative_int",
    "require_positive_int",
    "require_text",
]
