from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from chess_move_trainer.database.games.normalization import normalize_game
from chess_move_trainer.database.positions import CanonicalPosition

FIXTURES = Path(__file__).parent / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")


def _fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_replay_produces_n_plus_one_outgoing_moves_and_position_counters() -> None:
    result = normalize_game(_fixture("game-trainer-white.json"), TRAINER_UUID)

    assert result.game is not None
    occurrences = result.game.occurrences
    assert len(occurrences) == 5
    assert [occurrence.ply for occurrence in occurrences] == [0, 1, 2, 3, 4]
    assert [occurrence.move_uci for occurrence in occurrences] == [
        "e2e4",
        "e7e5",
        "g1f3",
        "b8c6",
        None,
    ]
    assert [occurrence.halfmove_clock for occurrence in occurrences] == [0, 0, 0, 1, 2]
    assert [occurrence.fullmove_number for occurrence in occurrences] == [1, 1, 2, 2, 3]
    assert all(isinstance(occurrence.position, CanonicalPosition) for occurrence in occurrences)


def test_repetition_reuses_db02_canonical_keys_while_counters_advance() -> None:
    result = normalize_game(_fixture("game-repetition-counters.json"), TRAINER_UUID)

    assert result.game is not None
    occurrences = result.game.occurrences
    assert len(occurrences) == 9
    assert occurrences[0].position == occurrences[4].position == occurrences[8].position
    assert [occurrences[index].halfmove_clock for index in (0, 4, 8)] == [0, 4, 8]
    assert [occurrences[index].fullmove_number for index in (0, 4, 8)] == [1, 3, 5]
    assert occurrences[-1].move_uci is None
