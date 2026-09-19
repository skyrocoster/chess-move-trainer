# Approved form controls and Trainer opening search integration

> **Status:** done - Stages 1-5 accepted on 2026-09-15

- **Read trigger:** Read before implementing the approved reusable form-control integration, opening catalogue cache, or Trainer Practice opening search. Read the upstream grilling record and approved Storybook candidate before making a visual or behavior-sensitive change.
- **Upstream:** [`docs/grilling-docs/reusable-form-controls-and-opening-search-direction.md`](../../grilling-docs/reusable-form-controls-and-opening-search-direction.md) governs product behavior and repository meaning; the approved production-backed candidate in `frontend/src/features/design-system/form-controls/` governs the control composition and visual interaction; `experiments/mock-ups/opening-search-combobox/index.html` is parent visual direction only. The candidate story is retained as an upstream reference until the final cleanup stage.

## Outcome

Trainer Practice uses the approved reusable controls to select a specific opening or an explicit **All openings** choice, choose Learner colour, retain the as-of date, and retrieve real training-required positions with the existing request contract and in-place loading, empty, stale-date, error, and result behavior. Game Loader and Line Library Filters use the same shared field/control language without changing their meanings or interaction timing.

The opening catalogue is fetched as one complete, versioned snapshot, persisted in the browser, filtered locally while typing, and refreshed when the backend reports a different active-database version. The final implementation retains production controls, styles, and tests, while removing the temporary exploratory Storybook story only after integrated behavior and visual fidelity have been accepted.

## Scope

- **Included:**
  - Promote and use the approved `Field`, `TextInput`, `Select`, `Combobox`, `RadioGroup`, and rich-option foundations without recreating the Storybook design.
  - Migrate or replace the eight suitable controls:
    1. Trainer Practice catalogue search input.
    2. Trainer Practice raw Opening select.
    3. Trainer Practice Learner colour select.
    4. Trainer Practice native as-of date input.
    5. Game Loader UUID input.
    6. Line Library Filters search input.
    7. Line Library Filters select.
    8. Line Library Filters binary checkbox.
  - Keep native date behavior through Field-only treatment and keep the existing binary Base UI checkbox and clickable label. The tri-state tree checkbox is not a migration candidate.
  - Add an opaque backend opening-catalogue version response header and a validated, namespaced, versioned localStorage snapshot of the complete catalogue.
  - Replace the Trainer Practice search button/input and raw Opening select with the approved opening-search composition, using only current production fields: stable key, ECO, name, and `route_count` where useful.
  - Preserve the existing `GET /api/positions/training-requirements` request, including exact opening key plus `opening_match=reached` for a specific opening, omitted opening filters for All, optional Learner colour, as-of date, `training_requirement_lt=0`, pagination, and abort behavior.
  - Prove focused component, API, backend, application, Storybook, and browser behavior at the listed stages.
- **Expected areas:**
  - `frontend/src/features/design-system/form-controls/**`
  - `frontend/src/features/game/GameLoader.tsx`, `frontend/src/features/game/GameLoader.module.css`, and `frontend/src/features/game/GameLoader.test.tsx`
  - `frontend/src/features/design-system/line-library/LineLibraryFilters.tsx`, `frontend/src/features/design-system/line-library/LineLibrary.module.css`, and `frontend/src/features/design-system/line-library/LineLibrary.test.tsx`
  - `frontend/src/features/trainer-practice/**`, including small opening-composition or storage helpers created inside this feature area only
  - `frontend/src/api/queryKeys.ts`, its focused test, and the existing handwritten API facade only if a bounded adapter requires it
  - `backend/app/caching.py`, `backend/app/main.py`, `backend/app/features/openings/**`, and focused opening/cache tests under `backend/tests/features/{openings,api_cache}/`
  - `frontend/src/App.test.tsx` and `tests/e2e/trainer-practice.spec.ts`
