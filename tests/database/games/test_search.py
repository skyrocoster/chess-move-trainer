from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, fields
from pathlib import Path
from uuid import UUID

import chess
import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.games.normalization import normalize_game
from chess_move_trainer.database.games.persistence import GameRepository
from chess_move_trainer.database.games.reading import GameReadRepository
from chess_move_trainer.database.games.search import (
    GameSearchPage,
    GameSearchQuery,
    GameSearchRepository,
    GameSearchSchemaError,
    GameSearchValidationError,
)
from chess_move_trainer.database.openings.persistence import OpeningCatalogueRepository
from chess_move_trainer.database.openings.source import OpeningRouteSource


TRAINER_UUID = "11111111-1111-4111-8111-111111111111"
GAMES_ROOT = Path(__file__).parent / "fixtures"


def _raw_game(
    uuid: str,
    moves: str,
    *,
    white_uuid: str = TRAINER_UUID,
    black_uuid: str = "99999999-9999-4999-8999-999999999991",
    white_result: str = "win",
    black_result: str = "resigned",
    white_rating: int | None = 1500,
    black_rating: int | None = 1490,
    date: str | None = "2026.08.01",
    time: str | None = "12:00:00",
    end_date: str | None = "2026.08.01",
    end_time: str | None = "12:30:00",
    time_control: str | None = "300+5",
    time_class: str | None = "blitz",
) -> dict[str, object]:
    headers = [f'[Event "search fixture"]']
    if date is not None:
        headers.extend([f'[UTCDate "{date}"]', f'[UTCTime "{time}"]'])
    if end_date is not None:
        headers.extend([f'[EndDate "{end_date}"]', f'[EndTime "{end_time}"]'])
    headers.append('[Result "*"]')
    return {
        "uuid": uuid,
        "url": f"https://www.chess.com/game/live/{uuid}",
        "rules": "chess",
        "pgn": "\n".join(headers) + f"\n\n{moves} *",
        "white": {"uuid": white_uuid, "rating": white_rating, "result": white_result},
        "black": {"uuid": black_uuid, "rating": black_rating, "result": black_result},
        "time_control": time_control,
        "time_class": time_class,
    }


def _database(tmp_path: Path, raw_games: list[dict[str, object]]) -> tuple[Path, list[int]]:
    database = tmp_path / "search.db"
    create_schema(database)
    game_ids: list[int] = []
    for raw in raw_games:
        normalized = normalize_game(raw, UUID(TRAINER_UUID))
        assert normalized.game is not None, normalized.warning
        game_ids.append(GameRepository(database).persist(normalized.game).game_id)
    return database, game_ids


def _route(eco: str, name: str, moves: tuple[str, ...]) -> OpeningRouteSource:
    board = chess.Board()
    for move_uci in moves:
        board.push_uci(move_uci)
    return OpeningRouteSource(eco, name, moves, board.fen(en_passant="fen"))


def _install_openings(database: Path) -> None:
    first_two = ("e2e4", "e7e5")
    first_four = (*first_two, "g1f3", "b8c6")
    OpeningCatalogueRepository(database).replace(
        (
            _route("C20", "King's Pawn Game", first_two),
            _route("B10", "Second Deep Label", first_four),
            _route("A10", "First Deep Label", first_four),
        )
    )


def _occurrence_ids(database: Path, game_id: int) -> list[tuple[int, int, str, str]]:
    game = GameReadRepository(database).read(game_id)
    assert game is not None
    return [
        (occurrence.ply, occurrence.position_id, occurrence.position.placement, occurrence.move_uci or "")
        for occurrence in game.occurrences
    ]


def _add_coverage(
    database: Path,
    position_ids: list[int],
    *,
    analysis: list[int] = (),
    preferred: list[int] = (),
) -> None:
    with sqlite3.connect(database) as connection:
        for position_id in analysis:
            connection.execute(
                """
                INSERT INTO derived_analysis_result
                    (derived_position_id, dar_quality, dar_configuration_version,
                     dar_settings_json, dar_engine_name, dar_engine_version,
                     dar_terminal_kind)
                VALUES (?, 'browser', 1, '{}', 'fixture', '1', 'stalemate')
                """,
                (position_id,),
            )
        for position_id in preferred:
            connection.execute(
                """
                INSERT INTO datasource_preferred_move_period
                    (derived_position_id, dpm_effective_from, dpm_effective_until, dpm_move_uci)
                VALUES (?, '2026-01-01', NULL, 'e2e4')
                """,
                (position_id,),
            )
        assert len(position_ids) >= len(analysis)


