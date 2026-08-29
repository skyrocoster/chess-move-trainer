# Complete preferred-move workflow - explicit management of one saved move

> **Status:** accepted/done - W2 complete; fresh final Quality validation passed and the Plan is archived

- **Read trigger:** Read before each W2 execution stage, before changing the Repertoire Builder preferred-move
  workflow, frontend API client, context/date composition, or focused proof, and at final closeout.
- **Upstream:** [Repertoire Builder master Plan](../../../../master-plans/repertoire-builder/repertoire-builder.md);
  [confirmed Repertoire Builder direction](../../../../grilling-docs/DONE/repertoire-builder-direction.md);
  [accepted W1 position-picker Plan](../../../../plans/done/repertoire-builder/position-picker-local-session/position-picker-local-session.md);
  [accepted preferred-move API Plan](../../../../plans/done/preferred-move-api/preferred-move-api.md);
  [accepted R1 UTC calendar Plan](../../../../plans/done/repertoire-builder/reusable-utc-calendar/reusable-utc-calendar.md);
  [accepted A1 position-context Plan](../../../../plans/done/repertoire-builder/neutral-position-context-api/neutral-position-context-api.md)

## Outcome

Complete the `/repertoire` preferred-move workflow over the existing W1 position-picker session. A person can inspect
one fixed-owner saved move in read-only form, explicitly add or replace it, play it locally, or confirm its removal.
The page shows the approved neutral context and saveability meaning, accepts one UTC calendar date for each mutation,
and preserves the existing preferred-move API, append-only storage, W1 local-line behavior, and ownership boundaries.

## Scope

- **Included:** A typed frontend client for the accepted preferred-move GET/PUT/DELETE contract; page-owned preferred
  move read and mutation state; read-only saved-move display; explicit Add, Save, Edit, Play saved move, and confirmed
  Remove actions; legal board/candidate selection through W1 seams; current-bottom-color context and saveability
  messaging; the existing reusable UTC calendar consumer behavior; focused component/client tests; existing Repertoire
  Builder Storybook states and interactions; and bounded existing Repertoire Builder Storybook browser proof.
- **Expected areas:** `frontend/src/features/repertoire-builder/**` for the page-local client, state, workflow
  presentation, tests, stories, and local CSS; existing `frontend/src/features/viewer/positionContextApi.ts`,
  `positionContextState.ts`, and `PositionContext.tsx` only for bounded composition or regression proof when needed;
  `frontend/src/features/design-system/CalendarDate.tsx` only as the approved consumer boundary; and
  `tests/e2e/repertoire-builder-storybook.spec.ts` plus existing `tests/e2e/playwright.config.ts` only for bounded
  additions to the registered Storybook proof. `backend/app/features/preferred_move/**` and its focused tests are
  read-only authoritative contract evidence, not W2 implementation areas.
- **Excluded:** Backend/API/schema/storage changes; new preferred-move endpoints, fields, or ownership; unobserved
  position insertion; multiple preferred moves; automatic engine, population, or selection authority; silent
  persistence; changes to W1 session semantics, Viewer behavior, A1 context facts, or R1 calendar rules; editable time,
  local-time semantics, new dependencies, new browser profiles or specs, universal abstractions, unrelated visual
  redesign, runtime database writes, generated artifacts, README or historical-record edits, commits, pushes, and
  unrelated worktree changes.

## Settled semantics

- The stable Skyrocoster owner and the exact four-field position identity remain fixed by the accepted backend API and
  storage. HTTP requests use the full six-field FEN and legal canonical UCI; backend responses provide SAN.
- A position with no overall corpus existence remains navigable but unsavable. A zero count in the selected personal
  color while the position exists overall remains savable.
- `session.bottomColor` selects the personal recurrence scope: `white_count` for White and `black_count` for Black.
  The displayed context uses the approved `Seen in N games as White/Black` or `Never seen as White/Black` meaning.
- A saved move is displayed and actionable only when the side to move equals the current bottom color. It opens
  read-only and exposes explicit Edit, Play saved move, and confirmed Remove actions. Playing it changes only the
  local W1 line; it never mutates the API.
- A legal move selected on an own-color turn is staged until explicit Add or Save. A move on an opponent turn advances
  the local line immediately and is never persisted. Board dragging and every displayed legal analysis candidate,
  including Best line, retain W1's legal and promotion path.
