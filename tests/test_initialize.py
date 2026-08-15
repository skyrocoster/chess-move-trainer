from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "initialize.ps1"


def powershell() -> str | None:
    return shutil.which("powershell") or shutil.which("pwsh")


pytestmark = pytest.mark.skip(
    reason="initialize.ps1 is not yet implemented; see docs/plans/active/repository-initializer"
)


@pytest.mark.skipif(powershell() is None, reason="Windows PowerShell is required")
def test_parameterized_initialization_updates_identity_and_is_safe(tmp_path: Path) -> None:
    destination = tmp_path / "copy"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".venv", "node_modules", "__pycache__"),
    )
    (destination / "node_modules").mkdir()
    (destination / "unknown-ignored.txt").write_text("keep", encoding="utf-8")
    command = [
        powershell(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(destination / SCRIPT.name),
        "-ProjectSlug",
        "sample-project",
        "-DisplayTitle",
        "Sample Project",
        "-ProjectDescription",
        "A sample project.",
        "-DocsBrand",
        "Sample Project Docs",
        "-CleanGenerated",
        "-NonInteractive",
        "-KeepInitializer",
    ]
    result = subprocess.run(command, cwd=destination, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (destination / "node_modules").exists()
    assert (destination / "unknown-ignored.txt").exists()
    assert json.loads((destination / "package.json").read_text())["name"] == "sample-project"
    assert "Sample Project" in (destination / "frontend/index.html").read_text()
    assert "sample-project" in (destination / "frontend/package-lock.json").read_text()


@pytest.mark.skipif(powershell() is None, reason="Windows PowerShell is required")
def test_noninteractive_requires_explicit_cleanup(tmp_path: Path) -> None:
    destination = tmp_path / "copy"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".venv", "node_modules", "__pycache__"),
    )
    command = [
        powershell(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(destination / SCRIPT.name),
        "-ProjectSlug",
        "sample-project",
        "-DisplayTitle",
        "Sample Project",
        "-ProjectDescription",
        "A sample project.",
        "-DocsBrand",
        "Sample Project Docs",
        "-NonInteractive",
    ]
    result = subprocess.run(command, cwd=destination, capture_output=True, text=True, timeout=30)
    assert result.returncode != 0
    assert "CleanGenerated" in result.stdout + result.stderr
