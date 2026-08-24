from pathlib import Path

from scripts import check


def test_default_mode_is_read_only(monkeypatch, capsys) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        check,
        "check_schema_freshness",
        lambda: calls.append("schema freshness") or True,
    )
    monkeypatch.setattr(check, "check_workflow_contract", lambda: calls.append("contract") or True)
    monkeypatch.setattr(
        check,
        "run_storybook_validation",
        lambda: calls.append("storybook") or True,
    )
    monkeypatch.setattr(
        check,
        "run_step",
        lambda step, show_success: calls.append(step.name) or True,
    )

    assert check.main([]) == 0
    assert calls == [
        "schema freshness",
        "contract",
        *(step.name for step in check.VERIFY),
        "storybook",
    ]
    assert "Read-only mode" in capsys.readouterr().out


def test_fix_mode_runs_fix_steps_before_verification(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        check,
        "regenerate_schema",
        lambda: calls.append("schema regeneration") or True,
    )
    monkeypatch.setattr(
        check,
        "check_schema_freshness",
        lambda: calls.append("schema freshness") or True,
    )
    monkeypatch.setattr(check, "check_workflow_contract", lambda: calls.append("contract") or True)
    monkeypatch.setattr(
        check,
        "run_storybook_validation",
        lambda: calls.append("storybook") or True,
    )
    monkeypatch.setattr(
        check,
        "run_step",
        lambda step, show_success: calls.append(step.name) or True,
    )

    assert check.main(["--fix"]) == 0
    assert calls == [
        *(step.name for step in check.FIX_STEPS),
        "schema regeneration",
        "schema freshness",
        "contract",
        *(step.name for step in check.VERIFY),
        "storybook",
    ]


def test_schema_freshness_reports_missing_and_stale_artifacts_with_fix_guidance(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    artifact = tmp_path / "schema.txt"
    monkeypatch.setattr(check.dump_schema, "OUT_PATH", artifact)

    assert check.check_schema_freshness() is False
    missing_output = capsys.readouterr().err
    assert f"Database schema is missing or stale: {artifact}" in missing_output
    assert check.SCHEMA_FIX_COMMAND in missing_output

    artifact.write_text("stale\n", encoding="utf-8")

    assert check.check_schema_freshness() is False
    stale_output = capsys.readouterr().err
    assert f"Database schema is missing or stale: {artifact}" in stale_output
    assert check.SCHEMA_FIX_COMMAND in stale_output


def test_schema_freshness_does_not_write_artifact_or_runtime_database(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = tmp_path / "schema.txt"
    runtime_database = tmp_path / "chess_games.db"
    check.dump_schema.write_schema(artifact)
    runtime_database.write_bytes(b"runtime database sentinel")
    artifact_before = (artifact.read_bytes(), artifact.stat().st_mtime_ns)
    runtime_before = (runtime_database.read_bytes(), runtime_database.stat().st_mtime_ns)
    monkeypatch.setattr(check.dump_schema, "OUT_PATH", artifact)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("read-only freshness verification attempted a write")

    monkeypatch.setattr(check.dump_schema, "write_schema", fail_if_called)

    assert check.check_schema_freshness() is True
    assert (artifact.read_bytes(), artifact.stat().st_mtime_ns) == artifact_before
    assert (runtime_database.read_bytes(), runtime_database.stat().st_mtime_ns) == runtime_before


def test_frontmatter_check_rejects_plain_markdown(tmp_path: Path) -> None:
    path = tmp_path / "agent.md"
    path.write_text("# no frontmatter\n", encoding="utf-8")

    assert check._frontmatter_is_present(path) is False
