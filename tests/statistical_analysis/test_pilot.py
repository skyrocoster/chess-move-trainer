import json
import sqlite3
from pathlib import Path

import pytest

from chess_move_trainer.statistical_analysis.artifacts import file_digest
from chess_move_trainer.statistical_analysis.audit import build_audit
from chess_move_trainer.statistical_analysis.extraction import extract
from chess_move_trainer.statistical_analysis.full_run import prepare_full_run
from chess_move_trainer.statistical_analysis.pilot import create_pilot
from chess_move_trainer.statistical_analysis.registry import freeze_registry
from chess_move_trainer.statistical_analysis.reporting import report
from chess_move_trainer.statistical_analysis.runner import run_questions
from chess_move_trainer.statistical_analysis.snapshot import create_snapshot
from chess_move_trainer.statistical_analysis.snapshot_pilot import create_snapshot_pilot

from .conftest import add_game

CATALOGUE = Path("docs/grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md")


def _full_run(source_database, tmp_path):
    add_game(source_database, 1, color="white", analysis=True)
    add_game(source_database, 2, color="white", analysis=True)
    add_game(source_database, 3, color="black", analysis=False)
    directory = tmp_path / "complete-source"
    create_snapshot(source_database, directory)
    freeze_registry(CATALOGUE, directory / "registry.json")
    extract(directory)
    return directory


def test_pilot_is_seeded_stratified_unweighted_and_non_destructive(source_database, tmp_path):
    source = _full_run(source_database, tmp_path)
    records_hash = file_digest(source / "records.db")
    first_path = tmp_path / "pilot-one"
    second_path = tmp_path / "pilot-two"

    first = create_pilot(source, first_path, max_games=2, seed=41)
    second = create_pilot(source, second_path, max_games=2, seed=41)

    assert first["status"] == "complete"
    assert first["sampled_games"] == 2
    assert first["identity"] == second["identity"]
    assert len(first["strata"]) == 2
    assert all(row["sample_games"] == 1 for row in first["strata"])
    assert first["weights_applied_to_outputs"] is False
    assert file_digest(source / "records.db") == records_hash
    with sqlite3.connect(first_path / "records.db") as connection:
        assert connection.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM moves").fetchone()[0] == 10
        sample_ids = [row[0] for row in connection.execute("SELECT id FROM games ORDER BY id")]
    with sqlite3.connect(second_path / "records.db") as connection:
        assert sample_ids == [
            row[0] for row in connection.execute("SELECT id FROM games ORDER BY id")
        ]

    audit = build_audit(first_path)
    assert audit["pilot"]["identity"] == first["identity"]
    assert {row["claim_type"] for row in audit["inventory"]} == {
        "pilot_sample_unweighted_descriptive_only"
    }
    review = report(first_path).read_text(encoding="utf-8")
    findings = json.loads((first_path / "findings.json").read_text(encoding="utf-8"))
    assert findings["status"] == "pilot_sample_descriptive_only"
    assert findings["associations"] == []
    assert "pilot-sample descriptions" in review
    assert "sampling weights applied: False" in review
    assert "Clean full-run reset" in (first_path / "PILOT.md").read_text(encoding="utf-8")
    diagnostic = run_questions(
        first_path,
        identifiers=[json.loads((first_path / "registry.json").read_text())["questions"][0]["id"]],
        diagnostic=True,
        replicates=2,
    )
    first_result = next(iter(diagnostic["results"].values()))
    assert diagnostic["mode"] == "exploratory_pilot_diagnostic_not_confirmatory"
    assert diagnostic["pilot_identity"] == first["identity"]
    assert "pilot_sample_not_promotable" in first_result["gate_failures"]

    with pytest.raises(FileExistsError, match="must be new"):
        create_pilot(source, first_path, max_games=2, seed=41)


