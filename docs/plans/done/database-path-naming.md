# Explicit database path naming - host seed and live container paths are distinct

> **Status:** complete - path naming/selection and data-preservation acceptance met. The isolated real-games-list performance threshold miss is retained as non-blocking evidence outside this Plan's naming acceptance.

- **Read trigger:** Read before any implementation, service activation, test, or guarded host-artifact migration for this outcome.
- **Upstream:** [Database path naming decisions](../../grilling-docs/database-path-naming.md), especially Decisions and Constraints and exclusions.

## Outcome

Host runs default to `data/database/chess-seed.db`, while the running backend explicitly receives
`CHESS_REBUILT_DATABASE_PATH=data/database/chess.db` from Compose. That keeps backend resolution at
`/workspace/data/database/chess.db`; worker arguments and Datasette resolution remain unchanged at
`data/database/chess.db` and `/data/chess.db`. Every role is selected explicitly without runtime environment
detection.

### Current behavior in plain English

`get_rebuilt_database_path()` is the same Python function on the host and in the backend container. With no
environment variable, both processes currently receive the same ambiguous relative path. The host intends that path
as seed/export storage, while the container volume makes it live storage. Compose does not currently tell the backend
which role to select. `DEFAULT_DATABASE_PATH` and a duplicate proof literal hide the distinction, and CLI help
describes one path as serving both roles.

### Desired behavior in plain English

When `CHESS_REBUILT_DATABASE_PATH` is absent, `get_rebuilt_database_path()` returns the lifecycle-owned
`HOST_SEED_DATABASE_PATH`, so host runs use `data/database/chess-seed.db`. The backend service receives an explicit
Compose value of `data/database/chess.db`, so its dependency selects the live database without detecting that it is
inside a container. `LIVE_DATABASE_PATH = Path("data/database/chess.db")` remains the lifecycle-owned programmatic
name for the live relative path; the backend dependency does not import it merely to create a reference. An explicit
`CHESS_REBUILT_DATABASE_PATH` value still wins unchanged.

## Scope

- **Included:**
  - A guarded rename of the ignored primary host file from `data/database/chess.db` to
    `data/database/chess-seed.db`, with precondition, no-overwrite, and byte-preservation checks.
  - `HOST_SEED_DATABASE_PATH` and `LIVE_DATABASE_PATH`, both owned by `lifecycle.py`; complete removal of
    `DEFAULT_DATABASE_PATH` rather than an alias or reassignment.
  - Host defaults in lifecycle, CLI, proof, real-database tests, and benchmarks; backend fallback to the host
    constant when its explicit override is absent.
  - An explicit `CHESS_REBUILT_DATABASE_PATH: data/database/chess.db` entry in the Compose backend environment,
    plus the minimum targeted activation sequence required for an already-running backend.
  - Deliberate updates to the pinned and directly affected tests, host-path documentation, and the Compose path
    contract.
- **Expected areas:**
  - `src/chess_move_trainer/database/{lifecycle.py,proof.py,proof_models.py,cli_helpers.py,cli_preferred.py,cli_lifecycle.py}`
  - `backend/app/dependencies.py`
  - `compose.yaml` and `dev.ps1` (the latter is read-only execution-contract evidence; no script edit is expected)
  - `tests/database/test_package_boundary.py`
  - `tests/database/test_source_boundary.py`
  - `tests/database/test_lifecycle_cli.py`
  - `tests/database/preferred_moves/test_cli.py`
  - `tests/database/proof/{test_proof.py,test_measurements.py}`
  - `backend/tests/features/games/test_api.py`
  - `backend/tests/features/position_training_requirements/test_real_database.py`
  - `backend/tests/benchmarks/test_api_benchmark_real.py`
  - `data/README.md` and `docs/DEVELOPMENT_SERVICES.md`
  - Ignored artifact `data/database/chess.db` -> `data/database/chess-seed.db` only.
