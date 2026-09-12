from __future__ import annotations

import sqlite3
import math
from pathlib import Path

import chess
import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.positions import (
    PositionRepository,
    TrainingRequirementPolicy,
    TrainingRequirementQuery,
    TrainingRequirementStaleError,
    TrainingRequirementValidationError,
    discover_training_requirements,
)


DEFAULT_POLICY = TrainingRequirementPolicy(0.8, 30)
TARGET_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
ANCHOR_FEN = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"


def _position_fen(*moves: str) -> str:
    board = chess.Board()
    for move in moves:
        board.push_uci(move)
    return board.fen()


def _game(connection: sqlite3.Connection, game_id: int, color: str, started: str | None) -> None:
    connection.execute(
        """
        INSERT INTO datasource_game (
            dg_game_id, dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
            dg_trainer_color, dg_trainer_chesscom_uuid, dg_started_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            game_id,
            f"training-game-{game_id}",
            f"https://example.test/training-game-{game_id}",
            "[Result \"*\"]\n\n*",
            color,
            f"trainer-{game_id}",
            started,
        ),
    )


def _occurrence(
    connection: sqlite3.Connection,
    game_id: int,
    ply: int,
    position_id: int,
    move_uci: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO derived_game_position (
            datasource_game_id, dgp_ply, derived_position_id,
            dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
        ) VALUES (?, ?, ?, ?, 0, 1)
        """,
        (game_id, ply, position_id, move_uci),
    )


def _preference(
    connection: sqlite3.Connection,
    position_id: int,
    periods: tuple[tuple[str, str | None, str | None], ...],
) -> None:
    connection.executemany(
        """
        INSERT INTO datasource_preferred_move_period (
            derived_position_id, dpm_effective_from,
            dpm_effective_until, dpm_move_uci
        ) VALUES (?, ?, ?, ?)
        """,
        ((position_id, start, end, move) for start, end, move in periods),
    )


def _opening_route(
    connection: sqlite3.Connection,
    position_id: int,
    eco: str,
    name: str,
) -> None:
    opening_id = connection.execute(
        "INSERT INTO datasource_opening (do_eco, do_name) VALUES (?, ?) RETURNING do_opening_id",
        (eco, name),
    ).fetchone()[0]
    connection.execute(
        """
        INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
        VALUES (?, ?)
        """,
        (opening_id, position_id),
    )


def _fixture(tmp_path: Path) -> tuple[Path, dict[str, int]]:
    database = tmp_path / "training.db"
    create_schema(database)
    fens = {
        "target": TARGET_FEN,
        "start": _position_fen(),
        "deep": _position_fen(
            "e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6"
        ),
    }
    position_ids = {
        name: PositionRepository(database).resolve_fen(fen)
        for name, fen in fens.items()
    }
    with sqlite3.connect(database) as connection:
        _game(connection, 1, "white", "2026-01-15T00:00:00Z")
        _game(connection, 2, "white", "2026-01-20T00:00:00Z")
        _game(connection, 3, "white", "2026-02-15T00:00:00Z")
        _game(connection, 4, "white", "2026-03-15T00:00:00Z")
        _game(connection, 5, "black", "2026-01-15T00:00:00Z")
        _game(connection, 6, "white", None)
        _game(connection, 7, "white", "2026-01-25T00:00:00Z")

        _occurrence(connection, 1, 1, position_ids["target"], "a2a3")
        _occurrence(connection, 2, 1, position_ids["target"], "c2c3")
        _occurrence(connection, 2, 2, position_ids["target"], "a2a3")
        _occurrence(connection, 3, 1, position_ids["target"], "a2a3")
        _occurrence(connection, 4, 1, position_ids["target"], "b2b3")
        _occurrence(connection, 5, 1, position_ids["target"], "a2a3")
        _occurrence(connection, 6, 1, position_ids["target"], "a2a3")
        _occurrence(connection, 7, 1, position_ids["target"], None)

        _occurrence(connection, 2, 3, position_ids["start"], "a2a3")
        _occurrence(connection, 2, 4, position_ids["deep"], "a2a3")

        _preference(
            connection,
            position_ids["target"],
            (
                ("2026-01-01", "2026-02-01", "a2a3"),
                ("2026-02-01", "2026-03-01", None),
                ("2026-03-01", None, "b2b3"),
            ),
        )
        _preference(connection, position_ids["start"], (("2020-01-01", None, "a2a3"),))
        _preference(connection, position_ids["deep"], (("2020-01-01", None, "a2a3"),))
        _opening_route(connection, position_ids["start"], "A00", "Early Label")
        _opening_route(connection, position_ids["deep"], "B00", "Deep Label")
    return database, position_ids


