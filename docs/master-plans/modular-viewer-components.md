# Modular viewer components

> **Status:** direction settled

## Destination

Turn the current position viewer into one page-owned composition of generic, controlled, independently
testable, and independently designable visible components that can support future page-specific workflows
without becoming a universal viewer, session, game, opening, or tree framework.

## Settled direction

- `ViewerWorkspace` owns loading, selected position, timeline traversal, temporary-branch state, analysis
  state, announcements, and the exact current page layout. Visible components receive display data or
  capabilities and emit user intentions; they do not own the viewer workflow.
- Establish small shared chess primitives first, then keep separate game, temporary-branch, and analysis
  workflow models. Do not create one universal game/opening/tree model or universal session API.
- As part of MVC-01's shared-primitive foundation, frontend-only legacy adapters, types, and mocks with no
  production or genuinely general/reusable role may be retired. Frontend production contracts and genuinely
  general/reusable states and variants, including warning/error states, remain protected even when currently
  unused; all backend API contracts and observable viewer behavior remain unchanged. This is directional only:
  a later focused MVC-01 Plan must prove consumer classification and regression safety before removing anything.
- Preserve the whole-game route, the legacy per-ply route, the typed payloads and errors, the existing
  `AnalysisClient` endpoint behavior, and all current viewer and analysis semantics. No backend change,
  endpoint versioning, universal tree endpoint, or speculative opening/picker endpoint is in scope.
- Extract or refine one visible component at a time with no redesign: preserve appearance, layout,
  responsive container behavior, keyboard/focus behavior, live announcements, source safety, motion
  preferences, and accessibility. Each stage must have focused tests, comprehensive Storybook states and
  interactions with relevant accessibility coverage, viewer integration proof, and reconnection before
  the next component is selected.
- Shared semantic foundations remain global only when genuinely semantic or repeated. Component geometry
  remains local; consolidation must not visibly change the UI. No new dependency is permitted.
- The approved page-ownership move is limited to this page-specific composition. Escalate any proposed
  change to behavior, contracts, dependencies, ownership outside the page, destructive effects, visual
  direction, or speculative abstractions before proceeding.

## Selectable slices

| Slice | Human-visible result | Depends on | Explicit exclusion |
|---|---|---|---|
| MVC-01 Foundations | The current viewer still behaves as it does now, backed by small shared chess primitives and separate game, branch, and analysis workflow models. | none | No component decoupling, redesign, endpoint change, backend change, or universal model. |
| MVC-02 Game loader | The existing Game Loader is a controlled reusable form with the same validation, loading, failure, reset, disclosure, and accessibility behavior. | MVC-01 | No request, abort, lookup, or page workflow logic inside the reusable form. |
| MVC-03 Static board | The existing `BoardAdapter` is independently usable as a controlled static-position display with identical rendering, orientation, coordinates, descriptions, fallback, and accessibility behavior. | MVC-02 | No interactive movement, branch policy, or visual redesign. |
| MVC-04 Promotion picker | The existing `PromotionPicker` has a confirmed controlled visible boundary and retains identical popover/drawer, focus, live-region, stale/illegal, and accessibility behavior. | MVC-03 | No branch policy, timeline state, or new promotion workflow. |
| MVC-05 Interactive branch board | The current interactive board and temporary-branch presentation remain visually and behaviorally identical while rendering and user intentions are separated from page-owned branch workflow logic. | MVC-04 | No change to chess mutation, SAN/FEN summaries, terminal detection, promotion semantics, or branch lifetime. |
| MVC-06 Navigation controls | The current toolbar remains identical while its visible contract is capability/callback based and owns no timeline state or ply-boundary arithmetic. | MVC-05 | No playback, skip, flip, or new navigation behavior. |
| MVC-07 Evaluation bar | The current evaluation bar is an independently designable controlled display of derived analysis state, with identical orientation, neutral/pending/best-line states, meter values, and accessible text. | MVC-06 | No analysis client, polling, enqueue action, or analysis ownership in the visible component. |
| MVC-08 Analysis panel | The current analysis presentation is a controlled component that displays the same missing, queued, running, complete, stale, failed, error, terminal, and retry/update states and emits the same deliberate intentions. | MVC-07 | No endpoint contract, analysis semantics, automatic action, or speculative analysis workflow. |
| MVC-09 Game context | Game metadata, safe source attribution, position disclosure, and analysis presentation have separate controlled boundaries while retaining the current grouping, order, copy, and layout. | MVC-08 | No new metadata, source behavior, opening model, or universal slot framework. |
| MVC-10 Page composition lock | `ViewerWorkspace` is visibly the same page-specific composition, with all extracted parts reconnected and page-owned state, exact layout, responsive behavior, and announcements preserved. | MVC-09 | No new page, product behavior, visual direction, universal framework, endpoint, dependency, or layout redesign. |

