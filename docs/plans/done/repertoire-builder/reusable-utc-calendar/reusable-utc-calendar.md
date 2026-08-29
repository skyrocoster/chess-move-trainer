# Reusable UTC calendar date - A token-styled Popover calendar selects UTC dates

> **Status:** accepted/done - R1 complete; fresh final Quality validation passed and the Plan is archived

- **Read trigger:** Read before each R1 execution stage, before changing the reusable calendar, its frontend manifests,
  its stories/tests, or the established Popover/token boundary, and at final closeout.
- **Upstream:** [Repertoire Builder master plan](../../../../master-plans/repertoire-builder/repertoire-builder.md);
  [confirmed Repertoire Builder direction](../../../../grilling-docs/DONE/repertoire-builder-direction.md);
  [accepted V3 clickable-analysis-moves Plan](../../../../plans/done/repertoire-builder/viewer-clickable-analysis-moves/viewer-clickable-analysis-moves.md)

## Outcome

Add one reusable, token-styled calendar-date component for the later Repertoire Builder workflow. It uses the approved
`react-day-picker@10.0.1` package inside the established Base UI Popover boundary, has no editable time, treats blank as
effective now for its later consumer, maps a selected calendar date to `00:00 UTC`, disables future UTC calendar dates,
and exposes a bounded clear/reset seam without integrating application state, mutations, or persistence.

## Scope

- **Included:** The exact direct `react-day-picker@10.0.1` dependency and npm lockfile update; one reusable calendar-date
  component in the design-system area; local token styling and Popover composition; deterministic UTC date
  normalization and future-date comparison; a bounded blank/clear/reset seam for later W2 use; focused unit,
  accessibility, keyboard, interaction, and Storybook proof; and this Plan record.
- **Expected areas:** `frontend/src/features/design-system/CalendarDate.tsx`,
  `frontend/src/features/design-system/CalendarDate.module.css` only if local styling is needed,
  `frontend/src/features/design-system/CalendarDate.test.tsx`,
  `frontend/src/features/design-system/CalendarDate.stories.tsx`, `frontend/package.json`,
  `frontend/package-lock.json`, and this Plan record. Existing Storybook configuration already covers the
  design-system story area and should not need changes.
- **Excluded:** Repertoire route or navigation work; Viewer or Analysis integration; Add/Edit/Remove mutation wiring;
  preferred-move or context clients; backend/API/database/schema/storage changes; editable time; local-time or
  non-UTC semantics; range or multiple-date selection; new global tokens, global package CSS, or design-system
  primitives; direct `date-fns` or `@date-fns/tz` dependencies; dependencies other than the approved package;
  new browser profiles/specs; unrelated visual redesign; README or historical-record edits; runtime writes; generated
  artifacts; `--fix`; commits; pushes; and unrelated worktree changes.

## Stages

1. **complete - Establish the approved dependency and UTC calendar boundary.** Add only the coordinator-authorized
   package and implement the reusable selection surface without application integration.
   - **Ordered actions:** Re-read this Plan, the master Plan, the confirmed direction, the accepted V3 record, and the
     current design-system/Popover conventions before editing. Add the exact direct pin `react-day-picker@10.0.1` to
     the frontend manifest and npm lockfile using the repository's npm lockfile v3. Preserve its package-managed
     runtime transitives `date-fns@^4.1.0` and `@date-fns/tz@^1.4.1` only as transitives; do not add either directly or
     add any other package. Use Base UI Popover and local CSS-module token styling; do not import the package's default
     CSS unless the package API makes local ownership impossible.
   - **UTC contract:** Treat a calendar day as the UTC tuple `(year, month, day)`. Derive the current UTC calendar day
     from an explicit instant. A date is future and unavailable only when its UTC tuple is strictly later than that
     current UTC tuple; the current UTC day remains selectable regardless of the current time. Convert a selected
     calendar tuple with `Date.UTC(year, month, day, 0, 0, 0, 0)`, never local `Date` getters or local-midnight
     construction. Represent blank as the component's empty selection/effective-now state; the later W2 consumer, not
     this component, performs mutations and maps blank to its effective now. The clear/reset seam must allow that
     consumer to return the component to blank after a successful mutation.
   - **Deterministic test seam:** Keep the production-facing behavior defaulted to the current instant, but put the UTC
     day calculation behind a pure/internal helper that accepts an explicit `now: Date`. Tests pass fixed instants
     around UTC midnight and never depend on the host timezone or wall clock. Do not expose a new product clock control
     or change the later mutation contract merely to make tests deterministic.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/design-system/CalendarDate.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a recommended finite `bash` tool timeout of `150000` ms.
   - **Breakpoint:** Stop if the approved package API cannot provide the bounded Popover/calendar behavior without
     default global CSS, another dependency, a changed UTC rule, a new public persistence contract, or a new product
     or visual decision.

