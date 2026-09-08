# DB-09 rebuilt-database proof gate

> **Status:** approved grilling handoff
> **Approved:** 2026-09-07
> **Selected case-worker:** Luna

## Purpose

DB-09 is the real-data proof gate for the clean replacement database and toolchain. It must establish that a
neighboring database can be rebuilt from real retained sources, passes its integrity checks, and supports the direct
database capabilities needed by later application work. It does not authorize application integration, cutover, old
database changes, or legacy-tool participation.

The binding product, data, and schema authorities remain
`docs/grilling-docs/database-rebuild-direction.md`, `docs/grilling-docs/database-rebuild-schema.md`, and the DB-09
envelope in `docs/master-plans/database-rebuild/database-rebuild.md`. This handoff settles only the DB-09 choices that
those authorities intentionally left open.

## Confirmed decisions

### Real source corpus

- Use the selected trainer account's full available Chess.com history, not a bounded month sample.
- Acquire the history through the clean supported `games acquire` path. Retain the monthly sources under the documented
  `data/chess-com/raw/games/<YYYY>/<MM>.json` structure; no old database rows are a source.
- Reuse only the username and trainer Chess.com UUID already held in the legacy configuration. Transfer those two
  identity values into a new supported configuration or supported explicit inputs. No legacy command, module, wrapper,
  or runtime path may participate.
- Acquire all five real Lichess opening files, `a.tsv` through `e.tsv`, through the clean supported `openings acquire`
  path at its pinned upstream revision. The assessment/Plan may choose a clear local source directory because the
  supported command intentionally requires an explicit path and no repository-wide default is settled.
- A network or source failure does not reduce the accepted corpus silently. DB-09 remains incomplete until the full
  discoverable archive and complete five-file opening source are usable, or a genuine external blocker is escalated.

### Neighboring database result

- Build and retain the real neighboring replacement through the clean package and supported CLI command map accepted by
  DB-08A. The old database remains untouched and is not an input to the rebuild.
- The retained candidate contains real regenerated games, occurrences, positions, openings, routes, route moves, and
  accepted analysis data.
- The retained candidate's `datasource_preferred_move_period` table remains empty. Preferred, explicit
  no-preference, and unconfigured states and period-edit transaction semantics are proven only in a disposable focused
  database or a transaction that is fully rolled back.
- No inferred setup proposal or fabricated/migrated preference row becomes canonical state. Setup inference remains
  owned by SETUP-01 after this gate.

### Analysis sample

- Use the already-supported initial preset: 20 commonly reached real positions plus the five settled technical
  positions covering checkmate, stalemate, legal en passant, promotion, and castling.
- Use the accepted Tool profile of 6,400,000 nodes, 6 threads, 1,024 MiB hash, and one serial Stockfish process. DB-09
  does not reopen that profile or add parallel workers.
- Prove the initial 25-position run and the separate on-demand bulk-selection behavior without creating a persisted
  target list. Preserve the settled quality ordering, terminal handling, complete candidate-line publication, and
  no-partial-publication rules.

### Direct capability proof

The focused proof must exercise and document these meanings directly over the rebuilt database without creating an
HTTP or frontend contract:

- reconstruct one or more real games and their ordered move/position occurrences, including the final occurrence;
- Position Context counts distinct games for the selected canonical position and trainer-color meaning;
- Move Response Distribution counts occurrences and outgoing moves while distinguishing trainer choices from opponent
  responses;
- PGN replay returns ordered recognized opening endpoints and the current label;
- exact route lookup and FEN lookup distinguish route matches from transposition matches, exclude unreached future
  variations, and do not imply the excluded Opening Line Library application surface;
- preferred, explicit no-preference, and unconfigured states have the settled meanings without populating the retained
  candidate; and
- analysis reads preserve Browser/Tool ordering, complete lines, and canonical terminal behavior.

### Integrity and access-path policy

- The Plan must use the real rebuilt corpus for foreign-key, check/integrity, schema/version, game/occurrence,
  opening-route, preference-emptiness, and complete-analysis assertions required by the master-plan envelope.
- Record repeatable query plans and elapsed measurements for the direct capability reads. There is no fixed latency or
  throughput pass/fail threshold in DB-09.
- Measure before changing indexes. Add only straightforward indexes justified by a demonstrated full scan or clearly
  wasteful access path on the real corpus, then repeat and record the measurement. Do not add speculative projections,
  caches, summary tables, or unrelated optimizations.
- A timing number alone does not excuse an integrity or semantic failure. Conversely, a correct measured read is not
  rejected merely for missing an invented timing target.
- Escalate rather than silently broadening DB-09 if an observed problem requires a new table, projection, cache,
  application contract, dependency, concurrency model, or behavioral change beyond evidence-backed indexes.

### Tool and evidence boundary

- Accepted commands come only from the package-owned inventory in `docs/flowcharts/database-command-inventory.md`.
  Nothing under `scripts/` may be an accepted command, import, fallback, wrapper target, delegated runtime path, or
  proof path.
- Proof includes useful CLI help, explicit inputs, successful automation-safe invocation, meaningful failure exits, and
  a source-boundary review for legacy copying/importing/wrapping/delegation.
- Evidence should use aggregate counts, bounded examples, and query measurements without publishing player-identifying
  or row-level private game data in workflow records.

## Acceptance boundary

DB-09 is accepted only when the full real-source rebuild and focused database/tool proof pass and the retained
neighboring candidate remains safe for the next slice. No backend or frontend application-consumer work begins here.
After acceptance, DB-09's evidence becomes the handoff for SETUP-01; API-01 remains gated until SETUP-01 is accepted.

Escalate any need for data outside the ten-table catalogue, partial-corpus acceptance, old-database use or mutation,
legacy runtime participation, a new dependency, application integration, cutover, deletion, or a different acceptance
policy.
