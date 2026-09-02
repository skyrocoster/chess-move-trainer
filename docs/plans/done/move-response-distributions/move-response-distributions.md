# Move response distributions - Repertoire Builder shows common replies with an honest tail

> **Status:** Complete - all three stages accepted and the Plan is archived

- **Read trigger:** Read before implementing or resuming any stage of the move-response distribution feature. Do not
  begin a later stage until the preceding stage's focused proof and acceptance are recorded here.
- **Upstream:** [`docs/grilling-docs/move-response-distributions.md`](../../../grilling-docs/move-response-distributions.md)
  and the signed-off 01C repository-aware hand-off at
  [`experiments/mock-ups/move-response-distributions/DESIGN.md`](../../../../experiments/mock-ups/move-response-distributions/DESIGN.md).
  The mock-up source is visual evidence only; neither upstream artifact authorizes implementation by itself.

## Outcome

Add a reusable move-response distribution feature first to `/repertoire`. For the current canonical position and
selected repertoire colour, the backend supplies normalized replies and distinct-game counts. A reusable frontend
composition then presents the signed-off focused 01C chart/list, explicit loading/no-games/unavailable states, the top
five replies, and a disclosure-only `Other` tail. A playable reply uses the existing Repertoire Builder move path and
does not create a second board, preview path, or repertoire mutation.

## Scope

- **Included:**
  - A dedicated read-only `GET` API accepting `fen` and `color=white|black`, with a strict normalized response containing
    the canonical parent FEN, selected colour, matching-game count, complete deterministically ranked move replies,
    canonical child UCI, backend-derived SAN, distinct-game-per-child counts, and nullable reliable opening names.
  - Backend validation of the accepted recurrence scope and the four-field position identity. Query move rows from
    `opening_recurrence_branch_projection` with `branch_kind='move'` and the selected colour; use the corresponding
    selected-colour position projection for the denominator. A zero result is successful data.
  - Reusable frontend transport, request lifecycle, pure grouping/percentage model, chart adapter, text controls,
    disclosure, and panel composition. The reusable panel accepts generic data and a move-selection callback and must
    not import or otherwise depend on Repertoire Builder.
  - `/repertoire` wiring beside `PositionReachFrequency`, using the current canonical session position and
    `session.bottomColor`, and dispatching selected UCI through `handleMoveIntent`/`applyMove`.
  - Focused component, API/model, workspace, Storybook, and browser proof for keyboard semantics, live status,
    forced colors, reduced motion, and the 412px breakpoint.
- **Expected areas:**
  - `backend/app/features/move_response_distribution/**`, `backend/app/main.py`, and
    `backend/tests/features/move_response_distribution/**`.
  - `frontend/src/features/move-response-distribution/**` for the reusable feature boundary.
  - `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx`,
    `RepertoireSessionPanel.tsx`, their focused tests/stories/helpers, and the existing
    `tests/e2e/repertoire-builder-storybook.spec.ts` proof seam.
  - `frontend/package.json` only if an already-declared chart dependency decision demonstrably requires an authorized
    change; no dependency change is presumed.
- **Excluded:** Viewer integration; mock-up framing, exploration chrome, simulated-corpus labels, and separate board;
  recommendation or engine ranking; raw-event counts; global game de-duplication; repertoire mutations; database
  schema/publication changes; invented opening-family placeholders; unrelated refactors; and a new cross-feature
  design-system primitive unless separately authorized.

## Design fidelity

- **Authority:** `DESIGN.md` governs signed-off 01C visual composition and repository-aware interaction meaning;
  `move-response-distributions.md` governs settled product semantics. Production translation uses the existing CMT
  Material tokens, CSS Modules, and Repertoire Builder panel ownership.
- **Excluded artifact content:** mock-up hero/framing copy, exploration stamp, simulated data labels, raw CSS values,
  demo reset/workbench controls, and its separate preview board.

