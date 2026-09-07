# DB-08A Lichess opening-source acquisition, configuration examples, and DB-09 command inventory - five fixed opening files can be safely fetched from one pinned upstream commit and published into a local source directory, with examples and a durable DB-09 command inventory

> **Status:** completed - all five stages accepted; focused offline proof passed.

- **Read trigger:** Read before any DB-08A Lichess acquisition implementation or focused DB-08A proof.
- **Upstream:** The coordinator-approved [DB-08A tool-surface handoff](../../../grilling-docs/database-rebuild-db-08a.md), especially "Planned change: Lichess opening-source acquisition" and "Boundaries and sequencing", is the binding behavior authority and now records the final Windows publication decision. The [database-rebuild master plan DB-08A and DB-09 envelopes](../../../master-plans/database-rebuild/database-rebuild.md) govern sequencing, the "no `scripts/` canon" boundary, and the DB-09 gate. The coordinator-approved PLAN-CANDIDATE assessment narrowed the scope and path selection. The accepted DB-03, DB-04, and DB-08 Plans are historical contract and retained-proof evidence only.

## Outcome

An operator can run `python -m chess_move_trainer.database openings acquire --source-dir PATH` to refresh the local five-file Lichess opening catalogue (`a.tsv` through `e.tsv`) from the fixed canonical upstream `https://github.com/lichess-org/chess-openings` (CC0 1.0). Each run resolves the upstream's latest default-branch state once to one immutable commit, retrieves exactly the five files from that commit, validates the complete staged set through the accepted DB-04 strict source service, and publishes it into the explicit source directory that `openings import --source-dir` consumes. A handled retrieval, validation, publication, or interruption failure restores the prior usable set; unchanged content is a zero-write idempotent no-op; the resolved commit is reported but never persisted. The same slice adds safe placeholder-only example YAML configuration files and a durable DB-09 lifecycle/legacy-tool command inventory, so DB-09 can proceed using only the rebuilt package and supported CLIs with no `scripts/` participation.

The accepted Chess.com `--month` direct change is upstream context, not an implementation stage of this Plan.

## Scope

- **Included:** A package-owned Lichess acquisition service with its own injectable transport; fixed host and URL policy; default-branch-to-one-commit resolution; exact five-file retrieval from the resolved commit; whole-set strict validation before publication; staged per-file atomic publication with prior-byte retention and rollback; idempotent unchanged-content handling; interruption and failure preservation; cleanup of all staging artifacts; result model and thin Typer command wiring; example YAML configuration files under `docs/examples/`; the durable DB-09 command inventory document with bounded flowchart updates; focused offline proof.
- **Expected areas:** `src/chess_move_trainer/database/openings/acquisition.py` (new); `src/chess_move_trainer/database/openings/__init__.py` (public exports only); `src/chess_move_trainer/database/cli.py` (one thin `openings acquire` command); `tests/database/openings/test_acquisition.py` (new) and `tests/database/openings/fixtures/` (new synthetic non-personal fixtures); focused additions to `tests/database/test_cli.py`, `tests/database/test_package_boundary.py`, and `tests/database/test_source_boundary.py`; `tests/database/test_configuration_examples.py` (new) and `tests/database/test_command_inventory.py` (new, small documentation consistency); `docs/examples/database-games.example.yaml`, `docs/examples/database-rebuild.example.yaml`, and `docs/examples/README.md` (new); `docs/flowcharts/database-command-inventory.md` (new) with bounded updates to `docs/flowcharts/database-toolchain.md`, `docs/flowcharts/database-operator-journeys.md`, and `docs/flowcharts/README.md` only where routing or wording is stale.
- **Windows publication decision (user-settled; state it plainly):** retrieve and validate all five files before publication; atomically replace each fixed file while retaining the prior bytes; any handled retrieval, validation, publication, or interruption failure restores the prior usable set; an abrupt process or machine crash during the swaps may temporarily leave mixed revisions, which an idempotent rerun repairs. Windows cannot atomically replace an existing nonempty five-file directory in one operation, so this practical staged behavior is accepted. The Plan must not claim literal whole-directory atomicity or invisibility to concurrent readers, and must not add versioned directories, a current pointer, a manifest, source history, or importer changes.
- **Excluded:** Any schema/DDL change; manifests, source-history, audit, run/failure, or provenance persistence; configurable upstream, branch, mirror, or revision input; new dependencies (pinned `httpx` 0.28.1 suffices); live-network proof; an opening-acquisition YAML config file (the fixed-source command needs only explicit CLI inputs); changes to `openings import/lookup/replay` behavior, `rebuild refresh` (stays offline), the Chess.com tool and raw ledger, preferred moves, Stockfish, or analysis; application/backend/frontend/API work; DB-09 real-data proof; cutover and old-database work; legacy script cleanup (RETIRE-01 owns it); commits or pushes; and re-implementation of the accepted Chess.com `--month` change.

