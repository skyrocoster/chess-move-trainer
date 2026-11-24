"""The root Typer application exposed as the ``sg`` command."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import typer

from tools.dev.cli import check_commands, dev_commands, screenshot_commands, test_commands
from tools.dev.config import REPOSITORY_ROOT, SG_SCRIPT, VENV_PYTHON
from tools.dev.console import echo, host_command

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help=(
        "The Chess Move Trainer developer CLI. Bootstrap once with"
        " `uv sync --frozen`, then run `uv run --no-sync sg ...`."
    ),
)


def _capture(command: list[str], timeout: float) -> tuple[int, str]:
    """Run one bounded query; return (exit code, combined output), -1 when it cannot run."""
    try:
        result = subprocess.run(
            host_command(command), capture_output=True, text=True, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return -1, str(error)
    return result.returncode, (result.stdout + result.stderr).strip()


def _node_ok(version: str) -> bool:
    match = re.match(r"v?(\d+)\.", version)
    return bool(match) and int(match.group(1)) == 24


def _playwright_chromium_installed() -> bool:
    override = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if override:
        base = Path(override)
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
    else:
        base = Path.home() / ".cache" / "ms-playwright"
    return base.is_dir() and any(base.glob("chromium-*"))


@app.command("setup", help="Check local prerequisites. Installs nothing.")
def setup_command() -> None:
    """Report each prerequisite as ok, warn or FAIL; exit 1 if a required one fails."""
    failures = 0

    def report(status: str, label: str, detail: str) -> None:
        nonlocal failures
        if status == "FAIL":
            failures += 1
        echo(f"[{status:>4}] {label:<14} {detail}")

    if shutil.which("uv") is None:
        report("FAIL", "uv", "not found on PATH; install uv")
    else:
        code, text = _capture(["uv", "--version"], 30)
        report("ok" if code == 0 else "FAIL", "uv", text)

    if not VENV_PYTHON.is_file():
        report("FAIL", ".venv python", f"missing {VENV_PYTHON}; run `uv sync --frozen`")
    else:
        code, text = _capture([str(VENV_PYTHON), "--version"], 30)
        ok = code == 0 and text.startswith("Python 3.12")
        report("ok" if ok else "FAIL", ".venv python", text + ("" if ok else " (need 3.12)"))

    if shutil.which("node") is None:
        report("warn", "node", "not found on PATH; needs >=24 <25")
    else:
        code, text = _capture(["node", "--version"], 30)
        if code == 0 and _node_ok(text):
            report("ok", "node", text)
        else:
            report("warn", "node", f"{text} (engines pin is >=24 <25; usually safe to ignore)")

    if shutil.which("npm") is None:
        report("FAIL", "npm", "not found on PATH")
    else:
        code, text = _capture(["npm", "--version"], 60)
        report("ok" if code == 0 else "FAIL", "npm", text)

    if shutil.which("docker") is None:
        report("FAIL", "docker", "CLI not found on PATH")
    else:
        code, text = _capture(["docker", "--version"], 30)
        report("ok" if code == 0 else "FAIL", "docker", text)
        code, text = _capture(["docker", "info", "--format", "{{.ServerVersion}}"], 60)
        if code == 0:
            report("ok", "docker daemon", f"server {text}")
        else:
            report("FAIL", "docker daemon", "Docker Desktop is not running")

    if SG_SCRIPT.is_file():
        report("ok", "sg script", str(SG_SCRIPT))
    else:
        report("FAIL", "sg script", f"missing {SG_SCRIPT}; run `uv sync --frozen`")

    if (REPOSITORY_ROOT / "node_modules").is_dir():
        report("ok", "node_modules", "present")
    else:
        report("warn", "node_modules", "missing; run `npm ci` before frontend or browser checks")

    if _playwright_chromium_installed():
        report("ok", "playwright", "chromium installed")
    else:
        report("warn", "playwright", "chromium not found; run `npx playwright install chromium`")

    if failures:
        raise typer.Exit(1)


@app.command("where", help="Print the repository root used by every sg command.")
def where_command() -> None:
    echo(str(REPOSITORY_ROOT))


app.add_typer(check_commands.app, name="check")
app.add_typer(dev_commands.app, name="dev")
app.add_typer(test_commands.app, name="test")
app.command(
    "screenshot",
    help="Capture UI screenshots and a JSON manifest for visual review.",
)(screenshot_commands.screenshot_command)


def main() -> None:
    """Console entry point for the ``sg`` command."""
    sys.argv[1:] = sys.argv[1:] or ["--help"]
    app()
