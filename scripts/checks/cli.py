"""Command-line interface for the check suite."""

from __future__ import annotations

import functools
import math
import time
from collections.abc import Iterable

from scripts.checks.coverage import check_storybook_coverage
from scripts.checks.schema import check_schema_freshness, regenerate_schema
from scripts.checks.steps import (
    ALL_TAGS,
    FIX_STEPS,
    STEP_BY_NAME,
    Step,
    remove_stale_failure_log,
    run_step,
    step_timeout,
)
from scripts.checks.storybook import run_storybook_validation
from scripts.checks.workflow import check_workflow_contract

STORYBOOK_VALIDATION_TIMEOUT_SECONDS = 300

EPILOG = """\
categories:
  lint        Ruff, ESLint, Prettier, TypeScript checks, source size
  python      pytest (project + workflow)
  frontend    Vitest component tests (unit project)
  e2e         Playwright end-to-end tests
  build       frontend build, Storybook build
  storybook   Storybook coverage checks
"""

QUICK_NAMES = [
    "Database schema freshness",
    "Workflow contract",
    "Source size check",
    "Ruff lint check",
    "Ruff format check",
    "Prettier check",
    "ESLint check",
    "TypeScript type check",
    "Python tests",
    "Workflow tests",
    "Frontend tests",
]

FULL_NAMES = [
    *QUICK_NAMES,
    "Frontend build",
    "Storybook build",
    "Storybook coverage",
    "Storybook validation",
    "End-to-end tests",
]


def _build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog="check.py",
        description="Run the repository's quality suite (quick by default; --full for everything).",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = p.add_argument_group("mode")
    g.add_argument(
        "--fix",
        action="store_true",
        help="run formatters and regenerate schema before verification",
    )
    g.add_argument(
        "--full", action="store_true", help="run the complete suite (builds, Storybook, E2E)"
    )
    g.add_argument("--list", action="store_true", help="print the effective check list and exit")
    g.add_argument(
        "--timeout-multiplier",
        type=float,
        default=1.0,
        metavar="FLOAT",
        help="scale every per-check timeout by FLOAT (must be finite and greater than zero)",
    )
    g.add_argument("-q", "--quiet", action="store_true", help="suppress START lines")
    g = p.add_argument_group("step selection")
    g.add_argument(
        "--only", metavar="NAME", help="run only steps whose name matches NAME (case-insensitive)"
    )
    g.add_argument(
        "--from",
        dest="from_step",
        metavar="NAME",
        help="start from step matching NAME (inclusive, case-insensitive)",
    )
    g.add_argument(
        "--no-build", action="store_true", help="skip build steps (Frontend build, Storybook build)"
    )
    g = p.add_argument_group("category selectors (combine to expand)")
    for tag in sorted(ALL_TAGS):
        help_text = (
            "run Storybook coverage checks" if tag == "storybook" else f"run only {tag} steps"
        )
        g.add_argument(f"--{tag}", action="store_true", dest=f"tag_{tag}", help=help_text)
    return p


def _filter_steps(
    steps: list[Step],
    *,
    only: str | None,
    from_step: str | None,
    selected_tags: set[str],
    no_build: bool,
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


def _print_list(full: bool) -> None:
    names = FULL_NAMES if full else QUICK_NAMES
    for name in names:
        step = STEP_BY_NAME.get(name)
        if step is None:
            print(f"  {name} (in-process)")
        else:
            tag = f" [{step.tag}]" if step.tag else ""
            print(f"  {name}{tag} ({step_timeout(step):.0f}s)")


def _run_in_process(name: str, fn, show_success: bool, *, timeout: int | None = None) -> bool:
    if show_success:
        print(f"START {name}", flush=True)
    started = time.monotonic()
    ok = fn(timeout=timeout) if timeout is not None else fn()
    duration = time.monotonic() - started
    print(f"{'PASS' if ok else 'FAIL'} {name} ({duration:.1f}s)", flush=True)
    return ok


def _build_entries(args, show_success: bool, multiplier: float) -> list[tuple[str, object]]:
    suite_names = FULL_NAMES if args.full else QUICK_NAMES
    selected_tags = {tag for tag in ALL_TAGS if getattr(args, f"tag_{tag}", False)}
    unfiltered = not args.only and not args.from_step and not selected_tags and not args.no_build
    ordered_steps = [STEP_BY_NAME[name] for name in suite_names if name in STEP_BY_NAME]
    allowed_names = {
        s.name
        for s in _filter_steps(
            ordered_steps,
            only=args.only,
            from_step=args.from_step,
            selected_tags=selected_tags,
            no_build=args.no_build,
        )
    }
    names = list(suite_names)
    if args.tag_storybook and "Storybook coverage" not in names:
        names.append("Storybook coverage")
    entries: list[tuple[str, object]] = []
    for name in names:
        if name == "Database schema freshness":
            runner = functools.partial(_run_in_process, name, check_schema_freshness, show_success)
        elif name == "Workflow contract":
            runner = functools.partial(_run_in_process, name, check_workflow_contract, show_success)
        elif name == "Storybook coverage":
            if not (args.tag_storybook or (args.full and unfiltered)):
                continue
            runner = functools.partial(
                _run_in_process, name, check_storybook_coverage, show_success
            )
        elif name == "Storybook validation":
            if not (args.full and unfiltered):
                continue
            timeout = int(STORYBOOK_VALIDATION_TIMEOUT_SECONDS * multiplier)
            runner = functools.partial(
                _run_in_process, name, run_storybook_validation, show_success, timeout=timeout
            )
        else:
            step = STEP_BY_NAME.get(name)
            if step is None or name not in allowed_names:
                continue
            runner = functools.partial(run_step, step, show_success, timeout_multiplier=multiplier)
        entries.append((name, runner))
    return entries


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not math.isfinite(args.timeout_multiplier) or args.timeout_multiplier <= 0:
        parser.error("--timeout-multiplier must be finite and greater than zero")
    if args.list:
        _print_list(args.full)
        return 0
    show_success = not args.quiet
    multiplier = args.timeout_multiplier
    if args.fix:
        print("== Fix phase (explicit deterministic formatters) ==", flush=True)
        for step in FIX_STEPS:
            if not run_step(step, show_success=show_success, timeout_multiplier=multiplier):
                return 1
        if not regenerate_schema():
            return 1
    print("== Verify phase ==", flush=True)
    for name, run in _build_entries(args, show_success, multiplier):
        if not run():
            return 1
    remove_stale_failure_log()
    return 0
