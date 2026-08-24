"""Run the repository's complete local quality suite.

The default mode is read-only. ``--fix`` explicitly runs deterministic formatters
and regenerates the database schema artifact before the same verification suite.
Workflow configuration is checked in-process; the retired lifecycle checkers are
not invoked.

Use category selectors to run subsets of the verification suite (e.g.
``--python`` for only Python-related steps).  Combine multiple selectors to
expand the set.  ``--only`` and ``--from`` offer fine-grained control by step
name.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from data.database import dump_schema  # noqa: E402


@dataclass
class Step:
    name: str
    command: list[str]
    cwd: str | None = None
    tag: str = ""


SCHEMA_FIX_COMMAND = r".venv\Scripts\python.exe scripts\check.py --fix"
STORYBOOK_WINDOWS_TEARDOWN_RETURN_CODE = 0xC0000409
STORYBOOK_WINDOWS_TEARDOWN_ASSERTION = (
    "Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), "
    r"file c:\ws\deps\uv\src\win\async.c, line 76"
)

FIX_STEPS: list[Step] = [
    Step("Ruff lint fix", [sys.executable, "-m", "ruff", "check", "--fix", "."]),
    Step("Ruff format", [sys.executable, "-m", "ruff", "format", "."]),
    Step("ESLint fix", ["npm.cmd", "run", "lint", "--prefix", "frontend", "--", "--fix"]),
    Step("Prettier format", ["npm.cmd", "run", "format", "--prefix", "frontend"]),
]

_RUFF = [sys.executable, "-m", "ruff"]
_NPM = lambda *a: ["npm.cmd", *a]  # noqa: E731
_PRETTIER = [r"frontend\node_modules\.bin\prettier.cmd"]
_PW = [r"node_modules\.bin\playwright.cmd"]

VERIFY: list[Step] = [
    Step("Ruff lint check", _RUFF + ["check", "."], tag="lint"),
    Step("Ruff format check", _RUFF + ["format", "--check", "."], tag="lint"),
    Step("Python tests", [sys.executable, "-m", "pytest"], tag="python"),
    Step("Workflow tests", [sys.executable, "-m", "pytest", "scripts/tests"], tag="python"),
    Step("Frontend tests",
         _NPM("run", "test", "--prefix", "frontend", "--", "--run"), tag="frontend"),
    Step("ESLint check", _NPM("run", "lint", "--prefix", "frontend"), tag="lint"),
    Step("Prettier check", _PRETTIER + ["--check", "frontend"], tag="lint"),
    Step("Frontend build", _NPM("run", "build", "--prefix", "frontend"), tag="build"),
    Step("Storybook build", _NPM("run", "build-storybook", "--prefix", "frontend"), tag="build"),
    Step("Source size check",
         [sys.executable, "scripts/check_size.py",
          "--source-max", "500", "--test-max", "700"], tag="lint"),
    Step("End-to-end tests",
         _PW + ["test", "--config", r"tests\e2e\playwright.config.ts"], tag="e2e"),
]

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
    "coordinator.md", "scout.md", "coordinator-caseworker.md",
    "coordinator-caseworker-flash.md", "coordinator-caseworker-sol.md",
    "quality.md", "exploration.md",
}
REQUIRED_SKILL_NAMES = {
    "assess-case", "browser-validation-invoke", "coordinator-workflow",
    "execute", "fix", "frontend-component-iteration", "frontend-design",
    "grilling", "master-plan", "mock-up", "plan", "prototype",
    "ux-design", "validate",
}
ALLOWED_SCRIPT_NAMES = {"check.py", "check_size.py", "dev.py", "scout_db_query.py"}


def run_step(step: Step, show_success: bool) -> bool:
    try:
        result = subprocess.run(
            step.command, cwd=step.cwd, check=False,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError as exc:
        print(f"--- {step.name} failed (missing executable) ---", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return False
    if result.returncode == 0:
        if show_success:
            print(f"Passed: {step.name}")
        return True
    is_documented_storybook_teardown = (
        os.name == "nt"
        and step.name == "Storybook build"
        and result.returncode == STORYBOOK_WINDOWS_TEARDOWN_RETURN_CODE
        and "Storybook build completed successfully" in result.stdout
        and result.stderr.strip() == STORYBOOK_WINDOWS_TEARDOWN_ASSERTION
    )
    if is_documented_storybook_teardown:
        if show_success:
            print(f"Passed: {step.name} (ignored documented Windows libuv teardown assertion)")
        return True
    print(f"--- {step.name} failed ---", file=sys.stderr)
    out = result.stdout.strip()
    err = result.stderr.strip()
    if out:
        print(out, file=sys.stderr)
    if err:
        print(err, file=sys.stderr)
    return False


def _stop_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False, capture_output=True, text=True,
        )
    else:
        process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


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
                command, cwd=REPO_ROOT, stdout=server_log,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                errors="replace", creationflags=creationflags,
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
                ["npm.cmd", "run", "test-storybook", "--prefix", "frontend",
                 "--", "--url", "http://127.0.0.1:6006"],
            )
            return run_step(step, show_success=True)
        finally:
            _stop_process_tree(process)


def regenerate_schema() -> bool:
    try:
        dump_schema.write_schema(dump_schema.OUT_PATH)
    except OSError as exc:
        print("--- Database schema regeneration failed ---", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return False
    print(f"Regenerated database schema: {dump_schema.OUT_PATH}")
    return True


def check_schema_freshness() -> bool:
    fresh_render = dump_schema.render_schema()
    try:
        is_current = dump_schema.OUT_PATH.read_text(encoding="utf-8") == fresh_render
    except FileNotFoundError:
        is_current = False
    if is_current:
        print(f"Passed: Database schema freshness ({dump_schema.OUT_PATH})")
        return True
    print(
        f"Database schema is missing or stale: {dump_schema.OUT_PATH}. "
        f"Run {SCHEMA_FIX_COMMAND} to regenerate it.",
        file=sys.stderr,
    )
    return False


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
            if path.is_file():
                failures.append(f"unexpected workflow command: {path.relative_to(REPO_ROOT)}")
    json_paths = (
        Path("package.json"), Path("frontend/package.json"),
        Path("experiments/package.json"), Path("experiments/package-lock.json"),
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
    print("Passed: Workflow contract")
    return True


ALL_TAGS = {"lint", "python", "frontend", "e2e", "build", "storybook"}
EPILOG = """\
categories:
  lint        Ruff, ESLint, Prettier checks, source size
  python      pytest (project + workflow)
  frontend    Vitest component tests
  e2e         Playwright end-to-end tests
  build       frontend build, Storybook build
  storybook   Storybook interaction and accessibility tests