| Anchor | Preserve | Allowed adaptation | Acceptance |
|---|---|---|---|
| 01C grouped-tail composition | Classic labelled pie with up to five ranked SAN replies and one grey `Other` sector only when a tail exists; equivalent text controls remain complete. | Use the selected chart implementation or a feature-owned chart adapter, CMT roles, production copy, and returned data. | Stage 2 component stories/tests show available data, five-plus-tail, and no-tail variants without making the chart the only interaction path. |
| Other and playable replies | `Other` discloses/hides tail replies and is never a move; common and tail controls select the same UCI. | Use existing button/disclosure primitives or equivalent token-driven controls. | Stage 2 tests prove `aria-expanded`/`aria-controls`, focus behavior, `aria-pressed`, and shared callbacks; Stage 3 proves the existing move path. |
| Existing session context | Place the card alongside `PositionReachFrequency`; retain the existing board, line, controls, analysis, and session ownership. | Candidate insertion is immediately after `PositionReachFrequency`, subject to the required visual breakpoint. | Stage 3 coordinator/user review confirms hierarchy and insertion in the existing session panel; no mock-up board or page-specific reusable panel is accepted. |
| States and responsive reading order | Loading clears stale replies, no-games has no empty chart/Other, unavailable offers retry, and text controls are the reliable reading path. | Use existing state/live-region patterns and responsive stage constraints. | Stage 3 browser proof covers wide, medium, 412px, no overflow, forced colors, reduced motion, visible focus, and readable wrapping. |

## Stages

1. **complete/accepted - Backend/API and focused backend tests:**
   1. Record the exact route and error-code names using the existing `/api` router and `{code,message}` envelope
      conventions. The route remains a dedicated read-only endpoint; invalid input is 422, unavailable accepted data
      is 503, unexpected failures are 500, and no-games remains a 200 response. Do not start frontend work before this
      decision and implementation are accepted.
   2. Add the bounded backend feature package and register its router. Reuse `canonical_fen` and the four-field key,
      validate `color`, require the accepted recurrence tables/state, query the selected-colour parent count and all
      selected-colour move branches, rank by descending `distinct_game_count` then stable UCI, and preserve overlap
      between child branches.
   3. Normalize each child UCI and derive SAN from the canonical parent position with the existing python-chess
      validation approach. Treat malformed or illegal accepted projection data as unavailable rather than exposing
      unnormalized data.
   4. Keep `opening_name` nullable. During this stage, test whether an already accepted classification/catalog join can
      associate a name deterministically; use a name only when that reliability condition holds and return `null`
      otherwise. Do not add classification tables or infer a family from a partial match.
   5. Add an isolated SQLite fixture and focused API tests for valid White/Black requests, counter-field identity
      invariance, stable tie ranking, distinct branch counts including repeated-parent overlap, zero/no rows, invalid
      FEN/colour, missing or incompatible data, strict errors, and read-only/no-sidecar behavior.
   - **Focused proof:** `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/move_response_distribution -q --maxfail=1`
     (command timeout 120s; tool timeout 130000ms).
   - **Breakpoint and escalation:** Stage acceptance requires the backend proof to pass and the route/error and optional
     classification decisions to be recorded. Escalate if the accepted data cannot support the contract without a
     schema/publication change, new data semantics, global de-duplication, or an unapproved API contract.

