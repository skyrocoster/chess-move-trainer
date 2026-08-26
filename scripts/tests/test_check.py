from pathlib import Path

from scripts.checks import cli, schema, steps, workflow
from scripts.checks.cli import main


def test_default_mode_is_read_only(monkeypatch, capsys) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        cli,
        "check_schema_freshness",
        lambda: calls.append("schema freshness") or True,
    )
    monkeypatch.setattr(
        cli,
        "check_workflow_contract",
        lambda: calls.append("contract") or True,
    )
    monkeypatch.setattr(
        cli,
        "check_storybook_coverage",
        lambda: calls.append("storybook coverage") or True,
    )
    monkeypatch.setattr(
        cli,
        "run_storybook_validation",
        lambda: calls.append("storybook") or True,
    )
    monkeypatch.setattr(
        cli,
        "run_step",
        lambda step, show_success: calls.append(step.name) or True,
    )

    assert main([]) == 0
    assert calls == [
        "schema freshness",
        "contract",
        *(step.name for step in steps.VERIFY),
        "storybook",
    ]
    assert "Read-only mode" in capsys.readouterr().out


def test_fix_mode_runs_fix_steps_before_verification(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        cli,
        "regenerate_schema",
        lambda: calls.append("schema regeneration") or True,
    )
    monkeypatch.setattr(
        cli,
        "check_schema_freshness",
        lambda: calls.append("schema freshness") or True,
    )
    monkeypatch.setattr(
        cli,
        "check_workflow_contract",
        lambda: calls.append("contract") or True,
    )
    monkeypatch.setattr(
        cli,
        "check_storybook_coverage",
        lambda: calls.append("storybook coverage") or True,
    )
    monkeypatch.setattr(
        cli,
        "run_storybook_validation",
        lambda: calls.append("storybook") or True,
    )
    monkeypatch.setattr(
        cli,
        "run_step",
        lambda step, show_success: calls.append(step.name) or True,
    )

    assert main(["--fix"]) == 0
    assert calls == [
        *(step.name for step in steps.FIX_STEPS),
        "schema regeneration",
        "schema freshness",
        "contract",
        *(step.name for step in steps.VERIFY),
        "storybook",
    ]


def test_storybook_coverage_requires_explicit_selector(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        cli,
        "check_schema_freshness",
        lambda: calls.append("schema freshness") or True,
    )
    monkeypatch.setattr(
        cli,
        "check_workflow_contract",
        lambda: calls.append("contract") or True,
    )
    monkeypatch.setattr(
        cli,
        "check_storybook_coverage",
        lambda: calls.append("storybook coverage") or True,
    )
    monkeypatch.setattr(
        cli,
        "run_storybook_validation",
        lambda: calls.append("storybook") or True,
    )
    monkeypatch.setattr(
        cli,
        "run_step",
        lambda step, show_success: calls.append(step.name) or True,
    )

    assert main(["--storybook"]) == 0
    assert calls == ["schema freshness", "contract", "storybook coverage"]


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
