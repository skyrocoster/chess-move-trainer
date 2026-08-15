# Verified Technology Foundation — prove the selected component-development stack

> **Status:** All 13 stages shipped and independently validated (orders 01-13); MP-01 accepted 2026-08-15. Production `/` remains unchanged because MP-01 is development-only.

- **Read trigger:** Open when reviewing or compiling MP-01 work after the master-plan slice has been selected and before any order authoring or implementation.

## What we're building & why

MP-01 will install and verify the selected React application and component-development foundation through
a temporary, clearly development-only Storybook Foundation Check. The check will visibly exercise each
technology boundary and the layered accessibility proof without turning compatibility scaffolding into
production UI.

The completed set of stages is one coherent human outcome: a developer can run or build the Foundation
Check, inspect its valid, invalid, structural, and contained-failure states, and confirm that production
`/` remains the existing backend-health page. Individual stages are deliberately separated by technology
boundary so compatibility failures remain attributable; no individual stage is a second product slice.

## Stages

1. **ORDERED** — Preserve the React, React DOM, TypeScript, Vite, and Node baseline while resolving the
   exact selected dependency versions and lockfile.
2. **ORDERED** — Configure Storybook `10.5.8` with `@storybook/react-vite` and prove shared global CSS,
   CSS Modules, and the development-only Foundation Check surface.
3. **ORDERED** — Prove `react-router-dom` `7.18.2` context inside the Foundation Check without changing
   production route composition.
4. **ORDERED** — Prove the selected `@base-ui/react` `1.7.0` structural primitive and its accessible
   behavior without creating the product shell or drawer.
5. **ORDERED** — Prove a real semantic `lucide-react` `1.31.0` icon with its accessible name owned by
   the control rather than the SVG.
6. **ORDERED** — Prove `chess.js` `1.4.0` validation and position inspection for one known valid and
   one known invalid FEN without enabling chess mutation or replay.
7. **ORDERED** — Prove safe static rendering through `react-chessboard` `5.12.0`, with no movement,
   highlighting, arrows, drag-and-drop, or package-specific state escaping an application-owned proof
   boundary.
8. **ORDERED** — Prove selective `react-error-boundary` `6.1.3` containment of a deliberately exercised
   render failure without establishing the later shared error architecture.
9. **ORDERED** — Add `@chialab/vitest-axe` `0.19.1` to the existing Vitest component-proof layer and
   execute the Foundation Check accessibility assertion.
10. **ORDERED** — Add the required Storybook axe accessibility integration and execute isolated-state
    accessibility proof.
11. **ORDERED** — Add the bounded Storybook workflow fallback `@storybook/test-runner@0.24.4` and
    execute the Foundation Check interaction proof through `npm run test-storybook`.
12. **ORDERED** — Add `@axe-core/playwright` `4.13.0` to the existing Playwright browser-proof layer
    and execute the real-browser accessibility proof.
13. **ORDERED** — Run the integrated Foundation Check and preserved-production regression gate; only the
    completed set constitutes MP-01 and is ready for human acceptance.

## Shipped

| Stage | What shipped (≤2 sentences) |
|-------|------------------------------|
| 1 | Pinned the six runtime and six dev/proof packages at exact MP-01 versions and regenerated the lockfile; the React/TS/Vite/Vitest/Node baseline and the `@storybook/addon-vitest` exclusion were preserved. |
| 2 | Configured Storybook 10.5.8 with `@storybook/react-vite` and a preview importing existing global CSS; added a development-only Foundation Check story proving one global-CSS effect and one bounded CSS-Module effect. |
| 3 | Proved `react-router-dom` 7.18.2 context inside the Foundation Check using an in-memory router that renders the consumed location; production `App.tsx` and `main.tsx` remain router-free with no `/viewer` route. |
| 4 | Proved the `@base-ui/react` 1.7.0 Collapsible structural primitive with its accessible keyboard/click behavior inside the Foundation Check. |
| 5 | Proved a real semantic `lucide-react` 1.31.0 icon whose accessible name is owned by the control, not the SVG. |
| 6 | Proved `chess.js` 1.4.0 FEN validation and position inspection with distinguishable valid and invalid results. |
| 7 | Proved safe static read-only `react-chessboard` 5.12.0 rendering after validation; no movement, arrows, or package state escapes the proof boundary. |
| 8 | Proved selective `react-error-boundary` 6.1.3 containment of a deliberately exercised render failure without establishing shared error architecture. |
| 9 | Added `@chialab/vitest-axe` 0.19.1 component-level proof in the Vitest layer, scoped to app-owned content. |
| 10 | Added the `@storybook/addon-a11y` 10.5.8 Storybook axe accessibility integration and executed isolated-state accessibility proof. |
| 11 | Added the bounded `@storybook/test-runner@0.24.4` workflow fallback, executing Foundation Check play functions via `npm run test-storybook`. |
| 12 | Added `@axe-core/playwright` 4.13.0 real-browser accessibility proof (root dependency) against the rendered proof surface. |
| 13 | Ran the integrated five-command gate and the preserved-production regression; the repository full local check passes green. |