- **Excluded:**
  - Repertoire-side API or state, any assumption that openings are colour-specific, and any synchronization between repertoire side and Learner colour.
  - Chain, repertoire-line, preferred-move, SAN-preview, move-replay, or other invented opening data models. Fixture-only repertoire-side and move-preview fields remain omitted from application rows.
  - A playable training session, new trainer-session endpoint, session length/randomization, or changes to scoring and scheduling semantics.
  - The Line Library composite tri-state tree checkbox, unrelated refactors, new dependencies, CI, broad maintenance checks, and changes to completed grilling records.
  - Git branches, worktrees, stashes, commits, pushes, or destructive repository/storage operations. The application may discard only an invalid entry in its own namespaced catalogue key; it must not clear unrelated browser storage.

## Design fidelity

- **Authority:** The grilling record is the behavior and product/repository authority. `ReusableFormControls.stories.tsx`, the approved production components, and `FormControls.module.css` are the signed-off executable visual authority from 2026-09-15. The HTML mock-up supplies only the parent concept; Storybook overrides it where they differ.
- **Excluded artifact content:** Do not integrate the mock-up masthead, hero, catalogue panel chrome, fake start workflow, fixture data, or handwritten accessibility implementation. The real action is retrieval and is labeled **Find training positions**, not **Start training**.

| Anchor | Preserve | Allowed adaptation | Acceptance |
|---|---|---|---|
| Shared Field and input states | Consistent label association, help/error presentation, required/disabled/invalid styling, external validation timing, fluid field frame, focus ring, and leading/trailing slots | Use the existing application shell and production tokens; retain feature-owned validation timing | Stage 1 focused control and consumer tests |
| Dropdown composition | Select, Combobox, and Autocomplete remain distinct; anchored popup is at least control width, can prefer a wider rich popup, collides within viewport gutters, bounds height, and scrolls internally | Opening-specific content is composed through the approved public option anatomy; do not expose Base UI popup internals to features | Stage 3 interaction tests and Stage 4 popup checks at 1280px and 412px |
| Opening option anatomy | ECO-leading content, opening name as primary content, selection indicator, and responsive option layout | Application rows use ECO, name, and current `route_count`; unavailable repertoire-side and move-preview slots are omitted, not synthesized | Stage 3 row/state tests and Stage 4 visual review |
| Segmented RadioGroup | Required one-of-many selection with All colours, White, and Black meanings; the checked choice cannot be toggled empty | Use the approved segmented appearance for the three short labels | Stage 1/3 focused tests and Stage 4 narrow review |
| Commitment interaction | Specific and All are explicit committed values; clear returns to uncommitted; Escape only closes; focusing a commitment selects its displayed text; typing replaces it and clears commitment | Use a domain sentinel for All while keeping API values unchanged | Stage 3 focused interaction tests and Stage 4 browser scenario |
| Catalogue and result placement | Local filtering, stable-key identity, real retrieval, and existing in-place loading/empty/stale/error/results behavior | Use a complete local snapshot and a conservative stale-refresh state; do not add a session workflow | Stages 2-4 focused proof |
| Responsive evidence | Approved narrow treatment retains ECO, name, and selection indication; control popup remains anchored rather than becoming a sheet | Use the approved 412px candidate and 1280px desktop/collision evidence; the upstream 560px control rule is not silently changed | Stage 4 visual acceptance before cleanup |

## Settled integration contracts

### Opening selection state

Use a discriminated domain state rather than relying on an empty string to represent two meanings:

- **Uncommitted:** `selection = null`. The user may type a query; no opening is committed, the ECO badge is hidden, and **Find training positions** is disabled. Clearing a field returns here.
- **Specific:** `selection = { kind: "specific", key: <stable opening key> }`. The current catalogue row supplies the displayed ECO and name. Submission sends that exact key and `opening_match=reached`.
- **All:** `selection = { kind: "all" }`. The combobox displays **All openings**. Submission omits both `opening_key` and `opening_match`, while retaining Learner colour, as-of date, `training_requirement_lt=0`, and pagination.

The combobox may use a private synthetic option value for All, but that sentinel must never cross the training-requirements API boundary. The committed specific identity is the stable key, not the current object reference. Replacing a snapshot re-resolves the display by key. If a refreshed snapshot no longer contains a committed key, show a safe missing/uncommitted state and disable retrieval; never silently convert it to All.

`trainerColor` retains the existing `"" | "white" | "black"` UI values. The RadioGroup labels are **All colours**, **White**, and **Black**; the request adapter maps the empty UI value to omitted `trainer_color`.

