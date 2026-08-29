# Repertoire Builder scaffold - `/repertoire` opens a Viewer-style standard-start workspace

> **Status:** accepted/done - R2 complete; fresh final Quality validation passed and the Plan is archived

- **Read trigger:** Read before each R2 execution stage, before changing the `/repertoire` route, shared navigation,
  repertoire page shell, or its focused proof, and at final closeout.
- **Upstream:** [Repertoire Builder master plan](../../../../master-plans/repertoire-builder/repertoire-builder.md);
  [confirmed Repertoire Builder direction](../../../../grilling-docs/DONE/repertoire-builder-direction.md);
  [accepted V1 Viewer Flip/navigation Plan](../../../../plans/done/repertoire-builder/viewer-flip-navigation/viewer-flip-navigation.md);
  [accepted V2 Viewer position-count Plan](../../../../plans/done/repertoire-builder/viewer-position-count/viewer-position-count.md);
  [accepted V3 clickable-analysis-moves Plan](../../../../plans/done/repertoire-builder/viewer-clickable-analysis-moves/viewer-clickable-analysis-moves.md);
  [accepted R1 reusable UTC calendar Plan](../../../../plans/done/repertoire-builder/reusable-utc-calendar/reusable-utc-calendar.md)

## Outcome

Add the first thin Repertoire Builder page surface at `/repertoire`. The page has a Repertoire Builder heading, uses the
shared application chrome and active desktop/drawer navigation, follows the established Viewer workspace's responsive
and token conventions, and opens with the standard starting `BoardAdapter` position with White at the bottom.

The AppShell owns application chrome and navigation; the repertoire page owns its workspace layout. This slice creates no
workflow state or temporary contracts. Existing `/`, `/viewer`, and unmatched-route behavior remains unchanged.

## Scope

- **Included:** The `/repertoire` route; one shared navigation entry labeled Repertoire Builder in the existing desktop
  and drawer navigation paths; a page-specific repertoire shell; the standard starting FEN through the existing
  `BoardAdapter` boundary with White orientation and the established accessible board-label convention; local page
  layout styling only where needed to follow the accepted Viewer responsive/container conventions; focused route,
  navigation, shell, accessibility, and responsive proof; one page-specific Storybook story; and a bounded extension of
  the existing application responsive-shell browser proof.
