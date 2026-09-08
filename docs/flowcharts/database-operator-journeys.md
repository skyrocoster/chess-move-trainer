# Database operator journeys — direct setup and updates

> **Decision support only.** These journeys show the confirmed current DB-09 lifecycle. The
> historical DB-08/DB-08A database-file operations are not supported current journeys.

The companion page [`database-toolchain.md`](database-toolchain.md) shows the internal data flow
and retained boundaries. The durable command inventory is
[`database-command-inventory.md`](database-command-inventory.md).

## Journeys

```mermaid
flowchart TD
    START(("Start"))

    subgraph A["A - First setup"]
        A1["Check fixed path<br/>data/database/chess.db"] --> A2{"Fixed file absent?"}
        A2 -->|"no"| A3["Clear failure<br/>existing file is preserved"]
        A2 -->|"yes"| A4["PUBLIC DATA LOADING<br/>setup"]
        A4 --> A5["Create schema; load complete base games<br/>and latest valid five-file openings"]
        A5 --> A6["Create normalized and derived rows<br/>then run quick local checks"]
        A6 --> A7["One long-lived fixed database"]
        A5 -->|"failure after creation"| A8["Remove only the database<br/>created by this setup invocation"]
    end

    subgraph B["B - Direct incremental game update"]
        B1["Saved monthly files<br/>only fetch ledger"] --> B2["PUBLIC DATA LOADING<br/>update games"]
        B2 --> B3["Refetch newest saved month<br/>fill missing months through current month"]
        B3 --> B4["Validate and process months independently"]
        B4 --> B5["Persist new/corrected valid games directly<br/>by Chess.com game ID; retain omissions"]
        B4 --> B6["Skip malformed, illegal, or unsupported games<br/>individually and report reasons"]
        B5 --> B7["Quick local checks and meaningful result"]
    end

    subgraph C["C - Complete latest opening update"]
        C1["Latest upstream a.tsv through e.tsv<br/>no configured commit/version"] --> C2["PUBLIC DATA LOADING<br/>update openings"]
        C2 --> C3["Stage and validate all five files"]
        C3 --> C4{"Complete valid set?"}
        C4 -->|"no"| C5["Preserve retained source set<br/>and current catalogue"]
        C4 -->|"yes"| C6["Publish catalogue, routes, route moves,<br/>and endpoint positions together"]
        C6 --> C7["Game data unchanged;<br/>quick local checks and meaningful result"]
    end

    subgraph D["D - Separate Stockfish analysis"]
        D1["Separate Stockfish operation<br/>benchmark / bulk / worker"] --> D2["Publish or read analysis data"]
        D3["setup and both update workflows"] -.->|"never invoke"| D1
    end

    subgraph E["E - Rare full rebuild"]
        E1["Operator deliberately removes or moves<br/>data/database/chess.db outside the tool"] --> E2["Run setup again"]
        E2 --> A1
    end

    subgraph F["F - Proof and application boundary"]
        F1["Separate DB-09 proof:<br/>integrity, measurements, direct reads,<br/>and bounded evidence"] --> F2["Only after acceptance:<br/>later application assessment"]
    end

    START --> A1
    A7 --> B2
    A7 --> C2
    A7 --> F1
    B7 --> F1
    C7 --> F1

    OLD["Old production database untouched<br/>raw sources retained; no deletion"] -.-> A1
    OTHER["Other data/database/ files<br/>outside workflow and not blockers"] -.-> A1

    classDef public fill:#dcefdd,stroke:#2f6b2f,color:#173315
    classDef internal fill:#e8e8ee,stroke:#55556b,color:#26263a
    classDef info fill:#e8e8ee,stroke:#55556b,color:#26263a
    classDef separate fill:#ece0f7,stroke:#6a3a9c,color:#3a2160
    classDef boundary fill:#f9dcdc,stroke:#9c2b2b,color:#5c1717

    class A4,B2,C2 public
    class A1,A2,A3,A5,A6,A7,A8,B1,B3,B4,B5,B6,B7,C1,C3,C4,C5,C6,C7,F1 info
    class D1,D2,E1,E2,F2 separate
    class START,D3 info
    class OLD,OTHER boundary
```

## What each journey shows

- **A — First setup.** `setup` uses only the exact fixed destination and refuses to touch a
  pre-existing file. It composes schema creation, complete base game loading, latest valid
  opening loading, and derived-row creation. A later failure removes only the newly created
  database; there is no resume or recovery protocol.
- **B — Games.** Saved monthly files remain the only fetch ledger. The newest saved month is
  refetched, missing months are filled, corrected games replace their saved representation by
  Chess.com ID, new games are added, omitted games remain, and successfully completed months
  remain usable if a later month fails.
- **C — Openings.** All five latest opening files are staged and validated before publication.
  An invalid set leaves both retained sources and the current catalogue in place. A valid set
  publishes the complete catalogue and routes without changing game data.
- **D — Stockfish.** Analysis is a separate operation. Setup and updates do not run the engine;
  internal analysis services do not turn Stockfish into a fourth data-loading workflow.
- **E — Rare rebuild.** A full rebuild is deliberately initiated by the operator outside the
  tool by removing or moving the fixed database, followed by `setup`. There is no supported
  reset, rebuild, snapshot, replacement, rollback, recovery, or separate verification command.
- **F — Proof and application.** Normal operations use quick local checks only. Full DB-09
  proof is separate, and backend/frontend/API application work remains behind the pre-application
  gate until DB-09 is accepted.

The old production database, retained raw sources (with only the approved current-month
refetch/merge), approved schema, legacy scripts, and unrelated files under `data/database/`
remain explicit boundaries. This document does not create a database,
authorize implementation, or rewrite completed DB-08/DB-08A Plans or prior grilling records.

## Evidence notes

- Current behavioral authority: `docs/grilling-docs/database-rebuild-simple-lifecycle.md`.
- Current Plan: `docs/plans/active/database-rebuild-db-09/database-rebuild-db-09.md`.
- The historical DB-08/DB-08A records remain preserved and are not current command authority.
