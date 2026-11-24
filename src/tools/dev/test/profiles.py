"""Approved, bounded test profiles for ``sg test``.

Profiles select from catalogue-owned units; they never run production builds
or start development services implicitly. ``full`` and ``e2e`` need the
development services (see docs/DEVELOPMENT_SERVICES.md); ``real-data`` is an
explicit opt-in that reads the live database through the repository's env-gated
real tests.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.dev.test.discovery import TestCase

# Soft total budgets. These warn and are persisted; the hard per-command
# deadlines in tools/dev/test/backends.py remain the enforcement mechanism.
PROFILE_BUDGETS = {
    "quick": 600.0,
    "smoke": 120.0,
    "full": 3600.0,
    "e2e": 900.0,
    "real-data": 900.0,
}

_SMOKE_SOURCES = {
    "backend/tests/features/health/test_health.py",
    "frontend/src/features/status/StatusView.test.tsx",
    "frontend/src/features/status/StatusPage.test.tsx",
    "tests/database/test_connection.py",
}


@dataclass(frozen=True)
class Profile:
    """One named, bounded test suite."""

    name: str
    description: str
    budget_seconds: float
    allow_real_data: bool = False


PROFILES: dict[str, Profile] = {
    "quick": Profile(
        name="quick",
        description=(
            "Offline default: every Python test and the frontend unit project;"
            " no services, no Playwright, no real-data tests."
        ),
        budget_seconds=PROFILE_BUDGETS["quick"],
    ),
    "smoke": Profile(
        name="smoke",
        description="A small offline cross-section: health API, status page and database connection.",
        budget_seconds=PROFILE_BUDGETS["smoke"],
    ),
    "full": Profile(
        name="full",
        description=(
            "quick plus the real-backend API client tests and every Playwright spec"
            " (needs healthy development services)."
        ),
        budget_seconds=PROFILE_BUDGETS["full"],
    ),
    "e2e": Profile(
        name="e2e",
        description="Explicit Playwright browser suite against the live development services.",
        budget_seconds=PROFILE_BUDGETS["e2e"],
    ),
    "real-data": Profile(
        name="real-data",
        description=(
            "Explicit opt-in: env-gated real-database and real-benchmark tests"
            " (reads the live database)."
        ),
        budget_seconds=PROFILE_BUDGETS["real-data"],
        allow_real_data=True,
    ),
}


def select(cases: list[TestCase], name: str) -> list[TestCase]:
    """Return the discovered units belonging to one approved profile."""
    try:
        predicate = _PREDICATES[name]
    except KeyError:
        raise KeyError(f"unknown test profile {name!r}") from None
    return [case for case in cases if predicate(case)]


def _quick(case: TestCase) -> bool:
    return case.layer in ("backend", "frontend") and not case.real_data


def _smoke(case: TestCase) -> bool:
    return case.source in _SMOKE_SOURCES


def _full(case: TestCase) -> bool:
    return _quick(case) or case.layer in ("frontend-api", "e2e")


def _e2e(case: TestCase) -> bool:
    return case.layer == "e2e"


def _real_data(case: TestCase) -> bool:
    return case.real_data


_PREDICATES = {
    "quick": _quick,
    "smoke": _smoke,
    "full": _full,
    "e2e": _e2e,
    "real-data": _real_data,
}
