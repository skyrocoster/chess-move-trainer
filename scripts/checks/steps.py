"""Step definitions, runner utilities, and shared constants for the check suite."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCHEMA_FIX_COMMAND = r".venv\Scripts\python.exe scripts\check.py --fix"
STORYBOOK_WINDOWS_TEARDOWN_RETURN_CODE = 0xC0000409
STORYBOOK_WINDOWS_TEARDOWN_ASSERTION = (
    "Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), "
    r"file c:\ws\deps\uv\src\win\async.c, line 76"
)


@dataclass
class Step:
    name: str
    command: list[str]
    cwd: str | None = None
    tag: str = ""


_NPM = lambda *a: ["npm.cmd", *a]  # noqa: E731
_PRETTIER = [r"frontend\node_modules\.bin\prettier.cmd"]
_PW = [r"node_modules\.bin\playwright.cmd"]
_RUFF = [sys.executable, "-m", "ruff"]

FIX_STEPS: list[Step] = [
    Step("Ruff lint fix", [sys.executable, "-m", "ruff", "check", "--fix", "."]),
    Step("Ruff format", [sys.executable, "-m", "ruff", "format", "."]),
    Step("ESLint fix", ["npm.cmd", "run", "lint", "--prefix", "frontend", "--", "--fix"]),
    Step("Prettier format", ["npm.cmd", "run", "format", "--prefix", "frontend"]),
]

VERIFY: list[Step] = [
    Step("Ruff lint check", _RUFF + ["check", "."], tag="lint"),
    Step("Ruff format check", _RUFF + ["format", "--check", "."], tag="lint"),
    Step("Python tests", [sys.executable, "-m", "pytest"], tag="python"),
    Step("Workflow tests", [sys.executable, "-m", "pytest", "scripts/tests"], tag="python"),
    Step(
        "Frontend tests", _NPM("run", "test", "--prefix", "frontend", "--", "--run"), tag="frontend"
    ),
    Step("ESLint check", _NPM("run", "lint", "--prefix", "frontend"), tag="lint"),
    Step("Prettier check", _PRETTIER + ["--check", "frontend"], tag="lint"),
    Step("Frontend build", _NPM("run", "build", "--prefix", "frontend"), tag="build"),
    Step("Storybook build", _NPM("run", "build-storybook", "--prefix", "frontend"), tag="build"),
    Step(
        "Source size check",
        [sys.executable, "scripts/check_size.py", "--source-max", "500", "--test-max", "700"],
        tag="lint",
    ),
    Step(
        "End-to-end tests", _PW + ["test", "--config", r"tests\e2e\playwright.config.ts"], tag="e2e"
    ),
]

ALL_TAGS = {"lint", "python", "frontend", "e2e", "build", "storybook"}


def run_step(step: Step, show_success: bool) -> bool:
    try:
        result = subprocess.run(
            step.command,
            cwd=step.cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        print(f"--- {step.name} failed (missing executable) ---", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return False
    if result.returncode == 0:
        if show_success:
            print(f"Passed: {step.name}")
        return True
    is_documented_storybook_teardown = (
        os.name == "nt"
        and step.name == "Storybook build"
        and result.returncode == STORYBOOK_WINDOWS_TEARDOWN_RETURN_CODE
        and "Storybook build completed successfully" in result.stdout
        and result.stderr.strip() == STORYBOOK_WINDOWS_TEARDOWN_ASSERTION
    )
    if is_documented_storybook_teardown:
        if show_success:
            print(f"Passed: {step.name} (ignored documented Windows libuv teardown assertion)")
        return True
    print(f"--- {step.name} failed ---", file=sys.stderr)
    out = result.stdout.strip()
    err = result.stderr.strip()
    if out:
        print(out, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    return False


def stop_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False,
            capture_output=True,
            text=True,
        )
    else:
        process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)
