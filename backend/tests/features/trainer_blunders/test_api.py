from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from backend.app.dependencies import (
    BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV,
    REBUILT_DATABASE_PATH_ENV,
)
from backend.app.features.trainer_blunders import router as trainer_blunders_router

from .conftest import GAME_UUID


def _params(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "started_at_from": "2026-08-01T14:00:00+02:00",
        "started_at_to": "2026-08-01T12:00:00Z",
    }
    values.update(overrides)
    return values


def test_discovery_returns_trainer_ready_blunder_without_writing(api_context) -> None:
    client, database = api_context
    before = database.read_bytes()

    response = client.get("/api/trainer/blunders", params=_params())

    assert response.status_code == 200
    assert response.json() == {
        "timeframe": {
            "started_at_from": "2026-08-01T12:00:00.000000Z",
            "started_at_to": "2026-08-01T12:00:00.000000Z",
        },
        "policy": {
            "minimum_expected_score_loss": 0.2,
            "evaluation_basis": "wdl_expected_score",
            "score_perspective": "trainer",
        },
        "coverage": {
            "examined_game_count": 1,
            "excluded_game_count": 0,
            "in_scope_game_count": 1,
            "trainer_move_count": 2,
            "comparable_move_count": 1,
            "skipped_missing_analysis_count": 1,
        },
        "items": [
            {
                "game_uuid": GAME_UUID,
                "source_url": f"https://www.chess.com/game/live/{GAME_UUID}",
                "started_at_utc": "2026-08-01T12:00:00Z",
                "trainer_color": "white",
                "ply": 0,
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "played_move_uci": "e2e4",
                "preferred_move_uci": "d2d4",
                "expected_score_before": 0.85,
                "expected_score_after": 0.55,
                "expected_score_loss": 0.3,
                "before_analysis_quality": "browser",
                "after_analysis_quality": "tool",
            }
        ],
        "page": 1,
        "page_size": 50,
        "total": 1,
        "total_pages": 1,
        "has_next": False,
    }
    assert database.read_bytes() == before


@pytest.mark.parametrize(
    "params",
    [
        _params(started_at_from="not-a-time"),
        _params(
            started_at_from="2026-08-02T00:00:00Z",
            started_at_to="2026-08-01T00:00:00Z",
        ),
        _params(trainer_color="purple"),
        _params(page=0),
        _params(page_size=101),
    ],
)
def test_invalid_filters_return_stable_422(params, api_context) -> None:
    client, _database = api_context

    response = client.get("/api/trainer/blunders", params=params)

    assert response.status_code == 422
    assert response.json() == {
        "code": "invalid_filter",
        "message": "Invalid blunder timeframe or filter",
    }


def test_configured_threshold_controls_discovery(
    api_context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _database = api_context
    monkeypatch.setenv(BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV, "0.31")

    response = client.get("/api/trainer/blunders", params=_params())

    assert response.status_code == 200
    assert response.json()["policy"]["minimum_expected_score_loss"] == 0.31
    assert response.json()["items"] == []
    assert response.json()["total"] == 0
    assert response.json()["coverage"]["comparable_move_count"] == 1


def test_identical_reads_are_cached_but_pagination_uses_a_distinct_key(
    api_context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _database = api_context
    original = trainer_blunders_router.discover_blunders
    calls = 0

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(trainer_blunders_router, "discover_blunders", counted)

    first = client.get("/api/trainer/blunders", params=_params())
    repeated = client.get("/api/trainer/blunders", params=_params())
    next_page = client.get("/api/trainer/blunders", params=_params(page=2))

    assert first.status_code == repeated.status_code == next_page.status_code == 200
    assert first.content == repeated.content
    assert calls == 2


def test_invalid_policy_configuration_returns_503(
    api_context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _database = api_context
    monkeypatch.setenv(BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV, "not-a-number")

    response = client.get("/api/trainer/blunders", params=_params())

    assert response.status_code == 503
    assert response.json() == {
        "code": "trainer_blunders_unavailable",
        "message": "Trainer blunders unavailable",
    }


def test_missing_database_returns_503_without_creating_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(missing))

    response = client.get("/api/trainer/blunders", params=_params())

    assert response.status_code == 503
    assert response.json()["code"] == "trainer_blunders_unavailable"
    assert not missing.exists()


def test_schema_incompatible_database_returns_503(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client,
) -> None:
    odd = tmp_path / "odd.db"
    with sqlite3.connect(odd) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(odd))

    response = client.get("/api/trainer/blunders", params=_params())

    assert response.status_code == 503
    assert response.json() == {
        "code": "trainer_blunders_unavailable",
        "message": "Trainer blunders unavailable",
    }


def test_black_filter_excludes_white_trainer_game(api_context) -> None:
    client, _database = api_context

    response = client.get("/api/trainer/blunders", params=_params(trainer_color="black"))

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["coverage"]["in_scope_game_count"] == 0
    assert body["coverage"]["trainer_move_count"] == 0


def test_openapi_exposes_the_additive_trainer_operation(client) -> None:
    operation = client.get("/openapi.json").json()["paths"]["/api/trainer/blunders"]["get"]

    assert operation["operationId"] == "getTrainerBlunders"
    assert operation["tags"] == ["trainer"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "TrainerBlundersResponse"
    )
