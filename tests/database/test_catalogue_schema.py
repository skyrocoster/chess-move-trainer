from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from chess_move_trainer.database.schema import create_schema


EXPECTED_COLUMNS = {
    "datasource_game": [
        ("dg_game_id", "INTEGER", 1, None, 1),
        ("dg_chesscom_game_uuid", "TEXT", 1, None, 0),
        ("dg_source_url", "TEXT", 1, None, 0),
        ("dg_original_pgn", "TEXT", 1, None, 0),
        ("dg_trainer_color", "TEXT", 1, None, 0),
        ("dg_trainer_chesscom_uuid", "TEXT", 1, None, 0),
        ("dg_opponent_chesscom_uuid", "TEXT", 0, None, 0),
        ("dg_trainer_rating", "INTEGER", 0, None, 0),
        ("dg_opponent_rating", "INTEGER", 0, None, 0),
        ("dg_started_at_utc", "TEXT", 0, None, 0),
        ("dg_ended_at_utc", "TEXT", 0, None, 0),
        ("dg_trainer_outcome", "TEXT", 0, None, 0),
        ("dg_termination_reason", "TEXT", 0, None, 0),
        ("dg_time_control_source", "TEXT", 0, None, 0),
        ("dg_time_class", "TEXT", 0, None, 0),
    ],
    "derived_position": [
        ("dp_position_id", "INTEGER", 1, None, 1),
        ("dp_placement", "TEXT", 1, None, 0),
        ("dp_side_to_move", "TEXT", 1, None, 0),
        ("dp_castling_rights", "TEXT", 1, None, 0),
        ("dp_legal_en_passant", "TEXT", 1, None, 0),
    ],
    "derived_game_position": [
        ("datasource_game_id", "INTEGER", 1, None, 1),
        ("dgp_ply", "INTEGER", 1, None, 2),
        ("derived_position_id", "INTEGER", 1, None, 0),
        ("dgp_move_uci", "TEXT", 0, None, 0),
        ("dgp_halfmove_clock", "INTEGER", 1, None, 0),
        ("dgp_fullmove_number", "INTEGER", 1, None, 0),
    ],
    "datasource_opening": [
        ("do_opening_id", "INTEGER", 1, None, 1),
        ("do_eco", "TEXT", 1, None, 0),
        ("do_name", "TEXT", 1, None, 0),
    ],
    "derived_opening_route": [
        ("dor_route_id", "INTEGER", 1, None, 1),
        ("datasource_opening_id", "INTEGER", 1, None, 0),
        ("derived_position_id", "INTEGER", 1, None, 0),
    ],
    "derived_opening_route_move": [
        ("derived_opening_route_id", "INTEGER", 1, None, 1),
        ("dorm_ply", "INTEGER", 1, None, 2),
        ("dorm_move_uci", "TEXT", 1, None, 0),
    ],
    "derived_analysis_result": [
        ("derived_position_id", "INTEGER", 1, None, 1),
        ("dar_quality", "TEXT", 1, None, 0),
        ("dar_configuration_version", "INTEGER", 1, None, 0),
        ("dar_settings_json", "TEXT", 1, None, 0),
        ("dar_engine_name", "TEXT", 1, None, 0),
        ("dar_engine_version", "TEXT", 1, None, 0),
        ("dar_terminal_kind", "TEXT", 0, None, 0),
    ],
    "derived_analysis_line": [
        ("derived_analysis_result_id", "INTEGER", 1, None, 1),
        ("dal_rank", "INTEGER", 1, None, 2),
        ("dal_score_kind", "TEXT", 1, None, 0),
        ("dal_score_value", "INTEGER", 1, None, 0),
        ("dal_wdl_wins", "INTEGER", 1, None, 0),
        ("dal_wdl_draws", "INTEGER", 1, None, 0),
        ("dal_wdl_losses", "INTEGER", 1, None, 0),
        ("dal_pv_uci_json", "TEXT", 1, None, 0),
        ("dal_depth", "INTEGER", 1, None, 0),
    ],
    "derived_analysis_queue": [
        ("derived_position_id", "INTEGER", 1, None, 1),
        ("daq_requested_quality", "TEXT", 1, None, 0),
        ("daq_state", "TEXT", 1, None, 0),
        ("daq_requested_at_utc", "TEXT", 1, None, 0),
        ("daq_claimed_at_utc", "TEXT", 0, None, 0),
        ("daq_claim_token", "TEXT", 0, None, 0),
    ],
    "datasource_preferred_move_period": [
        ("derived_position_id", "INTEGER", 1, None, 1),
        ("dpm_effective_from", "TEXT", 1, None, 2),
        ("dpm_effective_until", "TEXT", 0, None, 0),
        ("dpm_move_uci", "TEXT", 0, None, 0),
    ],
}

