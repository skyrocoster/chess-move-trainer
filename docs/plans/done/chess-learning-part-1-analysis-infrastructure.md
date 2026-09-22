# Part 1 analysis infrastructure - quick coverage and explicit full upgrade

> **Status:** done - all six stages and focused behavioral proof are accepted.

- **Read trigger:** Read before implementing or reviewing Part 1 analysis profiles, analysis requests and readers, the Stockfish queue worker, or the existing frontend analysis interaction.
- **Upstream:** `docs/grilling-docs/chess-learning-workflow-2026-09-21.md`, especially Part 1, is the governing directional evidence. `docs/grilling-docs/chess-analysis-idea-catalogue-2026-09-21.md` is Part 2 evidence only and is explicitly excluded from implementation.

## Purpose

Make stored analysis affordable enough to collect across the game corpus while keeping the existing analysis interaction useful. A normal frontend request should produce a quick rank-one result, a user may explicitly request a full multi-line upgrade, and the already-running serial worker should use idle time to collect bounded quick coverage without starving requested work.

## Outcome

- Persisted `browser` remains the quick tier: 200,000 nodes and SinglePV.
- Persisted `tool` remains the full tier: 6,400,000 nodes and MultiPV 5.
- One current result remains stored per canonical position. Full replaces quick; quick never replaces full.
- The frontend requests quick analysis by default and offers an explicit full-analysis upgrade in the existing analysis panel.
- The existing Docker worker continuously discovers all eligible game positions while its explicitly started service is running, but claims requested queue work first and never creates a large background FIFO backlog.
- Quick and full rank-one results retain the same data shape for later analysis; full results are not excluded or put in a separate confirmation population.

## Scope

- **Included:**
  - Profile-specific MultiPV, settings, and freshness/version handling.
  - Quality-aware validation, completeness, readers, request reuse, and focused publication contracts.
  - All-game-position quick target discovery with deterministic ordering and bounded atomic background seeding through the existing queue.
  - Existing serial worker engine reuse, mutex, claim tokens, stale reclaim, interruption, and restart recovery.
  - Existing API wire behavior, frontend request default, explicit upgrade control, and focused behavioral proof.
- **Expected areas:**
  - Core profiles and analysis: `src/chess_move_trainer/database/stockfish/configuration.py`, `src/chess_move_trainer/database/analysis/{models,validation,reading,requests,observation,repository}.py`.
  - Queue, targets, worker, and CLI: `src/chess_move_trainer/database/stockfish/{queue_helpers,queue_service,targets,worker}.py`, `src/chess_move_trainer/database/cli_stockfish.py`.
  - Existing consumers: `src/chess_move_trainer/database/positions/{insight_helpers,insight_models,insight_repository}.py` and rank-one blunder readers only where the changed shared reader contract requires focused fixture updates.
  - Frontend analysis interaction: `frontend/src/features/analysis/{analysisApi,analysisState,analysisFormatting,AnalysisPanel}.ts{,x}` and the existing caller `frontend/src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx`.
  - Adjacent focused tests and Storybook stories for those ownership areas.
- **Excluded:**
  - The Part 2 analysis-idea catalogue, statistical feature models, GEE/bootstrap work, statistical promotion, or any statistical result.
  - Learning exercises, pattern labels, explanations, final workflow integration, or Part 3 decisions.
  - AI, a second queue, a second worker, a parallel Stockfish path, a restart-policy change, or queue-wide background preloading.
  - Schema migration, new dependencies, generated API contract changes, unrelated frontend redesign, `DESIGN.md`, design exploration, branches, worktrees, commits, or pushes.
  - Database rebuild/replacement automation. The worker must not run across replacement of the active database file; this remains an operational boundary.

## Evidence and settled decisions