### Complete catalogue snapshot and invalidation

Use the smallest assessed contract:

1. Successful `GET /api/openings` responses carry `X-Openings-Catalogue-Version`.
2. The opaque header value is derived from the existing backend database signature for the resolved database and SQLite sidecars (main file, `-wal`, `-shm`, and journal metadata). Reuse that invalidation basis rather than hashing the full real database on every request or adding a version endpoint.
3. `backend/app/main.py` exposes the response header through CORS. The header is attached only to successful opening-catalogue reads.
4. The frontend reads the header from the generated SDK result's `response.headers`. No OpenAPI body/schema or generated SDK churn is expected. The checked-in generated contract remains unchanged unless this header cannot be consumed reliably; that is an escalation, not an invitation to add a second endpoint.
5. Store only a validated envelope under an application-owned key such as `cmt.openings.catalogue.v1`:

   ```json
   {
     "storage_schema": 1,
     "catalogue_version": "opaque-backend-version",
     "items": [
       {
         "key": "B10:Caro-Kann Defense",
         "eco": "B10",
         "name": "Caro-Kann Defense",
         "route_count": 2,
         "games_reached": 12,
         "games_deepest": 9
       }
     ]
   }
   ```

   Validate the envelope, item field types, finite integer counts, stable-key uniqueness, and complete snapshot shape before use. Treat malformed, unavailable, or quota-failed storage as a cache miss without clearing unrelated storage.
6. On Trainer Practice load or explicit retry, read a valid stored snapshot for immediate display, then probe page 1 with the complete request (`page=1`, `page_size=100`, `sort=name_asc`, no search). If the response version matches, use the stored complete items and do not fetch later pages. If it is missing or different, fetch all pages using the existing bounded concurrency/abort rules, verify the version remains consistent, and persist only the successful complete replacement.
7. Local filtering matches case-insensitive trimmed opening name, ECO, and stable key. Typing never sends a search request and never changes submitted training results until the primary action is submitted. A stale snapshot may remain visible while checking, but retrieval is enabled only for a confirmed ready catalogue; a failed refresh keeps the previous rows marked as stale/error and offers retry without overwriting the snapshot.

The TanStack Query key for this feature represents one complete sorted catalogue snapshot, not one search string or transport page. It remains in-memory only; localStorage is the separate browser persistence layer.

## Stages

Stages are sequential. Each stage has one bounded result and its own proof. A later stage may adjust an earlier stage's files only when required by the approved outcome; it must not broaden the scope.

1. **completed - Promote shared controls and migrate the six behavior-preserving control boundaries.**
   - **Actions:**
     1. Reuse the approved control implementations in `frontend/src/features/design-system/form-controls/`. Add only minimal forwarding/association or filtering hooks needed by consumers, without changing the approved visual language or exposing private Base UI popup parts.
     2. In `GameLoader.tsx`, replace the local UUID input presentation with `Field` and `TextInput`; preserve submit-time UUID validation, clear-on-change validation feedback, trim-only-on-submit behavior, loading/failure states, Reset, and the existing Button.
     3. In `LineLibraryFilters.tsx`, use shared `Field`/`TextInput`/`Select` for text/search/select filters. Wrap the existing binary Base UI checkbox with shared Field presentation while preserving its clickable label, disabled behavior, empty values, immediate/explicit apply mode, and callback values. Do not touch the tri-state checkbox in `LineLibraryTree.tsx`.
      4. In `TrainerPracticePanel.tsx`, migrate Learner colour to the required three-choice RadioGroup and give the native date Field-only presentation. Leave the catalogue search input/button and raw Opening select unchanged until Stage 3 replaces them directly; do not build temporary shared controls that are immediately discarded.
     5. Update only the directly affected focused tests and local CSS. Keep all feature-owned validation, disabled, callback, and empty-value meanings external to Field.
   - **Likely paths/symbols:** `frontend/src/features/design-system/form-controls/{Field,TextInput,Select,RadioGroup}.tsx`, `private/DropdownParts.tsx`, and `FormControls.module.css` only if a small consumer API adjustment is required; `frontend/src/features/game/GameLoader.tsx`, `GameLoader.module.css`, `GameLoader.test.tsx`; `frontend/src/features/design-system/line-library/LineLibraryFilters.tsx`, `LineLibrary.module.css`, `LineLibrary.test.tsx`; `frontend/src/features/trainer-practice/TrainerPracticePanel.tsx` and its focused test.
   - **Focused proof:** From repository root `G:\ChessMoveTrainer`, command timeout 120 seconds, recommended Bash tool timeout `150000` ms:
     ```text
     timeout 120s npm --workspace frontend test -- --run src/features/design-system/form-controls/ReusableFormControls.test.tsx src/features/game/GameLoader.test.tsx src/features/design-system/line-library/LineLibrary.test.tsx src/features/trainer-practice/TrainerPracticePanel.test.tsx
     ```
   - **Breakpoint:** None. Escalate rather than redesigning a shared control if preserving one of the existing callback, validation, disabled, or empty-value contracts requires a new product behavior.

