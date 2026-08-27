# Remove the legacy per-ply positions route - whole-game loading remains the only current position source

> **Status:** done - both stages, independent validation, and full closeout accepted.

- **Read trigger:** Read before dispatching each stage of this bounded route-removal change.
- **Upstream:** none

## Outcome

The per-ply positions URL is no longer available or represented by current backend and frontend code. The existing whole-game positions URL continues to return its accepted response and errors, and the viewer continues selecting and traversing returned plies in memory.

## Scope

- **Included:** Remove `GET /api/games/{game_uuid}/positions/{ply}` and only its current backend route, repository, schema, frontend client, and test uses. Update focused backend tests to prove the removed URL is unavailable and the whole-game contract remains unchanged. Remove the unused `fetchPosition` client surface and update its focused test. Update the existing live-viewer assertion for the removed URL while retaining whole-game request and in-memory traversal proof.
- **Expected areas:** `backend/app/features/positions/router.py`; legacy-only portions of `backend/app/features/positions/repository.py`; legacy-only portions of `backend/app/features/positions/schemas.py`; `backend/tests/features/positions/test_positions.py`; `frontend/src/features/viewer/positionApi.ts`; `frontend/src/features/viewer/positionApi.test.ts`; `tests/e2e/viewer-live-position.spec.ts`; the existing test-profile assignment for that spec in `tests/e2e/playwright.config.ts`
- **Excluded:** `ViewerWorkspace` behavior; the whole-game route, response, optional `ply`, errors, and current in-memory traversal; database or database-schema changes; unrelated routes or tests; completed historical records; dependencies and package changes; compatibility redirects or alternate endpoints.

## Stages

1. **done - remove backend route and legacy-only surfaces.**
   - **Ordered actions:** Remove the per-ply router handler and its legacy-only imports, response/error schemas, repository dataclass, repository methods, and wrapper while retaining shared whole-game errors and repository behavior. Update the focused positions tests to remove obsolete success/error coverage, assert the removed URL is unavailable, and retain exact whole-game success, optional-`ply`, typed-error, validation, and read-only coverage.
   - **Focused proof:** `.venv/Scripts/python.exe -m pytest backend/tests/features/positions -q`
   - **Breakpoint:** none.
   - **Escalation boundary:** Stop if an unlisted backend consumer appears or preserving the whole-game contract requires a behavior change.
2. **done - remove frontend client use and update integrated regression proof.**
   - **Ordered actions:** Remove `fetchPosition` and its legacy-only parsing, failure, and success types/helpers from the position API and focused test. Retain `fetchGame` request validation and whole-game URL/query coverage. Change the live-viewer regression assertion from preserving the per-ply response to asserting that URL is unavailable, while retaining the root status and one-request in-memory traversal checks.
   - **Focused proof:** `npm.cmd run test --prefix frontend -- --run src/features/viewer/positionApi.test.ts`; `node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-live-position.spec.ts`
   - **Breakpoint:** none.
   - **Escalation boundary:** Stop if the current runtime uses the removed client surface, if Viewer behavior must change, or if work outside the expected areas is necessary.

Stages are sequential; no stages run in parallel.

## Progress and decisions

- **Assessment:** done - the route and its current uses were confirmed; no active Plan collision was found.
- **Stage 1:** done - removed the backend per-ply route and legacy-only repository/schema surfaces; `.venv/Scripts/python.exe -m pytest backend/tests/features/positions -q` passed with 24 tests; breakpoint: none.
- **Stage 2:** done - removed the legacy frontend client surface and updated integrated regression proof; focused Vitest passed with 13 tests and fresh post-repair targeted Playwright validation passed with 3 tests; breakpoint: none.
- **Scope correction:** approved - independent validation found the existing Playwright profile classified this app-server spec as Storybook-only. Move only this spec from the Storybook set to the app set so the already-required browser proof can start ports 5666 and 8444; no product behavior or dependency changes.

## Proof

- `.venv/Scripts/python.exe -m pytest backend/tests/features/positions -q` - 24 passed.
- `npm.cmd run test --prefix frontend -- --run src/features/viewer/positionApi.test.ts` - 13 passed.
- `node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/viewer-live-position.spec.ts` - fresh post-repair validation passed all 3 tests.
- `.venv/Scripts/python.exe scripts/check.py` - all 14 read-only closeout checks passed.

## Escalation boundaries

- Any unlisted current consumer of the removed route or client surface.
- Any change to the whole-game route, response, optional-`ply` semantics, errors, or current in-memory traversal.
- Any request for compatibility, redirect behavior, an alternate endpoint, database/schema changes, dependency changes, or work outside the expected areas.
- Any unrelated check failure is reported without absorption; repair requires coordinator direction.

## Visible result

> Requests to the per-ply positions URL are unavailable, while the existing whole-game request still loads the complete response and the viewer traverses its positions without per-ply network requests.
