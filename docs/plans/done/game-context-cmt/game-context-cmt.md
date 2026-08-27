# Canonical Game Context presentation - production context matches the approved repository visual direction

> **Status:** done - implementation, visual acceptance, integrated proof, independent validation, and read-only closeout are complete

- **Read trigger:** Read before every sequential Game Context execution stage, at the visual breakpoint, and at final closeout.
- **Upstream:** Approved repository visual reference at `experiments/mock-ups/game context/gamecontext-repo.html`; completed context boundary at `docs/plans/done/mvc-09-game-context/mvc-09-game-context.md`; current design-system and viewer conventions routed by `docs/README.md`.

## Outcome

Translate the approved Game Context visual direction into the production React component without changing its data,
disclosure, source-safety, or child-composition contracts. A person will see a tokenized context panel with a correctly
numbered standard-chess SAN move treatment, a decorated but accessible-safe source link, and responsive presentation
that remains usable at narrow widths. The prototype remains visual reference material only.

## Scope

- **Included:** `GameContext` semantic presentation; deterministic move-number derivation from `ply`; tokenized SAN
  badge and source-link styling; decorative external-link icon; responsive overflow protection; forced-colors and
  reduced-motion treatment; existing empty, position, source, disclosure, composed-child, accessibility, and constrained
  Storybook/test coverage; and bounded integrated browser proof if the existing viewer Storybook specification needs a
  Game Context assertion.
- **Expected areas:**
  `frontend/src/features/viewer/GameContext.tsx`,
  `frontend/src/features/viewer/GameContext.module.css`,
  `frontend/src/features/viewer/GameContext.test.tsx`,
  `frontend/src/features/viewer/GameContext.stories.tsx`, and
  `tests/e2e/viewer-storybook.spec.ts` only if needed for bounded integrated responsive/accessibility proof. The
  expected implementation remains within the existing component, test, story, and existing browser-spec ownership;
  no new source path or design-system primitive is expected.
- **Excluded:** Any movement, redesign, or layout change to `AnalysisPanel`; `ViewerWorkspace.tsx` and its layout CSS;
  `Disclosure`; global token definitions; `stage1SourceSafety.ts`; backend/API/data contracts; dependencies; routes;
  abstractions; prototype edits; `Scratch/`; unrelated repairs; README or historical-record changes; edits to other
  active or completed Plans; `scripts/check.py --fix`; commits; and pushes. Decorative ply progress dots are explicitly
  omitted. This active Plan may receive its required progress, decision, and proof updates.

### Implementation-critical facts and guardrails

- Preserve `GameContextProps` and the current `GameContext.tsx:24-57` ownership: the `Game Context` disclosure remains
  `defaultOpen`, the empty state remains conditional, metadata remains ordered `Ply`, `Last move`, `Source`, and
  `children` remains after metadata in the same disclosure.
- Preserve the current production source contract. `stage1SourceSafety.ts:1-16` is not an edit target: only HTTPS
  `www.chess.com` live/daily game paths without a query or hash produce a link. Keep `target="_blank"` and
  `rel="noopener noreferrer"`, keep the accessible link name exactly `Chess.com game`, and mark the external-link
  icon `aria-hidden="true"`. Do not copy the prototype's expanded source `aria-label`.
- Derive standard notation deterministically from the stored half-move `ply` without changing `GamePosition` or API
  data. For `ply === 0`, retain plain `Initial position` with no move-number badge. For `ply > 0`, use
  `moveNumber = Math.floor((ply + 1) / 2)`; odd plies are White moves and display `<moveNumber>. <SAN>`, while even
  plies are Black moves and display `<moveNumber>... <SAN>`. Thus ply 1 is `1. e4`, ply 2 is `1... e5`, and ply 3 is
  `2. Nf3`. The visible SAN number and SAN text must both remain available to assistive technology as the exact
  notation string; do not hide the move number from the accessible presentation.
- The `san` value itself remains unchanged. A missing SAN at ply zero remains `Initial position`; do not invent move
  data for an invalid or incomplete position. Do not change `GameContext`'s public props or introduce a product state
  selector.
- Map the approved reference's surfaces, borders, spacing, radii, typography, focus, and link states to existing
  Material/CMT roles and typescale tokens. The installed `lucide-react` package is an existing convention, not a new
  dependency. Do not copy literal prototype colors, external fonts, page-level body/sheet layout, or prototype
  JavaScript.
- Keep `Disclosure` as the shared Base UI primitive. If local root, overflow, or motion hooks are needed, scope them to
  `GameContext.module.css`; do not redesign or alter the shared primitive. Keep `ViewerWorkspace` page placement and
  the `AnalysisPanel` child seam unchanged.
