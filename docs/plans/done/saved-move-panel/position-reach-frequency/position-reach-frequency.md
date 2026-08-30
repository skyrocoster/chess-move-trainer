# Position Reach Frequency - truthful selected-colour reach share

> **Status:** done - implemented, behaviorally proven, and user accepted

- **Read trigger:** Read before implementing F1, changing the position-context read contract, or changing the focused proof or Storybook review surface for this outcome.
- **Upstream:** [Saved Move Panel master plan](../../../../master-plans/saved-move-panel/saved-move-panel.md); the active [D1 Persisted Effective-Date Read Contract](../persisted-effective-date-read-contract/persisted-effective-date-read-contract.md) remains independent and must be preserved.

## Outcome

A reusable Storybook-visible Position Reach Frequency component presents one explicitly selected repertoire colour's reached count over that colour's all-games denominator, with a safe percentage and accessible proportional bar. It truthfully distinguishes an existing position with zero reaches, an absent position, and unavailable data, without route integration or denominator changes caused by board orientation or side to move.

## Scope

- **Included:** Additive colour-specific all-game totals on the existing position-context read contract, derived read-only from accepted recurrence game rows by stable repertoire colour; strict backend and frontend validation; only affected deterministic fixtures; reusable pure model, component, styles, focused tests, and Storybook stories under `frontend/src/features/position-reach-frequency/`; existing CMT tokens/primitives and `Meter`; and preservation of D1 edits and `effective_at` fixture fields.
- **Expected areas:** `backend/app/features/position_context/{api_schemas.py,repository.py,service.py}`; focused position-context tests and fixtures under `backend/tests/features/position_context/`; `frontend/src/features/viewer/positionContextApi.ts`, its focused test, and bounded existing response fixtures under `frontend/src/features/viewer/` and `frontend/src/features/repertoire-builder/`; `frontend/src/features/position-reach-frequency/`; and `frontend/.storybook/main.ts` only if Storybook discovery requires it.
- **Excluded:** `/viewer` or `/repertoire` integration; PositionContext, GameContext, or workspace replacement; move-frequency or engine statistics; migrations, schema changes, new persistence, recurrence rebuilds, new endpoints, new dependencies, or new materialized data; board-orientation, side-to-move, or both-colour denominator behavior; new route-owned state; unrelated or historical edits; D1 reruns; aggregate/full-suite checks; commits; and pushes.

## Stages

1. **complete** - **Add the colour-correct all-games totals to the existing position-context contract.** Extend the backend response additively and derive each colour's denominator from accepted recurrence game rows within the accepted scope, grouped by stable repertoire colour. Preserve the existing position identity, reached-count meaning, `overall_exists` absent-position semantics, and zero-count behavior; do not make the denominator depend on orientation or side to move. Update the strict backend response and focused fixtures/assertions, then update the strict frontend response type/validator and only the bounded deterministic consumers that require the new fields. Preserve all D1 `effective_at` fields and unrelated fixture edits. Run proof (a) and (b). **Escalation boundary:** stop if the accepted recurrence row seam cannot provide the denominator without a migration, rebuild, new persistence, endpoint, identity change, or recurrence-semantics change, or if the additive public response shape is not settled by the approved contract. **Breakpoint:** none while the approved read-only contract remains sufficient.
2. **complete** - **Build the reusable model and component.** Add a pure model that accepts one selected repertoire colour and maps reached/denominator data into positive, available-zero, absent, and unavailable states with a safe bounded percentage. Add the component and styles under the new feature ownership, using existing CMT tokens/primitives and `Meter`; expose an accessible value/bar relationship and keep denominator selection independent of orientation and side to move. Add focused model and component tests for exact values, percentage/bar behavior, zero-versus-absent semantics, unavailable data, accessibility, and constrained width as appropriate. Run proof (c). **Escalation boundary:** stop for a new token, primitive, dependency, hierarchy, copy direction, route-owned state, simultaneous colour display, or any change to authoritative position or recurrence semantics. **Breakpoint:** none before the review surface is built.
3. **complete** - **Add the Storybook review surface and stop for human visual review.** Add independently discoverable stories for positive, zero, absent, unavailable, constrained-width, accessibility, forced-colour, and reduced-motion review states as appropriate, without route wiring or composition changes. Update Storybook discovery only if required. Use the explicit human visual-review breakpoint as proof of the review surface; do not add a Storybook build or repository-maintenance command. User edits at that breakpoint are authoritative and must be incorporated through the coordinator before continuation. **Escalation boundary:** stop for any requested product, visual, API, data, dependency, ownership, route, or acceptance decision outside the approved outcome. **Breakpoint:** human visual review completed and accepted.

