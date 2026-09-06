from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli
from chess_move_trainer.database import create_schema
from chess_move_trainer.database.rebuild import (
    MAX_RETAINED_SNAPSHOTS,
    RebuildConfiguration,
    SnapshotOutcome,
    VerificationStatus,
    VerificationTarget,
    create_snapshot,
    verify_rebuild_target,
)
import chess_move_trainer.database.rebuild.snapshots as snapshot_service


def _schema_database(tmp_path: Path, name: str = "neighbour.db") -> Path:
    path = tmp_path / name
    create_schema(path)
    return path


def _add_openings(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            "INSERT INTO derived_position "
            "(dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant) "
            "VALUES ('8/8/8/8/8/8/8/8', 'w', '-', '-')"
        )
        position_id = connection.execute(
            "SELECT dp_position_id FROM derived_position"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('A00', 'Snapshot opening')"
        )
        opening_id = connection.execute(
            "SELECT do_opening_id FROM datasource_opening"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO derived_opening_route "
            "(datasource_opening_id, derived_position_id) VALUES (?, ?)",
            (opening_id, position_id),
        )
        route_id = connection.execute(
            "SELECT dor_route_id FROM derived_opening_route"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO derived_opening_route_move "
            "(derived_opening_route_id, dorm_ply, dorm_move_uci) VALUES (?, 1, 'e2e4')",
            (route_id,),
        )


def _add_game(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        position_id = connection.execute(
            "SELECT dp_position_id FROM derived_position LIMIT 1"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO datasource_game "
            "(dg_chesscom_game_uuid, dg_source_url, dg_original_pgn, "
            "dg_trainer_color, dg_trainer_chesscom_uuid) "
            "VALUES ('00000000-0000-4000-8000-000000000001', 'https://example.test/1', "
            "'1. e4 *', 'white', '11111111-1111-4111-8111-111111111111')"
        )
        game_id = connection.execute(
            "SELECT dg_game_id FROM datasource_game"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO derived_game_position "
            "(datasource_game_id, dgp_ply, derived_position_id, dgp_move_uci, "
            "dgp_halfmove_clock, dgp_fullmove_number) VALUES (?, 0, ?, NULL, 0, 1)",
            (game_id, position_id),
        )


def _ready_database(tmp_path: Path) -> Path:
    database = _schema_database(tmp_path)
    _add_openings(database)
    _add_game(database)
    return database


def test_fresh_snapshot_is_atomic_verified_and_read_only_to_the_neighbour(
    tmp_path: Path,
) -> None:
    neighbour = _ready_database(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    before = neighbour.read_bytes()

    outcome = create_snapshot(configuration)

    assert outcome.completed
    assert outcome.snapshot_path is not None
    assert outcome.snapshot_path.exists()
    assert outcome.snapshot_path.parent == neighbour.parent
    assert outcome.snapshot_path != neighbour
    assert outcome.verification is not None
    assert outcome.verification.target is VerificationTarget.SNAPSHOT
    assert outcome.verification.status is VerificationStatus.REPLACEMENT_READY
    assert neighbour.read_bytes() == before
    assert not tuple(neighbour.parent.glob(f".{outcome.snapshot_path.name}.*.tmp"))

    checked = verify_rebuild_target(
        configuration,
        VerificationTarget.SNAPSHOT,
        snapshot_path=outcome.snapshot_path,
    )
    assert checked.replacement_ready


def test_snapshot_backup_includes_committed_wal_content(tmp_path: Path) -> None:
    neighbour = _ready_database(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    connection = sqlite3.connect(neighbour)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA wal_autocheckpoint=0")
        connection.execute(
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('B00', 'WAL opening')"
        )
        connection.commit()
        wal_path = Path(f"{neighbour}-wal")
        assert wal_path.exists()

        outcome = create_snapshot(configuration)

        assert outcome.completed
        assert outcome.snapshot_path is not None
        with sqlite3.connect(outcome.snapshot_path) as snapshot:
            assert snapshot.execute(
                "SELECT COUNT(*) FROM datasource_opening WHERE do_name = 'WAL opening'"
            ).fetchone()[0] == 1
    finally:
        connection.close()


def test_rolling_retention_keeps_only_three_newest_verified_snapshots(
    tmp_path: Path,
) -> None:
    neighbour = _ready_database(tmp_path)
    configuration = RebuildConfiguration(neighbour)

    outcomes = [create_snapshot(configuration) for _ in range(4)]

    assert all(outcome.completed for outcome in outcomes)
    paths = tuple(
        sorted(
            neighbour.parent.glob(f"{neighbour.name}.snapshot-*.db"),
            key=lambda path: path.name,
            reverse=True,
        )
    )
    assert len(paths) == MAX_RETAINED_SNAPSHOTS
    assert paths == tuple(
        reversed(tuple(outcome.snapshot_path for outcome in outcomes[-3:]))
    )
    assert all(
        verify_rebuild_target(
            configuration,
            VerificationTarget.SNAPSHOT,
            snapshot_path=path,
        ).structurally_valid
        for path in paths
    )


def test_failed_snapshot_does_not_delete_verified_history_or_leave_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    neighbour = _ready_database(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    first = create_snapshot(configuration)
    assert first.completed
    before = tuple(neighbour.parent.glob(f"{neighbour.name}.snapshot-*.db"))

    def fail_backup(*_: object, **__: object) -> None:
        raise OSError("synthetic backup failure")

    monkeypatch.setattr(snapshot_service, "_backup_database", fail_backup)
    failed = create_snapshot(configuration)

    assert not failed.completed
    assert "backup failure" in failed.message
    assert tuple(neighbour.parent.glob(f"{neighbour.name}.snapshot-*.db")) == before
    assert not tuple(neighbour.parent.glob(f".{neighbour.name}.snapshot-*.db.*.tmp"))


def test_snapshot_cli_has_standalone_verified_json_output(tmp_path: Path) -> None:
    neighbour = _schema_database(tmp_path)
    config = tmp_path / "rebuild.yaml"
    config.write_text(f"rebuilt_neighbour: {neighbour}\n", encoding="utf-8")

    result = CliRunner().invoke(
        database_cli.app,
        ["rebuild", "snapshot", "--config", str(config), "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["operation"] == "snapshot"
    assert payload["status"] == "succeeded"
    assert Path(payload["snapshot_path"]).exists()
    assert result.stderr == ""