- **Excluded:**
  - Database contents, schema, row semantics, sidecar data, service topology, volume names, mounts, ports, and
    live locations. The ignored `chess.db.backup.pre-wal` is not renamed or edited.
  - Runtime environment detection, a new environment variable, a compatibility alias, a silent fallback, or a
    dependency/import-direction change. `CHESS_REBUILT_DATABASE_PATH` is an existing application variable; Compose
    gains an explicit value for it, not a new variable.
  - Changes to `CHESS_REBUILT_DATABASE_PATH` override precedence or accepted values.
  - The Graphify runtime-data rejection sentinel in `src/tools/graphify_catalogue_validation.py:74` and its pinned
    assertions in `tests/graphify/test_graphify_catalogue.py:181-197`; `data/database/chess.db` remains a rejection
    sentinel there.
  - Temporary fixture names such as `tmp_path / "chess.db"` in `tests/database/test_setup.py`,
    `tests/database/test_update_games.py`, `tests/database/test_update_openings.py`, and
    `backend/tests/features/openings/test_catalogue_api.py`; these are not host defaults.
  - Historical grilling records, including `docs/grilling-docs/chess-learning-workflow-2026-09-21.md` and the
    prior path-naming record itself.
  - Browser/E2E checks, unrelated service lifecycle work, lint, formatting, broad type/build, source-size,
    aggregate, repository-hygiene, and unrelated tests.

## Settled decisions and caller contracts

The upstream decision record settles the filesystem direction: callers choose explicitly, the host file is renamed to
`chess-seed.db`, the backend/worker live file remains `/workspace/data/database/chess.db`, Datasette remains
`/data/chess.db`, and `DEFAULT_DATABASE_PATH` is removed. The corrected boundary decision is that the shared Python
function keeps a host default, while Compose explicitly supplies the live choice to the backend process.

| Caller or area | Role | Intended path contract |
|---|---|---|
| `lifecycle.py` `LifecycleResult`, setup, game update, and opening update defaults | Host seed/export | `HOST_SEED_DATABASE_PATH` |
| `cli_helpers.py` lifecycle destination validation and `Target:` output | Host seed/export | `HOST_SEED_DATABASE_PATH` |
| `cli_preferred.py` fixed preferred-move setup | Host seed/export | `HOST_SEED_DATABASE_PATH` |
| `proof.py` host-oriented public constant surface | Host seed/export only | Expose `HOST_SEED_DATABASE_PATH`; do not expose `LIVE_DATABASE_PATH` through this proof surface |
| `proof_models.py` | Proof data models | Remove its duplicate literal/constant; do not own a path constant |
| `backend/app/dependencies.py` with no override | Host default | Return `HOST_SEED_DATABASE_PATH` |
| `backend/app/dependencies.py` with `CHESS_REBUILT_DATABASE_PATH` | Explicit caller-selected path | Return the exact override unchanged |
| Compose `backend.environment` | Live container | Set `CHESS_REBUILT_DATABASE_PATH: data/database/chess.db` explicitly |
| `lifecycle.py` live programmatic name | Live relative path value | Own `LIVE_DATABASE_PATH = Path("data/database/chess.db")`; no forced backend import |
| Compose worker and worker-six arguments | Live container | Keep `data/database/chess.db` relative to `/workspace`, resolving to `/workspace/data/database/chess.db` |
| Compose Datasette command | Live container | Keep `/data/chess.db` |
| Host proof, real-database, and benchmark tests | Host seed/export fixture | Use the renamed host seed path, then explicitly configure any backend test dependency to that chosen host file |

`proof.py` will expose the host constant by importing the single lifecycle-owned definition; `proof_models.py` will
not redefine it. This host-only shape avoids a misleading live export from proof APIs. `proof_models.py` may not
import proof or create a reverse dependency; the lifecycle-to-proof direction must remain acyclic.

## Stages

