from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.database import create_schema
import chess_move_trainer.database.rebuild.verification as verification_service
from chess_move_trainer.database.rebuild import (
    RebuildConfiguration,
    VerificationStatus,
    VerificationTarget,
    verify_database,
    verify_rebuild_target,
)


def _schema_database(tmp_path: Path, name: str = "database.db") -> Path:
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
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('A00', 'Test opening')"
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


def test_verify_empty_schema_is_structurally_valid_partial_and_read_only(
    tmp_path: Path,
) -> None:
    database = _schema_database(tmp_path)
    before = database.read_bytes()

    result = verify_database(database)

    assert result.status is VerificationStatus.STRUCTURALLY_VALID_PARTIAL
    assert result.structurally_valid
    assert not result.replacement_ready
    assert result.schema_compatible
    assert result.user_version == 1
    assert result.integrity_result == "ok"
    assert not result.foreign_key_errors
    assert database.read_bytes() == before


def test_verify_opening_only_checkpoint_is_valid_but_not_replacement_ready(
    tmp_path: Path,
) -> None:
    database = _schema_database(tmp_path)
    _add_openings(database)

    result = verify_database(database)

    assert result.status is VerificationStatus.STRUCTURALLY_VALID_PARTIAL
    assert result.openings_ready
    assert not result.games_ready
    assert not result.replacement_ready


def test_verify_openings_and_imported_games_are_replacement_ready(tmp_path: Path) -> None:
    database = _schema_database(tmp_path)
    _add_openings(database)
    _add_game(database)

    result = verify_database(database)

    assert result.status is VerificationStatus.REPLACEMENT_READY
    assert result.replacement_ready
    assert result.openings_ready
    assert result.games_ready


def test_verify_incompatible_database_is_distinguished_without_change(tmp_path: Path) -> None:
    database = tmp_path / "incompatible.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)")
        connection.execute("PRAGMA user_version = 1")
    before = database.read_bytes()

    result = verify_database(database)

    assert result.status is VerificationStatus.INCOMPATIBLE
    assert not result.structurally_valid
    assert result.user_version == 1
    assert database.read_bytes() == before


def test_verify_malformed_database_is_corrupt_and_missing_target_is_not_created(
    tmp_path: Path,
) -> None:
    malformed = tmp_path / "malformed.db"
    malformed.write_bytes(b"not a SQLite database")
    missing = tmp_path / "missing.db"

    corrupt = verify_database(malformed)
    absent = verify_database(missing, target=VerificationTarget.SNAPSHOT)

    assert corrupt.status is VerificationStatus.CORRUPT
    assert absent.status is VerificationStatus.MISSING
    assert not missing.exists()


def test_verify_foreign_key_invalid_database_is_distinguished(tmp_path: Path) -> None:
    database = _schema_database(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute(
            "INSERT INTO derived_game_position "
            "(datasource_game_id, dgp_ply, derived_position_id, dgp_move_uci, "
            "dgp_halfmove_clock, dgp_fullmove_number) VALUES (999, 0, 999, NULL, 0, 1)"
        )

    result = verify_database(database)

    assert result.status is VerificationStatus.FOREIGN_KEY_INVALID
    assert result.foreign_key_errors


def test_verify_access_failure_is_unavailable_not_corrupt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _schema_database(tmp_path)

    def deny_access(*_: object, **__: object) -> object:
        raise PermissionError("access denied")

    monkeypatch.setattr(verification_service, "_open_connection", deny_access)

    result = verification_service.verify_database(database)

    assert result.status is VerificationStatus.UNAVAILABLE
    assert not result.structurally_valid
    assert "no corruption claim" in result.message


def test_verify_unexpected_internal_error_is_not_swallowed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _schema_database(tmp_path)

    def defect(*_: object, **__: object) -> object:
        raise RuntimeError("synthetic programming defect")

    monkeypatch.setattr(verification_service, "_schema_snapshot", defect)

    with pytest.raises(RuntimeError, match="synthetic programming defect"):
        verification_service.verify_database(database)


def test_verify_managed_candidate_and_snapshot_selectors_use_one_service(
    tmp_path: Path,
) -> None:
    neighbour = _schema_database(tmp_path, "neighbour.db")
    candidate = tmp_path / "neighbour.db.candidate"
    snapshot = tmp_path / "snapshot.db"
    candidate.write_bytes(neighbour.read_bytes())
    snapshot.write_bytes(neighbour.read_bytes())
    configuration = RebuildConfiguration(neighbour)

    candidate_result = verify_rebuild_target(configuration, VerificationTarget.CANDIDATE)
    snapshot_result = verify_rebuild_target(
        configuration,
        VerificationTarget.SNAPSHOT,
        snapshot_path=snapshot,
    )

    assert candidate_result.target is VerificationTarget.CANDIDATE
    assert candidate_result.database_path == candidate.resolve()
    assert snapshot_result.target is VerificationTarget.SNAPSHOT
    assert snapshot_result.database_path == snapshot.resolve()


@pytest.mark.parametrize(
    ("target", "snapshot_path"),
    [
        (VerificationTarget.SNAPSHOT, None),
        (VerificationTarget.NEIGHBOUR, Path("unexpected.db")),
        (VerificationTarget.CANDIDATE, Path("unexpected.db")),
    ],
)
def test_verify_target_selector_rejects_ambiguous_snapshot_inputs(
    tmp_path: Path,
    target: VerificationTarget,
    snapshot_path: Path | None,
) -> None:
    configuration = RebuildConfiguration(tmp_path / "neighbour.db")

    with pytest.raises(ValueError, match="snapshot"):
        verify_rebuild_target(configuration, target, snapshot_path=snapshot_path)
