"""Selection, profiles, safety preflight and command construction."""

from __future__ import annotations

import pytest

from tools.dev.test import profiles
from tools.dev.test.backends import commands_for
from tools.dev.test.discovery import TestCase
from tools.dev.test.selection import SelectionError, preflight, resolve


def _case(
    *,
    layer: str = "backend",
    backend: str = "pytest",
    domain: str = "tooling",
    subdomain: str | None = None,
    source: str = "backend/tests/tooling/test_x.py",
    selector: str = "backend/tests/tooling/test_x.py::test_one",
    fixture: str = "none",
    real_data: bool = False,
) -> TestCase:
    name = selector.rsplit("::", 1)[-1] if "::" in selector else "group"
    identifier = f"{layer}.{domain}.test-x::{name}"
    return TestCase(
        id=identifier,
        backend=backend,
        layer=layer,
        domain=domain,
        subdomain=subdomain,
        source=source,
        selector=selector,
        display=selector,
        fixture=fixture,
        speed="fast",
        real_data=real_data,
    )


def test_resolve_exact_group_and_zero_match():
    cases = [_case(), _case(selector="backend/tests/tooling/test_x.py::test_two")]
    assert len(resolve(cases=cases, test_id=cases[0].id)) == 1
    assert len(resolve(cases=cases, test_id="backend.tooling.test-x")) == 2
    with pytest.raises(SelectionError, match="No test matches"):
        resolve(cases=cases, test_id="backend.tooling.missing")
    with pytest.raises(SelectionError, match="Select tests"):
        resolve(cases=cases)


def test_domain_and_layer_selection():
    cases = [_case(), _case(layer="frontend", backend="vitest", domain="design-system")]
    assert len(resolve(cases=cases, domain="tooling")) == 1
    assert len(resolve(cases=cases, layer="frontend")) == 1
    assert len(resolve(cases=cases, domain="design-system", layer="frontend")) == 1


def test_real_data_requires_explicit_opt_in():
    cases = [_case(real_data=True, fixture="real-db")]
    with pytest.raises(SelectionError, match="real-data"):
        preflight(cases, allow_real_data=False)
    preflight(cases, allow_real_data=True)


def test_profiles_are_disjoint_and_explicit():
    backend = _case()
    frontend = _case(layer="frontend", backend="vitest", domain="design-system")
    api = _case(
        layer="frontend-api",
        backend="vitest-api",
        source="frontend/src/api/healthClient.test.ts",
    )
    e2e = _case(layer="e2e", backend="playwright", domain="health")
    real = _case(
        real_data=True,
        fixture="real-db",
        source="backend/tests/features/position_training_requirements/test_real_database.py",
    )
    cases = [backend, frontend, api, e2e, real]

    quick = profiles.select(cases, "quick")
    assert {case.backend for case in quick} == {"pytest", "vitest"}
    assert api not in quick
    assert e2e not in quick
    assert real not in quick

    full = profiles.select(cases, "full")
    assert api in full
    assert e2e in full
    assert real not in full

    assert profiles.select(cases, "e2e") == [e2e]
    assert profiles.select(cases, "real-data") == [real]
    assert set(profiles.PROFILES) == {"quick", "smoke", "full", "e2e", "real-data"}


def test_smoke_profile_is_a_small_offline_cross_section():
    backend = _case(source="backend/tests/features/health/test_health.py")
    frontend = _case(
        layer="frontend",
        backend="vitest",
        source="frontend/src/features/status/StatusView.test.tsx",
    )
    unrelated = _case(source="backend/tests/features/api_cache/test_read_cache.py")
    e2e = _case(layer="e2e", backend="playwright", source="tests/e2e/status-page.spec.ts")
    assert profiles.select([backend, frontend, unrelated, e2e], "smoke") == [backend, frontend]


def test_commands_are_bounded_and_grouped(tmp_path):
    pytest_case = _case()
    vitest_case = _case(
        layer="frontend",
        backend="vitest",
        domain="design-system",
        source="frontend/src/features/design-system/Button.test.tsx",
        selector="src/features/design-system/Button.test.tsx",
    )
    playwright_case = _case(
        layer="e2e",
        backend="playwright",
        domain="health",
        source="tests/e2e/status-page.spec.ts",
        selector="tests/e2e/status-page.spec.ts:10",
    )
    commands = commands_for([pytest_case, vitest_case, playwright_case], report_dir=tmp_path)
    assert [command.backend for command in commands] == ["pytest", "vitest", "playwright"]
    for command in commands:
        assert command.timeout > 0
    assert any("--junitxml" in argument for argument in commands[0].args)
    assert "--project=unit" in commands[1].args
    assert commands[1].cwd == "frontend"
    assert commands[1].args[:3] == ("npx", "vitest", "run")
    assert "tests/e2e/playwright.config.ts" in commands[2].args
    assert commands[2].env["PLAYWRIGHT_JSON_OUTPUT_NAME"].endswith("playwright.json")


def test_api_tests_run_from_the_repository_root_with_the_api_config(tmp_path):
    api = _case(
        layer="frontend-api",
        backend="vitest-api",
        source="frontend/src/api/healthClient.test.ts",
        selector="src/api/healthClient.test.ts",
    )
    (command,) = commands_for([api], tmp_path)
    assert command.cwd == "."
    assert "frontend/vitest.api.config.ts" in command.args
    assert command.timeout > 0


def _vitest_cases(count: int) -> list[TestCase]:
    return [
        _case(
            layer="frontend",
            backend="vitest",
            source=f"frontend/src/features/area/__tests__/long-file-name-{n:03d}.test.tsx",
            selector=f"src/features/area/__tests__/long-file-name-{n:03d}.test.tsx",
        )
        for n in range(count)
    ]


def test_short_vitest_selection_is_one_unchanged_command(tmp_path):
    cases = _vitest_cases(3)
    (command,) = commands_for(cases, tmp_path)
    assert command.selectors == ()
    assert command.artifacts == {"junit": "vitest.xml"}
    assert command.args[-3:] == tuple(sorted(case.selector for case in cases))
    assert command.label == "Vitest unit (3 group(s))"


def test_long_vitest_selection_is_chunked_without_losing_files(tmp_path):
    import subprocess

    cases = _vitest_cases(164)
    commands = commands_for(cases, tmp_path)
    assert len(commands) > 1
    for command in commands:
        assert len(subprocess.list2cmdline(list(command.args))) < 7000
        assert "--project=unit" in command.args
    assert len({c.artifacts["junit"] for c in commands}) == len(commands)
    run = [selector for command in commands for selector in command.selectors]
    assert run == sorted(case.selector for case in cases)
    for command in commands:
        assert command.args[-len(command.selectors) :] == command.selectors