- `configuration.py:13-18,72-79` already has separate node budgets and per-profile fields, but currently gives both profiles MultiPV 5 and one configuration version.
- `analysis/validation.py:199-234` currently requires five non-terminal lines for every quality. Quick validation must instead require one line; full validation remains `min(5, legal root moves)`.
- `analysis/reading.py:87-152`, `analysis/observation.py:238-270`, and position insight readers all read the one current result. The shared read path must reject incomplete or quality/settings-inconsistent results rather than allowing a partial full result to appear ready.
- `analysis/requests.py:151-185,240-256` already preserves one queue row, promotes quality, reuses a higher-quality result for a browser request, and checks configuration and engine freshness.
- `analysis/repository.py:199-213` already prevents a browser result from replacing a tool result; this no-downgrade behavior remains authoritative.
- `stockfish/worker.py:107-254` already claims serially, reuses one engine within a drain, and releases work during interruption. `cli_stockfish.py:178-280` already keeps a positive-poll worker alive; only discovery and bounded scheduling need to be added.
- `stockfish/targets.py:103-259` currently implements opening-focused pages through ply 19 and per-target eligibility reads. Background discovery belongs in this target-selection boundary but must traverse all `derived_game_position` rows, not opening routes.
- `schema_v2.sql:35-49,77-129` already contains game-position occurrences, one current result per position, and one queue row per position. The `browser` and `tool` enum strings remain unchanged.
- The frontend POST is hard-coded to tool in `frontend/src/features/analysis/analysisApi.ts:235-246`. The controlled panel is `AnalysisPanel.tsx:242-300`, called by `RepertoireBuilderWorkspace.tsx:82-88,450-455`. The generated API types already expose both quality values, so no codegen change is expected.
- The current corpus is approximately 12,710 games, 530,732 unique positions, and 519,155 learner before/after positions. Existing full results are split between Stockfish 18 and 19; the profile/engine metadata remains provenance and is not discarded.

### Profile and freshness decisions

- Make the profile fields authoritative: browser MultiPV `1`, browser configuration version `2`; tool MultiPV `5`, tool configuration version remains `1` because its node budget, MultiPV, and other result-affecting settings are unchanged.
- Keep any existing global `MULTI_PV=5` and `CONFIGURATION_VERSION=1` aliases only for unchanged benchmark compatibility. Freshness decisions must resolve the expected profile rather than comparing every quality to one global version.
- Persist complete profile settings, including MultiPV, node budget, threads, hash, and WDL setting. Configuration version is the freshness identity; settings remain validated provenance and must agree with the profile contract for new results.
- A missing result is a background quick target. A stale browser result is a background quick target when it is non-terminal. A current browser result is not a target.
- A missing terminal position may be claimed once; the engine classifies it without a Stockfish search and publishes zero lines. A stored valid terminal result is covered for background collection even if old profile metadata would otherwise be stale; explicit requests may still refresh its provenance.
- A current or stale tool result is never a background quick target and is never downgraded. Both satisfy a browser request. An explicit tool request may refresh a stale tool result.
- A queued or running position is not selected for background discovery. Requested work is claimed before every background selection. Background seeding and claiming occur atomically when the queue is idle so a new frontend request waits behind at most the currently running quick search, apart from an already-existing requested backlog.
- Target order is distinct game count descending, then canonical position ID ascending, using bounded keyset pages. Selection must avoid an eligibility query per returned row and must not add a persistent target table or schema index without escalation.

## Ownership and compatibility boundaries

| Area | Owning paths | Required compatibility |
|---|---|---|
| Search profiles and provenance | `stockfish/configuration.py`, engine helpers | `browser`/`tool` strings, node budgets, Stockfish 19 identity, persisted settings |
| Validation and current-result reads | `analysis/validation.py`, `reading.py`, `observation.py` | terminal policy, legal PVs, rank-one quick data, full MultiPV data, one current row |
| Desired requests and publication | `analysis/requests.py`, `repository.py`, queue service | higher quality satisfies quick; tool replaces browser; browser cannot replace tool |
| Background target selection | `stockfish/targets.py` | all game positions, deterministic order, no opening-only restriction, no queue flood |
| Queue and worker scheduling | `stockfish/queue_helpers.py`, `queue_service.py`, `worker.py`, `cli_stockfish.py` | FIFO claims, atomic promotion, stale reclaim, mutex, engine reuse, graceful shutdown |
| HTTP and frontend interaction | existing analysis API feature and `frontend/src/features/analysis`, repertoire workspace caller | current routes and generated types, quick default, explicit full upgrade, no new visual direction |

