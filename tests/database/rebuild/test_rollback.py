from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.rebuild import (
    MAX_RETAINED_SNAPSHOTS,
    OperationExitCode,
    OperationStatus,
    RebuildConfiguration,
    RollbackInputError,
    create_snapshot,
    rollback_rebuilt_neighbour,
)
import chess_move_trainer.database.rebuild.rollback as rollback_service


def _ready_database(tmp_path: Path) -> Path:
    path = tmp_path / "neighbour.db"
    create_schema(path)
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
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('A00', 'rollback')"
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
        connection.execute(
            "INSERT INTO datasource_game "
            "(dg_chesscom_game_uuid, dg_source_url, dg_original_pgn, "
            "dg_trainer_color, dg_trainer_chesscom_uuid) VALUES "
            "('00000000-0000-4000-8000-000000000001', 'https://example.test/1', "
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
    connection.close()
    return path


def _change_marker(path: Path, marker: str) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE datasource_opening SET do_name = ? WHERE do_eco = 'A00'",
            (marker,),
        )
    connection.close()


def _opening_name(path: Path) -> str:
    with sqlite3.connect(path) as connection:
        value = str(
            connection.execute(
                "SELECT do_name FROM datasource_opening ORDER BY do_opening_id LIMIT 1"
            ).fetchone()[0]
        )
    connection.close()
    return value


