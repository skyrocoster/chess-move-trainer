"""Workflow contract verification — agents, skills, scripts, and JSON validity."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.checks.steps import REPO_ROOT

REQUIRED_WORKFLOW_PATHS = (
    Path(".opencode/agents/coordinator.md"),
    Path(".opencode/agents/scout.md"),
    Path(".opencode/agents/coordinator-caseworker.md"),
    Path(".opencode/agents/coordinator-caseworker-flash.md"),
    Path(".opencode/agents/coordinator-caseworker-sol.md"),
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
    "coordinator-caseworker-sol.md",
    "quality.md",
    "exploration.md",
    "readme-updater.md",
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
ALLOWED_COMMAND_NAMES = {"commit.md"}


def _frontmatter_is_present(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return text.startswith("---\n") and "\n---\n" in text[4:]


def check_workflow_contract() -> bool:
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
            if path.is_file() and path.name not in ALLOWED_COMMAND_NAMES:
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
        print("\n".join(f"- {f}" for f in failures), file=sys.stderr)
        return False
    return True