EXPECTED_FOREIGN_KEYS = {
    "derived_game_position": {
        ("datasource_game_id", "datasource_game", "dg_game_id", "RESTRICT"),
        ("derived_position_id", "derived_position", "dp_position_id", "RESTRICT"),
    },
    "derived_opening_route": {
        ("datasource_opening_id", "datasource_opening", "do_opening_id", "RESTRICT"),
        ("derived_position_id", "derived_position", "dp_position_id", "RESTRICT"),
    },
    "derived_opening_route_move": {
        ("derived_opening_route_id", "derived_opening_route", "dor_route_id", "CASCADE"),
    },
    "derived_analysis_result": {
        ("derived_position_id", "derived_position", "dp_position_id", "RESTRICT"),
    },
    "derived_analysis_line": {
        ("derived_analysis_result_id", "derived_analysis_result", "derived_position_id", "CASCADE"),
    },
    "derived_analysis_queue": {
        ("derived_position_id", "derived_position", "dp_position_id", "RESTRICT"),
    },
    "datasource_preferred_move_period": {
        ("derived_position_id", "derived_position", "dp_position_id", "RESTRICT"),
    },
}

EXPECTED_UNIQUE_CONSTRAINTS = {
    "datasource_game": {("dg_chesscom_game_uuid",)},
    "derived_position": {
        ("dp_placement", "dp_side_to_move", "dp_castling_rights", "dp_legal_en_passant"),
    },
    "datasource_opening": {("do_eco", "do_name")},
    "derived_analysis_queue": {("daq_claim_token",)},
}

EXPECTED_CHECKS = {
    "datasource_game": [
        "dg_trainer_color IN ('white','black')",
        "dg_opponent_chesscom_uuid IS NULL OR dg_opponent_chesscom_uuid <> dg_trainer_chesscom_uuid",
        "dg_trainer_outcome IN ('win','loss','draw')",
        "dg_termination_reason IS NULL OR dg_termination_reason NOT IN ('win','loss')",
    ],
    "derived_position": [
        "dp_side_to_move IN ('w','b')",
        "dp_castling_rights IN ('-','K','Q','k','q','KQ','Kk','Kq','Qk','Qq','kq','KQk','KQq','Kkq','Qkq','KQkq')",
        "dp_legal_en_passant = '-' OR dp_legal_en_passant GLOB '[a-h][36]'",
    ],
    "derived_game_position": [
        "dgp_ply >= 0",
        "dgp_move_uci IS NULL OR dgp_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dgp_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]'",
        "dgp_halfmove_clock >= 0",
        "dgp_fullmove_number >= 1",
    ],
    "datasource_opening": ["do_eco GLOB '[A-E][0-9][0-9]'"],
    "derived_opening_route_move": [
        "dorm_ply >= 1",
        "dorm_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dorm_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]'",
    ],
    "derived_analysis_result": [
        "dar_quality IN ('browser','tool')",
        "dar_configuration_version >= 1",
        "json_valid(dar_settings_json)",
        "dar_terminal_kind IS NULL OR dar_terminal_kind IN ('checkmate','stalemate','insufficient_material')",
    ],
    "derived_analysis_line": [
        "dal_rank BETWEEN 1 AND 5",
        "dal_score_kind IN ('cp','mate')",
        "dal_wdl_wins >= 0",
        "dal_wdl_draws >= 0",
        "dal_wdl_losses >= 0",
        "dal_wdl_wins + dal_wdl_draws + dal_wdl_losses = 1000",
        "json_valid(dal_pv_uci_json) AND json_type(dal_pv_uci_json) = 'array' AND json_array_length(dal_pv_uci_json) > 0",
        "dal_depth >= 0",
    ],
    "derived_analysis_queue": [
        "daq_requested_quality IN ('browser','tool')",
        "daq_state IN ('queued','running')",
        "daq_state = 'queued' AND daq_claimed_at_utc IS NULL AND daq_claim_token IS NULL",
        "daq_state = 'running' AND daq_claimed_at_utc IS NOT NULL AND daq_claim_token IS NOT NULL",
    ],
    "datasource_preferred_move_period": [
        "dpm_effective_from GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'",
        "dpm_effective_until IS NULL OR (dpm_effective_until GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'",
        "dpm_move_uci IS NULL OR dpm_move_uci GLOB '[a-h][1-8][a-h][1-8]' OR dpm_move_uci GLOB '[a-h][1-8][a-h][1-8][qrbn]'",
    ],
}