Stages were executed sequentially with no parallel stages. Passing proof remained valid through user acceptance. Route integration remains outside this completed Plan.

## Progress and decisions

- **Stage 1:** complete - the backend and strict frontend contract carry colour-specific totals; focused API and client tests passed, and affected typed consumers built successfully.
- **Stage 2:** complete - the reusable model and component cover positive, available-zero, absent, unavailable, selected-colour, percentage, and accessible-meter behavior; focused tests passed.
- **Stage 3:** complete - the Storybook review surface built successfully and the user accepted the review outcome.
- **Decision:** The denominator is read-only and colour-correct: accepted recurrence game rows are counted by stable repertoire colour, not by board orientation or side to move.
- **Decision:** Existing position identity and existing zero-versus-absent semantics remain authoritative. An existing position with zero reaches is available at 0%; absent and unavailable states are not frequency zero.
- **Decision:** The component renders one explicitly selected repertoire colour and does not show both colours simultaneously.
- **Decision:** D1 product/tests and `effective_at` fixture updates are retained; D1 proof remains unaffected and is not rerun by this Plan.
- **Decision:** The user explicitly deferred size, lint, and similar maintenance checks and directed the workflow to move on after proving behavior; no maintenance-only repair is part of F1 acceptance.
- **Acceptance:** The user accepted the component outcome and explicitly requested that this Plan and D1 be closed out.

## Proof

- (a) Backend position-context regression: `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/position_context/test_api.py -q` (bash tool timeout: `150000` ms) - passed, `8 passed`.
- (b) Frontend strict position-context client regression: `timeout 120s npm.cmd test --prefix frontend -- --run --project=unit src/features/viewer/positionContextApi.test.ts` (bash tool timeout: `150000` ms) - passed, `15 passed`.
- (c) Reusable model/component regression: `timeout 120s npm.cmd test --prefix frontend -- --run --project=unit src/features/position-reach-frequency/positionReachFrequencyModel.test.ts src/features/position-reach-frequency/PositionReachFrequency.test.tsx` (bash tool timeout: `150000` ms) - passed, `11 passed`.
- A bounded typed-consumer build passed after the additive contract change: `timeout 180s npm.cmd run build --prefix frontend` (bash tool timeout: `210000` ms).
- The Storybook review surface built successfully: `timeout 300s npm.cmd run build-storybook --prefix frontend` (bash tool timeout: `360000` ms).
- No lint, formatting, source-size, aggregate, or full-suite command is required for acceptance. Component tests cover behavior; the pending human breakpoint covers visual acceptance.
- D1 proof remains retained and unaffected. This Plan does not rerun D1 or alter its active Plan, product/tests, or `effective_at` fixtures.

## Escalation boundaries

- Any migration, schema or persistence change, recurrence rebuild, materialized-data change, new endpoint, dependency, or change to accepted recurrence semantics or denominator ownership.
- Any change to the authoritative position identity, `overall_exists`, reached-count meaning, zero-versus-absent semantics, accepted recurrence scope, stable repertoire colour, board orientation, or side-to-move behavior.
- Any simultaneous both-colour presentation, route integration, route-owned state, PositionContext/GameContext/workspace replacement, or composition change in `/viewer` or `/repertoire`.
- Any new design token or primitive, visual hierarchy or copy direction, accessibility acceptance direction, destructive action, or other product/visual decision not already approved.
- Any collision with D1 edits or `effective_at` fixtures, unrelated failure or worktree change, historical-record edit,
  commit, push, or request to add maintenance work to this Plan. Source/test size violations are deferred maintenance.

## Visible result

> In Storybook, a person can choose one repertoire colour and verify its exact reached/all-games values, safe percentage/bar, and truthful positive, zero, absent, and unavailable states at wide and narrow sizes.
