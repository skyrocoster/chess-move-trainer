from __future__ import annotations

import queue
import subprocess
import threading
from pathlib import Path
from typing import Any

import chess
import pytest

from chess_move_trainer.database.analysis import (
    AnalysisQuality,
    AnalysisScoreKind,
    AnalysisTerminalKind,
)
from chess_move_trainer.database.positions import canonicalize_fen
from chess_move_trainer.database.stockfish import (
    ANALYSIS_WATCHDOG_SECONDS,
    BROWSER_NODES,
    BROWSER_PROFILE,
    CONFIGURATION_VERSION,
    HASH_MB,
    MULTI_PV,
    STOCKFISH_VERSION,
    THREADS,
    TOOL_NODES,
    TOOL_PROFILE,
    StockfishEngine,
    StockfishIdentityError,
    StockfishWatchdogError,
    normalize_score,
    normalize_wdl,
    parse_uci_info,
)


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
CHECKMATE_FEN = "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1"


class _FakeStdout:
    def __init__(self) -> None:
        self._lines: queue.Queue[str | None] = queue.Queue()
        self.closed = False

    def put(self, line: str) -> None:
        self._lines.put(line + "\n")

    def end(self) -> None:
        self._lines.put(None)

    def readline(self) -> str:
        value = self._lines.get()
        return "" if value is None else value

    def close(self) -> None:
        self.closed = True