## Slice results

- **MVC-01:** [Completed MVC-01 Foundations Plan/result](../plans/done/mvc-01-foundations/mvc-01-foundations.md).
- **MVC-02:** [Completed MVC-02 Game loader Plan/result](../plans/done/mvc-02-game-loader/mvc-02-game-loader.md).
- **MVC-03:** [Completed MVC-03 Static board Plan/result](../plans/done/mvc-03-static-board/mvc-03-static-board.md).
- **MVC-04:** [Completed MVC-04 Promotion picker Plan/result](../plans/done/mvc-04-promotion-picker/mvc-04-promotion-picker.md).
- **MVC-05:** Focused Plan/result link reserved for later selection and acceptance.
- **MVC-06:** Focused Plan/result link reserved for later selection and acceptance.
- **MVC-07:** Focused Plan/result link reserved for later selection and acceptance.
- **MVC-08:** Focused Plan/result link reserved for later selection and acceptance.
- **MVC-09:** Focused Plan/result link reserved for later selection and acceptance.
- **MVC-10:** Focused Plan/result link reserved for later selection and acceptance.

## Directional acceptance and evidence

MVC-01 is mandatory and precedes every visual-component slice. Its expected evidence areas are the current
`frontend/src/features/viewer/stage1GameTypes.ts`, `positionApi.ts`, `positionLookup.ts`, `analysisApi.ts`,
`analysisState.ts`, and the branch-related types in `frontend/src/features/board-adapter/`. It must preserve
the whole-game `GET /api/games/{game_uuid}/positions` contract with optional `ply`, the legacy
`GET /api/games/{game_uuid}/positions/{ply}` contract, and the evaluation observation/enqueue/status
contracts. Contract evidence remains in `backend/app/features/positions/router.py`,
`backend/tests/features/positions/test_positions.py`, `backend/app/features/evaluation/router.py`, and
`backend/tests/features/evaluation/test_api.py`; these are not implementation targets for this destination.
The current `ViewerWorkspace.test.tsx`, `ViewerWorkspaceBranch.test.tsx`, `ViewerWorkspace.stories.tsx`,
and relevant viewer end-to-end coverage must still prove the unchanged viewer before MVC-02 begins.

For MVC-02 through MVC-09, each focused Plan must select one row only and define exact ordered actions and
proof commands. The directional acceptance boundary for every row is:

1. Refine or extract the named visible component behind a controlled, reusable interface without changing
   its appearance or behavior.
2. Retain or add focused component tests and comprehensive Storybook stories for meaningful states,
   interactions, keyboard/focus behavior, and relevant accessibility checks.
3. Reconnect it to the current viewer and prove through viewer integration tests that extraction is
   behaviorally invisible before selecting the next row.

The precise source, focused-test, story, and integration surfaces are:

- **MVC-02:** `viewer/GameLoader.tsx`, `GameLoader.module.css`, `GameLoader.test.tsx`, and
  `GameLoader.stories.tsx`; reconnect through `ViewerWorkspace.tsx`, `ViewerWorkspace.test.tsx`,
  `ViewerWorkspace.stories.tsx`, and existing viewer Storybook end-to-end coverage. Preserve the current
  UUID/Ply validation, typed failure copy, loading status, reset, and constrained state.
