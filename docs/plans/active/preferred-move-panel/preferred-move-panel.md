# Preferred Move Panel - `/repertoire` shows one confirmed choice and one staged proposal

> **Status:** pending - approved direction recorded; implementation has not started

- **Read trigger:** Read before implementing the selected preferred-move panel on `/repertoire`, and reread
  the two authoritative exploration files before each visual or behavior breakpoint.
- **Upstream:** `experiments/mock-ups/preferred-move-panel/DESIGN.md` and
  `experiments/mock-ups/preferred-move-panel/02-staged-move-is-the-proposal-final-choice.html`.

## Outcome

Replace the current add/edit/played-state preferred-move panel with the complete selected two-box
relationship design. The panel will show the last confirmed saved choice and the current local staged
move/proposal, expose only valid persistence actions, support accessible saved-box staging and independent
effective-date changes, and preserve the existing board, source-FEN, local-history, ownership, and typed
feedback contracts.

Implementation acceptance requires semantic agreement with `DESIGN.md` and visible composition matching the
selected HTML mock-up. The selected HTML's demo controls, review-sheet annotations, side cards, and outer
review-sheet chrome are excluded; the implementation must apply the corrections in `DESIGN.md` for action
withholding, first-choice date selection, and gating rather than copying the illustrative demo behavior.

## Scope

- **Included:**
  - A relationship model derived from confirmed saved presence, local staged presence, and canonical UCI
    equality. Remove old preferred-panel view-state and explicit `add`/`edit` draft machinery where no
    longer needed; retain move-history and focused source-position facts outside the panel only when the
    board/session still needs them.
  - Every owner-colour move becoming staged immediately. The saved-choice box becoming the play-and-stage
    capability, including pointer, Enter, Space, visible focus, descriptive accessible name, immediate
    replacement of temporary staging, no confirmation, and no persistence request.
  - Exact relationship/action behavior:

    | Confirmed saved choice | Staged move | Comparison | Presentation | Visible panel actions |
    |---|---|---|---|---|
    | Absent | Absent | N/A | Both labelled boxes remain visible and empty; the staged box contains the one legal-move instruction. | None |
    | Absent | Present | N/A | First-choice proposal. | `Save`, `Change effective date` |
    | Present | Absent | N/A | Saved choice plus empty staged box. | `Change effective date`, `Remove` |
    | Present | Present | Different canonical UCI | Replacement proposal; one consequence names new and old moves. | `Save`, `Change effective date`, `Remove` |
    | Present | Present | Matching canonical UCI | Already saved; one no-change consequence. | `Change effective date`, `Remove`; no `Save` |

  - `Save` persisting only the staged move at the source position's full FEN, with legal canonical UCI and
    selected UTC date when supplied. Successful Save clears staging/pending first-choice date only after
    confirmation and refreshes the read; it does not advance Move History.
  - `Remove` remaining behind the existing `RemoveConfirmation` alert dialog, deleting only the confirmed
    saved choice. It retains staged data on success, retains confirmed saved data while pending or failed,
    restores focus on Cancel, and leaves Save/date available when removing a saved choice with a staged move.
  - `Change effective date` being independent date-only persistence for an existing saved choice. Before
    the first Save, it becomes available once a move is staged and selects a pending initial date for Save;
    it does not claim that the pending date belongs to a saved record. Future days remain disabled through
    `CalendarDate`, UTC normalization remains canonical, and failed date operations retain recoverable input.
  - The approved API contract: add `PATCH /api/preferred-move` with strict `{ fen, effective_at }` input
    (full position identity and new effective date, with no `move_uci`) while retaining the saved move. The
    operation must be atomic and typed, use the fixed owner and existing full-FEN identity, and return the
    confirmed mutation result. It must not use a same-move `PUT` workaround and must not perform a non-atomic
    `DELETE`+`PUT` sequence.
  - Fixed component-owned consequence templates populated from structured model facts, not finished model
    prose:
    - `Save {stagedSan} as the current saved choice.`
    - `Save {stagedSan} to replace {savedSan}.`
    - `{savedSan} is already the current saved choice.`
    - No consequence for saved-without-staging or empty-without-staging; the staged box owns one empty
      explanation such as `Stage a legal move to propose replacing e4.` or `Stage a legal move to propose
      the first saved choice.`
  - The selected shell: existing preferred-move section/landmark and heading association; feature kicker,
    descriptive heading, concise textual status, two peer choice boxes, decorative relationship connector,
    one optional consequence block, and action footer. The saved box contains one SAN, optional UCI, and the
    one saved effective-date display; the staged box contains one SAN/optional UCI or one empty explanation.
  - Exact normal action labels only: `Save`, `Change effective date`, and `Remove`. Remove Add, Edit, Save
    replacement, Cancel edit, and Play saved move panel actions. Dialog Cancel and calendar Clear date/Close
    remain valid primitive labels.
  - `ownTurn`, saveability, loading, mutation, read errors, and workflow errors as gates or transient
    feedback in the same shell, never extra settled panel layouts. Opponent turn offers no owner staging,
    Save, date, or Remove action; a retained saved box is read-only and not clickable. Unsavable/unknown
    positions withhold invalid actions without fake save-ready copy. Pending operations preserve confirmed
    and staged facts, disable relevant controls, and announce one polite status. Errors use typed alert
    feedback and meaningful retry without optimistic success.
  - The saved/staged relationship must remain understandable without colour, in forced-colour mode, with
    reduced motion, and when boxes stack. Wide layouts keep saved, connector, staged in one row; narrow
    layouts stack in that reading order and wrap actions in Save/date/Remove order without horizontal
    overflow.
  - Properly abstracted semantic tokens and reusable primitives before panel composition. Use the existing
    CMT spacing/radius/focus foundation and Material surface/text/outline roles, adding reusable semantic
    aliases only where justified. Use the existing `Button` geometry as the baseline. `Save` and `Remove`
    must be separate reusable canonical components, likely feature/domain wrappers composing `Button`, with
    fixed visible labels, decorative installed icon support, shared icon box and 8px label gap, pending/
    disabled behavior, keyboard activation, focus treatment, and Save-primary/Remove-subordinate hierarchy.
    Do not add domain-specific Button variants without a demonstrated cross-feature need.
  - Preserve the model/presentation boundary: the panel receives relationship facts and callbacks; it does
    not own legal validation, source FEN, owner identity, board history, or a second history cursor. Keep
    `MoveHistory` as the only history surface, keep staged child preview out of it, and preserve candidate,
    promotion, opponent-local continuation, navigation, Flip/Reset cancellation, stale-read protection,
    and source-position identity.
  - Update stories, fixtures, assertions, direct model/component/API tests, backend API/storage tests where
    the PATCH contract affects them, and bounded Storybook browser scenarios for the complete behavior.