## Stages

Stages are sequential; no parallel stages. The coordinator may split an oversized stage without changing the outcome. Test-first work is used within each stage, but a stage must not require tests for behavior owned by a later stage. A passing proof item remains valid until a later change affects its command, inputs, exercised behavior, configuration, dependencies, or environment; later stages run only missing or invalidated proof.

### 1. completed - Package boundary, transport model, CLI contract skeleton, and synthetic fixtures

**Ordered actions**
1. Add `openings/acquisition.py` with ordinary typed values: fixed constants (repository `lichess-org/chess-openings`, the two pinned hosts `api.github.com` and `raw.githubusercontent.com`, the fixed file names `a.tsv`–`e.tsv`, and the exact URL templates); an injectable transport protocol with `get_json(url, *, timeout)` for commit resolution and `get_text(url, *, timeout)` for file retrieval; an `httpx`-based production adapter (pinned `httpx`, `raise_for_status`, finite timeout); `OpeningAcquisitionError`; and a frozen `OpeningAcquisitionResult` model (resolved commit, published files, unchanged files, failures with subject and message, `completed` property). The module must not import `games`, `scripts`, `backend`, or legacy code, must not open SQLite, and must not persist anything.
2. Add the result semantics now: resolution/retrieval/validation failures return a failure result without publication; publication uses the Stage 3 contract but its module-level shape (prior-byte snapshot, per-file atomic swap helper, rollback hook, staging cleanup) may already exist unexercised. Keep business rules out of `cli.py`.
3. Register `openings acquire` in `database/cli.py` with the settled option surface: `--source-dir PATH` (required explicit target directory, the same surface `openings import --source-dir` consumes), `--request-timeout` (default `30.0`; finite and positive), `--request-delay` (default `0.25`; finite and nonnegative). At this stage prove help, required inputs, invalid timing (status `2`), and that no acquisition runs without them; do not claim success/failure behavior yet.
4. Add public re-exports to `openings/__init__.py` and extend `test_package_boundary.py` accordingly; extend `test_source_boundary.py` with the openings-acquisition boundaries (no games/scripts/backend imports, no subprocess, no sqlite).
5. Create synthetic, non-personal fixtures under `tests/database/openings/fixtures/`: a tiny valid five-file TSV set (reusing the DB-04 fixture style), invalid variants (missing file, extra TSV, bad header, illegal PGN), a valid commit-resolution JSON payload, and malformed commit payloads. Transport and staging/publish helpers remain injectable for deterministic proof.

**Focused proof**
- `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q` from `G:\ChessMoveTrainer` (Bash tool timeout: `120000` ms).
- `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -k "openings and acquire" -q` from `G:\ChessMoveTrainer` (Bash tool timeout: `120000` ms).
- `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.database openings acquire --help` from `G:\ChessMoveTrainer` (Bash tool timeout: `60000` ms).

**Stage acceptance:** The package imports cleanly with its own transport boundary; help names `--source-dir`, `--request-timeout`, `--request-delay`, and the fixed-upstream meaning with no base-URL/revision option; invalid timing is status `2`; boundary tests prove no games/legacy/production import direction; fixtures contain no personal content.

**Escalation boundary:** Stop for a new dependency, a third host, a configurable branch/mirror/revision option, or any need to import games acquisition code. Exact internal helper names and the dual-method transport spelling are bounded executor choices.

