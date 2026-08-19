# MP-07 Arbitrary Stored-FEN Display - select a stored game occurrence by game UUID plus ply and display its validated FEN on the safe read-only board

> **Status:** MP-07 Plan approved for three stages; Stage 1 SHIPPED (shipped 2026-08-19 with explicit human acceptance), Stage 2 (backend API) SHIPPED (shipped 2026-08-19 with explicit human acceptance), and Stage 3 (live frontend integration and full-corpus browser proof) SHIPPED (shipped 2026-08-19 with explicit human acceptance).

- **Read trigger:** Open after the confirmed MP-07 grilling record at `docs/grilling-docs/mp07-arbitrary-stored-fen-display.md` and before authoring or implementing the first MP-07 stage; re-read the relevant stage subsection before each dispatch. Stages 2 and 3 may be dispatched only after the user explicitly accepts the Stage 1 Storybook design.

## What we're building & why

MP-07 lets a user enter a game UUID and ply into a compact form above the board in the existing `/viewer` area, retrieve that exact stored occurrence through a ready-to-use backend API, and display its validated six-field FEN on the existing safe read-only board, oriented with the corpus subject's color at the bottom. Selection lives in React state only (never the URL); the accepted standard starting board remains visible before the first lookup and after reset. After any failed lookup the prior board is removed and one of four distinct accessible states is shown.

Because this milestone introduces the first stored-position retrieval API and the first interactive viewer experience, it must begin with the complete mocked Storybook experience and stop at a mandatory human design checkpoint: no backend API and no live frontend integration may be implemented until the user explicitly approves the edited Storybook design. The confirmed design contract is the MP-07 grilling record, which this Plan preserves.

## Stages

1. **Mocked Storybook frontend experience, ending in the blocking human design gate (ORDERED).** Build the complete viewer experience with deterministic mocked lookup behavior in Storybook: the compact lookup form above the board, client-side validation, single in-flight submission, loading that preserves the current board, both subject-color successes, the four failure states, and Reset viewer, each in wide and constrained layouts, with Storybook interaction tests for validation, submission, loading, success, failures, and reset, plus component tests. This stage ships the full mocked design for the user to inspect, edit (components, stories, layout, styling, wording) for as long as needed, and explicitly accept. **That acceptance is the blocking human design checkpoint: Stages 2 and 3 are not authorized until it happens, and the approved stories and components then bind all later MP-07 work.**
2. **Backend API `GET /api/games/{game_uuid}/positions/{ply}` (ORDERED).** Introduce the `positions` backend feature: typed Pydantic response and error schemas, a router, and a read-only service or repository that reconstructs and validates the six-field FEN from the MP-06 corpus with the backend chess library before returning success. The API is complete and tested (200, 422, 404, 503, 500) with the pinned machine-readable error codes, an environment-configurable database path defaulting to `data/database/chess_games.db`, and corpus-DB failure that degrades only position requests, never `/api/health` or backend startup.
3. **Live frontend integration and full-corpus browser proof (ORDERED).** Wire the viewer to the real endpoint through a feature-owned API client, mapping the typed error codes to the four failure states and the success payload to the approved display contract, preserving the exact Stage 1 approved design rather than reinterpreting it. Prove the live experience with an automated Playwright browser test against the full untracked local corpus database `data/database/chess_games.db` (known game UUID and ply, subject color at the bottom, and one missing occurrence).

## Mandatory human design checkpoint

Stage 1's shipment requires explicit human acceptance of the **edited** Storybook design. The user may take as much time as needed to edit components, stories, layout, styling, wording, and other visual choices; the initial form-above-board placement is a starting direction, not advance approval. No Stage 2 or Stage 3 work may begin until the user explicitly approves the resulting design. After approval, the edited stories and components become the frontend design contract: later API and integration work must preserve that approved behavior rather than reinterpret it. This gate is blocking; it cannot be waived by automation.

## Shipped

