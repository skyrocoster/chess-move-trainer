from __future__ import annotations

import sqlite3
from pathlib import Path

import chess
import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import AnalysisQuality, AnalysisRepository
from chess_move_trainer.database.positions import PositionRepository, canonicalize_fen
from chess_move_trainer.database.stockfish import (
    BackgroundTargetSelector,
    BulkTargetSelector,
    QueueService,
)
from chess_move_trainer.database.stockfish.configuration import profile_for

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
D4_FEN = "rnbqkbnr/pppppppp/8/3P4/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
E4_E5_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
E4_E5_NF3_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"


def _database(tmp_path: Path) -> Path:
    database = tmp_path / "targets.db"
    create_schema(database)
    return database


def _position_ids(database: Path, fens: tuple[str, ...]) -> dict[str, int]:
    repository = PositionRepository(database)
    return {fen: repository.resolve_fen(fen) for fen in fens}


def _add_game_occurrences(
    database: Path,
    game_number: int,
    position_ids: tuple[int, ...],
    *,
    first_ply: int = 0,
) -> None:
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            INSERT INTO datasource_game (
                dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                dg_trainer_color, dg_trainer_chesscom_uuid
            ) VALUES (?, ?, ?, 'white', ?)
            """,
            (
                f"00000000-0000-4000-8000-{game_number:012d}",
                f"https://example.test/{game_number}",
                "1. e4 *",
                "11111111-1111-4111-8111-111111111111",
            ),
        )
        game_id = connection.execute(
            "SELECT dg_game_id FROM datasource_game WHERE dg_chesscom_game_uuid = ?",
            (f"00000000-0000-4000-8000-{game_number:012d}",),
        ).fetchone()[0]
        for offset, position_id in enumerate(position_ids):
            connection.execute(
                """
                INSERT INTO derived_game_position (
                    datasource_game_id, dgp_ply, derived_position_id,
                    dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
                ) VALUES (?, ?, ?, ?, 0, 1)
                """,
                (game_id, first_ply + offset, position_id, None),
            )


def _add_route(database: Path, endpoint_id: int) -> None:
    with sqlite3.connect(database) as connection:
        connection.execute(
            "INSERT INTO datasource_opening (do_eco, do_name) VALUES ('A00', 'Test route')"
        )
        opening_id = connection.execute(
            "SELECT do_opening_id FROM datasource_opening WHERE do_eco = 'A00'"
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO derived_opening_route (datasource_opening_id, derived_position_id)
            VALUES (?, ?)
            """,
            (opening_id, endpoint_id),
        )
        route_id = connection.execute(
            "SELECT dor_route_id FROM derived_opening_route WHERE datasource_opening_id = ?",
            (opening_id,),
        ).fetchone()[0]
        connection.executemany(
            """
            INSERT INTO derived_opening_route_move (
                derived_opening_route_id, dorm_ply, dorm_move_uci
            ) VALUES (?, ?, ?)
            """,
            [(route_id, 1, "e2e4"), (route_id, 2, "e7e5"), (route_id, 3, "g1f3")],
        )


