# Trainer Practice retrieval panel - select filters and display every matching position

> **Status:** done - all four stages and their focused behavioral proof are accepted.

- **Read trigger:** Read before implementing or proving the `/trainer` Trainer Practice retrieval page.
- **Upstream:** `docs/grilling-docs/trainer-practice-retrieval-contract.md` is the governing behavioral contract. No signed-off visual evidence exists; this Plan intentionally has no Design fidelity section.

## Outcome

Add a deliberately thin, utilitarian top-level `/trainer` page labelled **Trainer Practice**. A user can select an exact opening from the existing catalogue, optionally select learner colour, choose `as_of`, and submit a training-required retrieval. The page uses the existing `GET /api/positions/training-requirements` operation, follows its pagination, and minimally displays the stable response envelope and position items as functional scaffolding for a later designed frontend.

## Scope

- **Included:**
  - A representative real-database regression proving that base `B10:Caro-Kann Defense` with `opening_match=reached` includes a position from a deeper Caro-Kann variation.
  - Refreshing the checked-in frontend OpenAPI document and generated client surface for the already-existing training-requirements GET operation, then exposing it through `frontend/src/api/client.ts`.
  - A bounded `frontend/src/features/trainer-practice/` feature with native/functional controls for catalogue opening selection, trainer colour, and `as_of`.
  - Fixed `training_requirement_lt=0` and fixed `opening_match=reached` whenever an opening is selected.
  - Exact catalogue `key` values in requests; no display-text or hierarchy inference.
  - Initial `page=1&page_size=100` retrieval and sequential page accumulation in API order until `total` is loaded, without duplicates.
  - Safe loading, catalogue error, retrieval error, stale-date, and valid-empty states.
  - Minimal display of `as_of`, scoring policy, pagination/total metadata, and the stable position item fields.
  - `/trainer` registration, a “Trainer Practice” navigation entry, focused route/navigation tests, and one bounded browser scenario when shared services are healthy.
- **Expected areas:**
  - `backend/tests/features/position_training_requirements/test_real_database.py`
  - `frontend/src/api/generated/openapi.json`
  - generated files under `frontend/src/api/generated/`
  - `frontend/src/api/client.ts`
  - `frontend/src/api/generatedSurface.test.ts`
  - new files under `frontend/src/features/trainer-practice/`
  - `frontend/src/App.tsx` and its focused tests
  - `frontend/src/features/app-shell/AppShell.tsx` and its focused tests
  - `tests/e2e/trainer-practice.spec.ts` only for the approved bounded browser scenario
- **Excluded:** Polished visual design, Storybook, design exploration, `DESIGN.md`, visual fidelity proof, board handoff, position selection, trainer-session endpoint/state, randomization, scheduling or due-date changes, scoring changes, opening hierarchy inference, hardcoded Caro keys, arbitrary multi-opening collections, migrations, new backend endpoints, dependency changes, unrelated cleanup, and any branch/worktree/stash/commit/push operation.

## Stages

1. **complete - Prove representative Caro reached-opening semantics.**
   - **Ordered actions:** Extend the opt-in real-database proof with one narrowly named Caro-Kann case. Use the exact catalogue key returned by the repository data, compare base `reached` behavior with the deeper-only behavior, and assert the returned response shape/item evidence needed to show that a deeper variation is included. Do not change backend production code unless this proof contradicts the observed repository data.
   - **Focused proof:**
     ```text
     timeout 60s env CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE=1 .venv/Scripts/python.exe -m pytest backend/tests/features/position_training_requirements/test_real_database.py -k caro
     ```
     Working directory: `G:\ChessMoveTrainer`  
     Bash tool timeout: `120000` ms.
   - **Escalation boundary:** Stop before changing backend behavior or the settled contract if the repository data does not record the base Caro-Kann route for deeper variation games.
   - **Breakpoint:** None expected; this is behavioral proof, not a visual breakpoint.