The backend request schema already defaults quality to `browser` (`backend/app/features/analysis_requests/api_schemas.py:14-23`), and the generated frontend schema already permits both values. Preserve those contracts rather than adding a route or regeneration step.

## Stages

Stages are sequential. No independent stages are placed in parallel. A passing proof item remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment; later stages rerun only proof that is missing or invalidated.

1. **complete - establish profile-specific analysis contracts.**
   - Update the profile representation so browser resolves to 200,000 nodes, MultiPV 1, and configuration version 2 while tool remains 6,400,000 nodes, MultiPV 5, and configuration version 1.
   - Make the shared position validator derive completeness from quality/profile settings: one legal line for non-terminal browser results, all legal roots up to five for tool results, and no lines for terminal results. Preserve legal PV and contiguous-rank checks.
   - Make current-result readers validate the stored position and result together, so analysis observation, position insight, desired requests, and rank-one consumers cannot accept an incomplete full result. Keep rank bounds at five.
   - Preserve the existing one-row atomic replacement and no-downgrade publication behavior.
   - **Focused proof:**
     - `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_models.py tests/database/analysis/test_validation.py tests/database/analysis/test_reading.py tests/database/stockfish/test_engine.py`
     - Bash tool timeout: `150000` ms.
   - **Breakpoint:** none. Escalate before changing schema or persisted enum strings if the profile representation cannot remain backward-compatible.

2. **complete - preserve request, freshness, and API read behavior.**
   - Replace global freshness comparisons in desired-request and target eligibility code with profile-specific freshness resolution.
   - Ensure unchanged current tool results are reused, stale tool results remain tool and satisfy browser requests, explicit tool requests refresh stale tool results, and browser work cannot publish over tool.
   - Update only the focused fixtures and contracts that currently use one-line tool results or omit the persisted MultiPV setting. Keep the HTTP response fields, route names, generated types, and quality strings unchanged.
   - Verify that rank-one blunder scoring continues to pool current browser and tool results without quality filtering or a confirmation population.
   - **Focused proof:**
     - `timeout 150s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_requests.py tests/database/analysis/test_repository.py tests/database/analysis/test_observation.py backend/tests/features/analysis_requests/test_api.py backend/tests/features/analysis_observation/test_api.py backend/tests/features/position_insight/test_api.py tests/database/blunders/test_blunders.py`
     - Bash tool timeout: `180000` ms.
   - **Breakpoint:** none. Escalate only if preserving the existing API requires a wire-contract or codegen change.

3. **complete - add bounded all-position background selection and atomic queue seeding.**
   - Add the background selector in `stockfish/targets.py`, reusing canonical target values and package-owned database connections but not the manual opening-focused selector semantics.
   - Aggregate all game-position occurrences by distinct game count, order by `(game_count DESC, position_id ASC)`, and page with a deterministic keyset. Exclude queued/running positions and current or stale tool results. Select missing or stale non-terminal browser coverage, with the terminal policy recorded above.
   - Avoid the existing per-target eligibility-query pattern. Keep only a bounded in-memory candidate page; do not persist a corpus queue or enqueue the page as a batch.
   - Add an existing-queue operation that, under the queue’s immediate transaction, confirms no queue row exists, inserts one browser background request, and claims it immediately. A concurrent frontend request must win or leave the worker with the requested row to claim next.
   - Leave `BulkRunner` as direct tool analysis with its existing opening-focused target behavior.
   - **Focused proof:**
     - `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_targets.py tests/database/stockfish/test_queue.py`
     - Bash tool timeout: `150000` ms.
   - **Breakpoint:** none for the bounded page/query route. Escalate if measured target scans require a persistent index, schema change, or a different ordering policy.

