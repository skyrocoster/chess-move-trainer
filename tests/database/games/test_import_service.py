from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import UUID

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games.persistence import GameRepository, import_raw_games


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
