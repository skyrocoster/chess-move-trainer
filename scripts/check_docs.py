#!/usr/bin/env python
"""Validate the workflow documentation contract without product assumptions."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = REPO_ROOT / "docs"
ACTIVE_PLANS = DOCS_ROOT / "plans" / "active"
AGENTS_DIR = REPO_ROOT / ".opencode" / "agents"
LUNA_AGENT = AGENTS_DIR / "coordinator-caseworker.md"
FLASH_AGENT = AGENTS_DIR / "coordinator-caseworker-flash.md"
FLASH_MODEL = "opencode-go/deepseek-v4-flash"
LINK_RE = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
STATUS_RE = re.compile(r"^>\s+\*\*Status:\*\*\s+.+$", re.MULTILINE)
READ_TRIGGER_RE = re.compile(r"^[-*]\s+\*\*Read trigger:\*\*\s+.+$", re.MULTILINE)
TOUCHES_RE = re.compile(r"^##\s+Touches\s*$", re.MULTILINE | re.IGNORECASE)
TOUCH_GLOB_RE = re.compile(r"^\s*[-*]\s+`([^`]+)`\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Finding:
    path: str
    message: str
    fix: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}\n    fix: {self.fix}"


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def anchor(value: str) -> str:
    """Match the common GitHub Markdown anchor form for local documentation links."""
    value = unquote(value).strip().lower()
    value = re.sub(r"[^a-z0-9 _-]", "", value)
    return re.sub(r"[ _]+", "-", value).strip("-")


EXCLUDED_DOC_PREFIXES = ("grilling-docs", "plans/done")


def markdown_files() -> list[Path]:
    if not DOCS_ROOT.exists():
        return []
    files: list[Path] = []
    for path in DOCS_ROOT.rglob("*.md"):
        rel_parts = path.relative_to(DOCS_ROOT).parts
        if any(
            rel_parts[: len(prefix.split("/"))] == tuple(prefix.split("/"))
            for prefix in EXCLUDED_DOC_PREFIXES
        ):
            continue
        files.append(path)
    return sorted(files)


def generate_flash_agent(canonical_text: str) -> str:
    """Create the DeepSeek Flash variant from the canonical Luna caseworker agent."""
    flash = re.sub(
        r"^description:\s*(Luna case-worker)",
        r"description: DeepSeek Flash case-worker",
        canonical_text,
        flags=re.MULTILINE,
    )
    flash = re.sub(r"^model:\s*.+$", f"model: {FLASH_MODEL}", flash, flags=re.MULTILINE)
    flash = flash.replace("resumable Luna case-worker", "resumable DeepSeek Flash case-worker")
    flash = flash.replace("A fresh Luna session", "A fresh DeepSeek Flash session")
    flash = re.sub(r"^variant:\s*\w+", "variant: high", flash, flags=re.MULTILINE)
    return flash


def sync_caseworker_agents(write: bool) -> list[Finding]:
    """Keep the Flash caseworker agent as a carbon copy of the Luna one."""
    findings: list[Finding] = []
    if not LUNA_AGENT.exists():
        findings.append(
            Finding(
                relative(LUNA_AGENT),
                "canonical Luna caseworker agent is missing",
                "Restore .opencode/agents/coordinator-caseworker.md",
            )
        )
        return findings

    expected = generate_flash_agent(LUNA_AGENT.read_text(encoding="utf-8"))

    if write:
        FLASH_AGENT.write_text(expected, encoding="utf-8", newline="\n")
        return findings

    if not FLASH_AGENT.exists():
        findings.append(
            Finding(
                relative(FLASH_AGENT),
                "DeepSeek Flash caseworker agent is missing",
                "Run scripts/check_docs.py --write-generated to generate it",
            )
        )
        return findings

    actual = FLASH_AGENT.read_text(encoding="utf-8")
    if actual != expected:
        findings.append(
            Finding(
                relative(FLASH_AGENT),
                "DeepSeek Flash caseworker agent is out of sync with the Luna agent",
                "Run scripts/check_docs.py --write-generated to regenerate it",
            )
        )
    return findings


def check_links(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    headings = {anchor(match.group(2)) for match in HEADING_RE.finditer(text)}
    findings: list[Finding] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
        if (
            not target
            or target in {"#", "./#"}
            or target.startswith(("http://", "https://", "mailto:"))
        ):
            if target.startswith("#") and target != "#" and anchor(target[1:]) not in headings:
                findings.append(
                    Finding(
                        relative(path),
                        f"missing local anchor {target}",
                        "Correct or remove the fragment",
                    )
                )
            continue
        destination, separator, fragment = target.partition("#")
        resolved = (path.parent / destination).resolve()
        if not resolved.exists():
            findings.append(
                Finding(
                    relative(path),
                    f"broken local link: {target}",
                    "Create the target or correct the link",
                )
            )
            continue
        if separator and resolved.suffix.lower() == ".md":
            target_headings = {
                anchor(item.group(2))
                for item in HEADING_RE.finditer(resolved.read_text(encoding="utf-8"))
            }
            if anchor(fragment) not in target_headings:
                findings.append(
                    Finding(
                        relative(path),
                        f"missing linked anchor: {target}",
                        "Correct or remove the fragment",
                    )
                )
    return findings


def active_plans() -> list[Path]:
    if not ACTIVE_PLANS.exists():
        return []
    return sorted(
        path for path in ACTIVE_PLANS.glob("*/*.md") if path.parent.parent == ACTIVE_PLANS
    )


def check_plan(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    feature = path.parent.name
    if path.stem != feature:
        findings.append(
            Finding(
                relative(path),
                "active Plan filename must match its feature directory",
                "Rename it to <feature>/<feature>.md",
            )
        )
    if not STATUS_RE.search(text):
        findings.append(
            Finding(
                relative(path),
                "missing Plan Status line",
                "Add `> **Status:** ...` below the title",
            )
        )
    if not READ_TRIGGER_RE.search(text):
        findings.append(
            Finding(relative(path), "missing Read trigger", "Add `- **Read trigger:** ...`")
        )
    touches = TOUCHES_RE.search(text)
    if not touches:
        findings.append(
            Finding(
                relative(path),
                "missing `## Touches` section",
                "Declare the files or globs this Plan may change",
            )
        )
        return findings
    section = text[touches.end() :]
    next_heading = re.search(r"^##\s+", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    globs = TOUCH_GLOB_RE.findall(section)
    if not globs:
        findings.append(
            Finding(
                relative(path),
                "Touches has no backtick-quoted paths or globs",
                "Add one or more repo-relative ownership globs",
            )
        )
    for pattern in globs:
        normalized = pattern.replace("\\", "/").lstrip("./")
        if normalized.startswith("/") or ".." in Path(normalized).parts:
            findings.append(
                Finding(
                    relative(path),
                    f"invalid Touches glob: `{pattern}`",
                    "Use a repo-relative glob without traversal",
                )
            )
        elif not list(REPO_ROOT.glob(normalized)):
            findings.append(
                Finding(
                    relative(path),
                    f"Touches glob matches nothing: `{pattern}`",
                    "Correct the glob or remove it until the target exists",
                )
            )
    return findings


def check_orders() -> list[Finding]:
    checker_path = REPO_ROOT / "scripts" / "check_orders.py"
    if not checker_path.exists():
        return []
    spec = importlib.util.spec_from_file_location("workflow_order_checker", checker_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return [Finding(error.file, error.message, error.fix) for error in module.lint_orders()]


def run(write_generated: bool = False) -> list[Finding]:
    if not DOCS_ROOT.exists():
        return [
            Finding(
                "docs",
                "documentation directory is missing",
                "Create docs/ with the workflow documentation",
            )
        ]
    findings: list[Finding] = []
    for path in markdown_files():
        findings.extend(check_links(path))
    for path in active_plans():
        findings.extend(check_plan(path))
    findings.extend(check_orders())
    findings.extend(sync_caseworker_agents(write_generated))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate documentation (default)")
    parser.add_argument(
        "--write-generated",
        action="store_true",
        help="regenerate derived agent and documentation artifacts",
    )
    parser.add_argument(
        "--base",
        help="accepted for CI compatibility; no project-specific diff checks are configured",
    )
    args = parser.parse_args()
    write_generated = args.write_generated
    findings = run(write_generated=write_generated)
    if findings:
        print("\n\n".join(str(finding) for finding in findings))
        print(f"\n{len(findings)} documentation contract failure(s).")
        return 1
    if write_generated:
        print("Generated documentation artifacts written and all checks pass.")
    else:
        print("Documentation contract: all checks pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
