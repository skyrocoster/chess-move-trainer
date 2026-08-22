# MP-08 Complete-Game Traversal - load and traverse one validated stored game in the existing read-only viewer

> **Status:** done - all three stages shipped, independently validated, and human-accepted on 2026-08-19

- **Read trigger:** Read after the confirmed MP-08 grilling synthesis and before dispatching any MP-08 stage; re-read the applicable stage before each sequential dispatch.
- **Upstream:** [MP-08 grilling synthesis](../../../grilling-docs/mp08-complete-game-traversal.md), [static-position to analysis master plan](../../../master-plans/static-position-to-analysis.md), and accepted [MP-07 Plan](../../done/mp07-arbitrary-stored-fen-display/mp07-arbitrary-stored-fen-display.md). The MP-07 grilling file referenced by that archived Plan is absent and is not reconstructed.

## Outcome

MP-08 lets a human load a complete accepted stored game by Game UUID and optional Ply, then traverse the eagerly loaded ordered positions in memory one ply at a time through the existing safe read-only board. The viewer provides the confirmed Game Loader, Board Control, and Game Context components, preserves the prior game during replacement-load failures, remains session-only at `/viewer`, and exposes the required accessible loading, failure, reset, source-safety, responsive, and boundary states.

## Scope

- **Included:**
  - New read-only `GET /api/games/{game_uuid}/positions?ply={optional}` with the exact strict success envelope `{game_uuid, initial_ply, subject_color, source_url, positions}` and ordered `{ply, fen, san}` position objects, including `san: null` at ply zero.
  - Omitted Ply meaning zero; explicit out-of-range Ply mapped to Position not found; complete-game rejection for missing, gapped, malformed, invalid, or incorrectly owned stored data; safe source URL normalization to a validated HTTPS Chess.com live/daily URL or `null`.
  - Preservation and regression proof of the existing `/api/games/{game_uuid}/positions/{ply}` endpoint, while removing `/viewer` dependence on it.
  - Frontend Game Loader, Board Control, and Game Context components using the app-owned Disclosure/Base UI Collapsible boundary, existing Base UI-backed Button, Material tokens, CSS Modules, the workspace container-query convention, and the existing board adapter.
  - In-memory one-ply Previous/Next traversal; disabled initial/final controls; session-only state; loading cancellation; prior-context preservation; reset; polite Ply/SAN announcements; accessible typed error states; safe new-tab source links; empty, loading, success, replacement-load, failure, and boundary behavior.
  - Independent Storybook registration and interaction coverage for every new or reworked component, with representative wide/constrained, empty, loading, success, initial/final boundary, typed failure, reset, and replacement-load stories.
- **Expected areas:**
  - `docs/grilling-docs/mp08-complete-game-traversal.md`
  - `docs/master-plans/static-position-to-analysis.md` (bounded current-state/status/provenance/sequencing truth only)
  - `backend/app/features/positions/*`
  - `backend/tests/features/positions/*`
  - `frontend/src/features/viewer/*`
  - `tests/e2e/*` for the MP-08 viewer and full-corpus proof, with the existing single-position endpoint still covered
- **Excluded:**
  - Any change to the existing single-position endpoint contract, `/` status page, shell, board-adapter safety/read-only boundary, or unrelated design-system behavior.
  - Database writes, corpus extraction, schema migration, live-corpus modification, repair, initialization, or portable replacement of the accepted local corpus.
  - URL/query-string viewer state, browsing, search, metadata expansion, move lists, first/last controls, repeat behavior, swipe, arrows, drawing, board editing, engine analysis, persistence, or user-created positions.
  - New dependencies, package changes, unrelated refactors, historical Plan/grilling reconstruction, commits, pushes, and acceptance by automation alone.

## Stages

1. **done - modular mocked frontend components and independent Storybook design gate (ORDERED).**
   - **Ordered actions:** Rework the viewer composition around Game Loader, Board Control, and Game Context without making backend calls. Define deterministic mocked complete-game data covering ply zero, an intermediate SAN position, the final ply, both subject orientations, safe/unsafe/missing source attribution, and replacement-load behavior. Implement the confirmed wide and constrained arrangements, independent initially-open disclosures, empty state, loading state, all five accessible error headings, retry/reset/cancellation states, disabled boundaries, polite announcements, and native button behavior. Add component tests and independent Storybook stories/interaction tests for every new or reworked component plus representative composed viewer states.
   - **Focused proof:** `npm.cmd run test --prefix frontend -- --run src/features/viewer`; `npm.cmd run build-storybook --prefix frontend`; `npm.cmd run test-storybook --prefix frontend` with the Storybook server available.
   - **Breakpoint:** completed - human visual review and acceptance of the mocked Storybook design at wide and constrained sizes was given with “Okay, let's go.” The constrained-layout repair and authoritative user edits were incorporated before Stage 2.
2. **done - whole-game backend endpoint and temporary-database proof (ORDERED).**
   - **Ordered actions:** Extend the positions feature behind its application-owned repository/router/schema boundary with the approved whole-game route and strict response models. Eagerly query all ordered occurrences and source data, validate full-game completeness and every stored position before returning any response, sanitize source attribution, honor optional Ply, and preserve the existing single-position route and response unchanged. Extend only temporary test fixtures as needed to represent SAN, source URL, missing/gapped occurrences, malformed fields, out-of-range requests, missing games, ownership failures, and corpus failures. Add regression tests for the unchanged MP-07 route and read-only/no-live-corpus mutation behavior.
   - **Focused proof:** `.venv\Scripts\python.exe -m pytest backend/tests/features/positions -q`; inspect that temporary fixture bytes are unchanged after requests and that the live corpus is not modified.
   - **Escalation boundary:** Do not invent a different route, response field, error distinction, validation rule, source allowlist, or database ownership model. Escalate if the approved envelope cannot represent a required failure or if existing endpoint behavior would need to change.
