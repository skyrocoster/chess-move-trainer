from __future__ import annotations

import importlib
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.app.features.openings.router as openings_router
from backend.app.dependencies import TRAINING_TARGET_SUCCESS_RATE_ENV

from .conftest import OPENINGS_PARAMS, TARGET_FEN, TRAINING_PARAMS, count_reader_calls

# NOTE: the feature package __init__ re-exports `router` (the APIRouter), so a
# plain `import ... .router as ...` binds the router object, not the module.
training_router = importlib.import_module(
    "backend.app.features.position_training_requirements.router"
)

TRAINING_PATH = "/api/positions/training-requirements"
ANSWERS_PATH = "/api/positions/training-requirements/answers"
OPENINGS_PATH = "/api/openings"


def test_identical_repeat_reads_underlying_reader_once(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, training_router, "discover_training_requirements")

    first = client.get(TRAINING_PATH, params=TRAINING_PARAMS)
    second = client.get(TRAINING_PATH, params=TRAINING_PARAMS)

    assert first.status_code == second.status_code == 200
    assert len(calls) == 1
    assert first.content == second.content
    assert first.json() == second.json()


def test_reordered_and_equivalent_inputs_share_one_key(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, training_router, "discover_training_requirements")

    canonical = client.get(TRAINING_PATH, params=TRAINING_PARAMS)
    reordered = client.get(
        TRAINING_PATH,
        params=[
            ("training_requirement_gte", -100),
            ("as_of", "2026-01-15"),
        ],
    )
    respelled = client.get(
        TRAINING_PATH,
        params={"as_of": "2026-01-15", "training_requirement_gte": "-100.0"},
    )

    assert canonical.status_code == reordered.status_code == respelled.status_code == 200
    assert len(calls) == 1
    assert reordered.content == canonical.content
    assert respelled.content == canonical.content


def test_distinct_pages_and_policies_use_distinct_keys(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    calls = count_reader_calls(monkeypatch, training_router, "discover_training_requirements")

    page_one = client.get(TRAINING_PATH, params=TRAINING_PARAMS)
    page_two = client.get(TRAINING_PATH, params={**TRAINING_PARAMS, "page": 2})
    assert page_one.status_code == page_two.status_code == 200
    assert len(calls) == 2

    monkeypatch.setenv(TRAINING_TARGET_SUCCESS_RATE_ENV, "0.9")
    moved_policy = client.get(TRAINING_PATH, params=TRAINING_PARAMS)
    assert moved_policy.status_code == 200
    assert len(calls) == 3
    assert moved_policy.json()["scoring_policy"]["target_success_rate"] == 0.9


def test_error_responses_are_never_cached(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, database = api_context
    calls = count_reader_calls(monkeypatch, training_router, "discover_training_requirements")

    first_invalid = client.get(TRAINING_PATH, params={"as_of": "2026-01-15"})
    second_invalid = client.get(TRAINING_PATH, params={"as_of": "2026-01-15"})
    assert first_invalid.status_code == second_invalid.status_code == 422
    assert first_invalid.json() == second_invalid.json()
    assert calls == []

    missing = database.parent / "missing-cache.db"
    monkeypatch.setenv("CHESS_REBUILT_DATABASE_PATH", str(missing))
    first_missing = client.get(TRAINING_PATH, params=TRAINING_PARAMS)
    second_missing = client.get(TRAINING_PATH, params=TRAINING_PARAMS)
    assert first_missing.status_code == second_missing.status_code == 503
    assert not missing.exists()


def test_successful_answer_post_invalidates_training_and_openings(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, _database = api_context
    training_calls = count_reader_calls(
        monkeypatch, training_router, "discover_training_requirements"
    )
    openings_calls = count_reader_calls(monkeypatch, openings_router, "read_openings")

    assert client.get(TRAINING_PATH, params=TRAINING_PARAMS).status_code == 200
    assert client.get(OPENINGS_PATH, params=OPENINGS_PARAMS).status_code == 200
    assert len(training_calls) == 1
    assert len(openings_calls) == 1

    answer = client.post(
        ANSWERS_PATH,
        json={
            "fen": TARGET_FEN,
            "trainer_color": "white",
            "as_of": "2026-01-15",
            "played_move_uci": "a2a3",
        },
    )
    assert answer.status_code == 200

    assert client.get(TRAINING_PATH, params=TRAINING_PARAMS).status_code == 200
    assert client.get(OPENINGS_PATH, params=OPENINGS_PARAMS).status_code == 200
    assert len(training_calls) == 2
    assert len(openings_calls) == 2


def test_database_file_replacement_invalidates_cached_read(
    api_context: tuple[TestClient, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, database = api_context
    calls = count_reader_calls(monkeypatch, training_router, "discover_training_requirements")

    assert client.get(TRAINING_PATH, params=TRAINING_PARAMS).status_code == 200
    assert len(calls) == 1

    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO datasource_game (
                dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc
            ) VALUES (9, 'cache-api-game-9', 'https://example.test/cache-api-game-9',
                      '[Result "*"]' || char(10) || char(10) || '*', 'white', 'cache-trainer-9',
                      '2026-01-09T00:00:00Z')
            """
        )
        connection.commit()

    assert client.get(TRAINING_PATH, params=TRAINING_PARAMS).status_code == 200
    assert len(calls) == 2
