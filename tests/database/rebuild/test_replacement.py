from __future__ import annotations

import contextlib
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
    RebuildOperation,
    RebuildConfiguration,
    SnapshotOutcome,
    VerificationTarget,
    create_snapshot,
    replace_rebuilt_neighbour,
    verify_rebuild_target,
)
import chess_move_trainer.database.rebuild.replacement as replacement_service


def _ready_database(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
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
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('A00', ?) ",
            (name,),
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


def _candidate_for(neighbour: Path, tmp_path: Path) -> tuple[Path, bytes]:
    source = _ready_database(tmp_path, "candidate-source.db")
    candidate = neighbour.with_name(f"{neighbour.name}.candidate")
    candidate.write_bytes(source.read_bytes())
    return candidate, candidate.read_bytes()


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


def test_busy_neighbour_fails_without_terminating_owner_or_mutating_neighbour(
    tmp_path: Path,
) -> None:
    if os.name != "nt":
        pytest.skip("DB-08 destination mutex is Windows-only")
    neighbour = _ready_database(tmp_path, "neighbour.db")
    candidate, _ = _candidate_for(neighbour, tmp_path)
    configuration = RebuildConfiguration(neighbour)
    before = neighbour.read_bytes()
    snapshots_before = tuple(tmp_path.glob("neighbour.db.snapshot-*.db"))
    signal = tmp_path / "owner.signal"
    release = tmp_path / "owner.release"
    owner = _hold_sqlite_connection(neighbour, signal, release)
    deadline = time.monotonic() + 5
    while not signal.exists() and owner.poll() is None and time.monotonic() < deadline:
        time.sleep(0.01)
    assert signal.exists()
    try:
        outcome = replace_rebuilt_neighbour(configuration)
        assert outcome.status is OperationStatus.FAILED
        assert outcome.exit_code == OperationExitCode.FAILED
        assert "exclusive access" in outcome.message
        assert candidate.exists()
        assert neighbour.read_bytes() == before
        assert tuple(tmp_path.glob("neighbour.db.snapshot-*.db")) == snapshots_before
        assert owner.poll() is None
    finally:
        release.write_text("release", encoding="ascii")
        owner.wait(timeout=5)


def test_destination_guard_blocks_new_read_write_sqlite_opener(
    tmp_path: Path,
) -> None:
    if os.name != "nt":
        pytest.skip("DB-08 destination file guard is Windows-only")
    neighbour = _ready_database(tmp_path, "neighbour.db")
    signal = tmp_path / "opener.signal"
    child_code = """
import sqlite3
import sys
from pathlib import Path

try:
    connection = sqlite3.connect(sys.argv[1], timeout=0)
    connection.execute("CREATE TABLE IF NOT EXISTS __db08_guard_probe (value INTEGER)")
    connection.commit()
except Exception as error:
    Path(sys.argv[2]).write_text(f'blocked:{type(error).__name__}', encoding='ascii')
else:
    Path(sys.argv[2]).write_text('opened', encoding='ascii')
    connection.close()
"""
    with replacement_service.exclusive_destination(neighbour):
        opener = subprocess.Popen(
            [sys.executable, "-c", child_code, str(neighbour), str(signal)],
            cwd=Path(__file__).parents[3],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            opener.wait(timeout=5)
            assert signal.read_text(encoding="ascii").startswith("blocked:")
        finally:
            if opener.poll() is None:
                opener.kill()
                opener.wait(timeout=5)


def test_candidate_is_verified_before_exclusive_snapshot_and_atomic_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    neighbour = _ready_database(tmp_path, "neighbour.db")
    candidate, _ = _candidate_for(neighbour, tmp_path)
    configuration = RebuildConfiguration(neighbour)
    candidate_result = verify_rebuild_target(
        configuration, VerificationTarget.CANDIDATE
    )
    events: list[str] = []

    def verify(*_: object, **__: object):
        events.append("verify")
        return candidate_result

    @contextlib.contextmanager
    def exclusive(_: Path):
        events.append("exclusive")
        yield

    snapshot_path = tmp_path / "neighbour.db.snapshot-test.db"
    fake_snapshot = SnapshotOutcome(
        operation=RebuildOperation.REPLACE,
        status=OperationStatus.SUCCEEDED,
        message="synthetic verified snapshot",
        exit_code=OperationExitCode.SUCCEEDED,
        source_path=neighbour,
        snapshot_path=snapshot_path,
        verification=candidate_result,
        retained_snapshots=(snapshot_path,),
    )

    def snapshot(*_: object, **__: object) -> SnapshotOutcome:
        events.append("snapshot")
        return fake_snapshot

    def swap(source: Path, target: Path) -> None:
        events.append("swap")
        assert source == candidate
        assert target == neighbour

    monkeypatch.setattr(replacement_service, "verify_rebuild_target", verify)
    monkeypatch.setattr(replacement_service, "exclusive_destination", exclusive)
    monkeypatch.setattr(replacement_service, "create_snapshot", snapshot)
    monkeypatch.setattr(
        replacement_service,
        "os",
        type("ReplacementOS", (), {"replace": staticmethod(swap)})(),
    )

    outcome = replace_rebuilt_neighbour(configuration)

    assert outcome.completed
    assert events == ["verify", "exclusive", "snapshot", "swap"]


def test_replacement_creates_verified_snapshot_retains_three_and_swaps_atomically(
    tmp_path: Path,
) -> None:
    neighbour = _ready_database(tmp_path, "neighbour.db")
    candidate, candidate_bytes = _candidate_for(neighbour, tmp_path)
    configuration = RebuildConfiguration(neighbour)
    original_name = _opening_name(neighbour)
    for _ in range(MAX_RETAINED_SNAPSHOTS - 1):
        assert create_snapshot(configuration).completed

    outcome = replace_rebuilt_neighbour(configuration)

    assert outcome.completed
    assert outcome.snapshot is not None and outcome.snapshot.completed
    assert outcome.snapshot_path is not None and outcome.snapshot_path.exists()
    assert _opening_name(outcome.snapshot_path) == original_name
    assert neighbour.read_bytes() == candidate_bytes
    assert not candidate.exists()
    assert len(tuple(tmp_path.glob("neighbour.db.snapshot-*.db"))) == MAX_RETAINED_SNAPSHOTS
    assert verify_rebuild_target(
        configuration, VerificationTarget.NEIGHBOUR
    ).replacement_ready


def test_failed_atomic_swap_preserves_neighbour_and_verified_recovery_point(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    neighbour = _ready_database(tmp_path, "neighbour.db")
    candidate, _ = _candidate_for(neighbour, tmp_path)
    configuration = RebuildConfiguration(neighbour)
    before = neighbour.read_bytes()

    def fail_swap(*_: object, **__: object) -> None:
        raise OSError("synthetic swap failure")

    monkeypatch.setattr(
        replacement_service,
        "os",
        type("ReplacementOS", (), {"replace": staticmethod(fail_swap)})(),
    )
    outcome = replace_rebuilt_neighbour(configuration)

    assert not outcome.completed
    assert "swap failure" in outcome.message
    assert outcome.snapshot is not None and outcome.snapshot.completed
    assert outcome.snapshot_path is not None and outcome.snapshot_path.exists()
    assert neighbour.read_bytes() == before
    assert candidate.exists()


def test_replacement_does_not_read_or_modify_old_database(tmp_path: Path) -> None:
    neighbour = _ready_database(tmp_path, "neighbour.db")
    candidate, _ = _candidate_for(neighbour, tmp_path)
    old_database = tmp_path / "old-database.db"
    old_database.write_bytes(b"old database sentinel")
    old_before = old_database.read_bytes()

    outcome = replace_rebuilt_neighbour(RebuildConfiguration(neighbour))

    assert outcome.completed
    assert old_database.read_bytes() == old_before
    assert old_database.exists()
    assert candidate == neighbour.with_name("neighbour.db.candidate")
