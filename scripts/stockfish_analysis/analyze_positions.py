"""Explicit analysis-schema initialization and status reporting."""

from __future__ import annotations

import argparse
import signal
import sqlite3
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.features.analysis import (  # noqa: E402
    AnalysisProfile,
    AnalysisSchemaError,
    AnalysisValidationError,
    CorpusPreflight,
    InterruptController,
    initialize_analysis_schema,
    require_analysis_schema,
    run_all_positions,
    run_read_only_preflight,
    run_selected_games,
)
from backend.app.features.analysis.engine import ManagedStockfish, PythonChessProcess  # noqa: E402
from backend.app.features.analysis.provisioning import (  # noqa: E402
    DEFAULT_INSTALL_DIR,
    ProvisionedStockfish,
    verify_override,
)
from scripts.dev import clear_port  # noqa: E402

DEFAULT_DATABASE = Path(__file__).resolve().parents[2] / "data/database/chess_games.db"
BACKEND_PORT = 5666
QUALIFIED_PROFILE_ID = "mp09-balanced-nodes-v2-200000"
QUALIFIED_NODE_BUDGET = 200_000


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.0f}m {seconds % 60:.0f}s"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}h {minutes}m"


def initialize_database(path: Path) -> None:
    if not path.is_file():
        raise AnalysisSchemaError(f"database does not exist: {path}")
    connection = sqlite3.connect(path)
    try:
        initialize_analysis_schema(connection)
    finally:
        connection.close()


def report_schema(path: Path) -> int:
    if not path.is_file():
        raise AnalysisSchemaError(f"database does not exist: {path}")
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        return require_analysis_schema(connection)
    finally:
        connection.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage persisted backend analysis.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument(
        "--engine",
        type=Path,
        help="explicit verified Stockfish executable override",
    )
    parser.add_argument("--workers", type=int, default=1, help="analysis workers (1-6)")
    parser.add_argument("--watchdog", type=float, default=30.0)
    parser.add_argument("--shutdown-timeout", type=float, default=5.0)
    parser.add_argument("--profile-id", default=QUALIFIED_PROFILE_ID)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--init-schema", action="store_true")
    operation.add_argument("--report-schema", action="store_true")
    operation.add_argument(
        "--game",
        action="append",
        dest="game_uuids",
        metavar="UUID",
        help="analyze one accepted game; repeat for multiple games",
    )
    operation.add_argument(
        "--all",
        action="store_true",
        help="preflight or analyze every exact FEN in the accepted subject corpus",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="with --all, print the read-only corpus preflight and exit",
    )
    parser.add_argument(
        "--confirm-all",
        action="store_true",
        help="with --all, explicitly confirm full-corpus writes without prompting",
    )
    return parser


def _installed_override() -> Path:
    executables = sorted(
        path
        for path in DEFAULT_INSTALL_DIR.glob("*.exe")
        if path.is_file() and path.name.lower().startswith("stockfish")
    )
    if len(executables) != 1:
        raise AnalysisSchemaError(
            "no unique verified local Stockfish executable; pass --engine or run explicit setup"
        )
    return executables[0]


def _profile(args: argparse.Namespace) -> tuple[AnalysisProfile, ProvisionedStockfish]:
    if args.profile_id != QUALIFIED_PROFILE_ID:
        raise AnalysisValidationError(
            f"only the accepted profile {QUALIFIED_PROFILE_ID} may run analysis"
        )
    provisioned = verify_override((args.engine or _installed_override()).resolve(strict=True))
    profile = AnalysisProfile(
        profile_id=args.profile_id,
        engine_binary_sha256=provisioned.identity.binary_sha256,
        engine_name=provisioned.identity.reported_name,
        engine_version=provisioned.identity.version,
        node_budget=QUALIFIED_NODE_BUDGET,
        options={"UCI_ShowWDL": True},
    )
    return profile, provisioned


def _print_preflight(preflight: CorpusPreflight) -> None:
    report = preflight.report
    total = len(report.positions)
    to_process = len(report.positions_to_process)
    print("Corpus preflight (read-only, no changes made).")
    print(f"  database:           {preflight.database}")
    print(f"  total positions:    {total:,}")
    print(f"  already done:       {report.already_done:,} (skipped)")
    print(f"  need re-analysis:   {report.stale_positions:,} (settings changed)")
    print(f"  need analysis:      {report.missing_positions:,} (never analysed)")
    print(f"  to process:         {to_process:,}")
    print("  queue order:        ply ascending, FEN ascending")
    print(
        f"  engine:             {preflight.profile.engine_name} "
        f"(version {preflight.profile.engine_version})"
    )
    print(f"  profile:            {preflight.profile.profile_id}")
    print(f"  workers:            {preflight.workers}")
    print(f"  hash per worker:    {preflight.total_hash_memory_mib // preflight.workers} MiB")
    print(f"  projected duration: {_format_duration(preflight.projected_duration_seconds)}")
    if preflight.projected_pending_duration_seconds > 0:
        print(
            "  pending duration:   "
            f"{_format_duration(preflight.projected_pending_duration_seconds)}"
        )
    print(f"  projected disk:     {preflight.projected_disk_bytes / (1024 * 1024):.1f} MiB")
    if preflight.projected_pending_disk_bytes > 0:
        print(
            f"  pending disk:       "
            f"{preflight.projected_pending_disk_bytes / (1024 * 1024):.1f} MiB"
        )
    print(f"  watchdog:           {preflight.watchdog_seconds:g}s")


