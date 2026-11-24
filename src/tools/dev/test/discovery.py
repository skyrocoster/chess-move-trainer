"""Discover selectable test units and attach catalogue metadata.

Pytest cases come from ``pytest --collect-only`` and Playwright cases from
``playwright test --list``. Vitest is discovered as a file group:
its runner does not expose a bounded, dependable list command on this
project, and a file group is a first-class ``sg test`` selection anyway.

Discovery is cached under the ignored ``build/cache/`` tree behind a content
fingerprint. ``list``/``show``/``catalog`` never run a test, build, export or
start a development service.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from tools.dev.config import CACHE_DIR, PYTEST_ROOTS, REPOSITORY_ROOT, python
from tools.dev.test.catalog import Catalog

DISCOVERY_TIMEOUT_SECONDS = 300
CACHE_SCHEMA = 1
CACHE_PATH = CACHE_DIR / "test-discovery.json"

# Files outside the test sources that decide which parametrized cases pytest
# generates. Their paths and mtimes join the cache fingerprint, so adding,
# removing or editing one invalidates the cache. Add a glob here when a test
# parametrizes over files it does not live next to.
DISCOVERY_EXTRA_INPUT_GLOBS = ("backend/tests/**/conftest.py", "tests/**/conftest.py")

_E2E_CONFIG = "tests/e2e/playwright.config.ts"
_DEFAULT_SPEED = {
    "backend": "fast",
    "frontend": "fast",
    "frontend-api": "focused",
    "e2e": "focused",
}


@dataclass(frozen=True)
class TestCase:
    """One selectable test unit with its catalogue metadata."""

    __test__ = False  # never collect this data class as a pytest test

    id: str
    backend: str
    layer: str
    domain: str
    subdomain: str | None
    source: str
    selector: str
    display: str
    fixture: str
    speed: str
    real_data: bool = False
    manual: bool = False
    needs_services: bool = False
    tags: tuple[str, ...] = ()
    available: bool = True


@dataclass
class DiscoveryResult:
    """All discovered units plus non-fatal notes and real problems."""

    cases: list[TestCase] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    def add(self, case: TestCase) -> None:
        self.cases.append(case)


def slugify(name: str) -> str:
    """Return a lowercase kebab-case slug for a file or case name."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", name)
    return re.sub(r"[^a-z0-9]+", "-", spaced.lower()).strip("-")


def case_id(layer: str, domain_path: str, source: str, case_name: str) -> str:
    """Return the stable logical id for a case."""
    return f"{layer}.{domain_path}.{slugify(Path(source).stem)}::{case_name}"


def group_id(layer: str, domain_path: str, source: str) -> str:
    """Return the stable logical id for a file group."""
    return f"{layer}.{domain_path}.{slugify(Path(source).stem)}"


def discover_test_files(root: Path = REPOSITORY_ROOT) -> list[str]:
    """Return every test or story source that must carry catalogue metadata."""
    files: list[Path] = []
    for python_root in PYTEST_ROOTS:
        directory = root / python_root
        if directory.is_dir():
            files.extend(
                path
                for path in sorted(directory.rglob("test_*.py"))
                if "__pycache__" not in path.parts and "e2e" not in path.relative_to(root).parts
            )
    frontend = root / "frontend" / "src"
    if frontend.is_dir():
        for pattern in ("*.test.ts", "*.test.tsx", "*.test.mjs"):
            files.extend(
                path for path in sorted(frontend.rglob(pattern)) if "__pycache__" not in path.parts
            )
    e2e = root / "tests" / "e2e"
    if e2e.is_dir():
        files.extend(sorted(e2e.glob("*.spec.ts")))
    return [_relative(root, path) for path in sorted(set(files))]


def discover(
    catalog: Catalog,
    root: Path = REPOSITORY_ROOT,
    *,
    with_pytest: bool = True,
    with_playwright: bool = True,
    use_cache: bool = True,
) -> DiscoveryResult:
    """Discover units from every requested runner and attach catalogue metadata."""
    cacheable = use_cache and with_pytest and with_playwright and root == REPOSITORY_ROOT
    if cacheable:
        cached = _load_cache(catalog, root)
        if cached is not None:
            return cached
    result = DiscoveryResult()
    if with_pytest:
        _discover_pytest(catalog, root, result)
    _discover_frontend_groups(catalog, root, result)
    if with_playwright:
        _discover_playwright(catalog, root, result)
    if cacheable and not result.problems:
        # A runner failure depends on files outside the fingerprint (for example
        # product imports), so a transient failure must not be cached.
        _write_cache(catalog, root, result)
    return result