1. **complete - explicit backend Compose selection prepared before changing Python fallback behavior.**
   - **Ordered actions:**
     1. From `G:\ChessMoveTrainer`, run the finite `dev.ps1 status` preflight in the Service handoff section before
        any lifecycle action. Treat a failed, unclear, unhealthy, or partially reported backend state as a hard stop;
        do not guess or run raw Docker commands.
     2. Add only `CHESS_REBUILT_DATABASE_PATH: data/database/chess.db` to the existing backend service environment
        in `compose.yaml`. Do not change worker arguments, Datasette, mounts, volumes, topology, or ports.
     3. If status shows the backend is running and healthy, run the targeted `dev.ps1 rebuild backend` action from
        the Service handoff section. The inspected script uses `--build --force-recreate --wait --wait-timeout 300`
        for this target, so it applies the changed environment; a plain `restart` is not sufficient because its
        subsequent `up` uses `--no-recreate`.
     4. If the backend is not running, do not start it merely for this Plan. Leave it stopped; its next approved
        `dev.ps1 start backend` will use the changed Compose environment. The host/container source handoff may
        proceed only while the backend remains stopped.
   - **Focused proof:** the status preflight and targeted rebuild/start contract establish that an already-running
     backend has an explicit live selection before its bind-mounted Python fallback changes. No browser check is
     needed.
   - **Interruption/rollback:** if status or rebuild fails, stop before changing `backend/app/dependencies.py` or
     renaming the host file and escalate. If the backend was stopped, keep it stopped. Do not revert the Compose
     environment by guessing while a recreated backend is running; resolve the service failure first.
   - **Stage acceptance:** a running backend has `CHESS_REBUILT_DATABASE_PATH=data/database/chess.db`; a stopped
     backend has a prepared Compose value and no lifecycle action was forced; worker/Datasette live behavior remains
     unchanged; no host fallback has been changed yet.
   - **Breakpoint:** user approval is required before the targeted backend recreate. Ask if the backend is unhealthy,
     its state cannot be established, another process changes service state concurrently, or any action beyond
     `status` and targeted `rebuild backend` appears necessary.

2. **complete - switch Python constants/callers and perform the guarded host handoff.**
   - **Ordered actions:**
     1. Before editing or renaming, verify that `data/database/chess.db` exists as the expected regular host file,
        `data/database/chess-seed.db` does not exist, neither target path is a symlink, and no relevant primary or
        destination sidecar makes the handoff unsafe. Record size and a cryptographic hash without reading database
        contents. If any check is unsafe, stop without overwriting, renaming, or editing.
     2. Change only the named source files so `lifecycle.py` owns exactly
        `HOST_SEED_DATABASE_PATH: Final[Path] = Path("data/database/chess-seed.db")` and
        `LIVE_DATABASE_PATH: Final[Path] = Path("data/database/chess.db")`. Move lifecycle and host CLI defaults to
        the host constant; change `get_rebuilt_database_path()` to use the host constant when its existing override
        is absent; remove every executable definition/import/re-export of `DEFAULT_DATABASE_PATH`.
     3. Remove the duplicate proof-model literal and expose only the lifecycle-owned host constant through
        `proof.py`. Do not import `LIVE_DATABASE_PATH` into backend dependencies merely to create a reference.
     4. Without creating a review breakpoint between the source switch and filesystem handoff, rename the primary
        host file to `data/database/chess-seed.db` only when the destination is still absent. Verify the old path is
        absent and the new file has the recorded size and hash; do not touch the ignored backup.
   - **Focused proof:** source inspection of definitions/imports, the host fallback contract, and before/after
     artifact metadata; no database query or content inspection.
   - **Interruption/rollback:** if preflight fails, leave everything unchanged. If source edits occur but the rename
     has not completed, restore only those edits. If the rename completes and a later handoff action fails, restore
     the original source edits and rename the unchanged new file back only when the old path is absent and the target
     still matches the recorded metadata. Never overwrite either path; if rollback preconditions are not met, stop
     and escalate. A running backend is safe during this stage only because Stage 1 applied its explicit Compose
     override; if that condition is no longer true, stop before the source switch.
   - **Stage acceptance:** host code points to an existing renamed seed file; a running backend continues to select
     the live file through its explicit Compose override; both constants are explicit and lifecycle-owned; no old
     alias remains in executable source; the artifact has the same bytes and the backup is untouched.
   - **Breakpoint:** hard safety stop for any existing destination, unexpected file type/sidecar, changed hash/size,
     active writer, missing backend override, or import-cycle risk.

