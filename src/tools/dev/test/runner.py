"""Selection execution, bounded process control and run reporting for ``sg test``."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from tools.dev.config import REPOSITORY_ROOT
from tools.dev.console import echo, fail, host_command
from tools.dev.test import backends, reports
from tools.dev.test.discovery import TestCase
from tools.dev.test.selection import SelectionError


def commands_for(cases: list[TestCase], catalog, *, report_dir: Path | None = None):
    """Return the ordered commands for a selection (catalogue kept for parity)."""
    del catalog
    from tools.dev.config import TEST_RESULTS_DIR

    directory = report_dir or TEST_RESULTS_DIR / "<run-id>"
    return backends.commands_for(cases, directory)


def dry_run(
    cases: list[TestCase],
    catalog,
    *,
    allow_real_data: bool,
    budget_seconds: float | None = None,
) -> None:
    """Print the exact commands, timeouts and safety profile without running."""
    from tools.dev.test.selection import describe as selection_describe

    echo(f"Selection: {selection_describe(cases)}")
    echo(f"Real-data opt-in: {'yes' if allow_real_data else 'no'}")
    if budget_seconds is not None:
        echo(f"Soft budget: {budget_seconds:g}s (hard deadlines are per command)")
    echo("Concurrency: one runner command at a time")
    for command in commands_for(cases, catalog):
        echo(
            f"  [{command.timeout:g}s] (cwd {command.cwd}) "
            f"{subprocess.list2cmdline(list(command.args))}"
        )


def execute(
    cases: list[TestCase],
    catalog,
    *,
    request: dict,
    budget_seconds: float | None = None,
    allow_real_data: bool = False,
    selection_seconds: float = 0.0,
) -> reports.RunReport:
    """Run the resolved selection one bounded command at a time."""
    del allow_real_data  # enforced by preflight
    report = reports.RunReport.start(
        request=request,
        budget_seconds=budget_seconds,
        selection_seconds=selection_seconds,
    )
    try:
        commands = commands_for(cases, catalog, report_dir=report.directory)
    except SelectionError:
        report.abandon()
        raise
    for command in commands:
        group = [
            case
            for case in cases
            if case.backend == command.backend
            and (not command.selectors or case.selector in command.selectors)
        ]
        echo(f"# {command.label}")
        echo(f"> {subprocess.list2cmdline(list(command.args))}")
        result = _run_command(command)
        outcomes = reports.parse_artifact(command, report.directory)
        first_error = _first_error(command, result, outcomes)
        report.add_command(
            command,
            result.exit_code,
            result.duration_seconds,
            timed_out=result.timed_out,
            outcomes=outcomes,
            cases=group,
            first_error=first_error,
        )
        outcome = "PASS" if result.exit_code == 0 else "FAIL"
        echo(f"--- {outcome} {command.label} ({result.duration_seconds:.1f}s)")
        if result.exit_code != 0:
            if first_error:
                echo(f"First error: {first_error}", err=True)
            break
    report.finalize()
    report.write()
    echo(f"Report: {report.directory}")
    return report


class CommandResult:
    """The bounded outcome of one child process."""

    def __init__(self, exit_code: int, duration_seconds: float, timed_out: bool = False):
        self.exit_code = exit_code
        self.duration_seconds = duration_seconds
        self.timed_out = timed_out


def _run_command(command) -> CommandResult:
    environment = os.environ.copy()
    environment.update(command.env)
    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            host_command(command.args),
            cwd=str(REPOSITORY_ROOT / command.cwd),
            env=environment,
            creationflags=creation_flags,
            start_new_session=os.name != "nt",
        )
    except OSError as error:
        fail(f"Could not start {command.label}: {error}")
    try:
        exit_code = process.wait(timeout=command.timeout)
        return CommandResult(exit_code, time.monotonic() - started)
    except subprocess.TimeoutExpired:
        _kill_process_tree(process)
        echo(
            f"Error: {command.label} exceeded its {command.timeout:g}s hard deadline;"
            " its process tree was terminated.",
            err=True,
        )
        return CommandResult(1, time.monotonic() - started, timed_out=True)


def _first_error(command, result: CommandResult, outcomes) -> str:
    if result.timed_out:
        return f"exceeded the {command.timeout:g}s hard deadline"
    for outcome in outcomes:
        if outcome.failed and outcome.message:
            return outcome.message
    if result.exit_code != 0:
        return f"exit code {result.exit_code}"
    return ""


def _kill_process_tree(process: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    else:
        try:
            os.killpg(os.getpgid(process.pid), 9)
        except (ProcessLookupError, PermissionError):
            process.kill()
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=30)


def describe(cases: list[TestCase]) -> str:
    """Re-export the selection description for the command adapter."""
    from tools.dev.test.selection import describe as selection_describe

    return selection_describe(cases)