2. **completed - Add the opaque backend version and browser snapshot boundary.**
   - **Actions:**
     1. Add a public, bounded version helper alongside the existing cache signature logic, and attach `X-Openings-Catalogue-Version` to successful `/api/openings` responses in `backend/app/features/openings/router.py`.
     2. Configure CORS response-header exposure in `backend/app/main.py`. Preserve the existing JSON body and pagination contract.
     3. Extend the Trainer opening API adapter in `trainerPracticeApi.ts` to return catalogue items plus the version read from the generated response. Keep typed catalogue failures and abort errors distinct from successful data.
     4. Add a small storage module inside `frontend/src/features/trainer-practice/` for the exact envelope above, runtime validation, namespaced read/write, and safe cache-miss behavior. Do not add a persistence dependency or general storage framework.
     5. Add a complete-snapshot query key in `frontend/src/api/queryKeys.ts` and a query/data adapter that probes page 1, reuses a matching stored snapshot, fetches all pages only for a miss/stale version, verifies a consistent version, and writes only a complete successful replacement. Keep the existing four-request concurrency cap and abort behavior where applicable.
     6. Do not edit `frontend/src/api/generated/openapi.json` or generated files for a header-only contract. If the generated SDK response cannot expose the header through the existing `RequestResult.response`, stop and escalate before changing the contract shape.
   - **Likely paths/symbols:** `backend/app/caching.py` (`_current_signature` vicinity and a public opaque-version helper), `backend/app/features/openings/router.py` (`get_openings`), `backend/app/main.py`; `backend/tests/features/openings/test_catalogue_api.py`, `backend/tests/features/api_cache/test_openings_cache.py`, with a small focused storage test beside the new frontend helper; `frontend/src/features/trainer-practice/trainerPracticeApi.ts`, `trainerPracticeApi.test.ts`, and new bounded storage/query helper files; `frontend/src/api/queryKeys.ts` and `queryKeys.test.ts`.
   - **Focused proof:** From repository root `G:\ChessMoveTrainer`, command timeout 90 seconds, recommended Bash tool timeout `120000` ms:
     ```text
     timeout 90s .venv/Scripts/python.exe -m pytest backend/tests/features/openings/test_catalogue_api.py backend/tests/features/api_cache/test_openings_cache.py
     ```
     From repository root, command timeout 120 seconds, recommended Bash tool timeout `150000` ms:
     ```text
     timeout 120s npm --workspace frontend test -- --run src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/openingCatalogueStorage.test.ts src/api/queryKeys.test.ts
     ```
   - **Breakpoint:** None if the header is readable cross-origin and the existing file signature is sufficient. Escalate if a response-body version/new endpoint, a semantic manifest version, a dependency, or destructive storage migration is required.