- The user owns ongoing analysis feature extraction. Treat any dirty analysis, viewer, or test changes as authoritative;
  preserve them and stop rather than merging by assumption. The active `evalbar-cmt` Plan also identifies shared
  `ViewerWorkspace` paths as collision-sensitive; this Plan must not edit those paths.
- The documentation router has no central active-Plan index (`docs/README.md:10-16`), so creating this directory/file
  requires no related router update.

## Stages

1. **complete - Semantic markup and deterministic SAN presentation.** Added the smallest production markup needed for the
   approved move and source treatments while preserving every existing behavior and accessible contract.

   - **Ordered actions:**
     1. Re-read this Plan, the approved repository mock-up, the completed MVC-09 context record, the current named
        component/test/story files, and the active `evalbar-cmt` Plan. Confirm the coordinator baseline and stop before
        editing if a direct concurrent change is present in an approved path.
     2. Implement the bounded move-number derivation from `ply`: omit a badge for ply zero; use `floor((ply + 1) / 2)`
        and odd/even parity for White `N.` versus Black `N...`. Keep the rendered accessible notation exact and retain
        the existing SAN and `Initial position` text values.
     3. Add the token-ready SAN presentation wrapper and the existing `lucide-react` external-link icon only for a
        validated source URL. Preserve the source link's accessible name, target, rel, and unavailable fallback.
     4. Extend `GameContext.test.tsx` for ply-zero, White, Black, and final notation, source-safe/unsafe/missing
        variants, link attributes/name, default-open interaction, metadata-before-child order, and focused axe coverage.
        Do not alter `stage1SourceSafety.ts` or viewer ownership.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx`

     `npm.cmd run build --prefix frontend`
   - **Breakpoint:** None expected. Stop and escalate if correct numbering requires a changed model/API contract, a
     different interpretation of `ply`, changed source-link accessibility, changed child ownership, or a new public
     interface.

2. **complete - Canonical tokenized styling, Storybook states, and visual acceptance.** Translated the approved visual
   hierarchy into CSS Modules and make the complete component state set inspectable without changing page composition.

   - **Ordered actions:**
     1. Map the reference panel/body hierarchy to the existing `Disclosure` root and `GameContext` content while
        retaining current metadata order and spacing ownership. Keep prototype-only body, sheet, font, and JavaScript
        out of production.
     2. Style the SAN unit with existing surface-container-high, outline-variant, on-surface, primary, radius, spacing,
        and title-medium roles. Style the safe source link with the existing primary role, underline/focus treatment,
        hover treatment, and a decorative 16px external icon. Keep long content from creating horizontal overflow.
     3. Add scoped forced-colors treatment using system colors and scoped reduced-motion treatment for any local
        transition. Do not change global tokens or `Disclosure.module.css`.
     4. Reconcile `GameContext.stories.tsx` with structured coverage for empty, initial, White move, Black move, final
        move, safe/unsafe/missing source, constrained width, default-open/collapsed interaction, composed child, and
        accessibility states. Preserve the existing Storybook token imports and interaction conventions.
     5. Review the rendered component at desktop and constrained widths against the approved prototype. User edits at
        this breakpoint are authoritative, must stay within this outcome, and must be incorporated and revalidated
        before Stage 3.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run lint --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`
   - **Breakpoint:** Human visual review of the Game Context at desktop and constrained 320/480/640px widths. Verify
     the panel, SAN notation, source-link treatment, focus, and contrast direction against the approved reference.
   - **Escalate if:** The reference does not settle a spacing, width, typography, focus, forced-colors, reduced-motion,
     or accessibility treatment, or if review requires changing `ViewerWorkspace`, `AnalysisPanel`, global tokens, or
     acceptance of the exact notation/source-name contracts.