3. **complete - update pinned tests, CLI help, and host/live caller assertions.**
   - **Ordered actions:**
     1. Update package-boundary and source-boundary assertions to require both lifecycle constants, reject the old
        name/duplicate proof literal, and require only the host constant on the proof API. Pin the live constant's
        ownership/value without requiring backend dependencies to import it.
     2. Update lifecycle CLI and preferred-move CLI tests/help expectations to identify the host seed path.
     3. Update `backend/tests/features/games/test_api.py` so no environment returns `HOST_SEED_DATABASE_PATH` and
        an explicit `CHESS_REBUILT_DATABASE_PATH` (including a live-path choice) wins unchanged. Retain the ignored
        legacy `CHESS_DATABASE_PATH` behavior.
     4. Update the real-database training and benchmark tests, proof tests, and measurement tests to use
        `HOST_SEED_DATABASE_PATH`/`data/database/chess-seed.db` as host artifacts. Make the benchmark wording say
        its host default is `HOST_SEED_DATABASE_PATH`; its client setup then explicitly points the backend dependency
        at that chosen host file. Preserve opt-in gates and byte-preservation checks.
   - **Focused proof:** run P1 in the Proof section. It must prove no-env host fallback and explicit live override
     behavior without touching the real database.
   - **Stage acceptance:** tests name the role they exercise, the backend override still wins, proof tests cannot
     accidentally select the live container database, and no test change broadens the product contract.
   - **Breakpoint:** ask before changing an asserted public import surface beyond replacing the settled constant
     names, or before adding a new test dependency.

4. **complete - refresh host-facing documentation and verify the activated Compose contract.**
   - **Ordered actions:**
     1. In `data/README.md`, describe `chess-seed.db` as the ignored host seed/export file, retain the backup name
        unchanged, update host hash/export examples, and distinguish the live volume paths.
     2. In `docs/DEVELOPMENT_SERVICES.md`, update only host-side seed/export references and copy destinations;
        retain all live-volume checks and container paths. Document that a changed Compose environment requires the
        targeted backend rebuild path rather than a plain restart when relevant to the existing service guidance.
     3. Review `compose.yaml`: backend must have the explicit existing-variable value
        `CHESS_REBUILT_DATABASE_PATH: data/database/chess.db`; worker and worker-six must still receive
        `data/database/chess.db`; Datasette must still receive `/data/chess.db`; mounts, volumes, topology, and
        interpolation remain unchanged.
   - **Focused proof:** manual document/source review plus the retained Stage 1 activation result; no additional
     service lifecycle action and no browser/E2E check.
   - **Stage acceptance:** host fallback, backend Compose selection, worker arguments, and Datasette path are all
     visible and unambiguous; effective live behavior remains unchanged even though Compose now records the backend
     selection explicitly.
   - **Breakpoint:** ask before changing any mount, command argument, volume, topology, service, live path, or
     lifecycle guidance beyond the targeted backend activation.

5. **complete - focused behavioral proof retained; path naming/data-preservation acceptance closed.**
   - **Ordered actions:** run P1 first; run P2 only with the renamed host artifact available; run P3 and P4 only
     when their explicit real-database preconditions are satisfied. Do not run a broad suite or additional service
     lifecycle command. Retain a passing item until a later change affects its command, inputs, exercised behavior,
     configuration, dependencies, or environment.
    - **Focused proof:** the finite commands in the Proof section below.
    - **Stage acceptance:** P1, corrected P2A/P2B, and P3 pass; P4 exercised the renamed host seed and preserved
      path/data behavior but missed the unrelated real-games-list median threshold. Per the user's Option A decision,
      that isolated performance result is non-blocking and outside this naming Plan's acceptance. No command silently
      selected the live volume, and the real tests left the host seed bytes unchanged.
   - **Breakpoint:** stop and escalate on missing/changed seed bytes, a destination conflict, a live-volume access,
     an unexpected write, or any failure that suggests behavior beyond the settled rename.

