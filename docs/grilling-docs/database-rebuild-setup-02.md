# Database rebuild SETUP-02 API tooling

> Direction approved on 8 September 2026. This is the SETUP-02 grilling handoff. It records the
> agreed API-tooling outcome and boundaries; it is not a Plan and does not authorize implementation,
> application integration, database activation, API-01 through API-04, cutover, cleanup, or deletion.

## Outcome

Put the minimum correct tooling in place so a future FastAPI/Pydantic contract can produce clear,
typed TypeScript request functions with one explicit generation command. Keep the workflow simple,
quick to use, low in boilerplate, and neutral about the contracts that will eventually read and edit
`data/database/chess.db`.

SETUP-02 is tooling work only. It does not design ahead. In particular, the existing API-01 through
API-04 roadmap rows remain capability placeholders rather than approved URLs, request models,
response models, error contracts, database-access patterns, or application architecture.

## Settled tool direction

- FastAPI routes and Pydantic models are the Python source of truth.
- FastAPI's generated OpenAPI description is the bridge from Python to TypeScript. A separately
  hand-authored OpenAPI contract is not introduced.
- `@hey-api/openapi-ts` generates TypeScript types, API functions, and a self-contained vendored
  `fetch` client through its built-in bundled client plugin.
- The user initially installed both `@hey-api/openapi-ts` and `@hey-api/client-fetch` locally in the
  frontend workspace. Assessment against the installed `@hey-api/openapi-ts` version proved that its
  default bundled output neither imports nor otherwise requires the separate `@hey-api/client-fetch`
  package. The user therefore approved removing that redundant dependency during SETUP-02. No API
  generation package is installed globally.
- Generated consumers are plain asynchronous functions, not React hooks. SETUP-02 does not add
  React Query or another request-state framework.
- One explicit repository command exports the selected FastAPI OpenAPI contract and regenerates the
  TypeScript client. Generation does not require a separately running backend server and is not
  hidden inside every frontend build.
- The generated OpenAPI and TypeScript outputs are checked in so the current generated contract is
  available after checkout and changes are visible. Generated files are not edited by hand.
- Generated operation names are controlled with explicit, stable FastAPI `operation_id` values. A
  future operation can therefore generate a concise name such as `getGame()` without tying that
  public name to an internal Python function name.
- The generated client has one central place for its base configuration rather than repeating the
  API base URL in every feature.

No separate API-management or request-collection application is needed. FastAPI's existing
interactive documentation is sufficient for manual inspection and calls. SETUP-02 does not add
Bruno, Postman, an API gateway, generic CRUD tooling, an ORM, or another API framework.

## Sole proof contract

The checked-in SETUP-02 proof contract contains only the existing `GET /api/health` operation. That
operation receives the explicit operation ID `getHealth`; the generated TypeScript surface contains
the corresponding response type and plain asynchronous `getHealth()` request function.

The proof must establish the real Python-to-OpenAPI-to-TypeScript path and a successful call returning
the existing health result:

```json
{"status":"ok"}
```

No other currently registered endpoint belongs in the SETUP-02 generated contract or client. In
particular, SETUP-02 does not generate a durable snapshot of the legacy database-backed APIs or the
existing Opening Line Library endpoint. The production frontend does not import or use even the
generated health function in this outcome; the health operation is only a small real contract used
to prove the toolchain.

## TypeScript response boundary

Future generated clients will trust the FastAPI/Pydantic response contract. SETUP-02 does not install
Zod or another browser-side schema validator, generate duplicate runtime response validation, or
preserve the existing handwritten exact-key validators as a new client convention. HTTP and network
failure behavior for future application APIs remains a contract decision for the feature that needs
it; SETUP-02 does not invent a shared future error architecture.

## Relationship to the current APIs

Current routes, services, repositories, frontend request modules, and tests are evidence of present
capabilities, not a scaffold to preserve. The current backend has useful separation between HTTP,
service, and repository concerns, but it also has legacy database coupling, inconsistent connection
ownership, repeated HTTP error adapters, and frontend contract duplication. SETUP-02 does not repair
or standardize those application structures.

Every application API is expected to be reconsidered during the later rebuild. Future work may keep,
replace, or reorganize an observed pattern only when that feature's settled requirement justifies it.
The generation tooling remains neutral and can describe whatever future contract is approved.

## Exclusions

- No API-01, API-02, API-03, or API-04 assessment, design, Plan, or implementation.
- No promise to retain a current endpoint path or request, response, or error shape.
- No conversion of any existing frontend API call to the generated client.
- No generated client for current database-backed or Opening Line Library endpoints.
- No generic table API or CRUD surface over `chess.db`.
- No database-package integration, database-path change, physical database activation, or legacy
  database fallback, cleanup, or deletion.
- No refactor of router, service, repository, connection, error, or response-validation code merely
  to prepare for possible future work.
- No dependency beyond `@hey-api/openapi-ts`; the already installed but proven-redundant
  `@hey-api/client-fetch` package is removed from the frontend manifest and lockfile.
- No new authentication, authorization, rate limiting, versioning policy, security layer, API gateway,
  runtime schema-validation library, React request framework, or external API workspace.
- No use or modification of the legacy `setup.ps1` as part of this outcome.
- No broad maintenance suite, commit, push, branch, worktree, stash, or unrelated record change.

## Implementation handoff

A later approved SETUP-02 implementation may choose the smallest cohesive file layout and focused
proof needed to realize the decisions above. It may remove the approved redundant
`@hey-api/client-fetch` dependency. Its acceptance must show that one explicit command
reproducibly exports only the approved health proof contract, generates the checked-in plain
TypeScript client, and that `getHealth()` can complete a finite real call with the typed successful
result. Tool configuration details may vary when required by the installed package APIs, but any
change that introduces another dependency, includes another current endpoint, changes application
behavior, or settles a future API contract must return to the coordinator and user.