- **Expected areas:**
  - `frontend/src/features/repertoire-builder/PreferredMovePanel.tsx` and `.module.css`, plus new or
    appropriately named preferred-move action/choice/connector/consequence primitives and their focused tests.
  - `frontend/src/features/repertoire-builder/repertoireWorkflowModel.ts`,
    `preferredMoveWorkflowState.ts`, `positionPickerSession.ts`, `repertoireBuilderWorkspaceModel.ts`,
    `RepertoireBuilderWorkspace.tsx`, and `RepertoireSessionPanel.tsx`.
  - `frontend/src/features/repertoire-builder/preferredMoveApi.ts`, `preferredMoveState.ts`, feature
    README, story helpers/assertions, and all affected repertoire stories and colocated tests.
  - `frontend/src/features/design-system/Button.tsx`, `Button.module.css`, `CalendarDate.tsx`,
    `CalendarDateUtils.ts`, and existing feedback wrappers only as required to preserve their contracts;
    `frontend/src/styles/cmt-tokens.css` and relevant typescale usage for semantic tokens.
  - `backend/app/features/preferred_move/api_schemas.py`, `router.py`, `service.py`, `repository.py`, and
    the underlying `scripts/opening_catalog/preferred_move.py` contract only as required to implement the
    atomic PATCH without weakening append-only/effective-time behavior.
  - `backend/tests/features/preferred_move/test_api.py`,
    `tests/opening_catalog/test_preferred_move.py` when storage behavior is affected, and
    `tests/e2e/repertoire-builder-storybook.spec.ts`.
- **Excluded:**
  - The exploration files themselves, the outer review-sheet chrome, demo controls, side cards, coverage
    disclosure, review-sheet annotations, and exploratory copy.
  - A move-tree editor, automatic save, opponent-owner workflow, owner/player selector, historical `as_of`
    panel control, second board, analysis recommendation surface, or replacement for Move History.
  - Same-move PUT date changes, DELETE+PUT date changes, silent API contract substitutions, new dependencies,
    unrelated design-system or `/repertoire` refactors, and destructive/non-append-only data changes.
  - Lint, formatting, broad type/build, source-size, aggregate, maintenance, complete-suite, or optional
    Quality closeout work. Independent validation and maintenance remain separate user-requested workflows.

