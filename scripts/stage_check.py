#!/usr/bin/env python
"""Run the documentation contract and explicitly supplied project-wide checks.

Examples:
    python scripts/stage_check.py
    python scripts/stage_check.py --command "tests=your-test-command" --command "lint=your-lint-command"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_FAILURE_LINES = 30


def parse_command(value: str) -> tuple[str, str]:
    label, separator, command = value.partition("=")
    if not separator or not label.strip() or not command.strip():
        raise argparse.ArgumentTypeError("commands must use LABEL=COMMAND")
    return label.strip(), command.strip()


def run(label: str, command: str) -> bool:
    result = subprocess.run(command, cwd=REPO_ROOT, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode == 0:
        print(f"PASS  {label}")
        return True
    print(f"FAIL  {label} (exit {result.returncode})")
    for line in (result.stdout + "\n" + result.stderr).strip().splitlines()[-MAX_FAILURE_LINES:]:
        print(f"  {line}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", action="append", type=parse_command, default=[], metavar="LABEL=COMMAND")
    parser.add_argument("--skip-docs", action="store_true", help="do not run scripts/check_docs.py --check")
    args = parser.parse_args()
    commands = [] if args.skip_docs else [("documentation contract", f'"{sys.executable}" scripts/check_docs.py --check')]
    commands.extend(args.command)
    if not commands:
        parser.error("supply a project check or omit --skip-docs")
    failed = any(not run(label, command) for label, command in commands)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
