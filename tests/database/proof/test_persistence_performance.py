from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from uuid import UUID, uuid5

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games.persistence import (
    GameRepository,
    import_normalized_games,
    normalize_raw_games,
)

FIXTURES = Path(__file__).parents[1] / "games" / "fixtures"
TRAINER_UUID = UUID("11111111-1111-4111-8111-111111111111")
BENCHMARK_GAME_COUNT = 512


def _raw_game() -> dict[str, object]:
    return json.loads(
        (FIXTURES / "game-trainer-white.json").read_text(encoding="utf-8")
    )


def test_indexed_persistence_benchmark_is_bounded_and_aggregate_only(tmp_path: Path) -> None:
    database = tmp_path / "indexed-benchmark.db"
    create_schema(database)
    games: list[dict[str, object]] = []
    for index in range(BENCHMARK_GAME_COUNT):
        game = _raw_game()
        game["uuid"] = str(uuid5(TRAINER_UUID, f"direct-benchmark-{index}"))
        game["url"] = f"synthetic://direct-benchmark/{index}"
        games.append(game)

    expected_occurrences = BENCHMARK_GAME_COUNT * 5
    started = time.perf_counter()
    result = import_normalized_games(
        normalize_raw_games(games, TRAINER_UUID),
        GameRepository(database),
        bulk=True,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000

    with sqlite3.connect(database) as connection:
        game_count = int(
            connection.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0]
        )
        occurrence_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM derived_game_position"
            ).fetchone()[0]
        )
        index_columns = tuple(
            row[2]
            for row in connection.execute(
                "PRAGMA index_info('derived_game_position_position_idx')"
            ).fetchall()
        )

    assert result.completed
    assert result.imported_count == BENCHMARK_GAME_COUNT
    assert result.skipped_count == 0
    assert result.failure is None
    assert game_count == BENCHMARK_GAME_COUNT
    assert occurrence_count == expected_occurrences
    assert elapsed_ms < 180_000
    assert index_columns == (
        "derived_position_id",
        "datasource_game_id",
        "dgp_ply",
    )
    print(
        "benchmark "
        f"games={game_count} occurrences={occurrence_count} "
        f"elapsed_ms={elapsed_ms:.2f}"
    )
