from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from backend.app.caching import clear_caches
from backend.app.dependencies import (
    BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV,
    REBUILT_DATABASE_PATH_ENV,
)
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games.normalization import normalize_game
from chess_move_trainer.database.games.persistence import GameRepository
from chess_move_trainer.database.games.reading import GameReadRepository

TRAINER_UUID = "11111111-1111-4111-8111-111111111111"
OPPONENT_UUID = "99999999-9999-4999-8999-999999999991"
GAME_UUID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1"


def _raw_game() -> dict[str, object]:
    return {
        "uuid": GAME_UUID,
        "url": f"https://www.chess.com/game/live/{GAME_UUID}",
        "rules": "chess",
        "pgn": "\n".join(
            (
                '[Event "trainer blunder API fixture"]',
                '[UTCDate "2026.08.01"]',
                '[UTCTime "12:00:00"]',
                '[EndDate "2026.08.01"]',
                '[EndTime "12:05:00"]',
                '[Result "*"]',
                "",
                "1. e4 e5 2. Nf3 Nc6 *",
            )
        ),
        "white": {"uuid": TRAINER_UUID, "rating": 1500, "result": "win"},
        "black": {"uuid": OPPONENT_UUID, "rating": 1490, "result": "resigned"},
        "time_control": "300+5",
        "time_class": "blitz",
    }


def _add_analysis(
    database: Path,
    position_id: int,
    *,
    quality: str,
    wins: int,
    draws: int,
    losses: int,
    preferred_move: str,
) -> None:
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_analysis_result (
                derived_position_id, dar_quality, dar_configuration_version,
                dar_settings_json, dar_engine_name, dar_engine_version,
                dar_terminal_kind
            ) VALUES (?, ?, 1, '{}', 'fixture', '1', NULL)
            """,
            (position_id, quality),
        )
        connection.execute(
            """
            INSERT INTO derived_analysis_line (
                derived_analysis_result_id, dal_rank, dal_score_kind,
                dal_score_value, dal_wdl_wins, dal_wdl_draws, dal_wdl_losses,
                dal_pv_uci_json, dal_depth
            ) VALUES (?, 1, 'cp', 0, ?, ?, ?, json_array(?), 12)
            """,
            (position_id, wins, draws, losses, preferred_move),
        )


def create_blunder_database(path: Path) -> Path:
    create_schema(path)
    normalized = normalize_game(_raw_game(), UUID(TRAINER_UUID))
    assert normalized.game is not None, normalized.warning
    game_id = GameRepository(path).persist(normalized.game).game_id
    game = GameReadRepository(path).read(game_id)
    assert game is not None
    positions = {occurrence.ply: occurrence.position_id for occurrence in game.occurrences}
    _add_analysis(
        path,
        positions[0],
        quality="browser",
        wins=800,
        draws=100,
        losses=100,
        preferred_move="d2d4",
    )
    _add_analysis(
        path,
        positions[1],
        quality="tool",
        wins=500,
        draws=100,
        losses=400,
        preferred_move="e7e5",
    )
    return path


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    clear_caches()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    clear_caches()


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> tuple[TestClient, Path]:
    database = create_blunder_database(tmp_path / "trainer-blunders.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    monkeypatch.delenv(BLUNDER_MINIMUM_EXPECTED_SCORE_LOSS_ENV, raising=False)
    return client, database