def _item(page, preferred_move: str, fen: str | None = None):
    return next(
        item
        for item in page.items
        if item.preferred_move_uci == preferred_move
        and (fen is None or item.fen == fen)
    )


def test_discovery_counts_eligible_repeated_occurrences_and_current_preference(
    tmp_path: Path,
) -> None:
    database, _positions = _fixture(tmp_path)
    before = database.read_bytes()

    page = discover_training_requirements(
        database,
        TrainingRequirementQuery("2026-01-25", training_requirement_gte=-100),
        DEFAULT_POLICY,
    )

    target = _item(page, "a2a3", TARGET_FEN.rsplit(" ", 2)[0] + " 0 1")
    assert (target.encounters, target.hits, target.misses) == (3, 2, 1)
    assert target.game_balance == -2.0
    assert target.training_requirement == -2.0
    assert target.training_required is True
    assert page.total == 3
    assert database.read_bytes() == before


def test_preference_no_preference_and_reactivation_control_current_items(
    tmp_path: Path,
) -> None:
    database, _positions = _fixture(tmp_path)

    no_preference = discover_training_requirements(
        database,
        TrainingRequirementQuery("2026-02-20", training_requirement_gte=-100),
        DEFAULT_POLICY,
    )
    assert all(
        item.fen != TARGET_FEN.rsplit(" ", 2)[0] + " 0 1"
        for item in no_preference.items
    )

    reactivated = discover_training_requirements(
        database,
        TrainingRequirementQuery("2026-03-20", training_requirement_gte=-100),
        DEFAULT_POLICY,
    )
    target = _item(reactivated, "b2b3", TARGET_FEN.rsplit(" ", 2)[0] + " 0 1")
    assert (target.encounters, target.hits, target.misses) == (1, 1, 0)
    assert all(
        not (
            item.fen == TARGET_FEN.rsplit(" ", 2)[0] + " 0 1"
            and item.preferred_move_uci == "a2a3"
        )
        for item in reactivated.items
    )


def test_opening_filters_use_game_association_without_recalculating_global_evidence(
    tmp_path: Path,
) -> None:
    database, _positions = _fixture(tmp_path)
    query = TrainingRequirementQuery(
        "2026-01-25",
        training_requirement_gte=-100,
        opening_key="A00:Early Label",
        opening_match="reached",
    )

    reached = discover_training_requirements(database, query, DEFAULT_POLICY)
    reached_target = _item(
        reached, "a2a3", TARGET_FEN.rsplit(" ", 2)[0] + " 0 1"
    )
    assert (reached_target.encounters, reached_target.hits, reached_target.misses) == (3, 2, 1)

    deepest_a = discover_training_requirements(
        database,
        TrainingRequirementQuery(
            "2026-01-25",
            training_requirement_gte=-100,
            opening_key="A00:Early Label",
            opening_match="deepest",
        ),
        DEFAULT_POLICY,
    )
    assert deepest_a.items == ()

    deepest_b = discover_training_requirements(
        database,
        TrainingRequirementQuery(
            "2026-01-25",
            training_requirement_gte=-100,
            opening_key="B00:Deep Label",
            opening_match="deepest",
        ),
        DEFAULT_POLICY,
    )
    assert _item(
        deepest_b, "a2a3", TARGET_FEN.rsplit(" ", 2)[0] + " 0 1"
    ).encounters == 3


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"training_requirement_gt": float("nan")},
        {"training_requirement_gt": 2, "training_requirement_lt": 1},
        {"opening_key": "A00:Early Label"},
        {"opening_match": "reached"},
        {"page": 0},
        {"page_size": 101},
    ],
)
def test_query_requires_valid_range_opening_pair_and_pagination(kwargs: dict[str, object]) -> None:
    with pytest.raises(TrainingRequirementValidationError):
        TrainingRequirementQuery("2026-01-25", **kwargs)


