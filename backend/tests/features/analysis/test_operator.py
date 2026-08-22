from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

import chess
import pytest

from backend.app.features.analysis import (
    AnalysisBusyError,
    AnalysisCandidate,
    AnalysisLockError,
    AnalysisProfile,
    AnalysisRepository,
    AnalysisResult,
    AnalysisRunLock,
    InterruptController,
    initialize_analysis_schema,
    run_selected_games,
    select_positions,
)
from backend.app.features.analysis.selection import GameSelectionError

SUBJECT = "0101b08a-ce8b-11ee-b2fd-e90263e5548c"
GAME_ONE = "00000000-0000-0000-0000-000000000001"
GAME_TWO = "00000000-0000-0000-0000-000000000002"
START_FEN = chess.STARTING_FEN


def _profile(*, checksum: str = "a" * 64, node_budget: int = 200_000) -> AnalysisProfile:
    return AnalysisProfile(
        profile_id="mp09-balanced-nodes-v2-200000",
        engine_binary_sha256=checksum,
        engine_name="Stockfish 18 fake",
        engine_version="18-test",
        node_budget=node_budget,
        options={"UCI_ShowWDL": True},
    )


def _database(path: Path, game_uuids: tuple[str, ...] = (GAME_ONE,)) -> None:
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(
        """
        CREATE TABLE players (uuid TEXT PRIMARY KEY);
        CREATE TABLE games (uuid TEXT PRIMARY KEY);
        CREATE TABLE corpus (
            corpus_id INTEGER PRIMARY KEY, subject_player_uuid TEXT NOT NULL
        );
        CREATE TABLE corpus_game (corpus_id INTEGER NOT NULL, game_uuid TEXT NOT NULL);
        CREATE TABLE position_state (
            state_id INTEGER PRIMARY KEY,
            placement TEXT, side_to_move TEXT, castling TEXT, en_passant TEXT,
            UNIQUE (placement, side_to_move, castling, en_passant)
        );
        CREATE TABLE position_occurrence (
            occurrence_id INTEGER PRIMARY KEY, game_uuid TEXT, ply INTEGER,
            state_id INTEGER, halfmove_clock INTEGER, fullmove_number INTEGER
        );
        """
    )
    db.execute("INSERT INTO players VALUES (?)", (SUBJECT,))
    db.execute("INSERT INTO corpus VALUES (1, ?)", (SUBJECT,))
    state_ids: dict[tuple[str, str, str, str], int] = {}
    occurrence_id = 1
    state_id = 1
    for game_index, game_uuid in enumerate(game_uuids):
        db.execute("INSERT INTO games VALUES (?)", (game_uuid,))
        db.execute("INSERT INTO corpus_game VALUES (1, ?)", (game_uuid,))
        board = chess.Board()
        moves = ("e2e4", "e7e5", "g1f3", "b8c6")[0 : game_index + 2]
        for ply, uci in enumerate((None, *moves)):
            if uci:
                board.push_uci(uci)
            fields = board.fen(en_passant="fen").split()
            key = tuple(fields[:4])
            if key not in state_ids:
                state_ids[key] = state_id
                db.execute(
                    "INSERT INTO position_state VALUES (?, ?, ?, ?, ?)",
                    (state_id, *key),
                )
                state_id += 1
            db.execute(
                "INSERT INTO position_occurrence VALUES (?, ?, ?, ?, ?, ?)",
                (occurrence_id, game_uuid, ply, state_ids[key], int(fields[4]), int(fields[5])),
            )
            occurrence_id += 1
    db.commit()
    initialize_analysis_schema(db)
    db.close()


def _result(profile: AnalysisProfile, fen: str) -> AnalysisResult:
    board = chess.Board(fen)
    candidates = tuple(
        AnalysisCandidate(
            rank=rank,
            score_kind="cp",
            score_value=rank,
            wdl_wins=300,
            wdl_draws=500,
            wdl_losses=200,
            pv_uci=(move.uci(),),
            depth=12,
            seldepth=16,
            nodes=profile.node_budget,
            engine_time_ms=2,
        )
        for rank, move in enumerate(list(board.legal_moves)[:5], 1)
    )
    return AnalysisResult(
        fen=fen,
        profile=profile,
        candidates=candidates,
        terminal_kind=None,
        completed_at="2026-08-20T12:00:00+00:00",
        wall_time_ms=2,
    )


class FakeEngine:
    def __init__(
        self,
        profile: AnalysisProfile,
        *,
        fail: bool = False,
        started: threading.Event | None = None,
        release: threading.Event | None = None,
    ) -> None:
        self.profile = profile
        self.fail = fail
        self.started = started
        self.release = release
        self.closed = False
        self.forced = False

    def analyse(self, fen: str) -> AnalysisResult:
        if self.started:
            self.started.set()
        if self.release and not self.release.wait(2):
            raise TimeoutError("fake engine wait expired")
        if self.fail:
            raise RuntimeError("fake engine failure")
        return _result(self.profile, fen)

    def close(self) -> None:
        self.closed = True
        if self.release:
            self.release.set()

    def force_terminate(self) -> None:
        self.forced = True
        self.closed = True
        if self.release:
            self.release.set()


def test_selection_includes_ply_zero_and_deduplicates_exact_fens(tmp_path: Path) -> None:
    database = tmp_path / "selected.db"
    _database(database, (GAME_ONE, GAME_TWO))
    connection = sqlite3.connect(database)
    try:
        report = select_positions(connection, [GAME_TWO, GAME_ONE], _profile())
    finally:
        connection.close()

    assert report.game_uuids == (GAME_ONE, GAME_TWO)
    assert len(report.positions) == 4
    assert report.positions[0].first_occurrence.ply == 0
    assert report.positions[0].fen == START_FEN
    assert report.missing_positions == 4
    assert len(report.positions[0].occurrences) == 2


