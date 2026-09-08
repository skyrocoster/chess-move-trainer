from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy.engine import Connection

from chess_move_trainer.database import create_schema
import chess_move_trainer.database.games.persistence as persistence_service
from chess_move_trainer.database.games.persistence import (
    GameRepository,
    import_normalized_games,
    import_raw_games,
    normalize_raw_games,
)


FIXTURES = Path(__file__).parent / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")


def _raw(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _count(database: Path, table: str) -> int:
    with sqlite3.connect(database) as connection:
        return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _game_snapshot(database: Path) -> tuple[list[tuple[object, ...]], list[tuple[object, ...]]]:
    with sqlite3.connect(database) as connection:
        games = connection.execute("SELECT * FROM datasource_game ORDER BY dg_game_id").fetchall()
        occurrences = connection.execute(
            "SELECT * FROM derived_game_position ORDER BY datasource_game_id, dgp_ply"
        ).fetchall()
    return games, occurrences


def test_import_commits_valid_games_independently_and_continues_after_skip(tmp_path: Path) -> None:
    database = tmp_path / "independent.db"
    create_schema(database)
    first = _raw("game-trainer-white.json")
    malformed = _raw("game-malformed-pgn.json")
    second = _raw("game-trainer-black.json")

    result = import_raw_games([first, malformed, second], TRAINER_UUID, GameRepository(database))

    assert result.completed
    assert result.imported_count == 2
    assert result.skipped_count == 1
    assert len(result.warnings) == 1
    assert result.failure is None
    assert _count(database, "datasource_game") == 2


def test_import_opens_and_validates_schema_once_for_multiple_games(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "one-connection.db"
    create_schema(database)
    original_open = persistence_service._open_existing_connection
    original_assert = persistence_service._assert_compatible_schema
    open_calls = 0
    validation_calls = 0

    def count_open(*args: object, **kwargs: object) -> object:
        nonlocal open_calls
        open_calls += 1
        return original_open(*args, **kwargs)

    def count_validation(*args: object, **kwargs: object) -> None:
        nonlocal validation_calls
        validation_calls += 1
        original_assert(*args, **kwargs)

    monkeypatch.setattr(persistence_service, "_open_existing_connection", count_open)
    monkeypatch.setattr(persistence_service, "_assert_compatible_schema", count_validation)

    result = import_raw_games(
        [_raw("game-trainer-white.json"), _raw("game-trainer-black.json")],
        TRAINER_UUID,
        GameRepository(database),
    )

    assert result.completed
    assert result.imported_count == 2
    assert open_calls == 1
    assert validation_calls == 1


def test_one_transaction_per_written_game(tmp_path: Path) -> None:
    database = tmp_path / "transactions.db"
    create_schema(database)
    checkpoints: list[str] = []

    result = import_raw_games(
        [_raw("game-trainer-white.json"), _raw("game-trainer-black.json")],
        TRAINER_UUID,
        GameRepository(database, _checkpoint=checkpoints.append),
    )

    assert result.completed
    assert result.imported_count == 2
    assert checkpoints.count("metadata") == 2


def test_invalid_correction_never_opens_write_work_and_preserves_prior(tmp_path: Path) -> None:
    database = tmp_path / "invalid-correction.db"
    create_schema(database)
    original = _raw("game-trainer-white.json")
    repository = GameRepository(database)
    assert import_raw_games([original], TRAINER_UUID, repository).completed
    before = _game_snapshot(database)
    invalid = _raw("game-illegal-pgn.json")
    invalid["uuid"] = original["uuid"]
    checkpoints: list[str] = []

    result = import_raw_games(
        [invalid],
        TRAINER_UUID,
        GameRepository(database, _checkpoint=checkpoints.append),
    )

    assert result.completed
    assert result.imported_count == 0
    assert result.skipped_count == 1
    assert checkpoints == []
    assert _game_snapshot(database) == before


def test_interrupted_resume_skips_committed_unchanged_game(tmp_path: Path) -> None:
    database = tmp_path / "resume.db"
    create_schema(database)
    first = _raw("game-trainer-white.json")
    second = _raw("game-trainer-black.json")
    metadata_calls = 0

    def interrupt_second(boundary: str) -> None:
        nonlocal metadata_calls
        if boundary == "metadata":
            metadata_calls += 1
            if metadata_calls == 2:
                raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        import_raw_games(
            [first, second],
            TRAINER_UUID,
            GameRepository(database, _checkpoint=interrupt_second),
        )

    checkpoints: list[str] = []
    result = import_raw_games(
        [first, second],
        TRAINER_UUID,
        GameRepository(database, _checkpoint=checkpoints.append),
    )

    assert result.completed
    assert result.imported_count == 2
    assert checkpoints.count("metadata") == 1
    assert _count(database, "datasource_game") == 2


def test_batched_occurrence_writes_preserve_exact_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "batched-occurrences.db"
    create_schema(database)
    original_execute = Connection.execute
    occurrence_batches: list[object] = []

    def capture_execute(
        connection: Connection,
        statement: object,
        parameters: object = None,
        *args: object,
        **kwargs: object,
    ) -> object:
        if "INSERT INTO derived_game_position" in str(statement):
            occurrence_batches.append(parameters)
        return original_execute(connection, statement, parameters, *args, **kwargs)

    monkeypatch.setattr(Connection, "execute", capture_execute)
    result = import_raw_games(
        [_raw("game-trainer-white.json")],
        TRAINER_UUID,
        GameRepository(database),
    )

    assert result.completed
    assert len(occurrence_batches) == 1
    parameters = occurrence_batches[0]
    assert isinstance(parameters, list)
    assert [row["ply"] for row in parameters] == [0, 1, 2, 3, 4]
    assert parameters[-1]["move_uci"] is None
    occurrences = _game_snapshot(database)[1]
    assert [row[1] for row in occurrences] == [0, 1, 2, 3, 4]
    assert [row[3] for row in occurrences] == ["e2e4", "e7e5", "g1f3", "b8c6", None]
    assert [row[4:] for row in occurrences] == [(0, 1), (0, 1), (0, 2), (1, 2), (2, 3)]


def test_operational_failure_rolls_back_active_game_and_returns_incomplete(tmp_path: Path) -> None:
    database = tmp_path / "failure.db"
    create_schema(database)
    calls = 0

    def fail_second_metadata(boundary: str) -> None:
        nonlocal calls
        if boundary == "metadata":
            calls += 1
            if calls == 2:
                raise RuntimeError("synthetic second-game failure")

    result = import_raw_games(
        [_raw("game-trainer-white.json"), _raw("game-trainer-black.json")],
        TRAINER_UUID,
        GameRepository(database, _checkpoint=fail_second_metadata),
    )

    assert not result.completed
    assert result.imported_count == 1
    assert result.failure is not None
    assert "second-game failure" in result.failure.message
    assert _count(database, "datasource_game") == 1


def test_bulk_failure_rolls_back_all_games_and_retains_skip_reporting(tmp_path: Path) -> None:
    database = tmp_path / "bulk-failure.db"
    create_schema(database)
    first = _raw("game-trainer-white.json")
    malformed = _raw("game-malformed-pgn.json")
    second = _raw("game-trainer-black.json")

    metadata_calls = 0

    def fail_second_metadata(boundary: str) -> None:
        nonlocal metadata_calls
        if boundary == "metadata":
            metadata_calls += 1
            if metadata_calls == 2:
                raise RuntimeError("synthetic bulk failure")

    results = normalize_raw_games([first, malformed, second], TRAINER_UUID)
    result = import_normalized_games(
        results,
        GameRepository(database, _checkpoint=fail_second_metadata),
        bulk=True,
    )

    assert not result.completed
    assert result.imported_count == 0
    assert result.skipped_count == 1
    assert len(result.warnings) == 1
    assert result.failure is not None
    assert "bulk failure" in result.failure.message
    assert _count(database, "datasource_game") == 0
    assert _count(database, "derived_game_position") == 0


def test_bulk_interruption_rolls_back_all_games_and_propagates(tmp_path: Path) -> None:
    database = tmp_path / "bulk-interrupt.db"
    create_schema(database)
    first = _raw("game-trainer-white.json")
    second = _raw("game-trainer-black.json")
    metadata_calls = 0

    def interrupt_second_metadata(boundary: str) -> None:
        nonlocal metadata_calls
        if boundary == "metadata":
            metadata_calls += 1
            if metadata_calls == 2:
                raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        import_normalized_games(
            normalize_raw_games([first, second], TRAINER_UUID),
            GameRepository(database, _checkpoint=interrupt_second_metadata),
            bulk=True,
        )

    assert _count(database, "datasource_game") == 0
    assert _count(database, "derived_game_position") == 0


def test_interruption_rolls_back_only_active_game_and_propagates(tmp_path: Path) -> None:
    database = tmp_path / "interrupt.db"
    create_schema(database)
    metadata_calls = 0

    def interrupt_second(boundary: str) -> None:
        nonlocal metadata_calls
        if boundary == "metadata":
            metadata_calls += 1
            if metadata_calls == 2:
                raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        import_raw_games(
            [_raw("game-trainer-white.json"), _raw("game-trainer-black.json")],
            TRAINER_UUID,
            GameRepository(database, _checkpoint=interrupt_second),
        )

    assert _count(database, "datasource_game") == 1