2. **complete - Refresh and expose the generated API operation.**
   - **Ordered actions:** Bring the checked-in OpenAPI document in line with the served FastAPI contract, run the configured generator, update the handwritten API re-exports, and update the generated-surface expectations for the training-requirements operation and schemas/errors. Preserve all existing generated operations and the unrelated worktree changes.
   - **Focused proof:**
     ```text
     timeout 60s npm --prefix frontend run test -- --run src/api/generatedSurface.test.ts
     ```
     Working directory: `G:\ChessMoveTrainer`  
     Bash tool timeout: `120000` ms.
   - **Escalation boundary:** Do not hand-invent a request/response contract, add a new endpoint, or alter unrelated generated operations. Stop if the served backend schema conflicts with the upstream document.
   - **Breakpoint:** None expected.

3. **complete - Implement retrieval construction, pagination, states, and minimal results.**
   - **Ordered actions:** Add the trainer-practice API boundary and page/panel. Load opening choices from the existing catalogue operation and use each returned `key` as the select value, with an all-openings option that omits opening parameters. Construct only the settled query fields: valid `as_of`, `training_requirement_lt=0`, optional `trainer_color`, optional `opening_key` plus `opening_match=reached`, `page`, and `page_size=100`. Submit explicitly rather than refetching on every control change; append later pages in response order until the reported `total` is loaded. Protect against stale/aborted requests and map network, typed HTTP, stale-date, and empty outcomes to safe visible states. Render the envelope and item fields without importing board or session code.
   - **Focused proof:**
     ```text
     timeout 60s npm --prefix frontend run test -- --run src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/TrainerPracticePanel.test.tsx
     ```
     Working directory: `G:\ChessMoveTrainer`  
     Bash tool timeout: `120000` ms.
   - **Escalation boundary:** Do not add hierarchy or a hardcoded `B10:Caro-Kann Defense` default, expose arbitrary scoring/scheduling controls, change pagination semantics, or introduce board/session behavior.
   - **Breakpoint:** None expected; no visual design decision is authorized.

4. **complete - Integrate route/navigation and prove the request/result flow.**
   - **Ordered actions:** Register the lazy-loaded `/trainer` route and “Trainer Practice” navigation item using existing app-shell conventions. Add focused route/navigation assertions. Before browser proof, inspect shared service health only; if services are not healthy, do not restart or stop them in this stage. When healthy, exercise one live scenario that selects the exact Caro-Kann catalogue entry, selects a colour, submits, verifies the query, and verifies the returned list without board/session UI.
   - **Focused proof:**
     ```text
     timeout 60s npm --prefix frontend run test -- --run src/App.test.tsx src/features/app-shell/AppShell.test.tsx
     ```
     Working directory: `G:\ChessMoveTrainer`  
     Bash tool timeout: `120000` ms.

     Before the browser scenario:

     ```text
     timeout 30s powershell -ExecutionPolicy Bypass -File .\dev.ps1 status
     ```
     Working directory: `G:\ChessMoveTrainer`  
     Bash tool timeout: `60000` ms.

     If the required shared services report healthy:

     ```text
     timeout 90s npx playwright test tests/e2e/trainer-practice.spec.ts --config tests/e2e/playwright.config.ts
     ```
     Working directory: `G:\ChessMoveTrainer`  
     Bash tool timeout: `120000` ms.
   - **Escalation boundary:** Do not choose a different product route/name, start competing host services, or perform lifecycle changes outside the repository service instructions. Report unavailable live proof rather than weakening the behavioral acceptance criteria.
   - **Breakpoint:** None expected; no human visual breakpoint is required.

Stages are sequential. A passing proof remains valid until a later stage changes its exercised behavior, inputs, configuration, dependencies, or environment.

## Progress and decisions

- **Stage 1:** complete - exact base Caro-Kann `reached` scope includes representative deeper-variation evidence; focused opt-in proof passed; breakpoint: none.
- **Stage 2:** complete - the current backend contract was exported and regenerated, the training-requirements operation was canonically re-exported, and focused generated-surface proof passed; breakpoint: none.
- **Stage 3:** complete - the feature API and utilitarian panel construct the settled query, use explicit catalogue search, retrieve all pages safely, and display loading/error/empty/success states plus returned metadata/items; focused proof passed; breakpoint: none.
- **Stage 4:** complete - `/trainer` and its shell navigation are registered, focused route/navigation proof passed, shared services were healthy, and the bounded live Caro-Kann request/result scenario passed; breakpoint: none.
- **Settled decisions retained:** base opening selection uses exact catalogue keys; selected openings use `reached`; training-required means `training_requirement_lt=0`; filters intersect; `as_of` and pagination retain the existing API contract.
- **Unresolved decisions:** none within the approved behavior. The `/trainer` route and “Trainer Practice” label are approved by this packet.