def test_pilot_cap_must_cover_each_stratum_and_full_reset_starts_clean(
    source_database, tmp_path
):
    source = _full_run(source_database, tmp_path)
    too_small = tmp_path / "too-small-pilot"
    with pytest.raises(ValueError, match="non-empty strata"):
        create_pilot(source, too_small, max_games=1, seed=1)
    assert not too_small.exists()

    records_hash = file_digest(source / "records.db")
    fresh = tmp_path / "prepared-full-run"
    preparation = prepare_full_run(source, fresh)
    assert preparation["status"] == "ready_for_full_extraction"
    assert not (fresh / "records.db").exists()
    assert not (fresh / "diagnostics.json").exists()
    assert not (fresh / "audit.json").exists()
    assert file_digest(source / "records.db") == records_hash
    assert file_digest(fresh / "snapshot.db") == file_digest(source / "snapshot.db")
    reset_notes = (fresh / "FULL_RUN_RESET.md").read_text(encoding="utf-8")
    assert "rerun `extract` on this same" in reset_notes
    assert "never-used output path" in reset_notes

    full_extraction = extract(fresh)
    assert full_extraction["status"] == "complete"
    audit = build_audit(fresh)
    assert audit["total_games"] == 3
    assert "pilot" not in audit
    with pytest.raises(FileExistsError, match="must be new"):
        prepare_full_run(source, fresh)


def test_snapshot_pilot_samples_before_replay_and_resumes_only_sampled_games(
    source_database, tmp_path
):
    add_game(source_database, 1, color="white", analysis=True)
    add_game(source_database, 2, color="white", analysis=True)
    add_game(source_database, 3, color="black", analysis=False)
    source = tmp_path / "frozen-source"
    create_snapshot(source_database, source)
    freeze_registry(CATALOGUE, source / "registry.json")
    source_hash = file_digest(source / "snapshot.db")

    fresh_full = tmp_path / "clean-full-from-snapshot-only"
    preparation = prepare_full_run(source, fresh_full)
    assert preparation["status"] == "ready_for_full_extraction"
    assert not (fresh_full / "records.db").exists()
    assert not (fresh_full / "diagnostics.json").exists()

    pilot_path = tmp_path / "snapshot-pilot"
    pilot = create_snapshot_pilot(source, pilot_path, max_games=2, seed=71)
    assert pilot["status"] == "ready_for_extraction"
    assert pilot["sampled_games"] == 2
    assert pilot["source_total_games"] == 3
    assert pilot["weights_applied_to_outputs"] is False
    assert not (pilot_path / "records.db").exists()
    assert file_digest(source / "snapshot.db") == source_hash
    with pytest.raises(ValueError, match="pilot sample"):
        prepare_full_run(pilot_path, tmp_path / "incorrect-full-from-pilot")
    with sqlite3.connect(pilot_path / "snapshot.db") as connection:
        assert connection.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0] == 2
        assert connection.execute("PRAGMA foreign_key_check").fetchone() is None

    first_batch = extract(pilot_path, max_games=1)
    assert first_batch["status"] == "run_incomplete"
    assert json.loads((pilot_path / "pilot.json").read_text())["status"] == "ready_for_extraction"
    with pytest.raises(ValueError, match="complete extraction"):
        build_audit(pilot_path)
    resumed = extract(pilot_path)
    assert resumed["status"] == "complete"
    assert resumed["pilot_identity"] == pilot["identity"]
    assert json.loads((pilot_path / "pilot.json").read_text())["status"] == "complete"
    audit = build_audit(pilot_path)
    assert audit["total_games"] == 2
    assert audit["pilot"]["identity"] == pilot["identity"]

    registry = json.loads((pilot_path / "registry.json").read_text())
    diagnostic = run_questions(
        pilot_path,
        identifiers=[registry["questions"][0]["id"]],
        diagnostic=True,
        replicates=2,
    )
    assert diagnostic["pilot_identity"] == pilot["identity"]
    result = next(iter(diagnostic["results"].values()))
    assert "pilot_sample_not_promotable" in result["gate_failures"]