2. **complete/accepted - Reusable frontend feature and focused frontend proof:**
   1. Add a feature-owned transport client with strict response/error parsing, canonical parent identity checks, colour
      checks, and abort support. Add lifecycle state that clears old data on FEN/colour replacement, prevents stale
      responses from overwriting the current request, and exposes loading, available, no-games, and unavailable states
      with retry for the current key.
   2. Add a pure model that computes percentages from `distinct_game_count / matching_game_count`, preserves supplied
      stable rank, keeps ranks 1-5 individual, groups every remaining row into `Other`, omits `Other` without a tail,
      and never describes overlapping branch percentages as mutually exclusive games.
   3. Add reusable, compositionally bounded presentation pieces: a chart adapter, equivalent accessible response
      controls, disclosure/tail region, and the stateful distribution panel. The panel receives generic position/colour
      context and callbacks; it must not know `RepertoireBuilderWorkspace`, `applyMove`, repertoire records, or Viewer.
   4. Use CMT Material roles, CSS Modules, visible focus, keyboard buttons, `aria-pressed`, `aria-expanded`,
      `aria-controls`, and one suitable live/status region. At 412px and below, stack chart and controls, allow
      secondary text to wrap, preserve SAN/count/percentage readability, and prevent horizontal overflow. Respect
      forced colors and reduced motion.
   5. Add focused model/API/state/component tests and Storybook stories for available with tail, available without tail,
      loading, no-games, unavailable/retry, nullable names, stale replacement, keyboard/disclosure behavior, and
      constrained-width accessibility.
   - **Focused proof:** `timeout 120s npm.cmd exec --workspace frontend -- vitest run src/features/move-response-distribution src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --maxWorkers=1`
     (command timeout 120s; tool timeout 130000ms).
   - **Breakpoint and escalation:** Before implementation settles the chart, confirm whether the existing Recharts
      declaration is appropriate for this repository-owned production feature without manifest promotion or accessibility
      compromise. Otherwise use a feature-owned implementation only if it preserves 01C; escalate any dependency
      installation/promotion or cross-feature design-system primitive. Stage 2 must pass before page integration.

3. **complete/accepted - Repertoire integration, visual breakpoint, and focused live proof:**
   1. Pass the current canonical `session.currentPosition.fen`, `session.bottomColor`, and the new client through the
      workspace/session-panel composition. Insert the reusable panel at the candidate position beside
      `PositionReachFrequency`; keep board, current line, analysis, status, preferred-move workflow, and mutation
      ownership unchanged.
   2. Adapt UCI selection to the existing `handleMoveIntent`/`applyMove` seam, including staged-owner and immediate-
      opponent behavior. Selecting a new canonical position clears the old distribution selection; the panel must never
      directly mutate repertoire data. `Other` only toggles disclosure.
   3. Add deterministic workspace/session stories and focused regression tests for request keys, colour flips, position
      replacement, stale/abort handling, common/chart parity, tail selection, no-games/unavailable states, and
      preservation of existing history/preferred-move behavior.
   4. At the required coordinator/user visual breakpoint, review the integrated `/repertoire` result at wide, medium,
      and 412px widths. Confirm the candidate insertion, 01C hierarchy, production copy, readable stacked mobile order,
      forced-colors/reduced-motion treatment, and no horizontal overflow. Bounded user edits at this breakpoint are
      authoritative; changes to semantics, API, dependency, ownership, Viewer scope, or acceptance return to the
      coordinator.
   5. Run the focused Storybook browser scenario and retain its proof only until a later affecting change invalidates it.
   - **Focused proof:** `timeout 180s npm.cmd exec -- playwright test tests/e2e/repertoire-builder-storybook.spec.ts --config=tests/e2e/playwright.config.ts --grep "response distribution"`
     (command timeout 180s; tool timeout 190000ms). The scenario must cover 1280px, 800px, 412px, keyboard operation,
     accessibility scan, forced colors/reduced motion, and document/panel overflow.
   - **Breakpoint and escalation:** Final Stage 3 acceptance requires the coordinator/user visual confirmation and the
      focused browser proof. Escalate any request for Viewer integration, a separate board/preview, recommendation
      behavior, mutation changes, global de-duplication, a changed 412px requirement, or a changed 01C direction.

## Progress and decisions