## Progress

- **Stage 1:** complete - proof: C1; the stopped backend has the explicit Compose live-database selection prepared, and no lifecycle action was forced. Next boundary is the guarded source/artifact handoff in Stage 2.
- **Stage 2:** complete - proof: C2; lifecycle and host adapters now use the lifecycle-owned host seed constant, the
  backend fallback is host-seed-first with its explicit override preserved, and the guarded host artifact handoff is
  byte-preserving. Next boundary is the pinned host/live caller contract update in Stage 3.
- **Stage 3:** complete - proof: P1; CLI help, package/source boundaries, lifecycle/preferred adapters, backend
  fallback assertions, and host-seed real-database callers now name their roles explicitly. Next boundary is the
  host-facing documentation and final Compose contract review in Stage 4.
- **Stage 4:** complete - proof: C3; host documentation distinguishes the ignored seed/export copy from the live
  volume paths, and read-only Compose inspection confirms the accepted backend, worker, worker-six, and Datasette
  contract without another service action. Next boundary is the focused behavioral proof in Stage 5.
- **Stage 5:** complete - proof: P1, corrected P2A/P2B, P3, and P4 retained; P4's isolated real-games-list
  performance threshold miss is non-blocking evidence unrelated to path naming. The user's Option A decision closes
  the naming/data-preservation outcome without performance investigation or another test run.

## Decision ledger

- **D1:** `HOST_SEED_DATABASE_PATH` and `LIVE_DATABASE_PATH` are the only two production path choices; rationale and
  locations are settled by the upstream grilling record.
- **D2:** `DEFAULT_DATABASE_PATH` is removed completely, with no alias or reassignment.
- **D3:** Both constants are owned in `lifecycle.py`; host-oriented proof APIs expose only the host constant and
  never a live path.
- **D4:** `get_rebuilt_database_path()` defaults to the host seed when the existing override is absent. The backend
  container receives the live path explicitly through the existing `CHESS_REBUILT_DATABASE_PATH` variable in
  Compose; this is explicit configuration, not runtime detection.
- **D5:** Worker arguments, Datasette path, mounts, volume topology, and effective live behavior are unchanged;
  Compose gains only the explicit backend environment selection.
- **D6:** The primary ignored host file may be renamed only under the user's guarded authorization. The backup is
  outside that authorization.
- **D7:** A running backend must receive the Compose environment through the targeted `dev.ps1 rebuild backend`
  path before the bind-mounted Python fallback changes. A stopped backend is not started by this Plan.
- **D8:** Coordinator resolution for Stage 1: the backend's `Exited (255)` state followed normal startup and
  repeated health `200 OK` responses before a Docker Desktop bind-mount watcher I/O error at `/workspace/backend`;
  it is treated as a stopped Docker interruption artifact, not an application/configuration defect. The backend was
  not started, rebuilt, or restarted.
- **D9:** Stage 2 keeps `HOST_SEED_DATABASE_PATH` and `LIVE_DATABASE_PATH` lifecycle-owned, exposes only the host
  constant through proof APIs, uses the host constant for the no-override backend fallback, and preserves the exact
  existing override when present. The guarded primary host artifact moved without touching the backup.
- **D10:** Stage 3 expresses the settled host seed/live container split in CLI help and directly affected tests;
  explicit live overrides remain unchanged, `CHESS_DATABASE_PATH` remains ignored, and real-database callers retain
  their opt-in and byte-preservation safeguards.
- **D11:** Stage 4 keeps `data/database/chess-seed.db` as the ignored host seed/export copy, retains
  `chess.db.backup.pre-wal` as a separate manual backup, and documents the unchanged live volume paths and targeted
  backend rebuild requirement without changing Compose or service state.
- **D12:** The original combined P2 command remains non-passing diagnostic evidence after its 180-second timeout with
  no assertion or path-integration failure. Stage 5 proof was corrected only by splitting its two approved files into
  P2A and P2B, each with a finite 360-second bound; no product or test code was changed.
