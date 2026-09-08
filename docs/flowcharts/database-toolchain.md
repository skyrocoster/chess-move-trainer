# Database toolchain — current DB-09 direct lifecycle

> **Decision support only.** This diagram records the confirmed current DB-09 direction; it is
> not implementation authorization. Historical DB-08/DB-08A database-file machinery is not a
> supported part of this lifecycle.

The durable command inventory is tracked in
[`database-command-inventory.md`](database-command-inventory.md).

## Legend

| Style | Meaning | Examples |
|---|---|---|
| Green | **PUBLIC DATA LOADING** — exactly the three supported data-loading workflows | `setup`, `update games`, `update openings` |
| Grey | **INTERNAL — NO SEPARATE DATA-LOADING CLI** — package service composed by a public workflow | validation, normalization, persistence |
| Purple | **SEPARATE / OUTSIDE THE DATA-LOADING LIFECYCLE** | Stockfish analysis, later application work |
| Blue | **Retained data artifact** | monthly source files, five opening files, fixed database |
| Red | **Boundary** — retained or explicitly outside scope | old database, other `data/database/` files |

## Flow

```mermaid
flowchart TD
    %% ===== retained sources and boundaries =====
    BASE["Complete base game sources"]
    MONTHS[("Saved Chess.com monthly files<br/>fetch ledger<br/>historical months retained<br/>newest month refetched")]
    OPENINGS[("Latest upstream opening set<br/>a.tsv through e.tsv<br/>no configured commit/version<br/>only latest valid set retained")]
    OTHER[("Other files under data/database/<br/>outside workflow<br/>not inspected or blockers")]

    subgraph OLD["OLD WORLD - untouched and outside DB-09"]
        OLDDB[("Old production database<br/>not modified or deleted")]
        RAW[("Raw sources<br/>retained; no deletion<br/>current-month merge only")]
    end

    %% ===== fixed direct destination =====
    DB[("FIXED DATABASE<br/>data/database/chess.db<br/>approved ten-table schema<br/>no candidate or neighbor")]

    %% ===== exactly three public data-loading workflows =====
    SETUP["PUBLIC DATA LOADING<br/>setup<br/>only when fixed path is absent"]
    GAMES["PUBLIC DATA LOADING<br/>update games<br/>direct incremental update"]
    OPENS["PUBLIC DATA LOADING<br/>update openings<br/>latest valid complete set"]

    %% ===== internal composition =====
    SSETUP["INTERNAL - NO SEPARATE CLI<br/>schema/bootstrap + complete source composition"]
    SGAMES["INTERNAL - NO SEPARATE CLI<br/>acquire, validate, normalize, persist<br/>merge by Chess.com game ID"]
    SOPENS["INTERNAL - NO SEPARATE CLI<br/>validate all five, parse, publish<br/>catalogue + routes together"]
    QUICK["INTERNAL - NO SEPARATE CLI<br/>quick operation-local checks only"]

    %% ===== separate analysis and future gate =====
    STOCK["SEPARATE ANALYSIS SURFACE<br/>stockfish benchmark / bulk / worker<br/>never invoked by setup or updates"]
    ANALYSIS[("Analysis result and line data<br/>published by Stockfish operations")]
    DB09["DB-09 proof gate<br/>full integrity, measurements,<br/>direct reads and bounded proof<br/>separate from normal loading"]
    APP["FUTURE / OUTSIDE DB-09<br/>backend, frontend, HTTP API,<br/>application integration and cutover"]

    %% ===== manual rare rebuild boundary =====
    MANUAL["MANUAL RARE REBUILD<br/>operator deliberately removes or moves<br/>the fixed database outside the tool"]

    BASE --> SETUP
    OPENINGS --> SETUP
    SETUP --> SSETUP --> DB
    MONTHS --> GAMES --> SGAMES --> DB
    OPENINGS --> OPENS --> SOPENS --> DB
    SETUP --> QUICK
    GAMES --> QUICK
    OPENS --> QUICK

    DB --> STOCK --> ANALYSIS
    DB --> DB09 --> APP
    MANUAL -.->|afterward run setup| SETUP

    OLDDB -.->|never modified or deleted| DB09
    RAW -.->|retained source boundary| GAMES
    OTHER -.->|outside workflow| DB

    classDef public fill:#dcefdd,stroke:#2f6b2f,color:#173315
    classDef internal fill:#e8e8ee,stroke:#55556b,color:#26263a
    classDef separate fill:#ece0f7,stroke:#6a3a9c,color:#3a2160
    classDef store fill:#dbe9f7,stroke:#28588c,color:#173154
    classDef boundary fill:#f9dcdc,stroke:#9c2b2b,color:#5c1717

    class SETUP,GAMES,OPENS public
    class SSETUP,SGAMES,SOPENS,QUICK internal
    class STOCK,ANALYSIS,DB09,APP,MANUAL separate
    class BASE,MONTHS,OPENINGS,DB store
    class OLDDB,RAW,OTHER boundary
```

## How to read the flow

- **Exactly three public data-loading workflows.** `setup`, `update games`, and `update
  openings` are the only public end-to-end data-loading operations. Fetching and persistence
  are composed internally; separate fetch/import commands are not supported.
- **Fixed destination.** Every workflow writes only to `data/database/chess.db`. Setup refuses
  a pre-existing file. If a failed setup created the file, cleanup removes only that new file;
  it never replaces an existing database or deletes sources.
- **Games.** The saved monthly files are the only fetch ledger. The newest saved month is
  refetched, missing months are filled through the current month, and valid new or corrected
  games are persisted directly. Omitted games remain, invalid games are skipped individually,
  and month progress is independent.
- **Openings.** The latest upstream `a.tsv` through `e.tsv` set is obtained without a configured
  commit/version input and validated completely before publication. A bad or incomplete set
  leaves the retained source set and catalogue intact; a valid set publishes the catalogue and
  routes together without changing game data.
- **Quick checks and Stockfish.** Normal setup and updates run only quick local checks. Full
  proof routines and measurements are separate. Stockfish analysis is a separate surface and
  is never run as part of setup or either update.
- **Manual rare rebuild.** A full rebuild is an operator action outside the tool: deliberately
  remove or move the fixed database, then run `setup`. There is no reset, rebuild, resume,
  recovery, snapshot, rollback, replacement, or verification command for this lifecycle.
- **Boundaries.** The old production database remains untouched. Raw sources are retained with
  only the approved current-month refetch/merge; no raw source is deleted. The approved schema
  is not expanded, legacy scripts are noncanonical evidence only, and other files under
  `data/database/` are outside the workflow. No application consumer is integrated before the
  DB-09 gate is accepted.

The diagram does not create a database, authorize implementation or application work, or
rewrite completed DB-08/DB-08A Plans or prior grilling records.

## Evidence notes

- Current behavioral authority: `docs/grilling-docs/database-rebuild-simple-lifecycle.md`.
- Current lifecycle and boundaries: `docs/plans/active/database-rebuild-db-09/database-rebuild-db-09.md`.
- Current command inventory: [`database-command-inventory.md`](database-command-inventory.md).
- Historical DB-08/DB-08A records remain available as historical evidence only.
