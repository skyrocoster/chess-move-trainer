"""Import-safe explicit fixture-freeze and benchmark execution command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.features.analysis.benchmark import (  # noqa: E402
    canonical_write,
    execute_benchmark,
    freeze_from_v1_report,
    freeze_report,
    validate_same_fixtures,
)
from backend.app.features.analysis.benchmark_fixtures import (  # noqa: E402
    select_benchmark_fixtures,
)
from backend.app.features.analysis.errors import AnalysisValidationError  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = ROOT / "data/database/chess_games.db"
DEFAULT_REPORT = ROOT / "docs/benchmarks/mp09-stockfish-18-node-budget-v2.json"
DEFAULT_SOURCE_REPORT = ROOT / "docs/benchmarks/mp09-stockfish-18-node-budget-v1.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the MP-09 Stockfish profile benchmark (requires Stage 2 authorization)."
    )
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument(
        "--freeze-fixtures",
        action="store_true",
        help="select and persist fixtures read-only before any engine observation",
    )
    operation.add_argument("--run", action="store_true", help="run the frozen benchmark")
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--source-report", type=Path, default=DEFAULT_SOURCE_REPORT)
    parser.add_argument("--executable", type=Path, help="verified Stockfish 18 executable")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.freeze_fixtures:
            fixtures, exact_fen_count = select_benchmark_fixtures(args.db)
            canonical_write(args.report, freeze_report(fixtures, exact_fen_count))
            print(f"Frozen {len(fixtures)} fixtures before engine observation.")
            print(f"eligible_exact_fen_count: {exact_fen_count}")
            return 0
        if args.executable is None:
            raise AnalysisValidationError("--run requires --executable")
        frozen = freeze_from_v1_report(args.source_report)
        fixtures, exact_fen_count = select_benchmark_fixtures(args.db)
        validate_same_fixtures(frozen, fixtures, exact_fen_count)
        report = execute_benchmark(args.executable.resolve(strict=True), frozen)
        canonical_write(args.report, report)
        selected = report["qualification"]["selected_node_budget"]
        print(f"benchmark_status: {report['status']}")
        print(f"selected_node_budget: {selected}")
        return 0 if selected is not None else 2
    except (AnalysisValidationError, OSError, RuntimeError) as error:
        print(f"Stockfish benchmark failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
