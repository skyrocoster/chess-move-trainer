from __future__ import annotations

from pathlib import Path

from backend.app.features.health.docker_probe import (
    WorkerContainer,
    probe_workers,
    worker_containers,
)


def _container(service: str, number: str, state: str) -> dict:
    return {
        "State": state,
        "Labels": {
            "com.docker.compose.service": service,
            "com.docker.compose.container-number": number,
        },
    }


def test_orders_normal_worker_before_six_workers() -> None:
    containers = [
        _container("worker-six", "3", "running"),
        _container("worker", "1", "running"),
        _container("worker-six", "1", "running"),
        _container("worker-six", "2", "exited"),
    ]

    assert worker_containers(containers) == [
        WorkerContainer(service="worker", index=1, running=True),
        WorkerContainer(service="worker-six", index=1, running=True),
        WorkerContainer(service="worker-six", index=2, running=False),
        WorkerContainer(service="worker-six", index=3, running=True),
    ]


def test_ignores_non_worker_and_malformed_containers() -> None:
    containers = [
        _container("backend", "1", "running"),
        _container("datasette", "1", "running"),
        "not-a-container",
        {"State": "running", "Labels": {"com.docker.compose.service": "worker"}},
        {"State": "running", "Labels": None},
        _container("worker", "1", "running"),
    ]

    assert worker_containers(containers) == [
        WorkerContainer(service="worker", index=1, running=True)
    ]


def test_empty_and_non_list_inputs_return_no_workers() -> None:
    assert worker_containers([]) == []
    assert worker_containers(None) == []
    assert worker_containers({"State": "running"}) == []


def test_probe_returns_none_when_socket_is_missing(tmp_path: Path) -> None:
    assert probe_workers(str(tmp_path / "no-such-docker.sock")) is None
