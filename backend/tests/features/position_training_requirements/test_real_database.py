from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from chess_move_trainer.database.lifecycle import HOST_SEED_DATABASE_PATH

REAL_AS_OF = datetime.now(timezone.utc).date().isoformat()

pytestmark = pytest.mark.skipif(
    os.environ.get("CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE") != "1",
    reason="opt-in real-database fidelity smoke",
)


def test_real_database_training_requirement_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    database = Path(HOST_SEED_DATABASE_PATH)
    if not database.exists():
        pytest.skip(f"real database not found: {database}")
    before = database.read_bytes()
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    app.dependency_overrides.clear()
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/positions/training-requirements",
                params={
                    "as_of": REAL_AS_OF,
                    "training_requirement_gte": -1e300,
                    "page": 1,
                    "page_size": 100,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"as_of", "scoring_policy", "items", "page", "page_size", "total"}
    assert body["as_of"] == REAL_AS_OF
    assert body["page"] == 1
    assert body["page_size"] == 100
    assert body["total"] >= len(body["items"]) > 0
    item = body["items"][0]
    assert set(item) == {
        "fen",
        "trainer_color",
        "preferred_move_uci",
        "encounters",
        "hits",
        "misses",
        "observed_success_rate",
        "game_balance",
        "effective_training_balance",
        "training_adjustment",
        "training_updated_on",
        "training_requirement",
        "training_required",
        "correct_answers_needed",
    }
    assert item["trainer_color"] in {"white", "black"}
    assert item["encounters"] == item["hits"] + item["misses"]
    assert item["observed_success_rate"] == pytest.approx(
        item["hits"] / item["encounters"], abs=1e-6
    )
    assert item["training_requirement"] == pytest.approx(
        item["game_balance"] + item["training_adjustment"], abs=2e-6
    )
    assert item["training_required"] is (item["training_requirement"] < 0)
    if item["training_required"]:
        assert item["correct_answers_needed"] > 0
    else:
        assert item["correct_answers_needed"] == 0
    assert database.read_bytes() == before


def test_real_database_caro_reached_scope_includes_deeper_variation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Path(HOST_SEED_DATABASE_PATH)
    if not database.exists():
        pytest.skip(f"real database not found: {database}")
    before = database.read_bytes()
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    base_key = "B10:Caro-Kann Defense"
    request = {
        "as_of": REAL_AS_OF,
        "training_requirement_lt": 0,
        "opening_key": base_key,
        "opening_match": "reached",
        "page": 1,
        "page_size": 100,
    }

    app.dependency_overrides.clear()
    try:
        with TestClient(app) as client:
            reached_response = client.get(
                "/api/positions/training-requirements",
                params=request,
            )
            deepest_response = client.get(
                "/api/positions/training-requirements",
                params={**request, "opening_match": "deepest"},
            )
    finally:
        app.dependency_overrides.clear()

    assert reached_response.status_code == 200
    assert deepest_response.status_code == 200
    reached = reached_response.json()
    deepest = deepest_response.json()
    assert set(reached) == {"as_of", "scoring_policy", "items", "page", "page_size", "total"}
    assert reached["as_of"] == REAL_AS_OF
    assert reached["page"] == 1
    assert reached["page_size"] == 100

    representative_fen = "rnbqkbnr/pp2pppp/8/3p4/8/1B6/PPPP1PPP/RNBQK1NR b KQkq - 0 1"
    representative = next(
        item
        for item in reached["items"]
        if item["fen"] == representative_fen
        and item["trainer_color"] == "black"
        and item["preferred_move_uci"] == "g8f6"
    )
    assert representative["training_required"] is True
    assert not any(
        item["fen"] == representative_fen
        and item["trainer_color"] == "black"
        and item["preferred_move_uci"] == "g8f6"
        for item in deepest["items"]
    )

    placement, side_to_move, castling_rights, legal_en_passant, *_ = representative_fen.split()
    with sqlite3.connect(database) as connection:
        games_with_base_and_deeper_routes = connection.execute(
            """
            SELECT DISTINCT target_occurrence.datasource_game_id
            FROM derived_game_position AS target_occurrence
            JOIN derived_position AS target_position
              ON target_position.dp_position_id = target_occurrence.derived_position_id
            WHERE target_position.dp_placement = ?
              AND target_position.dp_side_to_move = ?
              AND target_position.dp_castling_rights = ?
              AND target_position.dp_legal_en_passant = ?
              AND EXISTS (
                  SELECT 1
                  FROM derived_game_position AS base_occurrence
                  JOIN derived_opening_route AS base_route
                    ON base_route.derived_position_id = base_occurrence.derived_position_id
                  JOIN datasource_opening AS base_opening
                    ON base_opening.do_opening_id = base_route.datasource_opening_id
                  WHERE base_occurrence.datasource_game_id = target_occurrence.datasource_game_id
                    AND base_opening.do_eco = 'B10'
                    AND base_opening.do_name = 'Caro-Kann Defense'
              )
              AND EXISTS (
                  SELECT 1
                  FROM derived_game_position AS deeper_occurrence
                  JOIN derived_opening_route AS deeper_route
                    ON deeper_route.derived_position_id = deeper_occurrence.derived_position_id
                  JOIN datasource_opening AS deeper_opening
                    ON deeper_opening.do_opening_id = deeper_route.datasource_opening_id
                  WHERE deeper_occurrence.datasource_game_id = target_occurrence.datasource_game_id
                    AND deeper_opening.do_eco = 'B10'
                    AND deeper_opening.do_name LIKE 'Caro-Kann Defense:%'
              )
            """,
            (placement, side_to_move, castling_rights, legal_en_passant),
        ).fetchall()

    assert games_with_base_and_deeper_routes
    assert database.read_bytes() == before