3. **complete - Bounded integrated Storybook/browser evidence and viewer regression.** Proved that the canonical component
   remains correct inside the existing viewer without moving or redesigning the analysis presentation.

   - **Ordered actions:**
     1. Run the focused Game Context and viewer integration tests, including the existing assertions that metadata
        precedes the controlled analysis child and that the context remains in the current disclosure. Include branch
        integration coverage only as needed to prove the unchanged child seam.
     2. Build Storybook before its interaction suite and run the existing structured Game Context stories. Confirm
        empty, all position boundaries, source variants, collapse/reopen, composed child, and axe behavior. Keep Storybook
        startup bounded to 30 seconds, clean up the started server, and confirm port 6006 is free.
     3. Inspect `tests/e2e/viewer-storybook.spec.ts`. Extend that existing file only if the component's integrated
        responsive/accessibility acceptance cannot be proved by its current viewer checks and the component stories; do
        not create a new browser spec or alter the Playwright server profile without coordinator approval.
     4. If an E2E addition is justified, prove the preserved `Chess.com game` accessible name, exact `N. SAN`/`N... SAN`
        output, no horizontal overflow at 320/480/640px, constrained visibility, forced colors, reduced motion, and
        axe. Do not add product state selectors or change `ViewerWorkspace` source/layout.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`
   - **Breakpoint:** None expected after Stage 2 visual acceptance. Stop if browser evidence reveals a new product,
     layout, accessibility, dependency, ownership, or acceptance decision.
   - **Escalate if:** The existing browser surface cannot prove the result without changing excluded viewer paths,
     adding a new test profile/spec, relaxing responsive acceptance, or modifying the AnalysisPanel nesting/layout.

4. **complete - Fresh independent validation and read-only closeout.** Confirmed the complete bounded result and archived the
   Plan only after independent validation and human acceptance.

   - **Ordered actions:**
     1. Request fresh independent Quality validation of semantic markup, standard move numbering, source safety/name,
        disclosure behavior, responsive styling, Storybook states, axe, forced colors, reduced motion, and unchanged
        viewer/AnalysisPanel composition. Repair only a coordinator-authorized in-scope defect; after one failed repair,
        return to the coordinator.
     2. Re-run focused component/viewer tests, frontend build, Storybook build/interactions, lint, read-only Prettier,
        and source-size validation. Report unrelated failures rather than repairing them through this Plan.
     3. Perform one final Git scope audit against the coordinator baseline and `git diff --check`. Confirm the approved
        prototype, all active/completed Plans, analysis feature extraction, `AnalysisPanel`, `ViewerWorkspace`, global
        tokens, source-safety helper, backend/API surfaces, historical records, and unrelated worktree content remain
        preserved.
     4. After fresh validation and final human acceptance, record truthful progress and move this Plan to
        `docs/plans/done/game-context-cmt/` according to repository convention. Do not alter the approved prototype,
        README, other Plans, or unrelated content.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/viewer/GameContext.test.tsx src/features/viewer/ViewerWorkspace.test.tsx src/features/viewer/ViewerWorkspaceBranch.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-storybook.spec.ts`

     `git diff --check`

     `.venv/Scripts/python.exe scripts/check.py`
   - **Breakpoint:** Fresh independent Quality validation, final human acceptance of the visible responsive component,
     bounded Storybook cleanup, and port-6006 confirmation are required before archival. No `--fix`, commit, or push is
     authorized.
   - **Escalate if:** Final proof requires scope expansion, acceptance relaxation, a new contract/dependency/
     architecture, an excluded-path edit, historical-record change, unrelated repair, unsafe server cleanup, or any
     absorption of the user's analysis feature extraction.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage only when the approved
outcome and all ratified decisions remain unchanged.

## Progress and decisions

- **Stage 1:** complete - proof: focused Game Context tests passed (12 tests), and the frontend production build passed;
  breakpoint: none. The exact `floor((ply + 1) / 2)` and odd/even notation rule is implemented with accessible output,
  and the existing source/disclosure/child contracts remain covered. Existing jsdom canvas/axe stderr and the Vite
  chunk-size warning were non-blocking.
- **Stage 2:** complete - proof: focused Game Context tests passed (12 tests), frontend build passed,
  frontend lint passed with one existing `ViewerWorkspace.tsx` hook warning, and the finite Storybook build passed with
  the documented non-fatal Windows libuv teardown assertion. Static Storybook browser review passed at 320/480/640/
  1440px with exact notation/source presence and no horizontal overflow; forced-colors plus reduced-motion emulation
  also had no overflow. Port 6006 was confirmed free after cleanup. Breakpoint: the user accepted the production
  rendering at desktop and constrained widths.
- **Stage 3:** complete - proof: focused Game Context plus ViewerWorkspace regression suite passed (31 tests across
  three files), and the finite Storybook build passed. No Game Context E2E expansion was justified because component
  stories/tests and recorded responsive browser evidence cover the outcome; pre-existing EvalBar edits in the shared
  E2E file were preserved. The Game Context Storybook interaction suite passed. The repository-wide Storybook runner
  reported unrelated failures in five other story files, including a transient connection refusal and existing test-
  runner initialization/dynamic-import failures; 16 suites and 92 tests passed overall. A stale repository Storybook
  process from a cancelled worker was identified by its exact command tree, stopped, and port 6006 was confirmed free
  after the bounded static-server run. Breakpoint: none after Stage 2 acceptance.
