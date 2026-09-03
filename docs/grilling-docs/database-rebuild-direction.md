# Database rebuild direction

> Historical decision evidence recorded on 3 September 2026. This document defines the agreed discovery boundary.
> It is not a Plan and does not authorize database deletion, schema changes, data migration, application changes, or
> implementation.

## Intent

Rebuild the database and all related APIs, scripts, and tools from first principles. The existing application now
provides enough real usage to identify what data is needed and how it must be accessed. Existing tables and pipelines
are evidence of what was previously attempted; they are not architecture that must be preserved.

The rebuild must understand every surviving data field and use. It should remove accidental complexity, unsupported
history, speculative projections, and machinery added for abandoned or failed directions.

## Governing scope

Version one preserves current, demonstrated user capabilities rather than current internal contracts. Existing API
paths, request shapes, response shapes, schemas, and models may be replaced. Frontend and backend contracts may change
together.

A table or persisted derived dataset is justified only by:

1. a current application capability; or
2. a tool the user actively uses.

Reachable code, tests, documents, old Plans, and historical scripts are evidence, not proof that a capability or table
must survive. New capabilities will be designed separately when their requirements exist; this rebuild must not add
speculative foundations for them.

## Data reset and migration boundary

- No rows from the current database will migrate.
- Raw external source files are the only retained inputs.
- Existing Stockfish analysis, classifications, projections, queues, run records, preferred moves, and all other
  database content will be discarded rather than migrated.
- All required tool-derived data will be regenerated using rebuilt tools.
- This decision is not authorization to delete the current database or any source files. The existing system remains
  evidence until a separately approved replacement process establishes what may be removed.

Newly generated derived data may still be persisted. Persistence is decided by actual usage and practical cost. For
example, expensive Stockfish output is worth storing, while cheap statistics may be calculated on demand. “Derived”
does not automatically mean disposable, and “currently stored” does not automatically justify persistence.

## Application and operating boundary

- The application serves one local trainer.
- Other chess players are not application users.
- The backend, import/rebuild tools, Stockfish workers, and maintenance processes may run concurrently on one Windows
  computer.
- Network-scale multi-user operation is not required.
- No API should be built before an actual application requirement needs it.

## Database technology direction

The current system uses SQLite plus source files. SQLite is not assumed to be the problem, but it is also not retained
automatically. The more evident existing problems are fragmented schema ownership, speculative materialized data,
large projections, and complicated publication and history machinery.

Embedded storage is preferred for a single-user local application. PostgreSQL or another managed database service is
acceptable only if measured concurrency, integrity, performance, or operational requirements show that an embedded
design cannot safely satisfy the rebuilt workload. The final engine and database boundaries remain unsettled until the
required reads, writes, rebuilds, and publication behavior are documented.

## Raw-source policy

- Do not introduce enterprise-style content-addressed storage, persistent file hashes, accepted-manifest pointers, or
  import audit histories without a current functional need.
- Replaceable external records use a latest-known snapshot model. A new profile fetch may replace the previous raw
  profile file rather than creating permanent profile history.
- Irreplaceable records such as individual games may have source-specific retention behavior.
- Operational state such as a fetch cursor or ETag may survive when it directly prevents unnecessary work.
- Schema versions and resumable-job state may exist when required for safe operation; they are not blanket
  authorization for families of schema/run/state tables.

## Required current workflows

### Chess.com game intake

The rebuilt system must:

- fetch Chess.com games;
- retain the raw game responses;
- process those inputs into the game and position facts needed by the viewer.

Existing corpus fingerprints, run histories, accepted-state pointers, and publication structure are not requirements.

### Stockfish analysis

The rebuilt system must support both:

- bulk offline Stockfish analysis; and
- individual Analyze/Update/Retry requests initiated from the viewer.

Both should use one coherent analysis capability. Newly regenerated analysis is expected to be persisted because it is
expensive to reproduce. The current evaluation queue is not protected: assessment found that the backend can enqueue
requests but has no production caller that drains the queue. Append-only batch and failure audit tables are likewise
not requirements.

