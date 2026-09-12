from __future__ import annotations

import sqlite3

import pytest

from backend.app.dependencies import get_training_requirement_policy
from backend.app.main import app
from chess_move_trainer.database.positions import TrainingRequirementPolicy

from .conftest import TARGET_CANONICAL_FEN, TARGET_FEN


def _query(**extra: object) -> dict[str, object]:
    return {
        "as_of": "2026-01-15",
        "training_requirement_gte": -100,
        **extra,
    }


def _answer(move: str = "a2a3", **extra: object) -> dict[str, object]:
    return {
        "fen": TARGET_FEN,
        "trainer_color": "white",
        "as_of": "2026-01-15",
        "played_move_uci": move,
        **extra,
    }


def test_discovery_returns_strict_scored_envelope_and_does_not_write(api_context) -> None:
    client, database, _position_id = api_context
    before = database.read_bytes()

    response = client.get("/api/positions/training-requirements", params=_query())

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"as_of", "scoring_policy", "items", "page", "page_size", "total"}
    assert body["as_of"] == "2026-01-15"
    assert body["scoring_policy"] == {
        "target_success_rate": 0.8,
        "game_hit_weight": 1.0,
        "game_miss_weight": 4.0,
        "training_curve": "squared",
        "training_credit_half_life_days": 30.0,
    }
    assert body["items"] == [
        {
            "fen": TARGET_CANONICAL_FEN,
            "trainer_color": "white",
            "preferred_move_uci": "a2a3",
            "encounters": 2,
            "hits": 1,
            "misses": 1,
            "observed_success_rate": 0.5,
            "game_balance": -3.0,
            "effective_training_balance": 0.0,
            "training_adjustment": 0.0,
            "training_updated_on": None,
            "training_requirement": -3.0,
            "training_required": True,
            "correct_answers_needed": 2,
        }
    ]
    assert body["page"] == 1
    assert body["page_size"] == 50
    assert body["total"] == 1
    assert database.read_bytes() == before


def test_discovery_accepts_overridden_policy_and_paired_opening_filter(api_context) -> None:
    client, _database, _position_id = api_context
    app.dependency_overrides[get_training_requirement_policy] = lambda: TrainingRequirementPolicy(
        0.75, 12.5
    )

    response = client.get(
        "/api/positions/training-requirements",
        params=_query(
            opening_key="A00:Training Opening",
            opening_match="reached",
        ),
    )

    assert response.status_code == 200
    assert response.json()["scoring_policy"] == {
        "target_success_rate": 0.75,
        "game_hit_weight": 1.0,
        "game_miss_weight": 3.0,
        "training_curve": "squared",
        "training_credit_half_life_days": 12.5,
    }


@pytest.mark.parametrize(
    "params",
    [
        {"as_of": "2026-01-15"},
        {**_query(), "opening_key": "A00:Training Opening"},
        {**_query(), "opening_match": "reached"},
        {**_query(), "opening_match": "other"},
        {**_query(), "as_of": "2026-1-15"},
        {**_query(), "page": 0},
        {**_query(), "page_size": 101},
    ],
)
def test_discovery_validation_returns_422(params, api_context) -> None:
    client, _database, _position_id = api_context

    response = client.get("/api/positions/training-requirements", params=params)

    assert response.status_code == 422


def test_invalid_configuration_makes_capability_unavailable(api_context, monkeypatch) -> None:
    client, _database, _position_id = api_context
    monkeypatch.setenv("CHESS_TRAINING_TARGET_SUCCESS_RATE", "not-a-rate")

    response = client.get("/api/positions/training-requirements", params=_query())

    assert response.status_code == 503
    assert response.json() == {
        "code": "position_training_requirements_unavailable",
        "message": "Position training requirements unavailable",
    }


def test_answer_is_backend_judged_and_returns_the_resulting_item(api_context) -> None:
    client, database, position_id = api_context
    before = database.read_bytes()

    response = client.post(
        "/api/positions/training-requirements/answers",
        json={**_answer(), "future_client_field": "ignored"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["as_of"] == "2026-01-15"
    assert body["correct"] is True
    assert body["item"]["effective_training_balance"] == 1.0
    assert body["item"]["training_updated_on"] == "2026-01-15"
    assert body["item"]["preferred_move_uci"] == "a2a3"
    assert body["item"]["fen"] == TARGET_CANONICAL_FEN
    assert database.read_bytes() != before
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            """
            SELECT dpta_training_balance, dpta_updated_on
            FROM derived_position_training_aggregate
            WHERE derived_position_id = ? AND dpta_preferred_move_uci = 'a2a3'
            """,
            (position_id,),
        ).fetchone() == (1.0, "2026-01-15")


@pytest.mark.parametrize(
    "payload",
    [
        {**_answer(), "trainer_color": "black"},
        {**_answer(), "played_move_uci": "e2e4"},
        {**_answer(), "as_of": "2026-1-15"},
        {**_answer(), "fen": "not a fen"},
    ],
)
def test_answer_validation_returns_422_without_writing(payload, api_context) -> None:
    client, database, _position_id = api_context
    before = database.read_bytes()

    response = client.post(
        "/api/positions/training-requirements/answers",
        json=payload,
    )

    assert response.status_code == 422
    assert database.read_bytes() == before


def test_missing_or_unknown_schema_database_returns_503_without_creation(
    tmp_path,
    monkeypatch,
    client,
) -> None:
    missing = tmp_path / "missing.db"
    monkeypatch.setenv("CHESS_REBUILT_DATABASE_PATH", str(missing))
    missing_response = client.get(
        "/api/positions/training-requirements",
        params=_query(),
    )
    assert missing_response.status_code == 503
    assert not missing.exists()

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE wrong (id INTEGER PRIMARY KEY)")
    before = incompatible.read_bytes()
    monkeypatch.setenv("CHESS_REBUILT_DATABASE_PATH", str(incompatible))
    incompatible_response = client.post(
        "/api/positions/training-requirements/answers",
        json=_answer(),
    )
    assert incompatible_response.status_code == 503
    assert incompatible.read_bytes() == before