def test_union_replays_routes_reuses_positions_and_orders_by_frequency_then_id(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    ids = _position_ids(
        database,
        (START_FEN, E4_FEN, D4_FEN, E4_E5_NF3_FEN),
    )
    _add_game_occurrences(database, 1, (ids[START_FEN], ids[E4_FEN]))
    _add_game_occurrences(database, 2, (ids[START_FEN], ids[D4_FEN]))
    _add_game_occurrences(database, 3, (ids[START_FEN],))
    _add_route(database, ids[E4_E5_NF3_FEN])

    targets = list(BulkTargetSelector(database, page_size=2).iter_targets())

    assert [target.frequency for target in targets] == [3, 1, 1, 0, 0]
    assert [target.position_id for target in targets[:3]] == [
        ids[START_FEN],
        ids[E4_FEN],
        ids[D4_FEN],
    ]
    route_only = targets[3:]
    assert all(target.frequency == 0 for target in route_only)
    assert len(route_only) == 2
    assert {target.position_id for target in route_only}.isdisjoint(
        {ids[START_FEN], ids[E4_FEN], ids[D4_FEN]}
    )
    with sqlite3.connect(database) as connection:
        stored = connection.execute("SELECT dp_position_id FROM derived_position").fetchall()
    assert len(stored) >= 5


def test_game_pages_are_bounded_and_stable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database = _database(tmp_path)
    ids = _position_ids(database, (START_FEN, E4_FEN, D4_FEN, E4_E5_FEN, E4_E5_NF3_FEN))
    for game_number, position_id in enumerate(ids.values(), start=1):
        _add_game_occurrences(database, game_number, (position_id,))

    selector = BulkTargetSelector(database, page_size=2)
    page_sizes: list[int] = []
    original = selector._load_game_page

    def wrapped(cursor):
        page = original(cursor)
        page_sizes.append(len(page))
        return page

    monkeypatch.setattr(selector, "_load_game_page", wrapped)
    targets = list(selector.iter_targets())

    assert len(targets) == 5
    assert page_sizes == [2, 2, 1, 0]
    assert all(size <= 2 for size in page_sizes)


def test_background_pages_use_distinct_game_frequency_and_keyset_boundaries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _database(tmp_path)
    ids = _position_ids(database, (START_FEN, E4_FEN, D4_FEN))
    _add_game_occurrences(database, 1, (ids[START_FEN], ids[START_FEN], ids[E4_FEN]))
    _add_game_occurrences(database, 2, (ids[START_FEN], ids[D4_FEN]))
    _add_game_occurrences(database, 3, (ids[D4_FEN],))

    selector = BackgroundTargetSelector(database, page_size=1)
    page_sizes: list[int] = []
    original = selector._load_game_page

    def wrapped(cursor):
        page = original(cursor)
        page_sizes.append(len(page))
        return page

    monkeypatch.setattr(selector, "_load_game_page", wrapped)
    targets = list(selector.iter_targets())

    assert [(target.frequency, target.position_id) for target in targets] == [
        (2, ids[START_FEN]),
        (2, ids[D4_FEN]),
        (1, ids[E4_FEN]),
    ]
    assert page_sizes == [1, 1, 1, 0]
    assert all(size <= 1 for size in page_sizes)


def test_background_selector_covers_all_plies_with_canonical_targets(tmp_path: Path) -> None:
    database = _database(tmp_path)
    ids = _position_ids(database, (E4_E5_NF3_FEN,))
    _add_game_occurrences(database, 1, (ids[E4_E5_NF3_FEN],), first_ply=20)

    targets = list(BackgroundTargetSelector(database).iter_targets())

    assert len(targets) == 1
    assert targets[0].position_id == ids[E4_E5_NF3_FEN]
    assert targets[0].frequency == 1
    assert targets[0].position == canonicalize_fen(E4_E5_NF3_FEN)


def test_background_selector_applies_set_based_result_and_queue_eligibility(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    terminal_fen = "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"
    missing_fen = "rnbqkbnr/pppp1ppp/8/4p3/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 2"
    queued_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    ids = _position_ids(
        database,
        (START_FEN, E4_FEN, D4_FEN, E4_E5_FEN, terminal_fen, missing_fen, queued_fen),
    )
    for game_number, position_id in enumerate(ids.values(), start=1):
        _add_game_occurrences(database, game_number, (position_id,))

    repository = AnalysisRepository(database)
    current_browser = ids[START_FEN]
    stale_browser = ids[E4_FEN]
    current_tool = ids[D4_FEN]
    stale_tool = ids[E4_E5_FEN]
    terminal = ids[terminal_fen]
    for position_id, quality, engine in (
        (current_browser, AnalysisQuality.BROWSER, "19"),
        (stale_browser, AnalysisQuality.BROWSER, "19"),
        (current_tool, AnalysisQuality.TOOL, "19"),
        (stale_tool, AnalysisQuality.TOOL, "19"),
    ):
        assert repository.publish(
            position_id,
            _valid_result(
                database,
                position_id,
                quality,
                profile_for(quality).configuration_version,
                engine,
            ),
        ).saved
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE derived_analysis_result SET dar_configuration_version = 1 WHERE derived_position_id = ?",
            (stale_browser,),
        )
        connection.execute(
            "UPDATE derived_analysis_result SET dar_configuration_version = 2 WHERE derived_position_id = ?",
            (stale_tool,),
        )
    terminal_result = _terminal_result(profile_for(AnalysisQuality.BROWSER))
    assert repository.publish(terminal, terminal_result).saved
    QueueService(database).enqueue(ids[queued_fen], AnalysisQuality.BROWSER)

    eligible = {target.position_id for target in BackgroundTargetSelector(database).iter_targets()}

    assert eligible == {stale_browser, ids[missing_fen]}


def test_eligibility_includes_missing_browser_and_stale_tool_but_skips_current_tool(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)
    ids = _position_ids(database, (START_FEN, E4_FEN, D4_FEN, E4_E5_FEN))
    for game_number, position_id in enumerate(ids.values(), start=1):
        _add_game_occurrences(database, game_number, (position_id,))
    repository = AnalysisRepository(database)
    for fen, quality, version, engine in (
        (E4_FEN, AnalysisQuality.BROWSER, 1, "anything"),
        (D4_FEN, AnalysisQuality.TOOL, 1, "19"),
        (E4_E5_FEN, AnalysisQuality.TOOL, 2, "19"),
    ):
        position_id = ids[fen]
        result = _valid_result(
            database,
            position_id,
            quality,
            profile_for(quality).configuration_version,
            engine,
        )
        assert repository.publish(position_id, result).saved
        with sqlite3.connect(database) as connection:
            connection.execute(
                """
                UPDATE derived_analysis_result
                SET dar_configuration_version = ?, dar_engine_version = ?
                WHERE derived_position_id = ?
                """,
                (version, engine, position_id),
            )

    eligible = {target.position_id for target in BulkTargetSelector(database).iter_targets()}

    assert eligible == {ids[START_FEN], ids[E4_FEN], ids[E4_E5_FEN]}


@pytest.mark.parametrize("limit", [0, -1, True])
def test_limit_must_be_positive_when_supplied(tmp_path: Path, limit: int) -> None:
    database = _database(tmp_path)
    with pytest.raises(ValueError, match="positive"):
        list(BulkTargetSelector(database).iter_targets(limit=limit))


def _valid_result(
    database: Path,
    position_id: int,
    quality: AnalysisQuality,
    version: int,
    engine: str,
):
    from chess_move_trainer.database.analysis import (
        AnalysisLine,
        AnalysisScoreKind,
        validate_analysis_result,
    )

    with sqlite3.connect(database) as connection:
        row = connection.execute(
            """
            SELECT dp_placement, dp_side_to_move, dp_castling_rights, dp_legal_en_passant
            FROM derived_position WHERE dp_position_id = ?
            """,
            (position_id,),
        ).fetchone()
    assert row is not None
    board = chess.Board(" ".join((*row, "0", "1")))
    profile = profile_for(quality)
    moves = tuple(move.uci() for move in board.legal_moves)[: profile.multipv]

    return validate_analysis_result(
        quality=quality,
        configuration_version=version,
        settings=dict(profile.settings),
        engine_name="Stockfish",
        engine_version=engine,
        lines=tuple(
            AnalysisLine(
                rank=rank,
                score_kind=AnalysisScoreKind.CP,
                score_value=rank,
                wdl_wins=400,
                wdl_draws=300,
                wdl_losses=300,
                pv_uci=(move,),
                depth=8,
            )
            for rank, move in enumerate(moves, start=1)
        ),
    )


def _terminal_result(profile):
    from chess_move_trainer.database.analysis import validate_analysis_result

    return validate_analysis_result(
        quality=profile.quality,
        configuration_version=profile.configuration_version,
        settings=dict(profile.settings),
        engine_name="Stockfish",
        engine_version="19",
        lines=(),
    )
