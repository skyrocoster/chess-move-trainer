"""Finite offline commands; no service or worker lifecycle side effects."""

import argparse
import json
import os
from pathlib import Path

from .protocol import DEFAULT_PROTOCOL

# Avoid BLAS oversubscription alongside the shared Stockfish workers.
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(key, "1")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--source", type=Path, required=True)
    snapshot.add_argument("--output", type=Path, required=True)
    snapshot.add_argument("--source-label")
    snapshot.add_argument("--seconds", type=float, required=True)
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--run", type=Path, required=True)
    freeze.add_argument(
        "--catalogue",
        type=Path,
        default=Path("docs/grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md"),
    )
    pilot = sub.add_parser("pilot", help="create a non-confirmatory stratified game sample")
    pilot.add_argument("--source-run", type=Path, required=True)
    pilot.add_argument("--output", type=Path, required=True)
    pilot.add_argument("--max-games", type=int, default=1000)
    pilot.add_argument("--seed", type=int, default=DEFAULT_PROTOCOL.seed)
    pilot.add_argument("--seconds", type=float, required=True)
    pilot_snapshot = sub.add_parser(
        "pilot-snapshot", help="sample games before full replay from a frozen snapshot"
    )
    pilot_snapshot.add_argument("--source-run", type=Path, required=True)
    pilot_snapshot.add_argument("--output", type=Path, required=True)
    pilot_snapshot.add_argument("--max-games", type=int, default=1000)
    pilot_snapshot.add_argument("--seed", type=int, default=DEFAULT_PROTOCOL.seed)
    pilot_snapshot.add_argument("--seconds", type=float, required=True)
    prepare = sub.add_parser(
        "prepare-full", help="prepare a fresh full run without copying prior results"
    )
    prepare.add_argument("--source-run", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--seconds", type=float, required=True)
    for name in ("extract", "audit", "fit"):
        command = sub.add_parser(name)
        command.add_argument("--run", type=Path, required=True)
        command.add_argument("--seconds", type=float, required=True)
        if name == "extract":
            command.add_argument("--max-games", type=int)
        if name == "fit":
            command.add_argument("--question", action="append")
            command.add_argument("--fit-seconds", type=float, default=30)
            command.add_argument("--replicates", type=int, default=2000)
            command.add_argument("--diagnostic", action="store_true")
    review = sub.add_parser("report")
    review.add_argument("--run", type=Path, required=True)
    simulation = sub.add_parser("calibrate")
    simulation.add_argument("--output", type=Path, required=True)
    simulation.add_argument("--scenario", default="null")
    simulation.add_argument("--repetitions", type=int, default=1000)
    simulation.add_argument("--seconds", type=float, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            from .snapshot import create_snapshot

            result = create_snapshot(
                args.source, args.output, seconds=args.seconds, source_label=args.source_label
            )
        elif args.command == "freeze":
            from .registry import freeze_registry

            result = freeze_registry(args.catalogue, args.run / "registry.json")
            result = {
                "identity": result["identity"],
                "questions": result["family_size"],
                "catalogue_items": len(result["catalogue"]),
            }
        elif args.command == "pilot":
            from .pilot import create_pilot

            result = create_pilot(
                args.source_run,
                args.output,
                max_games=args.max_games,
                seed=args.seed,
                seconds=args.seconds,
            )
            result = {
                "status": result["status"],
                "identity": result["identity"],
                "sampled_games": result["sampled_games"],
                "source_total_games": result["source_total_games"],
                "sampled_moves": result["sampled_moves"],
                "output": str(args.output),
            }
        elif args.command == "pilot-snapshot":
            from .snapshot_pilot import create_snapshot_pilot

            result = create_snapshot_pilot(
                args.source_run,
                args.output,
                max_games=args.max_games,
                seed=args.seed,
                seconds=args.seconds,
            )
            result = {
                "status": result["status"],
                "identity": result["identity"],
                "sampled_games": result["sampled_games"],
                "source_total_games": result["source_total_games"],
                "sampled_plies": result["sampled_plies"],
                "source_raw_rank1_pair_coverage": result["source_raw_rank1_pair_coverage"],
                "output": str(args.output),
            }
        elif args.command == "prepare-full":
            from .full_run import prepare_full_run

            result = prepare_full_run(args.source_run, args.output, seconds=args.seconds)
            result = {
                "status": result["status"],
                "snapshot_sha256": result["snapshot_sha256"],
                "registry_identity": result["registry_identity"],
                "source_total_games": result["source_total_games"],
                "output": str(args.output),
            }
        elif args.command == "extract":
            from .extraction import extract

            if args.max_games is not None and args.max_games < 1:
                raise ValueError("max-games must be positive")
            result = extract(args.run, seconds=args.seconds, max_games=args.max_games)
        elif args.command == "audit":
            from .audit import build_audit

            value = build_audit(args.run, seconds=args.seconds)
            result = {
                k: value[k]
                for k in (
                    "status",
                    "total_games",
                    "excluded_games",
                    "populations",
                    "measurement_limits",
                )
            }
            if "pilot" in value:
                result["pilot"] = value["pilot"]
        elif args.command == "fit":
            from .runner import run_questions

            result = run_questions(
                args.run,
                seconds=args.seconds,
                fit_seconds=args.fit_seconds,
                identifiers=args.question,
                replicates=args.replicates,
                diagnostic=args.diagnostic,
            )
            result = {"status": result["status"], "completed_questions": len(result["results"])}
        elif args.command == "calibrate":
            from .calibration import calibrate

            result = calibrate(
                args.output,
                scenario=args.scenario,
                repetitions=args.repetitions,
                seconds=args.seconds,
            )
        else:
            from .reporting import report

            result = {"report": str(report(args.run))}
    except (ValueError, RuntimeError, TimeoutError, OSError) as error:
        parser.exit(2, f"{type(error).__name__}: {error}\n")
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