def discovery_fingerprint(catalog: Catalog, root: Path = REPOSITORY_ROOT) -> str:
    """Return a fingerprint of every input that shapes discovery."""
    hasher = hashlib.sha256()
    inputs: list[Path] = [
        catalog.path,
        root / "pyproject.toml",
        Path(__file__),
        Path(__file__).with_name("catalog.py"),
    ]
    for relative in discover_test_files(root):
        inputs.append(root / relative)
    for pattern in DISCOVERY_EXTRA_INPUT_GLOBS:
        inputs.extend(root.glob(pattern))
    for path in sorted(set(inputs)):
        try:
            stat = path.stat()
        except OSError:
            continue
        relative = _relative(root, path) if path.is_relative_to(root) else str(path)
        hasher.update(f"{relative}|{stat.st_size}|{stat.st_mtime_ns}\n".encode())
    hasher.update(f"pytest={Path(python()).is_file()}\n".encode())
    hasher.update(f"playwright={(root / 'node_modules/.bin/playwright').exists()}\n".encode())
    return hasher.hexdigest()


def _load_cache(catalog: Catalog, root: Path) -> DiscoveryResult | None:
    try:
        payload = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("schema") != CACHE_SCHEMA:
        return None
    if payload.get("problems"):
        # Never replay a failed discovery: the failure may depend on product
        # files that the fingerprint does not cover.
        return None
    if payload.get("fingerprint") != discovery_fingerprint(catalog, root):
        return None
    try:
        cases = []
        for raw in payload["cases"]:
            data = dict(raw)
            data["tags"] = tuple(data.get("tags", []))
            cases.append(TestCase(**data))
        return DiscoveryResult(
            cases=cases,
            notes=list(payload.get("notes", [])),
            problems=list(payload.get("problems", [])),
        )
    except (KeyError, TypeError):
        return None


def _write_cache(catalog: Catalog, root: Path, result: DiscoveryResult) -> None:
    payload = {
        "schema": CACHE_SCHEMA,
        "fingerprint": discovery_fingerprint(catalog, root),
        "cases": [
            {
                "id": case.id,
                "backend": case.backend,
                "layer": case.layer,
                "domain": case.domain,
                "subdomain": case.subdomain,
                "source": case.source,
                "selector": case.selector,
                "display": case.display,
                "fixture": case.fixture,
                "speed": case.speed,
                "real_data": case.real_data,
                "manual": case.manual,
                "needs_services": case.needs_services,
                "tags": list(case.tags),
                "available": case.available,
            }
            for case in result.cases
        ],
        "notes": result.notes,
        "problems": result.problems,
    }
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary = CACHE_PATH.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(payload), encoding="utf-8")
        os.replace(temporary, CACHE_PATH)
    except OSError:
        return


def validate_catalog_files(catalog: Catalog, root: Path = REPOSITORY_ROOT) -> list[str]:
    """Return catalogue assignment problems for every known test source file."""
    return catalog.validate(discover_test_files(root))


def _relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _metadata(catalog: Catalog, relative: str, result: DiscoveryResult):
    metadata = catalog.domain_for_file(relative)
    if metadata is None:
        result.problems.append(f"{relative}: no catalogue domain for this test file")
        return None
    if metadata.layer == "unknown":
        result.problems.append(f"{relative}: could not derive an execution layer")
        return None
    return metadata


def _discover_pytest(catalog: Catalog, root: Path, result: DiscoveryResult) -> None:
    interpreter = python()
    if not Path(interpreter).is_file():
        result.notes.append("pytest discovery unavailable: the project .venv is missing")
        return
    node_ids, error = _collect_pytest(interpreter, root)
    if error is not None:
        result.problems.append(f"pytest discovery failed: {error}")
        return
    for node_id in sorted(node_ids):
        source, _, case_name = node_id.partition("::")
        if not case_name:
            result.problems.append(f"{node_id}: unparsable pytest node id")
            continue
        relative = _relative(root, root / source)
        metadata = _metadata(catalog, relative, result)
        if metadata is None:
            continue
        result.add(
            TestCase(
                id=case_id(metadata.layer, metadata.domain_path, relative, case_name),
                backend="pytest",
                layer=metadata.layer,
                domain=metadata.domain,
                subdomain=metadata.subdomain,
                source=relative,
                selector=node_id,
                display=node_id,
                fixture=metadata.fixture,
                speed=_DEFAULT_SPEED.get(metadata.layer, "fast"),
                real_data=metadata.fixture == "real-db",
                tags=metadata.tags,
            )
        )


def _is_node_id(line: str) -> bool:
    return "::" in line and line.startswith(tuple(f"{prefix}/" for prefix in PYTEST_ROOTS))


def _collect_pytest(interpreter: str, root: Path) -> tuple[set[str], str | None]:
    command = [
        interpreter,
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "-p",
        "no:cacheprovider",
        "-p",
        "tools.dev.test.collect_plugin",
        *PYTEST_ROOTS,
    ]
    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = (
        str(root / "src") + os.pathsep + existing if existing else str(root / "src")
    )
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            env=environment,
            capture_output=True,
            text=True,
            timeout=DISCOVERY_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return set(), str(error)
    output = completed.stdout + completed.stderr
    node_ids = {line.strip() for line in output.splitlines() if _is_node_id(line.strip())}
    if completed.returncode != 0:
        return set(), _pytest_failure_detail(output, completed.returncode)
    if not node_ids and "no tests ran" not in output:
        return set(), "collection produced no node ids"
    return node_ids, None