3. **done - live frontend integration, full-corpus browser proof, and final human gate (ORDERED).**
   - **Ordered actions:** Replace the viewer's single-position client call with the whole-game client while preserving the accepted Stage 1 design. Validate the exact response envelope and reject extras, load the requested initial pointer, keep the complete game in memory, prevent traversal requests, preserve prior context through replacement failures, cancel/ignore stale loads on reset, and map backend/network failures to the five accessible states. Add component tests for retry, cancellation, focus/announcement behavior, no URL mutation, one-ply controls, final/initial disabling, source safety, and prior-context recovery. Update/add the viewer E2E coverage using the full local corpus fixture `0007925c-5a8d-11f0-9740-f690a301000f`, subject Black, final ply 82, and its Chess.com live URL; retain direct regression proof for the unchanged MP-07 endpoint.
   - **Focused proof:** `npm.cmd run test --prefix frontend -- --run`; `node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts`; `.venv\Scripts\python.exe scripts\check.py` in read-only mode.
    - **Breakpoint:** completed - live wide/constrained browser review, keyboard/pointer/tap operation, focus retention, polite announcements, loading and failure recovery, source-link safety, reset, and initial/final boundaries were accepted by the user.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing this outcome or introducing a new decision.

## Progress and decisions

- **Documentation prerequisite:** done - confirmed grilling synthesis recorded first and the master plan corrected only for MP-07 accepted / MP-08 selected current-state truth.
- **Stage 1:** done - mocked components, independent stories, composed states, and focused tests shipped. The constrained-layout repair, focused tests, Storybook build, lint, type/build, formatting proof, and wide/constrained measurements were re-verified. The user explicitly accepted the visual breakpoint with “Okay, let's go.” Existing unmodified MP-07 `ViewerWorkspace.stories.tsx` runner failures remain unrelated/flaky and were not repaired or absorbed.
- **Stage 2:** done and independently validated/accepted - the strict whole-game read-only endpoint and temporary SQLite coverage passed 32 focused tests, with unchanged MP-07 behavior, typed failures, source safety, health isolation, and read-only bytes. Ruff/format/size proof passed; the representative live corpus returned 83 positions through final ply 82 without mutation. No Stage 2 breakpoint or escalation was reached.
- **Stage 3:** done - production `/viewer` uses the whole-game client and keeps traversal in memory with typed failures, replacement preservation, cancellation/reset, source safety, announcements, boundaries, and responsive composition. Independent final Quality validation was **PASS** with issue none. After reviewing the live viewer, the user explicitly accepted with “all good” on 2026-08-19.

## Proof

- `.venv\Scripts\python.exe -m pytest backend/tests/features/positions -q` - 32 whole-game and unchanged single-position API tests passed, including temporary corpus fixtures.
- `npm.cmd run test --prefix frontend -- --run src/features/viewer` - focused component, interaction, accessibility, state, and mocked-client proof during Stage 1.
- `npm.cmd run build-storybook --prefix frontend` - registered stories build successfully.
- `npm.cmd run test-storybook --prefix frontend` - registered Storybook interaction coverage; the Stage 1 Game Loader, Board Control, Game Context, and Mocked Game Viewer stories passed, and the reworked MP-08 `ViewerWorkspace.stories.tsx` runner passed with all 18 suites/94 tests.
- `npm.cmd run test --prefix frontend -- --run` - full frontend regression proof.
- `node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts` - wide/constrained viewer, Storybook, unchanged endpoint regression, and full-corpus live proof.
- Documentation phase: manually review Markdown links, Plan-template structure, and master-plan current-state truth, then run `git diff --check` for the three documentation paths.
- `.venv\Scripts\python.exe scripts\check.py` - final read-only repository closeout; never use `--fix` without explicit authorization.
- **Final closeout evidence (2026-08-19):** backend focused 32 passed; frontend 25 files/148 passed; Storybook 18 suites/94 passed and build passed (documented non-fatal teardown assertion only); Playwright 34 passed; Ruff, ESLint, Prettier, frontend build, source/test size, `git diff --check`, and full read-only `scripts\check.py` passed. The representative game `0007925c-5a8d-11f0-9740-f690a301000f` traversed 83 positions through final ply 82 with no per-ply network calls; live wide/constrained, focus/keyboard, announcements, replacement failures, reset, source safety, boundaries, Storybook registration, and `/` regression passed. The live database SHA-256 was unchanged.

The representative live fixture is the existing local corpus only; no generated or temporary database replaces it for browser proof. Temporary databases are limited to isolated backend tests and are never written to the live corpus.

## Escalation boundaries

- Any change to the approved endpoint path, exact success envelope, strict-extra behavior, optional-Ply semantics, error distinction, or existing MP-07 endpoint contract.
- Any change to the definition of a complete/valid stored game, source URL safety allowlist, subject ownership, or read-only database boundary.
- Any new product behavior, visual direction, component ownership, dependency, data/schema operation, destructive action, or acceptance gate outside this Plan.
- Any request to modify the live corpus, replace the accepted full-corpus fixture, weaken board safety/read-only behavior, or waive the Stage 1 visual or Stage 3 human acceptance gates.

## Visible result

> At `/viewer`, a human can load the confirmed live game and walk from ply 0 to ply 82 with Previous/Next while the board, SAN context, boundaries, errors, reset, and source attribution behave as specified.
