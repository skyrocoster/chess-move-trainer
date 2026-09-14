from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from backend.app.dependencies import get_training_requirement_policy
from backend.app.main import app
from chess_move_trainer.database.positions import PositionRepository, TrainingRequirementPolicy

from .conftest import TARGET_CANONICAL_FEN, TARGET_FEN


BLACK_TARGET_FEN = (
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
)
BLACK_TARGET_CANONICAL_FEN = " ".join((*BLACK_TARGET_FEN.split()[:4], "0", "1"))


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


def _add_black_training_item(database: Path) -> None:
    position_id = PositionRepository(database).resolve_fen(BLACK_TARGET_FEN)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO datasource_game (
                dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc
            ) VALUES (4, 'training-api-game-4', 'https://example.test/training-api-game-4',
                      '[Result "*"]\n\n*', 'black', 'trainer-4',
                      '2026-01-04T00:00:00Z')
            """
        )
        connection.execute(
            """
            INSERT INTO derived_game_position (
                datasource_game_id, dgp_ply, derived_position_id,
                dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
            ) VALUES (4, 1, ?, 'e7e5', 0, 1)
            """,
            (position_id,),
        )
        connection.execute(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_move_uci
            ) VALUES (?, '2026-01-01', 'd7d5')
            """,
            (position_id,),
        )
        opening_id = connection.execute(
            """
            INSERT INTO datasource_opening (do_eco, do_name)
            VALUES ('B00', 'Black Training Opening')
            RETURNING do_opening_id
            """
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?)
            """,
            (opening_id, position_id),
        )


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


def test_discovery_supports_global_opening_colour_and_combined_due_filters(
    api_context,
) -> None:
    client, database, _position_id = api_context
    _add_black_training_item(database)

    global_due = client.get(
        "/api/positions/training-requirements",
        params={"as_of": "2026-01-15", "training_requirement_lt": 0},
    )
    opening_due = client.get(
        "/api/positions/training-requirements",
        params={
            "as_of": "2026-01-15",
            "training_requirement_lt": 0,
            "opening_key": "A00:Training Opening",
            "opening_match": "reached",
        },
    )
    colour_due = client.get(
        "/api/positions/training-requirements",
        params={
            "as_of": "2026-01-15",
            "training_requirement_lt": 0,
            "trainer_color": "black",
        },
    )
    combined_due = client.get(
        "/api/positions/training-requirements",
        params={
            "as_of": "2026-01-15",
            "training_requirement_lt": 0,
            "trainer_color": "black",
            "opening_key": "B00:Black Training Opening",
            "opening_match": "reached",
        },
    )

    assert all(response.status_code == 200 for response in (
        global_due,
        opening_due,
        colour_due,
        combined_due,
    ))
    assert len(global_due.json()["items"]) == 2
    assert all(item["training_required"] for item in global_due.json()["items"])
    assert {item["trainer_color"] for item in opening_due.json()["items"]} == {"white"}
    assert {item["trainer_color"] for item in colour_due.json()["items"]} == {"black"}
    assert combined_due.json()["items"] == [
        {
            "fen": BLACK_TARGET_CANONICAL_FEN,
            "trainer_color": "black",
            "preferred_move_uci": "d7d5",
            "encounters": 1,
            "hits": 0,
            "misses": 1,
            "observed_success_rate": 0.0,
            "game_balance": -4.0,
            "effective_training_balance": 0.0,
            "training_adjustment": 0.0,
            "training_updated_on": None,
            "training_requirement": -4.0,
            "training_required": True,
            "correct_answers_needed": 2,
        }
    ]
    assert set(combined_due.json()) == {
        "as_of",
        "scoring_policy",
        "items",
        "page",
        "page_size",
        "total",
    }


def test_discovery_valid_combined_filters_can_return_empty_page(api_context) -> None:
    client, database, _position_id = api_context
    _add_black_training_item(database)

    response = client.get(
        "/api/positions/training-requirements",
        params={
            "as_of": "2026-01-15",
            "training_requirement_lt": 0,
            "trainer_color": "black",
            "opening_key": "A00:Training Opening",
            "opening_match": "reached",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_discovery_rejects_invalid_trainer_color_with_contract_error(api_context) -> None:
    client, _database, _position_id = api_context

    response = client.get(
        "/api/positions/training-requirements",
        params=_query(trainer_color="purple"),
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "invalid_trainer_color",
        "message": "trainer_color must be 'white' or 'black'",
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
