# Line Library - production opening API and Storybook selector

> **Status:** in progress - Stages 1-4 accepted; awaiting Storybook visual breakpoint

- **Read trigger:** Read before any Line Library API, opening-provider, reusable selector, Storybook fixture, or
  related documentation change.
- **Upstream:** [Line Library historical grilling synthesis](../../../grilling-docs/line-library.md)

## Outcome

Provide a production read-only opening Line Library API over the accepted opening and fixed-corpus data, and a
reusable rendered Line Library selector demonstrated through an opening-specific Storybook consumer. Storybook
uses clearly synthetic in-memory fixtures and never calls the production API; no application route or downstream
action is added.

## Scope

- **Included:** `GET /api/openings/line-library` as the recommended domain endpoint; a strict normalized transport
  contract with authoritative roots and addressable nodes; group, line, and reference nodes; disabled state and
  backend-supplied reasons; generic filter, sort, and selection-limit declarations; server-side text, ECO
  code/range, and `appears_in_my_games` filtering; backend ordering; fixed accepted-corpus lookup through
  `SUBJECT_PLAYER_UUID` without authentication; read-only repository/service/router behavior and API errors; a
  reusable Headless Tree + Base UI rendered selector; structured row slots; configurable shell; controlled and
  convenience-default state; single- and multi-selection; tri-state groups; stale-tree and failure states; empty
  states; optional generic Apply/commit reporting; and opening-specific Storybook stories with synthetic
  in-memory provider fixtures.
- **Expected areas:** `backend/app/features/openings/{__init__.py,router.py,api_schemas.py,service.py,repository.py,errors.py}`;
  `backend/app/main.py`; `backend/tests/features/openings/{__init__.py,conftest.py,test_contract.py,test_api.py}`;
  `frontend/src/features/design-system/line-library/{LineLibrary.tsx,lineLibraryTypes.ts,LineLibrary.module.css,LineLibrary.test.tsx,LineLibrary.stories.tsx}`;
  `frontend/src/features/openings/{openingsApi.ts,openingsApi.test.ts,openingLineLibraryFixtures.ts,OpeningLineLibrary.stories.tsx}`;
  `frontend/.storybook/main.ts` only if the opening story is outside an already discovered glob;
  `tests/e2e/line-library-storybook.spec.ts`; and `tests/e2e/playwright.config.ts` for Storybook-only test
  classification. Expected areas describe ownership, not blanket execution authority.
- **Excluded:** Any generic or opening database schema, migration, source/import change, runtime database write,
  authentication or authorization, frontend live API fetching, application page or route, downstream API action,
  board playback, training, repertoire mutation, client-side authoritative filtering, invented production IDs,
  relationships, or eligibility rules, lazy loading, row virtualization, opening filters beyond text/ECO/
  `appears_in_my_games`, new dependencies, historical-record edits, `Scratch/` changes, commits, pushes, and
  unrelated worktree or database content.

## Stages

1. **done - normalized API contract, identity, and ownership gate (ORDERED).**
   - **Ordered actions:** Confirm the recommended `GET /api/openings/line-library` route and strict response/error
     models using repository conventions. Define JSON names and generic declarations for roots, addressable nodes,
     node kind, children, reference target, disabled reason, domain metadata, filters, supported sorts, and any
     backend-declared selection limit. Define stable opaque backend IDs that preserve the existing
     `(manifest_hash, source_file, source_row_ordinal)` identity without SQLite `rowid`, frontend-generated domain
     identity, or a new table. Define deterministic canonical selectable locations and non-selectable references for
     existing transposition links. Define `appears_in_my_games` as filtering against the accepted corpus selected by
     `SUBJECT_PLAYER_UUID`, with no authentication. Keep the normalized representation transport-only and leave the
     accepted opening/corpus tables unchanged.
   - **Focused proof:** `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/openings/test_contract.py -q`
     (bash tool timeout: 120000 ms) against temporary SQLite contract fixtures, proving strict shape, composite
     identity preservation, explicit node kinds, reference non-selectability, canonical/reference uniqueness, and
     fixed-corpus filter scope.
   - **Breakpoint:** Coordinator approval is required before Stage 2 if JSON names, opaque ID encoding, or the
     deterministic canonical/reference transposition rule cannot be derived without changing authoritative data or
     relationships.
   - **Escalate if:** The contract requires a generic database model, a new identity, collapsed memberships,
     changed source ownership, authentication, or a different product/API boundary.

