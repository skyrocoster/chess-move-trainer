"""Run all local quality checks without PowerShell.

Two phases:
1. AUTOFIX - apply safe automatic fixes and formatters (Ruff --fix, Ruff format,
   ESLint --fix, Prettier --write, docs generation). These always run first, so
   the verify phase - including both test suites - executes against fixed code.
2. VERIFY - run every lint/format check, the test suites, the build, the size
   gate, and the end-to-end tests.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class Step:
    name: str
    command: list[str]
    cwd: str | None = None


AUTOFIX: list[Step] = [
    Step(
        "Documentation generation", [sys.executable, "scripts/check_docs.py", "--write-generated"]
    ),
    Step("Ruff lint fix", [sys.executable, "-m", "ruff", "check", "--fix", "."]),
    Step("Ruff format", [sys.executable, "-m", "ruff", "format", "."]),
    Step("ESLint fix", ["npm.cmd", "run", "lint", "--prefix", "frontend", "--", "--fix"]),
    Step("Prettier format", ["npm.cmd", "run", "format", "--prefix", "frontend"]),
]

VERIFY: list[Step] = [
    Step("Documentation check", [sys.executable, "scripts/check_docs.py", "--check"]),
    Step("Ruff lint check", [sys.executable, "-m", "ruff", "check", "."]),
    Step("Ruff format check", [sys.executable, "-m", "ruff", "format", "--check", "."]),
    Step("Python tests", [sys.executable, "-m", "pytest"]),
    Step("Frontend tests", ["npm.cmd", "run", "test", "--prefix", "frontend", "--", "--run"]),
    Step("ESLint check", ["npm.cmd", "run", "lint", "--prefix", "frontend"]),
    Step("Prettier check", [r"frontend\node_modules\.bin\prettier.cmd", "--check", "frontend"]),
    Step("Frontend build", ["npm.cmd", "run", "build", "--prefix", "frontend"]),
    Step(
        "Source size check",
        [sys.executable, "scripts/check_size.py", "--source-max", "500", "--test-max", "700"],
    ),
    Step(
        "End-to-end tests",
        [
            r"node_modules\.bin\playwright.cmd",
            "test",
            "--config",
            r"tests\e2e\playwright.config.ts",
        ],
    ),
]


def run_step(step: Step, show_success: bool) -> bool:
    try:
        result = subprocess.run(
            step.command,
            cwd=step.cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        print(f"--- {step.name} failed (missing executable) ---", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return False

    if result.returncode == 0:
        if show_success:
            print(f"Passed: {step.name}")
        return True

    print(f"--- {step.name} failed ---", file=sys.stderr)
    out = result.stdout.strip()
    err = result.stderr.strip()
    if out:
        print(out, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    return False


def main(argv: Iterable[str] | None = None) -> int:
    failed = False

    print("== Autofix phase (formatters and safe fixes run before tests) ==", flush=True)
    for step in AUTOFIX:
        if not run_step(step, show_success=False):
            failed = True

    print("== Verify phase ==", flush=True)
    for step in VERIFY:
        if not run_step(step, show_success=True):
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
