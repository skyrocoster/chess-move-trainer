#!/usr/bin/env python3
"""Interactive menu for stockfish analysis operations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data/database/chess_games.db"
DEFAULT_ENGINE = (
    Path(__file__).resolve().parents[2] / "data/stockfish/stockfish-windows-x86-64-avx2.exe"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_SCRIPT = Path(__file__).resolve().with_name("analyze_positions.py")
QUALIFIED_PROFILE = "mp09-balanced-nodes-v2-200000"
RUNNING_NOTICE_SECONDS = 30


def run_cmd(cmd: list[str]) -> int:
    print(f"\n> {' '.join(cmd)}\n", flush=True)
    process = subprocess.Popen(cmd, cwd=REPOSITORY_ROOT)
    while True:
        try:
            return process.wait(timeout=RUNNING_NOTICE_SECONDS)
        except subprocess.TimeoutExpired:
            print(
                "Analysis is still running; waiting for the next progress update...",
                flush=True,
            )


def menu() -> None:
    while True:
        print("\n" + "=" * 60)
        print("  STOCKFISH ANALYSIS MENU")
        print("=" * 60)
        print("  1. Initialize schema")
        print("  2. Report schema version")
        print("  3. Preflight (read-only corpus scan)")
        print("  4. Analyze specific game(s) by UUID")
        print("  5. Full corpus analysis (auto-confirm, ask workers)")
        print("  6. Full corpus analysis (non-interactive, defaults)")
        print("  7. Custom run")
        print("  0. Exit")
        print("-" * 60)

        choice = input("Select option [0-7]: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        elif choice == "1":
            run_cmd(
                [
                    sys.executable,
                    "-u",
                    str(ANALYSIS_SCRIPT),
                    "--db",
                    str(DEFAULT_DB),
                    "--init-schema",
                ]
            )

        elif choice == "2":
            run_cmd(
                [
                    sys.executable,
                    "-u",
                    str(ANALYSIS_SCRIPT),
                    "--db",
                    str(DEFAULT_DB),
                    "--report-schema",
                ]
            )

        elif choice == "3":
            run_cmd(
                [
                    sys.executable,
                    "-u",
                    str(ANALYSIS_SCRIPT),
                    "--db",
                    str(DEFAULT_DB),
                    "--engine",
                    str(DEFAULT_ENGINE),
                    "--profile-id",
                    QUALIFIED_PROFILE,
                    "--all",
                    "--preflight-only",
                ]
            )

        elif choice == "4":
            uuids = input("Enter game UUID(s) separated by space: ").strip().split()
            if not uuids:
                print("No UUIDs provided.")
                continue
            cmd = [
                sys.executable,
                "-u",
                str(ANALYSIS_SCRIPT),
                "--db",
                str(DEFAULT_DB),
                "--engine",
                str(DEFAULT_ENGINE),
                "--profile-id",
                QUALIFIED_PROFILE,
            ]
            for uuid in uuids:
                cmd.extend(["--game", uuid])
            run_cmd(cmd)

        elif choice == "5":
            workers = input("Workers [5]: ").strip() or "5"
            run_cmd(
                [
                    sys.executable,
                    "-u",
                    str(ANALYSIS_SCRIPT),
                    "--db",
                    str(DEFAULT_DB),
                    "--engine",
                    str(DEFAULT_ENGINE),
                    "--profile-id",
                    QUALIFIED_PROFILE,
                    "--all",
                    "--confirm-all",
                    "--workers",
                    workers,
                ]
            )

        elif choice == "6":
            workers = input("Workers [5]: ").strip() or "5"
            run_cmd(
                [
                    sys.executable,
                    "-u",
                    str(ANALYSIS_SCRIPT),
                    "--db",
                    str(DEFAULT_DB),
                    "--engine",
                    str(DEFAULT_ENGINE),
                    "--profile-id",
                    QUALIFIED_PROFILE,
                    "--all",
                    "--confirm-all",
                    "--workers",
                    workers,
                ]
            )

        elif choice == "7":
            print("\nCustom run - enter arguments (or press Enter for defaults):")
            db = input(f"DB path [{DEFAULT_DB}]: ").strip() or str(DEFAULT_DB)
            engine = input(f"Engine path [{DEFAULT_ENGINE}]: ").strip() or str(DEFAULT_ENGINE)
            profile = input(f"Profile ID [{QUALIFIED_PROFILE}]: ").strip() or QUALIFIED_PROFILE
            workers = input("Workers [5]: ").strip() or "5"
            watchdog = input("Watchdog seconds [30]: ").strip() or "30"
            shutdown = input("Shutdown timeout [5]: ").strip() or "5"

            print("\nOperation:")
            print("  a) --game UUID (repeatable)")
            print("  b) --all")
            print("  c) --all --preflight-only")
            op = input("Choose [a/b/c]: ").strip().lower()

            cmd = [
                sys.executable,
                "-u",
                str(ANALYSIS_SCRIPT),
                "--db",
                db,
                "--engine",
                engine,
                "--profile-id",
                profile,
                "--workers",
                workers,
                "--watchdog",
                watchdog,
                "--shutdown-timeout",
                shutdown,
            ]

            if op == "a":
                uuids = input("Game UUID(s): ").strip().split()
                for uuid in uuids:
                    cmd.extend(["--game", uuid])
            elif op == "b":
                cmd.append("--all")
                confirm = input("Auto-confirm? [y/N]: ").strip().lower()
                if confirm == "y":
                    cmd.append("--confirm-all")
            elif op == "c":
                cmd.extend(["--all", "--preflight-only"])
            else:
                print("Invalid operation.")
                continue

            run_cmd(cmd)

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive menu for stockfish analysis")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Database path")
    parser.add_argument("--engine", type=Path, default=DEFAULT_ENGINE, help="Stockfish executable")
    args = parser.parse_args()

    DEFAULT_DB = args.db
    DEFAULT_ENGINE = args.engine

    menu()