## Settled decisions and implementation invariants

The following decisions are copied into this Plan so implementation does not rely on external design context:

1. `DESIGN.md` is the semantic authority and the selected HTML is the visual authority. The canonical
   panel is the composition inside `article#live-panel`, translated to repository tokens; review-sheet
   chrome is never product UI, and the HTML's illustrative always-present Save, missing first-choice date,
   and “pointless” blocked layouts are corrected by `DESIGN.md`.
2. The relationship is derived from confirmed saved presence, staged presence, and canonical saved/staged
   UCI comparison. SAN is display text; UCI is identity. Old `matching-played` and `unsaved-played` panel
   view states are removed.
3. The left box is the last server-confirmed choice for the focused source FEN. The right box is the local
   staged move and, when different, the proposal Save would persist. Both boxes exist in the empty/empty
   presentation.
4. Every owner move selected from board or analysis is staged immediately. Explicit Add/Edit/Cancel-edit
   lifecycle and explicit Edit mode do not exist. Selecting another legal owner move replaces staging locally
   without confirmation or persistence.
5. An assigned saved box is a real keyboard-focusable play-and-stage control with a descriptive accessible
   name, visible focus treatment, Enter/Space activation, and no nested interactive date. It immediately
   replaces temporary staging, previews the child board position, does not enter Move History, and makes no
   persistence claim or request.
6. `Save` is visible only for a staged first choice or differing replacement and persists the staged move.
   Matching staging has no Save action and cannot issue a no-op save. Save uses full source FEN, canonical
   legal UCI, selected UTC date when present, and server current time otherwise.
7. `Remove` is visible only for confirmed saved presence when the owner action is permitted. It always
   confirms through the existing alert dialog, deletes saved choice/date only, retains staging, and keeps
   confirmed data visible while pending or failed.
8. `Change effective date` is independently date-only. Existing saved records use the new atomic PATCH;
   first-choice staging stores a pending local date and Save persists it. The saved move and staged move do
   not change during an existing-record date operation.
9. The only normal panel action labels are `Save`, `Change effective date`, and `Remove`. No product panel
   copy uses `Add`, `Edit`, `Save replacement`, `Cancel edit`, `Play saved move`, `matching-played`,
   `unsaved-played`, or “pointless”.
10. Consequences are fixed component-owned templates from structured facts. There is exactly one consequence,
    one empty staged explanation, one visible effective date, and one SAN plus optional UCI detail per fact.
11. Opponent turn, `unsavable`, `unknown`, loading, errors, and mutation pending are overlays/gates in the
    same panel shell. They do not create a sixth relationship layout, delete instruction, fake consequence,
    alternate title, or optimistic persistence claim.
12. `PATCH /api/preferred-move` is the approved dedicated date-only contract. Its strict request is
    `{ fen, effective_at }`: it carries the full position identity and new effective date, not a move; the
    server retains the saved move and performs the operation atomically. The existing same-move PUT is known
    to no-op when the requested later date sees the same current move, and DELETE+PUT is non-atomic, so
    neither workaround is allowed.
13. The PATCH must preserve fixed ownership, legal/source-position validation, UTC/future-date validation,
    typed safe errors, append-only/effective-time storage semantics, and unchanged staged state. Any storage
    migration or data-contract change needed to support complete date relocation is an escalation, not an
    unapproved implementation choice.
14. The current `CalendarDate` UTC normalization, future-day blocking, initial focus, and final focus are
    retained. The panel must not duplicate the selected day between a visible date display and the action
    trigger; a pending first-choice date must not be presented as a confirmed saved date.
15. The panel keeps one labelled region, exact box labels `Current saved choice` and `Staged move`, real
    buttons for actions, decorative arrows/icons/dots, shared focus rings, one polite pending announcement,
    typed alerts, and dialog/calendar focus restoration. It must not intercept Move History Arrow/Home/End
    navigation.
16. Semantic state survives monochrome/forced-colour modes and responsive stacking. Existing Material/CMT
    tokens are the source of spacing, surfaces, text, outline, feedback, and focus roles; raw mock-up hex
    values and private mock-up typography are not copied.
17. Board/session ownership remains in `RepertoireBuilderWorkspace` and `positionPickerSession`; the panel
    owns neither a second FEN nor history cursor. Staged child preview remains absent from Move History;
    committed opponent/local history, promotion, navigation, Flip, Reset, and stale request cancellation
    continue to work.
