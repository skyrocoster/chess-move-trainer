# Frontend server-state caching direction

Date: 2026-09-14

## Goal

Reuse recent backend results inside the running React application where that improves navigation and prevents duplicate requests, while keeping updates fresh and avoiding persistent browser storage.

## Current-state facts considered

- TanStack Query v5 is already installed and a `QueryClientProvider` exists in `frontend/src/main.tsx`.
- Only the health page currently uses TanStack Query, with its cache explicitly disabled. Other features use handwritten clients with `useEffect`, `useState`, and `AbortController`.
- The opening selector and training retrieval fetch multiple pages and repeat the work when their inputs are revisited.
- Two position-related frontend features can request the same position-insight data independently.
- Analysis observation is polled while work moves through queued, running, and ready states.
- Preferred-move and training-answer mutations make related read results stale.

## Approved direction

1. Use the existing TanStack Query dependency rather than adding another cache library or building a general custom cache.
2. Keep server-state data in application memory only. Do not persist API results to `localStorage`, `sessionStorage`, IndexedDB, or another browser-persistent store.
3. Prioritize:
   - the opening catalogue;
   - game details keyed by game UUID;
   - preferred moves keyed by canonical position;
   - shared position-insight requests keyed by normalized position inputs;
   - training-requirement results keyed by the complete normalized filter set;
   - games-list pages only when a frontend consumer exists.
4. Invalidate affected queries immediately after successful training answers, preferred-move changes, and analysis requests.
5. Treat analysis observation as active polling rather than long-lived fresh data. TanStack Query may coordinate and deduplicate that polling, but cached observations must not suppress required queued/running checks.
6. Do not cache errors as valid data. Health caching has no priority because the endpoint is already inexpensive.
7. Adopt TanStack Query incrementally rather than rewriting unrelated frontend state at once.

## Reasons

- Memory-only caching improves repeat navigation and concurrent-request deduplication without showing data retained from an earlier browser session.
- TanStack Query already provides query keys, in-flight deduplication, cancellation, freshness windows, garbage collection, mutation invalidation, and polling.
- Feature-specific adoption keeps behavior changes reviewable and allows existing loading, empty, error, retry, and cancellation behavior to be preserved.

## Exclusions

- No browser-persistent API cache.
- No service worker, HTTP `Cache-Control` change, or offline mode.
- No additional server-state library.
- No caching of errors as successful results.
- No backend implementation changes in the frontend Plan.
- No speculative games-list frontend integration while there is no current caller.

## Coordination note

The backend API latency and caching Plan under `docs/plans/active/api-latency-games-query-and-cache/` is being executed separately. Frontend assessment and planning must treat that work as read-only, avoid editing its files, and state any dependency on its final endpoint behavior without assuming unfinished changes are already available.

This record is directional evidence for assessment and Plan writing. It is not authorization to implement frontend changes.