- **D13:** The user selected Option A: accept the path naming/selection fix and record P4's isolated
  `real-games-list` performance threshold result (`1787.0ms >= 1500.0ms`) as unrelated, non-blocking evidence. No
  performance investigation is part of this Plan; it is separate follow-up work only if requested later.

## Proof ledger

- **C1:** complete - `timeout 90s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status` reported the same
  stopped backend (`Exited (255)`), and the retained bounded `dev.ps1 logs backend` diagnostic showed normal startup,
  repeated health `200 OK` responses, then the Docker Desktop bind-mount watcher I/O error. `compose.yaml` now has
  the exact backend-only `CHESS_REBUILT_DATABASE_PATH: data/database/chess.db` entry; worker paths, Datasette,
  mounts, volumes, ports, and topology remain unchanged. The backend remained stopped.
- **C2:** complete - bounded artifact preflight and post-rename verification recorded size `151248896` and SHA-256
  `4a4b70de7e8e383191666f91dc394efce95f1e73712fea0d89892eb06c9f3027`; the old path is absent, the new path is a
  regular non-symlink file with the same metadata, and no primary sidecar was present. Source inspection found the
  two lifecycle-owned constants, host-only proof export, host fallback/explicit override logic, and no executable
  `DEFAULT_DATABASE_PATH` in `src` or `backend/app`. Compose and the stopped-backend Stage 1 evidence are unchanged.
- **P1:** complete - from `G:\ChessMoveTrainer`, ran
  `timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py tests/database/test_lifecycle_cli.py tests/database/preferred_moves/test_cli.py backend/tests/features/games/test_api.py`
  with Bash tool timeout `180000` ms; result `45 passed, 1 skipped in 12.73s`. This covers lifecycle ownership and
  proof exports, rejection of the old name and duplicate proof literal, host/live CLI wording and adapters, no-env
  host fallback, explicit live override, and ignored legacy `CHESS_DATABASE_PATH`. It remains valid until a later
  affecting source, test, configuration, or environment change.
- **P2 diagnostic:** non-passing - the original combined command
  `timeout 180s .venv/Scripts/python.exe -m pytest tests/database/proof/test_proof.py tests/database/proof/test_measurements.py`
  ran from `G:\ChessMoveTrainer` with Bash tool timeout `240000` ms and reached `test_proof.py ..` before the
  command-level timeout, exit `124`. It reported no assertion or path-integration failure; the retained seed hash
  was unchanged. This is retained as diagnostic evidence, not proof.
- **P2A:** complete - from `G:\ChessMoveTrainer`, ran
  `timeout 360s .venv/Scripts/python.exe -m pytest tests/database/proof/test_proof.py`
  with Bash tool timeout `420000` ms; result `3 passed in 191.57s (0:03:11)`.
- **P2B:** complete - from `G:\ChessMoveTrainer`, ran
  `timeout 360s .venv/Scripts/python.exe -m pytest tests/database/proof/test_measurements.py`
  with Bash tool timeout `420000` ms; result `2 passed in 6.87s`.
- **P2 corrected:** complete - P2A and P2B both pass under the split finite bounds. The original combined timeout is
  retained only as non-passing diagnostic evidence.
- **P3:** complete - from `G:\ChessMoveTrainer`, ran
  `timeout 240s env CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE=1 .venv/Scripts/python.exe -m pytest backend/tests/features/position_training_requirements/test_real_database.py`
  with Bash tool timeout `300000` ms; result `2 passed in 6.51s`.
- **C3:** complete - bounded review of `data/README.md`, `docs/DEVELOPMENT_SERVICES.md`, and `compose.yaml` confirms
  the host seed/export path is `data/database/chess-seed.db`, the backup name is unchanged, and live paths remain
  `/workspace/data/database/chess.db` and `/data/chess.db`. Compose still has the explicit backend environment,
  unchanged worker and worker-six arguments, Datasette command, mounts, volumes, ports, and topology. P1 remains
  retained; no service action or database operation was run.