**Breakpoint:** none.

### 2. completed - Default-branch resolution and immutable five-file retrieval

**Ordered actions**
1. Test first, then implement commit resolution: GET the fixed GitHub REST commits-list URL for the fixed repository with no ref parameter (documented to default to the default branch, so no branch-name input exists); validate the response is a JSON list whose first element is an object with a `sha` string matching exactly forty lowercase hex characters; any other shape, empty list, or transport failure is an ordinary operational failure that stops before any file request. Rate limiting is an ordinary operational failure with no special state or exit code.
2. Construct file URLs only as `https://raw.githubusercontent.com/lichess-org/chess-openings/<resolved-sha>/{a,b,c,d,e}.tsv` from the validated SHA, the fixed repository, and the fixed file names; assert through the fake transport that only the two pinned hosts and exactly these five URLs are requested, in the fixed file order, with the wired finite timeout and the finite per-file delay before each file request (no delay before resolution).
3. Stage all five retrieved files into one temporary staging sibling directory beside the target; only when all five are retrieved does any validation or publication work begin. Any retrieval failure or interruption cleans the staging directory, changes no target file, and returns the failure result (or interruption, once CLI-wired).
4. Prove with the fake transport: valid resolution; malformed/empty/invalid-SHA responses; resolution HTTP failure; mid-set retrieval failure at file four of five with no publication and no target change; timeout/delay wiring; commit reporting carried through the result; and that nothing is written outside the staging and target paths.

**Focused proof**
- `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/openings/test_acquisition.py -q` from `G:\ChessMoveTrainer` (Bash tool timeout: `150000` ms).

**Stage acceptance:** One run cannot mix revisions at retrieval time; only the fixed hosts and exact five URLs are used; all-or-nothing retrieval holds; staging cleanup is proven on success and failure paths without live network access.

**Escalation boundary:** Stop if resolution requires authentication, a different host set, scraping, a branch-name input, or rate-limit behavior beyond ordinary operational failure.

**Breakpoint:** none.

### 3. completed - Whole-set validation, safe staged publication, rollback, and idempotence

**Ordered actions**
1. Test first, then implement whole-set validation: the staged directory is validated solely through `openings/source.load_opening_sources()` — the accepted strict five-file, legal-PGN, dedupe service is the only validation owner, with no duplicated rules. A failing staged set publishes nothing, leaves every target file unchanged, and cleans staging.
2. Implement publication per the user-settled Windows decision: byte-compare each staged file with its target; when all five are byte-identical, publish nothing, report the resolved commit with zero published and five unchanged files, and exit the service successfully (idempotent no-op). Otherwise snapshot both the prior bytes and prior presence/absence of every fixed target file, then replace each fixed file atomically (same-directory temporary file, flushed and fsynced content, `os.replace`) — mirroring the `games/raw_storage.py` convention. Only the five fixed names are touched; unrelated non-TSV files in the target directory are preserved untouched. An unexpected TSV filename makes the dedicated source directory invalid and must fail before mutation rather than being silently preserved into an unusable import source.
3. Implement rollback: any handled failure or `KeyboardInterrupt` during the swap sequence restores the prior bytes of files that existed and removes newly created fixed files that were previously absent, using atomic replacement for restored content; it then cleans the staging directory and in-memory prior-state snapshot and re-raises for interruption or returns the failure result. The service must not claim invisibility to concurrent readers during the swap window, and an abrupt crash mid-swap may leave mixed revisions that an idempotent rerun repairs — state this in the module docstring plainly.
4. Prove with fake transport and injectable publish/replace hooks: fresh publish into an empty directory; identical-content no-op with zero writes; changed-content full five-file replace; failure injected at each swap boundary restoring exact prior contents and prior absence; interruption rollback; staging cleanup on every exit path; unrelated non-TSV target-file preservation; unexpected TSV rejection before mutation; and that the published set passes `load_opening_sources` (non-regression rerun of the accepted source service).

