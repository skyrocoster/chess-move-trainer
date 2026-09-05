"""Run only the authorized four-analysis real Stockfish smoke proof."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from benchmark import (
    ArtifactStore,
    BenchmarkRunner,
    BenchmarkSpec,
    FULL_SEED,
    KeepAwake,
    Profile,
    StockfishSession,
    expected_manifest,
    load_install_metadata,
    load_positions,
    sha256_file,
    verify_engine_binary,
)


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = EXPERIMENT_DIR.parents[2]
INPUT_PATH = REPOSITORY_ROOT / "data" / "stockfish" / "test_positions.json"
INSTALL_PATH = REPOSITORY_ROOT / "data" / "stockfish" / "install.json"
ENGINE_PATH = REPOSITORY_ROOT / "data" / "stockfish" / "stockfish-windows-x86-64-avx2.exe"


class RecordingSession:
    """Record structured lifecycle facts without retaining UCI text."""

    def __init__(self, session: StockfishSession, events: list[dict[str, object]], profile: Profile):
        self.session = session
        self.events = events
        self.profile = profile
        self.identity = session.identity

    def configure(self, profile: Profile) -> None:
        self.events.append({"event": "configure", "profile": profile.as_dict()})
        self.session.configure(profile)

    def clear_hash(self) -> None:
        self.events.append({"event": "clear_hash", "profile": self.profile.as_dict()})
        self.session.clear_hash()

    def analyse(self, board, nodes: int, multipv: int):
        self.events.append(
            {
                "event": "analyse",
                "profile": self.profile.as_dict(),
                "nodes": nodes,
                "multipv": multipv,
            }
        )
        return self.session.analyse(board, nodes, multipv)

    def close(self) -> None:
        self.events.append({"event": "close", "profile": self.profile.as_dict()})
        self.session.close()


def main() -> int:
    positions = load_positions(INPUT_PATH)
    install = load_install_metadata(INSTALL_PATH)
    engine_sha256 = verify_engine_binary(ENGINE_PATH, install)
    smoke_positions = (positions[0],)
    spec = BenchmarkSpec(
        positions=smoke_positions,
        node_budgets=(100_000, 200_000),
        thread_values=(1, 2),
        hash_values_mb=(64,),
        rounds=(1,),
        seed=FULL_SEED + 1,
    )
    assert len(spec.ordered_jobs()) == 4

    run_name = datetime.now(UTC).strftime("run-%Y%m%dT%H%M%SZ")
    artifact_dir = EXPERIMENT_DIR / ".artifacts" / "smoke" / run_name
    manifest = expected_manifest(
        spec,
        INPUT_PATH,
        ENGINE_PATH,
        install,
        input_sha256=sha256_file(INPUT_PATH),
        engine_sha256=engine_sha256,
    )
    events: list[dict[str, object]] = []

    def engine_factory(profile: Profile) -> RecordingSession:
        events.append({"event": "start", "profile": profile.as_dict()})
        return RecordingSession(StockfishSession(ENGINE_PATH), events, profile)

    runner = BenchmarkRunner(
        spec,
        manifest,
        ArtifactStore(artifact_dir),
        engine_factory,
        KeepAwake,
        validate_engine_identity=True,
    )
    outcome = runner.run()
    if not outcome.complete or outcome.successful_jobs != 4 or outcome.total_jobs != 4:
        raise AssertionError(f"Smoke did not complete exactly four jobs: {outcome}")

    records = ArtifactStore(artifact_dir)
    records.manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
    attempts = records.attempts()
    successful = [record for record in attempts if record.get("status") == "success"]
    if len(attempts) != 4 or len(successful) != 4:
        raise AssertionError("Smoke checkpoint does not contain exactly four successful attempts")
    summary = json.loads((artifact_dir / "summary.json").read_text(encoding="utf-8"))
    if summary["counts"]["successful_jobs"] != 4:
        raise AssertionError("Smoke JSON summary count is incorrect")
    if not (artifact_dir / "summary.csv").is_file():
        raise AssertionError("Smoke CSV summary is missing")

    starts = [event for event in events if event["event"] == "start"]
    closes = [event for event in events if event["event"] == "close"]
    configures = [event for event in events if event["event"] == "configure"]
    analyses = [event for event in events if event["event"] == "analyse"]
    clears = [event for event in events if event["event"] == "clear_hash"]
    if len(starts) != 2 or len(closes) != 2 or len(configures) != 2:
        raise AssertionError("Smoke did not use two sequential configured engine processes")
    if len(analyses) != 6:
        raise AssertionError("Smoke expected two warm-ups plus four measured analyses")
    if len(clears) != 6:
        raise AssertionError("Smoke expected one post-warm-up and two measured hash clears per profile")
    measured = [event for event in analyses if event["multipv"] == 5]
    if len(measured) != 4 or {event["nodes"] for event in measured} != {100_000, 200_000}:
        raise AssertionError("Smoke measured-analysis shape is incorrect")
    if any(result["result"]["lines"] == [] for result in successful):
        raise AssertionError("Smoke contains an empty normalized candidate-line set")
    if artifact_dir.parent.name != "smoke" or artifact_dir.parent.parent.name != ".artifacts":
        raise AssertionError("Smoke artifact is not isolated under .artifacts/smoke")

    print(f"SMOKE PASS: {artifact_dir} (4 measured jobs, 4 successful checkpoints)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
