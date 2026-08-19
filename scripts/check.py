"""Run the repository's complete local quality suite.

The default mode is read-only. ``--fix`` explicitly runs deterministic formatters
before the same verification suite. Workflow configuration is checked in-process;
the retired lifecycle checkers are not invoked.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Step:
    name: str
    command: list[str]
    cwd: str | None = None


REPO_ROOT = Path(__file__).resolve().parents[1]

FIX_STEPS: list[Step] = [
    Step("Ruff lint fix", [sys.executable, "-m", "ruff", "check", "--fix", "."]),
    Step("Ruff format", [sys.executable, "-m", "ruff", "format", "."]),
    Step("ESLint fix", ["npm.cmd", "run", "lint", "--prefix", "frontend", "--", "--fix"]),
    Step("Prettier format", ["npm.cmd", "run", "format", "--prefix", "frontend"]),
]

VERIFY: list[Step] = [
    Step("Ruff lint check", [sys.executable, "-m", "ruff", "check", "."]),
    Step("Ruff format check", [sys.executable, "-m", "ruff", "format", "--check", "."]),
    Step("Python tests", [sys.executable, "-m", "pytest"]),
    Step("Workflow tests", [sys.executable, "-m", "pytest", "scripts/tests"]),
    Step("Frontend tests", ["npm.cmd", "run", "test", "--prefix", "frontend", "--", "--run"]),
    Step("ESLint check", ["npm.cmd", "run", "lint", "--prefix", "frontend"]),
    Step("Prettier check", [r"frontend\node_modules\.bin\prettier.cmd", "--check", "frontend"]),
    Step("Frontend build", ["npm.cmd", "run", "build", "--prefix", "frontend"]),
    Step(
        "Source size check",
        [sys.executable, "scripts/check_size.py", "--source-max", "500", "--test-max", "700"],
    ),
    Step(
        "End-to-end tests",
        [
            r"node_modules\.bin\playwright.cmd",
            "test",
            "--config",
            r"tests\e2e\playwright.config.ts",
        ],
    ),
]

REQUIRED_WORKFLOW_PATHS = (
    Path(".opencode/agents/coordinator.md"),
    Path(".opencode/agents/scout.md"),
    Path(".opencode/agents/coordinator-caseworker.md"),
    Path(".opencode/agents/coordinator-caseworker-flash.md"),
    Path(".opencode/agents/quality.md"),
    Path(".opencode/agents/exploration.md"),
    Path(".opencode/skills/coordinator-workflow/SKILL.md"),
    Path(".opencode/skills/grilling/SKILL.md"),
    Path(".opencode/skills/assess-case/SKILL.md"),
    Path(".opencode/skills/plan/SKILL.md"),
    Path(".opencode/skills/execute/SKILL.md"),
    Path(".opencode/skills/validate/SKILL.md"),
    Path(".opencode/skills/fix/SKILL.md"),
    Path(".opencode/skills/mock-up/SKILL.md"),
    Path(".opencode/skills/prototype/SKILL.md"),
    Path("experiments/README.md"),
    Path("experiments/.gitignore"),
    Path("experiments/pyproject.toml"),
    Path("experiments/package.json"),
    Path("experiments/package-lock.json"),
    Path("experiments/mock-ups/README.md"),
    Path("experiments/prototypes/README.md"),
    Path("experiments/fixtures/README.md"),
)

REQUIRED_AGENT_NAMES = {
    "coordinator.md",
    "scout.md",
    "coordinator-caseworker.md",
    "coordinator-caseworker-flash.md",
    "quality.md",
    "exploration.md",
}
REQUIRED_SKILL_NAMES = {
    "assess-case",
    "browser-validation-invoke",
    "coordinator-workflow",
    "execute",
    "fix",
    "frontend-component-iteration",
    "frontend-design",
    "grilling",
    "master-plan",
    "mock-up",
    "plan",
    "prototype",
    "ux-design",
    "validate",
}
ALLOWED_SCRIPT_NAMES = {"check.py", "check_size.py", "dev.py", "scout_db_query.py"}


def run_step(step: Step, show_success: bool) -> bool:
    try:
        result = subprocess.run(
            step.command,
            cwd=step.cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        print(f"--- {step.name} failed (missing executable) ---", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return False

    if result.returncode == 0:
        if show_success:
            print(f"Passed: {step.name}")
        return True

    print(f"--- {step.name} failed ---", file=sys.stderr)
    out = result.stdout.strip()
    err = result.stderr.strip()
    if out:
        print(out, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    return False


def _frontmatter_is_present(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return text.startswith("---\n") and "\n---\n" in text[4:]


def check_workflow_contract() -> bool:
    """Check the small, repository-independent workflow contract."""

    failures: list[str] = []
    for relative in REQUIRED_WORKFLOW_PATHS:
        if not (REPO_ROOT / relative).is_file():
            failures.append(f"missing required workflow file: {relative.as_posix()}")
    agents = REPO_ROOT / ".opencode" / "agents"
    skills = REPO_ROOT / ".opencode" / "skills"
    if not agents.is_dir():
        failures.append("missing workflow directory: .opencode/agents")
    else:
        for path in agents.glob("*.md"):
            if path.name not in REQUIRED_AGENT_NAMES:
                failures.append(f"unexpected workflow agent: {path.relative_to(REPO_ROOT)}")
            elif not _frontmatter_is_present(path):
                failures.append(f"missing frontmatter: {path.relative_to(REPO_ROOT)}")
    if not skills.is_dir():
        failures.append("missing workflow directory: .opencode/skills")
    else:
        for directory in skills.iterdir():
            if not directory.is_dir() or not (directory / "SKILL.md").is_file():
                continue
            if directory.name not in REQUIRED_SKILL_NAMES:
                failures.append(f"unexpected workflow skill: {directory.relative_to(REPO_ROOT)}")
                continue
            path = directory / "SKILL.md"
            if not path.is_file() or not _frontmatter_is_present(path):
                failures.append(f"missing skill frontmatter: {path.relative_to(REPO_ROOT)}")

    scripts = REPO_ROOT / "scripts"
    for path in scripts.glob("*.py"):
        if path.name not in ALLOWED_SCRIPT_NAMES:
            failures.append(f"unexpected top-level script: {path.relative_to(REPO_ROOT)}")

    commands = REPO_ROOT / ".opencode" / "commands"
    if commands.is_dir():
        for path in commands.rglob("*"):
            if path.is_file():
                failures.append(f"unexpected workflow command: {path.relative_to(REPO_ROOT)}")

    json_paths = (
        Path("package.json"),
        Path("frontend/package.json"),
        Path("experiments/package.json"),
        Path("experiments/package-lock.json"),
    )
    for relative in json_paths:
        path = REPO_ROOT / relative
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"invalid JSON in {relative.as_posix()}: {exc}")

    if failures:
        print("Workflow contract failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return False
    print("Passed: Workflow contract")
    return True


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="run deterministic formatters before verification; default mode is read-only",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    failed = False

    if args.fix:
        print("== Fix phase (explicit deterministic formatters) ==", flush=True)
        for step in FIX_STEPS:
            if not run_step(step, show_success=False):
                failed = True
    else:
        print("== Read-only mode (no formatters or generated files) ==", flush=True)

    print("== Verify phase ==", flush=True)
    if not check_workflow_contract():
        failed = True
    for step in VERIFY:
        if not run_step(step, show_success=True):
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
