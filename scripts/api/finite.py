"""Run one child command with an explicit finite timeout, Windows-safe.

Usage: python scripts/api/finite.py <seconds> <command> [args...]

On expiry the complete child process tree is terminated (taskkill /T /F) and the
wrapper exits with status 124. Otherwise the child's exit status is returned.
"""

from __future__ import annotations

import subprocess
import sys

KILL_EXIT_CODE = 124
GRACE_EXIT_WAIT_SECONDS = 10.0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: finite.py <seconds> <command> [args...]", file=sys.stderr)
        return 2
    try:
        seconds = float(argv[0])
    except ValueError:
        print(f"invalid seconds: {argv[0]!r}", file=sys.stderr)
        return 2
    if not seconds > 0 or seconds != seconds or seconds == float("inf"):
        print("seconds must be a positive finite number", file=sys.stderr)
        return 2

    command = argv[1:]
    try:
        process = subprocess.Popen(command)
    except FileNotFoundError as exc:
        print(f"command not found: {exc.filename}", file=sys.stderr)
        return 127

    try:
        return process.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        # Kill the whole process tree so spawned grandchildren cannot outlive the limit.
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            timeout=GRACE_EXIT_WAIT_SECONDS,
        )
        try:
            process.wait(timeout=GRACE_EXIT_WAIT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=GRACE_EXIT_WAIT_SECONDS)
        print(f"command exceeded {seconds:g}s and was terminated", file=sys.stderr)
        return KILL_EXIT_CODE


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
