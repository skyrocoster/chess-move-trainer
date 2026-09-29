"""Read-only Docker Engine probe for the analysis worker containers.

The status page reports one line per analysis worker. The backend runs inside
Docker, so it reads the Compose-managed container states through the Docker
Engine API over the mounted ``/var/run/docker.sock``. Any failure (socket not
mounted, Docker stopped, or a non-Docker host) resolves to ``None`` rather than
raising, and the status page shows that worker status is unavailable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

DOCKER_SOCKET_PATH = "/var/run/docker.sock"
COMPOSE_PROJECT = "chess-move-trainer"
NORMAL_SERVICE = "worker"
SIX_SERVICE = "worker-six"
WORKER_SERVICES = (NORMAL_SERVICE, SIX_SERVICE)
PROBE_TIMEOUT_SECONDS = 1.0


@dataclass(frozen=True)
class WorkerContainer:
    """One Compose analysis-worker container and whether it is running."""

    service: str
    index: int
    running: bool


def probe_workers(socket_path: str = DOCKER_SOCKET_PATH) -> list[WorkerContainer] | None:
    """Return every analysis worker container, or ``None`` when Docker is unreadable."""

    try:
        containers = _page_containers(socket_path)
    except Exception:
        return None
    return worker_containers(containers)


def worker_containers(containers: object) -> list[WorkerContainer]:
    """Map raw Docker container records to sorted worker records."""

    if not isinstance(containers, list):
        return []

    workers: list[WorkerContainer] = []
    for container in containers:
        if not isinstance(container, dict):
            continue
        labels = container.get("Labels") or {}
        if not isinstance(labels, dict):
            continue
        service = labels.get("com.docker.compose.service")
        if service not in WORKER_SERVICES:
            continue
        try:
            index = int(labels.get("com.docker.compose.container-number", ""))
        except (TypeError, ValueError):
            continue
        workers.append(
            WorkerContainer(
                service=service,
                index=index,
                running=container.get("State") == "running",
            )
        )

    workers.sort(key=lambda worker: (0 if worker.service == NORMAL_SERVICE else 1, worker.index))
    return workers


def _page_containers(socket_path: str) -> object:
    transport = httpx.HTTPTransport(uds=socket_path)
    with httpx.Client(
        transport=transport,
        base_url="http://docker",
        timeout=httpx.Timeout(PROBE_TIMEOUT_SECONDS),
    ) as client:
        response = client.get(
            "/containers/json",
            params={
                "all": "1",
                "filters": json.dumps(
                    {"label": [f"com.docker.compose.project={COMPOSE_PROJECT}"]}
                ),
            },
        )
        response.raise_for_status()
        return response.json()


__all__ = [
    "COMPOSE_PROJECT",
    "DOCKER_SOCKET_PATH",
    "NORMAL_SERVICE",
    "SIX_SERVICE",
    "WORKER_SERVICES",
    "WorkerContainer",
    "probe_workers",
    "worker_containers",
]
