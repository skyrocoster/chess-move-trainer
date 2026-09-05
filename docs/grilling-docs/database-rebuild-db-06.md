# DB-06 Grilling Handoff: Analysis Result Publication

**Status:** Coordinator-confirmed historical directional evidence for DB-06. This is the mandatory DB-06 grilling handoff before its implementation Plan/work begins. It is not implementation authorization and does not replace the database-rebuild master plan or the binding direction/schema records.

**Authority retained:** `docs/master-plans/database-rebuild/database-rebuild.md:L296-L320` remains authoritative for the DB-06 envelope, catalogue, sequencing, exclusions, and proof. The binding evidence is `database-rebuild-direction.md:L464-L550,L700-L729` and `database-rebuild-schema.md:L453-L565`. The settled ten-table catalogue and sequencing are not reopened here.

## Confirmed DB-06 contract

- DB-06 is an importable, package-only analysis storage/publication service. It adds no operator-facing CLI. DB-07 later owns benchmark, bulk-analysis, and worker commands.
- DB-06 accepts engine-independent, normalized analysis data. Parsing raw Stockfish/UCI output belongs to DB-07.
- Scores use White's point of view. Centipawn scores are signed centipawns. Mate scores are signed moves-to-mate: `+3` means White can force mate in three moves; `-2` means Black can force mate in two.
- DB-06 derives terminal status from the canonical position using a neutral board state. It recognizes only `checkmate`, `stalemate`, and `insufficient_material`. Repetition and fifty/seventy-five-move outcomes are not canonical terminal states.
- Publication targets an existing `dp_position_id`; DB-06 never creates positions. Other package tools/services own position creation.
- `dar_settings_json` must be a JSON object, but DB-06 requires no particular keys. DB-07 later defines actual engine-setting names.
- The approved quality ladder is exactly `Browser < Tool`. Completion time does not add strength. Tool may replace Browser; Browser never replaces Tool. Engine or configuration changes are same-level freshness changes, not new quality levels.
- An identical same-quality result for the same configuration and engine is not saved again. A changed configuration version or engine version may refresh a same-quality result.
- By explicit operating rule, engine and configuration changes occur only while no analysis is running. DB-06 therefore needs no special cross-version race/expected-state mechanism. It must still re-read the stored result immediately before publication and enforce no-downgrade and same-level replacement rules inside the write transaction. DB-07 later owns queue claim-token stale-worker protection.
- An outdated, duplicate, or lower-quality submission leaves the stored result untouched and returns a clear package-level `not saved` outcome with its reason. An expected concurrency rejection is not an unexpected system error.
- A complete result and all candidate lines publish atomically. The previous complete result remains visible until replacement commits. Validation, interruption, or write failure publishes nothing partial and leaves the previous complete result intact.

## Acceptance invariants and focused proof

The existing PK/FK design permits at most one current result per canonical position. A terminal result has zero lines. A nonterminal result has 1–5 lines, with fewer than five only when fewer legal root moves exist. Ranks are contiguous; root moves are distinct and legal; and each principal variation is a complete sequence of legal moves, move by move, from the canonical root.

Stored lines must honor the existing score-kind/domain constraints (`cp` or `mate` with the signed White-POV value), nonnegative WDL values whose sum is exactly 1000, valid nonempty PV JSON arrays, and the existing nonnegative displayed-depth constraint. Terminal/no-line behavior must remain legal under the neutral-root policy.

Focused proof must cover WDL sum, score domain, legal complete PVs, terminal/no-line behavior, no-downgrade replacement, stale/duplicate non-publication, and no partial publication on failure.

## Implementation handoff boundaries

The read-only Flash assessment identified the expected package area as `src/chess_move_trainer/database/analysis/`, composing existing DB-01 schema/connection ownership and DB-02 canonical positions. This is implementation-location evidence only, not product authority.

Because the work is nontrivial and sequential, recommend a focused Plan at `docs/plans/active/database-rebuild-db-06/database-rebuild-db-06.md`. Likely sequential scope is: validated input models and errors; neutral-root and invariant validation; transactional publication with the pre-write recheck; and focused rollback/replacement proof.

The handoff authorizes no implementation. The DB-06 boundary contains no schema/DDL change, CLI, analysis history, or excluded diagnostic/provenance fields. It also contains no queue, worker, benchmark, backend, frontend, API, cutover, or DB-07 work.

Escalate if implementation would require occurrence counters, a catalogue/schema change, diagnostic or provenance fields, a new quality definition, raw Stockfish parsing in DB-06, position creation, or behavior inconsistent with the no-analysis-running operating rule.
