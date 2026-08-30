# Persisted Effective-Date Read Contract - truthful preferred-move read metadata

> **Status:** done - implemented, behaviorally proven, and user accepted

- **Read trigger:** Read before implementing D1 of the Saved Move Panel destination, changing the preferred-move GET
  contract or typed client, or changing the focused proof for this outcome.
- **Upstream:** [Saved Move Panel master plan](../../../../master-plans/saved-move-panel/saved-move-panel.md); [accepted
  preferred-move API Plan](../../preferred-move-api/preferred-move-api.md); [accepted preferred-move storage
  Plan](../../preferred-move-storage/preferred-move-storage.md)

## Outcome

A preferred-move read exposes the persisted effective date of the saved move selected by the existing `as_of` and
event-ordering rules. Assigned reads return canonical UTC `effective_at` text, unassigned reads return
`effective_at: null`, and the typed frontend read state retains that value after loading or reloading a position.

## Scope

- **Included:** An additive `effective_at` field on the preferred-move GET response; read-only resolution from the
  selected existing preferred-move event; preservation of full-FEN validation, fixed ownership, four-field identity,
  `as_of`, effective/recorded event ordering, and append-only storage; strict frontend response typing and runtime
  validation; existing deterministic preferred-move response fixtures; and focused backend/frontend regression tests.
- **Expected areas:** `backend/app/features/preferred_move/{api_schemas.py,repository.py,service.py}`;
  `backend/tests/features/preferred_move/test_api.py`; and the bounded preferred-move client, read-state tests, and
  response fixtures under `frontend/src/features/repertoire-builder/`. Keep the shared
  `scripts/opening_catalog` read-state contract unchanged unless an existing non-duplicative seam proves necessary.
- **Excluded:** Panel presentation or effective-date display; recorded dates; changed `as_of` semantics; PUT/DELETE
  behavior; new persistence, schema objects, migrations, or database writes; route integration; Position Reach
  Frequency; Move History; R2 UX; new endpoints, dependencies, owners, identities, or broader API fields; unrelated
  worktree changes; historical-record edits; commits; and pushes.

## Stages

1. **complete - Add the truthful backend preferred-move read field.** Resolve the selected preferred-move event's
   persisted effective timestamp without changing the accepted storage or read semantics.
   - **Ordered actions:** Re-read the master plan and accepted API/storage Plans. Extend the strict GET response model
     with nullable `effective_at`, and carry the selected preferred-move event metadata through the existing backend
     repository/service read seam. Use the same `as_of` boundary and `effective_at`, `recorded_at`, and `event_id`
     ordering already used to derive the move. Return the canonical stored UTC value only when the selected state has
     a move; return `null` for no move, including an initial or removal-selected unassigned state. Do not expose
     `recorded_at`, call schema initialization, change mutations, or alter the shared storage state contract. Extend
     the isolated API tests for assigned, unassigned, and `as_of`-selected dates while preserving existing exact
     response and safety assertions.
   - **Focused proof:**
     `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_move/test_api.py -q`
     (bash tool timeout: `150000` ms).
   - **Breakpoint:** None for the additive field while the existing event lookup and storage boundaries remain usable.
     Stop and escalate if metadata cannot be obtained without changing schema, event ordering, `as_of`, mutation
     behavior, ownership, or the shared storage contract.

2. **complete - Preserve the effective date through the typed frontend read seam.** Make the accepted response shape
   strict in the client and prove that existing whole-response read state retains the field without adding UI.
   - **Ordered actions:** Add required nullable `effective_at` to `PreferredMoveResponse` and its exact-key runtime
     validator. Update deterministic client, hook, workspace-test, and Storybook response fixtures to represent the
     new read contract. Keep `usePreferredMoveState` page-local and whole-response based; add a focused regression
     assertion that the effective date survives the initial read and a position reload. Do not change
      `PreferredMovePanel`, date controls, mutation requests, or presentation. Run the frontend unit proof only;
      broad type/build coverage belongs to separate maintenance.
   - **Focused proof:**
      `timeout 120s npm.cmd test --prefix frontend -- --run --project=unit src/features/repertoire-builder/preferredMoveApi.test.ts src/features/repertoire-builder/preferredMoveState.test.ts`
      (bash tool timeout: `150000` ms).
   - **Breakpoint:** None for the settled typed additive response. Stop and escalate if retaining the field requires
     panel UX, a new client abstraction, mutation/API changes, a dependency, or a different reload/ownership model.

Stages are sequential; no parallel stages. A passing proof remains valid until a later change affects its command,
inputs, exercised behavior, configuration, dependencies, or environment. Maintenance results do not gate acceptance
or archival.

## Progress and decisions

- **Stage 1:** complete - backend GET responses now carry the selected persisted move event's `effective_at`, with
  assigned, unassigned, and `as_of` selection covered by the isolated API proof.
- **Stage 2:** complete - the strict typed client and whole-response read state retain nullable `effective_at`; bounded
  fixtures were updated and focused frontend tests plus the build passed.
- **Decision:** `effective_at` is the selected saved preferred-move event's effective timestamp, not `recorded_at` and
  not a requirement-event timestamp. An unassigned selected state has `effective_at: null`.
- **Decision:** The backend repository/service read seam carries the metadata locally so existing shared storage and
  history callers retain their current contract and behavior.
- **Maintenance decision:** Separate full-suite results do not gate this Plan's acceptance or archival.
- **Acceptance:** The user accepted the implemented outcome and asked work to continue to the next reviewable UI
  component. The focused behavioral proof is sufficient for this Plan.

## Proof

- Backend regression: `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_move/test_api.py -q`
  (bash tool timeout: `150000` ms) - passed, `18 passed in 1.59s`.
- Frontend typed client/read-state regression:
  `timeout 120s npm.cmd test --prefix frontend -- --run --project=unit src/features/repertoire-builder/preferredMoveApi.test.ts src/features/repertoire-builder/preferredMoveState.test.ts`
  (bash tool timeout: `150000` ms) - passed, `32 passed` across the two focused files.
- A frontend build happened during implementation and passed, but it is a historical maintenance result rather than
  required Plan proof.
- The shared `scripts/opening_catalog` read-state contract is intentionally unchanged, so
  `tests/opening_catalog/test_preferred_move.py` is not part of this Plan's proof. If implementation must change that
  contract, stop at the stated breakpoint and obtain coordinator approval before adding its
  `timeout 120s .venv/Scripts/python.exe -m pytest tests/opening_catalog/test_preferred_move.py -q` proof
  (bash tool timeout: `150000` ms).
- Passing behavioral proof is retained until an affecting change invalidates it. Maintenance checks do not gate this
  Plan.

## Escalation boundaries

- Any change to fixed preferred-move ownership, full-FEN input, four-field identity, existing `as_of` behavior,
  effective/recorded/event-id ordering, canonical UTC normalization, append-only storage, or PUT/DELETE semantics.
- Any need for a schema object, migration, new persistence, runtime database write, requirement-state exposure,
  recorded-date exposure, new endpoint, extra response field, dependency, identity, or client abstraction.
- Any change to panel presentation, effective-date controls, route integration, Position Reach Frequency, Move History,
  R2 UX, board/evaluation behavior, training behavior, or visual/accessibility acceptance.
- Any required modification to the shared `scripts/opening_catalog` read-state contract, or any unrelated failure,
  worktree collision, historical-record edit, commit, or push. Source/test size violations are deferred maintenance.

## Visible result

> A preferred-move GET response truthfully carries the persisted effective date of its selected saved move, while the
> typed frontend read state keeps that date after the position is loaded again.
