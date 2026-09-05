from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import chess
import chess.engine
import pytest

import benchmark
import start


ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = ROOT / "data" / "stockfish" / "test_positions.json"
INSTALL_PATH = ROOT / "data" / "stockfish" / "install.json"
ENGINE_PATH = ROOT / "data" / "stockfish" / "stockfish-windows-x86-64-avx2.exe"


def make_spec() -> benchmark.BenchmarkSpec:
    positions = benchmark.load_positions(INPUT_PATH)
    return benchmark.BenchmarkSpec(
        positions=(positions[0],),
        node_budgets=(100_000, 200_000),
        thread_values=(1, 2),
        hash_values_mb=(64,),
        rounds=(1,),
        seed=77,
    )


class FakePower:
    enters = 0
    exits = 0

    def __enter__(self):
        type(self).enters += 1
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        type(self).exits += 1


class FakeSession:
    def __init__(self, profile: benchmark.Profile, fail_first_measured: bool = False):
        self.profile = profile
        self.identity = {"name": "Fake Stockfish 18"}
        self.fail_first_measured = fail_first_measured
        self.calls: list[tuple[str, int, int]] = []
        self.closed = False

    def configure(self, profile):
        self.calls.append(("configure", profile.threads, profile.hash_mb))

    def clear_hash(self):
        self.calls.append(("clear_hash", 0, 0))

    def analyse(self, board, nodes: int, multipv: int):
        self.calls.append(("analyse", nodes, multipv))
        if self.fail_first_measured and len([call for call in self.calls if call[0] == "analyse"]) == 2:
            raise RuntimeError("synthetic engine failure")
        move = next(iter(board.legal_moves))
        score = chess.engine.PovScore(chess.engine.Cp(21), board.turn)
        wdl = chess.engine.PovWdl(chess.engine.Wdl(1, 2, 3), board.turn)
        return [
            {
                "multipv": rank,
                "score": score,
                "wdl": wdl,
                "pv": [move],
                "nodes": nodes,
                "nps": 10_000,
                "depth": 12,
                "seldepth": 15,
                "hashfull": 11,
                "time": 0.25,
            }
            for rank in range(1, min(benchmark.MULTI_PV, board.legal_moves.count()) + 1)
        ]

    def close(self):
        self.closed = True


def make_manifest(spec: benchmark.BenchmarkSpec) -> dict:
    install = benchmark.load_install_metadata(INSTALL_PATH)
    return benchmark.expected_manifest(spec, INPUT_PATH, ENGINE_PATH, install)


def test_positions_and_full_matrix_are_valid_and_deterministic():
    positions = benchmark.load_positions(INPUT_PATH)
    assert len(positions) == 10
    assert all(
        chess.Board(position.fen).status()
        in (chess.STATUS_VALID, chess.STATUS_INVALID_EP_SQUARE)
        for position in positions
    )
    spec = benchmark.full_spec(positions)
    first = spec.ordered_jobs()
    second = spec.ordered_jobs()
    assert len(first) == 2_520
    assert len({job.job_id for job in first}) == 2_520
    assert first == second
    assert len(spec.profile_blocks()) == 12
    assert first[0].profile == spec.profile_blocks()[0]


def test_manifest_records_matrix_ordering_and_rejects_incompatible_state(tmp_path):
    spec = make_spec()
    manifest = make_manifest(spec)
    store = benchmark.ArtifactStore(tmp_path / "run")
    store.prepare(manifest)
    loaded = json.loads((tmp_path / "run" / "manifest.json").read_text(encoding="utf-8"))
    assert loaded["matrix"]["total_jobs"] == 4
    assert loaded["ordering"]["job_ids"] == [job.job_id for job in spec.ordered_jobs()]

    incompatible = dict(manifest)
    incompatible["matrix"] = dict(manifest["matrix"])
    incompatible["matrix"]["multipv"] = 4
    with pytest.raises(benchmark.ConfigurationError):
        benchmark.ArtifactStore(tmp_path / "run").prepare(incompatible)


def run_fake(
    artifact_dir: Path,
    spec: benchmark.BenchmarkSpec,
    factory,
    *,
    validate=False,
):
    return benchmark.build_runner(
        spec,
        make_manifest(spec),
        artifact_dir,
        ENGINE_PATH,
        engine_factory=factory,
        power_factory=FakePower,
        validate_engine_identity=validate,
    ).run()