def test_selection_rejects_unaccepted_game_without_mutation(tmp_path: Path) -> None:
    database = tmp_path / "selected.db"
    _database(database)
    connection = sqlite3.connect(database)
    try:
        with pytest.raises(GameSelectionError, match="accepted"):
            select_positions(connection, ["00000000-0000-0000-0000-000000000099"], _profile())
    finally:
        connection.close()


def test_eligibility_stale_reuse_and_idempotent_resume(tmp_path: Path) -> None:
    database = tmp_path / "resume.db"
    _database(database)
    profile = _profile()
    engines: list[FakeEngine] = []

    def factory() -> FakeEngine:
        engine = FakeEngine(profile)
        engines.append(engine)
        return engine

    first = run_selected_games(database, [GAME_ONE], profile, factory)
    second = run_selected_games(database, [GAME_ONE], profile, factory)

    assert first.status == "success"
    assert first.completed_positions == 3
    assert second.status == "success"
    assert second.completed_positions == 0
    assert second.report.eligible_positions == 3
    assert second.report.skipped_positions == 3
    assert len(engines) == 1

    stale_profile = _profile(checksum="b" * 64)
    connection = sqlite3.connect(database)
    try:
        report = select_positions(connection, [GAME_ONE], stale_profile)
    finally:
        connection.close()
    assert report.stale_positions == 3
    assert report.missing_positions == 0


def test_retry_once_fresh_engine_and_circuit_breaker_records_failures(tmp_path: Path) -> None:
    database = tmp_path / "failure.db"
    _database(database, (GAME_TWO,))
    profile = _profile()
    created = 0

    def factory() -> FakeEngine:
        nonlocal created
        created += 1
        return FakeEngine(profile, fail=True)

    result = run_selected_games(database, [GAME_TWO], profile, factory, workers=2)

    assert result.status == "failed"
    assert result.circuit_breaker_tripped is True
    assert len(result.failures) == 3
    assert all(failure.attempts == 2 for failure in result.failures)
    assert created >= 6

    connection = sqlite3.connect(database)
    try:
        assert connection.execute("SELECT COUNT(*) FROM analysis_result").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM analysis_position_failure").fetchone() == (
            3,
        )
    finally:
        connection.close()


def test_first_interrupt_drains_active_and_second_forces_tracked_engine(tmp_path: Path) -> None:
    database = tmp_path / "interrupt.db"
    _database(database, (GAME_ONE, GAME_TWO))
    profile = _profile()
    started = threading.Event()
    release = threading.Event()
    created: list[FakeEngine] = []
    controller = InterruptController()

    def factory() -> FakeEngine:
        engine = FakeEngine(profile, started=started, release=release)
        created.append(engine)
        return engine

    first_result: list[object] = []

    def run() -> None:
        first_result.append(
            run_selected_games(database, [GAME_ONE], profile, factory, controller=controller)
        )

    thread = threading.Thread(target=run)
    thread.start()
    assert started.wait(1)
    assert controller.request_interrupt() == 1
    release.set()
    thread.join(2)
    assert not thread.is_alive()
    assert first_result[0].status == "interrupted"
    assert first_result[0].completed_positions == 1

    # A second signal during another active run uses forced cleanup, not a new dispatch.
    started.clear()
    release.clear()
    controller = InterruptController()
    second_result: list[object] = []

    def run_second() -> None:
        second_result.append(
            run_selected_games(database, [GAME_TWO], profile, factory, controller=controller)
        )

    thread = threading.Thread(target=run_second)
    thread.start()
    assert started.wait(1)
    assert controller.request_interrupt() == 1
    assert controller.request_interrupt() == 2
    release.set()
    thread.join(2)
    assert not thread.is_alive()
    assert second_result[0].status == "interrupted"
    assert any(engine.forced for engine in created)


def test_lock_refuses_concurrent_operator_and_is_released_on_close(tmp_path: Path) -> None:
    database = tmp_path / "lock.db"
    database.touch()
    first = AnalysisRunLock(database)
    second = AnalysisRunLock(database)
    first.acquire()
    try:
        with pytest.raises(AnalysisLockError, match="another"):
            second.acquire()
    finally:
        first.release()
    second.acquire()
    second.release()


def test_worker_ceiling_is_refused_before_engine_dispatch(tmp_path: Path) -> None:
    database = tmp_path / "workers.db"
    _database(database)
    profile = _profile()

    with pytest.raises(ValueError, match="between 1 and 6"):
        run_selected_games(database, [GAME_ONE], profile, lambda: FakeEngine(profile), workers=7)


def test_repository_reports_sqlite_busy_without_replacing_old_result(
    tmp_path: Path, profile
) -> None:
    database = tmp_path / "busy.db"
    first = sqlite3.connect(database)
    initialize_analysis_schema(first)
    repository = AnalysisRepository(first)
    result = _result(profile, START_FEN)
    repository.publish(result)
    second = sqlite3.connect(database, timeout=0)
    first.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(AnalysisBusyError, match="SQLite"):
            AnalysisRepository(second).publish(result)
        assert second.execute("SELECT COUNT(*) FROM analysis_result").fetchone() == (1,)
    finally:
        first.rollback()
        second.close()
        first.close()