3. **completed - Build and integrate the Trainer opening-search composition.**
   - **Actions:**
     1. Add the smallest opening-specific composition inside `frontend/src/features/trainer-practice/` (small helper/component filenames may be chosen within that directory). Compose the approved Combobox, Field, TextInput slots, dropdown option anatomy, existing Button, and production tokens; do not reimplement popup behavior.
     2. Adapt rows to current production data: ECO leading content, name as primary content, and `route_count` as the existing line-count analogue where useful. Do not synthesize repertoire side, move preview, chain, or preferred-move information.
     3. Include an explicit synthetic All openings option, map it only at the Trainer state boundary, and implement stable-key selection, current-label/ECO display, clear behavior, Escape behavior, focus-to-select, and type-to-replace behavior.
     4. Replace the intermediate catalogue search input, search button, and raw Opening select in `TrainerPracticePanel.tsx`. Keep the approved **Find training positions** action separate from the combobox.
      5. Retain the Stage 1 segmented Learner colour RadioGroup with its All colours/White/Black values and keep the as-of input native and Field-only.
     6. Refactor `TrainerPracticePage.tsx` and `trainerPracticeApi.ts` so editable selection/query/filter state remains separate from submitted filters. Preserve query-key normalization, exact request construction, full training-result pagination, aborting, retry, date validation, stale-date mapping, loading, empty, error, and in-place results. Do not send repertoire side.
     7. Update `TrainerPracticePanel.test.tsx`, `trainerPracticeApi.test.ts`, `frontend/src/App.test.tsx`, and any new focused composition tests for the complete state/request boundary. Keep `ReusableFormControls.test.tsx` as the generic production test suite.
   - **Likely paths/symbols:** `frontend/src/features/trainer-practice/TrainerPracticePanel.tsx`, `TrainerPracticePage.tsx`, `trainerPracticeApi.ts`, their focused tests, and bounded new opening presentation/composition files; `frontend/src/features/trainer-practice/TrainerPracticePanel.module.css` only if application composition needs feature-owned layout; `frontend/src/App.test.tsx`; `frontend/src/api/queryKeys.ts` if the complete-catalogue key is consumed there.
   - **Focused proof:** From repository root, command timeout 150 seconds, recommended Bash tool timeout `180000` ms:
     ```text
     timeout 150s npm --workspace frontend test -- --run src/features/design-system/form-controls/ReusableFormControls.test.tsx src/features/trainer-practice/TrainerPracticePanel.test.tsx src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/openingCatalogueStorage.test.ts src/api/queryKeys.test.ts src/App.test.tsx
     ```
   - **Breakpoint:** Stop for a product/API decision if All cannot remain an explicit UI commitment while omitting the opening API filters, if repertoire side must enter the request, if a missing field requires a new data model, or if changing existing result-state meaning is proposed. A removed stable key must follow the safe missing/uncommitted rule above, not silently become All.

4. **completed - Prove integrated behavior and visual fidelity before cleanup.**
   - **Actions:**
     1. Update `tests/e2e/trainer-practice.spec.ts` to navigate through the shell and prove a specific stable-key request, `opening_match=reached`, optional Learner colour, as-of date, fixed training filters, and complete in-place results.
     2. Add focused browser assertions that typing after the initial catalogue load makes no per-keystroke catalogue request; All is selectable and sends no opening key; clear disables retrieval and does not select All; committed focus selects text; typing replaces commitment; radio values remain independent; and loading/empty/stale/error/results remain in place.
     3. Before any browser or lifecycle work, from repository root run the shared-service status check and reuse healthy services. Do not start competing servers.
     4. Run the approved Storybook interaction/a11y proof while `ReusableFormControls.stories.tsx` still exists. Review the integrated application at the required 1280px desktop/collision and 412px narrow breakpoints. Confirm ECO/name/selection retention and the approved anchored popup treatment without importing mock-up chrome.
   - **Likely paths/symbols:** `tests/e2e/trainer-practice.spec.ts`, directly affected focused frontend tests, and no Storybook redesign. Any visual correction must remain within the approved production control/application integration areas.
   - **Focused proof:**
     - From repository root, command timeout 30 seconds, recommended Bash tool timeout `60000` ms:
       ```text
       timeout 30s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status
       ```
     - From repository root, command timeout 180 seconds, recommended Bash tool timeout `210000` ms:
       ```text
       timeout 180s npm --workspace frontend run test-storybook -- --run src/features/design-system/form-controls/ReusableFormControls.stories.tsx
       ```
     - From repository root, command timeout 120 seconds, recommended Bash tool timeout `150000` ms:
       ```text
       timeout 120s npm exec playwright test --config=tests/e2e/playwright.config.ts tests/e2e/trainer-practice.spec.ts
       ```
   - **Breakpoint:** Human/visual acceptance is required at 1280px and 412px before Stage 5. The approved Storybook candidate remains the comparison reference; do not resolve a mismatch by importing excluded HTML page chrome or fixture-only metadata.

