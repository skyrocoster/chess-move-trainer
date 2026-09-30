from __future__ import annotations

import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
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
from chess_move_trainer.database.positions import PositionRepository, canonicalize_fen
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
        profile = profile_for(quality)
        self.calls.append((position, profile.quality))
        if self.on_analyze is not None:
            self.on_analyze(position, profile.quality)
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, BaseException):
                raise response
        return _result(position, profile)

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


class _FakeBackgroundTarget:
    def __init__(self, position_id: int) -> None:
        self.position_id = position_id


class _FakeBackgroundSelector:
    def __init__(self, position_ids: list[int]) -> None:
        self._targets = [_FakeBackgroundTarget(position_id) for position_id in position_ids]
        self.calls = 0

    def iter_targets(self):
        self.calls += 1
        while self._targets:
            yield self._targets.pop(0)


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
        for rank, move in enumerate(tuple(board.legal_moves)[: profile.multipv], start=1)
    )
    return AnalysisResultInput(
        quality=profile.quality,
        configuration_version=profile.configuration_version,
        settings=profile.settings,
        engine_name="Stockfish",
        engine_version="19",
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


def _queue_rows(database: Path) -> list[tuple[object, ...]]:
    with sqlite3.connect(database) as connection:
        return connection.execute(
            """
            SELECT derived_position_id, daq_requested_quality, daq_state
            FROM derived_analysis_queue
            ORDER BY derived_position_id
            """
        ).fetchall()


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
    database = tmp_path / "must-not-be-created.db"
    mutex = _FakeMutex(busy=True)
    created: list[_FakeEngine] = []

    def engine_factory() -> _FakeEngine:
        engine = _FakeEngine()
        created.append(engine)
        return engine

    with pytest.raises(MutexBusyError, match="Stockfish analysis is already running"):
        _runner(database, mutex, engine_factory).run()

    assert mutex.acquire_calls == [0.0]
    assert not created
    assert not mutex.released
    assert not database.exists()


def test_fifo_claims_immutable_quality_and_serial_engine_reuse(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (START_FEN, E4_FEN))
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(ids[E4_FEN], AnalysisQuality.TOOL, requested_at=origin + timedelta(seconds=1))
    queue.enqueue(ids[START_FEN], AnalysisQuality.BROWSER, requested_at=origin)
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
    assert engines[0].calls == [
        (canonicalize_fen(START_FEN), AnalysisQuality.BROWSER),
        (canonicalize_fen(E4_FEN), AnalysisQuality.TOOL),
    ]
    assert engines[0].closed
    assert mutex.released
    assert _queue_row(database, ids[START_FEN]) is None
    assert _queue_row(database, ids[E4_FEN]) is None


def test_requested_work_precedes_one_at_a_time_background_browser_work(
    tmp_path: Path,
) -> None:
    database, ids = _database(tmp_path)
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    queue.enqueue(ids[START_FEN], AnalysisQuality.TOOL, requested_at=origin)
    selector = _FakeBackgroundSelector([ids[E4_FEN], ids[D4_FEN]])
    observed_rows: list[list[tuple[object, ...]]] = []

    def on_analyze(_position: object, _quality: AnalysisQuality) -> None:
        observed_rows.append(_queue_rows(database))

    engine = _FakeEngine(on_analyze=on_analyze)
    outcome = _runner(
        database,
        _FakeMutex(),
        lambda: engine,
        _background_selector_factory=lambda _path, _timeout: selector,
    ).run()

    assert outcome.succeeded
    assert outcome.claimed_count == outcome.completed_count == 3
    assert engine.calls == [
        (canonicalize_fen(START_FEN), AnalysisQuality.TOOL),
        (canonicalize_fen(E4_FEN), AnalysisQuality.BROWSER),
        (canonicalize_fen(D4_FEN), AnalysisQuality.BROWSER),
    ]
    assert observed_rows == [
        [(ids[START_FEN], "tool", "running")],
        [(ids[E4_FEN], "browser", "running")],
        [(ids[D4_FEN], "browser", "running")],
    ]
    assert engine.closed
    assert _queue_rows(database) == []


def test_queue_is_rechecked_before_next_background_target(tmp_path: Path) -> None:
    database, ids = _database(tmp_path)
    queue = QueueService(database)
    selector = _FakeBackgroundSelector([ids[E4_FEN], ids[D4_FEN]])

    def enqueue_requested_after_first_background(
        _position: object, quality: AnalysisQuality
    ) -> None:
        if quality is AnalysisQuality.BROWSER and len(engine.calls) == 1:
            queue.enqueue(ids[START_FEN], AnalysisQuality.TOOL)

    engine = _FakeEngine(on_analyze=enqueue_requested_after_first_background)
    outcome = _runner(
        database,
        _FakeMutex(),
        lambda: engine,
        _background_selector_factory=lambda _path, _timeout: selector,
    ).run()

    assert outcome.succeeded
    assert outcome.claimed_count == outcome.completed_count == 3
    assert engine.calls == [
        (canonicalize_fen(E4_FEN), AnalysisQuality.BROWSER),
        (canonicalize_fen(START_FEN), AnalysisQuality.TOOL),
        (canonicalize_fen(D4_FEN), AnalysisQuality.BROWSER),
    ]
    assert _queue_rows(database) == []
    assert _stored_quality(database, ids[START_FEN]) == "tool"
    assert _stored_quality(database, ids[E4_FEN]) == "browser"
    assert _stored_quality(database, ids[D4_FEN]) == "browser"


def test_background_interruption_releases_work_for_rerun_recovery(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (E4_FEN,))
    selector = _FakeBackgroundSelector([ids[E4_FEN]])
    interrupted_engine = _FakeEngine([KeyboardInterrupt()])
    first = _runner(
        database,
        _FakeMutex(),
        lambda: interrupted_engine,
        _background_selector_factory=lambda _path, _timeout: selector,
    ).run()

    assert first.interrupted
    assert first.exit_code == 130
    assert first.claimed_count == 1
    assert first.completed_count == 0
    assert _queue_row(database, ids[E4_FEN]) == ("browser", "queued", None, None)
    assert _stored_quality(database, ids[E4_FEN]) is None
    assert interrupted_engine.closed

    recovery_engine = _FakeEngine()
    second = _runner(
        database,
        _FakeMutex(),
        lambda: recovery_engine,
        _background_selector_factory=lambda _path, _timeout: _FakeBackgroundSelector([]),
    ).run()

    assert second.succeeded
    assert second.claimed_count == second.completed_count == 1
    assert recovery_engine.calls == [(canonicalize_fen(E4_FEN), AnalysisQuality.BROWSER)]
    assert recovery_engine.closed
    assert _queue_row(database, ids[E4_FEN]) is None
    assert _stored_quality(database, ids[E4_FEN]) == "browser"


def test_background_failure_is_isolated_without_same_launch_retry(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (E4_FEN, D4_FEN))
    # Offer the failed target again to prove this launch does not retry it.
    selector = _FakeBackgroundSelector([ids[E4_FEN], ids[D4_FEN], ids[E4_FEN]])
    engines: list[_FakeEngine] = []

    def engine_factory() -> _FakeEngine:
        engine = (
            _FakeEngine([RuntimeError("background search failed")])
            if not engines
            else _FakeEngine()
        )
        engines.append(engine)
        return engine

    outcome = _runner(
        database,
        _FakeMutex(),
        engine_factory,
        _background_selector_factory=lambda _path, _timeout: selector,
    ).run()

    assert outcome.exit_code == 1
    assert outcome.claimed_count == 2
    assert outcome.completed_count == 1
    assert len(outcome.failures) == 1
    assert outcome.failures[0].position_id == ids[E4_FEN]
    assert outcome.failures[0].message == "background search failed"
    assert len(engines) == 2
    assert engines[0].calls == [(canonicalize_fen(E4_FEN), AnalysisQuality.BROWSER)]
    assert engines[1].calls == [(canonicalize_fen(D4_FEN), AnalysisQuality.BROWSER)]
    assert _queue_rows(database) == []
    assert _stored_quality(database, ids[E4_FEN]) is None
    assert _stored_quality(database, ids[D4_FEN]) == "browser"
    assert all(engine.closed for engine in engines)


def test_browser_completion_releases_promotion_then_tool_completes(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (START_FEN,))
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    position_id = ids[START_FEN]
    queue.enqueue(position_id, AnalysisQuality.BROWSER, requested_at=origin)
    promoted = False
    stored_before_analysis: list[object | None] = []

    def promote(_position: object, quality: AnalysisQuality) -> None:
        nonlocal promoted
        stored_before_analysis.append(_stored_quality(database, position_id))
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
    assert stored_before_analysis == [None, "browser"]
    assert _stored_quality(database, position_id) == "tool"
    assert _queue_row(database, position_id) is None
    assert engine.closed
    assert mutex.released


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
    closed_before_replacement: list[bool] = []

    def engine_factory() -> _FakeEngine:
        if engines:
            closed_before_replacement.append(engines[-1].closed)
        engine = _FakeEngine([RuntimeError("failed search")]) if not engines else _FakeEngine()
        engines.append(engine)
        return engine

    outcome = _runner(database, mutex, engine_factory).run()

    assert outcome.exit_code == 1
    assert outcome.claimed_count == 3
    assert outcome.completed_count == 2
    assert len(outcome.failures) == 1
    assert outcome.failures[0].position_id == ids[START_FEN]
    assert outcome.failures[0].message == "failed search"
    assert len(engines) == 2
    assert closed_before_replacement == [True]
    assert engines[0].calls == [(canonicalize_fen(START_FEN), AnalysisQuality.TOOL)]
    assert engines[1].calls == [
        (canonicalize_fen(E4_FEN), AnalysisQuality.TOOL),
        (canonicalize_fen(D4_FEN), AnalysisQuality.TOOL),
    ]
    assert all(engine.closed for engine in engines)
    assert mutex.released
    assert _queue_rows(database) == []
    assert _stored_quality(database, ids[START_FEN]) is None
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
    assert outcome.completed_count == 0
    assert len(outcome.failures) == 1
    assert outcome.failures[0].position_id == position_id
    assert outcome.failures[0].message == "browser failed"
    assert engine.calls == [(canonicalize_fen(START_FEN), AnalysisQuality.BROWSER)]
    assert engine.closed
    assert _queue_row(database, position_id) == ("tool", "queued", None, None)
    assert _stored_quality(database, position_id) is None


def test_young_running_recovery_polls_only_to_boundary_and_publishes(tmp_path: Path) -> None:
    database, ids = _database(tmp_path, (START_FEN,))
    queue = QueueService(database)
    origin = datetime(2026, 1, 1, tzinfo=UTC)
    position_id = ids[START_FEN]
    queue.enqueue(position_id, AnalysisQuality.TOOL, requested_at=origin)
    abandoned_claim = queue.claim(now=origin)
    assert abandoned_claim is not None
    clock = _FakeClock(origin + timedelta(seconds=95))
    mutex = _FakeMutex(abandoned=True)
    analysis_started_at: list[datetime] = []
    engine = _FakeEngine(
        on_analyze=lambda _position, _quality: analysis_started_at.append(clock.now())
    )

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
    assert clock.sleeps == [10, 10, 5]
    assert analysis_started_at == [origin + timedelta(seconds=120)]
    assert outcome.claimed_count == outcome.completed_count == 1
    assert engine.calls == [(canonicalize_fen(START_FEN), AnalysisQuality.TOOL)]
    assert engine.closed
    assert mutex.released
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
    assert outcome.claimed_count == outcome.completed_count == 1
    assert engine.calls == [(canonicalize_fen(START_FEN), AnalysisQuality.TOOL)]
    assert engine.closed
    assert _stored_quality(database, position_id) == "tool"
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
    assert outcome.completed_count == 0
    assert outcome.failures == ()
    assert engine.calls == [(canonicalize_fen(START_FEN), AnalysisQuality.TOOL)]
    assert engine.closed
    assert mutex.released
    assert _stored_quality(database, position_id) is None
    assert _queue_row(database, position_id) == ("tool", "queued", None, None)


def test_empty_queue_drains_and_exits_without_starting_engine(tmp_path: Path) -> None:
    database, _ids = _database(tmp_path, ())
    mutex = _FakeMutex()

    def engine_factory() -> _FakeEngine:
        pytest.fail("An empty queue must not start an engine")

    outcome = _runner(database, mutex, engine_factory).run()

    assert outcome.succeeded
    assert outcome.claimed_count == outcome.completed_count == 0
    assert mutex.acquire_calls == [0.0]
    assert mutex.released


def test_parallel_workers_claim_six_distinct_background_targets(tmp_path: Path) -> None:
    fens: list[str] = []
    for move in ("e2e4", "d2d4", "c2c4", "g1f3", "b1c3", "f2f4"):
        board = chess.Board()
        board.push_uci(move)
        fens.append(board.fen())
    database, ids = _database(tmp_path, tuple(fens))
    position_ids = list(ids.values())
    selector_batches = iter(position_ids)
    selector_lock = threading.Lock()
    barrier = threading.Barrier(6)

    def selector_factory(_path: Path, _timeout: float) -> _FakeBackgroundSelector:
        with selector_lock:
            position_id = next(selector_batches)
        return _FakeBackgroundSelector([position_id])

    def run_one() -> tuple[object, _FakeEngine]:
        engine = _FakeEngine(on_analyze=lambda _position, _quality: barrier.wait(timeout=5))
        outcome = _runner(
            database,
            _FakeMutex(busy=True),
            lambda: engine,
            parallel=True,
            _background_selector_factory=selector_factory,
        ).run()
        return outcome, engine

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(lambda _index: run_one(), range(6)))

    for outcome, engine in results:
        assert outcome.succeeded, outcome.failures
        assert outcome.claimed_count == outcome.completed_count == 1
        assert len(engine.calls) == 1
        assert engine.calls[0][1] is AnalysisQuality.BROWSER
        assert engine.closed
    assert _queue_rows(database) == []
    assert all(_stored_quality(database, position_id) == "browser" for position_id in position_ids)