def _confirm_all() -> bool:
    try:
        response = input(
            "WARNING: this will analyze the full accepted corpus and write analysis results. "
            "Type 'ANALYZE ALL' to continue: "
        )
    except EOFError:
        print("Full-corpus operation refused: confirmation input ended at EOF.", file=sys.stderr)
        return False
    if response.strip() == "ANALYZE ALL":
        return True
    if response.strip().lower() in {"n", "no"}:
        print("Full-corpus operation refused.", file=sys.stderr)
    else:
        print("Full-corpus operation refused: invalid confirmation.", file=sys.stderr)
    return False


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.preflight_only and not args.all:
            raise ValueError("--preflight-only requires --all")
        if args.confirm_all and not args.all:
            raise ValueError("--confirm-all requires --all")
        if args.preflight_only and args.confirm_all:
            raise ValueError("--preflight-only cannot be combined with --confirm-all")
        if args.init_schema:
            initialize_database(args.db)
            print("Initialized analysis schema version 1.")
        elif args.report_schema:
            print(f"analysis_schema_version: {report_schema(args.db)}")
        else:
            profile, provisioned = _profile(args)
            if args.all:
                preflight = run_read_only_preflight(
                    args.db,
                    profile,
                    workers=args.workers,
                    watchdog_seconds=args.watchdog,
                )
                _print_preflight(preflight)
                if args.preflight_only:
                    return 0
                if not args.confirm_all and not _confirm_all():
                    return 1
                if args.confirm_all:
                    print("Noninteractive full-corpus confirmation accepted via --confirm-all.")

                print(f"Clearing backend port {BACKEND_PORT} to avoid database lock contention.")
                clear_port(BACKEND_PORT)

                start_time = time.monotonic()

                def progress(done: int, total: int) -> None:
                    elapsed = time.monotonic() - start_time
                    rate = done / elapsed if elapsed > 0 else 0
                    remaining = (total - done) / rate if rate > 0 else 0
                    print(
                        f"\rProgress: {done:,}/{total:,} "
                        f"({done * 100 // total}%) "
                        f"[{_format_duration(elapsed)} elapsed, "
                        f"~{_format_duration(remaining)} remaining]",
                        end="",
                        flush=True,
                    )

                controller = InterruptController()

                def handle_interrupt(_signum: int, _frame: object) -> None:
                    level = controller.request_interrupt()
                    print(
                        "Stopping dispatch and draining active analyses."
                        if level == 1
                        else "Forcing tracked engine shutdown.",
                        file=sys.stderr,
                        flush=True,
                    )

                previous = signal.getsignal(signal.SIGINT)
                signal.signal(signal.SIGINT, handle_interrupt)
                try:
                    result = run_all_positions(
                        args.db,
                        profile,
                        lambda: ManagedStockfish(
                            PythonChessProcess.launch(provisioned.executable),
                            profile,
                            watchdog_seconds=args.watchdog,
                            shutdown_seconds=args.shutdown_timeout,
                        ),
                        workers=args.workers,
                        controller=controller,
                        progress=progress,
                    )
                finally:
                    signal.signal(signal.SIGINT, previous)
                elapsed = time.monotonic() - start_time
                print()
                print("Run complete.")
                print(f"  run_id:         {result.run_id}")
                print(f"  status:         {result.status}")
                print(f"  positions:      {len(result.report.positions):,} total")
                print(f"    already done:   {result.report.already_done:,} (skipped)")
                print(f"    need re-analysis: {result.report.stale_positions:,}")
                print(f"    need analysis:  {result.report.missing_positions:,}")
                print(f"  completed:      {result.completed_positions:,}")
                print(f"  failed:         {len(result.failures)}")
                print(f"  duration:       {_format_duration(elapsed)}")
                return 0

            print(f"Clearing backend port {BACKEND_PORT} to avoid database lock contention.")
            clear_port(BACKEND_PORT)

            start_time = time.monotonic()

            def game_progress(done: int, total: int) -> None:
                elapsed = time.monotonic() - start_time
                rate = done / elapsed if elapsed > 0 else 0
                remaining = (total - done) / rate if rate > 0 else 0
                print(
                    f"\rProgress: {done:,}/{total:,} "
                    f"({done * 100 // total}%) "
                    f"[{_format_duration(elapsed)} elapsed, "
                    f"~{_format_duration(remaining)} remaining]",
                    end="",
                    flush=True,
                )

            controller = InterruptController()

            def handle_interrupt(_signum: int, _frame: object) -> None:
                level = controller.request_interrupt()
                print(
                    "Stopping dispatch and draining active analyses."
                    if level == 1
                    else "Forcing tracked engine shutdown.",
                    file=sys.stderr,
                    flush=True,
                )

            previous = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, handle_interrupt)
            try:
                result = run_selected_games(
                    args.db,
                    args.game_uuids or [],
                    profile,
                    lambda: ManagedStockfish(
                        PythonChessProcess.launch(provisioned.executable),
                        profile,
                        watchdog_seconds=args.watchdog,
                        shutdown_seconds=args.shutdown_timeout,
                    ),
                    workers=args.workers,
                    controller=controller,
                    progress=game_progress,
                )
            finally:
                signal.signal(signal.SIGINT, previous)
            elapsed = time.monotonic() - start_time
            print()
            print("Run complete.")
            print(f"  run_id:         {result.run_id}")
            print(f"  status:         {result.status}")
            print(f"  positions:      {len(result.report.positions):,} total")
            print(f"    already done:   {result.report.already_done:,} (skipped)")
            print(f"    need re-analysis: {result.report.stale_positions:,}")
            print(f"    need analysis:  {result.report.missing_positions:,}")
            print(f"  completed:      {result.completed_positions:,}")
            print(f"  failed:         {len(result.failures)}")
            print(f"  duration:       {_format_duration(elapsed)}")
        return 0
    except (OSError, RuntimeError, ValueError, sqlite3.Error) as error:
        print(f"Analysis operation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
