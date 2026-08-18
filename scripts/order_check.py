#!/usr/bin/env python
"""Run explicit work-order proof commands with compact failure output.

Examples:
    python scripts/order_check.py --command "unit checks=your-test-command"
    python scripts/order_check.py --cwd app --command "lint=your-lint-command" --docs
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_FAILURE_LINES = 25


def parse_command(value: str) -> tuple[str, str]:
    label, separator, command = value.partition("=")
    if not separator or not label.strip() or not command.strip():
        raise argparse.ArgumentTypeError("commands must use LABEL=COMMAND")
    return label.strip(), command.strip()


def run(label: str, command: str, cwd: Path) -> bool:
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        print(f"PASS  {label}")
        return True
    print(f"FAIL  {label} (exit {result.returncode})")
    output = (result.stdout + "\n" + result.stderr).strip().splitlines()
    for line in output[-MAX_FAILURE_LINES:]:
        print(f"  {line}")
    print(f"ADVICE  {label} did not pass; review the output above before proceeding")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=".", help="repo-relative working directory for commands")
    parser.add_argument(
        "--command", action="append", type=parse_command, default=[], metavar="LABEL=COMMAND"
    )
    parser.add_argument("--docs", action="store_true", help="also run the documentation contract")
    args = parser.parse_args()
    cwd = (REPO_ROOT / args.cwd).resolve()
    if not cwd.is_dir() or REPO_ROOT not in (cwd, *cwd.parents):
        parser.error("--cwd must be an existing directory inside the repository")
    commands = args.command
    if args.docs:
        commands.append(
            ("documentation contract", f'"{sys.executable}" scripts/check_docs.py --check')
        )
    if not commands:
        parser.error("supply --command LABEL=COMMAND and/or --docs")
    failed = False
    for label, command in commands:
        if not run(label, command, cwd):
            failed = True
    if failed:
        print("ADVICE  one or more checks did not pass; review before proceeding")
    else:
        print("ADVICE  all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
