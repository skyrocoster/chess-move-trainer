from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

from scripts.stockfish_analysis import analyze_positions


def test_schema_cli_initializes_and_reports_only_explicitly(tmp_path: Path) -> None:
    database = tmp_path / "existing.db"
    sqlite3.connect(database).close()

    assert analyze_positions.main(["--db", str(database), "--init-schema"]) == 0
    assert analyze_positions.report_schema(database) == 1


def test_schema_cli_report_refuses_missing_database_without_creating_it(tmp_path: Path) -> None:
    database = tmp_path / "missing.db"

    assert analyze_positions.main(["--db", str(database), "--report-schema"]) == 1
    assert not database.exists()


def test_schema_cli_import_and_help_are_side_effect_free(tmp_path: Path) -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "stockfish_analysis"
        / "analyze_positions.py"
    )
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--init-schema" in result.stdout
    assert list(tmp_path.iterdir()) == []
