# S5 Tracked-Player Projection Retrospective — Historical Grilling Synthesis

**Recorded:** 2026-08-23
**Status:** Closed historical synthesis; S5 was abandoned and not accepted
**Implementation authority:** None
**Relationship:** Closes the failed [S5 tracked-player projection Plan](../plans/done/s5-tracked-player-projection/s5-tracked-player-projection.md) without authorizing code removal, runtime publication, or follow-on implementation.

## Purpose

This record preserves what the S5 attempt proved, what failed during runtime publication, what was restored, and
the user's resulting direction. It is historical evidence, not a claim that S5 delivered a runtime or user-facing
capability. It does not authorize product, schema, API, database, code-removal, or master-plan work.

## Restored runtime state

- The restored runtime database retains the accepted S1 through S4 data and has no S5 tables or personal
  projection data.
- Corpus 1 remains owned by skyrocoster's stable player UUID,
  `0101b08a-ce8b-11ee-b2fd-e90263e5548c`.
- The failed S5 attempts did not replace or damage the accepted S1 through S4 foundation. The retained backup and
  restoration path preserved that boundary.
- S5 therefore delivered no runtime or user-facing capability. Its remaining implementation and tests are
  temporary-development evidence only.

## What the existing S3 and S4 data can already support

For skyrocoster, the existing corpus and S3/S4 facts can support queries or derived views for:

- high-frequency exact four-field positions;
- opening-route frequencies and memberships;
- actual move and terminal branches;
- player color, chronology, game results, and ratings; and
- computed association of losses with positions, routes, or observed branches.

These are existing factual inputs, not persisted S5 personal projections. Arbitrary multi-ply lines are not a
ready-made fact and require reconstruction and aggregation from the existing occurrence and branch data.

Engine analysis exists elsewhere in the repository, but it is not linked to a source game and ply, and no
evaluation-loss value is persisted for an observed move. There is also no durable designation of a chosen or
correct move and therefore no durable wrong-move comparison.

## What Stages 1 through 3 proved

Stages 1 through 3 implemented and tested a stable-UUID identity contract, additive S5 schema, deterministic
personal derivation, temporary publication, idempotent reruns, rollback, and rich fixtures. The fixtures covered
both player colors, multiple opening memberships, repeated positions and games, routes, move and terminal
branches, chronology, results, ratings, input-change refusal, and preservation of upstream facts.

Those results were valid functional proof in temporary SQLite databases. They did not demonstrate production-scale
runtime readiness, did not publish retained personal data, and did not create an inspectable user capability.

## Runtime failure and restoration

Stage 4 failed in two distinct runtime attempts:

1. The first publication attempt exhausted Python memory while materializing 2,402,576 route events. It resolved
   identity safely but published no personal state, run, classification, or projection rows.
2. A later bounded-memory attempt entered a large runtime transaction but was interrupted before successful
   publication and closeout. The retained backup was restored rather than treating the interrupted state as
   acceptable.

After restoration, the runtime database contained the accepted S1 through S4 state and no S5 tables or personal
projection data. The safeguards around backup, atomicity, and upstream preservation prevented the failed attempts
from becoming partial accepted state.

## Why the approach failed

The failure was not only one implementation defect. The approach and its proof boundary were mismatched to the
production data:

- Four copied/materialized personal projection families duplicated large S4-derived data instead of querying or
  narrowly projecting only missing personal capabilities.
- Temporary fixtures were too small to expose the production memory, transaction-duration, and database-growth
  behavior.
- The Plan had no adequate production resource budget, time limit, cancellation boundary, interruption handling,
  or recovery acceptance criteria before the write attempt.
- Repeated expensive safety and equality checks increased runtime pressure and extended the critical operation.
- Functional correctness, deterministic fixtures, rollback tests, and idempotency were treated as if they also
  proved production runtime readiness.

The backup, write authorization boundary, upstream signatures, atomic publication design, and restoration process
were nevertheless valuable safeguards: S1 through S4 survived and the failed S5 state was not retained.

## Abandonment decision

The user explicitly abandoned the four copied/materialized S5 personal projection tables. Future work is to use
skyrocoster's existing corpus and S4 data directly rather than retrying or repairing that materialization model.
The S5 Plan is closed and archived as not accepted. Existing S5 implementation code is not removed by this
documentation closeout.

## Bounded future direction

Retain S1 through S4. If separately settled and planned, future work should add only capabilities that are actually
missing, such as:

- bounded loss-association queries or narrowly justified projections;
- durable storage for a chosen correct move;
- comparison of the observed move with that chosen move; and
- game/ply-linked engine analysis and persisted evaluation loss.

This direction does not preselect schemas, APIs, materialization, ownership, thresholds, or a user interface.

## Decisions still open

The following questions are recorded, not resolved:

- Who or what is authoritative for a chosen correct move: manual selection, engine analysis, repertoire data, or a
  hybrid policy?
- What exact arbitrary multi-ply line scope and aggregation behavior are required?
- Which games, positions, and plies should receive evaluation analysis, and under what coverage, resource,
  cancellation, and recovery strategy?

Resolving any of these requires separate product and data decisions. This retrospective supplies no implementation
authority for them.
