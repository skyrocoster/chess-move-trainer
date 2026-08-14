"""Start Windows development services after clearing their exact ports."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from collections.abc import Iterable

PORTS = {"backend": 5666, "frontend": 8444}


def clear_port(port: int) -> None:
    inspection = (
        f"$connections = @(Get-NetTCPConnection -LocalPort {port} -State Listen "
        "-ErrorAction SilentlyContinue); "
        "if ($connections.Count -eq 0) { exit 0 }; "
        "$connections | Select-Object -Expand OwningProcess"
    )
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            inspection,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(f"Could not inspect port {port}: {result.stderr.strip()}")
    for line in set(result.stdout.splitlines()):
        if line.strip().isdigit() and int(line.strip()) > 0:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {line.strip()} -Force"],
                check=True,
            )


def command_for(mode: str) -> list[str]:
    if mode == "backend":
        return [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "localhost",
            "--port",
            "5666",
        ]
    return ["npm.cmd", "run", "dev", "--prefix", "frontend"]


def start(mode: str) -> int:
    services = [mode] if mode != "all" else ["backend", "frontend"]
    processes: list[subprocess.Popen[bytes]] = []
    try:
        for service in services:
            clear_port(PORTS[service])
        for service in services:
            processes.append(subprocess.Popen(command_for(service), env=os.environ.copy()))
        if mode != "all":
            return processes[0].wait()
        while True:
            if any(process.poll() is not None for process in processes):
                return 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        for process in processes:
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start the Windows development services.")
    parser.add_argument("mode", choices=["backend", "frontend", "all"])
    args = parser.parse_args(argv)
    return start(args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
