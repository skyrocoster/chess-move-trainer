# Retire Viewer - `/viewer` becomes ordinary Not Found while Repertoire remains unchanged

> **Status:** done - accepted 2026-09-09; all four stages and the coordinator-approved focused proof passed.

- **Read trigger:** Read before implementing `VIEWER-REMOVE-01`, relocating retained Viewer-owned capabilities, or
  updating its focused proof.
- **Upstream:** [approved Viewer-removal direction](../../../grilling-docs/database-rebuild-viewer-removal.md),
  [database-rebuild master plan](../../../master-plans/database-rebuild/database-rebuild.md), and the retained
  assessment for this case.

## Outcome

Remove the production Viewer before any further clean API consumer migration. `/viewer` remains at its requested URL
and renders the ordinary in-shell Not Found view with no redirect, compatibility UI, or retirement message. Viewer
navigation, workspace behavior, Viewer-only exploratory play, and Viewer-only artifacts disappear. Capabilities still
needed by Repertoire move to neutral ownership without changing Repertoire's visible behavior or current legacy API
calls.

## Scope

- **Included:**
  - Relocate retained chess primitives to `frontend/src/features/chess/`.
  - Relocate `gameModel.ts`, `positionApi.ts`, `GameLoader.tsx`, `GameLoader.module.css`, and
    `stage1SourceSafety.ts` to `frontend/src/features/game/`.
  - Move `analysisApi.ts`, `analysisState.ts`, `analysisFormatting.ts`, and `evalBarDisplay.ts` into the existing
    `frontend/src/features/analysis/` ownership.
  - Move `positionContextApi.ts` and `positionContextState.ts` into `frontend/src/features/position-context/`.
  - Move `BoardControl.tsx` and `BoardEvalStage.tsx`, their styles, and their focused proof into the existing
    `frontend/src/features/board-adapter/` ownership.
  - Move retained stored-game fixtures to `frontend/src/features/game/`, retained game story helpers to
    `frontend/src/features/game/`, retained analysis story clients to `frontend/src/features/analysis/`, and the
    shared Storybook frame style to `frontend/src/storybook/StoryFrame.module.css`; rename retained fixture symbols
    away from Viewer ownership and delete Viewer-only helpers and fixtures.
  - Remove the Viewer route and navigation entry, delete the Viewer workspace/context/branch/terminal surface, and
    update focused App, shell, Repertoire, Storybook, routing, responsive-shell, E2E configuration, and E2E README
    proof surfaces.
  - Apply the direct `VIEWER-REMOVE-01` sequence edit to the database-rebuild master plan.
- **Expected areas:**
  - `frontend/src/App.tsx`
  - `frontend/src/features/analysis/README.md`
  - `frontend/src/features/{viewer,app-shell,analysis,board-adapter,repertoire-builder,chess,game,position-context,move-response-distribution,position-reach-frequency}/**/*`
  - `frontend/src/storybook/**/*`
  - `tests/e2e/{routing.spec.ts,responsive-shell.spec.ts,viewer*.spec.ts,playwright.config.ts,repertoire-builder-storybook.spec.ts,README.md}`
  - `docs/master-plans/database-rebuild/database-rebuild.md`
- **Excluded:** Repertoire redesign or new interaction; preservation of Viewer behavior; redirect, retirement page,
  fallback, or compatibility shim; generated clean API adoption; backend route retirement; old-database work; new
  dependencies or tools; broad cleanup; completed historical records; lint, formatting, broad type/build, source-size,
  aggregate maintenance, and repository-hygiene proof.

## Stages

