from __future__ import annotations

import sqlite3
from pathlib import Path

import chess

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisScoreKind,
)
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.stockfish import (
    INITIAL_TECHNICAL_CATEGORIES,
    INITIAL_TECHNICAL_POSITIONS,
    InitialAnalysisTargetSelector,
    BulkRunner,
    StockfishAnalysis,
    TOOL_PROFILE,
)


CHECKMATE_FEN = INITIAL_TECHNICAL_POSITIONS[0].fen
COMMON_MOVES = (
    "e2e4",
    "e7e5",
    "g1f3",
    "b8c6",
    "f1c4",
    "g8f6",
    "d2d3",
    "f8c5",
    "c2c3",
    "d7d6",
    "e1g1",
    "e8g8",
    "c1g5",
    "h7h6",
    "g5h4",
    "c6b8",
    "b1d2",
    "b8c6",
    "f3d4",
)


class _FakeMutex:
    def __init__(self) -> None:
        self.entered = False
        self.released = False

    def __enter__(self) -> _FakeMutex:
        assert not self.entered
        self.entered = True
        return self

    def __exit__(self, *_: object) -> None:
        self.released = True


class _FakeEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[object, object]] = []
        self.closed = False

    def analyze(self, position: object, profile: object) -> StockfishAnalysis:
        assert profile is TOOL_PROFILE
        self.calls.append((position, profile))
        canonical = position
        board = chess.Board(
            " ".join(
                (
                    canonical.placement,
                    canonical.side_to_move,
                    canonical.castling_rights,
                    canonical.legal_en_passant,
                    "0",
                    "1",
                )
            )
        )
        moves = tuple(move.uci() for move in board.legal_moves)[:5]
        result = AnalysisResultInput(
            quality=AnalysisQuality.TOOL,
            configuration_version=TOOL_PROFILE.configuration_version,
            settings=TOOL_PROFILE.settings,
            engine_name="Stockfish",
            engine_version="18",
            lines=tuple(
                AnalysisLine(
                    rank=rank,
                    score_kind=AnalysisScoreKind.CP,
                    score_value=rank,
                    wdl_wins=400,
                    wdl_draws=300,
                    wdl_losses=300,
                    pv_uci=(move,),
                    depth=12,
                )
                for rank, move in enumerate(moves, start=1)
            ),
        )
        return StockfishAnalysis(
            profile=TOOL_PROFILE,
            result=result,
            terminal_kind=None,
        )

    def close(self) -> None:
        self.closed = True


def _common_fens() -> tuple[str, ...]:
    board = chess.Board()
    fens = [board.fen()]
    for move in COMMON_MOVES:
        board.push_uci(move)
        fens.append(board.fen())
    return tuple(fens)


def _database(tmp_path: Path) -> tuple[Path, dict[str, int]]:
    database = tmp_path / "initial-analysis.db"
    create_schema(database)
    common_fens = (CHECKMATE_FEN, *_common_fens())
    ids = {
        fen: PositionRepository(database).resolve_fen(fen) for fen in common_fens
    }
    with sqlite3.connect(database) as connection:
        for game_number, position_id in enumerate(ids.values(), start=1):
            connection.execute(
                """
                INSERT INTO datasource_game (
                    dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                    dg_trainer_color, dg_trainer_chesscom_uuid
                ) VALUES (?, ?, ?, 'white', ?)
                """,
                (
                    f"20000000-0000-4000-8000-{game_number:012d}",
                    f"https://example.test/initial/{game_number}",
                    "1. e4 *",
                    "11111111-1111-4111-8111-111111111111",
                ),
            )
            game_id = connection.execute(
                "SELECT dg_game_id FROM datasource_game "
                "WHERE dg_chesscom_game_uuid = ?",
                (f"20000000-0000-4000-8000-{game_number:012d}",),
            ).fetchone()[0]
            connection.execute(
                """
                INSERT INTO derived_game_position (
                    datasource_game_id, dgp_ply, derived_position_id,
                    dgp_move_uci, dgp_halfmove_clock, dgp_fullmove_number
                ) VALUES (?, 0, ?, NULL, 0, 1)
                """,
                (game_id, position_id),
            )
    return database, ids


def test_initial_selector_is_deterministic_unique_and_backfills_technical_overlap(
    tmp_path: Path,
) -> None:
    database, ids = _database(tmp_path)

    first = list(InitialAnalysisTargetSelector(database, page_size=3).iter_targets())
    second = list(InitialAnalysisTargetSelector(database, page_size=3).iter_targets())

    assert len(first) == 25
    assert [target.position_id for target in first] == [
        target.position_id for target in second
    ]
    assert len({target.position_id for target in first}) == 25
    assert ids[CHECKMATE_FEN] not in [target.position_id for target in first[:20]]
    assert ids[_common_fens()[-1]] == first[19].position_id
    assert {target.position for target in first[20:]} == {
        representative.canonical for representative in INITIAL_TECHNICAL_POSITIONS
    }


def test_fixed_representatives_cover_the_five_stable_technical_categories() -> None:
    assert INITIAL_TECHNICAL_CATEGORIES == (
        "checkmate",
        "stalemate",
        "legal en passant",
        "promotion",
        "castling",
    )
    for representative in INITIAL_TECHNICAL_POSITIONS:
        board = chess.Board(representative.fen)
        if representative.category == "checkmate":
            assert board.is_checkmate()
        elif representative.category == "stalemate":
            assert board.is_stalemate()
        elif representative.category == "legal en passant":
            assert board.has_legal_en_passant()
        elif representative.category == "promotion":
            assert any(move.promotion for move in board.legal_moves)
        elif representative.category == "castling":
            assert any(board.is_castling(move) for move in board.legal_moves)


def test_initial_analysis_is_serial_resumable_direct_and_queue_free(
    tmp_path: Path,
) -> None:
    database, _ids = _database(tmp_path)
    engines: list[_FakeEngine] = []
    mutexes: list[_FakeMutex] = []

    def engine_factory() -> _FakeEngine:
        engine = _FakeEngine()
        engines.append(engine)
        return engine

    def mutex_factory(_path: Path) -> _FakeMutex:
        mutex = _FakeMutex()
        mutexes.append(mutex)
        return mutex

    runner = BulkRunner(
        database,
        "fake-stockfish.exe",
        _engine_factory=engine_factory,
        _mutex_factory=mutex_factory,
    )

    first = runner.run(preset="initial")

    assert first.selected_count == first.published_count == 25
    assert first.preset == "initial"
    assert first.technical_categories == INITIAL_TECHNICAL_CATEGORIES
    assert len(engines) == 1
    assert len(engines[0].calls) == 25
    assert engines[0].closed
    assert mutexes[0].entered and mutexes[0].released
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_result"
        ).fetchone()[0] == 25
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_queue"
        ).fetchone()[0] == 0
        terminal_kinds = {
            row[0]
            for row in connection.execute(
                """
                SELECT dar_terminal_kind
                FROM derived_analysis_result AS result
                JOIN derived_position AS position
                  ON position.dp_position_id = result.derived_position_id
                WHERE position.dp_placement IN ('7k/6Q1/6K1/8/8/8/8/8',
                                                 '7k/5Q2/6K1/8/8/8/8/8')
                """
            )
        }
    assert terminal_kinds == {"checkmate", "stalemate"}

    second = runner.run(preset="initial")

    assert second.selected_count == 0
    assert second.published_count == 0
    assert len(engines) == 1