- **P4:** non-blocking evidence - from `G:\ChessMoveTrainer`, ran
  `timeout 600s env CHESS_RUN_API_BENCHMARK_REAL=1 .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v`
  with Bash tool timeout `660000` ms; result `5 passed, 1 failed in 41.07s`. The failure was the unrelated real
  games-list performance threshold: median `1787.0ms >= 1500.0ms`. The run created six timestamped reports under
  `docs/benchmarks/API`; the exact pre-run snapshot contained only `README.md`, and all six run-created reports were
  removed afterward. The directory was restored to that snapshot. The user explicitly accepted this as non-blocking
  and outside the naming Plan; no path or data failure occurred.
- No automated Plan checker is supplied; the final Plan check is a manual template, scope, stage, timeout, and
  escalation review.

## Service handoff

These are the only approved service commands in this Plan. They are direct Git Bash commands run with working
directory `G:\ChessMoveTrainer`; each has a finite shell command-level timeout and the stated finite Bash tool
timeout. They are not run while writing this Plan.

### Status preflight, required before activation

```text
timeout 90s powershell -ExecutionPolicy Bypass -File ./dev.ps1 status
```

- Bash tool timeout: `120000` ms.
- If the backend is running and healthy, apply the Compose environment and use the targeted rebuild below.
- If the backend is not running, do not start it; leave it stopped and let its next approved `start backend` consume
  the changed Compose configuration.
- If the state is unhealthy, partial, unclear, or the command fails, stop and ask rather than running a lifecycle
  action or changing the Python fallback.

### Targeted activation for an already-running backend

```text
timeout 360s powershell -ExecutionPolicy Bypass -File ./dev.ps1 rebuild backend
```

- Bash tool timeout: `420000` ms.
- This is the minimum targeted `dev.ps1` action that applies the changed Compose environment: the inspected script
  force-recreates only the backend, waits up to 300 seconds, and does not alter worker/Datasette topology.
- A plain `restart backend` is not an approved substitute because the script follows restart with `up --no-recreate`.
- If this action fails, stop before the Python source switch and host-file rename; do not start competing services,
  run raw Docker commands, or guess at recovery.

## Proof

All pytest commands below are direct Git Bash commands run with working directory `G:\ChessMoveTrainer`. Each has a
finite shell command-level timeout and the stated finite Bash tool timeout; none is run while writing this Plan.

### P1 - non-real host fallback and explicit live override

```text
timeout 120s .venv/Scripts/python.exe -m pytest tests/database/test_package_boundary.py tests/database/test_source_boundary.py tests/database/test_lifecycle_cli.py tests/database/preferred_moves/test_cli.py backend/tests/features/games/test_api.py
```

- Bash tool timeout: `180000` ms.
- Proves the constant ownership/export boundary, absence of the old alias, host CLI destination/help, preferred-move
  host selection, and `get_rebuilt_database_path()` returning `HOST_SEED_DATABASE_PATH` with no environment.
- Also proves an explicit `CHESS_REBUILT_DATABASE_PATH` live-path choice wins unchanged; this is programmatic
  override coverage, not a requirement for backend dependencies to import `LIVE_DATABASE_PATH`.
- It does not touch the real database or replace the Stage 1 Compose activation proof.

### P2 - host proof and measurement defaults

```text
timeout 180s .venv/Scripts/python.exe -m pytest tests/database/proof/test_proof.py tests/database/proof/test_measurements.py
```

- Bash tool timeout: `240000` ms.
- Preconditions: `data/database/chess-seed.db` exists from the guarded rename, matches the recorded pre-rename size
  and hash, and the retained raw/opening source inputs are present. The tests must use the host default; do not
  point `DIRECT_DATABASE` at the live volume.
- Proves host-oriented proof/measurement defaults and aggregate read-only behavior; it does not authorize reading
  or changing live container data.

### P3 - opt-in real training-requirements host default