1. **done - Relocate retained non-visual ownership** - Move chess primitives, game model/client/loader support,
   analysis logic, position-context API/state, retained fixtures, and focused unit support. Update every retained
   consumer while preserving the legacy game-position, position-context, evaluation, and preferred-move API calls.
   Do not remove the route or change runtime behavior in this stage.
   - **Focused proof:** From `frontend`, command timeout 120s and Bash tool timeout 130000ms:
     ```bash
     timeout 120s npm exec vitest -- --run --project unit --testTimeout=20000 src/features/chess/chessPrimitives.test.ts src/features/game/positionApi.test.ts src/features/game/GameLoader.test.tsx src/features/analysis/analysisApi.test.ts src/features/analysis/analysisState.test.ts src/features/analysis/analysisFormatting.test.ts src/features/analysis/evalBarDisplay.test.ts src/features/position-context/positionContextApi.test.ts src/features/position-context/positionContextState.test.ts
     ```
   - **Breakpoint:** Stop if a retained module is not covered by the approved ownership map, if behavior or an API
     call changes, or if clean generated client adoption becomes necessary.
2. **done - Relocate retained visual ownership and prove Repertoire units** - Move `BoardControl`, `BoardEvalStage`,
   their styles/tests/stories, and neutral Storybook frame support into board-adapter or neutral Storybook ownership.
   Update Storybook titles and all Repertoire/related imports without changing component contracts or visible behavior.
   - **Focused unit proof:** From `frontend`, command timeout 120s and Bash tool timeout 130000ms:
     ```bash
     timeout 120s npm exec vitest -- --run --project unit --testTimeout=20000 src/features/board-adapter/BoardControl.test.tsx src/features/board-adapter/BoardEvalStage.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/position-reach-frequency/PositionReachFrequency.test.tsx src/features/move-response-distribution/MoveResponseDistribution.test.tsx
     ```
   - **Breakpoint:** Stop if relocation changes Repertoire layout, board controls, analysis, position reach, move
     response, stored-game loading, or preferred-move behavior, or requires a new interaction or compatibility layer.
3. **done - Remove the production Viewer and reconcile route/shell proof** - Remove the Viewer lazy route and
   navigation entry; delete `frontend/src/features/viewer/` completely, including Viewer workspace, context,
   branch, terminal-message, Viewer-only styles, fixtures, tests, stories, and README. Remove dedicated Viewer
   Playwright specs, move generic Not Found coverage into bounded routing proof, and update App/AppShell,
   responsive-shell, E2E config, and E2E documentation.
   - **Focused unit proof:** From `frontend`, command timeout 120s and Bash tool timeout 130000ms:
     ```bash
     timeout 120s npm exec vitest -- --run --project unit --testTimeout=20000 src/App.test.tsx src/features/app-shell/AppShell.test.tsx
     ```
   - **Focused routing/shell proof:** From the repository root, command timeout 180s and Bash tool timeout 190000ms:
     ```bash
     timeout 180s npx playwright test --config tests/e2e/playwright.config.ts tests/e2e/routing.spec.ts tests/e2e/responsive-shell.spec.ts --grep "approved shell|drawer focus containment|Repertoire Builder route" --timeout=15000
     ```
   - **Breakpoint:** Stop if `/viewer` redirects, renders any compatibility surface, leaves a desktop or drawer
     Viewer link, or if the Viewer directory cannot be removed fully.
4. **done - Complete bounded audit and acceptance** - Update directly stale ownership signposts, record stage
   progress, rerun the focused Repertoire Storybook browser proof after the Stage 3 E2E configuration changes, and
   run a final bounded path/reference audit. Confirm no retained production, test, or configuration import points into
   Viewer, Repertoire proof remains valid after the configuration change, no clean operation was adopted, and backend
   legacy routes remain. The master-plan reconciliation is already part of this approved documentation change and is
   not deferred to product implementation.
    - **Focused Repertoire Storybook browser proof** (coordinator-approved scope narrowing: the five scenarios that
      directly exercise the retained visual/layout behavior affected by the ownership moves; stale pre-existing
      Preferred Move scenarios are excluded and reported, not absorbed): From the repository root, command timeout
      180s and Bash tool timeout 190000ms:
      ```bash
      timeout 180s npx playwright test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts --grep "browser evidence|container-width boundary|keyboard resizing|separator semantics|dense distribution label" --timeout=30000
      ```
    - **Bounded scope audit:** From the repository root, command timeout 30s and Bash tool timeout 40000ms:
      ```bash
      timeout 30s bash -lc 'test ! -d frontend/src/features/viewer && ! rg -n -F -e "features/viewer" -e "../viewer/" -e "./viewer/" frontend/src frontend/.storybook tests/e2e && ! rg --files tests/e2e | rg "/viewer[^/]*\\.spec\\.ts$"'
      ```
   - **Breakpoint:** Stop if any new production consumer, API migration, backend retirement, dependency, contract
     change, or behavior change is discovered. Do not absorb unrelated cleanup.

