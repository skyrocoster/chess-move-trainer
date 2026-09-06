from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from chess_move_trainer.database.analysis import (
    AnalysisLine,
    AnalysisResultInput,
    AnalysisScoreKind,
)
from chess_move_trainer.database.stockfish import (
    AtomicArtifactWriter,
    BenchmarkCompatibilityError,
    BenchmarkPersistenceError,
    BenchmarkPosition,
    BenchmarkRunner,
    BenchmarkSpec,
    DEFAULT_HASH_SIZES_MB,
    DEFAULT_NODE_BUDGETS,
    DEFAULT_THREAD_COUNTS,
    SearchMetrics,
    StockfishAnalysis,
    run_benchmark,
)


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"


def _write_input(path: Path, count: int = 2) -> Path:
    fens = (STARTING_FEN, AFTER_E4_FEN)
    path.write_text(
        json.dumps(
            {
                "positions": [
                    {"id": index, "fen": fens[(index - 1) % len(fens)]}
                    for index in range(1, count + 1)
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def _small_spec(input_path: Path) -> BenchmarkSpec:
    from chess_move_trainer.database.stockfish import load_positions

    return BenchmarkSpec(
        positions=load_positions(input_path),
        node_budgets=(100, 200),
        thread_counts=(1,),
        hash_sizes_mb=(64,),
        repetitions=1,
        shuffle_seed=17,
    )


def _fake_analysis(profile: Any) -> StockfishAnalysis:
    lines = tuple(
        AnalysisLine(
            rank=rank,
            score_kind=AnalysisScoreKind.CP,
            score_value=rank * 5,
            wdl_wins=600,
            wdl_draws=300,
            wdl_losses=100,
            pv_uci=(root, reply),
            depth=12,
        )
        for rank, (root, reply) in enumerate(
            (
                ("e2e4", "e7e5"),
                ("d2d4", "d7d5"),
                ("g1f3", "g8f6"),
                ("c2c4", "e7e5"),
                ("b1c3", "b8c6"),
            ),
            start=1,
        )
    )
    result = AnalysisResultInput(
        quality=profile.quality,
        configuration_version=profile.configuration_version,
        settings=profile.settings,
        engine_name="Stockfish",
        engine_version="18",
        lines=lines,
    )
    return StockfishAnalysis(
        profile=profile,
        result=result,
        terminal_kind=None,
        metrics=SearchMetrics(nodes=profile.nodes, nps=1000, depth=12, seldepth=18, hashfull=4, time_ms=3),
    )


@dataclass
class _FakeEngine:
    fail_first_measured: bool = False
    interrupt_first_measured: bool = False

    def __post_init__(self) -> None:
        self.calls: list[Any] = []
        self.started = False
        self.closed = False

    def start(self) -> None:
        self.started = True

    def analyze(self, _position: Any, profile: Any) -> StockfishAnalysis:
        self.calls.append(profile)
        is_measured = len(self.calls) > 1
        if is_measured and self.fail_first_measured and len(self.calls) == 2:
            raise RuntimeError("fake engine failure")
        if is_measured and self.interrupt_first_measured and len(self.calls) == 2:
            raise KeyboardInterrupt
        return _fake_analysis(profile)

    def close(self) -> None:
        self.closed = True


class _FakeFactory:
    def __init__(self, **engine_options: Any) -> None:
        self.engine_options = engine_options
        self.instances: list[_FakeEngine] = []

    def __call__(self, _executable: Path, **_: Any) -> _FakeEngine:
        engine = _FakeEngine(**self.engine_options)
        self.instances.append(engine)
        return engine


class _InjectedWriter:
    def __init__(self, *, transient_appends: int = 0, permanent_after: int | None = None) -> None:
        self.delegate = AtomicArtifactWriter()
        self.transient_appends = transient_appends
        self.permanent_after = permanent_after
        self.append_calls = 0
        self.paths: list[Path] = []

    def write_json(self, path: Path, payload: dict[str, Any]) -> None:
        self.paths.append(path)
        self.delegate.write_json(path, payload)

    def write_text(self, path: Path, content: str) -> None:
        self.paths.append(path)
        self.delegate.write_text(path, content)

    def append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        self.paths.append(path)
        self.append_calls += 1
        if self.append_calls <= self.transient_appends:
            raise PermissionError("temporary sharing violation")
        if self.permanent_after is not None and self.append_calls > self.permanent_after:
            raise OSError("permanent artifact failure")
        self.delegate.append_jsonl(path, payload)


def _runner(
    input_path: Path,
    output_dir: Path,
    factory: _FakeFactory,
    *,
    writer: _InjectedWriter | None = None,
    retries: int = 3,
) -> BenchmarkRunner:
    return BenchmarkRunner(
        _small_spec(input_path),
        executable=Path("fake-stockfish.exe"),
        position_input=input_path,
        output_dir=output_dir,
        engine_factory=factory,
        artifact_writer=writer,
        artifact_write_retries=retries,
        progress=lambda _: None,
    )


def test_default_matrix_is_exact_and_deterministically_shuffled(tmp_path: Path) -> None:
    input_path = _write_input(tmp_path / "positions.json", count=10)
    from chess_move_trainer.database.stockfish import load_positions

    spec = BenchmarkSpec(
        positions=load_positions(input_path),
        shuffle_seed=1234,
    )
    jobs = spec.jobs()
    assert spec.total_jobs == 2520
    assert len(jobs) == 2520
    assert len({job.job_id for job in jobs}) == 2520
    assert jobs == spec.jobs()
    block_size = len(spec.positions) * len(spec.node_budgets) * spec.repetitions
    assert len({(job.threads, job.hash_mb) for job in jobs[:block_size]}) == 1
    assert set(spec.node_budgets) == set(DEFAULT_NODE_BUDGETS)
    assert set(spec.thread_counts) == set(DEFAULT_THREAD_COUNTS)
    assert set(spec.hash_sizes_mb) == set(DEFAULT_HASH_SIZES_MB)


def test_run_writes_normalized_contained_artifacts_and_completed_run_is_noop(
    tmp_path: Path,
) -> None:
    input_path = _write_input(tmp_path / "positions.json")
    output_dir = tmp_path / "artifacts"
    first_factory = _FakeFactory()
    first = _runner(input_path, output_dir, first_factory).run()

    assert first.complete
    assert first.successful_jobs == 4
    assert first.attempts == 4
    expected_files = {"manifest.json", "attempts.jsonl", "checkpoint.json", "summary.json", "summary.csv", "status.txt"}
    assert {path.name for path in output_dir.iterdir()} == expected_files
    attempt_records = [json.loads(line) for line in (output_dir / "attempts.jsonl").read_text().splitlines()]
    assert len(attempt_records) == 4
    assert all(record["record_type"] == "benchmark_attempt" for record in attempt_records)
    assert all(record["metrics"]["engine_nodes"] in (100, 200) for record in attempt_records)
    assert all(record["lines"][0]["score_perspective"] == "white" for record in attempt_records)
    with (output_dir / "summary.csv").open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) == 4

    second_factory = _FakeFactory()
    second = _runner(input_path, output_dir, second_factory).run()
    assert second.complete
    assert second.resumed
    assert second_factory.instances == []
    assert len((output_dir / "attempts.jsonl").read_text().splitlines()) == 4


def test_incompatible_manifest_stops_without_mixing_state(tmp_path: Path) -> None:
    input_path = _write_input(tmp_path / "positions.json", count=1)
    output_dir = tmp_path / "artifacts"
    _runner(input_path, output_dir, _FakeFactory()).run()
    from chess_move_trainer.database.stockfish import load_positions

    incompatible = BenchmarkRunner(
        BenchmarkSpec(positions=load_positions(input_path), node_budgets=(300,), thread_counts=(1,), hash_sizes_mb=(64,), repetitions=1),
        executable=Path("fake-stockfish.exe"),
        position_input=input_path,
        output_dir=output_dir,
        engine_factory=_FakeFactory(),
        progress=lambda _: None,
    )
    with pytest.raises(BenchmarkCompatibilityError):
        incompatible.run()


def test_failures_continue_and_next_invocation_retries_only_failed_jobs(tmp_path: Path) -> None:
    input_path = _write_input(tmp_path / "positions.json", count=1)
    output_dir = tmp_path / "artifacts"
    first_factory = _FakeFactory(fail_first_measured=True)
    first = _runner(input_path, output_dir, first_factory).run()
    assert not first.complete
    assert first.successful_jobs == 1
    assert first.failed_jobs == 1
    assert first.exit_code == 1

    second_factory = _FakeFactory()
    second = _runner(input_path, output_dir, second_factory).run()
    assert second.complete
    assert second.failed_jobs == 0
    assert second.attempts == 3
    assert len(second_factory.instances) == 1
    records = [json.loads(line) for line in (output_dir / "attempts.jsonl").read_text().splitlines()]
    assert len(records) == 3
    assert sum(record["status"] == "failure" for record in records) == 1


def test_transient_artifact_permission_is_retried_but_only_for_current_write(tmp_path: Path) -> None:
    input_path = _write_input(tmp_path / "positions.json", count=1)
    output_dir = tmp_path / "artifacts"
    writer = _InjectedWriter(transient_appends=2)
    outcome = _runner(input_path, output_dir, _FakeFactory(), writer=writer, retries=2).run()

    assert outcome.complete
    assert writer.append_calls == 4
    assert len((output_dir / "attempts.jsonl").read_text().splitlines()) == 2
    assert all(path.resolve().is_relative_to(output_dir.resolve()) for path in writer.paths)


def test_permanent_artifact_failure_stops_without_engine_failure_classification(
    tmp_path: Path,
) -> None:
    input_path = _write_input(tmp_path / "positions.json", count=2)
    output_dir = tmp_path / "artifacts"
    writer = _InjectedWriter(permanent_after=1)

    with pytest.raises(BenchmarkPersistenceError) as error:
        _runner(input_path, output_dir, _FakeFactory(), writer=writer, retries=0).run()
    assert error.value.exit_code == 1
    records = [json.loads(line) for line in (output_dir / "attempts.jsonl").read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["status"] == "success"
    assert not list(output_dir.glob("*.log"))
    assert all(path.resolve().is_relative_to(output_dir.resolve()) for path in writer.paths)


def test_interrupt_leaves_readable_checkpoint_without_partial_current_result(tmp_path: Path) -> None:
    input_path = _write_input(tmp_path / "positions.json", count=1)
    output_dir = tmp_path / "artifacts"
    outcome = _runner(
        input_path,
        output_dir,
        _FakeFactory(interrupt_first_measured=True),
    ).run()

    assert outcome.interrupted
    assert outcome.exit_code == 130
    assert (output_dir / "attempts.jsonl").read_text(encoding="utf-8") == ""
    checkpoint = json.loads((output_dir / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["interrupted"] is True
    assert checkpoint["attempt_count"] == 0


def test_run_benchmark_accepts_explicit_matrix_inputs(tmp_path: Path) -> None:
    input_path = _write_input(tmp_path / "positions.json", count=1)
    outcome = run_benchmark(
        executable="fake-stockfish.exe",
        position_input=input_path,
        output_dir=tmp_path / "artifacts",
        node_budgets=(100,),
        thread_counts=(1,),
        hash_sizes_mb=(64,),
        repetitions=1,
        shuffle_seed=1,
        engine_factory=_FakeFactory(),
        progress=lambda _: None,
    )
    assert outcome.complete
    assert outcome.total_jobs == 1