4. **complete - integrate discovery into the persistent serial worker.**
   - Extend the existing worker drain so it claims all requested/reclaimable queue work first, then atomically claims one background browser target only when the queue is empty.
   - Recheck the queue between every completed background target. Reuse one `StockfishEngine` for active sequential work, continue to use the existing mutex and claim tokens, and close the engine only when the drain becomes idle or fails.
   - Keep the positive CLI poll loop alive until explicitly stopped. When no target remains, return to its existing quiet finite polling sleep. Do not add an automatic restart policy.
   - Preserve isolated failure handling, stale reclaim, Ctrl-C release, graceful engine close, and rerun recovery. Background work must never create automatic full upgrades.
   - **Focused proof:**
     - `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_worker.py tests/database/stockfish/test_bulk.py`
     - Bash tool timeout: `150000` ms.
   - **Breakpoint:** none. Escalate if the worker cannot guarantee requested-before-background behavior without adding a queue source field or second queue.

5. **complete - make the existing frontend interaction quick by default with explicit upgrade.**
   - Extend `analysisApi.ts` quality types and request plumbing so browser is the default while callers can explicitly request tool; preserve existing signal, error, observation, and cache invalidation behavior.
   - Retain result quality in the frontend model. Extend `analysisState.ts` and `analysisFormatting.ts` so a browser-ready result exposes a full-upgrade action, while missing results expose the existing deliberate quick Analyze action and active work exposes neither action.
   - Reuse `AnalysisPanel.tsx` and its existing action row. Add a semantic “Upgrade to full analysis” control for browser results and retain the existing “Analyze position” control for quick requests. Do not create a new panel, route, visual system, or design artifact.
   - Keep the repertoire workspace as the existing caller and preserve candidate-move behavior, polling, retained results during active work, and terminal presentation.
   - Update adjacent focused component tests, state/API tests, workspace tests, and Storybook fixtures/stories for one-line quick results, five-line full results, and the upgrade callback.
   - **Focused proof:**
     - `timeout 120s npm --workspace frontend exec -- vitest run src/features/analysis/analysisApi.test.ts src/features/analysis/analysisState.test.ts src/features/analysis/analysisFormatting.test.ts src/features/analysis/AnalysisPanel.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx`
     - Bash tool timeout: `150000` ms.
   - **Breakpoint:** the existing panel’s 320px, 480px, and 640px constrained behavior is the only visual breakpoint. Escalate if the upgrade interaction requires a new composition rather than reuse of the existing action row.

6. **complete - retain focused integrated behavioral proof and acceptance.**
   - Confirm shared services before browser proof; reuse healthy services through `dev.ps1` and do not start competing host processes.
   - Run the focused Storybook analysis-panel scenario for quick/default and full-upgrade controls, semantic states, accessibility, bounded layout, and no horizontal overflow.
   - Exercise the worker recovery scenario with a small database fixture: requested work is claimed before background work; only one background claim exists at a time; interruption leaves reclaimable work; rerun completes it; current tool results are never downgraded.
   - Confirm the operational boundary: the worker continues only while explicitly started, and database replacement is coordinated outside the worker rather than automated here.
   - **Focused proof:**
     - `timeout 30s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status`
     - Bash tool timeout: `45000` ms.
     - After confirming healthy shared Storybook service: `timeout 150s npx playwright test --config=tests/e2e/playwright.config.ts tests/e2e/analysis-panel-storybook.spec.ts`
     - Bash tool timeout: `180000` ms.
   - **Breakpoint:** none. Do not run broad, aggregate, hygiene, lint, formatting, build, or complete-suite checks as part of this Plan.

## Progress and decisions

