# Database operator journeys — refresh, stage, snapshot, replace, rollback, proof

> **Decision support only.** Not settled authority; not implementation authorization. Amber
> boxes show the implemented DB-08 commands and their safety ordering.

## Legend

| Style | Meaning |
|---|---|
| Green | **EXISTING CLI** — supported command delivered by DB-01..DB-07 |
| Amber | **DB-08 CLI** — implemented package-owned rebuild command |
| Purple | **FUTURE / OUTSIDE DB-08** |
| Grey | Scenario steps, outcomes, or decision points (not commands) |

The companion page [`database-toolchain.md`](database-toolchain.md) shows the full data flow
behind these journeys, including the untouched old database.

## Journeys

```mermaid
flowchart TD
    START(("Start"))

    subgraph A["A - First neighboring build"]
        A1["DB-08 CLI<br/>rebuild refresh --config PATH<br/>explicit retained local sources"] --> A2["DB-08 CLI<br/>rebuild verify --config PATH<br/>--target neighbour"]
        A2 --> A3{"STRUCTURAL PARTIAL<br/>opening-only checkpoint;<br/>valid, not replacement-ready"}
        A2 --> A4{"REPLACEMENT-READY<br/>ready openings + imported games<br/>and integrity/compatibility checks"}
        A3 -->|"next normal idempotent refresh"| A1
    end

    subgraph B["B - Later update from retained local sources"]
        B1["DB-08 CLI<br/>rebuild candidate --config PATH<br/>managed sibling only; explicit local sources"]
        B1 --> B2["DB-08 CLI<br/>rebuild verify --config PATH<br/>--target candidate"]
        B2 --> B3{"Candidate state?"}
        B3 -->|"partial"| B4["Partial candidate<br/>not replacement-ready"]
        B3 -->|"replacement-ready"| B5["Replacement-ready<br/>managed candidate outcome"]
        B4 -->|"next normal idempotent<br/>rebuild candidate rerun"| B1
    end

    subgraph C["C - Optional acquisition first"]
        C1["EXISTING CLI<br/>games acquire --config PATH --raw-root PATH<br/>network; current month UUID-merged"] --> C2["Retained local raw month ledger<br/>available to rebuild refresh/candidate"]
        C2 --> A1
    end

    subgraph D["D - Direct initial analysis versus API-03 queue"]
        D1["EXISTING CLI<br/>stockfish bulk --preset initial<br/>20 common + five technical<br/>serial, resumable, direct publication;<br/>no queue rows"]
        D2["FUTURE / OUTSIDE DB-08<br/>API-03 analysis request enqueue"] --> D3["EXISTING CLI<br/>stockfish worker --database --executable<br/>queue requests only"]
    end

    subgraph E["E - Interrupted candidate, then ordinary rerun"]
        E1["Interruption or crash-like failure<br/>during managed candidate work"] --> E2["Working neighbour remains active;<br/>partial candidate is not replacement-ready"]
        E2 --> E3["Next normal idempotent<br/>rebuild candidate rerun"]
        E3 --> B1
    end

    subgraph F["F - Snapshot + candidate replacement"]
        F1["DB-08 CLI<br/>rebuild snapshot --config PATH<br/>optional standalone verified WAL-safe backup;<br/>retain newest three"]
        F2["Managed candidate artifact<br/>replacement-ready outcome<br/>from Journey B"] --> F3["DB-08 CLI<br/>rebuild replace --config PATH<br/>reverify candidate; obtain exclusive boundary"]
        F3 --> F4["Automatic fresh verified snapshot<br/>then atomic swap only configured neighbour"]
    end

    subgraph G["G - Rollback after a bad replacement"]
        G1["DB-08 CLI<br/>rebuild rollback --config PATH<br/>newest or explicit retained snapshot"] --> G2["Reverify snapshot; preserve current neighbour first;<br/>atomically restore only neighbour path"]
    end

    subgraph H["H - DB-09 proof"]
        H1["FUTURE / OUTSIDE DB-08<br/>real-data proof gate over the<br/>populated neighbor using only<br/>supported CLIs from DB-01..DB-08"]
    end

    START --> A1
    START -.->|"optional acquisition first"| C1
    A4 --> B1
    A4 -->|"optional direct initial analysis"| D1
    B5 -->|"optional direct initial analysis"| D1
    B5 -.->|"optional standalone snapshot"| F1
    B5 -->|"already replacement-ready artifact"| F2
    F4 --> G1
    F4 --> H1

    classDef cli fill:#dcefdd,stroke:#2f6b2f,color:#173315
    classDef cand fill:#fdf0d5,stroke:#a3690a,color:#4a3005
    classDef future fill:#ece0f7,stroke:#6a3a9c,color:#3a2160
    classDef info fill:#e8e8ee,stroke:#55556b,color:#26263a

    class C1,D1,D3 cli
    class A1,A2,B1,B2,F1,F3,G1 cand
    class D2,H1 future
    class A3,A4,B3,B4,B5,F2,F4,START,E1,E2,E3,G2 info
```