- **Stage 1:** complete/accepted - dedicated route `GET /api/move-response-distribution`; error codes `invalid_fen`, `invalid_color`, `move_response_distribution_unavailable`, and `unexpected_failure`; `opening_name` remains nullable/null because no reliable deterministic existing lookup exists. Proof: `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/move_response_distribution -q --maxfail=1` from the workspace root (command timeout 120s; bash tool timeout 130000ms), result **12 passed**. Establishes canonical FEN/four-field identity and White/Black colour handling, strict success/error envelopes and validation, deterministic complete ranking with SAN/UCI normalization, zero matching-game/reply data, unavailable/incompatible data handling, distinct-per-child repeated-parent overlap semantics without global de-duplication, and read-only/no-sidecar behavior.
- **Stage 2:** complete/accepted - used the already-declared Recharts dependency without manifest promotion or a new dependency; the reusable feature-owned transport, model, lifecycle, chart, controls, disclosure, and panel remain independent from Repertoire Builder. Proof: `timeout 120s npm.cmd exec --workspace frontend -- vitest run src/features/move-response-distribution src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx --maxWorkers=1` from the workspace root (command timeout 120s; bash tool timeout 130000ms), result **56 passed** across 5 test files. Establishes strict response/error parsing and canonical four-field identity checks, loading/available/no-games/unavailable states, abort and stale-result replacement, retry, supplied-rank top-five/tail grouping, overlap-safe denominator percentages, nullable opening names, shared UCI selection callbacks, disclosure-only `Other`, keyboard/ARIA behavior, accessibility, constrained layout, forced-colors, and reduced-motion boundaries.
- **Stage 3:** complete/accepted - the user signed off the remaining product and visual decisions. The reusable panel is integrated immediately after `PositionReachFrequency`, keyed to the displayed canonical position and `session.bottomColor`, and routes reply UCI through the existing move-intent/apply path while leaving `Other` disclosure-only. Focused frontend proof: `timeout 120s npm.cmd exec --workspace frontend -- vitest run src/features/move-response-distribution src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.moveResponseDistribution.test.tsx --maxWorkers=1` from the workspace root (command timeout 120s; bash tool timeout 130000ms), result **72 passed** across 9 files. The Plan's `npm.cmd exec` browser invocation could not spawn under the Windows shell because the resolved `C:\Program Files\...` command was split; the repository-equivalent direct Playwright invocation `timeout 180s npx playwright test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "response distribution"` (command timeout 180s; bash tool timeout 190000ms) passed **1 test** in 32.1 seconds. Browser evidence covers 1280px, 800px, and 412px, keyboard selection and disclosure, accessibility scan, forced colors, reduced motion, and document/panel overflow. Inspected screenshots preserve the signed-off 01C hierarchy, grey disclosure-only tail, production context, readable mobile stacking, and existing single-board session ownership.

Passing behavioral proof remains valid until a later change affects its command, inputs, exercised behavior, configuration,
dependencies, or environment. No lint, formatting, broad type/build, aggregate, or maintenance check is part of this
Plan.

## Proof

- Backend API/model proof covers canonical position and colour inputs, strict success/error envelopes, stable ranking,
  distinct-per-child overlap semantics, optional names without placeholders, zero data, unavailable data, and read-only
  behavior.
- Frontend focused proof covers strict transport parsing, request replacement/abort, grouping and percentages, all four
  visible states, chart/list callback parity, disclosure semantics, keyboard/focus/live-region behavior, and existing
  workspace regression behavior.
- Browser proof covers integrated Repertoire Builder behavior at wide, medium, and 412px widths, no horizontal
  overflow, forced colors, reduced motion, accessibility, and the required visual breakpoint.

## Escalation boundaries

- Exact endpoint path and error-code names, or response fields beyond the settled contract, if they cannot be selected
  from existing repository conventions.
- Any required schema/publication change, new data source, global game de-duplication, or non-null/invented opening
  classification.
- Installing or promoting a chart dependency, or adding a cross-feature design-system primitive rather than a
  feature-owned reusable boundary.
- A conflict over the candidate session-panel insertion, 01C visual fidelity, 412px behavior, accessibility semantics,
  page ownership, Viewer scope, board/preview behavior, or repertoire mutation semantics.

## Visible result

> On `/repertoire`, a learner can see the five common replies and disclose the remaining tail for the current position,
> then play any listed reply through the existing Repertoire Builder flow without stale data or page overflow.