def test_parallel_worker_claims_requested_work_before_background_refill(tmp_path: Path) -> None:
    fens: list[str] = []
    for move in ("e2e4", "d2d4", "c2c4", "g1f3", "b1c3", "f2f4", "a2a3"):
        board = chess.Board()
        board.push_uci(move)
        fens.append(board.fen())
    database, ids = _database(tmp_path, tuple(fens))
    position_ids = list(ids.values())
    queue = QueueService(database)
    background_claims = [
        queue.seed_and_claim_background(position_id, capacity=6) for position_id in position_ids[:6]
    ]
    assert all(claim is not None for claim in background_claims)
    assert queue.complete(
        background_claims[0],
        _result(canonicalize_fen(fens[0]), AnalysisQuality.BROWSER),
    ).applied
    queue.enqueue(position_ids[0], AnalysisQuality.TOOL)
    engine = _FakeEngine()

    outcome = _runner(
        database,
        _FakeMutex(busy=True),
        lambda: engine,
        parallel=True,
        _background_selector_factory=lambda _path, _timeout: _FakeBackgroundSelector(
            [position_ids[6]]
        ),
    ).run()

    assert outcome.succeeded
    assert outcome.claimed_count == outcome.completed_count == 2
    assert engine.calls == [
        (canonicalize_fen(fens[0]), AnalysisQuality.TOOL),
        (canonicalize_fen(fens[6]), AnalysisQuality.BROWSER),
    ]
    assert engine.closed
    assert _queue_rows(database) == [
        (position_id, "browser", "running") for position_id in sorted(position_ids[1:6])
    ]
    assert _stored_quality(database, position_ids[0]) == "tool"
    assert _stored_quality(database, position_ids[6]) == "browser"
