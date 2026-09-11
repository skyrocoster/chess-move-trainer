from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import chess
import pytest

from chess_move_trainer.database import create_schema
from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisQuality,
    AnalysisResultInput,
    AnalysisScoreKind,
)
from chess_move_trainer.database.positions import PositionRepository
from chess_move_trainer.database.stockfish import (
    MutexBusyError,
    QueueService,
    WorkerRunner,
    profile_for,
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
D4_FEN = "rnbqkbnr/pppppppp/8/3P4/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"


class _FakeMutex:
    def __init__(self, *, abandoned: bool = False, busy: bool = False) -> None:
        self.acquired_abandoned = abandoned
        self.busy = busy
        self.acquire_calls: list[float] = []
        self.released = False

    def acquire(self, *, timeout: float) -> bool:
        self.acquire_calls.append(timeout)
        return not self.busy

    def release(self) -> None:
        self.released = True


class _FakeEngine:
    def __init__(self, responses: list[object] | None = None, on_analyze=None) -> None:
        self.responses = list(responses or [])
        self.on_analyze = on_analyze
        self.calls: list[tuple[object, AnalysisQuality]] = []
        self.closed = False

    def analyze(self, position: object, quality: AnalysisQuality) -> AnalysisResultInput:
        self.calls.append((position, quality))
        if self.on_analyze is not None:
            self.on_analyze(position, quality)
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, BaseException):
                raise response
        return _result(position, quality)

    def close(self) -> None:
        self.closed = True


class _FakeClock:
    def __init__(self, current: datetime) -> None:
        self.current = current
        self.sleeps: list[float] = []

    def now(self) -> datetime:
        return self.current

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.current += timedelta(seconds=seconds)


def _result(position: object, quality: AnalysisQuality | str) -> AnalysisResultInput:
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
    profile = profile_for(quality)
    lines = tuple(
        AnalysisLine(
            rank=rank,
            score_kind=AnalysisScoreKind.CP,
            score_value=rank,
            wdl_wins=400,
            wdl_draws=300,
            wdl_losses=300,
            pv_uci=(move.uci(),),
            depth=12,
        )
        for rank, move in enumerate(tuple(board.legal_moves)[:5], start=1)
    )
    return AnalysisResultInput(
        quality=profile.quality,
        configuration_version=profile.configuration_version,
        settings=profile.settings,
        engine_name="Stockfish",
        engine_version="18",
        lines=lines,
    )


def _database(tmp_path: Path, fens: tuple[str, ...] = (START_FEN, E4_FEN, D4_FEN)):
    database = tmp_path / "worker.db"
    create_schema(database)
    positions = PositionRepository(database)
    ids = {fen: positions.resolve_fen(fen) for fen in fens}
    return database, ids


def _queue_row(database: Path, position_id: int) -> tuple[object, ...] | None:
    with sqlite3.connect(database) as connection:
        return connection.execute(
            """
            SELECT daq_requested_quality, daq_state, daq_claimed_at_utc,
                   daq_claim_token
            FROM derived_analysis_queue
            WHERE derived_position_id = ?
            """,
            (position_id,),
        ).fetchone()


def _stored_quality(database: Path, position_id: int) -> object | None:
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT dar_quality FROM derived_analysis_result WHERE derived_position_id = ?",
            (position_id,),
        ).fetchone()
    return None if row is None else row[0]


def _runner(database: Path, mutex: _FakeMutex, engine_factory, **kwargs: Any) -> WorkerRunner:
    return WorkerRunner(
        database,
        "fake-stockfish.exe",
        _mutex_factory=lambda _path: mutex,
        _engine_factory=engine_factory,
        **kwargs,
    )


def test_busy_mutex_fails_before_engine_work(tmp_path: Path) -> None:
    database, _ids = _database(tmp_path, (START_FEN,))
    mutex = _FakeMutex(busy=True)
    created: list[_FakeEngine] = []

    def engine_factory() -> _FakeEngine:
        engine = _FakeEngine()
        created.append(engine)
        return engine

    with pytest.raises(MutexBusyError):
        _runner(database, mutex, engine_factory).run()

    assert mutex.acquire_calls == [0.0]
    assert not created
    assert not mutex.released


def test_fifo_claims_immutable_quality_and_serial_engine_reuse(tmp_path: Path) -> None:
    database, ids = _database(tmp_path)
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(ids[START_FEN], AnalysisQuality.BROWSER, requested_at=origin)
    queue.enqueue(ids[E4_FEN], AnalysisQuality.TOOL, requested_at=origin + timedelta(seconds=1))
    mutex = _FakeMutex()
    engines: list[_FakeEngine] = []

    def engine_factory() -> _FakeEngine:
        engine = _FakeEngine()
        engines.append(engine)
        return engine

    outcome = _runner(database, mutex, engine_factory).run()

    assert outcome.succeeded
    assert outcome.claimed_count == outcome.completed_count == 2
    assert len(engines) == 1
    assert [quality for _position, quality in engines[0].calls] == [
        AnalysisQuality.BROWSER,
        AnalysisQuality.TOOL,
    ]
    assert engines[0].closed
    assert mutex.released
    assert _queue_row(database, ids[START_FEN]) is None
    assert _queue_row(database, ids[E4_FEN]) is None