18. Confirmed saved data is not cleared optimistically. Failed reads/mutations/date changes retain facts and
    recoverable input. Successful operations refresh the preferred read and announce the confirmed result
    once without duplicating the session live status.
19. Reusable semantic abstractions precede panel composition. Save and Remove are independently reusable
    canonical components over the existing Button geometry, with consistent labels, icons, spacing,
    keyboard/focus, disabled/pending behavior, and hierarchy.
20. Stories and focused behavioral proof must cover every relationship row, gates, pending/error retention,
    date behavior, saved-box keyboard behavior, Remove confirmation/retention, board/history invariants,
    responsive no-overflow, and accessibility. Passing proof remains valid until a later affecting change;
    only invalidated proof is rerun.

## Stages

Stages are sequential; no stage runs in parallel. Each stage has one implementation outcome and must stop at
its stated escalation boundary rather than choosing a new product, API, data, dependency, ownership, or
acceptance decision.

1. **completed - establish semantic tokens and reusable primitives before panel composition**
   - Ordered actions: map the selected HTML geometry to existing CMT/Material roles; add only reusable
     semantic token aliases; define shared action layout and focus/disabled/pending rules; create reusable
     choice-box, move-value, connector, consequence, date, and action primitives; create named reusable Save
     and Remove components as feature/domain wrappers over `Button`; use installed decorative icons only.
   - Focused proof: prove Save/Remove fixed labels, real button semantics, icon `aria-hidden`, common icon
     box and 8px gap, primary/destructive hierarchy, pending/disabled behavior, keyboard activation,
     focus-visible styling, and reuse outside one anonymous panel branch.
   - Breakpoint/escalation: stop if the abstraction requires a new global Button API, dependency, raw colour,
     or visual direction not justified by the two references.
2. **pending - replace draft/view-state coupling with relationship data flow**
   - Ordered actions: redesign `RepertoirePositionModel` around saved/staged facts and UCI comparison;
     remove obsolete draft helpers/props and old panel state vocabulary; make every owner move stage through
     the normal picker path; route saved-box activation through a play-and-stage transition; adapt workspace,
     session-panel, source-FEN, focused-transition, and read-refresh wiring while preserving board/history,
     promotion, opponent continuation, navigation, Flip, Reset, and stale-read behavior.
   - Focused proof: model matrix and canonical-comparison tests plus picker/workspace tests proving staged
     child preview is absent from Move History and saved-box activation issues no mutation.
   - Breakpoint/escalation: stop if preserving existing local history requires changing the settled source-FEN,
     owner, committed-history, or board-preview contract.
3. **pending - implement PATCH and complete persistence workflow**
   - Ordered actions: add strict frontend/backend PATCH schemas, route, client method, service/repository
     operation, typed failure mapping, and atomic date-only behavior; preserve the existing PUT/DELETE
     contracts; add workflow date mutation/pending/error handling; implement Save first-choice/replacement,
     Remove-retains-staged, refresh, status, and failure-retention semantics.
   - Focused proof: frontend API request/response validation and backend tests for PATCH identity, date-only
     retention, atomicity, UTC/future validation, append-only/effective-time behavior, fixed ownership, and
     unchanged PUT/DELETE behavior.
   - Breakpoint/escalation: do not substitute PUT or DELETE+PUT. Stop for any required schema migration,
     altered append-only meaning, changed response/ownership contract, or inability to relocate an effective
     date correctly without an approved data decision.
4. **pending - compose the selected panel and interactions**
   - Ordered actions: compose the token-backed shell, header/status, peer boxes, decorative responsive
     connector, fixed consequence, exact action footer, one-date treatment, CalendarDate interaction,
     existing RemoveConfirmation, typed feedback, gates, pending states, and accessible focus behavior;
     implement wide/narrow/forced-colour/reduced-motion styling without raw mock-up values or overflow.
   - Focused proof: component tests for all five relationship/action readings, exact labels and withheld
     actions, one-date/one-consequence/one-empty-explanation rules, saved-box Enter/Space/focus behavior,
     dialog/date focus restoration, gates, alerts, pending controls, and responsive DOM semantics.
   - Breakpoint/escalation: stop for any visual mismatch that requires reopening the selected visual direction,
     or any interaction deviation from `DESIGN.md`.
