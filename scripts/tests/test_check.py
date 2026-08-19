from pathlib import Path

from scripts import check


def test_default_mode_is_read_only(monkeypatch, capsys) -> None:
    calls: list[str] = []

    monkeypatch.setattr(check, "check_workflow_contract", lambda: calls.append("contract") or True)
    monkeypatch.setattr(
        check,
        "run_step",
        lambda step, show_success: calls.append(step.name) or True,
    )

    assert check.main([]) == 0
    assert calls == ["contract", *(step.name for step in check.VERIFY)]
    assert "Read-only mode" in capsys.readouterr().out


def test_fix_mode_runs_fix_steps_before_verification(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(check, "check_workflow_contract", lambda: calls.append("contract") or True)
    monkeypatch.setattr(
        check,
        "run_step",
        lambda step, show_success: calls.append(step.name) or True,
    )

    assert check.main(["--fix"]) == 0
    assert calls == [
        *(step.name for step in check.FIX_STEPS),
        "contract",
        *(step.name for step in check.VERIFY),
    ]


def test_frontmatter_check_rejects_plain_markdown(tmp_path: Path) -> None:
    path = tmp_path / "agent.md"
    path.write_text("# no frontmatter\n", encoding="utf-8")

    assert check._frontmatter_is_present(path) is False