- **Stage 4:** complete - proof: fresh independent Quality validation passed; 31 focused Game Context/ViewerWorkspace
  tests passed, frontend build passed, lint completed with one pre-existing ViewerWorkspace hook warning, Prettier check
  passed, `git diff --check` found no whitespace errors, and `.venv/Scripts/python.exe scripts/check.py` exited 0.
  Breakpoint: the user accepted the production visuals before integrated and final validation. One unrelated existing
  viewer-branch axe race (`Axe is already running`) and documented Vite/Storybook warnings were reported, not absorbed.
- **Decisions:** The repository mock-up is visual reference only. Production uses the existing `Disclosure`, Material/CMT
  tokens, CSS Modules, and `lucide-react` convention. Standard notation is derived from half-move `ply`; ply zero is
  `Initial position`, odd plies use `N.`, even plies use `N...`, and the accessible SAN presentation includes the move
  number. The source link remains named `Chess.com game`; its external icon is decorative and hidden. Ply progress dots,
  product state selectors, AnalysisPanel movement/redesign, ViewerWorkspace edits, and global design-system changes are
  not authorized. The dirty-worktree collision gate is mandatory because the user's analysis feature extraction and the
  active EvalBar record identify nearby/shared viewer work as sensitive.

## Proof

- Component proof covers empty, initial, White, Black, and final positions; exact standard notation; source-safe,
  unsafe, and missing values; exact link name/target/rel; default-open disclosure behavior; metadata-before-child order;
  and focused axe checks.
- Storybook proof covers the complete structured state set, constrained presentation, collapse/reopen interaction,
  composed child, forced colors, reduced motion, and accessibility review using repository token imports.
- Integrated proof reuses the existing bounded Storybook server profile and viewer browser specification. It proves no
  responsive overflow and preserves the current viewer composition; the E2E file changes only if existing checks cannot
  cover the approved result.
- Static closeout runs frontend build/lint, read-only Prettier, source-size validation, `git diff --check`, one final
  coordinator-baseline scope audit, and the complete read-only `.venv/Scripts/python.exe scripts/check.py` suite. The
  final repository check is never run with `--fix`.

## Acceptance

- `GameContext` visually follows the approved repository reference using existing React/design-system conventions and no
  copied prototype code.
- Ply zero remains `Initial position` without decorative dots. Ply 1 renders `1. e4`, ply 2 renders `1... e5`, and ply 3
  renders `2. Nf3`; the exact notation, including its move number, is available to assistive technology.
- The source link remains available only for the existing safe Chess.com URLs, retains the accessible name
  `Chess.com game`, retains `target="_blank"` and `rel="noopener noreferrer"`, and uses an `aria-hidden` external icon.
- Empty, initial, intermediate, final, safe/unsafe/missing source, default-open/collapsed, constrained, composed-child,
  forced-colors, reduced-motion, and axe coverage pass without changing data or product state behavior.
- Metadata remains ordered `Ply`, `Last move`, `Source`, and remains before the existing child presentation in the same
  disclosure. `AnalysisPanel` is not moved, redesigned, or otherwise changed.
- The component remains usable at desktop and 320/480/640px constrained widths without horizontal overflow, and all
  focused tests, Storybook proof, browser proof when justified, independent validation, and the complete read-only
  repository check pass.
- No unrelated worktree changes, user analysis extraction, active/completed Plans, prototype, source-safety helper,
  global tokens, README, or historical records are modified.

## Escalation boundaries

- Any disagreement with the ratified move-number formula, ply parity, initial-position treatment, accessible SAN output,
  or source-link accessible name/attributes.
- Any change to `GameContextProps`, `GamePosition`, API/backend/data contracts, source URL allowlisting, product state
  selectors, disclosure ownership, child ordering, or automatic behavior.
- Any edit to `AnalysisPanel`, `ViewerWorkspace.tsx`, `ViewerWorkspace.module.css`, `Disclosure`, global tokens,
  `stage1SourceSafety.ts`, the approved prototype, active/completed historical Plans, README, or unrelated worktree
  content.
- Any need for a new dependency, design-system primitive, abstraction, route, browser profile/spec, or broader
  responsive/page-layout change.
- Any direct dirty-worktree collision, especially with the user's analysis feature extraction or the active EvalBar
  work. Preserve both edits and return to the coordinator; do not merge by assumption.
- Any visual, focus, typography, color, forced-colors, reduced-motion, responsive, or acceptance choice not settled by
  the reference and ratified contracts; use the Stage 2 human breakpoint rather than guessing.
- Any unbounded Storybook/browser startup, failed cleanup, occupied port 6006 owned by another process, unrelated
  validation failure, request for `--fix`, destructive Git operation, commit, or push.

## Visible result

> The production Game Context shows correctly numbered chess notation and a safe, accessible source link in the approved responsive visual style while its existing disclosure and child behavior remain unchanged.
