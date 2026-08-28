import subprocess
from pathlib import Path

import pytest

from scripts.checks import cli, schema, steps, storybook, workflow
from scripts.checks.cli import main


def _quick_step_names() -> list[str]:
    return [name for name in cli.QUICK_NAMES if name in steps.STEP_BY_NAME]


def _patch_checks(monkeypatch, calls: list[str]) -> None:
    monkeypatch.setattr(
        cli, "check_schema_freshness", lambda: calls.append("schema freshness") or True
    )
    monkeypatch.setattr(cli, "check_workflow_contract", lambda: calls.append("contract") or True)
    monkeypatch.setattr(
        cli, "check_storybook_coverage", lambda: calls.append("storybook coverage") or True
    )
    monkeypatch.setattr(
        cli, "run_storybook_validation", lambda **kwargs: calls.append("storybook") or True
    )
    monkeypatch.setattr(
        cli,
        "run_step",
        lambda step, show_success, **kwargs: calls.append(step.name) or True,
    )
    monkeypatch.setattr(
        cli, "regenerate_schema", lambda: calls.append("schema regeneration") or True
    )


def test_default_mode_runs_quick_suite_in_order(monkeypatch, capsys) -> None:
    calls: list[str] = []
    _patch_checks(monkeypatch, calls)
    stale_removed: list[str] = []
    monkeypatch.setattr(cli, "remove_stale_failure_log", lambda: stale_removed.append("removed"))

    assert main([]) == 0
    assert calls == ["schema freshness", "contract", *_quick_step_names()]
    assert stale_removed == ["removed"]
    assert "== Verify phase ==" in capsys.readouterr().out


def test_full_mode_runs_complete_suite_in_order(monkeypatch) -> None:
    calls: list[str] = []
    _patch_checks(monkeypatch, calls)

    assert main(["--full"]) == 0

    expected: list[str] = []
    for name in cli.FULL_NAMES:
        if name == "Database schema freshness":
            expected.append("schema freshness")
        elif name == "Workflow contract":
            expected.append("contract")
        elif name == "Storybook coverage":
            expected.append("storybook coverage")
        elif name == "Storybook validation":
            expected.append("storybook")
        else:
            expected.append(name)
    assert calls == expected


def test_first_failure_stops_later_checks(monkeypatch) -> None:
    calls: list[str] = []
    _patch_checks(monkeypatch, calls)
    monkeypatch.setattr(
        cli, "run_step", lambda step, show_success, **kwargs: calls.append(step.name) or False
    )
    monkeypatch.setattr(cli, "remove_stale_failure_log", lambda: calls.append("stale removed"))

    assert main([]) == 1
    assert calls == ["schema freshness", "contract", _quick_step_names()[0]]


def test_schema_failure_stops_before_steps(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        cli, "check_schema_freshness", lambda: calls.append("schema freshness") or False
    )
    monkeypatch.setattr(cli, "check_workflow_contract", lambda: calls.append("contract") or True)
    monkeypatch.setattr(
        cli, "run_step", lambda step, show_success, **kwargs: calls.append(step.name) or True
    )

    assert main([]) == 1
    assert calls == ["schema freshness"]


def test_fix_mode_runs_fix_steps_then_quick_verification(monkeypatch) -> None:
    calls: list[str] = []
    _patch_checks(monkeypatch, calls)

    assert main(["--fix"]) == 0
    assert calls == [
        *(step.name for step in steps.FIX_STEPS),
        "schema regeneration",
        "schema freshness",
        "contract",
        *_quick_step_names(),
    ]


def test_storybook_coverage_requires_explicit_selector(monkeypatch) -> None:
    calls: list[str] = []
    _patch_checks(monkeypatch, calls)

    assert main(["--storybook"]) == 0
    assert calls == ["schema freshness", "contract", "storybook coverage"]


def test_timeout_multiplier_reaches_runners(monkeypatch) -> None:
    step_kwargs: list[dict] = []
    validation_kwargs: list[dict] = []
    monkeypatch.setattr(cli, "check_schema_freshness", lambda: True)
    monkeypatch.setattr(cli, "check_workflow_contract", lambda: True)
    monkeypatch.setattr(cli, "check_storybook_coverage", lambda: True)
    monkeypatch.setattr(
        cli,
        "run_step",
        lambda step, show_success, **kwargs: step_kwargs.append(kwargs) or True,
    )
    monkeypatch.setattr(
        cli,
        "run_storybook_validation",
        lambda **kwargs: validation_kwargs.append(kwargs) or True,
    )

    assert main(["--full", "--timeout-multiplier", "2.0"]) == 0
    assert step_kwargs
    assert all(kwargs["timeout_multiplier"] == 2.0 for kwargs in step_kwargs)
    assert validation_kwargs == [{"timeout": 600}]


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf"])
def test_timeout_multiplier_must_be_finite_and_positive(value: str) -> None:
    with pytest.raises(SystemExit):
        main(["--timeout-multiplier", value])


