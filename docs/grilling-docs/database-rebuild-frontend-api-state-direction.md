# Database rebuild frontend API-state direction

> **Status:** confirmed on 2026-09-09
> **Purpose:** Durable frontend direction for the database-rebuild consumer migrations, beginning with
> `CONSUMER-01`.
> **Authority:** This records decisions reached with the user. It is not a Plan, implementation authorization,
> migration acceptance, or permission to move any consumer other than an independently approved slice.

## Goal

Adopt the generated clean API without creating a second handwritten client architecture or prematurely building
facilities for later workflows. The frontend should gain request-lifecycle support as each consumer needs it while
remaining easy to understand and change.

The governing rule is:

> Generate boring contract glue; introduce feature behavior only when the feature being migrated needs it.

## Responsibility boundary

- FastAPI and the curated OpenAPI document define the HTTP contract.
- HeyAPI remains responsible for generated TypeScript types, operation functions, and the fetch client.
- TanStack Query is the normal React-side manager for server-owned data: request state, temporary reuse, cancellation,
  deliberate polling, and refresh after writes.
- React components remain responsible for presentation and ordinary local interface state.

TanStack Query does not replace HeyAPI, become another database, or justify a generic application service layer.

## Incremental adoption

TanStack Query is the standard direction for consumer migrations, but only the capabilities needed by the current
consumer are introduced. `CONSUMER-01` is a small vertical proof, not an authorization to construct the later analysis,
position, or preferred-move architecture.

HeyAPI should initially generate only the basic TanStack query keys and query options. Generated React hooks,
infinite-query machinery, mutation machinery, and other optional helpers remain disabled until a migrated consumer has
a concrete need for them.

A simple feature should use the generated query option directly. No handwritten hook or wrapper is created merely to
forward arguments. A feature-owned helper is appropriate only when it performs a real job, such as coordinating
analysis request and polling behavior or removing demonstrated repetition.

## Predictable network behavior

Project defaults should be conservative:

- no automatic retry;
- no refetch merely because the browser regains focus;
- no refetch merely because connectivity returns; and
- ordinary fetching when a screen mounts remains available.

Polling, retries, prefetching, and other background requests are explicit feature decisions introduced only when the
owning workflow needs them.

## Response and error handling

The generated OpenAPI types are the normal frontend contract. The frontend does not add Zod, Valibot, or a general
runtime-validation layer now.

Focused runtime checks remain appropriate when the interface depends on a critical assumption. In `CONSUMER-01`, a
successful health response must still contain status `"ok"`; malformed success data must not be presented as healthy.
HTTP and transport failures must enter the feature's ordinary error state. No general application error hierarchy is
introduced by this slice.

The Status screen uses one stable, friendly backend-unavailable message for a failed health request. Preserving a
numeric HTTP status or exposing a raw backend response does not justify custom translation machinery for this simple
consumer.

## Temporary data reuse

TanStack Query may reuse recently fetched answers in memory while the application is open. API data is not persisted
to browser storage and is cleared by a full page reload. There is no universal guessed freshness duration; each feature
sets a freshness rule only when its behavior requires one.

Every response-shaping input must participate in request identity. For example, position insight varies by FEN,
trainer color, and date. Exact query-key construction remains generated implementation detail.

## Navigation and writes

Moving between game plies remains immediate and local after game detail has loaded. The complete clean game-detail
response contains the ordered occurrence timeline needed for board navigation. Position insight is requested only for
the currently selected FEN and updates independently; revisiting a position may reuse its in-memory answer. Adjacent
plies are not prefetched unless later evidence shows a real responsiveness problem.

The default write policy is server confirmation followed by refreshing the affected read. The frontend does not
pretend that a write succeeded before the backend answers and does not perform optimistic cache edits now. This keeps
backend-owned preferred-move interval normalization authoritative. A later consumer may propose optimistic behavior
only for a demonstrated user-experience need.

## Testing direction

`CONSUMER-01` uses the existing focused frontend test tools and bounded real-path proof. MSW is not added merely to
simulate one health request. It may be reconsidered when a consumer such as analysis polling genuinely needs a
multi-request server conversation in tests.

React Query Devtools, persistent caching, runtime-schema libraries, neighbouring-position prefetch, and other optional
facilities are also deferred until they have a concrete job.

## `CONSUMER-01` consequence

The focused assessment should establish only the minimum shared TanStack provider and narrow HeyAPI generation needed
to move the Status health request to generated `getHealth()`. Status retains its explicit loading, success, and error
presentation, cancellation, critical `"ok"` check, and one-consumer scope. Automatic network behavior must not silently
change, and no other production API usage may migrate.

Provider placement, exact generator configuration, generated file changes, cancellation wiring, focused proof, and
whether the slice warrants a direct change or a focused Plan remain assessment work.
