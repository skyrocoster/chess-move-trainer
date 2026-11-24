"""Worker mode, service health and starting or stopping the analysis workers."""

from __future__ import annotations

import json
from dataclasses import dataclass

from tools.dev.config import SERVICE_NAMES, WORKER_PROFILE
from tools.dev.console import echo, fail, is_dry_run, run
from tools.dev.services.compose import (
    QUERY_TIMEOUT,
    compose,
    compose_command,
    require_docker,
    worker_compose,
)


def parse_ps_rows(text: str) -> list[dict[str, object]]:
    """Parse ``compose ps --format json`` output (JSON lines or one JSON array)."""
    if not text.strip():
        return []
    try:
        payload = json.loads(text)
        items = payload if isinstance(payload, list) else [payload]
    except json.JSONDecodeError:
        items = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                fail("Docker Compose returned invalid status JSON.")
    return [item for item in items if isinstance(item, dict)]


@dataclass(frozen=True)
class WorkerMode:
    label: str
    normal_running: int
    accelerated_running: int

    @property
    def invalid(self) -> bool:
        return self.label.startswith("invalid")


def classify_worker_mode(rows: list[dict[str, object]]) -> WorkerMode:
    """Classify the analysis workers from compose ps rows."""
    normal = sum(1 for r in rows if r.get("Service") == "worker" and r.get("State") == "running")
    six = sum(1 for r in rows if r.get("Service") == "worker-six" and r.get("State") == "running")
    if normal == 1 and six == 0:
        label = "normal"
    elif normal == 0 and six == 6:
        label = "accelerated-six"
    elif normal == 0 and six == 0:
        label = "stopped"
    elif normal > 0 and six > 0:
        label = "invalid/mixed"
    else:
        label = "invalid/partial"
    return WorkerMode(label, normal, six)


def _ps_rows(services: list[str]) -> list[dict[str, object]]:
    result = run(
        compose_command(
            ["--profile", WORKER_PROFILE, "ps", "--all", "--format", "json", *services]
        ),
        capture_output=True,
        quiet=True,
        check=False,
        timeout=QUERY_TIMEOUT,
    )
    if result.returncode != 0:
        fail(f"Docker Compose status failed with exit code {result.returncode}.")
    return parse_ps_rows(result.stdout)


def get_worker_mode() -> WorkerMode:
    if is_dry_run():
        # Nothing is queried in a dry run; assume the default single worker is running.
        return WorkerMode("normal", 1, 0)
    return classify_worker_mode(_ps_rows(["worker", "worker-six"]))


def assert_worker_counts(mode: WorkerMode) -> None:
    if mode.normal_running != 0 or mode.accelerated_running != 0:
        fail(
            "Analysis workers did not stop cleanly: "
            f"normal={mode.normal_running}, accelerated={mode.accelerated_running}."
        )


def assert_workers_stopped() -> None:
    """Fail unless no analysis worker is running (skipped in a dry run)."""
    if not is_dry_run():
        assert_worker_counts(get_worker_mode())


def rows_healthy(rows: list[dict[str, object]]) -> bool:
    """Return whether backend, frontend and datasette are running and healthy."""
    for name in SERVICE_NAMES:
        row = next((r for r in rows if r.get("Service") == name), None)
        if row is None or row.get("State") != "running" or row.get("Health") != "healthy":
            return False
    return True


def stack_healthy() -> bool:
    if get_worker_mode().label not in ("normal", "accelerated-six"):
        return False
    return rows_healthy(_ps_rows(list(SERVICE_NAMES)))


def require_stack_healthy() -> None:
    """Fail unless backend, frontend and datasette are running and healthy."""
    require_docker()
    if not rows_healthy(_ps_rows(list(SERVICE_NAMES))):
        fail(
            "Development services are not all healthy (backend, frontend, datasette)."
            " Run `uv run --no-sync sg dev start` and retry."
        )
    echo("backend, frontend and datasette are running and healthy.")


def print_worker_mode() -> None:
    mode = get_worker_mode()
    echo(
        f"Worker mode: {mode.label} (normal running={mode.normal_running},"
        f" accelerated running={mode.accelerated_running})"
    )


def stop_normal_worker() -> None:
    compose(["stop", "worker"])


def stop_accelerated_workers() -> None:
    worker_compose(["stop", "worker-six"])


def start_normal_worker() -> None:
    stop_accelerated_workers()
    if get_worker_mode().accelerated_running != 0 and not is_dry_run():
        fail("Accelerated workers are still running; normal mode was not started.")
    compose(["up", "--detach", "--scale", "worker=1", "--wait", "--wait-timeout", "180", "worker"])


def start_accelerated_workers() -> None:
    stop_normal_worker()
    if get_worker_mode().normal_running != 0 and not is_dry_run():
        fail("The normal worker is still running; accelerated mode was not started.")
    worker_compose(
        [
            "up", "--detach", "--scale", "worker-six=6",
            "--wait", "--wait-timeout", "180", "worker-six",
        ]
    )