2. **done - read-only opening provider API (ORDERED).**
   - **Ordered actions:** Implement the bounded `backend/app/features/openings/` feature after the Stage 1 gate.
     Open the existing database in read-only mode, validate the accepted catalog, relationship, recurrence, and
     corpus schema versions, query `opening_catalog`, `opening_parent_link`, `opening_transposition_link`, and the
     corpus-scoped recurrence projection, then translate authoritative facts into the normalized response. Apply
     text, ECO, and fixed-corpus appearance filters in the repository/database layer; retain backend default order
     and declared sort/limit metadata. Return appropriate 422, 503, and 500 error responses rather than successful
     application-level failures. Register only the new API router in `backend/app/main.py`; do not initialize or
     mutate the database.
   - **Focused proof:** `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/openings/test_api.py -q`
     (bash tool timeout: 120000 ms), covering complete normalized results, arbitrary-depth hierarchy, transposition
     references, all approved filters, fixed-corpus semantics, ordering, schema refusal, read-only behavior, and
     typed HTTP failures against temporary SQLite databases.
   - **Breakpoint:** None while the approved Stage 1 contract and existing-table ownership remain unchanged.
   - **Escalate if:** The API needs a database write, migration, runtime publication, a changed endpoint/contract,
     a new filter, a different corpus, or a relationship not represented by accepted S1-S4 data.