def test_browser_completion_releases_promotion_then_tool_completes(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (START_FEN,))
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    position_id = ids[START_FEN]
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=origin)
    promoted = False

    def promote(_position: object, quality: AnalysisQuality) -> None:
        nonlocal promoted
        if not promoted:
            assert quality is AnalysisQuality.BROWSER
            queue.enqueue(
                position_id, AnalysisQuality.TOOL, requested_at=origin + timedelta(seconds=1)
            )
            promoted = True

    mutex = _FakeMutex()
    engine = _FakeEngine(on_analyze=promote)
    outcome = _runner(database, mutex, lambda: engine).run()

    assert outcome.succeeded
    assert outcome.claimed_count == outcome.completed_count == 2
    assert [quality for _position, quality in engine.calls] == [
        AnalysisQuality.BROWSER,
        AnalysisQuality.TOOL,
    ]
    assert _stored_quality(database, position_id) == "tool"
    assert _queue_row(database, position_id) is None


def test_isolated_engine_failure_replaces_process_and_is_not_retried(tmp_path: Path) -> None:
    database, ids = _database(tmp_path)
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    for offset, fen in enumerate((START_FEN, E4_FEN, D4_FEN)):
        queue.enqueue(
            ids[fen], AnalysisQuality.TOOL, requested_at=origin + timedelta(seconds=offset)
        )
    mutex = _FakeMutex()
    engines: list[_FakeEngine] = []

    def engine_factory() -> _FakeEngine:
        engine = _FakeEngine([RuntimeError("failed search")]) if not engines else _FakeEngine()
        engines.append(engine)
        return engine

    outcome = _runner(database, mutex, engine_factory).run()

    assert outcome.exit_code == 1
    assert len(outcome.failures) == 1
    assert outcome.failures[0].position_id == ids[START_FEN]
    assert len(engines) == 2
    assert len(engines[0].calls) == 1
    assert len(engines[1].calls) == 2
    assert all(engine.closed for engine in engines)
    assert _queue_row(database, ids[START_FEN]) is None
    assert _stored_quality(database, ids[E4_FEN]) == "tool"
    assert _stored_quality(database, ids[D4_FEN]) == "tool"


def test_failure_after_browser_promotion_is_released_without_same_launch_retry(
    tmp_path: Path,
) -> None:
    database, ids = _database(tmp_path, (START_FEN,))
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    position_id = ids[START_FEN]
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=origin)

    def fail_after_promotion(_position: object, quality: AnalysisQuality) -> None:
        assert quality is AnalysisQuality.BROWSER
        queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=origin + timedelta(seconds=1))

    engine = _FakeEngine([RuntimeError("browser failed")], on_analyze=fail_after_promotion)
    outcome = _runner(database, _FakeMutex(), lambda: engine).run()

    assert outcome.exit_code == 1
    assert outcome.claimed_count == 1
    assert len(engine.calls) == 1
    assert _queue_row(database, position_id) is not None
    assert _queue_row(database, position_id)[0:2] == ("tool", "queued")


def test_young_running_recovery_polls_only_to_boundary_and_publishes(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (START_FEN,))
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    position_id = ids[START_FEN]
    queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=origin)
    abandoned_claim = queue.claim(now=origin)
    assert abandoned_claim is not None
    clock = _FakeClock(origin + timedelta(seconds=90))
    mutex = _FakeMutex(abandoned=True)
    engine = _FakeEngine()

    outcome = _runner(
        database,
        mutex,
        lambda: engine,
        _clock=clock.now,
        _sleep=clock.sleep,
        recovery_poll_seconds=10,
    ).run()

    assert outcome.succeeded
    assert outcome.recovery_polls == 3
    assert clock.sleeps == [10, 10, 10]
    assert outcome.claimed_count == outcome.completed_count == 1
    assert _stored_quality(database, position_id) == "tool"
    assert _queue_row(database, position_id) is None


def test_abandoned_stale_claim_reclaims_immediately_without_waiting(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (START_FEN,))
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    position_id = ids[START_FEN]
    queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=origin)
    assert queue.claim(now=origin) is not None
    clock = _FakeClock(origin + timedelta(minutes=2, seconds=1))
    engine = _FakeEngine()

    outcome = _runner(
        database,
        _FakeMutex(abandoned=True),
        lambda: engine,
        _clock=clock.now,
        _sleep=clock.sleep,
    ).run()

    assert outcome.succeeded
    assert outcome.recovery_polls == 0
    assert clock.sleeps == []
    assert _queue_row(database, position_id) is None


def test_ctrl_c_terminates_engine_releases_claim_and_returns_130(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (START_FEN,))
    queue = QueueService(database)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    position_id = ids[START_FEN]
    queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=now)
    engine = _FakeEngine([KeyboardInterrupt()])
    mutex = _FakeMutex()

    outcome = _runner(database, mutex, lambda: engine).run()

    assert outcome.interrupted
    assert outcome.exit_code == 130
    assert outcome.claimed_count == 1
    assert engine.closed
    assert mutex.released
    assert _stored_quality(database, position_id) is None
    assert _queue_row(database, position_id)[1] == "queued"


def test_empty_queue_drains_and_exits_without_starting_engine(tmp_path: Path) -> None:
    database, _ids = _database(tmp_path, (START_FEN,))
    mutex = _FakeMutex()
    created: list[_FakeEngine] = []

    def engine_factory() -> _FakeEngine:
        engine = _FakeEngine()
        created.append(engine)
        return engine

    outcome = _runner(database, mutex, engine_factory).run()

    assert outcome.succeeded
    assert outcome.claimed_count == 0
    assert not created
    assert mutex.released
