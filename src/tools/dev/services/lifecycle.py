"""Lifecycle actions behind ``sg dev``: start, stop, restart, rebuild, status, logs, update, setup."""

from __future__ import annotations

from tools.dev.config import LIVE_DATABASE_CONTAINER_PATH, WORKER_PROFILE
from tools.dev.console import echo, fail, is_dry_run, run
from tools.dev.services.compose import (
    QUERY_TIMEOUT,
    REBUILD_TIMEOUT,
    compose,
    compose_command,
    probe_budget_ms,
    require_docker,
    setup_budget_ms,
    update_budget_ms,
    worker_compose,
)
from tools.dev.services.jobs import (
    SETUP_CLEANUP_CONTAINER,
    SETUP_CLEANUP_PYTHON,
    SETUP_CONTAINER,
    budgeted_compose_run,
    live_database_exists,
    run_database_updates,
)
from tools.dev.services.workers import (
    assert_workers_stopped,
    get_worker_mode,
    print_worker_mode,
    stack_healthy,
    start_accelerated_workers,
    start_normal_worker,
    stop_accelerated_workers,
    stop_normal_worker,
)


def _targets(service: str) -> list[str]:
    return [] if service == "all" else [service]


# --- Lifecycle actions ------------------------------------------------------

_UP = ["up", "--detach", "--wait", "--wait-timeout", "180"]


def start(service: str = "all") -> None:
    require_docker()
    if service == "worker-six":
        start_accelerated_workers()
    elif service == "worker":
        start_normal_worker()
    elif service == "all":
        if stack_healthy():
            echo(
                "Stack is already healthy; leaving it alone "
                "(no data update, no worker-mode change)."
            )
            return
        if not live_database_exists():
            fail(
                "No live database found in the chess-database volume. Run"
                " `uv run --no-sync sg dev setup-db` once to create it, then start again."
            )
        mode_before = get_worker_mode().label
        if mode_before.startswith("invalid"):
            echo(
                f"WARNING: Workers are in state '{mode_before}';"
                " stopping them before the data update.",
                err=True,
            )
        stop_accelerated_workers()
        stop_normal_worker()
        outcome = run_database_updates(update_budget_ms())
        if not outcome.ok:
            echo(
                f"WARNING: Data update did not complete ({outcome.reason});"
                " starting services on the existing data.",
                err=True,
            )
        if mode_before == "accelerated-six":
            start_accelerated_workers()
            compose([*_UP, "backend", "frontend", "datasette"])
        else:
            stop_accelerated_workers()
            compose(["up", "--detach", "--scale", "worker=1", "--wait", "--wait-timeout", "180"])
    else:
        compose([*_UP, *_targets(service)])


def stop(service: str = "all") -> None:
    require_docker()
    if service in ("worker", "worker-six"):
        stop_accelerated_workers()
        stop_normal_worker()
        assert_workers_stopped()
    elif service == "all":
        worker_compose(["stop"])
        assert_workers_stopped()
    else:
        compose(["stop", *_targets(service)])


def restart(service: str = "all") -> None:
    require_docker()
    if service == "worker-six":
        stop_accelerated_workers()
        start_accelerated_workers()
    elif service == "worker":
        start_normal_worker()
    elif service == "all":
        worker_compose(["stop"])
        assert_workers_stopped()
        compose(["up", "--detach", "--scale", "worker=1", "--wait", "--wait-timeout", "180"])
    else:
        compose(["restart", *_targets(service)])
        compose([*_UP, "--no-recreate", *_targets(service)])


def rebuild(service: str = "all") -> None:
    require_docker()
    build = ["up", "--detach", "--build", "--force-recreate"]
    wait = ["--wait", "--wait-timeout", "300"]
    if service == "worker-six":
        stop_normal_worker()
        worker_compose(
            [*build, "--scale", "worker-six=6", *wait, "worker-six"], timeout=REBUILD_TIMEOUT
        )
    elif service == "worker":
        stop_accelerated_workers()
        compose([*build, "--scale", "worker=1", *wait, "worker"], timeout=REBUILD_TIMEOUT)
    elif service == "all":
        stop_accelerated_workers()
        compose([*build, "--scale", "worker=1", *wait], timeout=REBUILD_TIMEOUT)
    else:
        compose([*build, *wait, *_targets(service)], timeout=REBUILD_TIMEOUT)


