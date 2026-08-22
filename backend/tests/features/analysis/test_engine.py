from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Mapping

import chess
import chess.engine
import pytest

from backend.app.features.analysis import (
    AnalysisTimeoutError,
    AnalysisValidationError,
    EngineLifecycleError,
)
from backend.app.features.analysis.engine import (
    EngineIdentity,
    ManagedStockfish,
    PythonChessProcess,
)


class FakeProcess:
    def __init__(self, checksum: str, version: str, *, mode: str = "normal") -> None:
        self.identity = EngineIdentity("Stockfish 18 fake", version, checksum)
        self.pid = 4242
        self.mode = mode
        self.events: list[tuple[str, object]] = []
        self.exited = threading.Event()
        self.release_analysis = threading.Event()
        self.analysis_calls = 0
        self.malformed_field: str | None = None

    def configure(self, options: Mapping[str, object]) -> None:
        self.events.append(("configure", dict(options)))

    def analyse(self, board: chess.Board, limit: chess.engine.Limit, **kwargs: object) -> object:
        self.analysis_calls += 1
        self.events.append(
            (
                "analyse",
                {
                    "nodes": limit.nodes,
                    "multipv": kwargs.get("multipv"),
                    "game": kwargs.get("game"),
                },
            )
        )
        if self.mode == "hang":
            self.release_analysis.wait(5)
        entries = []
        for index, move in enumerate(list(board.legal_moves)[:5]):
            score: chess.engine.Score = chess.engine.Cp(30 - index)
            if index == 0 and self.mode == "mate_given":
                score = chess.engine.MateGiven
            elif index == 1 and self.mode == "mate_given":
                score = chess.engine.Mate(0)
            entry = {
                "score": chess.engine.PovScore(score, chess.WHITE),
                "wdl": chess.engine.PovWdl(chess.engine.Wdl(300, 500, 200), chess.WHITE),
                "pv": [move],
                "depth": 12,
                "seldepth": 16,
                "nodes": 50_000,
                "time": 0.025,
            }
            if self.malformed_field:
                entry.pop(self.malformed_field)
            entries.append(entry)
        return entries

    def quit(self) -> None:
        self.events.append(("quit", None))
        if self.mode != "stubborn_quit":
            self.exited.set()

    def terminate(self) -> None:
        self.events.append(("terminate", self.pid))
        self.exited.set()
        self.release_analysis.set()

    def wait_exited(self, timeout: float) -> bool:
        return self.exited.wait(timeout)


def managed(profile, *, mode: str = "normal", watchdog: float = 1.0):
    process = FakeProcess(profile.engine_binary_sha256, profile.engine_version, mode=mode)
    return ManagedStockfish(
        process, profile, watchdog_seconds=watchdog, shutdown_seconds=0.2
    ), process


def test_managed_engine_configures_multipv_only_on_analysis_and_isolates_order(profile) -> None:
    adapter, process = managed(profile)
    fen = chess.STARTING_FEN

    first = adapter.analyse(fen)
    second = adapter.analyse(fen)
    adapter.close()

    assert process.events[0] == (
        "configure",
        {"Threads": 1, "Hash": 128, "UCI_ShowWDL": True},
    )
    configure_values = [event[1] for event in process.events if event[0] == "configure"]
    assert all("MultiPV" not in value for value in configure_values)
    analyses = [event[1] for event in process.events if event[0] == "analyse"]
    assert [item["multipv"] for item in analyses] == [5, 5]
    assert analyses[0]["game"] is not analyses[1]["game"]
    assert [event[0] for event in process.events[:5]] == [
        "configure",
        "configure",
        "analyse",
        "configure",
        "analyse",
    ]
    assert first.candidates[0].score_kind == "cp"
    assert first.candidates[0].wdl_wins == 300
    assert first.candidates[0].pv_uci
    assert second.candidates[0].engine_time_ms == 25


def test_engine_serializes_mate_given_separately_from_mate_zero(profile) -> None:
    adapter, _process = managed(profile, mode="mate_given")

    result = adapter.analyse(chess.STARTING_FEN)
    adapter.close()

    assert (result.candidates[0].score_kind, result.candidates[0].score_value) == (
        "mate_given",
        0,
    )
    assert (result.candidates[1].score_kind, result.candidates[1].score_value) == ("mate", 0)


def test_terminal_and_fewer_root_move_positions_are_complete(profile) -> None:
    adapter, process = managed(profile)
    terminal = adapter.analyse("7k/5Q2/7K/8/8/8/8/8 b - - 0 1")
    fewer = adapter.analyse("8/8/8/8/8/2q5/2k5/K7 w - - 0 1")
    adapter.close()

    assert terminal.terminal_kind == "stalemate"
    assert terminal.candidates == ()
    assert len(fewer.candidates) == 1
    assert process.analysis_calls == 1


