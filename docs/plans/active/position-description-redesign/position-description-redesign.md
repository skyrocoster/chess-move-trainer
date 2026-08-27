# Position description redesign - one grouped summary with one authoritative narration

> **Status:** pending - implementation dispatch waits for a non-conflicting baseline with the active EvalBar Plan

- **Read trigger:** Read before every sequential stage, at the Stage 2 visual/accessibility breakpoint, after any
  context rollover, and before final closeout.
- **Upstream:** `experiments/mock-ups/position description/position_description.html`, the completed
  [MVC-03 static-board Plan](../../done/mvc-03-static-board/mvc-03-static-board.md), the completed
  [safe read-only board-adapter record](../../done/safe-read-only-board-adapter/safe-read-only-board-adapter.md), and
  the active [EvalBar continuation Plan](../evalbar-cmt/evalbar-cmt.md).

## Outcome

Replace `BoardAdapter`'s plain visible position paragraph with a polished, grouped, responsive summary inspired by the
adapted prototype and implemented with repository Material/CMT conventions. Sighted users receive a concise scan-friendly
inventory; assistive technology receives one stable linear spoken description. Both representations come from one
position model, so the visible and spoken descriptions cannot drift or be announced twice.

## Scope

- **Included:** Enrich the existing internal `BoardAdapter` position model with side/piece groups and position metadata
  from the same `chess.js` board/FEN source as the spoken description; render orientation, side-to-move, White/Black
  inventories, square tokens, castling, en-passant, halfmove, and fullmove information; keep the spoken description
  outside the disclosure as the authoritative live/description layer; make the reordered visible presentation
  `aria-hidden` and `inert`; preserve the existing disclosure trigger and collapsed default; apply local responsive,
  focus, forced-colors, reduced-motion, typography, and tokenized styling; update focused component tests, Storybook
  cases, and targeted browser evidence.
- **Expected areas:**
  `frontend/src/features/board-adapter/BoardAdapter.tsx`,
  `frontend/src/features/board-adapter/BoardAdapter.module.css`,
  `frontend/src/features/board-adapter/BoardAdapter.test.tsx`,
  `frontend/src/features/board-adapter/BoardAdapter.stories.tsx`, and
  `tests/e2e/board-adapter-storybook.spec.ts`. A tightly coupled internal helper may be added only if the 500-line
  handwritten-source limit requires it; it must remain under `frontend/src/features/board-adapter/` and preserve the
  existing adapter ownership.
- **Excluded:** `InteractiveBoardAdapter` and loaded branch-position narration; board appearance or movement; viewer
  workflow; EvalBar, analysis, backend/API/data contracts; new dependencies; global token or shared `Disclosure`
  changes; prototype edits; README changes; unrelated worktree changes; completed-record rewrites; `--fix`; commits;
  and pushes.

## Stages

1. **pending - Shared position model and accessibility layer.** Enrich the existing model and establish the single
   authoritative spoken/visible data boundary without changing the public adapter or board contract.

   - **Ordered actions:**
     1. Re-read this Plan, the adapted prototype, MVC-03's accepted adapter contract, the named BoardAdapter source and
        tests, and the active EvalBar Plan. Confirm the BoardAdapter paths are not being changed concurrently; stop if
        the coordinator baseline conflicts.
     2. Extend the existing `PositionModel` so one board traversal and the existing FEN fields produce the stable
        occupied-square narration, grouped side/piece inventory, side-to-move/orientation metadata, and castling,
        en-passant, halfmove, and fullmove facts. Do not create an independent parser or hardcoded visible fixture.
     3. Keep the complete linear description associated with the board through the existing unique
        `aria-describedby`. Keep it outside the disclosure and apply the approved single live/spoken semantics
        (`role="status"`, polite live behavior, and atomic updates) without creating a second announcement source.
     4. Render the disclosure's reordered visual body from the same model and mark that body `aria-hidden="true"` and
        `inert`; remove its unnecessary focus stop/accessible label while preserving the disclosure trigger, keyboard
        behavior, collapsed default, board `role="img"`, package isolation, and fallback behavior.
     5. Extend `BoardAdapter.test.tsx` for model parity, exact stable narration, grouped data, orientation/turn/facts,
        unique association, one live/spoken layer, hidden/inert visible content, disclosure persistence, controlled
        updates, strict invalid-FEN handling, non-interactivity, and axe coverage.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx`

     `npm.cmd run build --prefix frontend`
   - **Breakpoint:** None expected. Escalate if the single live/description layer cannot coexist with the accepted
     board semantics, if empty inventory behavior needs new product copy, or if the model requires a new ownership or
     public API decision.

2. **pending - Canonical visual presentation.** Implement the grouped presentation with repository styling and prove
   it at the required visual/accessibility breakpoint before expanding browser evidence.

   - **Ordered actions:**
     1. Add a local consumer presentation around the existing `Disclosure`; do not modify the shared primitive. Keep the
        trigger name `Position description`, derive its side-to-move state from the model, and preserve the closed
        default and existing bounded disclosure behavior.
     2. Implement the prototype-inspired metadata strip, side columns, ordered piece rows, square tokens, and fact
        chips in `BoardAdapter.module.css`. Use existing `--md-sys-*`, `--cmt-spacing-*`, `--cmt-radius-*`, focus, and
        typescale roles; do not copy prototype CSS literals or introduce a new design-system primitive.
     3. Use component-local responsive rules consistent with the repository's container-driven behavior: preserve the
        bounded 40rem adapter, stack metadata and side columns when the available inline size is constrained, wrap
        facts and square tokens, and prevent horizontal overflow at 320px, 480px, and 640px.
     4. Add hover/focus, reduced-motion, and forced-colors treatment using existing conventions. Preserve readable
        contrast and ensure the inaccessible visual subtree does not remove the spoken description.
     5. Run the focused component proof and render the starting, rich, Black-orientation, expanded, and constrained
        stories for review.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run lint --prefix frontend`
   - **Breakpoint:** Human visual and accessibility review is required before Stage 3. At wide and 320px/480px/640px
     constrained sizes, confirm the grouped hierarchy is legible and scan-friendly, the summary remains usable when
     collapsed/expanded, no horizontal overflow occurs, and the existing board/fallback appearance is unchanged.
     Confirm with the accessibility tree or assistive technology that exactly one linear spoken/live description is
     exposed, the visible reordered body is hidden/inert, the board retains one stable `aria-describedby`, and keyboard
     disclosure focus remains correct. Review forced-colors and reduced-motion contexts. User edits at this breakpoint
     are authoritative and must remain within this outcome; incorporate and revalidate them before continuing.

