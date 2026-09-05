"""No-argument entry point for the future unattended full DB-07 benchmark."""

from __future__ import annotations

import sys
from pathlib import Path

from benchmark import (
    BenchmarkError,
    build_runner,
    expected_manifest,
    full_spec,
    load_install_metadata,
    load_positions,
    verify_engine_binary,
)


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = EXPERIMENT_DIR.parents[2]
INPUT_PATH = REPOSITORY_ROOT / "data" / "stockfish" / "test_positions.json"
INSTALL_PATH = REPOSITORY_ROOT / "data" / "stockfish" / "install.json"
ENGINE_PATH = REPOSITORY_ROOT / "data" / "stockfish" / "stockfish-windows-x86-64-avx2.exe"
DEFAULT_RUN_DIR = EXPERIMENT_DIR / ".artifacts" / "full-run"


def run_startup(
    *,
    artifact_dir: Path = DEFAULT_RUN_DIR,
    spec_factory=full_spec,
    engine_factory=None,
    validate_engine_identity: bool = True,
):
    positions = load_positions(INPUT_PATH)
    install = load_install_metadata(INSTALL_PATH)
    engine_sha256 = verify_engine_binary(ENGINE_PATH, install)
    spec = spec_factory(positions)
    manifest = expected_manifest(
        spec,
        INPUT_PATH,
        ENGINE_PATH,
        install,
        input_sha256=None,
        engine_sha256=engine_sha256,
    )
    runner = build_runner(
        spec,
        manifest,
        artifact_dir,
        ENGINE_PATH,
        engine_factory=engine_factory,
        validate_engine_identity=validate_engine_identity,
    )
    return runner.run()


def main() -> int:
    if len(sys.argv) != 1:
        print("start.py accepts no arguments or prompts", file=sys.stderr)
        return 2
    try:
        outcome = run_startup()
    except BenchmarkError as exc:
        print(f"BENCHMARK STOPPED: {exc}", file=sys.stderr)
        return 1
    print(
        f"BENCHMARK {'COMPLETE' if outcome.complete else 'INCOMPLETE'}: "
        f"{outcome.artifact_dir} ({outcome.successful_jobs}/{outcome.total_jobs} successful)"
    )
    return outcome.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
