from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
import backend.app.features.games.router as games_router
import backend.app.features.position_insight.router as insight_router
from backend.tests.features.position_insight.conftest import create_insight_database

from .conftest import TARGET_FEN, count_reader_calls

analysis_router = importlib.import_module(
    "backend.app.features.analysis_observation.router"
)
preferred_moves_router = importlib.import_module(
    "backend.app.features.preferred_moves.router"
)


def test_repeated_analysis_reads_share_cached_payloads(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    analysis_calls = count_reader_calls(
        monkeypatch, analysis_router, "read_analysis_observation"
    )

    first = client.get("/api/analysis", params={"fen": TARGET_FEN})
    second = client.get("/api/analysis", params={"fen": TARGET_FEN})
    assert first.status_code == second.status_code == 200
    assert first.content == second.content

    assert len(analysis_calls) == 1

    requested = client.post("/api/analysis-requests", json={"fen": TARGET_FEN})
    refreshed = client.get("/api/analysis", params={"fen": TARGET_FEN})

    assert requested.status_code == 202
    assert refreshed.status_code == 200
    assert refreshed.json()["state"] == "queued"
    assert len(analysis_calls) == 2


def test_repeated_insight_reads_share_cached_payloads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, client: TestClient
) -> None:
    database = create_insight_database(tmp_path / "insight-cache.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    insight_calls = count_reader_calls(
        monkeypatch, insight_router, "read_position_insight"
    )

    params = {
        "fen": TARGET_FEN,
        "trainer_color": "white",
        "as_of": "2026-01-15",
    }
    first = client.get("/api/positions/insight", params=params)
    second = client.get("/api/positions/insight", params=params)

    assert first.status_code == second.status_code == 200
    assert first.content == second.content
    assert len(insight_calls) == 1


def test_repeated_preferred_move_and_game_detail_reads_share_cached_payloads(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    preferred_calls = count_reader_calls(
        monkeypatch, preferred_moves_router, "read_preferred_moves"
    )
    game_calls = count_reader_calls(monkeypatch, games_router, "read_game")

    timeline_params = {
        "fen": TARGET_FEN,
        "from": "2026-01-15",
        "until": "2026-02-15",
    }
    first_timeline = client.get("/api/preferred-moves", params=timeline_params)
    second_timeline = client.get("/api/preferred-moves", params=timeline_params)
    assert first_timeline.status_code == second_timeline.status_code == 200
    assert first_timeline.content == second_timeline.content

    games = client.get("/api/games", params={"page": 1, "page_size": 1})
    assert games.status_code == 200
    game_uuid = games.json()["items"][0]["game_uuid"]
    first_detail = client.get(f"/api/games/{game_uuid}")
    second_detail = client.get(f"/api/games/{game_uuid}")
    assert first_detail.status_code == second_detail.status_code == 200
    assert first_detail.content == second_detail.content

    assert len(preferred_calls) == 1
    assert len(game_calls) == 1
