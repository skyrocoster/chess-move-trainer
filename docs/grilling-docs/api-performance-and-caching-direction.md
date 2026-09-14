# API performance and caching direction

Date: 2026-09-14

## Goal

Address the measured backend API delays without using caching to hide an unnecessarily expensive cold request.

## Evidence considered

- The real games-list benchmark under `docs/benchmarks/API/` took about 88.5 seconds to return 50 of 12,710 games.
- The current games search loads and processes the full corpus before filtering, ordering, and pagination. Much of the cost comes from constructing and validating chess positions for every stored occurrence.
- A response cache by itself would make only repeated identical requests fast. A first request, a different page, or a different filter could still take about 88 seconds.
- Training-requirement requests take about 5.7–6.0 seconds, while the openings list takes about 321 milliseconds. These are candidates for safe repeated-read caching.

## Approved direction

1. Optimize the games search and pagination path before relying on caching.
2. Preserve existing filters, totals, ordering, response fields, statuses, and edge cases.
3. Require the real cold games-list median on the same 12,710-game database to be no more than 1.5 seconds.
4. Start without a database schema change, migration, or new index. If the target cannot be reached without one, stop and return for a new decision.
5. Add bounded, process-local backend caching for safe successful reads, including training requirements and the opening catalogue.
6. Decide whether to cache games from the post-optimization measurements; do not add it when the optimized query is already inexpensive enough that caching has little value.
7. Invalidate backend cache entries after relevant successful writes and when the selected database file changes.
8. Do not add browser caching or `Cache-Control` caching headers. Backend-controlled caching is sufficient and avoids a browser showing stale information after a write.

## Reasons

- Cold-query optimization addresses the delay every user encounters, not only repeated requests.
- Backend-only caching targets the expensive repeated work while keeping freshness under application control.
- Preserving the current database schema keeps this first change bounded. Schema or index work can be considered separately if measurements prove it necessary.

## Exclusions

- No frontend changes.
- No Redis, shared cache service, disk cache, or multi-worker cache design.
- No caching of failed responses, writes, health checks, or rapidly changing analysis/queue responses.
- No response-contract changes.
- No database schema, migration, or index change without another user decision.

## Remaining uncertainty

- The optimized games-query latency is not known until implementation is benchmarked. If it exceeds 1.5 seconds, the implementation must stop rather than silently expand into schema work.
- Games-response caching is conditional on the measured post-optimization benefit.

This record is directional evidence for Plan writing. It is not authorization to implement the Plan.