All stages are sequential. A passing proof remains valid until a later stage changes its command, inputs, exercised
behavior, configuration, dependencies, or environment; rerun only affected proof.

## Progress and decisions

- **Stage 1:** done - moved chess primitives to `features/chess/`; `gameModel`, `positionApi`(+test), `GameLoader`
  (+CSS/test), `stage1SourceSafety`, and neutral retained fixtures/helpers (`gameFixtures.ts` with `GAME`/`GAME_UUID`,
  `gameStoryFixtures.ts` with `PROMOTION_GAME`, `gameStoryHelpers.ts` with `completeGameLookup`) to `features/game/`;
  `analysisApi`/`analysisState`/`analysisFormatting`/`evalBarDisplay` (+tests) and retained analysis story clients
  (`analysisStoryClients.ts`) to `features/analysis/`; `positionContextApi`/`positionContextState` (+tests) to
  `features/position-context/`. Viewer-only fixture/helper remainders stayed in `features/viewer/` for later deletion;
  every retained Viewer and Repertoire import was reconciled and the legacy games-positions, position-context, and
  evaluation HTTP calls are unchanged; `BoardControl`/`BoardEvalStage` and the Viewer route remain untouched.
  Focused proof passed: 9 test files, 82 tests, ~12.7s. Breakpoint not hit.
- **Stage 2:** done - moved `BoardControl`/`BoardEvalStage` (components, CSS, focused tests, focused stories) into
  `features/board-adapter/`; moved/renamed `Stage1Story.module.css` to `src/storybook/StoryFrame.module.css` and
  updated all eight story imports; renamed the two retained story titles from `Application/Viewer/...` to
  `Application/Board Adapter/...`; reconciled `ViewerWorkspace`, `RepertoireBoardLane`, and the
  `RepertoireBoardLane.test.tsx` mock paths. Component contracts, props, behavior, and visible output are unchanged.
  Focused proof passed: 8 test files, 92 tests, ~19.9s. Stage 1 proof inputs untouched, so it remains valid.
  Breakpoint not hit.
- **Stage 3:** done - removed the Viewer lazy import and `/viewer` route from `App.tsx` and the Viewer `NavLink` from
  `AppShell.tsx` (desktop and drawer share `NavigationItems`); `/viewer` now falls through to the existing
  `PageNotFoundView` with no redirect or compatibility surface. Deleted `frontend/src/features/viewer/` completely
  and the five dedicated Viewer Playwright suites; removed only their entries from `playwright.config.ts` and the
  spec-coverage line in `tests/e2e/README.md`; added `tests/e2e/routing.spec.ts` proving `/viewer` keeps its URL and
  renders ordinary in-shell Not Found with no Viewer links; updated `responsive-shell.spec.ts` to assert Viewer-link
  absence on desktop/drawer while keeping Repertoire navigation and drawer focus/dismissal behavior. Focused unit
  proof passed: 2 files, 11 tests, ~5.8s. Focused routing/shell proof passed: 4 scenarios, ~12.6s (approved shell,
  drawer focus containment, Repertoire Builder route, `/viewer` ordinary Not Found). Stage 1 and 2 unit-proof inputs
  untouched, so both remain valid. Breakpoint not hit; stale signposts (analysis README prose, Storybook viewer
  stories glob in `.storybook/main.ts`) intentionally left for Stage 4.
