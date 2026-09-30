import json
import sqlite3

import pytest

from chess_move_trainer.statistical_analysis.artifacts import Budget, file_digest
from chess_move_trainer.statistical_analysis.extraction import extract
from chess_move_trainer.statistical_analysis.snapshot import create_snapshot, verify_snapshot

from .conftest import add_game


def test_snapshot_is_consistent_readonly_and_immutable(source_database, tmp_path):
    add_game(source_database)
    before = file_digest(source_database)
    directory = tmp_path / "run"
    manifest = create_snapshot(source_database, directory)
    assert manifest["status"] == "complete"
    assert file_digest(source_database) == before
    add_game(source_database, 2)
    with sqlite3.connect(directory / "snapshot.db") as connection:
        assert connection.execute("SELECT COUNT(*) FROM datasource_game").fetchone()[0] == 1
    assert verify_snapshot(directory, Budget(5)) == manifest
    with pytest.raises(FileExistsError):
        create_snapshot(source_database, directory)
    with sqlite3.connect(directory / "snapshot.db") as connection:
        connection.execute("UPDATE datasource_game SET dg_trainer_rating=2000")
    with pytest.raises(ValueError, match="contents changed"):
        verify_snapshot(directory, Budget(5))


def test_extract_resume_mixed_tiers_and_populations(source_database, tmp_path):
    add_game(source_database)
    add_game(source_database, 2, color="black")
    directory = tmp_path / "run"
    create_snapshot(source_database, directory)
    frozen = file_digest(directory / "snapshot.db")
    assert extract(directory, max_games=1)["status"] == "run_incomplete"
    assert extract(directory)["status"] == "complete"
    assert extract(directory)["processed_games"] == 2
    with sqlite3.connect(directory / "records.db") as connection:
        records = [
            json.loads(r[0])
            for r in connection.execute("SELECT record FROM moves ORDER BY game, ply")
        ]
        assert len(records) == 10
        assert {r["population"] for r in records} == {"learner", "opponent"}
        assert records[0]["loss_units"] == 400
        assert records[0]["severe"] == 1
        assert records[0]["before_analysis"]["quality"] == "browser"
        assert records[0]["after_analysis"]["quality"] == "tool"
        assert records[0]["fen_after"].endswith("0 1")
        assert records[4]["fen_after"].endswith("3 3")
    assert file_digest(directory / "snapshot.db") == frozen


def test_bad_game_is_quarantined_atomically(source_database, tmp_path):
    add_game(source_database)
    with sqlite3.connect(source_database) as connection:
        connection.execute("UPDATE derived_game_position SET dgp_halfmove_clock=5 WHERE dgp_ply=3")
    directory = tmp_path / "run"
    create_snapshot(source_database, directory)
    extract(directory)
    with sqlite3.connect(directory / "records.db") as connection:
        assert connection.execute("SELECT status FROM games").fetchone()[0] == "excluded"
        assert connection.execute("SELECT COUNT(*) FROM moves").fetchone()[0] == 0


def test_missing_and_invalid_analysis_are_not_imputed(source_database, tmp_path):
    add_game(source_database, analysis=False)
    directory = tmp_path / "run"
    create_snapshot(source_database, directory)
    extract(directory)
    with sqlite3.connect(directory / "records.db") as connection:
        record = json.loads(connection.execute("SELECT record FROM moves LIMIT 1").fetchone()[0])
    assert record["loss"] is None
    assert record["issues"] == ["missing_before_analysis", "missing_after_analysis"]


@pytest.mark.parametrize("seconds", [0, -1, float("inf"), float("nan"), True])
def test_budget_rejects_unbounded_values(seconds):
    with pytest.raises(ValueError):
        Budget(seconds)