5. **completed - Remove temporary exploratory Storybook material after acceptance.**
   - **Actions:**
     1. Only after Stage 4 behavioral proof and the 1280px/412px visual acceptance pass, delete `frontend/src/features/design-system/form-controls/ReusableFormControls.stories.tsx`.
     2. Retain `Field.tsx`, `TextInput.tsx`, `Select.tsx`, `Combobox.tsx`, `Autocomplete.tsx`, `RadioGroup.tsx`, `DropdownOptionContent.tsx`, private dropdown foundations, `FormControls.module.css`, and appropriate production component tests.
     3. Directly verify that the deleted file and the temporary Storybook title `In Development/Design System/Exploration/Reusable Form Controls` are absent, while retained production components/tests remain. Do not rerun the intentionally deleted story's test after this stage.
   - **Likely paths/symbols:** Delete only `frontend/src/features/design-system/form-controls/ReusableFormControls.stories.tsx`; verify the retained files in the same directory and the final Storybook catalog has no temporary entry.
   - **Focused proof:** From repository root, command timeout 30 seconds, recommended Bash tool timeout `60000` ms:
     ```text
     timeout 30s powershell -NoProfile -Command "if (Test-Path 'frontend/src/features/design-system/form-controls/ReusableFormControls.stories.tsx') { exit 1 }; if (Get-ChildItem 'frontend/src' -Recurse -File | Select-String -SimpleMatch 'In Development/Design System/Exploration/Reusable Form Controls') { exit 1 }; if (!(Test-Path 'frontend/src/features/design-system/form-controls/ReusableFormControls.test.tsx')) { exit 1 }"
     ```
     Run the retained focused component/application tests from Stage 3 only if Stage 5 changes could affect them; do not require the deleted Storybook file's test.
   - **Breakpoint:** This is mandatory final acceptance, not optional maintenance. Do not delete the story earlier, and escalate if cleanup would remove production components or tests rather than only the temporary exploration artifact.

## Progress and decisions