- **Stage 4:** done - reconciled the stale `analysis/README.md` ownership prose, removed the empty Viewer stories
  glob from `.storybook/main.ts` (also removes its startup warning), corrected a stale test title in
  `positionContextState.test.ts` (title only; no assertion change), and corrected the bounded audit command to
  include `frontend/.storybook`. The corrected bounded audit PASSED (Viewer directory absent; no `features/viewer`,
  `../viewer/`, or `./viewer/` references in `frontend/src`, `frontend/.storybook`, or `tests/e2e`; no dedicated
  Viewer E2E spec remains); the continuation edited only the Plan, so the audit remains valid without rerun. Under
  the coordinator-approved proof-scope narrowing, the filtered Repertoire Storybook browser command cleanly passed
  its five selected direct scenarios in one run (5 passed, ~15.4s): representative wide/medium/narrow geometry
  evidence, exact container-width boundary transitions, keyboard resizing/focus/minimums/reset, separator semantics
  in forced-colors and reduced-motion, and dense distribution label readability. The earlier broad Storybook
  command (all 16 scenarios) is recorded as non-acceptance evidence, not a passing proof: 5 passed / 11 failed in
  ~1.5m, where the 11 failures are pre-existing stale assertions locating the removed
  "What is saved, and what is staged?" region and the effective-date/save-label UI that commit `ec224d6`
  (2026-09-03, before this Plan) removed when redesigning `PreferredMovePanel` without updating this spec; those
  unrelated failures were reported to the coordinator, not repaired or absorbed. Legacy clients verified still
  calling `api/games/{uuid}/positions`, `api/position-context`, `api/evaluation(/status)`, `api/preferred-move`,
  and `api/move-response-distribution`; backend untouched; no dependency, generated-client, or behavior change.
  Stage 1-3 unit/routing proof and the Stage 4 audit remain valid.
- **Decisions:** The approved neutral destinations and stable slice identifier `VIEWER-REMOVE-01` are settled. No
  design fidelity section is required; this is a behavior and ownership removal Plan, not a visual redesign.
  Coordinator-approved Stage 4 proof-scope correction: the Repertoire Storybook browser proof is narrowed to the
  five scenarios that directly exercise the retained visual/layout behavior affected by the ownership moves; the
  stale Preferred Move scenarios belong to the `ec224d6` panel redesign, not this Plan, and remain reported as
  unrelated failures.

## Proof

- Moved chess, game loading, analysis, position-context, BoardControl, and BoardEvalStage unit tests, using only the
  finite Stage 1 and Stage 2 Vitest commands above.
- Focused Repertoire workspace/workflow/model, position reach, and move-response unit tests.
- Focused Repertoire Storybook browser proof over the five coordinator-approved direct scenarios of
  `tests/e2e/repertoire-builder-storybook.spec.ts` (geometry evidence, boundary transitions, keyboard resizing,
  separator semantics, dense distribution labels), rerun in Stage 4 after the Stage 3 E2E configuration changes.
- App/AppShell unit proof for removed route and navigation.
- Bounded routing and responsive-shell Playwright proof for URL preservation, ordinary Not Found, absent Viewer links,
  and retained Repertoire routing.
- Final bounded path/reference audit proving `frontend/src/features/viewer/` is absent and no retained source or E2E
  import/spec points into it. This is scope evidence, not repository-hygiene proof.
- No clean generated operation is adopted; the moved game client continues using the legacy game-position route, and
  no backend route is removed.

## Escalation boundaries

- Escalate if an additional production consumer of Viewer is found.
- Escalate if Repertoire behavior or a public component/API contract must change rather than moving ownership.
- Escalate if `getGame()` or another clean generated operation is adopted in this slice.
- Escalate if backend route retirement, old-database work, a dependency/tool, or a compatibility layer is proposed.
- Escalate if `frontend/src/features/viewer/` cannot be deleted completely.
- Escalate any new product, visual, data, destructive, ownership, dependency, or acceptance decision.

## Visible result

> A visitor entering `/viewer` sees the normal “Page not found” screen, while Repertoire still behaves exactly as before.
