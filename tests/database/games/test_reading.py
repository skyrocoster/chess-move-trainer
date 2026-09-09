from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from uuid import UUID

import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games import read_game
from chess_move_trainer.database.games.normalization import normalize_game
from chess_move_trainer.database.games.persistence import GameRepository
from chess_move_trainer.database.games.reading import GameReadRepository
from chess_move_trainer.database.schema import SchemaIncompatibleError


FIXTURES = Path(__file__).parent / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")
GAME_UUID = "dddddddd-dddd-4ddd-8ddd-ddddddddddd1"


def test_game_reader_returns_ordered_occurrences_including_final(tmp_path: Path) -> None:
    database = tmp_path / "reading.db"
    create_schema(database)
    raw = json.loads(
        (FIXTURES / "game-trainer-white.json").read_text(encoding="utf-8")
    )
    normalized = normalize_game(raw, TRAINER_UUID)
    assert normalized.game is not None
    persisted = GameRepository(database).persist(normalized.game)

    game = GameReadRepository(database).read(persisted.game_id)

    assert game is not None
    assert game.game_id == persisted.game_id
    assert game.trainer_color == "white"
    assert [occurrence.ply for occurrence in game.occurrences] == [0, 1, 2, 3, 4]
    assert [occurrence.move_uci for occurrence in game.occurrences] == [
        "e2e4",
        "e7e5",
        "g1f3",
        "b8c6",
        None,
    ]
    assert game.occurrences[-1].move_uci is None
    assert game.occurrences[-1].position.placement == "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R"


def test_public_game_detail_returns_metadata_pgn_and_replayable_fens(tmp_path: Path) -> None:
    database = tmp_path / "detail.db"
    create_schema(database)
    raw = json.loads(
        (FIXTURES / "game-trainer-white.json").read_text(encoding="utf-8")
    )
    normalized = normalize_game(raw, TRAINER_UUID)
    assert normalized.game is not None
    GameRepository(database).persist(normalized.game)

    detail = read_game(database, GAME_UUID)

    assert detail is not None
    assert detail.game_uuid == GAME_UUID
    assert detail.source_url == "https://www.chess.com/game/live/synthetic-white"
    assert detail.original_pgn == raw["pgn"]
    assert detail.trainer_color == "white"
    assert detail.trainer_chesscom_uuid == str(TRAINER_UUID)
    assert detail.opponent_chesscom_uuid == "99999999-9999-4999-8999-999999999991"
    assert detail.trainer_rating == 1500
    assert detail.opponent_rating == 1490
    assert detail.started_at_utc == "2026-08-01T12:00:00Z"
    assert detail.ended_at_utc == "2026-08-01T12:04:00Z"
    assert detail.trainer_outcome == "win"
    assert detail.termination_reason == "resigned"
    assert detail.time_control == "300+5"
    assert detail.time_class == "blitz"
    assert [occurrence.ply for occurrence in detail.occurrences] == [0, 1, 2, 3, 4]
    assert [occurrence.move_uci for occurrence in detail.occurrences] == [
        "e2e4",
        "e7e5",
        "g1f3",
        "b8c6",
        None,
    ]
    assert [occurrence.fen for occurrence in detail.occurrences] == [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]
    serialized = asdict(detail)
    serialized_text = json.dumps(serialized)
    assert all(private not in serialized_text for private in ("game_id", "position_id"))


def test_public_game_detail_is_read_only_and_uses_schema_compatibility(tmp_path: Path) -> None:
    database = tmp_path / "detail.db"
    create_schema(database)
    raw = json.loads(
        (FIXTURES / "game-trainer-white.json").read_text(encoding="utf-8")
    )
    normalized = normalize_game(raw, TRAINER_UUID)
    assert normalized.game is not None
    GameRepository(database).persist(normalized.game)
    before = database.read_bytes()

    assert read_game(database, GAME_UUID) is not None
    assert read_game(database, "00000000-0000-4000-8000-000000000000") is None
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("detail.db-*"))

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE not_schema_v1 (value TEXT)")
    incompatible_before = incompatible.read_bytes()
    with pytest.raises(SchemaIncompatibleError):
        read_game(incompatible, GAME_UUID)
    assert incompatible.read_bytes() == incompatible_before
