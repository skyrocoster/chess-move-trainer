from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import schema as schema_service
from chess_move_trainer.database.schema import (
    create_schema,
    upgrade_schema,
)

ROOT = Path(__file__).parents[2]
PACKAGE_PATH = ROOT / "src" / "chess_move_trainer" / "database"
V1_RESOURCE = PACKAGE_PATH / "schema_v1.sql"


def _create_v1_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript(V1_RESOURCE.read_text(encoding="utf-8"))
        connection.execute(
            "INSERT INTO derived_position "
            "(dp_position_id, dp_placement, dp_side_to_move, "
            "dp_castling_rights, dp_legal_en_passant) "
            "VALUES (1, ?, 'w', 'KQkq', '-')",
            ("8/8/8/8/8/8/8/8",),
        )
        connection.execute(
            "INSERT INTO datasource_game "
            "(dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn, "
            "dg_trainer_color, dg_trainer_chesscom_uuid) "
            "VALUES (1, 'game-1', 'https://example.test/game-1', '[Event \"test\"]', "
            "'white', 'trainer')"
        )
        connection.execute(
            "INSERT INTO derived_game_position "
            "(datasource_game_id, dgp_ply, derived_position_id, dgp_move_uci, "
            "dgp_halfmove_clock, dgp_fullmove_number) "
            "VALUES (1, 0, 1, 'e2e4', 0, 1)"
        )
        connection.execute(
            "INSERT INTO datasource_opening (do_opening_id, do_eco, do_name) "
            "VALUES (1, 'A00', 'Test opening')"
        )
        connection.execute(
            "INSERT INTO derived_opening_route "
            "(dor_route_id, datasource_opening_id, derived_position_id) VALUES (1, 1, 1)"
        )
        connection.execute(
            "INSERT INTO derived_opening_route_move "
            "(derived_opening_route_id, dorm_ply, dorm_move_uci) VALUES (1, 1, 'e2e4')"
        )
        connection.execute(
            "INSERT INTO derived_analysis_result "
            "(derived_position_id, dar_quality, dar_configuration_version, dar_settings_json, "
            "dar_engine_name, dar_engine_version) "
            "VALUES (1, 'browser', 1, '{}', 'test', '1')"
        )
        connection.execute(
            "INSERT INTO derived_analysis_line "
            "(derived_analysis_result_id, dal_rank, dal_score_kind, dal_score_value, "
            "dal_wdl_wins, dal_wdl_draws, dal_wdl_losses, dal_pv_uci_json, dal_depth) "
            "VALUES (1, 1, 'cp', 0, 333, 334, 333, '[\"e2e4\"]', 1)"
        )
        connection.execute(
            "INSERT INTO derived_analysis_queue "
            "(derived_position_id, daq_requested_quality, daq_state, daq_requested_at_utc) "
            "VALUES (1, 'browser', 'queued', '2026-09-12T00:00:00Z')"
        )
        connection.execute(
            "INSERT INTO datasource_preferred_move_period "
            "(derived_position_id, dpm_effective_from, dpm_move_uci) "
            "VALUES (1, '2026-01-01', 'e2e4')"
        )


def _data_snapshot(path: Path) -> dict[str, list[tuple[object, ...]]]:
    tables = (
        "datasource_game",
        "derived_position",
        "derived_game_position",
        "datasource_opening",
        "derived_opening_route",
        "derived_opening_route_move",
        "derived_analysis_result",
        "derived_analysis_line",
        "derived_analysis_queue",
        "datasource_preferred_move_period",
    )
    with sqlite3.connect(path) as connection:
        return {
            table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table}")]
            for table in tables
        }


def test_exact_v1_upgrade_preserves_rows_and_starts_empty_aggregate(tmp_path: Path) -> None:
    database_path = tmp_path / "v1.db"
    _create_v1_database(database_path)
    before = _data_snapshot(database_path)

    result = upgrade_schema(database_path)

    assert result.upgraded is True
    assert _data_snapshot(database_path) == before
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM derived_position_training_aggregate"
            ).fetchone()[0]
            == 0
        )
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []

        connection.execute(
            "INSERT INTO derived_position_training_aggregate "
            "(derived_position_id, dpta_preferred_move_uci, "
            "dpta_training_balance, dpta_updated_on) "
            "VALUES (1, 'e2e4', CAST(? AS REAL), ?)",
            ("-1.25", "2026-09-12"),
        )
        assert connection.execute(
            "SELECT dpta_training_balance, dpta_updated_on FROM derived_position_training_aggregate"
        ).fetchone() == (-1.25, "2026-09-12")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO derived_position_training_aggregate "
                "(derived_position_id, dpta_preferred_move_uci, dpta_training_balance) "
                "VALUES (99, 'e2e4', CAST(0 AS REAL))"
            )


def test_exact_v2_upgrade_is_a_byte_preserving_no_op(tmp_path: Path) -> None:
    database_path = tmp_path / "v2.db"
    create_schema(database_path)
    before = database_path.read_bytes()

    result = upgrade_schema(database_path)

    assert result.upgraded is False
    assert database_path.read_bytes() == before


@pytest.mark.parametrize("kind", ["unknown", "malformed"])
def test_unknown_or_malformed_upgrade_target_is_rejected_unchanged(
    tmp_path: Path,
    kind: str,
) -> None:
    database_path = tmp_path / f"{kind}.db"
    if kind == "unknown":
        with sqlite3.connect(database_path) as connection:
            connection.execute("CREATE TABLE unrelated (value TEXT)")
            connection.execute("PRAGMA user_version = 99")
    else:
        database_path.write_bytes(b"not sqlite")
    before = database_path.read_bytes()

    with pytest.raises(Exception):
        upgrade_schema(database_path)

    assert database_path.read_bytes() == before


def test_interrupted_upgrade_rolls_back_additive_ddl_and_version(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "interrupted.db"
    _create_v1_database(database_path)
    before = _data_snapshot(database_path)
    original_resource = schema_service._execute_schema_resource

    def interrupt_after_resource(connection: object, resource_name: str = "schema_v2.sql") -> None:
        if resource_name == schema_service._UPGRADE_RESOURCE_NAME:
            original_resource(connection, resource_name)
            raise KeyboardInterrupt
        original_resource(connection, resource_name)

    monkeypatch.setattr(schema_service, "_execute_schema_resource", interrupt_after_resource)

    with pytest.raises(KeyboardInterrupt):
        upgrade_schema(database_path)

    assert _data_snapshot(database_path) == before
    with sqlite3.connect(database_path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'derived_position_training_aggregate'"
            ).fetchone()
            is None
        )