### Repertoire statistics

Position Context and Move Response Distribution are key current capabilities and must continue to work. Their visible
meaning is required; their existing APIs, models, recurrence tables, and projection tables are not.

The rebuild must include a supported opening-data preparation capability that:

- ingests the raw opening reference sources;
- classifies the game corpus as required; and
- supplies the facts needed by those two statistics features.

The calculation and persistence design must follow the real queries. Existing projection tables must not be retained
merely because the current panels read them. In particular, prior failed work created projection tables the user
considers useless.

The raw opening data and its acquisition tool are believed to remain on disk, but their presence, completeness, and
shape have not yet been verified.

### Preferred moves

No current preferred-move rows will migrate; the rebuilt system starts empty. The data model must nevertheless support
the current preferred-move capability with these semantics:

- database state is preferred versus not preferred; alternative “also acceptable” rules are future work;
- preference applies with UK calendar-date precision rather than timestamp precision;
- historical periods are editable, not append-only;
- periods may later be inserted, moved, shortened, extended, replaced, or deleted;
- reselecting a move creates another effective period rather than erasing the earlier period;
- unconfigured time must be distinguishable from a deliberately empty/no-preference period; and
- the model must not use no-update/no-delete triggers that prevent correcting effective dates.

Evaluating historical games against the preference applicable on their played date is future work. It is explicitly
excluded from the present rebuild implementation.

## Explicitly excluded capabilities

### Opponent profiles

Shared opponent-profile support is new functionality and is excluded. The raw files under
`data/chess-com/raw/profiles/` remain untouched for a separate future project. A permitted sample found 11,735 JSON
files; the first two contained flat Chess.com profile responses with stable-looking `player_id` and `username` fields
plus mutable profile attributes. That available data does not justify tables or ingestion in this rebuild.

### Opening Line Library

The repository has an Opening Line Library backend endpoint, frontend API client, and Storybook work, but no current
application page exposes it. It is unfinished/new functionality and is excluded from this rebuild.

### Historical and stopped work

The following do not define required behavior:

- the stopped Chess.com refresh direction;
- abandoned tracked-player tables and code;
- speculative or unconsumed projection tables;
- write-only audit histories;
- schema/state/run table families inherited only from previous pipeline structure; and
- tests or stories for features with no current application or actively used tool consumer.

## Current-use assessment retained for the next stage

A user-authorized Flash case-worker traced current production paths. The assessment found:

- the game viewer reads corpus, game, occurrence, and position data;
- evaluation UI reads stored analysis and can enqueue requests, but the running backend has no production queue
  drainer;
- Position Context reads recurrence game and position-derived data;
- Move Response Distribution reads position and branch-derived data;
- preferred-move APIs currently reuse append-only storage that conflicts with the newly settled mutable-period
  requirement;
- the Opening Line Library has no rendered application route;
- some recurrence projections are current readers' dependencies, while other projections have no reader; and
- opening classification and recurrence writers are currently reached only through tests or the stopped refresh
  orchestration, so the required preparation tool must be redesigned rather than silently revived.

These findings classify existing dependencies; they do not authorize keeping the corresponding tables.

## Next discovery stage

The next stage should document the minimum information and operations needed for each approved workflow before
designing tables:

1. raw game acquisition and retained source shape;
2. canonical game and position facts needed by the viewer;
3. Stockfish input, result, bulk-run, and viewer-request lifecycles;
4. exact Position Context and Move Response Distribution query semantics;
5. opening source inputs and the minimum classification facts those statistics require;
6. preferred-move effective-period semantics and integrity constraints; and
7. concurrent-process, rebuild, failure, recovery, and publication requirements.

Only after those workflows are understood should the work compare SQLite and alternatives, propose database
boundaries, design a replacement schema, identify which existing table concepts survive, and prepare implementation
planning. Any further repository agent work requires explicit user permission.