def _uuids(page: GameSearchPage) -> list[str]:
    return [item.game_uuid for item in page.items]


def test_search_returns_rich_summaries_and_selects_deepest_opening(tmp_path: Path) -> None:
    raw_games = [
        _raw_game("dddddddd-dddd-4ddd-8ddd-ddddddddddd1", "1. e4 e5 2. Nf3 Nc6"),
        _raw_game(
            "dddddddd-dddd-4ddd-8ddd-ddddddddddd2",
            "1. d4 Nf6 2. c4 e6",
            white_uuid="99999999-9999-4999-8999-999999999992",
            black_uuid=TRAINER_UUID,
            white_result="win",
            black_result="resigned",
            white_rating=1600,
            black_rating=1400,
            date=None,
            time=None,
            end_date=None,
            end_time=None,
        ),
        _raw_game(
            "dddddddd-dddd-4ddd-8ddd-ddddddddddd3",
            "1. c4",
            white_result="agreed",
            black_result="agreed",
            date="2026.08.03",
            time="09:00:00",
            end_date="2026.08.03",
            end_time="09:10:00",
            time_control="86400",
            time_class="daily",
        ),
    ]
    database, game_ids = _database(tmp_path, raw_games)
    _install_openings(database)
    positions = _occurrence_ids(database, game_ids[0])
    _add_coverage(
        database,
        [position_id for _ply, position_id, _placement, _move in positions],
        analysis=[positions[0][1]],
        preferred=[positions[2][1], positions[3][1]],
    )

    page = GameSearchRepository(database).search()

    assert _uuids(page) == [raw_games[2]["uuid"], raw_games[0]["uuid"], raw_games[1]["uuid"]]
    assert page.page == 1
    assert page.page_size == 50
    assert page.total == 3
    assert page.total_pages == 1
    assert not page.has_next
    summary = page.items[1]
    assert summary.source_url == raw_games[0]["url"]
    assert summary.occurrence_count == 5
    assert summary.length_plies == 4
    assert summary.deepest_opening is not None
    assert summary.deepest_opening.key == "A10:First Deep Label"
    assert summary.deepest_opening.ply == 4
    assert summary.coverage.distinct_position_count == 5
    assert summary.coverage.analyzed_position_count == 1
    assert summary.coverage.preferred_position_count == 2
    assert summary.coverage.analysis_coverage == "partial"
    assert summary.coverage.preferred_coverage == "partial"
    serialized = asdict(summary)
    assert not {field.name for field in fields(summary)} & {
        "game_id",
        "position_id",
        "opening_id",
        "route_id",
    }
    serialized_text = json.dumps(serialized)
    assert all(private not in serialized_text for private in ("game_id", "position_id", "opening_id", "route_id"))


