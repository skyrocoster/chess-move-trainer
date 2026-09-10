from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import REBUILT_DATABASE_PATH_ENV
from backend.app.main import app
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import PositionRepository

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
TARGET_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
TARGET_CANONICAL_FEN = " ".join((*TARGET_FEN.split()[:4], "0", "1"))
TARGET_WITH_COUNTERS = " ".join((*TARGET_FEN.split()[:4], "99", "120"))
OTHER_COLOR_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
OTHER_COLOR_CANONICAL_FEN = " ".join((*OTHER_COLOR_FEN.split()[:4], "0", "1"))
UNSEEN_FEN = STARTING_FEN
UNSEEN_CANONICAL_FEN = " ".join((*UNSEEN_FEN.split()[:4], "0", "1"))


def _position_id(database: Path, fen: str) -> int:
    return PositionRepository(database).resolve_fen(fen)


def _game(connection: sqlite3.Connection, game_id: int, color: str) -> None:
    connection.execute(
        """
        INSERT INTO datasource_game (
            dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
            dg_trainer_color, dg_trainer_chesscom_uuid
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            game_id,
            f"game-{game_id}",
            f"https://example.test/game-{game_id}",
            '[Result "*"]\n\n*',
            color,
            f"trainer-{game_id}",
        ),
    )


def _occurrence(
    connection: sqlite3.Connection,
    game_id: int,
    ply: int,
    position_id: int,
    move_uci: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO derived_game_position (
            datasource_game_id, dgp_ply, derived_position_id,
            dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
        ) VALUES (?, ?, ?, ?, 0, 1)
        """,
        (game_id, ply, position_id, move_uci),
    )


def _install_opening(connection: sqlite3.Connection, position_id: int) -> None:
    opening = connection.execute(
        """
        INSERT INTO datasource_opening (do_eco, do_name)
        VALUES ('C20', 'King''s Pawn Game')
        RETURNING do_opening_id
        """
    ).fetchone()[0]
    route = connection.execute(
        """
        INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
        VALUES (?, ?)
        RETURNING dor_route_id
        """,
        (opening, position_id),
    ).fetchone()[0]
    connection.executemany(
        """
        INSERT INTO derived_opening_route_move
            (derived_opening_route_id, dorm_ply, dorm_move_uci)
        VALUES (?, ?, ?)
        """,
        ((route, 1, "e2e4"), (route, 2, "e7e5")),
    )


def _install_analysis(connection: sqlite3.Connection, position_id: int) -> None:
    connection.execute(
        """
        INSERT INTO derived_analysis_result (
            derived_position_id, dar_quality, dar_configuration_version,
            dar_settings_json, dar_engine_name, dar_engine_version, dar_terminal_kind
        ) VALUES (?, 'tool', 7, ?, 'Stockfish', '18', NULL)
        """,
        (position_id, json.dumps({"Hash": 16})),
    )
    connection.execute(
        """
        INSERT INTO derived_analysis_line (
            derived_analysis_result_id, dal_rank, dal_score_kind, dal_score_value,
            dal_wdl_wins, dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json, dal_depth
        ) VALUES (?, 1, 'cp', 34, 450, 300, 250, '["a2a3"]', 22)
        """,
        (position_id,),
    )


def _install_preferences(connection: sqlite3.Connection, position_id: int) -> None:
    connection.executemany(
        """
        INSERT INTO datasource_preferred_move_period (
            derived_position_id, dpm_effective_from, dpm_effective_until, dpm_move_uci
        ) VALUES (?, ?, ?, ?)
        """,
        (
            (position_id, "2026-01-01", "2026-02-01", "a2a3"),
            (position_id, "2026-02-01", "2026-03-01", None),
            (position_id, "2026-03-01", None, "b2b3"),
        ),
    )


def create_insight_database(path: Path) -> Path:
    create_schema(path)
    position_id = _position_id(path, TARGET_FEN)
    other_color_position_id = _position_id(path, OTHER_COLOR_FEN)
    with sqlite3.connect(path) as connection:
        _game(connection, 1, "white")
        _game(connection, 2, "white")
        _game(connection, 3, "black")
        _game(connection, 4, "black")
        _game(connection, 5, "white")
        _occurrence(connection, 1, 2, position_id, "a2a3")
        _occurrence(connection, 1, 4, position_id, "a2a3")
        _occurrence(connection, 2, 2, position_id, "b2b3")
        _occurrence(connection, 3, 2, position_id, "a2a3")
        _occurrence(connection, 4, 2, position_id, None)
        _occurrence(connection, 3, 6, other_color_position_id, "e2e4")
        _install_opening(connection, position_id)
        _install_analysis(connection, position_id)
        _install_preferences(connection, position_id)
    return path


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def api_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> tuple[TestClient, Path]:
    database = create_insight_database(tmp_path / "position-insight.db")
    monkeypatch.setenv(REBUILT_DATABASE_PATH_ENV, str(database))
    return client, database