def status(service: str = "all", *, as_json: bool = False) -> None:
    require_docker()
    if as_json:
        if service in ("worker", "worker-six"):
            targets = ["worker", "worker-six"]
        else:
            targets = _targets(service)
        result = run(
            compose_command(
                ["--profile", WORKER_PROFILE, "ps", "--all", "--format", "json", *targets]
            ),
            capture_output=True,
            quiet=True,
            timeout=QUERY_TIMEOUT,
        )
        echo(result.stdout.rstrip())
        return
    if service == "all":
        worker_compose(["ps", "--all"], timeout=QUERY_TIMEOUT)
        print_worker_mode()
    elif service in ("worker", "worker-six"):
        worker_compose(["ps", "--all", "worker", "worker-six"], timeout=QUERY_TIMEOUT)
        print_worker_mode()
    else:
        compose(["ps", "--all", *_targets(service)], timeout=QUERY_TIMEOUT)


def logs(service: str = "all", *, tail: int = 100) -> None:
    require_docker()
    base = ["logs", "--tail", str(tail), "--no-log-prefix"]
    if service == "all":
        worker_compose(base, timeout=QUERY_TIMEOUT)
    elif service == "worker-six":
        worker_compose([*base, "worker-six"], timeout=QUERY_TIMEOUT)
    else:
        compose([*base, *_targets(service)], timeout=QUERY_TIMEOUT)


def update() -> None:
    """Refresh games and openings with the workers paused, then restore the worker mode."""
    require_docker()
    if not live_database_exists():
        fail(
            "No live database found in the chess-database volume. Run"
            " `uv run --no-sync sg dev setup-db` once to create it."
        )
    mode = get_worker_mode()
    if mode.invalid:
        fail(
            f"Refusing to update while workers are in state '{mode.label}'."
            " Resolve the worker state first."
        )
    active = mode.label
    stop_accelerated_workers()
    stop_normal_worker()
    assert_workers_stopped()
    outcome = run_database_updates(update_budget_ms())
    if active == "accelerated-six":
        start_accelerated_workers()
    elif active == "normal":
        start_normal_worker()
    if not outcome.ok:
        fail(f"Data update failed ({outcome.reason}); workers were restored to mode '{active}'.")
    echo(f"Data update completed; workers restored to mode '{active}'.")


def setup_database() -> None:
    """Create the live database once; refuses when it already exists."""
    require_docker()
    exists = live_database_exists()
    if exists and not is_dry_run():
        fail(
            "Live database already exists in the chess-database volume;"
            " setup refused to avoid overwriting it."
        )
    budget = setup_budget_ms()
    result = budgeted_compose_run(
        SETUP_CONTAINER,
        [
            "--rm", "--no-deps", "--name", SETUP_CONTAINER, "worker",
            "python", "-m", "chess_move_trainer.database",
            "setup", "--database", LIVE_DATABASE_CONTAINER_PATH,
        ],
        budget,
        "Setup",
    )
    if result.timed_out:
        echo(
            f"WARNING: Setup timed out after {budget} ms;"
            " removing the partial database it created.",
            err=True,
        )
        cleanup = budgeted_compose_run(
            SETUP_CLEANUP_CONTAINER,
            [
                "--rm", "--no-deps", "--name", SETUP_CLEANUP_CONTAINER, "worker",
                "python", "-c", SETUP_CLEANUP_PYTHON,
            ],
            probe_budget_ms(),
            "Setup cleanup",
        )
        if cleanup.timed_out or cleanup.exit_code != 0:
            fail(
                "Setup timed out and partial-database cleanup did not complete;"
                " inspect the chess-database volume before retrying."
            )
        fail(f"Setup timed out after {budget} ms; its partial database was removed.")
    if result.exit_code != 0:
        fail(f"Setup exited with code {result.exit_code}.")
    echo("Setup completed: live database created in the chess-database volume.")