- **Expected areas:** `frontend/src/App.tsx`, `frontend/src/App.test.tsx`,
  `frontend/src/features/app-shell/AppShell.tsx`, `frontend/src/features/app-shell/AppShell.test.tsx`,
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx`,
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.module.css` only if local styling is needed,
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`,
  `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.stories.tsx`,
  `tests/e2e/responsive-shell.spec.ts` only for bounded `/repertoire` route/navigation assertions, and this Plan.
- **Excluded:** R1 calendar integration; alternate game or position loading; game-loader, local-session, staging,
  preferred-move, Add/Edit/Save/Remove, date mutation, context, analysis, or persistence workflow; fake save controls,
  placeholder workflow contracts, backend/API/database/schema/storage changes, new dependencies, new global tokens or
  primitives, universal workspace extraction, changes to Viewer behavior or Viewer-owned layout, new browser profiles or
  browser specs, Storybook configuration, unrelated visual redesign, README or historical-record edits, runtime writes,
  generated artifacts, `--fix`, commits, pushes, and unrelated worktree changes.

## Stages

1. **complete - Establish the route, shared navigation, and page-owned static shell.** Add the bounded application surface
   without creating later workflow contracts.
   - **Ordered actions:** Re-read this Plan, the master Plan, the confirmed direction, and the accepted R1/V1/V2/V3
     records. Inspect the current `App`, `AppShell`, Viewer workspace, and `BoardAdapter` seams before editing and
     preserve the coordinator baseline. Register `/repertoire` using the existing route conventions while preserving
     `/`, `/viewer`, and the in-shell not-found route. Add the Repertoire Builder link through the existing shared
     `NavigationItems` path so desktop and drawer navigation expose the same destination and router active state. Reuse
     the current icon, link, copy, token, and layout conventions where they are factual; do not invent a new icon or
     visual hierarchy. Create only a page-specific repertoire shell with the settled heading and standard starting
     `BoardAdapter` position, using the accepted starting FEN and White-at-bottom orientation. Keep AppShell responsible
     for chrome and the new page responsible for workspace layout; do not extract or modify a universal workspace.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/App.test.tsx src/features/app-shell/AppShell.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a recommended finite `bash` tool timeout of `150000` ms.
   - **Breakpoint:** Stop and escalate if the thin static surface cannot follow the established Viewer layout and
     accessibility conventions without selecting a new hierarchy, copy, icon, responsive rule, token, primitive,
     workspace ownership model, temporary state contract, or Viewer change.

2. **complete - Prove the page story, navigation states, accessibility, and responsive browser result.** Make the settled
   scaffold inspectable without adding a new product surface or browser profile.
   - **Ordered actions:** Add a page-specific Storybook story for the standard starting state and the existing wide and
     constrained composition conventions. Add focused page and AppShell assertions for the heading, accessible starting
     board, active route, shared desktop/drawer links, unchanged existing routes, and axe-clean markup. Extend only the
     existing `responsive-shell.spec.ts` app profile to prove `/repertoire` at desktop and constrained widths, active
     navigation, drawer selection, URL preservation, board visibility, and no horizontal overflow. Do not add a browser
     profile or new browser spec. Build Storybook before running its supported interaction suite; do not pass an
     unsupported `--url` argument.
   - **Focused proof:**
     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/responsive-shell.spec.ts`

     Each command has a recommended finite `bash` tool timeout of `360000` ms. Storybook startup health is separately
     bounded to 30 seconds, and the proof server must be cleaned up with port 6006 confirmed free.
   - **Breakpoint:** A bounded visual/accessibility review is required at the existing wide and constrained states. Stop
     rather than guessing if the shell needs a new visual hierarchy, exact copy or icon decision, landmark/focus model,
     responsive rule, selector contract, or acceptance change.