- Blank date means the mutation's effective time is now. A selected date is the CalendarDate UTC-midnight value. The
  date control is cleared only after a successful Add, Save, or Remove mutation; failed mutations retain their state.
- Frontend and Storybook/browser proof uses mocked API clients and deterministic fixtures. Focused backend tests use
  isolated temporary databases. No W2 proof writes the runtime database.

## Stages

1. **complete - Establish the typed preferred-move and context state seams.** Add the smallest page-local boundary needed
   to read the accepted API and derive the settled saveability meaning without changing backend or W1 contracts.
   - **Ordered actions:** Re-read this Plan, the master Plan, the confirmed direction, W1, the preferred-move API,
     A1, and R1 records. Inspect the current W1 session/workspace, position-context client/state, PositionContext,
     CalendarDate, and accepted backend tests before editing. Add strict runtime validation for the accepted preferred
     move response, mutation responses, and safe typed failures. Use the current full `currentPosition.fen`; do not add
     a player field or alter GET/PUT/DELETE semantics. Compose displayed-FEN context from the existing position-context
     seam, select the count by `bottomColor`, and keep absent-overall unsavable while preserving zero-personal-count
     saveability. Keep page state page-local; if the current workspace approaches the 500-line limit, extract only a
     bounded Repertoire-local component or helper and do not create a universal workspace/session abstraction.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/repertoire-builder`

     `timeout 120s npm.cmd run build --prefix frontend`

     Each command has a finite recommended `bash` tool timeout of `150000` ms. Frontend tests mock the API and never
     select the runtime database.
   - **Breakpoint:** Stop and escalate if the accepted API response/error contract, full-FEN boundary, fixed owner,
     context denominator, saveability rule, W1 ownership, or source-size limit requires a new product, API, data,
     ownership, persistence, or abstraction decision.

2. **complete - Implement explicit saved-move actions and UTC-dated mutations.** Connect the W1 staged/local move seams
   to the existing preferred-move lifecycle without silent persistence or duplicate chess rules.
   - **Ordered actions:** Re-read the current W1 workspace and the accepted preferred-move and CalendarDate contracts
     before editing. Show assigned moves read-only only on own-color turns. Allow Edit to select one legal replacement,
     then require explicit Save; require explicit Add for a newly staged move. Route Play saved move through the
     existing legal local move/promotion path and leave persisted state unchanged. Require confirmation before Remove,
     then issue the accepted DELETE only after confirmation. Before implementing confirmation, locate an established
     accessible dialog/confirmation convention in the repository and reuse it exactly if one exists. If no factual
     precedent exists and a material visual hierarchy, focus, dialog, or confirmation decision is needed, stop at the
     execution breakpoint and escalate rather than inventing one. Pass selected UTC-midnight dates to `effective_at`
     and pass blank as the accepted effective-now state. Clear the date only after a successful mutation; retain date,
     staging, and safe status on failure. Refresh or update the read-only result without changing append-only backend
     behavior, and keep opponent moves local-only.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/repertoire-builder`

     `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_move -q`

     Each command has a finite recommended `bash` tool timeout of `150000` ms. The backend suite must continue to use
     its isolated temporary-database fixtures; no backend source or runtime database changes are authorized.
   - **Breakpoint:** Stop and escalate for any API field/status or timestamp change, mutation of an absent-overall
     position, automatic selection, multiple move, silent save, changed confirmation/focus decision, changed Viewer or
     W1 behavior, or inability to reuse the existing legal/promotion path.