3. **pending - Storybook and browser evidence.** Lock the canonical states and prove responsive, accessibility, and
   no-duplication behavior against the real Storybook iframe.

   - **Ordered actions:**
     1. Update the existing Board Adapter stories for starting, rich, Black orientation, hidden coordinates,
        constrained sizing, invalid FEN, and expanded description. Add an edge fixture only when needed to prove the
        model's already-settled behavior; do not add speculative product states or an eighth story without escalation.
     2. Extend `tests/e2e/board-adapter-storybook.spec.ts` to assert grouped metadata/inventory/facts, model-derived
        spoken content, one description/live node, `aria-hidden`/`inert` visible content, stable ID association,
        collapsed/expanded keyboard behavior, orientation, constrained sizing, no overflow, forced colors, reduced
        motion, static non-interactivity, fallback, and axe results.
     3. Build Storybook before its interaction suite, bound startup to the repository's existing 30-second convention,
        clean up the server, and confirm port 6006 is free. Report unrelated historical Storybook failures rather than
        absorbing them.
   - **Focused proof:**
     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/board-adapter-storybook.spec.ts`
   - **Breakpoint:** None expected after Stage 2 acceptance. Stop and escalate if browser evidence requires a changed
     accessibility contract, new visual direction, relaxed responsive acceptance, a new dependency, or an interactive
     adapter change.

4. **pending - Regression, read-only closeout, and scope audit.** Independently validate the complete in-scope result
   and close the Plan only after final human acceptance and truthful scope review.

   - **Ordered actions:**
     1. Run the focused BoardAdapter tests together with the existing viewer regression; confirm static viewer wiring,
        loaded interactive behavior, board labels, navigation, analysis, and announcements were not changed.
     2. Run frontend build, lint, read-only Prettier, Storybook build/interactions, targeted Board Adapter Playwright,
        source-size validation, and the complete read-only repository check without `--fix`.
     3. Request fresh independent Quality validation of the model parity, one spoken layer, visible hidden/inert
        presentation, disclosure behavior, responsive rendering, forced-colors/reduced-motion behavior, and preserved
        static-board contract. Repair only a coordinator-authorized in-scope defect; after one failed repair, return to
        the coordinator.
     4. Perform one final Git scope audit against the coordinator baseline and `git diff --check`. Confirm only the
        approved implementation/test/browser areas changed; preserve the prototype, all active/completed Plans,
        unrelated worktree changes, interactive adapter, viewer workflow, and historical records.
     5. After acceptance, record truthful progress and move this Plan to `docs/plans/done/position-description-redesign/`
        according to repository convention. Do not modify README or other records.
   - **Focused proof:**
     `npm.cmd run test --prefix frontend -- --run src/features/board-adapter/BoardAdapter.test.tsx src/features/viewer/ViewerWorkspace.test.tsx`

     `npm.cmd run build --prefix frontend`

     `npm.cmd run build-storybook --prefix frontend`

     `npm.cmd run test-storybook --prefix frontend -- --url http://127.0.0.1:6006`

     `npm.cmd run lint --prefix frontend`

     `frontend/node_modules/.bin/prettier.cmd --check frontend`

     `./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/board-adapter-storybook.spec.ts`

     `./.venv/Scripts/python.exe scripts/check.py`

     `git diff --check`
   - **Breakpoint:** Fresh independent Quality validation and final human acceptance of the visible responsive summary
     and assistive-technology layer are required before archival. No `--fix`, commit, or push is authorized.
   - **Escalate if:** Final proof needs scope expansion, acceptance relaxation, historical-record edits, README
     maintenance, or repair of an unrelated failure.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage only when the approved