2. **complete - Prove the reusable interaction and accessible presentation.** Make the component inspectable through
   existing Storybook coverage without creating an application surface.
   - **Ordered actions:** Add stories for blank, selected, future-disabled, and constrained states using existing
     design-system token conventions. Add Storybook play coverage for opening/closing the Popover, keyboard date
     selection, blank/clear behavior, focus semantics, and accessible names/roles. Add focused component proof for
     axe-clean markup, keyboard interaction, UTC-midnight emission, UTC-midnight boundary comparison, current-day
     selectability, future-day disabling, and clear/reset behavior. Keep the component styling local and do not add
     package-default CSS, a global primitive, or a new browser spec/profile. Build Storybook before running its
     configured interaction suite.
   - **Focused proof:**
     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     Each command has a recommended finite `bash` tool timeout of `360000` ms. Storybook interaction testing must use
     the supported configured command without a `--url` argument.
   - **Breakpoint:** A bounded visual/accessibility review is required at the existing wide and constrained Storybook
     states. Stop rather than guessing if the calendar needs a new hierarchy, copy, date-format decision, responsive
     rule, token, design primitive, focus model, or acceptance change.

3. **accepted/done - Complete read-only validation and prepare coordinator closeout.** Confirm the accepted R1 result and
   preserve all unrelated material before execution can be accepted.
   - **Ordered actions:** Re-run the focused component tests and frontend build, then run Storybook build/interactions,
     lint, read-only Prettier, source-size validation, and the final whitespace proof. Perform the one final Git scope
     audit against the coordinator baseline, confirming only the approved calendar component, focused proof, manifests,
     and this active Plan are in scope. Preserve unrelated worktree content, all application/persistence surfaces, and
     all historical records. Report unrelated failures rather than repairing or absorbing them. Do not use `--fix`.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/design-system/CalendarDate.test.tsx`

     `timeout 120s npm.cmd run build --prefix frontend`

     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     `timeout 120s npm.cmd run lint --prefix frontend`

     `timeout 120s frontend/node_modules/.bin/prettier.cmd --check frontend/src/features/design-system/CalendarDate* frontend/package.json frontend/package-lock.json`

     `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`

     `timeout 30s git diff --check`

     `timeout 600s .venv/Scripts/python.exe scripts/check.py`

     Recommended finite `bash` tool timeouts are respectively `150000`, `150000`, `360000`, `360000`, `150000`,
     `150000`, `90000`, `60000`, and `660000` ms. The repository closeout runs without `--fix`.
   - **Breakpoint:** Coordinator-owned independent Quality validation, successful bounded Storybook cleanup, a clean
     final scope audit, and final acceptance are required before archival. Stop for any unrelated failure requiring
     repair or any scope, acceptance, contract, ownership, dependency, or safety expansion.

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the outcome
or requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - CalendarDate and the approved UTC comparison/test seam were implemented; 9 focused tests
  passed. The fake-timer timeout repair was test-only, and the source Prettier repair was formatting-only; breakpoint:
  none.
- **Stage 2:** complete - stories cover blank, selected, current, future, clear, keyboard, focus, constrained, and
  forced-colors states; Storybook passed 30 files/161 tests; breakpoint: none.
- **Stage 3:** accepted/done - the exact full closeout, focused/build/lint/read-only Prettier/size/whitespace proof,
  cleanup, and port checks passed; fresh independent Quality validation passed and accepted semantic, dependency, and
  scope review; breakpoint: none.
- **Settled decisions:** R1 uses the exact direct pin `react-day-picker@10.0.1`; React 19/Node `>=24` compatibility and
  npm lockfile v3 are accepted. `date-fns@^4.1.0` and `@date-fns/tz@^1.4.1` remain package-managed transitives only.
  The component uses Base UI Popover and repository tokens, has no editable time, compares UTC calendar tuples, maps
  selected dates to UTC midnight, and leaves mutation integration to W2.
- **No new product decision:** The deterministic clock seam is internal/pure and test-injected; it does not expose a
  user-facing current-date control or alter blank/effective-now semantics.
- **Dependency and repair record:** `react-day-picker@10.0.1` is the exact direct dependency; only its expected
  package-managed transitives are present, with no direct `date-fns` or `@date-fns/tz` dependency. The only repairs
  were test-only fake-timer timeout handling and source formatting; neither changed product semantics. The separate
  design-system README updater added the CalendarDate signpost and required no validation.

## Proof

- Focused Vitest/React Testing Library proof covers blank/effective-now representation, clear/reset, keyboard and
  Popover behavior, accessible roles and focus, exact UTC-midnight conversion, the UTC calendar-day boundary around
  midnight, current-day selectability, and future-date disabling with fixed injected instants.
- Storybook build and the supported headless Chromium `test-storybook -- --run` command cover the reusable stories,
  interaction states, accessibility, and constrained presentation. No new E2E profile or spec is required because the
  configured Storybook Vitest project already runs stories in Chromium.
- Frontend build, lint, read-only Prettier, source-size validation, `git diff --check`, and the exact governing
  `timeout 600s .venv/Scripts/python.exe scripts/check.py` closeout run with finite command and tool timeouts.
- Final scope review must preserve the approved dependency boundary, package-managed transitives, unrelated worktree
  material, completed Plans, the master Plan, and all excluded application/persistence surfaces.
- Final accepted proof: Stage 1 passed 9 focused tests; Storybook passed 30 files/161 tests; the exact
  `timeout 600s .venv/Scripts/python.exe scripts/check.py` closeout and focused/build/lint/read-only Prettier/size/
  `git diff --check` proof passed; cleanup and ports were clean. Fresh independent Quality validation reran the
  focused tests, build/lint/Prettier/size/diff, Storybook build and all 30/161 interactions, and accepted semantics,
  dependency, and scope.

## Escalation boundaries

- Any dependency other than direct `react-day-picker@10.0.1`, any direct `date-fns` or `@date-fns/tz` dependency, any
  package API incompatibility, or any requirement for package-default global CSS, another stylesheet, or a new design
  primitive.
- Any change to UTC comparison, selected-date normalization, blank/effective-now meaning, future-date policy, or the
  internal deterministic clock seam; local-time behavior, locale/timezone choices, editable time, ranges, and multiple
  dates are not authorized.
- Any new public mutation/API/persistence contract, route, Viewer integration, preferred-move behavior, schema/storage
  work, ownership rule, automatic selection, or consumer behavior beyond the bounded clear/reset seam.
- Any new visual hierarchy, copy, date-format, responsive, focus, accessibility, token, or design-system ownership
  decision not supported by the settled direction and existing Popover conventions.
- Any new browser profile/spec, Storybook configuration change, runtime write, generated artifact, size violation,
  `--fix`, commit, push, historical-record edit, direct baseline collision, failed server cleanup, or unrelated failure
  requiring repair or scope absorption.

## Visible result

> **Accepted R1 result (done):** A user can open one token-styled Popover calendar, choose any allowed UTC date, and
> clear it again without entering a time or changing application persistence.
