from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from chess_move_trainer.database import cli as database_cli


ROOT = Path(__file__).parents[3]
FLOWCHART_PATHS = (
    ROOT / "docs/flowcharts/database-toolchain.md",
    ROOT / "docs/flowcharts/database-operator-journeys.md",
    ROOT / "docs/flowcharts/README.md",
)
COMMANDS = (
    "refresh",
    "verify",
    "snapshot",
    "candidate",
    "replace",
    "rollback",
)
REQUIRED_TERMS = (
    "opening-only",
    "replacement-ready",
    "stockfish bulk --preset initial",
    "20 common",
    "five technical",
    "serial",
    "no queue rows",
    "API-03",
    "games acquire",
    "never acquire from the network",
    "WAL-safe",
    "rolling",
    "exclusive",
    "atomic",
    "idempotent",
    "old database",
    "cutover",
)
STALE_TERMS = (
    "DB-08 CLI CANDIDATE",
    "names are not yet decided",
    "names and exact shapes are not yet decided",
    "capability labels only, names unsettled",
    "recover:",
    "RECOVER[",
    "candidate discarded",
)


def test_flowcharts_match_db08_commands_and_safety_terms() -> None:
    documents = [path.read_text(encoding="utf-8") for path in FLOWCHART_PATHS]
    combined = "\n".join(documents).lower()
    toolchain = documents[0].lower()
    journeys = documents[1].lower()

    help_result = CliRunner().invoke(database_cli.app, ["rebuild", "--help"])
    assert help_result.exit_code == 0
    assert help_result.stderr == ""
    for command in COMMANDS:
        assert command in help_result.stdout
        assert f"rebuild {command}" in combined
    for term in REQUIRED_TERMS:
        assert term.lower() in combined
    for term in STALE_TERMS:
        assert term.lower() not in combined

    assert 'snapf -->|"snapshot target input to shared verifier"| ver' in toolchain
    assert (
        'ver -->|"integrity_check, foreign_key_check,<br/>exact-v1 compatibility, user_version"| snapf'
        not in toolchain
    )
    assert 'rollback -->|"1. select newest or explicit retained snapshot"| selected' in toolchain
    assert 'selected -->|"2. rollback re-verifies source<br/>through shared verifier"| ver' in toolchain
    assert 'rready -->|"3. preserve current neighbour first"| preserve' in toolchain
    assert 'preserve -->|"4. fresh verified recovery point;<br/>then atomic restore selected source"| restore' in toolchain
    assert 'restore -->|"5. restore only configured neighbour"| neighbor' in toolchain
    assert 'ver["db-08 cli<br/>rebuild verify --config path<br/>--target neighbour|candidate|snapshot<br/>snapshot target: --snapshot path"]' in toolchain

    assert 'b3 -->|"partial"| b4' in journeys
    assert 'b3 -->|"replacement-ready"| b5' in journeys
    assert 'b4 -->|"next normal idempotent<br/>rebuild candidate rerun"| b1' in journeys
    assert 'b5 -->|"optional direct initial analysis"| d1' in journeys
    assert 'a4 -->|"optional direct initial analysis"| d1' in journeys
    assert 'b5 -->|"already replacement-ready artifact"| f2' in journeys
    assert 'b5 -.->|"optional standalone snapshot"| f1' in journeys
    assert 'f2["managed candidate artifact<br/>replacement-ready outcome<br/>from journey b"]' in journeys
    assert 'f2["managed candidate artifact<br/>replacement-ready outcome<br/>from journey b"] --> f3[' in journeys
    assert 'f1 --> f3' not in journeys
    assert 'b3 --> d1' not in journeys
    assert 'b3 --> f2' not in journeys
    assert 'a2["db-08 cli<br/>rebuild verify --config path<br/>--target neighbour"]' in journeys
    assert 'b2["db-08 cli<br/>rebuild verify --config path<br/>--target candidate"]' in journeys
    assert 'rebuild verify --target neighbour' not in journeys
    assert 'rebuild verify --target candidate' not in journeys
    assert 'a3 -->|"next normal idempotent refresh"| a1' in journeys
    assert 'class a1,a2,b1,b2,f1,f3,g1 cand' in journeys
    assert 'class a3,a4,b3,b4,b5,f2,f4,start,e1,e2,e3,g2 info' in journeys
