"""Command-line interface for the check suite."""

from __future__ import annotations

from collections.abc import Iterable

from scripts.checks.coverage import check_storybook_coverage
from scripts.checks.schema import check_schema_freshness, regenerate_schema
from scripts.checks.steps import (
    ALL_TAGS,
    FIX_STEPS,
    VERIFY,
    Step,
    run_step,
)
from scripts.checks.storybook import run_storybook_validation
from scripts.checks.workflow import check_workflow_contract

EPILOG = """\
categories:
  lint        Ruff, ESLint, Prettier checks, source size
  python      pytest (project + workflow)
  frontend    Vitest component tests
  e2e         Playwright end-to-end tests
  build       frontend build, Storybook build
  storybook   Storybook coverage checks
"""


def _build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog="check.py",
        description="Run the repository's complete local quality suite.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = p.add_argument_group("mode")
    g.add_argument(
        "--fix",
        action="store_true",
        help="run formatters and regenerate schema before verification",
    )
    g.add_argument("--list", action="store_true", help="print all verification steps and exit")
    g.add_argument("-q", "--quiet", action="store_true", help="suppress passing step output")
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
        VERIFY,
        only=args.only,
        from_step=args.from_step,
        selected_tags=selected_tags,
        no_build=args.no_build,
    )
    print("== Verify phase ==", flush=True)
    if not check_schema_freshness():
        failed = True
    if not check_workflow_contract():
        failed = True
    if args.tag_storybook:
        check_storybook_coverage()
    for step in verify_steps:
        if not run_step(step, show_success=show_success):
            failed = True
    if not selected_tags and not args.only and not args.from_step and not args.no_build:
        if not run_storybook_validation():
            failed = True
    return 1 if failed else 0
