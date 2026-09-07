from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[2]
FLOWCHARTS = ROOT / "docs" / "flowcharts"
INVENTORY = FLOWCHARTS / "database-command-inventory.md"
SUPPORTED_COMMANDS = (
    "schema create",
    "schema inspect",
    "games acquire",
    "games import",
    "openings acquire",
    "openings import",
    "openings lookup",
    "openings replay",
    "preferred-moves list",
    "preferred-moves resolve",
    "preferred-moves set",
    "preferred-moves unset",
    "stockfish benchmark",
    "stockfish bulk",
    "stockfish worker",
    "rebuild refresh",
    "rebuild verify",
    "rebuild snapshot",
    "rebuild candidate",
    "rebuild replace",
    "rebuild rollback",
)


def test_db09_command_inventory_and_flowcharts_are_consistent() -> None:
    inventory = INVENTORY.read_text(encoding="utf-8").lower()
    assert "# db-09 package command inventory" in inventory
    assert all(command in inventory for command in SUPPORTED_COMMANDS)
    assert "scripts/" in inventory
    assert "replaced" in inventory
    assert "authority-excluded" in inventory
    assert (
        "no `scripts/` command, import, wrapper, fallback, or delegation is permitted"
        in inventory
    )

    inventory_link = "database-command-inventory.md"
    for name in ("database-toolchain.md", "database-operator-journeys.md"):
        flowchart = (FLOWCHARTS / name).read_text(encoding="utf-8").lower()
        assert "openings acquire" in flowchart
        assert inventory_link in flowchart
