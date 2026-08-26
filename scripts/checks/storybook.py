"""Storybook interaction and accessibility validation."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

from scripts.checks.steps import (
    REPO_ROOT,
    Step,
    run_step,
    stop_process_tree,
)


def _storybook_is_ready(process: subprocess.Popen[str], timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen("http://127.0.0.1:6006/index.json", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.5)
    return False


def run_storybook_validation() -> bool:
    command = ["npm.cmd", "run", "storybook", "--prefix", "frontend", "--", "--ci"]
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as server_log:
        try:
            process = subprocess.Popen(
                command,
                cwd=REPO_ROOT,
                stdout=server_log,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creationflags,
            )
        except FileNotFoundError as exc:
            print("--- Storybook validation failed (missing executable) ---", file=sys.stderr)
            print(str(exc), file=sys.stderr)
            return False
        try:
            if not _storybook_is_ready(process, timeout=120):
                print("--- Storybook server failed to become ready ---", file=sys.stderr)
                server_log.seek(0)
                log = server_log.read().strip()
                if log:
                    print(log, file=sys.stderr)
                return False
            step = Step(
                "Storybook interaction and accessibility tests",
                [
                    "npm.cmd",
                    "run",
                    "test-storybook",
                    "--prefix",
                    "frontend",
                    "--",
                    "--url",
                    "http://127.0.0.1:6006",
                ],
            )
            return run_step(step, show_success=True)
        finally:
            stop_process_tree(process)
