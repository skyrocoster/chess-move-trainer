"""Stable public keys for persisted opening labels."""

from __future__ import annotations

import re

_ECO_PATTERN = re.compile(r"[A-E][0-9]{2}\Z")


class OpeningKeyError(ValueError):
    """Raised when an opening API key cannot be represented safely."""


def opening_api_key(eco: str, name: str) -> str:
    """Return the stable ``ECO:Name`` key used by clean API capabilities."""

    if type(eco) is not str or _ECO_PATTERN.fullmatch(eco) is None:
        raise OpeningKeyError("eco must be an uppercase ECO code from A00 through E99")
    if type(name) is not str or not name:
        raise OpeningKeyError("name must be a non-empty string")
    return f"{eco}:{name}"


def parse_opening_api_key(value: str) -> tuple[str, str]:
    """Validate and split one stable ``ECO:Name`` key."""

    if type(value) is not str:
        raise OpeningKeyError("opening_key must be a string formatted as ECO:Name")
    eco, separator, name = value.partition(":")
    if not separator:
        raise OpeningKeyError("opening_key must be formatted as ECO:Name")
    try:
        expected = opening_api_key(eco, name)
    except OpeningKeyError as error:
        raise OpeningKeyError("opening_key must be formatted as ECO:Name") from error
    if expected != value:
        raise OpeningKeyError("opening_key must be formatted as ECO:Name")
    return eco, name


__all__ = ["OpeningKeyError", "opening_api_key", "parse_opening_api_key"]