"""


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="check.py",
        description="Run the repository's complete local quality suite.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = p.add_argument_group("mode")
    g.add_argument("--fix", action="store_true",
                   help="run formatters and regenerate schema before verification")
    g.add_argument("--list", action="store_true",
                   help="print all verification steps and exit")
    g.add_argument("-q", "--quiet", action="store_true",
                   help="suppress passing step output")
    g = p.add_argument_group("step selection")
    g.add_argument("--only", metavar="NAME",
                   help="run only steps whose name matches NAME (case-insensitive)")
    g.add_argument("--from", dest="from_step", metavar="NAME",
                   help="start from step matching NAME (inclusive, case-insensitive)")
    g.add_argument("--no-build", action="store_true",
                   help="skip build steps (Frontend build, Storybook build)")
    g = p.add_argument_group("category selectors (combine to expand)")
    for tag in sorted(ALL_TAGS):
        g.add_argument(f"--{tag}", action="store_true", dest=f"tag_{tag}",
                       help=f"run only {tag} steps")
    return p


def _filter_steps(
    steps: list[Step], *, only: str | None, from_step: str | None,
    selected_tags: set[str], no_build: bool,
) -> list[Step]:
    result = list(steps)
    if only:
        lower = only.lower()
        return [s for s in result if lower in s.name.lower()]
    if from_step:
        lower = from_step.lower()
        for i, s in enumerate(result):
            if lower in s.name.lower():
                result = result[i:]
                break
        else:
            result = []
    if selected_tags:
        result = [s for s in result if s.tag in selected_tags]
    if no_build:
        result = [s for s in result if s.tag != "build"]
    return result


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    if args.list:
        for step in VERIFY:
            tag = f" [{step.tag}]" if step.tag else ""
            print(f"  {step.name}{tag}")
        return 0
    show_success = not args.quiet
    failed = False
    if args.fix:
        print("== Fix phase (explicit deterministic formatters) ==", flush=True)
        for step in FIX_STEPS:
            if not run_step(step, show_success=False):
                failed = True
        if not regenerate_schema():
            failed = True
    else:
        print("== Read-only mode (no formatters or generated files) ==", flush=True)
    selected_tags = {tag for tag in ALL_TAGS if getattr(args, f"tag_{tag}", False)}
    verify_steps = _filter_steps(
        VERIFY, only=args.only, from_step=args.from_step,
        selected_tags=selected_tags, no_build=args.no_build,
    )
    print("== Verify phase ==", flush=True)
    if not check_schema_freshness():
        failed = True
    if not check_workflow_contract():
        failed = True
    for step in verify_steps:
        if not run_step(step, show_success=show_success):
            failed = True
    if not selected_tags and not args.only and not args.from_step and not args.no_build:
        if not run_storybook_validation():
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