3. **done - generic rendered selector and interaction mechanics (ORDERED).**
   - **Ordered actions:** Implement the reusable component and types under the bounded design-system area using
     Headless Tree for hierarchy/focus/selection and Base UI for generic controls. Keep domain presentation in
     structured row slots, allow an optional custom escape hatch, support configurable self-contained or embedded
     shells, and support controlled state with convenience defaults. Implement single and multi-selection,
     visible eligible descendant traversal for group selection, unchecked/indeterminate/checked group state,
     selection recomputation when filters change, removal of filtered-out leaves, optional backend-declared maximums,
     reference non-selectability, generic commit descriptions, search/filter submission state, last-successful-tree
     retention during refetch, disabled selection while updating or failed, retry/error, and empty states. Use only
     existing design-system tokens and component styling conventions.
   - **Focused proof:** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/design-system/line-library/LineLibrary.test.tsx`
     (bash tool timeout: 120000 ms), covering controlled/uncontrolled state, single/multi-selection, tri-state
     groups, filtered visible-descendant semantics, references, disabled rows, commit descriptions, stale/error
     retention, empty/loading states, keyboard focus, and slot/shell behavior.
   - **Breakpoint:** None for interaction behavior already settled by the synthesis; preserve a later human
     Storybook visual review rather than inventing a new product visual direction.
   - **Escalate if:** Generic code must know opening/ECO/player semantics, generate domain identity, perform domain
     filtering, own downstream actions, or require a dependency beyond the already installed packages.

4. **done - opening Storybook specialization and typed API boundary (ORDERED).**
   - **Ordered actions:** Add the production-contract TypeScript client/runtime guards without wiring it into an
     application route or Storybook fetch. Add clearly labelled synthetic fixture data and an in-memory provider
     that deterministically simulates the opening filters, backend ordering, selection limits if declared, loading,
     stale refresh, failure, retry, empty results, disabled nodes, and transposition references. Supply opening row
     slots and the three approved filter scenarios, including the fixed accepted-corpus meaning of
     `appears_in_my_games`; do not present fixture IDs or values as authoritative production data. Add Storybook
     play assertions for selection, filtering, keyboard interaction, and generic commit reporting. Keep Storybook
     stories within the existing discovery glob where practical.
   - **Focused proof:** `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/design-system/line-library src/features/openings`
     (bash tool timeout: 300000 ms), covering the opening-specialized stories and their interaction assertions; and
     `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/openings/openingsApi.test.ts`
     (bash tool timeout: 120000 ms), covering strict production-response parsing and typed error mapping without a
     network request.
   - **Breakpoint:** Human Storybook review confirms that the rendered hierarchy, filters, row slots, states, and
     responsive shell are legible and accessible; user edits at this visual breakpoint are authoritative and must
     be incorporated before browser closeout.
   - **Escalate if:** A story calls the live API, requires an application route, claims fixture data is authoritative,
     adds an opening filter, or changes the generic selector contract.

5. **pending - focused browser proof and structural documentation route (ORDERED).**
   - **Ordered actions:** Add the Storybook-only browser spec and classify it in `tests/e2e/playwright.config.ts`
     so it starts only the Storybook server. Verify axe coverage, keyboard focus, no horizontal overflow at the
     selected responsive viewports, stale/error/empty states, and the opening specialization. Retain valid behavioral
     receipts, review the Plan and scoped changes, and route any stale
     `backend/README.md`, relevant frontend feature README, or E2E README maintenance to `readme-updater` after
      structural changes. Do not run an aggregate suite as part of this Plan.
   - **Focused proof:** `timeout 600s node_modules/.bin/playwright.cmd test --config tests/e2e/playwright.config.ts tests/e2e/line-library-storybook.spec.ts`
     (bash tool timeout: 600000 ms). Do not run Ruff, formatting, TypeScript-wide, ESLint, Prettier, source-size,
     build, aggregate, or other repository-maintenance checks in this Plan.
   - **Breakpoint:** Explicit human acceptance of the focused browser result is required before archival.
   - **Escalate if:** Behavioral proof fails because of the implemented behavior, or work requires an unrelated
     repair, route/API/data scope expansion, historical
     edits, or claiming runtime/database behavior not proven by the read-only API tests.

Stages are sequential; no stages run in parallel. The coordinator may split an oversized stage without changing
the approved outcome or requiring a new product, API, data, dependency, ownership, or acceptance decision.

## Progress and decisions

- **Stage 1:** done - strict normalized schemas use `roots`, keyed `nodes`, `filters`, `filter_apply_mode`, `sorts`,
  and `selection_limit`; nodes expose `id`, `kind`, `child_ids`, disabled state/reason, metadata, selection state, and
  reference targets where applicable. Stable `ol1_` IDs encode the full catalog composite identity. For each
  authoritative source-row identity in accepted transposition links, the lowest existing appearance by ply, UCI
  prefix, and exact position is canonical and other existing appearances are non-selectable references. The fixed
  corpus/no-auth boundary is explicit.
- **Stage 2:** done - `GET /api/openings/line-library` is registered with server-side `search`, `eco_from`,
  `eco_to`, `appears_in_my_games`, and `sort`; it validates accepted schema/classification versions, reads the
  catalog, hierarchy, transpositions, and fixed-corpus recurrence projection without mutation, and returns strict
  normalized results with typed HTTP failures.
- **Stage 3:** done - the split reusable component modules implement Headless Tree hierarchy/focus/selection,
  Base UI filter controls, structured/custom rows, panel or embedded shells, controlled/default state, single/multi
  selection, tri-state visible-descendant group behavior, limits, references, disabled reasons, generic commits,
  filter modes, and retained stale/error/empty/loading states without domain knowledge.
- **Stage 4:** done - strict production-response parsing and typed errors are covered without network requests;
  explicitly synthetic in-memory opening stories cover selection/commit, all three approved filters, limits,
  disabled/reference nodes, loading, stale refresh, retry failure, and empty results. Story discovery was extended
  without adding an application route or live API consumer.
- **Stage 5:** pending - focused proof retains valid earlier receipts and routes README maintenance to readme-updater when
  structural changes make existing documentation stale.
- **Decision:** Opening v1 `appears_in_my_games` is the existing accepted corpus selected by
  `SUBJECT_PLAYER_UUID`; authentication is explicitly out of scope. The API is production read-only, while the
  frontend has no application route or live API consumer.
- **Proof receipt (Stage 1):** `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/openings/test_contract.py -q`
  passed `7 passed in 0.24s` with bash tool timeout `120000 ms`. This supersedes an earlier six-test receipt
  invalidated by the final fixed-corpus and transposition-prefix refinement.
- **Proof receipt (Stage 2):** `timeout 120s .venv/Scripts/python.exe -m pytest backend/tests/features/openings/test_api.py -q`
  passed `9 passed in 0.58s` with bash tool timeout `120000 ms`. A bounded read-only TestClient smoke returned HTTP
  `200` with `4297` normalized nodes under the same finite timeout. Stage 1 remained valid because its code did not
  change.
- **Proof receipt (Stage 3):** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/design-system/line-library/LineLibrary.test.tsx`
  passed one file and `8` tests with bash tool timeout `120000 ms`. Backend Stage 1-2 receipts remain valid because
  no backend or dependency files changed.