**Focused proof**
- `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/openings/test_acquisition.py tests/database/openings/test_source.py -q` from `G:\ChessMoveTrainer` (Bash tool timeout: `150000` ms).

**Stage acceptance:** Prior usable set survives every handled retrieval, validation, publication, and interruption failure; unchanged content writes nothing; the five-file set is the only mutation surface; no partial or invalid file is ever left at a target path by a handled failure; the transient-crash mixed-revision window is documented, not hidden.

**Escalation boundary:** Stop if Windows reality prevents even this contract (for example locked target files that rollback cannot restore), if proof shows a handled failure can leave a partial set, or if rollback would require manifest/history machinery.

**Breakpoint:** none; the publication semantics are user-settled. The coordinator reviews only if proof exposes a genuine conflict with the settled decision.

### 4. completed - CLI wiring, example configuration files, and the durable DB-09 command inventory

**Ordered actions**
1. Complete the thin CLI: parse/validate timing options, call the service, and map outcomes to the settled exits — `0` complete (including the already-current no-op, with the resolved commit and published/unchanged counts on stdout), `1` operational or incomplete failure (message on stderr), `2` invalid invocation or timing, `130` interruption. No `--json` and no schema exit; commands stay noninteractive with errors only on stderr.
2. Add `tests/database/test_cli.py` scenarios for help, required `--source-dir`, invalid timing (`2`), success reporting with commit and counts (`0`), service failure (`1`), and interruption (`130`), using monkeypatched service behavior — never live network.
3. Add the smallest nonduplicative safe examples: `docs/examples/database-games.example.yaml` shared by `games acquire`/`games import` (placeholder `username` and `trainer_chesscom_uuid`, optional commented timing values), and `docs/examples/database-rebuild.example.yaml` (`rebuilt_neighbour` placeholder path). Do not invent an opening-acquisition YAML config. Add `docs/examples/README.md` stating that the files are examples with safe placeholders, which commands consume them, and that real identity must never be committed. Each file carries a comment header naming its owning contracts (DB-03/DB-08; examples added by DB-08A). No real username, real trainer UUID, secrets, or personal identifiers may appear.
4. Add `tests/database/test_configuration_examples.py`: the example files exist, parse as YAML, use only keys supported by the corresponding loaders, and contain the exact documented safe placeholder values. Do not place or hard-code any real username, trainer UUID, path, secret, or other personal identifier in either the examples or their tests.
5. Add the durable inventory `docs/flowcharts/database-command-inventory.md`: map every DB-09 lifecycle step to its package-owned command (schema, games acquire/import, openings acquire/import/lookup/replay, preferred-moves, stockfish, rebuild operations); classify each relevant legacy `scripts/` family as replaced or authority-excluded/noncanonical; and explicitly forbid any `scripts/` command, import, wrapper, fallback, or delegation in the accepted DB-09 path. Do not duplicate detailed historical proof or private data.
6. Make bounded flowchart updates: show `openings acquire` in `docs/flowcharts/database-toolchain.md` (acquisition step feeding the local five-file source directory) and in `docs/flowcharts/database-operator-journeys.md` (acquisition journey), update `docs/flowcharts/README.md` routing/wording where stale, and reference the new inventory. Do not edit historical records or reopen settled DB-08 content.
7. Add `tests/database/test_command_inventory.py`: a finite consistency check that the inventory exists and names the supported command surface including `openings acquire`, carries the legacy-forbidden statement, and that both flowchart docs reference `openings acquire` and the inventory link.

**Focused proof**
- `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q` from `G:\ChessMoveTrainer` (Bash tool timeout: `150000` ms).
- `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/test_configuration_examples.py tests/database/test_command_inventory.py -q` from `G:\ChessMoveTrainer` (Bash tool timeout: `90000` ms).

**Stage acceptance:** The supported CLI surface, example files, durable inventory, and flowcharts all express the real implemented behavior; placeholders only; exits `0/1/2/130` hold; no unrelated flowchart or historical record content was altered.

**Escalation boundary:** Stop if example content would need real identity, if the inventory would need to name a legacy script as canonical or acceptable for DB-09, or if flowchart reconciliation would require reopening settled DB-08 decisions.

