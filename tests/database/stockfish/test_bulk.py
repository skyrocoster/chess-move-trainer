from __future__ import annotations

import sqlite3
from pathlib import Path

import chess

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisRepository,
    AnalysisResultInput,
    AnalysisScoreKind,
    PublicationOutcome,
)
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.stockfish import (
    TOOL_PROFILE,
    BulkRunner,
    StockfishAnalysis,
    StockfishError,
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
D4_FEN = "rnbqkbnr/pppppppp/8/3P4/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"


class _FakeMutex:
    def __init__(self) -> None:
        self.entered = False
        self.released = False

    def __enter__(self):
        assert not self.entered
        self.entered = True
        return self

    def __exit__(self, *_: object) -> None:
        self.released = True


class _FakeEngine:
    def __init__(self, responses: list[object] | None = None) -> None:
        self.responses = list(responses or [])
        self.calls: list[tuple[object, object]] = []
        self.closed = False

    def analyze(self, position: object, profile: object) -> StockfishAnalysis:
        assert profile is TOOL_PROFILE
        self.calls.append((position, profile))
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, BaseException):
                raise response
        return _tool_analysis(position)

    def close(self) -> None:
        self.closed = True


class _RecordingPublisher:
    def __init__(self, database: Path) -> None:
        self.repository = AnalysisRepository(database)
        self.calls: list[int] = []

    def publish(self, position_id: int, result: AnalysisResultInput) -> PublicationOutcome:
        self.calls.append(position_id)
        with sqlite3.connect(self.repository._database_path) as connection:
            assert connection.execute(
                "SELECT COUNT(*) FROM derived_analysis_queue"
            ).fetchone()[0] == 0
        return self.repository.publish(position_id, result)


def _database(tmp_path: Path) -> tuple[Path, dict[str, int]]:
    database = tmp_path / "bulk.db"
    create_schema(database)
    repository = PositionRepository(database)
    ids = {fen: repository.resolve_fen(fen) for fen in (START_FEN, E4_FEN, D4_FEN)}
    for game_number, position_id in enumerate(ids.values(), start=1):
        with sqlite3.connect(database) as connection:
            connection.execute(
                """
                INSERT INTO datasource_game (
                    dg_chesscom_game_uuid, dg_source_url, dg_original_pgn,
                    dg_trainer_color, dg_trainer_chesscom_uuid
                ) VALUES (?, ?, ?, 'white', ?)
                """,
                (
                    f"10000000-0000-4000-8000-{game_number:012d}",
                    f"https://example.test/{game_number}",
                    "1. e4 *",
                    "11111111-1111-4111-8111-111111111111",
                ),
            )
            game_id = connection.execute(
                "SELECT dg_game_id FROM datasource_game WHERE dg_chesscom_game_uuid = ?",
                (f"10000000-0000-4000-8000-{game_number:012d}",),
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


def _tool_analysis(position: object) -> StockfishAnalysis:
    assert hasattr(position, "placement")
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


def _runner(
    database: Path,
    engine_factory,
    mutex: _FakeMutex,
    publisher_factory=None,
) -> BulkRunner:
    return BulkRunner(
        database,
        "fake-stockfish.exe",
        page_size=1,
        _engine_factory=engine_factory,
        _mutex_factory=lambda _path: mutex,
        _publisher_factory=publisher_factory,
    )


def test_limit_restart_and_unlimited_recompute_publish_directly_without_queue(
    tmp_path: Path,
) -> None:
    database, _ids = _database(tmp_path)
    engines: list[_FakeEngine] = []
    publishers: list[_RecordingPublisher] = []
    mutexes: list[_FakeMutex] = []

    def engine_factory() -> _FakeEngine:
        engine = _FakeEngine()
        engines.append(engine)
        return engine

    def publisher_factory() -> _RecordingPublisher:
        publisher = _RecordingPublisher(database)
        publishers.append(publisher)
        return publisher

    def mutex_factory(_path: Path) -> _FakeMutex:
        mutex = _FakeMutex()
        mutexes.append(mutex)
        return mutex

    runner = BulkRunner(
        database,
        "fake-stockfish.exe",
        page_size=1,
        _engine_factory=engine_factory,
        _publisher_factory=publisher_factory,
        _mutex_factory=mutex_factory,
    )

    first = runner.run(limit=1)
    second = runner.run()
    third = runner.run()

    assert (first.selected_count, first.published_count, first.exit_code) == (1, 1, 0)
    assert (second.selected_count, second.published_count, second.exit_code) == (2, 2, 0)
    assert third == type(third)(0, 0, 0)
    assert len(engines) == 2
    assert all(engine.closed for engine in engines)
    assert all(mutex.entered and mutex.released for mutex in mutexes)
    assert sum(len(publisher.calls) for publisher in publishers) == 3
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_result"
        ).fetchone()[0] == 3
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_queue"
        ).fetchone()[0] == 0


def test_isolated_failure_continues_once_without_same_launch_retry(tmp_path: Path) -> None:
    database, ids = _database(tmp_path)
    mutex = _FakeMutex()
    engine = _FakeEngine([StockfishError("first target failed")])
    runner = _runner(database, lambda: engine, mutex)

    outcome = runner.run()

    assert outcome.selected_count == 3
    assert outcome.published_count == 2
    assert len(outcome.failures) == 1
    assert outcome.failures[0].position_id == ids[START_FEN]
    assert len(engine.calls) == 3
    assert outcome.exit_code == 1
    assert engine.closed
    assert mutex.entered and mutex.released


def test_ctrl_c_discards_only_current_result_and_releases_bulk_mutex(tmp_path: Path) -> None:
    database, _ids = _database(tmp_path)
    mutex = _FakeMutex()
    engine = _FakeEngine([KeyboardInterrupt()])
    runner = _runner(database, lambda: engine, mutex)

    outcome = runner.run()

    assert outcome.interrupted
    assert outcome.selected_count == 1
    assert outcome.published_count == 0
    assert outcome.exit_code == 130
    assert engine.closed
    assert mutex.entered and mutex.released
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM derived_analysis_result"
        ).fetchone()[0] == 0


def test_direct_tool_profile_is_used_for_every_serial_engine_call(tmp_path: Path) -> None:
    database, _ids = _database(tmp_path)
    mutex = _FakeMutex()
    engine = _FakeEngine()
    runner = _runner(database, lambda: engine, mutex)

    outcome = runner.run(limit=2)

    assert outcome.succeeded
    assert len(engine.calls) == 2
    assert all(profile is TOOL_PROFILE for _position, profile in engine.calls)