3. **complete - Prove the complete workflow in Storybook and the existing browser surface.** Make the settled states
   inspectable at wide and constrained sizes without adding a browser profile or new product surface.
   - **Ordered actions:** Add deterministic stories and interactions for unassigned/savable, assigned/read-only,
     Edit/Save, Play saved move, Add, confirmed Remove, failed mutation, selected UTC date, blank-now behavior,
     zero-versus-absent context, opponent-only local movement, keyboard/focus, accessibility, constrained fit, and
     no-overflow behavior. Reuse the current Storybook fixtures and registered Repertoire Builder browser spec. Build
     Storybook before its interaction suite; bound readiness to 30 seconds, clean only the proof server, and confirm
     port 6006 is free. Perform a bounded visual/accessibility review at existing wide and constrained states. Do not
     guess new copy, hierarchy, token, focus, responsive, confirmation, or selector decisions; escalate if existing
     conventions do not settle them.
   - **Focused proof:**
     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`

     Each command has a finite recommended `bash` tool timeout of `360000` ms. Storybook startup health has a separate
     maximum of 30 seconds and the server must not remain running after proof.
   - **Breakpoint:** Stop for any new visual or accessibility hierarchy, confirmation/focus model, responsive rule,
     selector contract, browser profile/spec, dependency, or acceptance decision.

4. **accepted/done - Complete read-only validation and prepare coordinator closeout.** Confirm W2 while preserving all
   accepted upstreams, backend boundaries, and unrelated material before independent Quality validation.
   - **Ordered actions:** Re-run the focused frontend workflow/client/context tests and isolated backend preferred-move
     tests, frontend build, Storybook build/interactions, bounded Repertoire Builder browser proof, lint, read-only
     Prettier, source-size validation, and whitespace proof. Run the governing repository check without `--fix` or
     `--full`. A trivial deterministic formatting repair is preauthorized only in W2-touched files after a read-only
     check identifies it; inspect the resulting scope and do not use `scripts/check.py --fix` or perform semantic repair.
     Perform the one final Git scope audit against the coordinator baseline during execution only. Preserve W1, Viewer,
     A1, R1, the accepted backend contract, completed historical records, and unrelated worktree content. Report
     unrelated failures rather than repairing or absorbing them.
   - **Focused proof:**
     `timeout 120s npm.cmd test --prefix frontend -- --run src/features/repertoire-builder`

     `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_move -q`

     `timeout 120s npm.cmd run build --prefix frontend`

     `timeout 300s npm.cmd run build-storybook --prefix frontend`

     `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run`

     `timeout 300s ./node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts`

     `timeout 120s npm.cmd run lint --prefix frontend`

     `timeout 120s frontend/node_modules/.bin/prettier.cmd --check frontend/src/features/repertoire-builder tests/e2e/repertoire-builder-storybook.spec.ts`

     `timeout 60s .venv/Scripts/python.exe scripts/check_size.py --source-max 500 --test-max 700`

     `timeout 30s git diff --check`

     `timeout 600s .venv/Scripts/python.exe scripts/check.py`

     Recommended finite `bash` tool timeouts are respectively `150000`, `150000`, `150000`, `360000`, `360000`,
     `360000`, `150000`, `150000`, `90000`, `60000`, and `660000` ms. The governing closeout runs without `--fix` or
     `--full`; all browser/server cleanup and listener checks remain bounded.
   - **Breakpoint:** Coordinator-owned independent Quality validation, successful Storybook cleanup with port 6006
     confirmation, final acceptance, and a clean scope audit are required before archival. Stop for any unrelated
     failure requiring repair or any scope, contract, ownership, visual, dependency, runtime-write, or safety expansion.

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the outcome or
requiring a new human decision.

## Progress and decisions

- **Stage 1:** complete - typed preferred-move read/mutation acknowledgment and context/saveability state; focused
  frontend proof passed 76 tests; breakpoint: none.
- **Stage 2:** complete - explicit Add/Save/Edit/Play/confirmed Remove workflow with UTC date behavior; isolated backend
  preferred-move proof passed 17 tests; breakpoint: none.
- **Stage 3:** complete - deterministic Storybook and existing Repertoire Builder browser proof; Storybook passed 32
  files/184 tests and the bounded E2E proof passed 6 tests; breakpoint: none.
- **Stage 4:** accepted/done - read-only closeout, fresh independent Quality PASS, acceptance, cleanup, and final scope
  audit completed; breakpoint: none.
- **Settled decisions:** One fixed-owner preferred move remains authoritative; absent overall positions are unsavable,
  zero personal-color counts remain savable, and `bottomColor` selects the personal scope. Saved moves are visible and
  actionable only on own-color turns; opponent moves are local-only. Blank dates mean now, selected dates are UTC
  midnight, and dates clear only after successful mutation. Frontend/browser proof is mocked and backend proof is
  isolated; no runtime writes, new dependencies, browser profiles/specs, backend changes, or W1/Viewer changes are
  included.
- **No new decision:** Confirmation mechanism is not selected here. Execution must reuse an established accessible
  confirmation convention; a material visual or focus choice without factual precedent is an escalation.
- **Validation-only timing repair:** App lazy heading lookup uses a 5-second find timeout with a 20-second per-test
  timeout, and responsive heading lookup uses a 10-second timeout; these are test-only changes with no product semantic
  impact.
- **Closeout decision:** Accept W2 as done. The separate README updater remains separate; this record-only closeout edits
  no product, test, or README files.

## Proof

- Focused frontend proof covers strict mocked preferred-move responses/failures, full-FEN requests, context-derived
  saveability, read-only visibility, explicit Add/Save/Edit/Play/Remove behavior, confirmation, failed mutations,
  UTC-midnight and blank dates, successful-only date clearing, W1 staging/opponent/local navigation, and accessibility.
- Existing isolated backend preferred-move tests remain a regression guard for the unchanged fixed-owner API, append-only
  behavior, timestamps, safe errors, and no request-time schema/runtime writes.
- Storybook and the existing Repertoire Builder browser spec cover assigned/unassigned, zero-versus-absent, mutation,
  confirmation, date, keyboard, accessibility, constrained, and no-overflow states using mocked clients and fixtures.
- Frontend build, lint, read-only Prettier, source/test size, `git diff --check`, and the exact finite
  `timeout 600s .venv/Scripts/python.exe scripts/check.py` closeout run without `--fix` or `--full`.
- Final accepted proof passed the focused frontend workflow/client/context proof at 76 tests, isolated backend
  preferred-move proof at 17 tests, Storybook at 32 files/184 tests, and the bounded E2E proof at 6 tests. Fresh
  independent Quality PASS covered App4/full356, browser12, targeted format, the default `scripts/check` run, and
  `scripts/check --full` including E2E; listeners were clean. The App lazy-heading 5-second find/20-second per-test and
  responsive-heading 10-second timing adjustments were test-only repairs.

## Acceptance

The result is acceptable only when a person can start from either accepted W1 origin, inspect a saved move read-only on
an own-color turn, explicitly Add or Save one legal staged move, Edit and replace it, Play it locally without mutation,
and confirm its Remove. A saved move is hidden on opponent turns; opponent choices advance locally and never persist.
The current bottom-color context shows the approved White/Black seen/never-seen meaning, permits saving when the overall
position exists even at zero personal count, and blocks saving when the position is absent overall. Blank date uses
effective now, selected dates use UTC midnight, and the date clears only after successful Add/Save/Remove. The accepted
preferred-move API, append-only storage, fixed ownership, W1 behavior, Viewer behavior, and runtime database remain
unchanged. Focused tests, isolated backend regression, Storybook, existing browser proof, finite repository checks,
independent Quality validation, final acceptance, and scope audit pass.

## Escalation boundaries

- Any change to the accepted preferred-move HTTP fields, statuses, errors, full-FEN boundary, legal UCI/SAN behavior,
  timestamps, fixed ownership, four-field identity, append-only storage, or backend/schema policy.
- Any attempt to save an absent-overall position, persist an opponent move, select automatically, store multiple moves,
  add a new endpoint/field, expose a new identity, or change explicit user authority.
- Any change to `bottomColor` meaning, zero-versus-absent saveability, saved-move visibility, W1 legal/promotion/session
  ownership, Viewer behavior, A1 recurrence facts, or R1 UTC/blank/clear semantics.
- Any need for a confirmation dialog, visual hierarchy, copy, token, focus, accessibility, responsive, or selector
  decision not established by repository precedent. Reuse an established accessible confirmation convention; otherwise
  stop during execution and return to the coordinator rather than guessing.
- Any dependency, browser profile/spec, universal abstraction, runtime database write, generated artifact, source/test
  size violation, unbounded command/server, failed Storybook cleanup or occupied port 6006, `--fix`, commit, push,
  historical edit, direct baseline collision, or unrelated failure requiring repair or scope absorption.

## Visible result

> **Accepted W2 result (done):** A person can explicitly inspect, add, replace, play, date, and confirm removal of one
> preferred move in Repertoire Builder while unsavable positions remain safe, dates clear only after success, and W1 plus
> the accepted backend remain unchanged.