## Proof

- **Stage 1:** `timeout 60s env CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE=1 .venv/Scripts/python.exe -m pytest backend/tests/features/position_training_requirements/test_real_database.py -k caro` from `G:\ChessMoveTrainer`, Bash tool timeout `120000` ms - **1 passed, 1 deselected in 14.28s**. This proves exact `B10:Caro-Kann Defense` with `opening_match=reached` includes a representative game that continued into a deeper Caro-Kann variation.
- **Stage 2:** `timeout 60s npm --prefix frontend run test -- --run src/api/generatedSurface.test.ts` from `G:\ChessMoveTrainer`, Bash tool timeout `120000` ms - **1 file passed, 2 tests passed**. This proves the generated frontend surface includes the existing training-requirements operation and retains its expected operations.
- **Stage 3:** `timeout 60s npm --prefix frontend run test -- --run src/features/trainer-practice/trainerPracticeApi.test.ts src/features/trainer-practice/TrainerPracticePanel.test.tsx` from `G:\ChessMoveTrainer`, Bash tool timeout `120000` ms - **2 files passed, 25 tests passed**. This proves exact/omitted filter construction, explicit catalogue search, fixed training and reached-opening parameters, ordered full pagination, stale-request protection, date handling, panel states, and minimal metadata/item rendering.
- **Stage 4 route/navigation:** `timeout 60s npm --prefix frontend run test -- --run src/App.test.tsx src/features/app-shell/AppShell.test.tsx` from `G:\ChessMoveTrainer`, Bash tool timeout `120000` ms - **2 files passed, 14 tests passed**.
- **Stage 4 service status:** `timeout 30s powershell -ExecutionPolicy Bypass -File './dev.ps1' status` from `G:\ChessMoveTrainer`, Bash tool timeout `60000` ms - backend, frontend, and Storybook reported healthy immediately before browser proof.
- **Stage 4 browser:** `timeout 90s npx playwright test tests/e2e/trainer-practice.spec.ts --config tests/e2e/playwright.config.ts` from `G:\ChessMoveTrainer`, Bash tool timeout `120000` ms - **1 test passed in 58.7 seconds**. The live response returned HTTP 200 with four exact Caro-Kann/black positions; the scenario verified the settled query parameters, visible non-empty results, and absence of board/session UI.
- The stage-1 opt-in real-database test proves that base Caro-Kann reached scope includes a deeper Caro-Kann variation.
- The stage-2 generated-surface test proves the checked-in frontend contract and canonical client exports include the existing operation without losing approved operations.
- The stage-3 API and component tests prove exact query construction, omitted optional filters, fixed training/reached filters, sequential pagination accumulation, request cancellation/staleness protection, loading/error/stale/empty states, minimal item rendering, and absence of board/session handoff.
- The stage-4 route/navigation tests prove `/trainer` and the shell entry. The bounded browser scenario proves the live catalogue-to-request-to-result flow when shared services are healthy.

## Escalation boundaries

- Stop before changing the upstream API behavior, response envelope, scoring meaning, reached-opening semantics, or pagination contract.
- Stop before adding backend production behavior, a new endpoint, a migration, dependency, or arbitrary opening hierarchy.
- Stop before overriding relevant user-authored overlapping changes; preserve the existing backend training changes, board-adapter work, untracked grilling/experiment content, and all unrelated files shown by the assessment baseline.
- Stop if the served OpenAPI contract and the authoritative grilling record disagree.
- Do not substitute visual design work or a visual breakpoint for the approved functional scaffolding.

## Visible result

> A user can open **Trainer Practice**, choose an exact catalogue opening and optional colour/date filters, submit, and see every matching training-required position listed with its returned API metadata—without a chessboard or training session.