- **Proof receipt (Stage 4):** `timeout 120s npm.cmd run test --prefix frontend -- --run --project=unit src/features/openings/openingsApi.test.ts`
  passed `6` tests with bash tool timeout `120000 ms`; `timeout 300s npm.cmd run test-storybook --prefix frontend -- --run src/features/design-system/line-library src/features/openings`
  passed `10` tests with bash tool timeout `300000 ms`; the scoped Prettier check passed. Stage 1-3 focused receipts
  remain valid because their implementation files were unchanged.
- **Maintenance note:** a separate TypeScript maintenance check previously reported an error in the Stage 3
  `LineLibrary.test.tsx`, and an attempted ESLint check found no repository `eslint.config.*`. Neither is Stage 5
  implementation proof or blocks this Plan; the separate complete test/fix workflow owns them.

## Proof

- Stage-specific contract, API, component, Storybook, and browser commands above all use explicit finite command
  wrappers and state finite bash tool timeouts in milliseconds.
- Temporary SQLite API fixtures must prove accepted-table reads, fixed-corpus filtering, composite identity
  preservation, strict errors, no writes, no sidecars, and no new schema objects. A bounded read-only smoke may be
  added only if runtime availability is required to verify the deployed endpoint; it must not publish or mutate the
  database.
- Storybook proof must cover the generic interaction contract and opening-specific display without calling the live
  API. Axe and browser assertions supplement, but do not replace, human visual/accessibility review.
- Passing proof remains valid until a later change affects its command, inputs, exercised behavior, configuration,
  dependencies, or environment. Stage 5 runs only focused evidence gaps or checks invalidated by its changes.

## Acceptance

The API returns authoritative existing opening data as a strict normalized tree with arbitrary-depth groups,
selectable lines/groups, non-selectable canonical transposition references, backend disabled reasons, declared
filters/sorts/limits, correct fixed-corpus appearance filtering, backend ordering, and appropriate HTTP failures.
It is read-only and does not add tables or mutate accepted data. Storybook visibly demonstrates the reusable
selector and opening specialization with synthetic fixtures: structured row slots, configurable shell, keyboard
hierarchy navigation, controlled/default state, single/multi-selection, tri-state current-visible eligible descendant
semantics, filter-driven selection recomputation, stale/error/empty/loading states, references, disabled rows, and
optional generic commit reporting. No application route, live frontend fetch, authentication, board behavior,
training behavior, repertoire mutation, or downstream action exists. Focused proof passes, the visual breakpoint is
accepted, and README maintenance is routed appropriately.

## Escalation boundaries

- Any inability to preserve `(manifest_hash, source_file, source_row_ordinal)` identity, accepted S1-S4
  relationships, or the one-canonical-location/reference transposition rule without a new data decision.
- Any request for a new database table, migration, source/import change, runtime database write, destructive action,
  authentication, authorization, player identity, or corpus other than the accepted `SUBJECT_PLAYER_UUID` corpus.
- Any change to `GET /api/openings/line-library`, its normalized contract, HTTP status semantics, filter scope,
  backend ordering, declared limits, or API ownership not approved at the Stage 1 gate.
- Any domain-specific logic or authoritative data in the generic frontend component; any client-side opening
  filtering; any fixture presented as production truth; any live API call from Storybook; or any application route or
  downstream action.
- Any lazy-loading or virtualization implementation in v1, extra opening filter, new dependency, or change to the
  installed Headless Tree + Base UI direction.
- Any uncertain SQLite schema/version, read-only access, response completeness, transposition mapping, accessibility
  behavior, visual acceptance, unrelated worktree preservation, README ownership, historical record, commit, push,
  `--fix`, or closeout acceptance.

## Visible result

> A human can call the read-only opening Line Library API and inspect a Storybook picker that browses authoritative-shaped opening scenarios with correct hierarchy, filters, selection, transposition, loading, and failure behavior without any application route or downstream action.