def test_list_shows_quick_suite_by_default(capsys) -> None:
    assert main(["--list"]) == 0
    out = capsys.readouterr().out
    for name in cli.QUICK_NAMES:
        assert name in out
    assert "End-to-end tests" not in out
    assert "Source size check [lint] (60s)" in out


def test_list_full_shows_complete_suite(capsys) -> None:
    assert main(["--list", "--full"]) == 0
    out = capsys.readouterr().out
    for name in cli.FULL_NAMES:
        assert name in out


def test_storybook_validation_runs_bounded_vitest_project(monkeypatch) -> None:
    calls: list[dict] = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def run(command, **kwargs):
        calls.append({"command": command, **kwargs})
        return Result()

    monkeypatch.setattr(storybook.subprocess, "run", run)

    assert storybook.run_storybook_validation() is True
    assert calls == [
        {
            "command": [
                "npm.cmd",
                "run",
                "test-storybook",
                "--prefix",
                "frontend",
                "--",
                "--run",
            ],
            "cwd": storybook.REPO_ROOT,
            "check": False,
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": 300,
        }
    ]


def test_storybook_validation_accepts_timeout_override(monkeypatch) -> None:
    seen: dict = {}

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def run(command, **kwargs):
        seen.update(kwargs)
        return Result()

    monkeypatch.setattr(storybook.subprocess, "run", run)

    assert storybook.run_storybook_validation(timeout=600) is True
    assert seen["timeout"] == 600


