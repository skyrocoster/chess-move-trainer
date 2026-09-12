from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from chess_move_trainer.database.positions import TrainingAnswerRepository

from test_training_answers import POLICY, _balance, _fixture, _request


def test_concurrent_answers_serialize_against_latest_aggregate(tmp_path: Path) -> None:
    database, position_id = _fixture(tmp_path)

    def submit() -> float:
        return TrainingAnswerRepository(
            database,
            clock=lambda: date(2026, 1, 5),
        ).submit(_request("2026-01-05"), POLICY).item.effective_training_balance

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = sorted(executor.map(lambda _value: submit(), (1, 2)))

    assert results == [1.0, 2.0]
    assert _balance(database, position_id) == (2.0, "2026-01-05")
