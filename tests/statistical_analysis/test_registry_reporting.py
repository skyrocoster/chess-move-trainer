import json
from pathlib import Path

import pytest

from chess_move_trainer.statistical_analysis.audit import build_audit
from chess_move_trainer.statistical_analysis.extraction import extract
from chess_move_trainer.statistical_analysis.registry import (
    Question,
    catalogue_inventory,
    freeze_registry,
    questions,
    validate_question,
)
from chess_move_trainer.statistical_analysis.reporting import report
from chess_move_trainer.statistical_analysis.runner import run_questions
from chess_move_trainer.statistical_analysis.snapshot import create_snapshot

from .conftest import add_game

CATALOGUE = Path("docs/grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md")


def test_inventory_preserves_all_bullets_and_stable_ids():
    inventory = catalogue_inventory(CATALOGUE)
    text = CATALOGUE.read_text(encoding="utf-8")
    section = text.split("## Candidate learner-move analyses", 1)[1].split(
        "## Reliability and interpretation hazards", 1
    )[0]
    assert len(inventory) == sum(line.startswith("- ") for line in section.splitlines())
    assert len(inventory) > 200
    assert len({row["id"] for row in inventory}) == len(inventory)
    assert any(row["status"] == "data_unavailable" for row in inventory)
    assert any(row["status"] == "definition_blocked" for row in inventory)
    assert len({q.id for q in questions()}) == len(questions())


def test_future_adjustment_rejected():
    q = Question("leak", "Q01", "learner", "capture", True, "loss", adjustment=("game_result",))
    with pytest.raises(ValueError, match="leakage"):
        validate_question(q)


def test_complete_small_review_package(source_database, tmp_path):
    add_game(source_database)
    add_game(source_database, 2, analysis=False)
    directory = tmp_path / "run"
    create_snapshot(source_database, directory)
    registry = freeze_registry(CATALOGUE, directory / "registry.json")
    with pytest.raises(FileExistsError):
        freeze_registry(CATALOGUE, directory / "registry.json")
    extract(directory)
    audit = build_audit(directory)
    assert audit["total_games"] == 2 and audit["excluded_games"] == 0
    learner_pieces = [
        r for r in audit["inventory"] if r["feature"] == "piece" and r["population"] == "learner"
    ]
    assert sum(r["count"] for r in learner_pieces) == 6
    assert sum(r["share_all_moves"] for r in learner_pieces) == pytest.approx(1)
    with pytest.raises(ValueError, match="calibration"):
        run_questions(directory)
    ledger = run_questions(directory, identifiers=[registry["questions"][0]["id"]], diagnostic=True)
    assert ledger["status"] == "run_incomplete"
    assert len(ledger["results"]) == 1
    assert len(ledger["corrected"]) == registry["family_size"]
    assert all(row["status"] != "supported" for row in ledger["corrected"].values())
    assert "No association is promoted" in report(directory).read_text()
    findings = json.loads((directory / "findings.json").read_text())
    assert findings["associations"] == []


def test_incomplete_extraction_cannot_report(source_database, tmp_path):
    add_game(source_database)
    add_game(source_database, 2)
    directory = tmp_path / "run"
    create_snapshot(source_database, directory)
    extract(directory, max_games=1)
    with pytest.raises(ValueError, match="complete extraction"):
        build_audit(directory)
