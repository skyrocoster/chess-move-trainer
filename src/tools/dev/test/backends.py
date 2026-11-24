"""Command builders for the four test runners.

Each builder returns one :class:`Command` with a finite hard deadline. The
runner executes the commands serially and persists their artifacts under the
run directory.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from tools.dev.config import E2E_DIR, FRONTEND_DIR, PYTEST_ROOTS, REPOSITORY_ROOT, python
from tools.dev.test.discovery import TestCase, discover_test_files
from tools.dev.test.selection import Command

# Windows cmd.exe fails above 8191 characters; leave room for the launcher prefix.
_MAX_COMMAND_CHARS = 6000
_PYTEST_TIMEOUT = 900
_VITEST_TIMEOUT = 1800
_VITEST_API_TIMEOUT = 600
_PLAYWRIGHT_TIMEOUT = 1800


def commands_for(cases: list[TestCase], report_dir: Path) -> list[Command]:
    """Return the ordered bounded commands for a resolved selection."""
    commands: list[Command] = []
    backend = [case for case in cases if case.backend == "pytest"]
    if backend:
        commands.append(_pytest(backend, report_dir))
    unit = [case for case in cases if case.backend == "vitest"]
    if unit:
        commands.extend(_vitest(unit, report_dir))
    api = [case for case in cases if case.backend == "vitest-api"]
    if api:
        commands.extend(_vitest_api(api, report_dir))
    e2e = [case for case in cases if case.backend == "playwright"]
    if e2e:
        commands.append(_playwright(e2e, report_dir))
    return commands


# Opt-in real-data tests only run when these variables are set; the real-data profile sets them.
REAL_DATA_ENVIRONMENT = {
    "CHESS_RUN_API_BENCHMARK_REAL": "1",
    "CHESS_RUN_REAL_DB_SMOKE": "1",
    "CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE": "1",
}


def _pytest(cases: list[TestCase], report_dir: Path) -> Command:
    selections = sorted({case.selector for case in cases})
    all_python = {
        relative
        for relative in discover_test_files(REPOSITORY_ROOT)
        if relative.endswith(".py")
    }
    selected_sources = {case.source for case in cases}
    arguments = [
        python(),
        "-m",
        "pytest",
        "-q",
        "--tb=short",
        "-p",
        "no:cacheprovider",
        "-W",
        "error",
    ]
    if selected_sources == all_python:
        arguments.extend(PYTEST_ROOTS)
    elif len(cases) > 80:
        # A large domain/file selection is still safely expressed by file path.
        arguments.extend(sorted(selected_sources))
    else:
        arguments.extend(selections)
    arguments.append(f"--junitxml={report_dir / 'pytest.xml'}")
    environment = dict(REAL_DATA_ENVIRONMENT) if any(case.real_data for case in cases) else {}
    return Command(
        label=f"pytest ({len(cases)} case(s))",
        backend="pytest",
        args=tuple(arguments),
        timeout=_PYTEST_TIMEOUT,
        layer="backend",
        env=environment,
        artifacts={"junit": "pytest.xml"},
        speed="fast",
    )


def chunk_selectors(
    prefix: list[str], selectors: list[str], limit: int = _MAX_COMMAND_CHARS
) -> list[list[str]]:
    """Split file selectors so each command line stays under ``limit`` characters.

    Windows ``cmd.exe`` rejects lines over 8191 characters. Selectors keep
    their order; every selector lands in exactly one chunk, and a short
    selection yields a single chunk.
    """
    base = len(subprocess.list2cmdline(prefix))
    chunks: list[list[str]] = []
    current: list[str] = []
    length = base
    for selector in selectors:
        added = len(subprocess.list2cmdline([selector])) + 1
        if current and length + added > limit:
            chunks.append(current)
            current, length = [], base
        current.append(selector)
        length += added
    if current or not chunks:
        chunks.append(current)
    return chunks


def _chunked_junit_commands(
    cases: list[TestCase],
    report_dir: Path,
    *,
    npm_args: list[str],
    artifact_stem: str,
    title: str,
    **command_fields,
) -> list[Command]:
    sources = sorted({case.selector for case in cases})
    count = len(cases)

    def prefix_for(artifact: str) -> list[str]:
        return [
            *npm_args,
            "--reporter=junit",
            f"--outputFile={report_dir / artifact}",
        ]

    # Chunk against the longest artifact name so every chunk is safely sized.
    chunks = chunk_selectors(prefix_for(f"{artifact_stem}-99.xml"), sources)
    commands: list[Command] = []
    for index, chunk in enumerate(chunks, start=1):
        artifact = f"{artifact_stem}.xml" if len(chunks) == 1 else f"{artifact_stem}-{index}.xml"
        if len(chunks) == 1:
            label = f"{title} ({count} group(s))"
            chunk_selectors_field: tuple[str, ...] = ()
        else:
            members = set(chunk)
            label = (
                f"{title} ({sum(c.selector in members for c in cases)} group(s),"
                f" chunk {index}/{len(chunks)})"
            )
            chunk_selectors_field = tuple(chunk)
        commands.append(
            Command(
                label=label,
                args=tuple([*prefix_for(artifact), *chunk]),
                artifacts={"junit": artifact},
                selectors=chunk_selectors_field,
                **command_fields,
            )
        )
    return commands


def _vitest(cases: list[TestCase], report_dir: Path) -> list[Command]:
    return _chunked_junit_commands(
        cases,
        report_dir,
        npm_args=["npx", "vitest", "run", "--project=unit"],
        artifact_stem="vitest",
        title="Vitest unit",
        backend="vitest",
        timeout=_VITEST_TIMEOUT,
        layer="frontend",
        cwd="frontend",
        speed="fast",
    )


def _vitest_api(cases: list[TestCase], report_dir: Path) -> list[Command]:
    return _chunked_junit_commands(
        cases,
        report_dir,
        npm_args=["npx", "vitest", "run", "--config", "frontend/vitest.api.config.ts"],
        artifact_stem="vitest-api",
        title="Vitest API",
        backend="vitest-api",
        timeout=_VITEST_API_TIMEOUT,
        layer="frontend-api",
        cwd=".",
        speed="focused",
    )


def _playwright(cases: list[TestCase], report_dir: Path) -> Command:
    selectors = sorted({_selector(case.selector) for case in cases})
    arguments = [
        "npx",
        "playwright",
        "test",
        "--config",
        "tests/e2e/playwright.config.ts",
        "--reporter=json",
        *selectors,
    ]
    return Command(
        label=f"Playwright e2e ({len(cases)} case(s))",
        backend="playwright",
        args=tuple(arguments),
        timeout=_PLAYWRIGHT_TIMEOUT,
        layer="e2e",
        cwd=".",
        env={
            "PLAYWRIGHT_JSON_OUTPUT_NAME": str(report_dir / "playwright.json"),
        },
        artifacts={"playwright": "playwright.json"},
        speed="focused",
    )


def _selector(selector: str) -> str:
    """Return a forward-slash Playwright filter.

    Playwright treats arguments as regular expressions matched against test
    files. Repository-relative selectors work from the repository-root cwd, while an
    absolute Windows path contains backslashes and cannot be matched safely.
    """
    return selector.replace("\\", "/")


def playwright_executable() -> Path:
    """Return the root Playwright launcher used for discovery."""
    name = "playwright.cmd" if os.name == "nt" else "playwright"
    return REPOSITORY_ROOT / "node_modules" / ".bin" / name


def e2e_dir() -> Path:
    """Return the Playwright test directory (kept for callers and tests)."""
    return E2E_DIR


def frontend_dir() -> Path:
    """Return the frontend workspace directory."""
    return FRONTEND_DIR
