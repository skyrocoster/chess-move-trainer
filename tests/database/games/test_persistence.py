from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy.engine import Connection

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games.normalization import (
    NormalizationResult,
    NormalizedGame,
    normalize_game,
)
from chess_move_trainer.database.games.persistence import (
    GamePersistenceError,
    GameRepository,
    import_normalized_games,
)

FIXTURES = Path(__file__).parent / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")


def _raw(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _normalized(name: str = "game-trainer-white.json") -> NormalizedGame:
    result = normalize_game(_raw(name), TRAINER_UUID)
    assert result.game is not None
    return result.game


def _rows(database: Path, table: str) -> list[tuple[object, ...]]:
    with sqlite3.connect(database) as connection:
        return connection.execute(f"SELECT * FROM {table} ORDER BY 1, 2").fetchall()


def test_fresh_game_persists_exact_metadata_positions_and_occurrences(tmp_path: Path) -> None:
    database = tmp_path / "fresh.db"
    create_schema(database)
    game = _normalized()

    result = GameRepository(database).persist(game)

    assert not result.corrected
    assert result.occurrence_count == 5
    game_rows = _rows(database, "datasource_game")
    assert game_rows == [
        (
            result.game_id,
            str(game.chesscom_game_uuid),
            game.source_url,
            game.original_pgn,
            "white",
            str(TRAINER_UUID),
            "99999999-9999-4999-8999-999999999991",
            1500,
            1490,
            "2026-08-01T12:00:00Z",
            "2026-08-01T12:04:00Z",
            "win",
            "resigned",
            "300+5",
            "blitz",
        )
    ]
    occurrences = _rows(database, "derived_game_position")
    assert [row[1] for row in occurrences] == [0, 1, 2, 3, 4]
    assert [row[3] for row in occurrences] == ["e2e4", "e7e5", "g1f3", "b8c6", None]
    assert [row[4:] for row in occurrences] == [(0, 1), (0, 1), (0, 2), (1, 2), (2, 3)]


def test_repeated_and_cross_game_positions_reuse_db02_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "reuse.db"
    create_schema(database)
    repeated = _normalized("game-repetition-counters.json")
    second = replace(
        repeated,
        chesscom_game_uuid=UUID("66666666-6666-4666-8666-666666666666"),
        source_url="https://www.chess.com/game/live/synthetic-repetition-two",
    )
    repository = GameRepository(database)

    first_result = repository.persist(repeated)
    first_positions = [row[2] for row in _rows(database, "derived_game_position")]
    third = replace(
        second,
        chesscom_game_uuid=UUID("77777777-7777-4777-8777-777777777777"),
        source_url="https://www.chess.com/game/live/synthetic-repetition-three",
    )
    original_execute = Connection.execute
    position_insert_calls = 0

    def count_position_inserts(
        connection: Connection,
        statement: object,
        parameters: object = None,
        *args: object,
        **kwargs: object,
    ) -> object:
        nonlocal position_insert_calls
        if "INSERT INTO derived_position" in str(statement):
            position_insert_calls += 1
        return original_execute(connection, statement, parameters, *args, **kwargs)

    monkeypatch.setattr(Connection, "execute", count_position_inserts)
    result = import_normalized_games(
        [
            NormalizationResult(game=second, warning=None),
            NormalizationResult(game=third, warning=None),
        ],
        repository,
    )
    assert result.completed
    assert result.imported_count == 2
    all_positions = _rows(database, "derived_game_position")

    assert first_positions[0] == first_positions[4] == first_positions[8]
    game_ids = [row[0] for row in _rows(database, "datasource_game")]
    assert game_ids[0] == first_result.game_id
    assert [row[2] for row in all_positions if row[0] == game_ids[0]] == first_positions
    assert [row[2] for row in all_positions if row[0] == game_ids[1]] == first_positions
    assert [row[2] for row in all_positions if row[0] == game_ids[2]] == first_positions
    unique_positions = {
        (
            occurrence.position.placement,
            occurrence.position.side_to_move,
            occurrence.position.castling_rights,
            occurrence.position.legal_en_passant,
        )
        for occurrence in repeated.occurrences
    }
    assert position_insert_calls == len(unique_positions)
    assert len(_rows(database, "derived_position")) < len(all_positions)


def test_valid_correction_replaces_every_metadata_field_and_occurrence(tmp_path: Path) -> None:
    database = tmp_path / "correction.db"
    create_schema(database)
    original = _normalized()
    repository = GameRepository(database)
    first = repository.persist(original)
    old_positions = _rows(database, "derived_position")
    corrected = replace(
        _normalized("game-trainer-black.json"),
        chesscom_game_uuid=original.chesscom_game_uuid,
        source_url="https://www.chess.com/game/live/synthetic-corrected",
    )

    result = repository.persist(corrected)

    assert result.corrected
    assert result.game_id == first.game_id
    assert result.occurrence_count == len(corrected.occurrences)
    rows = _rows(database, "datasource_game")
    assert len(rows) == 1
    assert rows[0][2:] == (
        corrected.source_url,
        corrected.original_pgn,
        corrected.trainer_color,
        str(corrected.trainer_chesscom_uuid),
        str(corrected.opponent_chesscom_uuid),
        corrected.trainer_rating,
        corrected.opponent_rating,
        corrected.started_at_utc,
        corrected.ended_at_utc,
        corrected.trainer_outcome,
        corrected.termination_reason,
        corrected.time_control_source,
        corrected.time_class,
    )
    assert len(_rows(database, "derived_game_position")) == len(corrected.occurrences)
    assert set(old_positions).issubset(set(_rows(database, "derived_position")))


@pytest.mark.parametrize("failure_boundary", ["metadata", "position", "occurrence"])
def test_correction_failure_at_each_boundary_preserves_prior_game(
    tmp_path: Path, failure_boundary: str
) -> None:
    database = tmp_path / f"failure-{failure_boundary}.db"
    create_schema(database)
    original = _normalized()
    GameRepository(database).persist(original)
    before = {
        table: _rows(database, table)
        for table in ("datasource_game", "derived_game_position", "derived_position")
    }
    corrected = replace(
        _normalized("game-trainer-black.json"),
        chesscom_game_uuid=original.chesscom_game_uuid,
    )

    def fail(boundary: str) -> None:
        if boundary == failure_boundary:
            raise RuntimeError(f"synthetic {boundary} failure")

    with pytest.raises(GamePersistenceError, match=failure_boundary):
        GameRepository(database, _checkpoint=fail).persist(corrected)

    for table, rows in before.items():
        assert _rows(database, table) == rows


def test_interrupted_active_game_rolls_back_without_removing_earlier_commit(tmp_path: Path) -> None:
    database = tmp_path / "interruption.db"
    create_schema(database)
    first = _normalized()
    second = replace(
        _normalized("game-trainer-black.json"),
        chesscom_game_uuid=UUID("55555555-5555-4555-8555-555555555555"),
    )
    GameRepository(database).persist(first)
    tables = ("datasource_game", "derived_game_position", "derived_position")
    before = {table: _rows(database, table) for table in tables}

    def interrupt(boundary: str) -> None:
        if boundary == "occurrence":
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        GameRepository(database, _checkpoint=interrupt).persist(second)

    for table, rows in before.items():
        assert _rows(database, table) == rows


def test_repository_exposes_no_database_handle_or_general_sql_contract(tmp_path: Path) -> None:
    database = tmp_path / "opaque.db"
    create_schema(database)
    repository = GameRepository(database)

    assert not hasattr(repository, "connection")
    assert not hasattr(repository, "raw_connection")
    assert not hasattr(repository, "execute")
    assert not hasattr(repository, "delete")
