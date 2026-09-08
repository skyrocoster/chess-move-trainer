from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games.normalization import normalize_game
from chess_move_trainer.database.games.persistence import GameRepository
from chess_move_trainer.database.games.reading import GameReadRepository


FIXTURES = Path(__file__).parent / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")


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
