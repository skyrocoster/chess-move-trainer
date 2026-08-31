"""Step definitions, runner utilities, and shared constants for the check suite."""

from __future__ import annotations

import os
import subprocess
import sys
import time
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
FAILURE_LOG_PATH = REPO_ROOT / "artifacts" / "check-failure.log"
EXCERPT_LINES = 20
DEFAULT_TIMEOUT_SECONDS = 300.0


@dataclass
class Step:
    name: str
    command: list[str]
    cwd: str | None = None
    tag: str = ""
    timeout: float | None = None


_NPM = lambda *a: ["npm.cmd", *a]  # noqa: E731
_PRETTIER = [r"node_modules\.bin\prettier.cmd"]
_PW = [r"node_modules\.bin\playwright.cmd"]
_RUFF = [sys.executable, "-m", "ruff"]
_TSC = [r"node_modules\.bin\tsc.cmd"]

FIX_STEPS: list[Step] = [
    Step("Ruff lint fix", [sys.executable, "-m", "ruff", "check", "--fix", "."], timeout=120),
    Step("Ruff format", [sys.executable, "-m", "ruff", "format", "."], timeout=120),
    Step(
        "ESLint fix", ["npm.cmd", "run", "lint", "--prefix", "frontend", "--", "--fix"], timeout=120
    ),
    Step("Prettier format", ["npm.cmd", "run", "format", "--prefix", "frontend"], timeout=120),
]

VERIFY: list[Step] = [
    Step("Ruff lint check", _RUFF + ["check", "."], tag="lint", timeout=120),
    Step("Ruff format check", _RUFF + ["format", "--check", "."], tag="lint", timeout=120),
    Step("Python tests", [sys.executable, "-m", "pytest"], tag="python", timeout=600),
    Step(
        "Workflow tests",
        [sys.executable, "-m", "pytest", "scripts/tests"],
        tag="python",
        timeout=180,
    ),
    Step(
        "Frontend tests",
        _NPM("run", "test", "--prefix", "frontend", "--", "--run", "--project=unit"),
        tag="frontend",
        timeout=600,
    ),
    Step("ESLint check", _NPM("run", "lint", "--prefix", "frontend"), tag="lint", timeout=300),
    Step("Prettier check", _PRETTIER + ["--check", "frontend"], tag="lint", timeout=180),
    Step("TypeScript type check", _TSC + ["-b", "frontend"], tag="lint", timeout=300),
    Step("Frontend build", _NPM("run", "build", "--prefix", "frontend"), tag="build", timeout=900),
    Step(
        "Storybook build",
        _NPM("run", "build-storybook", "--prefix", "frontend"),
        tag="build",
        timeout=900,
    ),
    Step(
        "Source size check",
        [sys.executable, "scripts/check_size.py", "--source-max", "500", "--test-max", "700"],
        tag="lint",
        timeout=60,
    ),
    Step(
        "End-to-end tests",
        _PW + ["test", "--config", r"tests\e2e\playwright.config.ts"],
        tag="e2e",
        timeout=1800,
    ),
]

STEP_BY_NAME = {step.name: step for step in VERIFY}
ALL_TAGS = {"lint", "python", "frontend", "e2e", "build", "storybook"}


def step_timeout(step: Step) -> float:
    return step.timeout if step.timeout is not None else DEFAULT_TIMEOUT_SECONDS


def run_step(step: Step, show_success: bool, *, timeout_multiplier: float = 1.0) -> bool:
    timeout = step_timeout(step) * timeout_multiplier
    if show_success:
        print(f"START {step.name}", flush=True)
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            step.command,
            cwd=step.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        _report_failure(step, started, "", "", timeout=timeout, exc=exc)
        return False
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        stop_process_tree(process)
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            stdout, stderr = "", ""
    if timed_out:
        _report_failure(step, started, stdout, stderr, timeout=timeout, timed_out=True)
        return False
    if process.returncode == 0:
        _report_pass(step, started)
        return True
    is_documented_storybook_teardown = (
        os.name == "nt"
        and step.name == "Storybook build"
        and process.returncode == STORYBOOK_WINDOWS_TEARDOWN_RETURN_CODE
        and "Storybook build completed successfully" in stdout
        and stderr.strip() == STORYBOOK_WINDOWS_TEARDOWN_ASSERTION
    )
    if is_documented_storybook_teardown:
        _report_pass(step, started, note="ignored documented Windows libuv teardown assertion")
        return True
    _report_failure(step, started, stdout, stderr, timeout=timeout)
    return False


def _report_pass(step: Step, started: float, note: str = "") -> None:
    duration = time.monotonic() - started
    suffix = f" ({note})" if note else ""
    print(f"PASS {step.name}{suffix} ({duration:.1f}s)", flush=True)


def _report_failure(
    step: Step,
    started: float,
    stdout: str,
    stderr: str,
    *,
    timeout: float,
    timed_out: bool = False,
    exc: BaseException | None = None,
) -> None:
    duration = time.monotonic() - started
    if timed_out:
        print(f"TIMEOUT {step.name} ({duration:.1f}s, limit {timeout:.0f}s)", flush=True)
    else:
        print(f"FAIL {step.name} ({duration:.1f}s)", flush=True)
    _write_failure_log(step, stdout, stderr)
    if exc is not None:
        print(f"  {exc}", file=sys.stderr)
    _print_excerpt(stdout, stderr)
    print(f"  Rerun: {_rerun_command(step)}", file=sys.stderr, flush=True)


def _merged_output(stdout: str, stderr: str) -> str:
    chunks = [chunk for chunk in (stdout, stderr) if chunk and chunk.strip()]
    return "\n".join(chunks).strip()


def _print_excerpt(stdout: str, stderr: str) -> None:
    lines = [line for line in _merged_output(stdout, stderr).splitlines() if line.strip()]
    lines = lines[-EXCERPT_LINES:]
    if not lines:
        print("  (no captured output)", file=sys.stderr)
        return
    print("  --- excerpt (tail) ---", file=sys.stderr)
    for line in lines:
        print(f"  {line}", file=sys.stderr)


def _write_failure_log(step: Step, stdout: str, stderr: str) -> None:
    FAILURE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    body = f"=== check: {step.name} ===\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}\n"
    FAILURE_LOG_PATH.write_text(body, encoding="utf-8")


def remove_stale_failure_log() -> None:
    if FAILURE_LOG_PATH.is_file():
        FAILURE_LOG_PATH.unlink()


def _rerun_command(step: Step) -> str:
    command = " ".join(step.command)
    if step.cwd and step.cwd != str(REPO_ROOT):
        return f"{command} (cwd: {step.cwd})"
    return command


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
