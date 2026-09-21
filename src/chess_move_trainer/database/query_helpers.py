"""Small, dependency-neutral helpers for bounded database queries."""

from __future__ import annotations

from collections.abc import Iterable


def chunk_sorted_ids(values: Iterable[int], size: int = 500) -> list[list[int]]:
    """Return sorted unique integer identifiers in non-empty bounded chunks."""

    if type(size) is not int or size < 1:
        raise ValueError("chunk size must be a positive integer")
    ordered = sorted(set(values))
    return [ordered[index : index + size] for index in range(0, len(ordered), size)]


__all__ = ["chunk_sorted_ids"]