3. **accepted/done - Complete read-only validation and prepare coordinator closeout.** Confirm the accepted R2 result while
   preserving all unrelated and historical material before independent Quality validation.
   - **Ordered actions:** Re-run the focused App, AppShell, and repertoire tests, frontend build, Storybook build and
     interactions, bounded existing application browser proof, lint, read-only Prettier, source-size validation, and
     whitespace proof. Perform one final Git scope audit against the coordinator baseline during execution only,
     confirming that changes are limited to the route, shared navigation, page-specific shell/proof, and this Plan.
     Preserve the existing routes, Viewer, R1 calendar, completed Plans, master Plan, and unrelated worktree content.
     Report unrelated failures rather than repairing or absorbing them. Run the exact governing repository check without
     `--fix` or `--full`.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/App.test.tsx src/features/app-shell/AppShell.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/responsive-shell.spec.ts`

     `timeout 120s npm.cmd run lint --prefix frontend`

     `timeout 120s frontend/node_modules/.bin/prettier.cmd --check frontend/src/App.tsx frontend/src/App.test.tsx frontend/src/features/app-shell/AppShell.tsx frontend/src/features/app-shell/AppShell.test.tsx frontend/src/features/repertoire-builder`

     `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`

     `timeout 30s git diff --check`

     `timeout 600s .venv/Scripts/python.exe scripts/check.py`

     Recommended finite `bash` tool timeouts are respectively `150000`, `150000`, `360000`, `360000`, `360000`,
     `150000`, `150000`, `90000`, `60000`, and `660000` ms. The governing closeout runs without `--fix` or `--full`.
   - **Breakpoint:** Coordinator-owned independent Quality validation, successful bounded Storybook cleanup, final
     scope audit, and acceptance are required before archival. Stop for any unrelated failure requiring repair or any
     scope, contract, ownership, dependency, visual, accessibility, or safety expansion.

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the outcome or
requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - route, shared navigation, and static page shell were implemented; 13 focused tests passed;
  breakpoint: none.
- **Stage 2:** complete - the page story and bounded route/navigation browser proof were added; Storybook passed 30
  files/161 tests and responsive Playwright passed 6 tests; breakpoint: none.
- **Stage 3:** accepted/done - the initial exact full closeout was blocked only by prior R1 README table-padding formatting.
  One authorized targeted README formatting repair was applied. Fresh Quality PASS covered the exact governing check at
  11/11, targeted README Prettier, diff, scope, and listener checks; breakpoint: none.
- **Settled decisions:** R2 is the next slice after accepted R1. AppShell owns application chrome and shared navigation;
  the repertoire page owns its layout. The page starts from the standard FEN with White at the bottom and reuses the
  existing BoardAdapter and Viewer responsive conventions. Existing routes and Viewer behavior remain untouched.
- **Closeout decision:** accept R2 as done. The README updater separately changed `frontend/README.md` and added
  `frontend/src/features/repertoire-builder/README.md`; those documentation changes were not expanded into product or
  test scope.
- **Explicit non-decisions:** R1's calendar is not integrated here. No game loading, local session, preferred-move
  workflow, fake controls, temporary persistence contract, backend/API work, or universal workspace abstraction is
  authorized. Any material visual choice not established by current conventions pauses for coordinator/human review.

## Proof

- Focused Vitest/React Testing Library proof covers `/repertoire` routing, Repertoire Builder heading, standard-start
  board and accessible White orientation, active shared navigation in desktop and drawer paths, unchanged existing
  routes, and focused axe coverage.
- The page Storybook proof covers the established wide/constrained Viewer-style composition, standard board visibility,
  accessibility, and no-overflow behavior using the supported `build-storybook` then `test-storybook -- --run` commands.
- The bounded existing application browser proof covers `/repertoire` URL retention, active navigation, drawer selection,
  desktop/constrained shell behavior, board visibility, and preservation of `/viewer` and `/` checks.
- Frontend build, lint, read-only Prettier, source-size validation, `git diff --check`, and the exact
  `timeout 600s .venv/Scripts/python.exe scripts/check.py` closeout run with finite command and tool timeouts and no
  `--fix` or `--full`.
- Stage 1 passed 13 focused route, navigation, and workspace tests. Stage 2 passed the page Storybook proof at 30
  files/161 tests and 6 responsive-shell Playwright tests.
- Quality semantic validation passed. The initial exact full closeout was blocked only by prior R1 README table-padding
  formatting; one authorized targeted README formatting repair was applied without changing product or test semantics.
  Fresh Quality PASS included the exact `scripts/check.py` result at 11/11, README Prettier, diff, scope, and listener
  checks, all clean.
- The README updater separately changed `frontend/README.md` and added
  `frontend/src/features/repertoire-builder/README.md`; this Plan records that separate documentation work without
  changing it.
- Final scope review must preserve R1 and all accepted upstreams, existing Viewer behavior, completed Plans, the master
  Plan, unrelated worktree material, and all excluded workflow/persistence surfaces.

## Escalation boundaries

- Any new product, visual, API, data, dependency, destructive, ownership, accessibility, or acceptance decision.
- Any need for temporary state, fake save controls, alternate loading, local-session mechanics, preferred-move reads or
  mutations, date/calendar integration, persistence, backend/schema/storage work, or W1/W2 behavior.
- Any change to AppShell's chrome ownership, any universal workspace/session abstraction, or any modification to accepted
  Viewer behavior, layout ownership, analysis, navigation, branch, context, or board semantics.
- Any visual hierarchy, exact copy, icon, responsive rule, landmark, focus, token, or primitive choice that cannot be
  derived from established local conventions. Human pauses are limited to genuine material visual/product decisions.
- Any new dependency, browser profile/spec, Storybook configuration change, generated artifact, runtime write, `--fix`,
  commit, push, historical-record edit, direct baseline collision, failed Storybook cleanup, occupied port 6006, source/
  test-size violation, or unrelated failure requiring repair or scope absorption.

## Visible result

> **Accepted R2 result (done):** A person can open `/repertoire` and see the Repertoire Builder heading, active shared
> navigation, and a responsive Viewer-style workspace showing the standard chess starting position with White at the
> bottom.
