from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[2]
FLOWCHARTS = ROOT / "docs" / "flowcharts"
INVENTORY = FLOWCHARTS / "database-command-inventory.md"
PUBLIC_DATA_LOADING_WORKFLOWS = (
    "setup",
    "update games",
    "update openings",
)
RETIRED_DATA_LOADING_COMMANDS = (
    "games acquire",
    "games import",
    "openings acquire",
    "openings import",
    "rebuild refresh",
    "rebuild verify",
    "rebuild snapshot",
    "rebuild candidate",
    "rebuild replace",
    "rebuild rollback",
)


def test_db09_command_inventory_and_flowcharts_are_consistent() -> None:
    inventory = INVENTORY.read_text(encoding="utf-8").lower()
    assert "# db-09 direct-lifecycle command inventory" in inventory
    assert "there are exactly three public data-loading workflows" in inventory
    assert "destination is exactly `data/database/chess.db`" in inventory
    assert all(f"`{workflow}`" in inventory for workflow in PUBLIC_DATA_LOADING_WORKFLOWS)
    assert all(command not in inventory for command in RETIRED_DATA_LOADING_COMMANDS)
    assert "stockfish remains a separate analysis surface" in inventory
    assert "manual" in inventory and "rare" in inventory and "full" in inventory
    assert "old production database remains untouched" in inventory
    assert "raw game sources remain retained" in inventory
    assert "approved ten-table schema" in inventory
    assert "legacy scripts remain read-only" in inventory
    assert "no script command" in inventory
    assert all(term in inventory for term in ("wrapper", "fallback", "delegation"))
    assert "pre-application" in inventory
    assert "other files under `data/database/` are outside" in inventory

    inventory_link = "database-command-inventory.md"
    for name in ("database-toolchain.md", "database-operator-journeys.md"):
        flowchart = (FLOWCHARTS / name).read_text(encoding="utf-8").lower()
        assert inventory_link in flowchart
        assert "public data loading" in flowchart
        assert all(workflow in flowchart for workflow in PUBLIC_DATA_LOADING_WORKFLOWS)
        assert "data/database/chess.db" in flowchart
        assert "stockfish" in flowchart and "separate" in flowchart
        assert "rare" in flowchart and "rebuild" in flowchart
        assert "old production database" in flowchart
        assert "raw sources" in flowchart
        assert "approved schema" in flowchart
        assert "legacy scripts" in flowchart
        assert "application" in flowchart and "gate" in flowchart