def test_schema_freshness_reports_missing_and_stale_artifacts_with_fix_guidance(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    from data.database import dump_schema

    artifact = tmp_path / "schema.txt"
    monkeypatch.setattr(dump_schema, "OUT_PATH", artifact)

    assert schema.check_schema_freshness() is False
    missing_output = capsys.readouterr().err
    assert f"Database schema is missing or stale: {artifact}" in missing_output
    assert steps.SCHEMA_FIX_COMMAND in missing_output

    artifact.write_text("stale\n", encoding="utf-8")

    assert schema.check_schema_freshness() is False
    stale_output = capsys.readouterr().err
    assert f"Database schema is missing or stale: {artifact}" in stale_output
    assert steps.SCHEMA_FIX_COMMAND in stale_output


def test_schema_freshness_does_not_write_artifact_or_runtime_database(
    tmp_path: Path, monkeypatch
) -> None:
    from data.database import dump_schema

    artifact = tmp_path / "schema.txt"
    runtime_database = tmp_path / "chess_games.db"
    dump_schema.write_schema(artifact)
    runtime_database.write_bytes(b"runtime database sentinel")
    artifact_before = (artifact.read_bytes(), artifact.stat().st_mtime_ns)
    runtime_before = (runtime_database.read_bytes(), runtime_database.stat().st_mtime_ns)
    monkeypatch.setattr(dump_schema, "OUT_PATH", artifact)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("read-only freshness verification attempted a write")

    monkeypatch.setattr(dump_schema, "write_schema", fail_if_called)

    assert schema.check_schema_freshness() is True
    assert (artifact.read_bytes(), artifact.stat().st_mtime_ns) == artifact_before
    assert (runtime_database.read_bytes(), runtime_database.stat().st_mtime_ns) == runtime_before


def test_frontmatter_check_rejects_plain_markdown(tmp_path: Path) -> None:
    path = tmp_path / "agent.md"
    path.write_text("# no frontmatter\n", encoding="utf-8")

    assert workflow._frontmatter_is_present(path) is False


# --- Stage 2: runner mechanics (timeouts, tree stop, artifacts, fail-fast) ---


class _RecordingPopen:
    """Fake Popen that records the timeout passed to communicate()."""

    def __init__(self, command, **kwargs):
        self.command = command
        self.kwargs = kwargs
        self.returncode = 0
        self.stdout = ""
        self.stderr = ""
        self.communicate_timeouts: list[float | None] = []

    def communicate(self, timeout=None):
        self.communicate_timeouts.append(timeout)
        return self.stdout, self.stderr

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        return self.returncode


def _install_recording_popen(monkeypatch) -> list[_RecordingPopen]:
    created: list[_RecordingPopen] = []

    def popen(command, **kwargs):
        process = _RecordingPopen(command, **kwargs)
        created.append(process)
        return process

    monkeypatch.setattr(steps.subprocess, "Popen", popen)
    return created


def test_run_step_passes_step_timeout_times_multiplier_to_communicate(monkeypatch) -> None:
    created = _install_recording_popen(monkeypatch)

    step = steps.Step(name="Fake step", command=["fake"], timeout=42)
    assert steps.run_step(step, show_success=False, timeout_multiplier=2.0) is True
    assert created[0].communicate_timeouts == [84.0]


def test_run_step_defaults_timeout_when_step_has_none(monkeypatch) -> None:
    created = _install_recording_popen(monkeypatch)

    step = steps.Step(name="Fake step", command=["fake"])
    assert steps.run_step(step, show_success=False) is True
    assert created[0].communicate_timeouts == [steps.DEFAULT_TIMEOUT_SECONDS]


class _TimeoutPopen:
    """Fake Popen whose communicate() always raises TimeoutExpired."""

    def __init__(self, command, **kwargs):
        self.command = command
        self.kwargs = kwargs
        self.pid = 424242

    def communicate(self, timeout=None):
        raise subprocess.TimeoutExpired("fake", timeout)

    def poll(self):
        return None

    def wait(self, timeout=None):
        return None


def test_timeout_reports_timeout_line_and_stops_process_tree(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    monkeypatch.setattr(steps.subprocess, "Popen", _TimeoutPopen)
    stopped: list[object] = []
    monkeypatch.setattr(steps, "stop_process_tree", lambda process: stopped.append(process))
    log_path = tmp_path / "check-failure.log"
    monkeypatch.setattr(steps, "FAILURE_LOG_PATH", log_path)

    step = steps.Step(name="Slow step", command=["slow"], timeout=5)
    assert steps.run_step(step, show_success=True) is False
    assert len(stopped) == 1
    out = capsys.readouterr()
    assert "START Slow step" in out.out
    assert "TIMEOUT Slow step" in out.out
    assert "limit 5s" in out.out
    assert log_path.is_file()


def test_failure_writes_failure_log_and_prints_excerpt(monkeypatch, capsys, tmp_path: Path) -> None:
    log_path = tmp_path / "check-failure.log"
    monkeypatch.setattr(steps, "FAILURE_LOG_PATH", log_path)

    class _FailingPopen:
        def __init__(self, command, **kwargs):
            self.returncode = 1
            self.stdout = "first line\nsecond line\n"
            self.stderr = "boom detail\n"

        def communicate(self, timeout=None):
            return self.stdout, self.stderr

    monkeypatch.setattr(steps.subprocess, "Popen", _FailingPopen)

    step = steps.Step(name="Failing step", command=["fail"], timeout=5)
    assert steps.run_step(step, show_success=False) is False
    captured = capsys.readouterr()
    assert "FAIL Failing step" in captured.out
    assert "--- excerpt (tail) ---" in captured.err
    assert "boom detail" in captured.err
    body = log_path.read_text(encoding="utf-8")
    assert "=== check: Failing step ===" in body
    assert "second line" in body
    assert "boom detail" in body


def test_remove_stale_failure_log_deletes_existing_file(tmp_path: Path, monkeypatch) -> None:
    log_path = tmp_path / "check-failure.log"
    log_path.write_text("stale", encoding="utf-8")
    monkeypatch.setattr(steps, "FAILURE_LOG_PATH", log_path)

    steps.remove_stale_failure_log()
    assert not log_path.exists()


def test_remove_stale_failure_log_is_noop_when_absent(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(steps, "FAILURE_LOG_PATH", tmp_path / "check-failure.log")
    steps.remove_stale_failure_log()


def test_failure_in_middle_stops_later_checks_and_skips_stale_removal(monkeypatch) -> None:
    calls: list[str] = []
    _patch_checks(monkeypatch, calls)
    quick_names = _quick_step_names()
    failing = quick_names[3]

    def run_step(step, show_success, **kwargs):
        calls.append(step.name)
        return step.name != failing

    monkeypatch.setattr(cli, "run_step", run_step)
    monkeypatch.setattr(cli, "remove_stale_failure_log", lambda: calls.append("stale removed"))

    assert main([]) == 1
    assert calls == ["schema freshness", "contract", *quick_names[:4]]
    assert "stale removed" not in calls