- **Stage 1:** completed - shared-control adoption and six behavior-preserving migration boundaries accepted with existing values, validation, callbacks, labels, disabled behavior, native date picker, checkbox label click, and retrieval behavior preserved. The Trainer catalogue search/raw Opening select and tri-state tree checkbox remained untouched. Proof on 2026-09-15 from repository root: `timeout 120s npm --workspace frontend test -- --run src/features/design-system/form-controls/ReusableFormControls.test.tsx src/features/game/GameLoader.test.tsx src/features/design-system/line-library/LineLibrary.test.tsx src/features/trainer-practice/TrainerPracticePanel.test.tsx` passed 47 tests in 4 files with Bash tool timeout `150000` ms.
- **Stage 2:** completed - the opaque catalogue response header, CORS exposure, generated-response header read, validated namespaced localStorage envelope, complete version-probed snapshot helper, and complete-catalogue query key were accepted without generated API or application-integration changes. Backend proof on 2026-09-15 from repository root: `timeout 90s .venv/Scripts/python.exe -m pytest backend/tests/features/openings/test_catalogue_api.py backend/tests/features/api_cache/test_openings_cache.py` passed 31 tests with Bash tool timeout `120000` ms. Frontend proof from repository root: `timeout 120s npm --workspace frontend test -- --run src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/openingCatalogueStorage.test.ts src/api/queryKeys.test.ts` passed 28 tests with Bash tool timeout `150000` ms.
- **Stage 3:** completed - the approved opening combobox, explicit All/uncommitted/specific selection state, stable-key/ECO/name local filtering, Learner colour, complete catalogue reuse, and real Trainer request/results integration are accepted. A minimal shared `onInputClick` forwarding hook preserves select-all/type-to-replace when a committed input is already focused; no popup behavior or product meaning changed. Proof on 2026-09-15 from repository root: `timeout 150s npm --workspace frontend test -- --run src/features/design-system/form-controls/ReusableFormControls.test.tsx src/features/trainer-practice/TrainerPracticePanel.test.tsx src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/openingCatalogueStorage.test.ts src/api/queryKeys.test.ts src/App.test.tsx` passed 59 tests in 6 files with Bash tool timeout `180000` ms.
- **Stage 4:** completed - focused browser behavior and visual fidelity are accepted. Proof on 2026-09-15 from repository root: `timeout 30s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status` confirmed healthy backend, frontend, and Storybook services with Bash tool timeout `60000` ms; `timeout 180s npm --workspace frontend run test-storybook -- --run src/features/design-system/form-controls/ReusableFormControls.stories.tsx` passed 7 tests with Bash tool timeout `210000` ms; `timeout 120s npm exec playwright test --config=tests/e2e/playwright.config.ts tests/e2e/trainer-practice.spec.ts` passed 7 tests with Bash tool timeout `150000` ms. Representative 1280px and 412px screenshots retain ECO/name/route-count option content, selection indication, the anchored internally scrolling popup, segmented colour control, native date, shell, action, and in-place results without horizontal overflow. The user explicitly accepted the visual result on 2026-09-15.
- **Stage 5:** completed - after visual acceptance, the temporary `ReusableFormControls.stories.tsx` exploration story was deleted while all production form-control components, private foundations, styles, and `ReusableFormControls.test.tsx` were retained. Proof on 2026-09-15 from repository root: `timeout 30s powershell -NoProfile -Command "if (Test-Path 'frontend/src/features/design-system/form-controls/ReusableFormControls.stories.tsx') { exit 1 }; if (Get-ChildItem 'frontend/src' -Recurse -File | Select-String -SimpleMatch 'In Development/Design System/Exploration/Reusable Form Controls') { exit 1 }; if (!(Test-Path 'frontend/src/features/design-system/form-controls/ReusableFormControls.test.tsx')) { exit 1 }"` passed with Bash tool timeout `60000` ms. No production proof was invalidated by deleting the isolated story.
- **Decision:** The browser version is an opaque header derived from the existing database signature. A response-body version or new endpoint is not part of this Plan unless the header cannot be exposed/read reliably.
- **Decision:** The persisted cache is one validated complete snapshot under one namespaced localStorage key. It is not general query persistence and does not issue search requests per keystroke.
- **Decision:** Existing generated API files remain unchanged for the header-only contract. Regeneration or generated-schema changes require escalation.
- **Decision:** The approved Storybook story is upstream evidence during integration and is deleted only after Stage 4 acceptance.

## Proof

- Use only the finite stage commands listed above. Do not add lint, formatting, broad type/build, source-size, aggregate, complete-suite, CI, or repository-hygiene checks to this Plan.
- A passing behavioral proof remains valid until a later stage changes its command, inputs, exercised behavior, configuration, dependencies, or environment. Rerun only proof invalidated by the later change.
- Stage 1's intermediate Trainer control proof is expected to be invalidated by Stage 3's replacement composition; rerun the final Trainer proof then. Backend/cache proof remains valid unless the version or opening request boundary changes.
- Stage 4 Storybook proof is intentionally invalidated by deleting the story in Stage 5. Do not require a test for an intentionally removed file; prove the retained production component tests and final application behavior instead.

## Escalation boundaries

- The response-header contract cannot be read reliably through CORS or the existing generated SDK response, or a response-body version/new endpoint becomes necessary.
- The existing database-file/SQLite-sidecar signature is insufficient to detect the active catalogue change, or a semantic manifest/version source is required.
- A new npm/Python dependency, general persistence framework, or generated-client regeneration is required.
- A missing production field would require chain, repertoire, preferred-move, SAN-preview, move-replay, or another new data model.
- The approved public behavior or visual direction changes, including changing All/uncommitted meaning, making openings colour-specific, adding repertoire side to the request, changing retrieval into a playable session, or changing existing result/scoring semantics.
- Clearing or migrating browser storage beyond the single application-owned invalid snapshot entry is proposed.
- Work leaves the named Trainer Practice, Game Loader, Line Library Filters, opening backend/version, focused-test, visual-proof, or final-cleanup areas.

## Visible result

> The Trainer Practice page visibly uses the approved controls, finds real training positions from a specific opening or explicit All openings choice, and no temporary reusable-control exploration story remains after final acceptance.