def test_checkpoint_resume_failures_and_summaries_do_not_repeat_successes(tmp_path):
    spec = make_spec()
    first_sessions: list[FakeSession] = []

    def first_factory(profile):
        session = FakeSession(profile, fail_first_measured=profile.threads == 1)
        first_sessions.append(session)
        return session

    artifact_dir = tmp_path / "run"
    first = run_fake(artifact_dir, spec, first_factory)
    assert first.exit_code == 1
    assert first.failed_jobs == 1
    assert first.successful_jobs == 3
    assert all(session.closed for session in first_sessions)
    first_records = benchmark.ArtifactStore(artifact_dir)
    first_records.manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
    attempts_before = first_records.attempts()
    assert len(attempts_before) == 4
    assert len({record["job_id"] for record in attempts_before}) == 4

    second_sessions: list[FakeSession] = []

    def second_factory(profile):
        session = FakeSession(profile)
        second_sessions.append(session)
        return session

    second = run_fake(artifact_dir, spec, second_factory)
    assert second.complete
    assert second.successful_jobs == 4
    assert [session.profile.threads for session in second_sessions] == [1]
    measured_calls = [call for session in second_sessions for call in session.calls if call[0] == "analyse"]
    assert [call[1] for call in measured_calls].count(100_000) == 1
    assert [call[1] for call in measured_calls].count(200_000) == 1
    assert (artifact_dir / "summary.json").is_file()
    with (artifact_dir / "summary.csv").open(newline="", encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == 4

    final_records = benchmark.ArtifactStore(artifact_dir)
    final_records.manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
    attempts_after = final_records.attempts()
    retried = [record for record in attempts_after if record["job_id"] == attempts_before[0]["job_id"]]
    assert max(record["attempt"] for record in retried) == 2


def test_completed_run_is_a_noop_and_power_request_is_released(tmp_path):
    spec = make_spec()
    sessions: list[FakeSession] = []

    def factory(profile):
        session = FakeSession(profile)
        sessions.append(session)
        return session

    first = run_fake(tmp_path / "run", spec, factory)
    assert first.complete
    session_count = len(sessions)
    second = run_fake(tmp_path / "run", spec, lambda _profile: pytest.fail("completed run started again"))
    assert second.complete
    assert len(sessions) == session_count
    assert FakePower.enters >= 1
    assert FakePower.enters == FakePower.exits


def test_normalized_scores_wdl_and_pv_keep_explicit_perspectives():
    position = benchmark.load_positions(INPUT_PATH)[0]
    board = chess.Board(position.fen)
    move = next(iter(board.legal_moves))
    job = benchmark.Job(1, position.position_id, 100_000, 1, 64)
    infos = [
        {
            "multipv": rank,
            "score": chess.engine.PovScore(chess.engine.Mate(3), board.turn),
            "wdl": chess.engine.PovWdl(chess.engine.Wdl(5, 6, 7), board.turn),
            "pv": [move],
            "nodes": 100_000,
        }
        for rank in range(1, 6)
    ]
    result = benchmark.normalize_analysis(
        board,
        infos,
        job,
        1,
        0.125,
    )
    assert result["lines"][0]["score"] == {"kind": "mate", "value": 3, "perspective": "side_to_move"}
    assert result["lines"][0]["wdl"]["perspective"] == "side_to_move"
    assert result["lines"][0]["pv"] == [move.uci()]


def test_start_py_no_arguments_uses_isolated_state_without_real_full_run(tmp_path, monkeypatch):
    spec = make_spec()
    sessions: list[FakeSession] = []

    def factory(profile):
        session = FakeSession(profile)
        sessions.append(session)
        return session

    monkeypatch.setattr(start, "DEFAULT_RUN_DIR", tmp_path / "full-run")
    monkeypatch.setattr(start, "full_spec", lambda _positions: spec)
    monkeypatch.setattr(start, "run_startup", lambda: benchmark.build_runner(
        spec,
        make_manifest(spec),
        start.DEFAULT_RUN_DIR,
        ENGINE_PATH,
        engine_factory=factory,
        power_factory=FakePower,
        validate_engine_identity=False,
    ).run())
    monkeypatch.setattr(sys, "argv", ["start.py"])
    assert start.main() == 0
    assert len(sessions) == 2
    assert start.DEFAULT_RUN_DIR.is_dir()


def test_watchdog_is_bounded_and_aborts_operation():
    aborted = []

    with pytest.raises(benchmark.EngineWatchdogExpired):
        benchmark._call_with_watchdog(lambda: __import__("time").sleep(0.05), 0.001, lambda: aborted.append(True))
    assert aborted == [True]
