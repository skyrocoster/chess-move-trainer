"""Console output and finite subprocess helpers shared by ``sg`` commands."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from tools.dev.config import REPOSITORY_ROOT

# When true, run() only prints the command and pretends it succeeded with no output.
_dry_run = False


def set_dry_run(enabled: bool) -> None:
    """Switch dry-run mode on or off for every helper in this module."""
    global _dry_run
    _dry_run = enabled


def is_dry_run() -> bool:
    """Return whether commands are only being printed."""
    return _dry_run


def echo(message: str = "", *, err: bool = False) -> None:
    """Print one line to stdout or stderr."""
    print(message, file=sys.stderr if err else sys.stdout, flush=True)


def fail(message: str, code: int = 1) -> NoReturn:
    """Report a failure on stderr and exit with the given code."""
    echo(message, err=True)
    raise SystemExit(code)


def host_command(command: Sequence[str | Path]) -> list[str]:
    """Return a command Windows can execute directly.

    ``npm`` and ``npx`` are ``.cmd`` shims on Windows and cannot be started by
    ``subprocess`` without a command shell.
    """
    resolved = [str(part) for part in command]
    if sys.platform == "win32" and resolved and resolved[0] in ("npm", "npx"):
        return ["cmd", "/c", *resolved]
    return resolved


def run(
    command: Sequence[str | Path],
    *,
    cwd: Path = REPOSITORY_ROOT,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
    check: bool = True,
    quiet: bool = False,
    timeout: float,
) -> subprocess.CompletedProcess[str]:
    """Run one bounded child process, echoing the command first.

    ``quiet`` suppresses the command echo (used for status queries).
    """
    if timeout <= 0:
        raise ValueError("subprocess timeout must be finite and positive")
    resolved = host_command(command)
    if _dry_run:
        if not quiet:
            echo(f"[dry-run] > {subprocess.list2cmdline(resolved)}")
        return subprocess.CompletedProcess(resolved, 0, "", "")
    if not quiet:
        echo(f"> {subprocess.list2cmdline(resolved)}")
    try:
        result = subprocess.run(
            resolved,
            cwd=str(cwd),
            env=env,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        if capture_output:
            _show_timeout_output(error)
        fail(f"Command timed out after {timeout:g} seconds: {subprocess.list2cmdline(resolved)}")
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result


def output(
    command: Sequence[str | Path],
    *,
    cwd: Path = REPOSITORY_ROOT,
    timeout: float,
) -> str:
    """Run one bounded command quietly and return its combined output."""
    if timeout <= 0:
        raise ValueError("subprocess timeout must be finite and positive")
    resolved = host_command(command)
    try:
        result = subprocess.run(
            resolved,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        _show_timeout_output(error)
        fail(f"Command timed out after {timeout:g} seconds: {subprocess.list2cmdline(resolved)}")
    return (result.stdout + result.stderr).strip()


def kill_process_tree(process: subprocess.Popen[str]) -> None:
    """Kill a child process and everything it started."""
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],
                capture_output=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        process.kill()
    except OSError:
        pass


def _show_timeout_output(error: subprocess.TimeoutExpired) -> None:
    """Preserve captured output when a bounded command expires."""
    for stream_text, stream in ((error.stdout, sys.stdout), (error.stderr, sys.stderr)):
        if isinstance(stream_text, bytes):
            stream_text = stream_text.decode(errors="replace")
        if stream_text:
            print(stream_text, end="", file=stream)
