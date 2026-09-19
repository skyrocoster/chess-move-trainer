# Core data and worker review

Scope: `src/chess_move_trainer/database/`, the generated SQLite schema reference,
and `src/tools/graphify_catalogue.py`.

## P1 — `positions` and `openings` have a real import cycle

Graphify reports multiple cycles through
`openings/recognition.py -> positions/__init__.py -> positions/insight.py -> ...
-> openings/recognition.py`. The immediate cause is visible in
`openings/recognition.py` line 14, which imports canonical position values from
9–30), which depend on opening recognition.

This works only while Python import timing happens to be favorable. It makes a
small import change capable of causing a partially initialized module failure.

**Change candidate:** put canonical position types/functions in a dependency-low
module and import it directly (`positions.canonicalization` or a neutral
identity module). Narrow `positions/__init__.py` to a deliberate public API that
does not load feature services. Add an import-graph test that rejects cycles.

**Tools:** import-linter or Grimp, `pydeps`, and the existing Graphify catalogue
as a review aid. Run a fresh-interpreter import test for each public package.

## P1 — Opening recognition reloads and validates the entire catalogue per lookup

`lookup_fen()` calls `_load_routes()` for every lookup, then builds a complete
endpoint map. `_load_routes()` reads all routes and moves, validates every row,
and replays every route (lines 149–246); `lookup_fen()` then replays matched
routes again (lines 68–94). This is defensively correct but scales with the full
opening catalogue for a request that asks about one FEN.

**Change candidate:** measure first. If the catalogue is large, move the exact
endpoint lookup and validation into a bounded SQL query with supporting indexes,
or build an immutable, versioned read model that is atomically swapped after
publication. Preserve corruption detection with a validation command rather
than making every request perform a full audit.

**Tools:** SQLite `EXPLAIN QUERY PLAN`, pytest benchmark fixtures, py-spy or
pyinstrument, and Hypothesis tests comparing the optimized path to the current
reference behaviour.

## P1 — Schema compatibility is a high-fan-out choke point

Graphify identifies `_assert_compatible_schema()` and
`SchemaIncompatibleError` as the two most connected core symbols (69 and 66
edges). The generated `data/database/schema.md` shows a single v2 SQLite schema
with no triggers/views and many readers that independently require compatibility.
This concentration means schema evolution will create a large, easy-to-miss
regression surface.

**Change candidate:** write an explicit schema ownership and migration policy:
which package owns each schema change, compatibility windows, upgrade/rollback
behaviour, backup expectations, and a fixture for every historical supported
version. Keep one canonical DDL owner, but replace repeated ad-hoc compatibility
checks with a small connection/session factory that reports version and reason.

**Tools:** Alembic only if it fits the intentionally explicit SQLite lifecycle;
otherwise a tested in-house migration ledger. Use `sqlite3` integrity checks,
property-based migration tests, and `openapi-diff` when schema changes affect
responses.

## P1 — Stockfish supply-chain verification is weaker in Docker than in Python

`backend/Dockerfile` downloads a release tarball by URL and selects the first
`stockfish*` file returned by `find` (lines 6 and 17–26). It verifies the
reported engine version, but does not pin the base image by digest or verify the
archive checksum/signature. The Python provisioning code has a checksum-oriented
boundary according to Graphify, so the two installation routes offer different
assurance.

**Change candidate:** pin image digests where operationally acceptable, pin the
Stockfish artifact hash (and architecture), use a deterministic extraction path,
and retain the version check. Document the update procedure so a deliberate
engine upgrade changes URL, hash, expected identity, benchmark baselines, and
tests together.

**Tools:** Trivy or Docker Scout, Syft/Grype SBOM scanning, `hadolint`, and a
Docker build test that rejects an altered archive.

## P2 — Public barrels are too broad for a dependency-sensitive package

`positions/__init__.py` re-exports 60+ values from canonicalization, insight,
repository, scoring, discovery, and answer modules. It makes dependencies easy
to write but hides runtime loading cost and caused the cycle above. The new
Stockfish README correctly calls out three public compatibility modules; use
that same explicit-boundary standard for `positions`, `games`, and `openings`.

**Change candidate:** document a small stable public surface, move internal
imports to sibling modules, and deprecate only the re-exports that create cycles
or blur ownership. Avoid a breaking cleanup without a compatibility plan.

**Tools:** import-linter, Pyright export checks, and a fresh-process public API
smoke test.

## P2 — Graphify is valuable but the generated report is hard to act on

`src/tools/graphify_catalogue.py` is 568 lines and embeds output lifecycle,
path security, provenance rewriting, extraction, clustering, and preservation
logic. Its reports list hundreds of anonymous “Community N” entries; the
repository report has 252 communities, which provides little ownership guidance.
The documented refresh command uses Unix `timeout` even though this is a
Windows-focused repository, while the Python subprocess timeout is 900 seconds.

**Change candidate:** split the generator into validation, artifact I/O, and
orchestration modules; use a Windows-valid documented command or invoke Python
with an explicit wrapper; and produce a compact actionable report containing
cycles, changed hubs, boundary violations, and owner/path links. Preserve the
current strict output-path validation before refactoring.

**Tools:** Ruff/Pyright, unit tests already present under `tests/graphify/`,
mutation testing for path-validation branches, and Graphify diff snapshots.
