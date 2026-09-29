from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import get_rebuilt_database_path
from backend.app.features.health import router as health_router
from backend.app.features.health.docker_probe import WorkerContainer
from backend.app.main import app
from chess_move_trainer.database.schema import create_schema

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_dependency_overrides() -> None:
    yield
    app.dependency_overrides.clear()


def _create_database(path: Path) -> None:
    create_schema(path)
    with sqlite3.connect(path) as connection:
        connection.execute(
            "INSERT INTO derived_position (dp_position_id, dp_placement, dp_side_to_move, "
            "dp_castling_rights, dp_legal_en_passant) VALUES "
            "(1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-'), "
            "(2, '8/8/8/8/8/8/8/K5k', 'b', '-', '-')"
        )
        connection.execute(
            "INSERT INTO datasource_game (dg_game_id, dg_chesscom_game_uuid, dg_source_url, "
            "dg_original_pgn, dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc) "
            "VALUES (1, 'uuid-1', 'https://example.test/g/1', '1. e4', 'white', "
            "'trainer-uuid', '2026-09-20T12:00:00+00:00')"
        )
        connection.execute(
            "INSERT INTO derived_analysis_result (derived_position_id, dar_quality, "
            "dar_configuration_version, dar_settings_json, dar_engine_name, dar_engine_version) "
            "VALUES (1, 'tool', 1, '{}', 'Stockfish', '17')"
        )
        connection.execute(
            "INSERT INTO derived_analysis_queue (derived_position_id, daq_requested_quality, "
            "daq_state, daq_requested_at_utc) "
            "VALUES (2, 'tool', 'queued', '2026-09-21T00:00:00+00:00')"
        )
        connection.commit()


def test_health_returns_typed_ok_response() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert set(body) == {"status", "analysis", "workers", "last_game_at"}
    assert body["workers"] is None or isinstance(body["workers"], list)


def test_health_reports_analysis_backlog_and_last_game(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "chess.db"
    _create_database(database)
    app.dependency_overrides[get_rebuilt_database_path] = lambda: database
    monkeypatch.setattr(
        health_router,
        "probe_workers",
        lambda: [WorkerContainer(service="worker", index=1, running=True)],
    )

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "analysis": {"positions": 2, "analyzed": 1, "queued": 1, "running": 0, "remaining": 0},
        "workers": [{"service": "worker", "index": 1, "running": True}],
        "last_game_at": "2026-09-20T12:00:00+00:00",
    }


def test_health_reports_unreadable_database_as_null(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "missing.db"
    app.dependency_overrides[get_rebuilt_database_path] = lambda: missing
    monkeypatch.setattr(health_router, "probe_workers", lambda: None)

    body = client.get("/api/health").json()

    assert body["status"] == "ok"
    assert body["analysis"] is None
    assert body["last_game_at"] is None
    assert body["workers"] is None


def test_health_reports_each_worker_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app.dependency_overrides[get_rebuilt_database_path] = lambda: tmp_path / "missing.db"
    monkeypatch.setattr(
        health_router,
        "probe_workers",
        lambda: [
            WorkerContainer(service="worker", index=1, running=False),
            WorkerContainer(service="worker-six", index=1, running=True),
            WorkerContainer(service="worker-six", index=2, running=True),
            WorkerContainer(service="worker-six", index=3, running=False),
        ],
    )

    body = client.get("/api/health").json()

    assert body["workers"] == [
        {"service": "worker", "index": 1, "running": False},
        {"service": "worker-six", "index": 1, "running": True},
        {"service": "worker-six", "index": 2, "running": True},
        {"service": "worker-six", "index": 3, "running": False},
    ]


def test_unknown_route_returns_not_found() -> None:
    assert client.get("/api/missing").status_code == 404


def test_cors_allows_frontend_origin() -> None:
    response = client.get("/api/health", headers={"Origin": "http://localhost:8444"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:8444"


def test_cors_does_not_allow_other_origins() -> None:
    response = client.get("/api/health", headers={"Origin": "http://localhost:3000"})

    assert "access-control-allow-origin" not in response.headers