## What each journey shows

- **A — First neighboring build.** `rebuild refresh` creates or opens the v1 neighbor, consumes
  explicit retained local opening and game sources, and runs the shared verifier. An opening-only
  result is a valid structural partial checkpoint; replacement-ready additionally requires imported
  games and all verifier checks. Initial creation is the same idempotent tooling as later refreshes.
- **B — Later local update.** `rebuild candidate` refreshes only the managed sibling candidate and
  verifies it without touching the working neighbor. Satisfied work is skipped and incomplete work
  is resumed by the next ordinary invocation. `rebuild verify --config PATH --target candidate`
  distinguishes partial from ready.
- **C — Optional acquisition.** Network acquisition stays an explicit, separate operator step.
  `games acquire` publishes retained raw months; `rebuild refresh` and `rebuild candidate` consume
  those local files and never acquire from the network.
- **D — Optional Stockfish population.** `stockfish bulk --preset initial` selects 20 common plus
  five fixed technical positions, runs serially, resumes eligible work, and publishes directly with
  no queue rows. The worker is a separate path for API-03 queue requests only.
- **E — Interruption and recovery.** An interrupted or crash-like managed candidate remains isolated
  from the usable neighbor and is not replacement-ready. The next normal `rebuild candidate` rerun
  resumes or reconstructs it; there is no recover command or permanent run/failure record.
- **F — Snapshot plus candidate replacement.** `rebuild snapshot` uses a verified WAL-safe SQLite
  backup and retains the newest three. `rebuild replace` verifies the managed candidate, obtains the
  exclusive Windows mutation boundary, automatically takes a fresh verified snapshot, then atomically
  swaps only the configured neighbor. The old database and application cutover are never involved.
- **G — Rollback.** `rebuild rollback` re-verifies the newest or selected retained snapshot, preserves
  the current neighbor first, and atomically restores only the neighbor path. This is distinct from
  RETIRE-01's separate old-database restore path; the old database is never involved.
- **H — DB-09 proof.** Real rebuilt data proves the foundation using only supported commands
  from DB-01..DB-08. Cutover (CUT-01) remains outside DB-08 entirely.

## Evidence notes

- DB-08 envelope: `docs/master-plans/database-rebuild/database-rebuild.md`, slice "DB-08 —
  Rebuild, snapshot, and replacement operations" (visible result, scope, exclusions, focused
  proof, escalate-if).
- Idempotence, resumability, snapshot, and rollback authority:
  `docs/grilling-docs/database-rebuild-direction.md` sections 2.3-2.5.
- Existing commands and their proven failure/interruption behavior: focused Plans under
  `docs/plans/done/database-rebuild-db-01/` through `.../database-rebuild-db-07/`.