outcome, decisions, and breakpoints remain unchanged.

## Progress and decisions

- **Stage 1:** pending - proof: not started; breakpoint: none expected.
- **Stage 2:** pending - proof: not started; breakpoint: human visual and accessibility review at wide and constrained
  sizes.
- **Stage 3:** pending - proof: not started; breakpoint: none expected after Stage 2 acceptance.
- **Stage 4:** pending - proof: not started; breakpoint: fresh independent Quality validation and final human
  acceptance before archival.
- **Decisions:** The adapted HTML is noncanonical visual/accessibility guidance; its standalone implementation is not
  copied. One `BoardAdapter` position model feeds both the stable linear narration and the reordered visible summary.
  The visible body is `aria-hidden`/`inert`, the spoken layer remains outside the disclosure, and the disclosure remains
  collapsed by default. `InteractiveBoardAdapter` and loaded branch positions are outside this outcome. The active
  `evalbar-cmt` Plan is a coordination gate because it names overlapping board-adapter paths; execution requires that
  work to be closed or a fresh non-conflicting baseline established. README maintenance is not expected for this
  internal component redesign.

## Proof

- Focused BoardAdapter Vitest proves model parity, stable narration, accessibility association, disclosure behavior,
  static semantics, fallback, and axe coverage.
- Storybook interaction and targeted Playwright proof cover the real grouped visual, keyboard disclosure, responsive
  320px/480px/640px layouts, no overflow, forced colors, reduced motion, fallback, and duplicate-announcement guard.
- Viewer regression proves the static BoardAdapter integration and all existing loaded interactive/viewer behavior stay
  unchanged.
- Closeout runs frontend build/lint, read-only Prettier, Storybook, targeted browser proof, the complete read-only
  `scripts/check.py` suite, and one final Git scope audit. Unrelated baseline failures remain report-only.

## Acceptance

- The Board Adapter shows a polished grouped summary with orientation and side-to-move metadata, White/Black piece
  inventories, square tokens, and position facts, using repository colours, typography, tokens, focus, and responsive
  conventions.
- The visible presentation remains collapsed by default, works by keyboard, stays readable at wide and constrained
  sizes, and never creates horizontal overflow.
- Assistive technology receives exactly one stable linear description in accepted FEN order through the existing board
  association; the visible reordered subtree is `aria-hidden`/`inert` and is not announced as a duplicate.
- Spoken and visible output update together from one position model. Strict untrimmed FEN validation, unavailable
  fallback, public props, orientation/coordinates, package isolation, static board semantics, and unique IDs remain
  unchanged.
- Focused tests, Storybook, axe, targeted browser proof, frontend checks, fresh Quality validation, and the complete
  read-only repository check pass. Unrelated worktree changes and historical records remain intact.
- No README change is made unless a genuinely new public architecture or structural convention is introduced; that
  need is an escalation, not an assumption.

## Escalation boundaries

- Any change to `BoardAdapter` public props, strict untrimmed FEN validation, invalid/unrenderable fallback, board
  appearance, package isolation, board role/label, coordinates, orientation, unique `aria-describedby`, stable FEN
  narration order, disclosure default, or static non-interactivity.
- Any ambiguity in the live-region, `aria-describedby`, `aria-hidden`, `inert`, focus, or duplicate-announcement
  contract; any need for empty-inventory copy or layout not inferable from the approved outcome and repository evidence.
- Any request to add narration to `InteractiveBoardAdapter` or loaded branch positions, change viewer/branch/analysis
  ownership, or alter an API, data, dependency, backend, global token, shared Disclosure, or public architecture.
- Any need to copy or edit the prototype, rewrite completed records, edit README, absorb unrelated worktree changes or
  failures, invoke `--fix`, commit, or push.
- Any conflict with the active `evalbar-cmt` Plan or coordinator baseline; dispatch must stop until a fresh non-conflicting
  baseline is established.
- Any visual breakpoint failure involving hierarchy, readability, responsive arrangement, colors, typography, focus,
  forced colors, reduced motion, or accessibility that cannot be resolved without a new human decision.

## Visible result

> The Board Adapter presents a clear grouped position summary for sighted users while assistive technology hears one complete, stable description of the same position.