def _hold_sqlite_connection(
    database: Path, signal: Path, release: Path
) -> subprocess.Popen[str]:
    code = """
import sqlite3
import sys
import time
from pathlib import Path

connection = sqlite3.connect(sys.argv[1], timeout=0)
Path(sys.argv[2]).write_text('acquired', encoding='ascii')
try:
    while not Path(sys.argv[3]).exists():
        time.sleep(0.01)
finally:
    connection.close()
"""
    return subprocess.Popen(
        [
            sys.executable,
            "-c",
            code,
            str(database),
            str(signal),
            str(release),
        ],
        cwd=Path(__file__).parents[3],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _three_snapshots(
    tmp_path: Path,
) -> tuple[RebuildConfiguration, tuple[Path, ...]]:
    neighbour = _ready_database(tmp_path)
    configuration = RebuildConfiguration(neighbour)
    snapshots: list[Path] = []
    for index in range(MAX_RETAINED_SNAPSHOTS):
        if index:
            _change_marker(neighbour, f"version-{index}")
        outcome = create_snapshot(configuration)
        assert outcome.completed and outcome.snapshot_path is not None
        snapshots.append(outcome.snapshot_path)
    return configuration, tuple(snapshots)


def test_busy_neighbour_fails_without_terminating_owner(tmp_path: Path) -> None:
    if os.name != "nt":
        pytest.skip("DB-08 destination mutex is Windows-only")
    configuration, _ = _three_snapshots(tmp_path)
    before = configuration.rebuilt_neighbour.read_bytes()
    signal = tmp_path / "owner.signal"
    release = tmp_path / "owner.release"
    snapshots_before = {path: path.read_bytes() for path in tuple(tmp_path.glob("neighbour.db.snapshot-*.db"))}
    owner = _hold_sqlite_connection(configuration.rebuilt_neighbour, signal, release)
    deadline = time.monotonic() + 5
    while not signal.exists() and owner.poll() is None and time.monotonic() < deadline:
        time.sleep(0.01)
    assert signal.exists()
    try:
        outcome = rollback_rebuilt_neighbour(configuration)
        assert outcome.status is OperationStatus.FAILED
        assert outcome.exit_code == OperationExitCode.FAILED
        assert "exclusive access" in outcome.message
        assert configuration.rebuilt_neighbour.read_bytes() == before
        assert {
            path: path.read_bytes()
            for path in tuple(tmp_path.glob("neighbour.db.snapshot-*.db"))
        } == snapshots_before
        assert owner.poll() is None
    finally:
        release.write_text("release", encoding="ascii")
        owner.wait(timeout=5)


def test_default_rollback_restores_newest_and_preserves_current_neighbour(
    tmp_path: Path,
) -> None:
    configuration, snapshots = _three_snapshots(tmp_path)
    _change_marker(configuration.rebuilt_neighbour, "current-before-rollback")
    current_before = _opening_name(configuration.rebuilt_neighbour)
    newest_before = snapshots[-1].read_bytes()

    outcome = rollback_rebuilt_neighbour(configuration)

    assert outcome.completed
    assert outcome.selected_snapshot == snapshots[-1]
    assert configuration.rebuilt_neighbour.read_bytes() == newest_before
    assert outcome.snapshot_path is not None and outcome.snapshot_path.exists()
    assert _opening_name(outcome.snapshot_path) == current_before
    assert len(tuple(tmp_path.glob("neighbour.db.snapshot-*.db"))) == MAX_RETAINED_SNAPSHOTS


def test_explicit_older_retained_snapshot_is_allowed_and_unretained_is_rejected(
    tmp_path: Path,
) -> None:
    configuration, snapshots = _three_snapshots(tmp_path)
    _change_marker(configuration.rebuilt_neighbour, "current-before-rollback")
    selected_bytes = snapshots[0].read_bytes()

    outcome = rollback_rebuilt_neighbour(
        configuration,
        snapshot_path=snapshots[0],
    )

    assert outcome.completed
    assert configuration.rebuilt_neighbour.read_bytes() == selected_bytes

    arbitrary = tmp_path / "arbitrary-source.db"
    arbitrary.write_bytes(selected_bytes)
    with pytest.raises(RollbackInputError, match="retained"):
        rollback_rebuilt_neighbour(configuration, snapshot_path=arbitrary)


def test_rollback_reverifies_source_before_preserving_current_neighbour(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configuration, snapshots = _three_snapshots(tmp_path)
    calls: list[tuple[object, Path | None]] = []
    original = rollback_service.verify_rebuild_target

    def verify(*args: object, **kwargs: object):
        target = kwargs.get("target")
        selected = kwargs.get("snapshot_path")
        calls.append((target, selected if isinstance(selected, Path) else None))
        return original(*args, **kwargs)

    monkeypatch.setattr(rollback_service, "verify_rebuild_target", verify)
    outcome = rollback_rebuilt_neighbour(configuration, snapshot_path=snapshots[-1])

    assert outcome.completed
    selected_calls = [path for _, path in calls if path == snapshots[-1]]
    assert len(selected_calls) >= 2


def test_failed_rollback_swap_preserves_neighbour_and_snapshot_recovery_point(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configuration, snapshots = _three_snapshots(tmp_path)
    _change_marker(configuration.rebuilt_neighbour, "current-before-rollback")
    before = configuration.rebuilt_neighbour.read_bytes()

    def fail_swap(*_: object, **__: object) -> None:
        raise OSError("synthetic rollback swap failure")

    monkeypatch.setattr(rollback_service, "_atomic_replace", fail_swap)
    outcome = rollback_rebuilt_neighbour(configuration, snapshot_path=snapshots[-1])

    assert not outcome.completed
    assert "rollback swap failure" in outcome.message
    assert outcome.snapshot is not None and outcome.snapshot.completed
    assert outcome.snapshot_path is not None and outcome.snapshot_path.exists()
    assert configuration.rebuilt_neighbour.read_bytes() == before
    assert not tuple(tmp_path.glob(".rollback-source-*.tmp"))


def test_rollback_does_not_read_or_modify_old_database(tmp_path: Path) -> None:
    configuration, snapshots = _three_snapshots(tmp_path)
    old_database = tmp_path / "old-database.db"
    old_database.write_bytes(b"old database sentinel")
    old_before = old_database.read_bytes()

    outcome = rollback_rebuilt_neighbour(configuration, snapshot_path=snapshots[-1])

    assert outcome.completed
    assert old_database.read_bytes() == old_before
    assert old_database.exists()
