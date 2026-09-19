# Backend review

Scope: `backend/app/`, its API-facing tests, and the backend-to-database
boundary. This is a code review, not a design review.

## P0 — Single-flight requests can wait forever

`backend/app/caching.py:get_or_compute()` waits on
`inflight.condition.wait()` with no timeout (lines 276–278). A stuck database
read or a defect in a computation leaves every matching request blocked. This
conflicts with the repository rule that waits must be finite. The cache catches
`BaseException` to notify waiters, but that does not help when the leader never
returns.

**Change candidate:** give each single-flight operation a deadline, publish a
typed timeout failure, remove the failed in-flight entry, and instrument leader
duration and waiter count. Do not cache timeout responses. Prove that a stuck
leader releases waiters and a later request can become leader.

**Tools:** pytest with a controlled blocking callable; Locust or k6 to prove the
endpoint does not exhaust workers under a same-key stampede; OpenTelemetry
spans/metrics for cache leader and wait durations.

## P1 — Broad exception translation hides production failures

The routers commonly use `except Exception` and return a generic 500 or 503:
for example `position_training_requirements/router.py` lines 197 and 252,
`preferred_moves/router.py`, `openings/router.py`, and `games/router.py`.
Expected domain exceptions are mapped, but unexpected errors are discarded with
no log, error identifier, or traceback. Returning 503 for schema and storage
errors also makes an incompatible database indistinguishable from a temporary
outage.

**Change candidate:** centralize exception handling in FastAPI exception
handlers. Keep stable public error codes, log the original exception with a
request ID, distinguish unavailable dependency from incompatible schema, and
ensure programmer errors remain visible in development. Never return raw
database paths, SQL, FEN, PGN, or environment values to clients.

**Tools:** structlog or standard-library JSON logging, Sentry or equivalent
error collection, Semgrep/Ruff rules that flag broad catches, and API tests for
every public error code.

## P1 — Cache invalidation is coarse and relies on filesystem metadata

Every tracked database signature change clears all cache namespaces in
`_refresh_signature_locked()` (lines 121–133), including unrelated games,
openings, and training data. A signature combines size, mtime, device, inode,
and SQLite sidecars. This is safe-minded but can create a recomputation storm on
busy WAL traffic and can still be unreliable across bind mounts or coarse file
timestamp filesystems. `clear_caches()` does not clear `_last_signatures`, which
makes invalidation history implicit rather than observable.

**Change candidate:** establish explicit, per-resource versions at the write
boundary (or a small version table), invalidate only the affected namespace,
and expose cache hits/misses/evictions for local diagnosis. Keep a defensive
filesystem fallback only if it is needed for external writers.

**Tools:** `EXPLAIN QUERY PLAN` for version reads, pytest concurrency tests,
filesystem matrix tests on the Docker bind mount, and Prometheus/OpenTelemetry
cache metrics.

## P1 — Environment configuration fails closed but silently

`get_training_requirement_policy()` in `backend/app/dependencies.py` converts
invalid configuration into `None`, then routes return a generic 503. Operators
cannot tell which variable is bad, and health reports only `{"status":"ok"}`.
`get_rebuilt_database_path()` accepts an unvalidated path from the environment.

**Change candidate:** validate configuration once at process startup or provide
a dependency/readiness report that names the invalid setting without revealing
secrets. Resolve and validate the database parent/path according to the
application's supported deployment model. Keep `/api/health` simple if needed,
but add a protected or local readiness diagnostic for operators.

**Tools:** Pydantic Settings, startup tests using invalid environment values,
and Docker Compose health/readiness tests.

## P2 — Response construction repeats domain calculations

`_item_response()` calls `item.public_dict()` five times per training item
(`position_training_requirements/router.py` lines 61–77). Even if the current
method is cheap, this couples a transport mapper to a repeated opaque
calculation and is an easy source of inconsistent fields if it later changes.

**Change candidate:** obtain the immutable public mapping once, or expose a
typed transport-ready projection from the domain layer. Add a test that the
projection is evaluated once per item if evaluation is non-trivial.

**Tools:** pytest spy test; py-spy or pyinstrument before optimizing a real
large result page.

## P2 — CORS and exposed headers are manually maintained

`backend/app/main.py` contains a fixed frontend origin, method list, header
allow-list, and a single exposed header. This is appropriate for the current
local service, but a new request header, frontend port, or deployed origin can
fail in the browser without an API test. The generated client has no clear
documented deployment configuration contract beyond `VITE_API_BASE_URL`.

**Change candidate:** express supported origins and exposed headers as validated
configuration, document the local default, and add a browser/API preflight test
for each non-simple request used by the client.

**Tools:** Playwright network assertions, FastAPI `TestClient` OPTIONS tests,
and Schemathesis for normal API inputs (not CORS itself).