def test_all_requirement_boundaries_are_applied_before_pagination(tmp_path: Path) -> None:
    database, _positions = _fixture(tmp_path)

    def total(**kwargs: float) -> int:
        return discover_training_requirements(
            database,
            TrainingRequirementQuery("2026-01-25", **kwargs),
            DEFAULT_POLICY,
        ).total

    assert total(training_requirement_lt=-2) == 0
    assert total(training_requirement_lte=-2) == 1
    assert total(training_requirement_gt=-2) == 2
    assert total(training_requirement_gte=-2) == 3

    all_items = discover_training_requirements(
        database,
        TrainingRequirementQuery(
            "2026-01-25", training_requirement_gte=-100, page=1, page_size=1
        ),
        DEFAULT_POLICY,
    )
    second = discover_training_requirements(
        database,
        TrainingRequirementQuery(
            "2026-01-25", training_requirement_gte=-100, page=2, page_size=1
        ),
        DEFAULT_POLICY,
    )
    third = discover_training_requirements(
        database,
        TrainingRequirementQuery(
            "2026-01-25", training_requirement_gte=-100, page=3, page_size=1
        ),
        DEFAULT_POLICY,
    )
    assert all_items.total == second.total == third.total == 3
    assert len({
        page.items[0].fen for page in (all_items, second, third)
    }) == 3


def test_stale_current_state_is_rejected_before_range_filtering(tmp_path: Path) -> None:
    database, positions = _fixture(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_position_training_aggregate (
                derived_position_id, dpta_preferred_move_uci,
                dpta_training_balance, dpta_updated_on
            ) VALUES (?, 'a2a3', CAST(2 AS REAL), '2026-02-01')
            """,
            (positions["target"],),
        )

    with pytest.raises(TrainingRequirementStaleError):
        discover_training_requirements(
            database,
            TrainingRequirementQuery("2026-01-25", training_requirement_gt=0),
            DEFAULT_POLICY,
        )


def test_future_preview_decays_without_writing_storage(tmp_path: Path) -> None:
    database, positions = _fixture(tmp_path)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO derived_position_training_aggregate (
                derived_position_id, dpta_preferred_move_uci,
                dpta_training_balance, dpta_updated_on
            ) VALUES (?, 'a2a3', CAST(2 AS REAL), '2026-01-01')
            """,
            (positions["target"],),
        )
    before = database.read_bytes()

    page = discover_training_requirements(
        database,
        TrainingRequirementQuery("2026-01-31", training_requirement_gte=-100),
        DEFAULT_POLICY,
    )

    target = _item(page, "a2a3", TARGET_FEN.rsplit(" ", 2)[0] + " 0 1")
    assert target.effective_training_balance == pytest.approx(math.sqrt(2))
    assert target.training_adjustment == pytest.approx(2.0)
    assert database.read_bytes() == before


def test_approved_real_data_anchor_is_mathematically_reproduced(tmp_path: Path) -> None:
    database = tmp_path / "anchor.db"
    create_schema(database)
    position_id = PositionRepository(database).resolve_fen(ANCHOR_FEN)
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO datasource_opening (do_eco, do_name)
            VALUES ('B02', 'Alekhine Defense')
            """
        )
        opening_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
        connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?)
            """,
            (opening_id, position_id),
        )
        connection.execute(
            """
            INSERT INTO datasource_preferred_move_period (
                derived_position_id, dpm_effective_from, dpm_move_uci
            ) VALUES (?, '2024-02-29', 'b1c3')
            """,
            (position_id,),
        )
        for game_id in range(1, 87):
            _game(connection, game_id, "white", "2024-03-01T00:00:00Z")
            _occurrence(
                connection,
                game_id,
                1,
                position_id,
                "b1c3" if game_id <= 28 else "a2a3",
            )

    page = discover_training_requirements(
        database,
        TrainingRequirementQuery(
            "2026-09-12",
            training_requirement_lt=0,
            opening_key="B02:Alekhine Defense",
            opening_match="reached",
        ),
        DEFAULT_POLICY,
    )
    assert len(page.items) == 1
    item = page.items[0]
    assert item.fen == ANCHOR_FEN.rsplit(" ", 2)[0] + " 0 1"
    assert item.trainer_color == "white"
    assert item.preferred_move_uci == "b1c3"
    assert (item.encounters, item.hits, item.misses) == (86, 28, 58)
    assert (item.game_balance, item.effective_training_balance) == (-204.0, 0.0)
    assert item.training_adjustment == 0.0
    assert item.training_requirement == -204.0
    assert item.training_required is True
    assert item.correct_answers_needed == 15
