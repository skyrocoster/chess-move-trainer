"""Selection metadata and safety rules for ``sg test``."""

from __future__ import annotations

from dataclasses import dataclass, field

from tools.dev.test.discovery import TestCase


class SelectionError(RuntimeError):
    """Raised when a selection matches no unit or an unsafe unit."""


@dataclass(frozen=True)
class Command:
    """One bounded runner invocation for a resolved selection."""

    label: str
    backend: str
    args: tuple[str, ...]
    timeout: float
    layer: str = ""
    cwd: str = "."
    env: dict[str, str] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    allow_failure: bool = False
    speed: str = ""
    # Non-empty when this command runs only part of its backend's selection
    # (a length-limited chunk); the runner reports just those selectors.
    selectors: tuple[str, ...] = ()


def resolve(
    *,
    cases: list[TestCase],
    test_id: str = "",
    domain: str = "",
    layer: str = "",
) -> list[TestCase]:
    """Return exactly the requested units, or raise a visible error."""
    if test_id:
        matches = [case for case in cases if case.id == test_id]
        if not matches and "::" not in test_id:
            matches = [case for case in cases if case.id.split("::", 1)[0] == test_id]
        if matches:
            return matches
        import difflib

        close = difflib.get_close_matches(test_id, [case.id for case in cases], n=5, cutoff=0.5)
        hint = f" Close matches: {', '.join(close)}" if close else ""
        raise SelectionError(f"No test matches --id {test_id!r}.{hint}")
    if not domain and not layer:
        raise SelectionError("Select tests with --id, or with --domain and/or --layer.")
    selected = [
        case
        for case in cases
        if (not domain or _domain_matches(case, domain)) and (not layer or case.layer == layer)
    ]
    if not selected:
        available = sorted({case.domain for case in cases})
        raise SelectionError(
            f"No tests match domain={domain!r} layer={layer!r}. Domains: {', '.join(available)}"
        )
    return selected


def _domain_matches(case: TestCase, domain: str) -> bool:
    if case.domain == domain:
        return True
    return bool(case.subdomain) and f"{case.domain}.{case.subdomain}" == domain


def preflight(cases: list[TestCase], *, allow_real_data: bool) -> None:
    """Refuse unsafe selections before starting any process."""
    real_data = [case for case in cases if case.real_data]
    if real_data and not allow_real_data:
        listing = ", ".join(case.id for case in real_data[:5])
        raise SelectionError(
            "This selection reads the live database through opt-in real-data tests"
            f" ({listing}). Run it only through `sg test profiles real-data`."
        )
    unavailable = [case for case in cases if not case.available]
    if unavailable:
        listing = ", ".join(case.id for case in unavailable[:5])
        raise SelectionError(f"Discovery is unavailable for {listing}.")


def describe(cases: list[TestCase]) -> str:
    """Return a short human summary of a selection."""
    from collections import Counter

    by_backend = Counter(case.backend for case in cases)
    parts = ", ".join(f"{backend}: {count}" for backend, count in sorted(by_backend.items()))
    fixtures = sorted({case.fixture for case in cases})
    return f"{len(cases)} unit(s) [{parts}]; fixtures: {', '.join(fixtures)}"