## Touches

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/features`
- `frontend/vitest.config.ts`

The future Storybook directory, temporary foundation files, and browser proof file are recorded in the
stage handoff below rather than added as placeholder paths. Verification-only paths are not unconditional
Plan ownership. Existing production composition and status files are intentionally outside the Touches
set even though they are regression-test subjects.

## Acceptance

1. Start the temporary Storybook surface and confirm its explicit development-only label and available
   Foundation Check states.
2. Inspect shared global CSS and a CSS Module, confirming that the check does not create a second visual
   implementation of production components.
3. Confirm the Lucide icon and Base UI primitive render with the expected accessible names and behavior.
4. Confirm router context is available in the check without adding production route composition or a
   `/viewer` route.
5. Exercise one valid FEN and confirm a safe static board renders; exercise one invalid FEN and confirm
   an explicit unavailable proof rather than a silent starting-position fallback.
6. Deliberately exercise the render-failure path and confirm the selected error boundary contains it.
7. Execute the Storybook accessibility and workflow checks, the Vitest/axe check, and the Playwright/axe
   browser proof; inspect failures rather than treating automation as complete WCAG acceptance.
8. Open production `/` through the existing browser path and confirm its health success and unavailable
   states remain unchanged.
9. Confirm no movement, legal interaction, PGN, stored data, Stockfish, persistence, speculative
   controls, final Material system, shell, board adapter, or shared product error architecture appears.

## Automated gates and routing

- Exact package metadata and peer compatibility are reverified immediately before installation; the
  existing React/TypeScript/Vite/Node baseline is not upgraded. Because Storybook `10.5.8`'s maintained
  `@storybook/addon-vitest` requires `@vitest/browser-playwright` `^4` and Vitest 4, while
  `@storybook/addon-interactions@10.5.8` is unavailable, MP-01 explicitly uses the narrow compatibility
  fallback `@storybook/test-runner@0.24.4` and keeps the mandated Vitest `3.0.5` baseline; do not add
  `@storybook/addon-vitest` or upgrade Vitest.
- Storybook development and static-build commands succeed.
- Focused Vitest component tests and `@chialab/vitest-axe` checks succeed.
- Storybook `@storybook/addon-a11y@10.5.8` accessibility integration builds and executes, and the
  `@storybook/test-runner@0.24.4` workflow command executes the Foundation Check play functions through
  `npm run test-storybook`.
- Playwright with `@axe-core/playwright` executes against the selected rendered proof surface.
- Existing frontend tests, frontend build, lint, and existing `/` Playwright tests remain green.
- The documentation checker passes after this Plan is written and after any later documentation change.

The stages are all `ORDERED` because dependency resolution, temporary harness setup, proof-layer
configuration, and integrated regression evidence require bounded compiler/executor context. Work-order
sequencing must remain within the stage boundary; no stage may begin MP-02 or any later product behavior.

## Exclusions

- Any production `/` composition, styling, status behavior, or existing acceptance-surface change.
- `/viewer`, production route composition, final Material palette or typescale, shell, board adapter,
  shared error architecture, or reusable product components.
- Exposing the Foundation Check as product UI or retaining it as a duplicate diagnostics surface after
  MP-05 replaces its compatibility proofs.
- Board movement, legal-move interaction, PGN parsing, stored data, Stockfish, persistence, and
  speculative application APIs.
- Custom routing, FEN parsing, chessboard rendering, drawer/focus mechanics, runtime theme generation,
  Google Fonts or Material Symbols requests, global application state, and JavaScript-driven responsive
  layout state.
- Changes to unrelated dirty worktree files or assumptions that current dirty files represent a clean
  baseline.

## Compiler handoff

### Stage 1 — baseline and exact lock resolution

- **Verified edit sites:** `frontend/package.json` — manifest currently contains React `19.0.0`, React DOM
  `19.0.0`, TypeScript `5.7.3`, Vite `6.0.11`, Vitest `3.0.5`, and Node `>=22 <23`; `frontend/package-lock.json`
  — existing lockfile. Existing scripts include `build`, `test`, and `lint`.
- **Verified tests:** `frontend/src/features/status/StatusPage.test.tsx` — current loading, success, network
  failure, and non-OK response coverage must remain valid.
- **Settled contracts:** Pin the six runtime/foundation packages and the development/proof technologies at
  the versions named by MP-01; preserve the baseline rather than performing a general toolchain upgrade.
  Keep `@storybook/addon-a11y@10.5.8`. For the Storybook workflow proof, explicitly select
  `@storybook/test-runner@0.24.4` as a narrow compatibility fallback: Storybook `10.5.8`'s maintained
  `@storybook/addon-vitest` requires `@vitest/browser-playwright` `^4` and Vitest 4, conflicting with
  the mandated Vitest `3.0.5` baseline, and `@storybook/addon-interactions@10.5.8` is unavailable. Do
  not add `@storybook/addon-vitest` or upgrade Vitest; record this as a bounded exception rather than a
  silent technology substitution.
- **Constraints:** The worktree already contains unrelated modifications, including both package files;
  establish the current dirty files as the preservation baseline and never discard them.
- **Open questions:** Recheck registry metadata, peer requirements, exact lockfile resolution, and the
  smallest package-script additions immediately before installation.

### Stage 2 — Storybook and React-Vite CSS surface

- **Verified edit sites:** No `frontend/.storybook/` directory or story files currently exist. `frontend/src/app.css:1-28`
  is the existing global stylesheet with current status-page styling and must not be changed for this stage.
- **Verified tests:** No Storybook harness or story precedent exists; the master plan requires development
  and static-build proof plus shared global CSS and CSS Modules.
- **Settled contracts:** Use Storybook `10.5.8` with `@storybook/react-vite`; the future exact files are
  `frontend/.storybook/main.ts`, `frontend/.storybook/preview.tsx`, and a foundation story under
  `frontend/src/features/foundation/` if the compiler confirms those conventional locations.
- **Constraints:** Storybook reuses committed application CSS and future application-owned proof boundaries;
  it is not a parallel component API, production route, or product surface.
- **Open questions:** Verify the current Storybook 10 configuration shape, minimum required integrations,
  exact scripts, and whether preview configuration can load existing global CSS without touching `App.tsx`
  or `app.css`.

### Stage 3 — React Router DOM context

- **Verified edit sites:** `frontend/src/App.tsx:1-5` renders only `StatusPage`; there is no production router.
  The temporary proof must be isolated to a future foundation story/component, not `App.tsx`.
- **Verified tests:** `tests/e2e/status.spec.ts:3-13` proves the existing `/` success and unavailable paths;
  these tests remain unchanged and are regression evidence.
- **Settled contracts:** Use `react-router-dom` `7.18.2` only to prove context in the development-only
  Foundation Check; do not create `/viewer` or production route composition.
- **Constraints:** Use conventional package composition and avoid router-specific abstractions that would
  make the later MP-05 route change harder.
- **Open questions:** Confirm the smallest in-story router provider/context exercise supported by the pinned
  package and record the exact future foundation proof file.

### Stage 4 — Base UI structural primitive

- **Verified edit sites:** No existing structural primitive or drawer exists. Future proof code belongs under
  the bounded foundation feature path and must not modify the status page.
- **Verified tests:** No Base UI test precedent exists; accessibility behavior must be proven by the
  Foundation Check workflow and relevant axe layers.
- **Settled contracts:** Use `@base-ui/react` `1.7.0` selectively for one minimal documented structural
  behavior. Base UI supplies behavior, not product appearance or the future shell.
- **Constraints:** Do not build a drawer, focus trap, modal-dismissal system, shell, or alternative design
  system in MP-01; application appearance remains CSS/class-owned.
- **Open questions:** Select the smallest documented primitive that visibly proves the package without
  implying a later product contract; verify its exact import and interaction API.

### Stage 5 — Lucide semantic icon

- **Verified edit sites:** No icon control currently exists in production. Add only a future foundation proof
  control under `frontend/src/features/foundation/`.
- **Verified tests:** Existing status tests have no icon assertions; the Foundation Check and browser proof
  must inspect the accessible name on the control.
- **Settled contracts:** Use `lucide-react` `1.31.0` with a real local semantic icon; icon-only controls
  receive their accessible name on the control, and icons inherit semantic CSS color.
- **Constraints:** Import only an icon needed by the check; do not add navigation, menu, or speculative
  future controls.
- **Open questions:** Confirm the smallest icon/control example and exact accessible query for the story and
  workflow proof.

### Stage 6 — chess.js validation and inspection

- **Verified edit sites:** No chess validation or position component currently exists. Future foundation proof
  code must remain separate from the eventual MP-04 board adapter.
- **Verified tests:** No chess test precedent exists; the master acceptance requires one known valid and one
  known invalid FEN with distinguishable results.
- **Settled contracts:** Use `chess.js` `1.4.0` for FEN validation and required position inspection only;
  invalid input must never silently become the standard starting position.
- **Constraints:** Do not enable movement, legal-move interaction, replay, PGN parsing, or chess-state
  mutation; do not create a custom FEN parser.
- **Open questions:** Verify the pinned package's exact `validateFen` result shape and choose stable valid and
  invalid fixtures for the proof.

### Stage 7 — react-chessboard static rendering

- **Verified edit sites:** No board or board adapter currently exists. The temporary proof may use a narrow
  foundation-only wrapper, but the application-owned MP-04 adapter remains out of scope.
- **Verified tests:** No board tests or stories exist; the Foundation Check must visibly distinguish valid
  static rendering from invalid-position handling.
- **Settled contracts:** Use `react-chessboard` `5.12.0` only for safe static rendering after validation;
  keep package-specific state behind the future proof boundary and preserve standard FEN as the application
  representation.
- **Constraints:** No movement handlers, drag-and-drop, highlighting, arrows, or inactive callbacks/props;
  any package style exception remains third-party internals, not application CSS practice.
- **Open questions:** Verify the pinned package's exact static/read-only option shape and the smallest
  bounded board rendering setup compatible with the Storybook CSS surface.

### Stage 8 — react-error-boundary containment

- **Verified edit sites:** No error boundary exists in the current application. The future deliberate-failure
  story belongs under the foundation feature and must not wrap or alter `App.tsx`.
- **Verified tests:** Existing status tests cover expected health failures as typed `role="alert"` state;
  they must not be converted to boundary failures.
- **Settled contracts:** Use `react-error-boundary` `6.1.3` selectively around the deliberately failing
  Foundation Check region; expected invalid-FEN/unavailable outcomes remain ordinary typed UI states.
- **Constraints:** Do not establish the later shared error architecture or imply that boundaries catch event,
  arbitrary async, server-rendering, or boundary-self failures.
- **Open questions:** Confirm the minimal render-failure trigger and fallback assertion that exercises the
  package without introducing production error copy or architecture.

### Stage 9 — Vitest component proof and @chialab/vitest-axe

- **Verified edit sites:** `frontend/vitest.config.ts:1-11` currently configures the React plugin, JSDOM,
  existing setup, and source tests. `frontend/src/features/status/StatusPage.test.tsx:1-35` is the existing
  React Testing Library/Vitest style precedent.
- **Verified tests:** Preserve all existing StatusPage tests; add a focused future foundation test file only
  after the exact axe API and setup requirements are verified.
- **Settled contracts:** Use `@chialab/vitest-axe` `0.19.1` for fast component-level accessibility checks
  in the existing Vitest/JSDOM layer; component checks supplement, not replace, browser and human review.
- **Constraints:** Keep the test focused on the Foundation Check states and accessible semantics; do not
  broaden the test setup or alter unrelated status behavior.
- **Open questions:** Verify the package's Vitest 3 API, matcher/setup requirements, exact future test path,
  and whether `frontend/vitest.config.ts` or `frontend/src/test-setup.ts` actually needs modification.

### Stage 10 — Storybook axe accessibility integration

- **Verified edit sites:** No Storybook configuration or accessibility integration currently exists. Future
  configuration is under `frontend/.storybook/`; no placeholder files may be created during Plan writing.
- **Verified tests:** No isolated Storybook accessibility precedent exists; MP-01 requires the selected
  maintained Storybook axe integration to build and execute.
- **Settled contracts:** Use `@storybook/addon-a11y@10.5.8` as the Storybook accessibility integration;
  inspect isolated valid, invalid, structural, and failure states at this layer.
- **Constraints:** Automated axe results do not replace keyboard, responsive, assistive-technology, or human
  WCAG 2.2 AA review, and no unneeded addon may be introduced.
- **Open questions:** Reverify the Storybook 10.5.8-supported integration/package and exact configuration
  before installation; do not silently substitute an older or unrelated accessibility addon.

### Stage 11 — Storybook workflow and interaction integration

- **Verified edit sites:** No Storybook workflow configuration or stories currently exist. Future interaction
  stories belong under `frontend/src/features/foundation/` and must remain development-only.
- **Verified tests:** There is no Storybook interaction-test precedent; existing browser tests remain the
  independent production regression layer.
- **Settled contracts:** Use `@storybook/test-runner@0.24.4` as the narrow Storybook 10.5 workflow/
  interaction compatibility fallback. It executes story `play` functions through `npm run test-storybook`
  and interoperates with `@storybook/addon-a11y@10.5.8`; it is officially superseded, but is selected here
  because preserving the mandated Vitest `3.0.5` baseline outranks the newer maintained
  `@storybook/addon-vitest` integration. Do not add `@storybook/addon-vitest` or upgrade Vitest.
- **Constraints:** Do not invent product controls, inactive future interactions, or a parallel application
  API; the workflow proves compatibility behavior only. Record the test-runner choice as this bounded
  exception, not as a silent substitution.
- **Open questions:** Confirm the exact Storybook test-runner configuration and script wiring, then name
  the exact story files in the compiled order; do not reopen the settled package choice.

### Stage 12 — Playwright browser proof and @axe-core/playwright

- **Verified edit sites:** `tests/e2e/playwright.config.ts:1-21` starts the existing backend and frontend
  servers and has no browser axe integration. Existing `tests/e2e/status.spec.ts:3-13` must remain the
  unchanged `/` regression precedent.
- **Verified tests:** The future verification-only path is expected to be `tests/e2e/foundation-accessibility.spec.ts`;
  it is not unconditional Plan ownership. Any required existing-config edit must be named explicitly by the
  compiler rather than assumed.
- **Settled contracts:** Use `@axe-core/playwright` `4.13.0` against the selected fully rendered proof
  surface, while retaining the existing browser proof for `/` health success and unavailable behavior.
- **Constraints:** Browser automation must not alter production `/`, use ports for unrelated services, or
  treat axe output as complete human accessibility acceptance.
- **Open questions:** Determine whether the browser axe target is a Storybook dev/static server, its exact
  startup/cleanup command and port, and the smallest Playwright config change needed to run it deterministically.

### Stage 13 — integrated Foundation Check and regression gate

- **Verified edit sites:** `frontend/src/App.tsx:1-5`, `frontend/src/features/status/StatusPage.tsx:7-39`,
  `frontend/src/app.css:1-28`, and `tests/e2e/status.spec.ts:3-13` are preserved production/status surfaces;
  no implementation edit is authorized there.
- **Verified tests:** Existing frontend status tests and `/` Playwright success/unavailable tests are the
  neighboring regression proof. The repository's documented full check is `powershell -ExecutionPolicy
  Bypass -File .\check.ps1`.
- **Settled contracts:** The integrated completed set must build and execute every prior technology proof,
  preserve `/`, retain the development-only label, and stop before MP-02.
- **Constraints:** Human acceptance is required after MP-01; green automation alone neither accepts the
  milestone nor authorizes the next one. Preserve all unrelated dirty worktree changes.
- **Open questions:** Compiler must assemble the exact ordered proof commands, record any pre-existing
  failures verbatim, and confirm no future file or package was added outside the authorized MP-01 boundary.