- **Stage 1:** complete - browser/tool profiles now carry authoritative MultiPV and configuration versions; quality-aware validation and shared position-plus-result reads reject incomplete or profile-inconsistent current results. Focused proof passed: `66 passed in 0.84s`.
- **Stage 2:** complete - desired requests and target eligibility now resolve freshness from the applicable profile; stale tool results continue to satisfy browser requests, explicit tool requests refresh stale tool results, no-downgrade behavior remains unchanged, and focused API/rank-one fixtures carry complete valid provenance. Focused proof passed: `105 passed in 5.13s`.
- **Stage 3:** complete - bounded keyset discovery now covers all game plies in distinct-game-count order with set-based eligibility, and the existing queue can atomically seed and immediately claim one browser target only when empty. Existing requested work remains untouched and `BulkRunner` remains unchanged. Focused proof passed: `20 passed in 1.71s`.
- **Stage 4:** complete - the serial drain now claims requested/reclaimable work before every bounded background attempt, seeds only one browser target at a time, and rechecks the queue after each completion. Existing engine reuse, mutex/token, interruption, recovery, failure-isolation, close, CLI polling, and `BulkRunner` behavior remain intact. Focused proof passed: `17 passed in 1.83s`.
- **Stage 5:** complete - frontend requests now default to browser quality, explicit upgrades request tool quality, result quality reaches presentation state, and the existing action row shows the appropriate quick or upgrade control while preserving active, terminal, polling, retained-result, candidate, and constrained compositions. Focused proof passed: `5 files, 53 tests in 10.40s`.
- **Stage 6:** complete - shared-service status was checked, only Storybook was started, and the focused Storybook scenario passed for quick/full controls, semantic states, accessibility/focus, and 320/480/640px no-overflow behavior. Retained Stage 2-4 proof continues to establish no-downgrade and small-database worker scheduling, interruption, and recovery. The worker remained stopped pending post-Plan startup. Focused browser proof passed: `4 passed in 15.6s`.

### Decision log

- `browser` and `tool` remain the persisted enum strings; “quick” and “full” are user-facing roles only.
- Browser configuration version increments to 2 because its MultiPV changes; tool remains configuration version 1 because its approved settings do not change.
- Full quality always satisfies quick coverage, including when the full result is stale; background work never downgrades or automatically refreshes full quality.
- Missing terminal positions may be stored through the existing no-search engine classification; stored terminal results are not background-refresh targets.
- Distinct-game frequency descending and canonical position ID ascending is the deterministic background order.
- One background target is inserted and claimed atomically through the existing durable queue; no queue source field or second queue is introduced.
- No database schema migration, dependency change, generated API change, automatic restart policy, or design exploration is authorized by this Plan.

## Behavioral acceptance

- A browser-profile non-terminal search publishes exactly one legal rank-one line with the 200,000-node settings and browser provenance. A terminal result publishes zero lines.
- A tool-profile non-terminal search publishes five lines, or one per legal root when fewer than five exist, with the 6,400,000-node settings and tool provenance. Tool remains MultiPV 5.
- Current tool results from the unchanged tool profile are not falsely stale after the browser profile version changes.
- A tool result replaces a browser result atomically; a browser result cannot replace a tool result.
- Missing and stale non-terminal browser targets are discoverable across all game plies. Opening-route-only targets are insufficient.
- Requested queue work is claimed before each background target. At most one background target is claimed beyond existing requested backlog, and a frontend request can wait behind no more than the currently running quick job.
- Background collection never enqueues automatic tool upgrades, never downgrades a tool result, and returns to quiet polling when no quick target remains.
- Stopping or interrupting the worker releases or leaves safely reclaimable work; restarting the explicitly started worker completes it without duplicate current results.
- The frontend POST defaults to `quality: "browser"`; the existing panel exposes an explicit full upgrade for a browser-ready result and no upgrade for a tool-ready result.
- Rank-one consumers use whichever current result is stored, regardless of quick/full quality. Multi-line consumers continue to require available candidate lines.
- The Plan is accepted only after the focused proof above passes. Passing proof is retained until an affecting change invalidates it.

## Proof

Only the finite behavioral commands listed in the stages are in scope. They directly cover profile validation, current-result compatibility, queue and target ordering, worker scheduling/recovery, frontend request bodies and interaction, and the existing Storybook surface. Lint, formatting, broad type/build, source-size, aggregate, complete-suite, and repository-hygiene checks are excluded from this Plan.