def _pytest_failure_detail(output: str, returncode: int) -> str:
    """Return the most useful line from a failed pytest collection.

    Collected node ids are printed to the same stream before the error section,
    and a node id can contain ``error`` in its name. Prefer pytest's own ``E``
    diagnostic or ``ERROR`` summary line and never report a node id as the
    failure.
    """
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for prefix in ("E ", "ERROR "):
        for line in lines:
            if line.startswith(prefix):
                return line
    for line in lines:
        if _is_node_id(line):
            continue
        if "error" in line.lower():
            return line
    return next(
        (line for line in lines if not _is_node_id(line)),
        f"exit code {returncode}",
    )


def _discover_frontend_groups(catalog: Catalog, root: Path, result: DiscoveryResult) -> None:
    for relative in discover_test_files(root):
        if not relative.startswith("frontend/src/"):
            continue
        if not (
            relative.endswith(".test.ts")
            or relative.endswith(".test.tsx")
            or relative.endswith(".test.mjs")
        ):
            continue
        metadata = _metadata(catalog, relative, result)
        if metadata is None:
            continue
        if metadata.layer == "frontend-api":
            backend = "vitest-api"
        else:
            backend = "vitest"
        result.add(
            TestCase(
                id=group_id(metadata.layer, metadata.domain_path, relative),
                backend=backend,
                layer=metadata.layer,
                domain=metadata.domain,
                subdomain=metadata.subdomain,
                source=relative,
                selector=relative.removeprefix("frontend/"),
                display=relative,
                fixture=metadata.fixture,
                speed=_DEFAULT_SPEED.get(metadata.layer, "fast"),
                needs_services=backend == "vitest-api",
                tags=metadata.tags,
            )
        )


def _discover_playwright(catalog: Catalog, root: Path, result: DiscoveryResult) -> None:
    executable = (
        root / "node_modules" / ".bin" / ("playwright.cmd" if os.name == "nt" else "playwright")
    )
    if not executable.exists():
        result.notes.append("Playwright discovery unavailable: run `npm ci` at the repository root")
        return
    command = [str(executable), "test", "--config", _E2E_CONFIG, "--list", "--reporter=json"]
    if os.name == "nt":
        command = ["cmd", "/c", *command]
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=DISCOVERY_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        result.problems.append(f"Playwright discovery failed: {error}")
        return
    output = completed.stdout
    start = output.find("{")
    if completed.returncode != 0 or start < 0:
        detail = (output + completed.stderr).strip().splitlines()
        result.problems.append(
            "Playwright discovery failed: "
            + (detail[0] if detail else f"exit code {completed.returncode}")
        )
        return
    try:
        payload = json.loads(output[start:])
    except json.JSONDecodeError as error:
        result.problems.append(f"Playwright discovery JSON was invalid: {error}")
        return
    seen: dict[str, int] = {}
    for suite in payload.get("suites", []):
        _playwright_suite(catalog, root, suite, seen, result, ())


def _playwright_suite(
    catalog: Catalog,
    root: Path,
    suite: dict,
    seen: dict[str, int],
    result: DiscoveryResult,
    parents: tuple[str, ...],
) -> None:
    title = suite.get("title", "")
    chain = parents + ((title,) if title else ())
    for spec in suite.get("specs", []):
        filename = spec.get("file") or ""
        if not filename:
            continue
        relative = f"tests/e2e/{filename}"
        metadata = _metadata(catalog, relative, result)
        if metadata is None:
            continue
        full_title = " > ".join(chain + (spec.get("title", ""),))
        base = group_id(metadata.layer, metadata.domain_path, relative)
        slug = slugify(spec.get("title", "")) or "case"
        case_name = slug
        seen[base] = seen.get(base, 0) + 1
        if any(
            case.id == f"{base}::{case_name}" for case in result.cases if case.source == relative
        ):
            case_name = f"{slug}#{seen[base]}"
        result.add(
            TestCase(
                id=f"{base}::{case_name}",
                backend="playwright",
                layer=metadata.layer,
                domain=metadata.domain,
                subdomain=metadata.subdomain,
                source=relative,
                selector=f"tests/e2e/{filename}:{spec.get('line', 0)}",
                display=full_title,
                fixture=metadata.fixture,
                speed="focused",
                needs_services=True,
                tags=metadata.tags,
            )
        )
    for child in suite.get("suites", []):
        _playwright_suite(catalog, root, child, seen, result, chain)


def summarize(problems: list[str], notes: list[str]) -> None:
    """Print discovery problems and notes, and fail on real problems."""
    from tools.dev.console import echo, fail

    for note in notes:
        echo(f"Note: {note}", err=True)
    if problems:
        for problem in problems:
            echo(f"Problem: {problem}", err=True)
        fail(f"Test catalogue validation failed with {len(problems)} problem(s).")
