# Frontend review

Scope: `frontend/src/`, generated OpenAPI consumption, and frontend test
configuration. This review intentionally excludes visual design.

## P0 — The current conditional-hook pattern is unsafe

`useAnalysisState()`, `useMoveResponseDistributionState()`, and
`usePositionContextState()` select different hook implementations by comparing a
client argument to a default function. The current worktree explicitly suppresses
`react-hooks/rules-of-hooks` in the first two branches, for example
`frontend/src/features/analysis/analysisState.ts` lines 423–435. The comment
claims changing the client “remounts this feature”, but changing a prop does not
remount a React component. If a caller changes that client while the component
remains mounted, React can receive a different hook sequence and corrupt state
or throw.

**Change candidate:** replace conditional hook invocation with a wrapper that
selects between two keyed child components (so React actually remounts), or use
one common hook implementation with injected I/O. Remove the lint suppressions
only after the hook order is structurally unconditional. Add a test that rerenders
with a different client and confirms clean state plus no console hook-order
warning.

**Tools:** ESLint React Hooks with suppressions prohibited in application hooks,
React Testing Library rerender tests, and Playwright console-error assertions.

## P1 — Analysis state is duplicated and has competing state machines

`analysisState.ts` is 436 lines with `useDefaultAnalysisState` and
`useInjectedAnalysisState`. Both manage request controllers, pending flags,
position changes, error mapping, and polling, but one combines TanStack Query
with retained observations and invalidation while the other runs manual timers.
The two implementations will drift; the P0 branch split makes this debt more
visible rather than solving it.

**Change candidate:** define one explicit analysis state-machine contract and
move transport/query adapters behind it. Ensure abort, poll limit, position
change, retry, stale response, and request-after-unmount transitions are tested
once against both transports. Do not change user-facing behaviour during the
extraction.

**Tools:** XState/Stately only if it reduces complexity rather than adding
another abstraction; otherwise pure reducer tests, fake timers, MSW, and
React Testing Library.

## P1 — Generated-client errors have an acknowledged type hole

The checked-in generated fetch client says “TODO: we probably want to return
error and improve types” at `src/api/generated/client/client.gen.ts:214`. The
generated client returns `undefined` for `responseStyle === "data"` after a
non-throwing failure. Handwritten feature adapters must reconstruct failures,
and a generator upgrade can silently change that behaviour.

**Change candidate:** configure generation for a discriminated success/error
result if the library supports it, or provide one handwritten boundary adapter
that converts generated responses and thrown values into an app-owned result
type. Keep generated files untouched except through regeneration. Add contract
tests for each HTTP error body and malformed response.

**Tools:** `openapi-diff`, Schemathesis against the local service, MSW for
frontend failure cases, and a generator-version update test/snapshot.

## P1 — The handwritten API barrel is a manual contract mirror

`src/api/client.ts` re-exports a long hand-maintained list of generated
operations and types (138 lines). It is intended to protect the app from
generated-file replacement, but it can omit a newly needed operation or retain
a removed one without a compile failure at the boundary. The OpenAPI generator
configuration has no package script for regeneration and no documented command
that refreshes the checked-in `openapi.json` from the served backend.

**Change candidate:** make API generation a named local command with finite
timeouts and document its inputs/outputs. Prefer a narrow feature-owned facade
over a global type re-export list, and add a test that compares the public facade
to intentional allowed generated exports.

**Tools:** `@hey-api/openapi-ts` in an npm script, `openapi-diff`, TypeScript
build checks, and the existing `generatedSurface.test.ts` extended as a contract
gate.

## P2 — Runtime configuration is build-time and undocumented for deployments

`src/api/client.ts` reads `VITE_API_BASE_URL` and otherwise hard-codes
`http://localhost:5666`. Vite replaces this value at build time. A container
cannot normally point an already-built frontend at a different backend without
a rebuild, and the exact supported environment variables are not in the root
README.

**Change candidate:** document the build-time contract now. If runtime
configuration is needed later, load a validated same-origin configuration file
at startup rather than exposing arbitrary URL construction throughout features.

**Tools:** Vite environment schema validation, Docker smoke tests with an
alternate base URL, and Playwright request assertions.

## P2 — Test configuration suppresses a browser diagnostic globally by message

`frontend/vitest.config.ts` lines 54–65 ignores one exact ResizeObserver error
for every Storybook test path. This is narrow compared with a blanket ignore,
but a matching real regression will be hidden and the condition depends on an
internal Vitest property (`VITEST_TEST_PATH`).

**Change candidate:** isolate the known library behaviour in the affected story
test/setup or add a post-test assertion that the expected fixture caused it.
Review it whenever Vitest, Storybook, or the resizable-panel dependency changes.

**Tools:** Vitest upgrade canary, Playwright Storybook smoke tests, and a
console-message allowlist that reports unexpected messages.