@pytest.mark.parametrize("field", ["wdl", "score", "pv", "depth", "seldepth", "nodes", "time"])
def test_required_engine_proof_fields_are_refused(profile, field: str) -> None:
    adapter, process = managed(profile)
    process.malformed_field = field

    with pytest.raises(AnalysisValidationError):
        adapter.analyse(chess.STARTING_FEN)
    adapter.close()


def test_hard_watchdog_terminates_only_tracked_engine_and_proves_pid_exit(profile) -> None:
    adapter, process = managed(profile, mode="hang", watchdog=0.03)

    with pytest.raises(AnalysisTimeoutError, match="4242"):
        adapter.analyse(chess.STARTING_FEN)

    assert process.exited.is_set()
    assert ("terminate", 4242) in process.events
    adapter.close()  # Idempotent after forced timeout cleanup.


def test_normal_quit_and_bounded_force_close_leave_no_child(profile) -> None:
    normal, normal_process = managed(profile)
    normal.close()
    normal.close()
    assert normal_process.exited.is_set()
    assert not any(event[0] == "terminate" for event in normal_process.events)

    forced, forced_process = managed(profile, mode="stubborn_quit")
    forced.close()
    assert forced_process.exited.is_set()
    assert ("terminate", 4242) in forced_process.events


def test_process_checksum_identity_is_required(profile) -> None:
    process = FakeProcess("f" * 64, profile.engine_version)
    with pytest.raises(AnalysisValidationError, match="checksum"):
        ManagedStockfish(process, profile)


def test_engine_instance_refuses_concurrent_worker_sharing(profile) -> None:
    adapter, process = managed(profile, mode="hang", watchdog=1)
    first_error: list[BaseException] = []

    def first_call() -> None:
        try:
            adapter.analyse(chess.STARTING_FEN)
        except BaseException as error:
            first_error.append(error)

    thread = threading.Thread(target=first_call)
    thread.start()
    while process.analysis_calls == 0:
        threading.Event().wait(0.005)
    with pytest.raises(EngineLifecycleError, match="shared"):
        adapter.analyse(chess.STARTING_FEN)
    process.release_analysis.set()
    thread.join(1)
    adapter.close()
    assert first_error == []


class _EventLoopTransportStub:
    """Minimal asyncio.SubprocessTransport-shaped stub with a mutable return code."""

    def __init__(self) -> None:
        self._returncode: int | None = None

    def get_pid(self) -> int:
        return 7777

    def get_returncode(self) -> int | None:
        return self._returncode


class _StrictAsyncioEvent(asyncio.Event):
    """Real asyncio event that fails loudly if lifecycle code ever awaits it."""

    def wait(self, *args: object, **kwargs: object) -> object:
        raise AssertionError("lifecycle code must not await asyncio.Event.wait()")


class _SimpleEngineStub:
    """SimpleEngine-shaped stub whose shutdown flag is a real asyncio.Event."""

    def __init__(self) -> None:
        self.shutdown_event = _StrictAsyncioEvent()
        self.transport = _EventLoopTransportStub()

    def mark_shut_down_and_exited(self) -> None:
        self.shutdown_event.set()
        self.transport._returncode = 0


def _real_python_chess_process() -> tuple[PythonChessProcess, _SimpleEngineStub]:
    engine = _SimpleEngineStub()
    process = PythonChessProcess(engine, EngineIdentity("Stockfish 18 fake", "18", "0" * 64))
    return process, engine


def test_wait_exited_requires_both_asyncio_shutdown_flag_and_child_return_code() -> None:
    process, engine = _real_python_chess_process()

    assert process.wait_exited(0) is False  # shutdown flag unset
    engine.shutdown_event.set()
    assert process.wait_exited(0) is False  # shutdown flag set but no return code yet
    engine.transport._returncode = 0
    assert process.wait_exited(0) is True  # both conditions hold -> immediate proof


def test_wait_exited_transitions_to_exited_within_the_bounded_deadline() -> None:
    process, engine = _real_python_chess_process()
    results: list[bool] = []

    def poll() -> None:
        results.append(process.wait_exited(1.0))

    started = time.monotonic()
    thread = threading.Thread(target=poll)
    thread.start()
    time.sleep(0.05)
    engine.mark_shut_down_and_exited()
    thread.join(1)

    assert results == [True]
    assert time.monotonic() - started < 0.5


def test_wait_exited_times_out_within_the_bounded_deadline() -> None:
    process, _engine = _real_python_chess_process()

    started = time.monotonic()
    assert process.wait_exited(0.05) is False
    elapsed = time.monotonic() - started
    assert 0.049 <= elapsed < 0.5