**Breakpoint:** final coordinator Markdown review of the examples and inventory; no earlier human breakpoint.

### 5. completed - Final focused DB-08A proof and retained-proof reconciliation

**Ordered actions**
1. Run the consolidated focused proof below after all behavior exists. Reconcile retained proof: the accepted direct Chess.com `--month` service proof (`tests/database/games/test_acquisition.py`) remains valid because no stage edits games code; the shared `cli.py` and boundary proof are refreshed by this Plan's Stage 1/4/5 runs. If any stage edit touched `games/acquisition.py` or games behavior contrary to scope, rerun `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/games/test_acquisition.py -q` (Bash tool timeout `150000` ms) before claiming completion.
2. Confirm exclusions in the final diff: no schema, persistence, dependency, upstream configurability, legacy reuse, application integration, or unrelated-path change; unrelated worktree changes preserved.
3. Record progress, proof, and the visible result; leave the repository uncommitted.

**Focused proof**
- `timeout 150s .venv/Scripts/python.exe -m pytest tests/database/openings tests/database/test_cli.py tests/database/test_package_boundary.py tests/database/test_source_boundary.py tests/database/test_configuration_examples.py tests/database/test_command_inventory.py -q` from `G:\ChessMoveTrainer` (Bash tool timeout: `180000` ms).
- `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.database openings acquire --help` from `G:\ChessMoveTrainer` (Bash tool timeout: `60000` ms).

**Stage acceptance:** The consolidated focused set passes offline; the finite help invocation exits `0`; the diff stays inside the expected areas; no maintenance, aggregate, live-network, or hygiene check was run as implementation proof.

**Escalation boundary:** Stop rather than absorb any failure that can be solved only by exceeding the approved boundaries, weakening the settled safety behavior, or editing unrelated paths.

**Breakpoint:** coordinator acceptance of the complete Plan result.

## Progress and decisions

- **Stage 1:** completed - package-owned fixed-source constants, injectable JSON/text transport, immutable result/failure models, truthful CLI help/usage skeleton, public exports, clean source boundaries, and synthetic non-personal fixtures accepted. Proof from `G:\ChessMoveTrainer`: `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py -q` passed 17 tests; `timeout 90s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -k "openings and acquire" -q` passed 9 tests with 81 deselected; `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.database openings acquire --help` exited 0 and showed the required source directory, finite timing defaults, fixed upstream, and no configurable revision/base URL. Bash tool timeouts were respectively `120000`, `120000`, and `60000` milliseconds. Retrieval and publication remain deferred to later stages; breakpoint: none.
- **Stage 2:** completed - fixed default-branch commit resolution and exact immutable five-file staging accepted with failure/interruption cleanup and no target publication. Proof from `G:\ChessMoveTrainer`: `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/openings/test_acquisition.py -q` passed 21 tests in 2.62 seconds with Bash tool timeout `150000` milliseconds; Stage 1 proof remains retained; breakpoint: none.
- **Stage 3:** completed - strict staged validation through the existing source service, full five-file publication, unchanged no-op behavior, unexpected-TSV rejection, exact handled-failure/interruption rollback, and the accepted abrupt-crash limitation are accepted. Proof from `G:\ChessMoveTrainer`: `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/openings/test_acquisition.py tests/database/openings/test_source.py -q` passed 52 tests in 19.64 seconds with Bash tool timeout `150000` milliseconds. The Stage 2 acquisition proof is superseded; a coordinator-requested docstring-only truthfulness correction did not invalidate runtime proof; breakpoint: none.
- **Stage 4:** completed - thin CLI outcome reporting and exits, safe placeholder-only YAML examples, the durable DB-09 package-command inventory, and bounded flowchart routing updates accepted after coordinator Markdown review. Proof from `G:\ChessMoveTrainer`: `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_cli.py -q` passed 92 tests with Bash tool timeout `150000` milliseconds; `timeout 60s .venv/Scripts/python.exe -m pytest tests/database/test_configuration_examples.py tests/database/test_command_inventory.py -q` passed 4 tests with Bash tool timeout `90000` milliseconds. The examples contain only documented placeholders, the inventory forbids every `scripts/` command/import/wrapper/fallback/delegation in DB-09, and the flowchart edits remain bounded; breakpoint: coordinator review passed.
- **Stage 5:** completed - consolidated offline DB-08A proof passed 186 tests: `timeout 150s .venv/Scripts/python.exe -m pytest tests/database/openings tests/database/test_cli.py tests/database/test_package_boundary.py tests/database/test_source_boundary.py tests/database/test_configuration_examples.py tests/database/test_command_inventory.py -q` from `G:\ChessMoveTrainer`, with Bash tool timeout `180000` milliseconds. `timeout 30s .venv/Scripts/python.exe -m chess_move_trainer.database openings acquire --help` exited `0` with Bash tool timeout `60000` milliseconds and showed the required source directory, timing defaults, and fixed upstream without revision/base-URL options. The complete scope audit found no schema, persistence, dependency, upstream configurability, legacy reuse, application integration, live-network, or unrelated-path change. The accepted games `--month` proof remains retained because DB-08A did not alter games acquisition behavior; breakpoint: coordinator acceptance passed.

