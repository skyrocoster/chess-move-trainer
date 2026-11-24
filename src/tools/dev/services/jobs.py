"""One-shot worker containers: the live-database probe and the data update jobs."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from tools.dev.config import LIVE_DATABASE_CONTAINER_PATH, REPOSITORY_ROOT
from tools.dev.console import echo, fail, host_command, is_dry_run, kill_process_tree, run
from tools.dev.services.compose import (
    DOCKER_RM_TIMEOUT,
    compose_command,
    probe_budget_ms,
)

PROBE_CONTAINER = "chess-move-trainer-db-probe"
UPDATE_CONTAINER = "chess-move-trainer-db-update"
SETUP_CONTAINER = "chess-move-trainer-db-setup"
SETUP_CLEANUP_CONTAINER = "chess-move-trainer-db-setup-cleanup"

PROBE_PYTHON = (
    "import sys; from pathlib import Path; "
    "sys.exit(0 if Path('data/database/chess.db').exists() else 1)"
)
SETUP_CLEANUP_PYTHON = (
    "from pathlib import Path; "
    "[Path('data/database/chess.db' + suffix).unlink(missing_ok=True) "
    "for suffix in ('', '-journal', '-wal', '-shm')]"
)


@dataclass(frozen=True)
class BudgetedResult:
    timed_out: bool
    exit_code: int | None


def _remove_container(name: str) -> None:
    run(
        ["docker", "rm", "-f", name],
        capture_output=True,
        check=False,
        quiet=True,
        timeout=DOCKER_RM_TIMEOUT,
    )


def budgeted_compose_run(
    container: str, run_args: list[str], budget: int, label: str
) -> BudgetedResult:
    """Run ``docker compose run`` with a time budget, removing the container on timeout."""
    echo_rm = ["docker", "rm", "-f", container]
    if is_dry_run():
        echo(f"[dry-run] > {subprocess.list2cmdline(echo_rm)}")
    _remove_container(container)
    command = host_command(compose_command(["run", *run_args]))
    if is_dry_run():
        echo(f"[dry-run] > {subprocess.list2cmdline(command)}")
        return BudgetedResult(False, 0)
    echo(f"> {subprocess.list2cmdline(command)}")
    process = subprocess.Popen(command, cwd=str(REPOSITORY_ROOT), text=True)
    try:
        code = process.wait(timeout=budget / 1000)
    except subprocess.TimeoutExpired:
        echo(
            f"WARNING: {label} timed out after {budget} ms; removing container {container}.",
            err=True,
        )
        _remove_container(container)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            kill_process_tree(process)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        _remove_container(container)
        return BudgetedResult(True, None)
    _remove_container(container)
    return BudgetedResult(False, code)


def live_database_exists() -> bool:
    """Probe the chess-database volume from a one-shot worker container."""
    budget = probe_budget_ms()
    result = budgeted_compose_run(
        PROBE_CONTAINER,
        ["--rm", "--no-deps", "--name", PROBE_CONTAINER, "worker", "python", "-c", PROBE_PYTHON],
        budget,
        "Live-database probe",
    )
    if result.timed_out:
        fail(f"Live-database probe timed out after {budget} ms.")
    if result.exit_code == 0:
        return True
    if result.exit_code == 1:
        return False
    fail(f"Live-database probe failed with exit code {result.exit_code}.")


@dataclass(frozen=True)
class UpdateOutcome:
    ok: bool
    reason: str = ""


def run_database_updates(budget: int) -> UpdateOutcome:
    """Run ``update games`` then ``update openings`` in one-shot worker containers."""
    for label, step in (("Update games", "games"), ("Update openings", "openings")):
        result = budgeted_compose_run(
            UPDATE_CONTAINER,
            [
                "--rm", "--no-deps", "--name", UPDATE_CONTAINER, "worker",
                "python", "-m", "chess_move_trainer.database",
                "update", step, "--database", LIVE_DATABASE_CONTAINER_PATH,
            ],
            budget,
            label,
        )
        if result.timed_out:
            return UpdateOutcome(False, f"{label} timed out after {budget} ms")
        if result.exit_code != 0:
            return UpdateOutcome(False, f"{label} exited with code {result.exit_code}")
    return UpdateOutcome(True)