| Stage | What shipped (<=2 sentences) |
|-------|------------------------------|
| 1 | Mocked Storybook viewer experience shipped and explicitly human-accepted: the deterministic lookup form, validation, loading, success, failure, reset, wide/constrained stories, interaction tests, component tests, and shared Disclosure integration are complete. The recorded proof suite passed. |
| 2 | Backend API GET /api/games/{game_uuid}/positions/{ply} shipped and explicitly human-accepted: typed Pydantic schemas, router, read-only service/repository reconstructing and validating the six-field FEN with the pinned chess library, subject-color derivation, the pinned lowercase error codes/statuses, configurable DB path, and startup/health isolation are complete. The recorded proof suite passed. |
| 3 | Live frontend integration shipped and explicitly human-accepted: the feature-owned API client, viewer wiring preserving the accepted design, the fixed typed-code-to-failure-state mapping, mocked-fetch component tests, and the full-corpus live browser spec (known game UUID and ply with the corpus subject's color at the bottom, plus one missing occurrence) are complete. The recorded proof suite passed. |

## Touches

- `frontend/src/features/viewer/*`
- `frontend/src/features/board-adapter/BoardAdapter.tsx`
- `frontend/src/features/board-adapter/BoardAdapter.module.css`
- `frontend/src/features/board-adapter/BoardAdapter.test.tsx`
- `frontend/src/features/design-system/Disclosure.tsx`
- `frontend/src/features/design-system/Disclosure.module.css`
- `frontend/src/features/design-system/Disclosure.stories.tsx`
- `frontend/src/features/design-system/Disclosure.test.tsx`
- `backend/app/features/*`
- `backend/app/main.py`
- `backend/tests/features/*`
- `tests/e2e/*`

The `backend/app/features/*` and `backend/tests/features/*` globs are the ownership envelope for the new `positions` feature: the stages create `backend/app/features/positions/` and `backend/tests/features/positions/` within them. The existing `backend/app/features/health/*` and `backend/tests/features/health/*` files are **not** modified (exclusions below). `docs/plans/active/mp07-arbitrary-stored-fen-display/` is the Plan's own location, not an implementation ownership glob. Exact new-file paths are carried in each stage's compiler handoff below. No active Plan exists, so there is no `Depends on:` entry; MP-07 builds on the accepted MP-06 corpus (archived `docs/plans/done/mp06-validated-fen-corpus/`).

## Compiler handoff

### Stage 1 - mocked Storybook frontend experience and blocking human design gate (ORDERED)

- **Verified edit sites:**
  - `frontend/src/features/viewer/ViewerWorkspace.tsx:28-44` - currently static: renders `<BoardAdapter fen={STARTING_FEN} label="Chess board: standard starting position, White at the bottom" />`, a context panel (`tabIndex={0}`) and a `details` context disclosure; no form, state, or API. The new lookup form, result states, and reset build on this file; the standard starting board must remain the initial state and the accepted context panel/disclosure stay in place unless the design checkpoint changes them.
  - `frontend/src/features/board-adapter/BoardAdapter.tsx:4-8,149-221` - `BoardAdapterProps` exposes `fen`, `orientation?: "white" | "black"`, `showCoordinates`, `label`; `STARTING_FEN` is exported for fixtures; `validateFen` plus `createPositionModel` failure path render `UnavailablePosition` (PanelFeedback severity="error"). The approved Stage 1 design replaces only the native position-description disclosure with the shared `Disclosure` component; the adapter's props, strict FEN safety, read-only rendering, and accessible descriptions remain unchanged.
  - `frontend/src/features/board-adapter/BoardAdapter.module.css:47-82` - the adapter-local position-description styles are narrowed to the content inside the shared `Disclosure`; existing board layout, token use, and forced-colors behavior remain the contract.
  - `frontend/src/features/board-adapter/BoardAdapter.test.tsx:88-103` - the focused adapter test verifies the shared Disclosure trigger's `aria-expanded` state while preserving the assistive description relationship.
  - `frontend/src/features/design-system/Disclosure.tsx:1-46` - new shared token-driven wrapper around the Base UI `Collapsible` primitive; it supplies the existing viewer and board-adapter disclosures with accessible trigger/panel behavior, controlled and uncontrolled state, consumer props, and class-name placement.
  - `frontend/src/features/design-system/Disclosure.module.css:1-73` - new shared Disclosure styles using project tokens, including focus-visible and forced-colors behavior.
  - `frontend/src/features/design-system/Disclosure.stories.tsx:1-85` - new Storybook coverage for collapsed, open, and long-content Disclosure states.
  - `frontend/src/features/design-system/Disclosure.test.tsx:1-102` - new component coverage for default, toggled, controlled, ARIA, and consumer-prop behavior.
  - `frontend/src/features/viewer/ViewerWorkspace.stories.tsx:15-26` - today has `Wide` and `Constrained` stories using `styles.constrainedStory`; expand to the ten MP-07 states in both layouts with deterministic mocked lookup behavior and no backend or database.
  - New feature-local files under `frontend/src/features/viewer/*` (e.g., a mocked lookup service and the viewer state module; exact names are implementation defaults within this ownership envelope).
- **Verified tests:**
  - Storybook interaction-test precedent: `frontend/src/features/board-adapter/BoardAdapter.stories.tsx:83-84` (`play` + `userEvent.click` + `within`), `frontend/src/features/app-shell/AppShell.stories.tsx:44-48,93-94`, `frontend/src/features/design-system/FoundationSpecimen.stories.tsx:19-20`. `@storybook/test-runner` 0.24.4 is installed; `frontend/package.json:11-15` scripts: `"storybook": "storybook dev -p 6006"`, `"test-storybook": "test-storybook"`, `"build-storybook": "storybook build"`.
  - Focused component-test precedent: `frontend/src/features/board-adapter/BoardAdapter.test.tsx:88-103` covers the adapter disclosure trigger and assistive description; `frontend/src/features/design-system/Disclosure.test.tsx:11-102` covers shared Disclosure default, toggle, controlled, ARIA, and consumer-prop behavior.
  - Component-test pattern: `frontend/src/features/status/statusApi.ts:3-14` - `API_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666"`, `fetch` with `AbortSignal`, throws on non-ok, shape-checks the body; `frontend/src/features/status/StatusView.test.tsx` is the component test precedent.
  - Frontend test runner: `npm.cmd run test --prefix frontend -- --run` (full suite, as used by `scripts/check.py:41`); focused vitest accepts file-path filters after `--run`.
- **Settled contracts:**
  - Ten visual states, each in wide and constrained layouts: (1) initial starting-position board with empty form; (2) invalid form input (client requires a syntactically valid UUID and a whole-number ply of zero or greater before any request); (3) loading while preserving the current board, with submission disabled until the lookup finishes (one in-flight lookup, no queue or race); (4) successful retrieval with the corpus subject as White; (5) successful retrieval with the corpus subject as Black; (6) position not found; (7) corpus unavailable; (8) stored position unavailable; (9) unexpected request failure; (10) reset behavior.
  - Editing form fields never changes the loaded board until another valid submission succeeds. After a failed lookup the prior board is removed so it cannot be mistaken for the requested occurrence. **Reset viewer** clears the form and restores the empty-form standard starting-position state. Selection is React state only; reloading or leaving and returning to `/viewer` starts again with the empty form and the starting board; no URL representation.
  - Successful retrieval visibly associates game UUID, ply, complete six-field FEN, and corpus subject color with the board; the board is oriented with the subject's color at the bottom; its accessible label identifies the game UUID, ply, and which corpus-subject color is at the bottom; the existing board adapter continues to provide its detailed textual position description.
  - Storybook uses deterministic mocked API behavior; it does not require a running backend or database. The mock injection mechanism (injected lookup prop vs. module-level mock) and the UUID/ply validation approach are implementation defaults.
  - Stage 1 ends with the blocking human design gate: the user edits the Storybook design as long as needed and explicitly accepts it; Stages 2 and 3 are not authorized until that explicit acceptance, and the approved stories/components bind them.
- **Constraints:** keep the board read-only; no real API calls in Stage 1; preserve the accepted context panel/disclosure and the `/` status page; the board adapter's strict FEN safety contract is never weakened; no backend, database, or network dependency in Storybook. The approved scope includes only the three named board-adapter files and four named Disclosure files for the shared Disclosure integration; no other board-adapter or design-system work is authorized.
- **Open questions:** none material. Exact visual copy, spacing, and layout beyond the settled wording are the user's edits at the design checkpoint, not pre-decisions.

### Stage 2 - backend API (ORDERED)

- **Verified edit sites:**
  - `backend/app/main.py:7-17` - `create_app()` includes the health router and CORS `allow_origins=["http://localhost:8444"]`, `allow_methods=["GET"]`; the new positions router is included here and must not widen CORS methods.
  - `backend/app/features/health/router.py:5-10` and `backend/app/features/health/schemas.py:1-7` - feature-first precedent: `APIRouter(prefix="/api", tags=[...])`, `@router.get(path, response_model=...)`, pydantic `BaseModel` with `ConfigDict(extra="forbid")`.
  - New feature directory `backend/app/features/positions/` (router, schemas, and a read-only service/repository module; exact file split is an implementation default within this envelope).
- **Verified tests:**
  - `backend/tests/features/health/test_health.py:1-28` - `TestClient(app)` precedent, including CORS origin assertions. pytest `testpaths=["backend/tests","tests"]`, `pythonpath=["."]`.
  - New `backend/tests/features/positions/` suite using temporary fixture databases for isolated backend tests; precedent `tests/test_extract_corpus.py` (MP-06) uses pytest `tmp_path` + `sqlite3.connect` with `from scripts.chess_com import fetch_games`-style imports.
  - Focused selector: `.venv\Scripts\python.exe -m pytest backend/tests/features/positions -q`; full suite: `.venv\Scripts\python.exe -m pytest`; full local check: `.venv\Scripts\python.exe scripts\check.py`.
- **Settled contracts:**
  - Endpoint `GET /api/games/{game_uuid}/positions/{ply}`. A successful response contains only `game_uuid`, `ply`, `fen` (complete six-field), and `subject_color` constrained to `white` or `black`. The endpoint is a complete, tested API; it does not return game metadata, adjacent positions, or traversal controls.
  - FEN reconstruction: join `position_occurrence` (`game_uuid`, `ply`, `halfmove_clock`, `fullmove_number`, `state_id`) with `position_state` (`placement`, `side_to_move`, `castling`, `en_passant`) for the six fields, then validate with the backend's pinned chess library (`chess==1.11.2` in `requirements.txt` per MP-06) before returning success. The frontend's `chess.js` `validateFen` remains a separate defensive boundary; neither replaces the other.
  - Subject color: compare the game's `white_player_uuid`/`black_player_uuid` with `corpus.subject_player_uuid` (`0101b08a-ce8b-11ee-b2fd-e90263e5548c`); MP-06 membership test precedent: `(white_player_uuid = :s) != (black_player_uuid = :s)`.
  - Database boundary: path is environment-configurable; local default `data/database/chess_games.db`; the repository/service receives a read-only connection and has no write authority; MP-07 does not initialize, repair, migrate, or upgrade corpus storage; failure to open the corpus database does not prevent backend start or `/api/health` (health stays 200; position requests return 503).
  - Typed error bodies with machine-readable codes and safe messages; the exact pinned codes are lowercase: **`position_not_found`** (404 - no matching game UUID and ply), **`corpus_unavailable`** (503 - missing, inaccessible, uninitialized, or unsupported corpus schema), **`stored_position_invalid`** (500 - a matching occurrence whose persisted fields violate the promised position invariants), **`unexpected_failure`** (any other unexpected backend failure, returned as an applicable non-success response). Malformed UUID or invalid ply returns HTTP **422**, preserving FastAPI's own validation body; no custom code is defined for it. No error body exposes technical details or database internals, and the frontend never infers behavior from prose.
- **Constraints:** never write `games`, `players`, `fetch_state`, or any corpus table; no schema auto-migration; GET-only CORS unchanged; the pinned codes above are fixed, not reversible defaults; error messages are safe and stable.
- **Open questions:** none material. Exact SQLite read-only connection mechanics (URI mode vs. connection flag) and the 500-invariant test fixture construction are bounded implementation choices following the settled contract and the temp-DB precedent.

### Stage 3 - live frontend integration and full-corpus browser proof (ORDERED)

- **Verified edit sites:**
  - New feature-local API client under `frontend/src/features/viewer/*` mirroring `frontend/src/features/status/statusApi.ts:3-14` (`VITE_API_BASE_URL` default `http://localhost:5666`, fetch with `AbortSignal`, non-ok throws, body shape checks); viewer wiring consumes the real endpoint while preserving the Stage 1 approved design contract exactly.
  - New live browser spec under `tests/e2e/*` alongside the existing `tests/e2e/playwright.config.ts` (referenced by `scripts/check.py:50-57`); existing specs (`viewer.spec.ts`, `status.spec.ts`, etc.) are the harness precedent and are not modified.
- **Verified tests:**
  - Component tests with mocked fetch covering the success payload and each typed-code-to-failure-state mapping; run via `npm.cmd run test --prefix frontend -- --run`.
  - Live proof command: `node_modules\.bin\playwright.cmd test --config tests\e2e\playwright.config.ts` (exact command as used by `scripts/check.py:50-57`). `tests/e2e/playwright.config.ts` already declares the backend, frontend, and Storybook `webServer` entries with `reuseExistingServer: true`; the backend uses port 5666 and the frontend uses port 8444. The full local check is `.venv\Scripts\python.exe scripts\check.py` and the documentation check is `.venv\Scripts\python.exe scripts\check_docs.py --check`.
- **Settled contracts:**
  - Failure mapping (fixed): 404 `position_not_found` -> **Position not found**; 503 `corpus_unavailable` -> **Corpus unavailable**; 500 `stored_position_invalid` -> **Stored position unavailable**; any other non-success or network failure -> **Unable to load position**. The prior board is removed after a failed lookup; the current board remains visible while loading.
  - Live proof uses the full untracked local corpus database at `data/database/chess_games.db`: submit a known game UUID and ply from the full corpus; display the returned identity and FEN; verify that the corpus subject's color is at the bottom; and exercise one missing occurrence. **No generated or minimal E2E fixture is substituted**; the full local database is an accepted untracked local prerequisite. Temporary fixture databases remain allowed only for the isolated backend tests in Stage 2.
  - The approved Stage 1 stories and components are the frontend design contract; this stage preserves that behavior rather than reinterpreting it.
- **Constraints:** board remains read-only; selection remains React state only (no URL representation); no database writes from any MP-07 code; no new CORS origins or methods.
  - **Open questions:** none material. No package-script command requires a later lookup: every command above is already pinned in `frontend/package.json` or `scripts/check.py` and is recorded exactly as known.

## Exclusions

- No URL-addressable positions, query-string selection, or remembered selection across viewer visits or browser restarts.
- No game browsing or search, game metadata presentation, adjacent-position data, or Previous/Next or other traversal controls (MP-08).
- No board movement or editing (MP-11), user-created position persistence (MP-12), PGN replay, Stockfish/browser analysis (MP-09/MP-10).
- No database writes, initialization, repair, or migration; no modification of `scripts/chess_com/fetch_games.py`, `scripts/chess_com/extract_corpus.py`, or the fetcher-owned `games`/`players`/`fetch_state` tables.
- No portable fixture databases, committing or rebuilding the corpus for fresh-checkout verification, or E2E fixtures other than the full untracked local `data/database/chess_games.db`.
- No modification of `backend/app/features/health/*`, `backend/tests/features/health/*`, or `frontend/src/features/status/*` (regression-covered, not touched).
- No board-adapter changes beyond the approved Stage 1 shared Disclosure integration in `frontend/src/features/board-adapter/BoardAdapter.tsx`, `frontend/src/features/board-adapter/BoardAdapter.module.css`, and `frontend/src/features/board-adapter/BoardAdapter.test.tsx`; the adapter's props, strict FEN safety, read-only behavior, and other contracts remain unchanged.
- No design-system changes beyond `frontend/src/features/design-system/Disclosure.tsx`, `Disclosure.module.css`, `Disclosure.stories.tsx`, and `Disclosure.test.tsx` as the supporting shared Disclosure integration; no unrelated design-system work.
- No final visual approval before the mandatory Storybook checkpoint, and no authorization to skip, automate, or waive that checkpoint.