EXPECTED_CHECK_COUNTS = {
    "datasource_game": 4,
    "derived_position": 3,
    "derived_game_position": 4,
    "datasource_opening": 1,
    "derived_opening_route": 0,
    "derived_opening_route_move": 2,
    "derived_analysis_result": 4,
    "derived_analysis_line": 8,
    "derived_analysis_queue": 3,
    "datasource_preferred_move_period": 3,
}


def _normalized_sql(connection: sqlite3.Connection, table: str) -> str:
    sql = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()[0]
    return re.sub(r"\s+", " ", sql).replace(", ", ",").lower()


def test_canonical_resource_is_installed_and_schema_is_exact(tmp_path: Path) -> None:
    database_path = tmp_path / "schema.db"
    create_schema(database_path)

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert tables == set(EXPECTED_COLUMNS)
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"

        selected_indexes = {
            row[1]
            for row in connection.execute(
                "SELECT type, name FROM sqlite_master WHERE type IN ('index', 'trigger', 'view')"
            )
            if not row[1].startswith("sqlite_autoindex")
        }
        assert selected_indexes == set()

        for table, expected_columns in EXPECTED_COLUMNS.items():
            actual_columns = [
                (row[1], row[2], row[3], row[4], row[5])
                for row in connection.execute(f'PRAGMA table_info("{table}")')
            ]
            assert actual_columns == expected_columns

            actual_foreign_keys = {
                (row[3], row[2], row[4], row[6])
                for row in connection.execute(f'PRAGMA foreign_key_list("{table}")')
            }
            assert actual_foreign_keys == EXPECTED_FOREIGN_KEYS.get(table, set())

            normalized = _normalized_sql(connection, table)
            for expected_check in EXPECTED_CHECKS.get(table, []):
                assert expected_check.lower() in normalized
            assert len(re.findall(r"\bcheck\s*\(", normalized)) == EXPECTED_CHECK_COUNTS[table]
            assert connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] == 0


def test_unique_constraints_are_exact_and_internal_autoindexes_only(tmp_path: Path) -> None:
    database_path = tmp_path / "unique.db"
    create_schema(database_path)

    with sqlite3.connect(database_path) as connection:
        for table in EXPECTED_COLUMNS:
            unique_constraints = set()
            for row in connection.execute(f'PRAGMA index_list("{table}")'):
                assert row[1].startswith("sqlite_autoindex_")
                assert row[3] in {"pk", "u"}
                if row[3] == "u":
                    unique_constraints.add(
                        tuple(
                            index_row[2]
                            for index_row in connection.execute(f'PRAGMA index_xinfo("{row[1]}")')
                            if index_row[5]
                        )
                    )
            assert unique_constraints == EXPECTED_UNIQUE_CONSTRAINTS.get(table, set())
