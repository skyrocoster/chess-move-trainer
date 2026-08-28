"""Storybook interaction and accessibility validation."""

from __future__ import annotations

import subprocess
import sys

from scripts.checks.steps import REPO_ROOT

STORYBOOK_TEST_TIMEOUT_SECONDS = 300


def run_storybook_validation(timeout: int = STORYBOOK_TEST_TIMEOUT_SECONDS) -> bool:
    command = [
        "npm.cmd",
        "run",
        "test-storybook",
        "--prefix",
        "frontend",
        "--",
        "--run",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        print("--- Storybook validation failed (missing executable) ---", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print(
            f"--- Storybook validation failed (timed out after {timeout}s) ---",
            file=sys.stderr,
        )
        return False

    if result.returncode == 0:
        return True

    print("--- Storybook interaction and accessibility tests failed ---", file=sys.stderr)
    output = result.stdout.strip()
    error = result.stderr.strip()
    if output:
        print(output, file=sys.stderr)
    if error:
        print(error, file=sys.stderr)
    return False