- **MVC-03:** `board-adapter/BoardAdapter.tsx`, its module CSS, test, and stories; reconnect through the
  static-board path in `ViewerWorkspace.tsx` and its integration tests/stories, with existing
  `tests/e2e/board-adapter-storybook.spec.ts` coverage retained. Preserve invalid-position fallback,
  generated descriptions, `useId` accessibility wiring, orientation, coordinates, and disclosure behavior.
- **MVC-04:** `board-adapter/PromotionPicker.tsx`, its module CSS, test, and stories; retain the
  `usePromotionController` only as a narrowly justified chess helper if the selected focused Plan confirms
  it. Exercise both presentation primitives, selection, cancellation, focus restoration, stale/illegal
  rejection, live announcements, and axe coverage through the existing promotion and branch surfaces.
- **MVC-05:** `board-adapter/InteractiveBoardAdapter.tsx`, its module CSS, test, and stories, plus
  `viewer/ViewerWorkspaceBranch.test.tsx` and branch stories. Preserve the current branch snapshot,
  reset-token and captured-ply behavior, legal/illegal movement, SAN/FEN output, terminal classification,
  promotion integration, accessibility labels, and the existing `tests/e2e/viewer-branch*.spec.ts` proof.
- **MVC-06:** `viewer/BoardControl.tsx`, its module CSS, test, and stories, plus the navigation assertions
  in `ViewerWorkspace.test.tsx` and `ViewerWorkspace.stories.tsx`. Preserve toolbar semantics, labels,
  focus movement, disabled states, empty state, loading gate, and temporary-branch gate while removing
  timeline ownership from the visible contract.
- **MVC-07:** `viewer/EvalBar.tsx`, its module CSS, test, and stories, with the analysis display derivation
  kept outside the visible component and the shared-observation assertions retained in `ViewerWorkspace.test.tsx`.
  Preserve neutral, queued/running, completed, stale/failed, orientation, meter, and accessible-value states.
- **MVC-08:** `viewer/AnalysisPanel.tsx`, `analysisFormatting.ts`, its module CSS, test, and stories, with
  `analysisState.ts` and `AnalysisClient` remaining workflow/API seams rather than visible-component state.
  Preserve deliberate Analyze/Update/Retry actions, observation retry, queue polling, five ranked lines,
  SAN formatting, WDL/score text, terminal empty results, errors, and accessibility coverage.
- **MVC-09:** `viewer/GameContext.tsx`, `stage1SourceSafety.ts`, its module CSS, test, and stories, plus
  the context-area integration in `ViewerWorkspace.tsx`. Keep metadata/source/disclosure presentation
  separate from `AnalysisPanel` without changing the current visual location, default-open behavior, safe
  source link rules, empty state, Ply/SAN copy, or accessibility semantics.
- **MVC-10:** `viewer/ViewerWorkspace.tsx`, `ViewerWorkspace.module.css`, its tests/stories, branch tests,
  `tests/e2e/viewer-storybook.spec.ts`, and the existing branch end-to-end specs. Prove the same whole-game
  loading, legacy compatibility, traversal, temporary branch, analysis, layout, container-query, reset,
  failure-preservation, announcement, and accessibility behavior. Existing hardcoded reusable-instance IDs
  may change only when mechanically required by an approved reusable boundary and covered by that proof.

## Exclusions

- No visual redesign, new page, new product behavior, or page layout change beyond mechanical wiring.
- No universal game/opening/tree/session model, universal viewer framework, slot framework, speculative
  opening-tree or picker API, or speculative endpoint.
- No endpoint path, query, payload, typed-error, analysis-semantic, temporary-branch-semantic, or frontend
  production position-contract change.
- No backend behavior change, dependency addition, database change, destructive cleanup, rewrite of
  completed Plans or historical records, or modification of unrelated worktree changes.
- No globalization of component geometry, no new visual token direction, and no change to fonts, colors,
  typography, focus treatment, motion preferences, common controls, or other semantic foundations except
  to preserve or mechanically reuse the existing global foundations.