def test_every_filter_family_combines_and_canonical_fen_move_filters(tmp_path: Path) -> None:
    raw = _raw_game("dddddddd-dddd-4ddd-8ddd-dddddddddd11", "1. e4 e5 2. Nf3 Nc6")
    other = _raw_game(
        "dddddddd-dddd-4ddd-8ddd-dddddddddd12",
        "1. c4",
        white_result="agreed",
        black_result="agreed",
        date="2026.08.03",
        time="09:00:00",
        end_date="2026.08.03",
        end_time="09:10:00",
        time_control="86400",
        time_class="daily",
    )
    database, game_ids = _database(tmp_path, [raw, other])
    _install_openings(database)
    start = chess.STARTING_FEN
    after_e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    query = GameSearchQuery(
        started_at_from="2026-08-01T12:00:00Z",
        started_at_to="2026-08-01T12:00:00+00:00",
        ended_at_from="2026-08-01T12:30:00Z",
        ended_at_to="2026-08-01T12:30:00Z",
        trainer_color="white",
        trainer_outcome="win",
        termination_reason="  RESIGNED ",
        trainer_rating_min=1500,
        trainer_rating_max=1500,
        opponent_rating_min=1490,
        opponent_rating_max=1490,
        opponent_chesscom_uuid="99999999-9999-4999-8999-999999999991",
        time_class="blitz",
        time_control="300+5",
        opening_key="A10:First Deep Label",
        opening_match="deepest",
        contains_fen=after_e4,
        move_fen=start,
        move_uci="e2e4",
        min_length_plies=4,
        max_length_plies=4,
    )

    page = GameSearchRepository(database).search(query)

    assert _uuids(page) == [raw["uuid"]]
    assert GameSearchRepository(database).search(
        GameSearchQuery(opening_key="C20:King's Pawn Game", opening_match="reached")
    ).total == 1
    assert GameSearchRepository(database).search(
        GameSearchQuery(trainer_color="black")
    ).total == 0
    assert GameSearchRepository(database).search(
        GameSearchQuery(time_class="daily")
    ).items[0].game_uuid == other["uuid"]
    assert GameSearchRepository(database).search(GameSearchQuery(max_length_plies=1)).total == 1
    assert game_ids


@pytest.mark.parametrize(
    "kwargs",
    [
        {"page": 0},
        {"page_size": 101},
        {"started_at_from": "2026-01-02T00:00:00Z", "started_at_to": "2026-01-01T00:00:00Z"},
        {"trainer_rating_min": 5, "trainer_rating_max": 4},
        {"opening_key": "C20:King's Pawn Game"},
        {"opening_match": "reached"},
        {"contains_fen": "not a FEN"},
        {"move_fen": chess.STARTING_FEN},
        {"move_fen": chess.STARTING_FEN, "move_uci": "e2e5"},
        {"time_class": "rapidly"},
        {"sort": "unknown"},
    ],
)
def test_known_invalid_values_and_combinations_are_rejected(kwargs: dict[str, object]) -> None:
    with pytest.raises(GameSearchValidationError):
        GameSearchQuery(**kwargs)


def test_coverage_states_pagination_and_deterministic_repeated_reads(tmp_path: Path) -> None:
    raw = _raw_game("dddddddd-dddd-4ddd-8ddd-dddddddddd21", "1. e4 e5")
    database, game_ids = _database(tmp_path, [raw])
    positions = _occurrence_ids(database, game_ids[0])
    position_ids = [position_id for _ply, position_id, _placement, _move in positions]
    repository = GameSearchRepository(database)

    assert repository.search(GameSearchQuery(analysis_coverage="none")).total == 1
    assert repository.search(GameSearchQuery(preferred_coverage="none")).total == 1
    _add_coverage(database, position_ids, analysis=[position_ids[0]], preferred=[position_ids[0]])
    partial = repository.search(GameSearchQuery(page_size=1, page=1, sort="length_desc"))
    assert partial.items[0].coverage.analysis_coverage == "partial"
    assert partial.items[0].coverage.preferred_coverage == "partial"
    assert partial.has_next is False
    _add_coverage(
        database,
        position_ids,
        analysis=position_ids[1:],
        preferred=position_ids[1:],
    )
    complete = repository.search(GameSearchQuery(analysis_coverage="complete", preferred_coverage="complete"))
    assert complete.total == 1
    assert repository.search(GameSearchQuery()) == repository.search(GameSearchQuery())


def test_search_is_read_only_and_rejects_incompatible_schema(tmp_path: Path) -> None:
    raw = _raw_game("dddddddd-dddd-4ddd-8ddd-dddddddddd31", "1. e4")
    database, _game_ids = _database(tmp_path, [raw])
    before = database.read_bytes()
    page = GameSearchRepository(database).search()
    assert page.total == 1
    assert database.read_bytes() == before
    assert not list(tmp_path.glob("search.db-*"))

    incompatible = tmp_path / "incompatible.db"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE not_schema_v1 (value TEXT)")
    incompatible_before = incompatible.read_bytes()
    with pytest.raises(GameSearchSchemaError):
        GameSearchRepository(incompatible).search()
    assert incompatible.read_bytes() == incompatible_before