5. **pending - update stories/fixtures and run focused behavioral/browser proof**
   - Ordered actions: replace legacy stories, fixtures, helpers, and assertions with relationship fixtures;
     preserve unrelated history/frequency stories; add first-choice, saved/no-stage, replacement,
     matching, empty/empty, gates, date, mutation, failure, removal-retention, keyboard, promotion, and
     responsive scenarios; update the feature README to the selected terminology; run only the proof below.
   - Focused proof: execute the direct commands in the Proof section, rerunning earlier commands only when a
     later change invalidates their exercised behavior.
   - Breakpoint/escalation: report unrelated failures; do not absorb maintenance work or add a Quality or
     complete-suite closeout stage.

## Progress and decisions

- **Stage 1:** completed - reusable preferred-move primitives and canonical Save/Remove wrappers added without changing the panel or generic Button API; proof: `timeout 150s npm exec -- vitest run --project unit src/features/repertoire-builder/PreferredMoveActionButtons.test.tsx src/features/design-system/Button.test.tsx` passed 15 tests from `frontend` (Bash timeout 180000 ms); breakpoint: not triggered.
- **Stage 2:** pending - proof: not run; breakpoint: preserve board, history, source FEN, and ownership facts.
- **Stage 3:** pending - proof: not run; breakpoint: PATCH is approved; schema/data changes remain escalation-only.
- **Stage 4:** pending - proof: not run; breakpoint: selected HTML visual direction plus `DESIGN.md` semantics.
- **Stage 5:** pending - proof: not run; breakpoint: focused proof only, with no maintenance closeout.
- **Recorded API decision:** use dedicated `PATCH /api/preferred-move` for atomic date-only updates. This is
  required because same-move PUT can be suppressed by move-only deduplication, while DELETE+PUT is not atomic.
- **Recorded abstraction decision:** Save and Remove are reusable feature/domain components composing the
  existing token-driven Button primitive; no new generic Button variant is assumed.
- **Worktree preservation:** do not modify the two authoritative preferred-panel references or the unrelated
  modified `experiments/mock-ups/saved-moves/saved-move.html`.

## Proof

All commands below use Git Bash and have an explicit command-level timeout. The listed Bash tool timeout is
also mandatory; no proof command may run unbounded.

- **Foundation and frontend unit/component proof** (from `frontend`; command timeout 150 seconds; Bash tool
  timeout `180000` ms):
  ```bash
  timeout 150s npm exec -- vitest run --project unit src/features/repertoire-builder/PreferredMoveActionButtons.test.tsx src/features/repertoire-builder/PreferredMovePanel.test.tsx src/features/design-system/Button.test.tsx src/features/repertoire-builder/repertoireWorkflowModel.test.ts src/features/repertoire-builder/positionPickerSession.test.ts src/features/repertoire-builder/preferredMoveApi.test.ts src/features/repertoire-builder/preferredMoveState.test.ts src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspaceWorkflow.test.tsx
  ```
- **Backend/API and effective-time proof** (from the repository root; command timeout 120 seconds; Bash tool
  timeout `150000` ms):
  ```bash
  timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/preferred_move/test_api.py tests/opening_catalog/test_preferred_move.py
  ```
- **Bounded selected browser proof** (from the repository root; command timeout 180 seconds; Bash tool
  timeout `240000` ms):
  ```bash
  timeout 180s npx playwright test --config tests/e2e/playwright.config.ts tests/e2e/repertoire-builder-storybook.spec.ts
  ```
  The affected browser scenarios must prove all five relationship rows, both empty boxes, exact action
  visibility, saved-box Enter/Space replacement without API mutation, Save, PATCH date-only retention,
  first-choice date selection, Remove confirmation/retained staging, gates/errors/pending states, board and
  Move History invariants, 412px no-overflow, focus, and Axe coverage.

## Escalation boundaries

- Do not change the approved PATCH contract, replace it with PUT or DELETE+PUT, or change its atomic/date-only
  meaning without coordinator/user resolution.
- Escalate any required schema migration, new storage action, altered append-only/effective-time semantics,
  destructive data operation, ownership/player change, dependency, or unrelated API change.
- Escalate any deviation from the authoritative `DESIGN.md` relationship matrix, labels, accessibility,
  responsive behavior, fixed copy templates, token/abstraction requirement, or selected mock-up composition.
- Escalate conflicts with concurrent/user edits, especially changes to either authoritative design reference;
  preserve those edits and do not resolve the conflict autonomously.
- Escalate any acceptance expansion beyond the single complete preferred-move panel outcome. Unrelated test or
  maintenance failures are reported, not absorbed.

## Visible result

> On `/repertoire`, the panel clearly shows what is saved and what is staged, offers only the valid Save/date/Remove action, and lets the user play-and-stage the saved choice without losing board or history behavior.
