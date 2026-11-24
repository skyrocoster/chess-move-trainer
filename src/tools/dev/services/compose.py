"""Compose command building, environment budgets and the Docker preflight."""

from __future__ import annotations

import os
import subprocess

from tools.dev.config import (
    COMPOSE_FILE,
    DEFAULT_PROBE_BUDGET_MS,
    DEFAULT_SETUP_BUDGET_MS,
    DEFAULT_UPDATE_BUDGET_MS,
    REPOSITORY_ROOT,
    WORKER_PROFILE,
)
from tools.dev.console import fail, is_dry_run, run

COMPOSE_TIMEOUT = 300.0
REBUILD_TIMEOUT = 900.0
QUERY_TIMEOUT = 120.0
DOCKER_RM_TIMEOUT = 60.0


def budget_ms(variable: str, default: int) -> int:
    """Return a millisecond budget from the environment, falling back to ``default``."""
    raw = os.environ.get(variable, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        fail(f"{variable} must be a whole number of milliseconds, got {raw!r}.")
    if value <= 0:
        fail(f"{variable} must be positive, got {value}.")
    return value


def update_budget_ms() -> int:
    return budget_ms("CHESS_START_UPDATE_BUDGET_MS", DEFAULT_UPDATE_BUDGET_MS)


def setup_budget_ms() -> int:
    return budget_ms("CHESS_DEV_SETUP_BUDGET_MS", DEFAULT_SETUP_BUDGET_MS)


def probe_budget_ms() -> int:
    return budget_ms("CHESS_DEV_PROBE_BUDGET_MS", DEFAULT_PROBE_BUDGET_MS)


def compose_command(arguments: list[str]) -> list[str]:
    """Return a ``docker compose`` invocation rooted at this repository."""
    return [
        "docker",
        "compose",
        "--file",
        str(COMPOSE_FILE),
        "--project-directory",
        str(REPOSITORY_ROOT),
        *arguments,
    ]


def compose(arguments: list[str], *, timeout: float = COMPOSE_TIMEOUT) -> None:
    """Run ``docker compose``; a non-zero exit stops sg with that exit code."""
    run(compose_command(arguments), timeout=timeout)


def worker_compose(arguments: list[str], *, timeout: float = COMPOSE_TIMEOUT) -> None:
    """Run ``docker compose`` with the ``worker-six`` profile enabled."""
    compose(["--profile", WORKER_PROFILE, *arguments], timeout=timeout)


def require_docker() -> None:
    """Fail with a clear message when Docker Desktop is unavailable."""
    if is_dry_run():
        return
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        fail("Docker Desktop is not running. Start Docker Desktop and try again.")
    if result.returncode != 0:
        fail("Docker Desktop is not running. Start Docker Desktop and try again.")
