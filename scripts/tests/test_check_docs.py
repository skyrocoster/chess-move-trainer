from pathlib import Path

from scripts import check_docs

CANONICAL_AGENT = """---
description: Luna case-worker for assessment.
mode: subagent
model: openai/gpt-5.6-luna
---

You are the resumable Luna case-worker.
A fresh Luna session may begin later.
"""

EXPECTED_FLASH = """---
description: DeepSeek Flash case-worker for assessment.
mode: subagent
model: deepseek/deepseek-v4-flash
---

You are the resumable DeepSeek Flash case-worker.
A fresh DeepSeek Flash session may begin later.
"""


def test_generate_flash_agent_replaces_model_and_references() -> None:
    assert check_docs.generate_flash_agent(CANONICAL_AGENT) == EXPECTED_FLASH


def test_sync_caseworker_agents_reports_missing_canonical(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(check_docs, "LUNA_AGENT", tmp_path / "missing-luna.md")
    monkeypatch.setattr(check_docs, "FLASH_AGENT", tmp_path / "flash.md")

    findings = check_docs.sync_caseworker_agents(write=False)

    assert len(findings) == 1
    assert "canonical Luna caseworker agent is missing" in findings[0].message


def test_sync_caseworker_agents_reports_missing_flash(tmp_path: Path, monkeypatch) -> None:
    luna = tmp_path / "luna.md"
    luna.write_text(CANONICAL_AGENT, encoding="utf-8")
    flash = tmp_path / "flash.md"
    monkeypatch.setattr(check_docs, "LUNA_AGENT", luna)
    monkeypatch.setattr(check_docs, "FLASH_AGENT", flash)

    findings = check_docs.sync_caseworker_agents(write=False)

    assert len(findings) == 1
    assert "DeepSeek Flash caseworker agent is missing" in findings[0].message


def test_sync_caseworker_agents_reports_out_of_sync_flash(tmp_path: Path, monkeypatch) -> None:
    luna = tmp_path / "luna.md"
    luna.write_text(CANONICAL_AGENT, encoding="utf-8")
    flash = tmp_path / "flash.md"
    flash.write_text("stale content", encoding="utf-8")
    monkeypatch.setattr(check_docs, "LUNA_AGENT", luna)
    monkeypatch.setattr(check_docs, "FLASH_AGENT", flash)

    findings = check_docs.sync_caseworker_agents(write=False)

    assert len(findings) == 1
    assert "out of sync" in findings[0].message


def test_sync_caseworker_agents_passes_when_in_sync(tmp_path: Path, monkeypatch) -> None:
    luna = tmp_path / "luna.md"
    luna.write_text(CANONICAL_AGENT, encoding="utf-8")
    flash = tmp_path / "flash.md"
    flash.write_text(EXPECTED_FLASH, encoding="utf-8")
    monkeypatch.setattr(check_docs, "LUNA_AGENT", luna)
    monkeypatch.setattr(check_docs, "FLASH_AGENT", flash)

    findings = check_docs.sync_caseworker_agents(write=False)

    assert findings == []


def test_sync_caseworker_agents_write_generates_flash(tmp_path: Path, monkeypatch) -> None:
    luna = tmp_path / "luna.md"
    luna.write_text(CANONICAL_AGENT, encoding="utf-8")
    flash = tmp_path / "flash.md"
    monkeypatch.setattr(check_docs, "LUNA_AGENT", luna)
    monkeypatch.setattr(check_docs, "FLASH_AGENT", flash)

    findings = check_docs.sync_caseworker_agents(write=True)

    assert findings == []
    assert flash.read_text(encoding="utf-8") == EXPECTED_FLASH
