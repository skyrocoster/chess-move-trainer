from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from chess_move_trainer.database.lifecycle import DEFAULT_DATABASE_PATH


pytestmark = pytest.mark.skipif(
    os.environ.get("CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE") != "1",
    reason="opt-in real-database fidelity smoke",
)


def test_real_database_training_requirement_anchor(monkeypatch: pytest.MonkeyPatch) -> None:
    database = Path(DEFAULT_DATABASE_PATH)
    before = database.read_bytes()
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    app.dependency_overrides.clear()
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/positions/training-requirements",
                params={
                    "as_of": "2026-09-12",
                    "training_requirement_lt": 0,
                    "opening_key": "B02:Alekhine Defense",
                    "opening_match": "reached",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["as_of"] == "2026-09-12"
    matching_items = [
        candidate
        for candidate in body["items"]
        if candidate["fen"]
        == "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
        and candidate["trainer_color"] == "white"
        and candidate["preferred_move_uci"] == "b1c3"
    ]
    assert len(matching_items) == 1
    item = matching_items[0]
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
    assert item == {
        "fen": "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
        "trainer_color": "white",
        "preferred_move_uci": "b1c3",
        "encounters": 86,
        "hits": 28,
        "misses": 58,
        "observed_success_rate": round(28 / 86, 6),
        "game_balance": -204.0,
        "effective_training_balance": 0.0,
        "training_adjustment": 0.0,
        "training_updated_on": None,
        "training_requirement": -204.0,
        "training_required": True,
        "correct_answers_needed": 15,
    }
    assert database.read_bytes() == before


def test_real_database_caro_reached_scope_includes_deeper_variation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Path(DEFAULT_DATABASE_PATH)
    before = database.read_bytes()
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    base_key = "B10:Caro-Kann Defense"
    request = {
        "as_of": "2026-09-14",
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
    assert reached["as_of"] == "2026-09-14"
    assert reached["page"] == 1
    assert reached["page_size"] == 100

    representative_fen = (
        "rnbqkbnr/pp2pppp/8/3p4/8/1B6/PPPP1PPP/RNBQK1NR b KQkq - 0 1"
    )
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
