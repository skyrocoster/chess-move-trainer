from __future__ import annotations

import os
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