- **Stage 1 (2026-09-22):** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_models.py tests/database/analysis/test_validation.py tests/database/analysis/test_reading.py tests/database/stockfish/test_engine.py` from the repository root with Bash tool timeout `150000` ms - `66 passed in 0.84s`. This proves the profile values, quality-aware completeness, settings consistency, and validated shared current-result read path. Relied on the Stage 1 source and tests in `stockfish/configuration.py`, `analysis/validation.py`, `analysis/reading.py`, and their focused test files.
- **Stage 2 (2026-09-22):** `timeout 150s .venv/Scripts/python.exe -m pytest tests/database/analysis/test_requests.py tests/database/analysis/test_repository.py tests/database/analysis/test_observation.py backend/tests/features/analysis_requests/test_api.py backend/tests/features/analysis_observation/test_api.py backend/tests/features/position_insight/test_api.py tests/database/blunders/test_blunders.py` from the repository root with Bash tool timeout `180000` ms - `105 passed in 5.13s`. This proves profile-specific desired-request and target freshness, stale-tool reuse and explicit refresh behavior, unchanged API and publication contracts, and rank-one pooling across valid current browser/tool results. Stage 1 proof remained valid.
- **Stage 3 (2026-09-22):** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_targets.py tests/database/stockfish/test_queue.py` from the repository root with Bash tool timeout `150000` ms - `20 passed in 1.71s`. This proves bounded all-ply keyset discovery, distinct-game-count ordering, set-based browser/tool/result/queue eligibility, and one atomic queue-empty browser seed plus immediate claim. Retained Stage 1-2 proof remained valid.
- **Stage 4 (2026-09-22):** `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/stockfish/test_worker.py tests/database/stockfish/test_bulk.py` from the repository root with Bash tool timeout `150000` ms - `17 passed in 1.83s`. This proves requested-before-background scheduling, one-at-a-time browser claims, queue rechecks between background targets, engine reuse and close, interruption release plus rerun recovery, and isolated background failure handling. Retained Stage 1-3 proof remained valid.
- **Stage 5 (2026-09-22):** `timeout 120s npm --workspace frontend exec -- vitest run src/features/analysis/analysisApi.test.ts src/features/analysis/analysisState.test.ts src/features/analysis/analysisFormatting.test.ts src/features/analysis/AnalysisPanel.test.tsx src/features/repertoire-builder/RepertoireBuilderWorkspace.test.tsx` from the repository root with Bash tool timeout `150000` ms - `5 files passed, 53 tests passed in 10.40s`. This proves browser-default and explicit-tool request bodies, quality retention, quick/full action visibility, upgrade callback wiring, active and terminal behavior, and the existing workspace interaction. Backend/worker proof remained valid.
- **Stage 6 service check (2026-09-22):** `timeout 30s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status` from the repository root with Bash tool timeout `45000` ms reported backend, frontend, worker, and Storybook exited. Only Storybook was then started with `timeout 120s powershell -ExecutionPolicy Bypass -File ./dev.ps1 start storybook` and Bash tool timeout `150000` ms; it became healthy while the other services remained stopped.
- **Stage 6 browser proof (2026-09-22):** `timeout 150s npx playwright test --config=tests/e2e/playwright.config.ts tests/e2e/analysis-panel-storybook.spec.ts` from the repository root with Bash tool timeout `180000` ms - `4 passed in 15.6s`. This proves deliberate quick Analyze, browser-ready full upgrade, five-line full without upgrade, active and terminal action suppression, accessibility/focus semantics, and no horizontal overflow at 320px, 480px, and 640px. Retained Stage 2-4 proof supplies no-downgrade and the small-database worker recovery scenario; no affecting backend change occurred.

## Escalation boundaries

- Ask before adding a schema migration, persistent target/index table, queue source-priority field, second queue, second worker, or new Stockfish execution path.
- Ask if measured target selection requires changing the approved deterministic order or relaxing all-game-position coverage.
- Ask if database replacement must be made safe while the worker remains active, or if API and worker database paths cannot be operationally aligned.
- Ask before changing the `browser`/`tool` wire values, the existing HTTP routes, generated API contracts, dependency set, or publication semantics.
- Ask before changing terminal eligibility, stale-full treatment, quick/full population pooling, or the acceptance rules above.
- Ask before expanding the frontend beyond the existing analysis interaction or introducing a new visual direction.
- Any request for Part 2 statistical models, Part 3 training behavior, AI explanations, pattern labels, or learning-workflow integration is outside this Plan.

## Visible result

> The analysis panel requests an affordable quick result by default, offers a clear full-analysis upgrade, and the running worker steadily fills the complete game-position corpus without building a large queue or replacing deeper results.