## Proof

- All proof is finite, offline, and focused: synthetic-transport acquisition tests, the accepted opening-source non-regression run, focused CLI scenarios, package/source-boundary tests, configuration-example tests, and the command-inventory consistency check. No live GitHub request, lint, formatting, broad build/type/source-size, aggregate/full-suite, maintenance, backend/frontend, or hygiene check is implementation proof.
- **Retained direct-change proof:** the accepted Chess.com `--month` work's focused proof (`tests/database/games/test_acquisition.py` + `tests/database/test_cli.py` 111 passed; boundary tests 16 passed; `games acquire --help` exit `0`) remains valid retained evidence. Invalidation rules: it is re-run only if a later edit touches `games/acquisition.py` or games behavior; the shared `cli.py` and boundary files are directly affected by Stages 1/4 and are refreshed by this Plan's own proof; the DB-04 `tests/database/openings/test_source.py` proof is refreshed in Stage 3 because validation reuse affects that seam.
- Every command above carries an explicit command-level `timeout Ns` and an explicit finite Bash tool timeout in milliseconds.

## Escalation boundaries

- **Dependency:** any new dependency, SDK, or auth token (pinned `httpx` must suffice); any packaging change.
- **GitHub contract:** authentication, scraping, a third host, a branch/mirror/revision input, or rate-limit behavior beyond ordinary operational failure.
- **Filesystem safety:** any handled failure or interruption that cannot restore the prior usable set; any need for manifests, version directories, pointers, source history, or persistence to preserve safety; a rollback that itself fails.
- **Licensing/provenance:** any upstream other than the fixed `lichess-org/chess-openings` repository, or any need to persist provenance/audit records.
- **Persistence/history:** schema or DDL change; any run/failure/source-version/manifest storage; any persisted resolved-commit state.
- **Upstream configurability:** any configurable repository, branch, mirror, URL, or revision input.
- **Legacy reuse:** any `scripts/` import, wrapper, call, copy, patch, fallback, or delegation; any inventory wording that admits a legacy command into the accepted DB-09 path.
- **Application integration:** backend/frontend/API work, DB-09 real-data proof, cutover, old-database access, raw-game policy change, or edits to completed historical Plans, the master plan, or the coordinator-owned DB-08A handoff.

Known unrelated worktree state to preserve: user-owned deleted/changed files under `data/chess-com/raw/` (do not read or touch); existing user modifications to `docs/grilling-docs/database-rebuild-direction.md` and `docs/master-plans/database-rebuild/database-rebuild.md`; the accepted direct-month implementation edits in games acquisition, shared CLI, and tests; the coordinator-owned `docs/grilling-docs/database-rebuild-db-08a.md` as read-only evidence. No commit or push.

## Visible result

> An operator can refresh the local five-file Lichess opening catalogue with one command that pins one upstream commit, validates the whole set, and never leaves the previous usable catalogue damaged — with example configs and a DB-09 command inventory proving only clean package commands remain.