```text
timeout 240s env CHESS_RUN_REAL_TRAINING_REQUIREMENTS_SMOKE=1 .venv/Scripts/python.exe -m pytest backend/tests/features/position_training_requirements/test_real_database.py
```

- Bash tool timeout: `300000` ms.
- Preconditions: the intact renamed host seed and retained data are available; no live-volume path is substituted.
- Proves the affected real-database backend read path and its before/after byte-preservation checks.

### P4 - opt-in real API benchmark host default

```text
timeout 600s env CHESS_RUN_API_BENCHMARK_REAL=1 .venv/Scripts/python.exe -m pytest backend/tests/benchmarks/test_api_benchmark_real.py -v
```

- Bash tool timeout: `660000` ms.
- Preconditions: the intact renamed host seed is available; leave `CHESS_REBUILT_DATABASE_PATH` unset so the
  benchmark's `_real_database()` exercises its `HOST_SEED_DATABASE_PATH` default. The test then explicitly sets
  the backend dependency override to that chosen host file before requests; do not start/stop services.
- The benchmark's own bounded request limits and before/after byte checks remain authoritative. This proves the
  directly affected real benchmark default without changing database contents.

No lint, formatting, broad type/build, source-size, aggregate, repository-hygiene, browser/E2E, unrelated service
lifecycle, or unrelated tests are part of this Plan.

## Acceptance

- With no `CHESS_REBUILT_DATABASE_PATH`, host code returns and uses `data/database/chess-seed.db` through
  `HOST_SEED_DATABASE_PATH`.
- A running backend receives `CHESS_REBUILT_DATABASE_PATH=data/database/chess.db` from Compose before the Python
  fallback changes, so it resolves to `/workspace/data/database/chess.db`. Worker arguments and Datasette remain
  `data/database/chess.db` and `/data/chess.db`; mounts, volume topology, and effective live behavior do not drift.
- `DEFAULT_DATABASE_PATH` has no executable definition, import, re-export, alias, or reassignment. The historical
  decision record may retain the name as a record of what was removed.
- The two constants are owned only by `lifecycle.py`, with no import cycle, and proof APIs expose only the host seed
  constant. `LIVE_DATABASE_PATH` remains available as the programmatic lifecycle-owned live value without a forced
  misleading backend import.
- `CHESS_REBUILT_DATABASE_PATH` remains the explicit override with no silent fallback or environment-based role
  detection; P1 proves both no-env host fallback and explicit live override.
- The guarded rename never overwrites an existing destination, leaves the backup untouched, and preserves the host
  file's recorded bytes/size/hash.
- Host documentation distinguishes seed/export storage from live volume storage, and Compose configuration records
  the backend selection explicitly while preserving worker/Datasette values and service topology.
- Focused path/data proof passes: P1, corrected P2A/P2B, and P3 pass, while P4 exercised the intact renamed artifact
  without a path or data failure. P4's isolated real-games-list threshold miss is explicitly non-blocking and does
  not prevent naming acceptance; no misleading host proof API can select the live container database.

## Closeout notes

- The user's explicit Option A decision closes this Plan on path naming/selection and data preservation, not API speed.
- No tests or implementation commands were rerun during closeout. No Plan-specific transient `handoff.md` exists.
- This Plan is archived at `docs/plans/done/database-path-naming.md`.

## Escalation boundaries

Ask before changing any behavior or contract beyond the settled rename, including a new or renamed public API beyond
the two approved constants, runtime environment detection, a new dependency, an import-ownership change, a different
host/live path, a Compose mount/argument/topology/service change, a service action beyond the approved status and
targeted backend rebuild, a database-content or backup operation, a destination overwrite, a destructive rollback, a
broadened test suite, or an acceptance requirement not stated here. If status cannot establish the backend state, the
backend is unhealthy/partial, the explicit Compose override is not active before the source switch, or the guarded
rename finds an existing destination or any unsafe condition, stop without overwriting or guessing and ask.

## Visible result

> Host runs use `chess-seed.db`, while the backend is explicitly configured for the unchanged live container database
> and workers/Datasette keep their existing live paths.
