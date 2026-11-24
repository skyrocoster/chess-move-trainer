"""Paths and shared constants used by the ``sg`` developer CLI."""

from __future__ import annotations

import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPOSITORY_ROOT / "src"
BACKEND_DIR = REPOSITORY_ROOT / "backend"
FRONTEND_DIR = REPOSITORY_ROOT / "frontend"
E2E_DIR = REPOSITORY_ROOT / "tests" / "e2e"
CATALOG_PATH = REPOSITORY_ROOT / "tests" / "catalog" / "domains.toml"
BUILD_DIR = REPOSITORY_ROOT / "build"
TEST_RESULTS_DIR = BUILD_DIR / "test-results"
SCREENSHOTS_DIR = BUILD_DIR / "screenshots"
CACHE_DIR = BUILD_DIR / "cache"
COMPOSE_FILE = REPOSITORY_ROOT / "compose.yaml"
COMPOSE_PROJECT = "chess-move-trainer"

VENV_DIR = REPOSITORY_ROOT / ".venv"
VENV_PYTHON = VENV_DIR / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
SG_SCRIPT = VENV_DIR / ("Scripts/sg.exe" if sys.platform == "win32" else "bin/sg")
PYTHON = str(VENV_PYTHON if VENV_PYTHON.is_file() else Path(sys.executable))

# Services a user can target. "worker-six" belongs to the Compose profile of the same name.
SERVICE_NAMES = ("backend", "frontend", "datasette")
WORKER_SERVICE_NAMES = ("worker", "worker-six")
TARGET_SERVICE_NAMES = (*SERVICE_NAMES, *WORKER_SERVICE_NAMES)
WORKER_PROFILE = "worker-six"

LIVE_DATABASE_CONTAINER_PATH = "data/database/chess.db"

# Millisecond budgets, overridable through CHESS_START_UPDATE_BUDGET_MS, CHESS_DEV_SETUP_BUDGET_MS
# and CHESS_DEV_PROBE_BUDGET_MS.
DEFAULT_UPDATE_BUDGET_MS = 900_000
DEFAULT_SETUP_BUDGET_MS = 3_600_000
DEFAULT_PROBE_BUDGET_MS = 60_000


def python() -> str:
    """Return the project virtual-environment interpreter."""
    return PYTHON


# Fixture profiles attached to catalogue domains. They describe the data a
# selected test may touch; they are not runnable fixtures themselves.
FIXTURE_PROFILES = (
    "none",
    "temp-db",
    "live-services",
    "browser",
    "real-db",
)

# Layers are orthogonal to domains and come from the test's location and
# runner, never from the catalogue file. More specific prefixes come first.
LAYER_ROOTS: tuple[tuple[str, str], ...] = (
    ("tests/e2e/", "e2e"),
    ("backend/tests/", "backend"),
    ("tests/", "backend"),
)

# Python test roots collected by pytest.
PYTEST_ROOTS = ("backend/tests", "tests")

FRONTEND_TEST_ROOT = "frontend/src/"
# The only frontend test that needs the live backend; it runs through
# frontend/vitest.api.config.ts and is excluded from the unit project.
FRONTEND_API_TEST = "frontend/src/api/healthClient.test.ts"