class _FakeStdin:
    def __init__(self, commands: queue.Queue[str], history: list[str]) -> None:
        self._commands = commands
        self._history = history
        self.closed = False

    def write(self, command: str) -> int:
        normalized = command.rstrip("\n")
        self._history.append(normalized)
        self._commands.put(normalized)
        return len(command)

    def flush(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True


class _FakeProcess:
    def __init__(self, *, wrong_identity: bool = False, hang: bool = False) -> None:
        self.stdout = _FakeStdout()
        self.stdin_commands: queue.Queue[str] = queue.Queue()
        self.commands: list[str] = []
        self.stdin = _FakeStdin(self.stdin_commands, self.commands)
        self.stderr = None
        self._stopped = threading.Event()
        self._returncode: int | None = None
        self._wrong_identity = wrong_identity
        self._hang = hang
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

    def _run(self) -> None:
        while not self._stopped.is_set():
            try:
                command = self.stdin_commands.get(timeout=0.02)
            except queue.Empty:
                continue
            if command == "uci":
                name = "Not Stockfish 18" if self._wrong_identity else "Stockfish 18"
                self.stdout.put(f"id name {name}")
                self.stdout.put("uciok")
            elif command == "isready":
                self.stdout.put("readyok")
            elif command.startswith("go nodes ") and not self._hang:
                self._send_analysis()

    def _send_analysis(self) -> None:
        roots = (
            "e2e4",
            "d2d4",
            "g1f3",
            "c2c4",
            "b1c3",
        )
        replies = ("e7e5", "d7d5", "g8f6", "e7e5", "b8c6")
        for rank, (root, reply) in enumerate(zip(roots, replies), start=1):
            self.stdout.put(
                f"info depth {10 + rank} multipv {rank} score cp {rank * 10} "
                f"wdl 600 300 100 pv {root} {reply}"
            )
        self.stdout.put("bestmove e2e4")

    def poll(self) -> int | None:
        return self._returncode

    def terminate(self) -> None:
        self._returncode = -15
        self._stopped.set()
        self.stdout.end()

    def kill(self) -> None:
        self._returncode = -9
        self._stopped.set()
        self.stdout.end()

    def wait(self, timeout: float | None = None) -> int:
        if not self._stopped.wait(timeout):
            raise subprocess.TimeoutExpired("fake-stockfish", timeout)
        return self._returncode or 0


class _FakeFactory:
    def __init__(self, *, wrong_identity: bool = False, hangs: int = 0) -> None:
        self.processes: list[_FakeProcess] = []
        self._wrong_identity = wrong_identity
        self._hangs = hangs

    def __call__(self, _executable: str, **_: Any) -> _FakeProcess:
        process = _FakeProcess(
            wrong_identity=self._wrong_identity,
            hang=len(self.processes) < self._hangs,
        )
        self.processes.append(process)
        return process


def test_fixed_profiles_and_identity_contract_are_explicit() -> None:
    assert BROWSER_PROFILE.quality is AnalysisQuality.BROWSER
    assert BROWSER_PROFILE.nodes == BROWSER_NODES == 200_000
    assert TOOL_PROFILE.quality is AnalysisQuality.TOOL
    assert TOOL_PROFILE.nodes == TOOL_NODES == 6_400_000
    for profile in (BROWSER_PROFILE, TOOL_PROFILE):
        assert profile.threads == THREADS == 6
        assert profile.hash_mb == HASH_MB == 1024
        assert profile.multipv == MULTI_PV == 5
        assert profile.configuration_version == CONFIGURATION_VERSION == 1
    assert STOCKFISH_VERSION == "18"
    assert "Nodes" in TOOL_PROFILE.settings


def test_score_and_wdl_are_normalized_from_side_to_move_to_white_pov() -> None:
    assert normalize_score(AnalysisScoreKind.CP, 35, chess.WHITE) == (
        AnalysisScoreKind.CP,
        35,
    )
    assert normalize_score("mate", 3, chess.BLACK) == (AnalysisScoreKind.MATE, -3)
    assert normalize_wdl(700, 200, 100, chess.BLACK) == (100, 200, 700)

    parsed = parse_uci_info(
        "info depth 20 multipv 2 score cp 35 wdl 700 200 100 pv e2e4 e7e5",
        chess.BLACK,
    )
    assert parsed is not None
    assert parsed.score_value == -35
    assert (parsed.wdl_wins, parsed.wdl_draws, parsed.wdl_losses) == (100, 200, 700)
    assert parsed.pv_uci == ("e2e4", "e7e5")


def test_engine_applies_fixed_options_clears_hash_and_returns_complete_pvs() -> None:
    factory = _FakeFactory()
    engine = StockfishEngine(
        "fake-stockfish",
        startup_timeout=1,
        popen_factory=factory,
    )
    try:
        first = engine.analyze(canonicalize_fen(STARTING_FEN), TOOL_PROFILE)
        second = engine.analyze(canonicalize_fen(STARTING_FEN), BROWSER_PROFILE)
    finally:
        engine.close()

    assert first.result.engine_name == "Stockfish"
    assert first.result.engine_version == STOCKFISH_VERSION
    assert first.profile is TOOL_PROFILE
    assert len(first.lines) == 5
    assert first.lines[0].pv_uci == ("e2e4", "e7e5")
    assert second.profile is BROWSER_PROFILE
    commands = factory.processes[0].commands
    assert commands.count("setoption name Clear Hash") == 2
    assert "setoption name Threads value 6" in commands
    assert "setoption name Hash value 1024" in commands
    assert "setoption name MultiPV value 5" in commands
    assert "go nodes 6400000" in commands
    assert "go nodes 200000" in commands
    assert all("movetime" not in command for command in commands)


def test_terminal_position_returns_no_lines_without_a_search() -> None:
    factory = _FakeFactory()
    engine = StockfishEngine("fake-stockfish", startup_timeout=1, popen_factory=factory)
    try:
        analysis = engine.analyze(canonicalize_fen(CHECKMATE_FEN), TOOL_PROFILE)
    finally:
        engine.close()

    assert analysis.terminal_kind is AnalysisTerminalKind.CHECKMATE
    assert analysis.lines == ()
    commands = factory.processes[0].commands
    assert not any(command.startswith("go ") for command in commands)


def test_identity_failure_terminates_the_child() -> None:
    factory = _FakeFactory(wrong_identity=True)
    engine = StockfishEngine("fake-stockfish", startup_timeout=1, popen_factory=factory)

    with pytest.raises(StockfishIdentityError):
        engine.start()

    assert not engine.is_running
    assert factory.processes[0].poll() is not None


def test_watchdog_terminates_failed_process_before_replacement() -> None:
    factory = _FakeFactory(hangs=1)
    engine = StockfishEngine(
        "fake-stockfish",
        startup_timeout=1,
        watchdog_seconds=0.05,
        popen_factory=factory,
    )
    position = canonicalize_fen(STARTING_FEN)

    with pytest.raises(StockfishWatchdogError):
        engine.analyze(position, TOOL_PROFILE)
    assert not engine.is_running
    assert factory.processes[0].poll() is not None

    analysis = engine.analyze(position, TOOL_PROFILE)
    assert len(analysis.lines) == 5
    assert len(factory.processes) == 2
    engine.close()


def test_watchdog_default_is_the_approved_thirty_seconds() -> None:
    engine = StockfishEngine("fake-stockfish", popen_factory=_FakeFactory())
    assert engine.watchdog_seconds == ANALYSIS_WATCHDOG_SECONDS == 30
