from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.app.features.health.database_probe import (
    AnalysisBacklog,
    read_database_health,
)
from chess_move_trainer.database.schema import create_schema


def test_missing_database_returns_none(tmp_path: Path) -> None:
    assert read_database_health(tmp_path / "missing.db") is None


def test_directory_without_database_returns_none(tmp_path: Path) -> None:
    assert read_database_health(tmp_path) is None


def test_empty_schema_reports_zero_backlog(tmp_path: Path) -> None:
    database = tmp_path / "chess.db"
    create_schema(database)

    health = read_database_health(database)

    assert health is not None
    assert health.analysis == AnalysisBacklog(
        positions=0, analyzed=0, queued=0, running=0, remaining=0
    )
    assert health.last_game_at is None


def test_counts_and_remaining_are_computed_from_the_schema(tmp_path: Path) -> None:
    database = tmp_path / "chess.db"
    create_schema(database)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "INSERT INTO derived_position (dp_position_id, dp_placement, dp_side_to_move, "
            "dp_castling_rights, dp_legal_en_passant) VALUES "
            "(1, '8/8/8/8/8/8/8/K6k', 'w', '-', '-'), "
            "(2, '8/8/8/8/8/8/8/K5k', 'b', '-', '-'), "
            "(3, '8/8/8/8/8/8/8/K4k', 'w', '-', '-')"
        )
        connection.execute(
            "INSERT INTO datasource_game (dg_game_id, dg_chesscom_game_uuid, dg_source_url, "
            "dg_original_pgn, dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc) "
            "VALUES (1, 'uuid-1', 'https://example.test/g/1', '1. e4', 'white', "
            "'trainer-uuid', '2026-09-20T12:00:00+00:00')"
        )
        connection.execute(
            "INSERT INTO derived_analysis_result (derived_position_id, dar_quality, "
            "dar_configuration_version, dar_settings_json, dar_engine_name, dar_engine_version) "
            "VALUES (1, 'tool', 1, '{}', 'Stockfish', '17')"
        )
        connection.execute(
            "INSERT INTO derived_analysis_queue (derived_position_id, daq_requested_quality, "
            "daq_state, daq_requested_at_utc, daq_claimed_at_utc, daq_claim_token) "
            "VALUES (2, 'tool', 'running', '2026-09-21T00:00:00+00:00', "
            "'2026-09-21T00:01:00+00:00', 'token-2')"
        )
        connection.commit()

    health = read_database_health(database)

    assert health is not None
    assert health.analysis == AnalysisBacklog(
        positions=3, analyzed=1, queued=0, running=1, remaining=1
    )
    assert health.last_game_at == "2026-09-20T12:00:00+00:00"
