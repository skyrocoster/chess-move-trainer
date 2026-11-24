from __future__ import annotations

import json

from tools.dev.checks import full_process as full_test_process
from tools.dev.checks.full_process import Step, StepResult


def _step(name: str) -> Step:
    return Step(name, ("fake", name), 10)


def test_inventory_covers_all_test_build_and_quality_layers() -> None:
    steps = full_test_process.build_steps()
    names = [step.name for step in steps]

    assert names == [
        "Compose configuration",
        "Python dependency integrity",
        "Node dependency integrity",
        "TypeScript",
        "Python tests including opt-in real tests",
        "Frontend unit tests",
        "Development service preflight",
        "Frontend real-backend API tests",
        "Frontend production build",
        "Playwright end-to-end tests",
        "Source size limits",
        "Ruff lint",
        "ESLint",
        "Ruff formatting",
        "Prettier formatting",
    ]
    python_tests = steps[names.index("Python tests including opt-in real tests")]
    assert "--maxfail=1" in python_tests.command
    assert python_tests.environment["CHESS_RUN_API_BENCHMARK_REAL"] == "1"
    assert python_tests.environment["CHESS_RUN_REAL_DB_SMOKE"] == "1"
    assert python_tests.environment["CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE"] == "1"
    assert "--max-warnings" in steps[names.index("ESLint")].command
    assert "--max-failures=1" in steps[names.index("Playwright end-to-end tests")].command


def test_warning_output_fails_a_successful_process() -> None:
    step = _step("Example")

    result = full_test_process.classify_result(step, 0, "build warnings: chunk is large", "")

    assert result.passed is False
    assert result.reason.startswith("warning output:")


def test_documented_zero_and_engine_warning_lines_are_ignored() -> None:
    output = "0 warnings\nnpm warn EBADENGINE Unsupported engine\n"

    assert full_test_process.warning_lines(output, "") == []


def test_suite_stops_at_failure_and_resumes_at_that_check(tmp_path, monkeypatch) -> None:
    steps = [_step("first"), _step("second"), _step("third")]
    state_directory = tmp_path / "state"
    monkeypatch.setattr(full_test_process, "STATE_DIRECTORY", state_directory)
    monkeypatch.setattr(full_test_process, "STATE_PATH", state_directory / "state.json")
    monkeypatch.setattr(
        full_test_process,
        "FAILURE_LOG_PATH",
        state_directory / "latest-failure.log",
    )
    first_calls: list[str] = []

    def fail_second(step: Step) -> StepResult:
        first_calls.append(step.name)
        return StepResult(step.name != "second", "test result")

    monkeypatch.setattr(full_test_process, "execute_step", fail_second)

    assert full_test_process.run_suite(steps, 0) == 1
    assert first_calls == ["first", "second"]
    state = json.loads(full_test_process.STATE_PATH.read_text(encoding="utf-8"))
    assert state["next_step"] == "second"
    assert full_test_process._load_resume_index(steps) == 1

    resumed_calls: list[str] = []
    monkeypatch.setattr(
        full_test_process,
        "execute_step",
        lambda step: resumed_calls.append(step.name) or StepResult(True, "test result"),
    )

    assert full_test_process.run_suite(steps, full_test_process._load_resume_index(steps)) == 0
    assert resumed_calls == ["second", "third"]
    assert not full_test_process.STATE_PATH.exists()


def test_from_step_requires_one_unambiguous_match() -> None:
    steps = [_step("Ruff lint"), _step("Ruff formatting"), _step("ESLint")]

    assert full_test_process._matching_index(steps, "Ruff lint") == 0
    assert full_test_process._matching_index(steps, "format") == 1

    try:
        full_test_process._matching_index(steps, "Ruff")
    except ValueError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("ambiguous names must fail")


def test_inventory_has_no_storybook_or_powershell_and_is_finite() -> None:
    steps = full_test_process.build_steps()
    names = [step.name for step in steps]

    assert len(set(names)) == len(names)
    for step in steps:
        assert step.timeout_seconds > 0
        text = " ".join((step.name, *step.command)).lower()
        assert "storybook" not in text
        assert "powershell" not in text
        assert "dev.ps1" not in text


def test_preflight_uses_sg_check_services() -> None:
    steps = full_test_process.build_steps()
    preflight = next(step for step in steps if step.name == "Development service preflight")

    assert preflight.command[-3:] == ("tools.dev", "check", "services") or (
        preflight.command[-2:] == ("check", "services")
    )


def test_only_step_runs_one_check_and_leaves_checkpoint(tmp_path, monkeypatch, capsys) -> None:
    state_directory = tmp_path / "state"
    monkeypatch.setattr(full_test_process, "STATE_DIRECTORY", state_directory)
    monkeypatch.setattr(full_test_process, "STATE_PATH", state_directory / "state.json")
    monkeypatch.setattr(
        full_test_process, "FAILURE_LOG_PATH", state_directory / "latest-failure.log"
    )
    monkeypatch.setattr(
        full_test_process, "build_steps", lambda: [_step("alpha"), _step("beta")]
    )
    calls: list[str] = []
    monkeypatch.setattr(
        full_test_process,
        "execute_step",
        lambda step: calls.append(step.name) or StepResult(True, "ok"),
    )

    full_test_process.run_full_process(only_step="beta")

    assert calls == ["beta"]
    assert not (state_directory / "state.json").exists()
    capsys.readouterr()


def test_style_steps_run_after_behaviour_and_formatting_last() -> None:
    names = [step.name for step in full_test_process.build_steps()]
    style = ["Source size limits", "Ruff lint", "ESLint", "Ruff formatting", "Prettier formatting"]
    formatting = ["Ruff formatting", "Prettier formatting"]
    behaviour = [name for name in names if name not in style]

    first_style = min(names.index(name) for name in style)
    assert all(names.index(name) < first_style for name in behaviour)
    assert set(names[-2:]) == set(formatting)
