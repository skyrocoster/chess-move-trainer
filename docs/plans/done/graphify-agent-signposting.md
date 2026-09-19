# Graphify agent signposting - Six deterministic graph bundles refresh before `/commit`

> **Status:** done - all three stages and their finite focused proof were accepted on 2026-09-15.

- **Read trigger:** Read before implementing the Graphify dependency, catalogue generator, focused tests, documentation, or `/commit` integration. Re-read before initial bundle generation and closeout.
- **Upstream:** `docs/grilling-docs/graphify-agent-signposting-direction.md` is the confirmed direction for coverage, AI-free extraction, database boundaries, stored artifacts, provenance, and commit ordering. The retained `PHASE: ASSESS` research establishes Graphify 0.9.61 CLI and output semantics and selected `PLAN-CANDIDATE` because this is one coherent outcome with sequential setup, generation, normalization, and proof stages.

## Outcome

Provide agents with an advisory, repository-backed Graphify catalogue that is generated locally from code ASTs and no-label clustering, never from an API or LLM. Repository-owned preservation keeps derived presentation stable when the canonical graph is unchanged. The repository contains six committed bundles under `docs/graphify/`, and the repository-defined `/commit` command refreshes every bundle from the complete pre-commit working tree before reviewing or staging changes. Any generation failure blocks the commit flow.

The approved catalogue directories and source roots are:

| Bundle | Graphify source root | Coverage note |
|---|---|---|
| `docs/graphify/repository/` | repository root `.` | Full Git-visible, supported-code corpus; Graphify honors `.gitignore` and `.graphifyignore`. |
| `docs/graphify/backend/` | `backend/` | Backend application and colocated backend tests. |
| `docs/graphify/frontend/` | `frontend/` | Frontend application, component tests, and Storybook source. |
| `docs/graphify/core-data/` | `src/` | Complete core/worker Python package, including its database schema Python and SQL source only. |
| `docs/graphify/tests/` | top-level `tests/` | Integration, database, engine, and end-to-end tests. No composite staging tree; backend/frontend tests remain in their domain bundles. |
| `docs/graphify/agent-workflow/` | `.opencode/` | Supported code in agent workflow/tooling; Markdown remains excluded by `--code-only`. |

Each bundle contains exactly these meaningful committed artifacts:

- `GRAPH_REPORT.md`
- `graph.html`
- `graph.json`
- `.graphify_analysis.json`
- `manifest.json`

## Current facts

- `requirements.txt` is the application dependency input used by `backend/Dockerfile:11-12`; the selected pin is `graphifyy[sql,svg]==0.9.61`.
- The local user `uv` tool has Graphify 0.9.61, but the application `.venv` currently lacks Graphify and `tree-sitter-sql`; dependency proof must occur after the requirements change and environment installation.
- `graphify extract --code-only` performs local AST extraction and writes graph/analysis output. It does not generate the report or HTML, so the generator must follow it with `graphify cluster-only --no-label`.
- `cluster-only --no-label` is required so community labels are deterministic placeholders and no community-labeling LLM path is entered.
- `GRAPHIFY_OUT` accepts an absolute path. The generator will pass each bundle directory as an absolute output path while passing the source root explicitly, so regeneration does not depend on a committed `.graphify_root`.
- `graphify update` is not the catalogue driver: without an explicit custom-output mechanism it reads `.graphify_root` or defaults to `.`, which is unsafe for six external bundle directories.
- Graphify writes ephemeral `cache/`, `.graphify_root`, stale markers, and other sidecars. The generator removes its own ephemeral outputs after each successful bundle, while `.gitignore` protects against interrupted runs.
- The existing root `graphify-out/` is a known untracked status-feature Graphify tree containing only meaningful Graphify output, cache, and `.graphify_root`. It may be removed only after an allowlist and symlink/type check; unknown content must stop the generator without deletion.
- The live ignored `data/database/chess.db` and all other runtime data are never opened, queried, exported, or indexed. The `src/` core-data layer covers the complete core/worker Python package, including its database schema Python and SQL source.
- `AGENTS.md`, source code, and active Plans remain authoritative over generated graph suggestions.
- The current `.opencode/commands/commit.md` is ignored by `.gitignore:46`; a narrow exception for the commands directory and this command is required so the requested repository workflow can be committed. Other ignored `.opencode` content remains ignored.
- No Dockerfile, Compose, `opencode.jsonc`, Graphify MCP, Git hook, CI, or product behavior change is part of this outcome. The existing backend image will receive the dependency through `requirements.txt`; container rebuild is not an implementation proof requirement.

## Scope

- **Included:**
  - Pinning the approved Graphify dependency in `requirements.txt`.
  - Graphify-specific recursion exclusions and ephemeral-output protection in new/updated ignore rules.
  - Repository-owned generation, validation, safe cleanup, and provenance normalization in `src/tools/graphify_catalogue.py`.
  - Focused tooling tests in `tests/graphify/test_catalogue.py`.
  - A thin agent-facing catalogue index at `docs/graphify/README.md`.
  - A Graphify orientation note in `AGENTS.md`.
  - Fail-fast regeneration as the first operation in `.opencode/commands/commit.md`.
  - Initial committed artifacts in the six approved bundle directories.
  - Allowlist-only replacement/removal of the existing untracked root `graphify-out/`.
  - The core-data bundle's complete `src/` core/worker Python package and its database schema source.
- **Expected areas:** `requirements.txt`, `.gitignore`, `.graphifyignore`, `src/` including `src/tools/graphify_catalogue.py`, `tests/graphify/test_catalogue.py`, `AGENTS.md`, `.opencode/commands/commit.md`, `docs/graphify/README.md`, and `docs/graphify/{repository,backend,frontend,core-data,tests,agent-workflow}/`.
- **Excluded:** the live ignored `data/database/chess.db` and all other runtime data (never opened, queried, exported, or indexed); semantic extraction, APIs, API keys, AI-generated labels, MCP, hooks, CI, package-manifest redesign, Docker/Compose redesign, application behavior, feature graphs, composite test staging trees, broad test/lint/build/hygiene runs, Git commits/pushes/stashes/branches/worktrees, and unrelated dirty changes.

## Provenance and artifact contract

The generator must normalize Graphify’s pre-commit output after both Graphify commands have succeeded:

- `graph.json` must not claim the final commit hash. Preserve a nullable `built_at_commit` value and add the stable `graphify_provenance` value `complete pre-commit working tree`.
- `.graphify_analysis.json` carries the same `graphify_provenance` value.
- `GRAPH_REPORT.md` replaces Graphify’s `Built from commit` claim and misleading `git rev-parse HEAD` freshness instruction with wording that the report represents the complete pre-commit working tree, including local changes, and points to `manifest.json` for per-file content hashes.
- `graph.html` carries the same wording in stable HTML metadata/comment; no visual or runtime application integration is added.
- `manifest.json` retains Graphify’s incremental `mtime`, `seen`, `ast_hash`, and `semantic_hash` records. Hashes are content evidence; timestamp fields are not rewritten for byte-level cross-clone reproducibility.
- Graphify 0.9.61 can vary derived clustering scores across unchanged runs even with deterministic process seeding. Compare the newly extracted canonical `graph.json` with the prior normalized graph before clustering. When the graph is unchanged, preserve the prior `.graphify_analysis.json`, `GRAPH_REPORT.md`, and `graph.html` bytes; when the graph changes, recompute and normalize them. This keeps advisory presentation stable without suppressing real topology changes.
- Graph JSON, analysis JSON, report, and HTML must be written/normalized atomically or through temporary files with cleanup on failure. The generator validates the final five-file contract before declaring a layer successful.

## Stages

### 1. **completed** - Establish the dependency, exclusions, generator, normalization contract, legacy cleanup, and focused tests

**Ordered actions**

1. Add `graphifyy[sql,svg]==0.9.61` to `requirements.txt`. Do not add a separate global/`uvx` tool path or alter `pyproject.toml`’s existing dependency model.
2. Add `.graphifyignore` with `/docs/graphify/` and `/graphify-out/` so committed catalogue output and the legacy root output cannot recursively enter the repository graph, including when output files are already tracked.
3. Extend `.gitignore` only for `/graphify-out/`, `docs/graphify/**/cache/`, Graphify machine-local/stale/label sidecars, and the narrow `!.opencode/commands/` plus `!.opencode/commands/commit.md` exception. Do not broadly unignore `.opencode/`.
4. Implement `src/tools/graphify_catalogue.py` with the exact six source/output mappings above. The user requires repository scripts to live under `src/`; keep this maintenance entry point outside the shipped `chess_move_trainer` package. The core-data mapping must use `src/`, so it covers the complete core/worker Python package, its database schema source, and this repository tool. For each layer, run Graphify through the invoking Python interpreter with an absolute `GRAPHIFY_OUT`, `extract <source> --code-only`, then `cluster-only <source> --no-label`.
5. Give every Graphify child process a finite 900-second subprocess timeout. Capture stdout/stderr and report the layer plus exact failed command. Stop immediately on a nonzero exit, timeout, malformed output, missing required artifact, or normalization/cleanup error; do not continue to later layers.
6. Preflight output directories. Refuse symlinks, non-directories, or unknown top-level entries. Remove the existing root `graphify-out/` only when its complete tree is made of an explicit Graphify allowlist; remove only known Graphify sidecars/caches from owned bundle directories. Never use `git clean`, recursive repository deletion, or a broad untracked-file cleanup.
7. Normalize and validate provenance and artifact paths as specified above. Ensure generated source/manifest paths are relative to their layer source root (including `src/` for core-data), contain no path to the live database or other runtime data, and do not point into `docs/graphify/`.
8. Add focused tests at `tests/graphify/test_catalogue.py` for the layer map (including the complete `src/` core/worker mapping), command flags/environment, no-LLM contract, provenance normalization, required artifact validation, safe legacy cleanup, unknown-file refusal, relative-path checks, manifest hash preservation, and runtime-data exclusion. Tests must use temporary fixtures and must not open, query, export, or index the live database or other runtime data.

**Focused proof**

- Install the changed application dependency set: `timeout 900s .venv/Scripts/python.exe -m pip install -r requirements.txt` (recommended Bash tool timeout: `910000` ms).
- Confirm the exact package and SQL parser import without extraction: `timeout 30s .venv/Scripts/python.exe -c "import importlib.metadata as m; assert m.version('graphifyy') == '0.9.61'; import graphify, tree_sitter_sql"` (recommended Bash tool timeout: `40000` ms).
- Run only the focused tests: `timeout 120s .venv/Scripts/python.exe -m pytest tests/graphify/test_catalogue.py -q` (recommended Bash tool timeout: `130000` ms).

**Acceptance and breakpoint**

Stage 1 is accepted when the pinned dependency imports with SQL support, the focused tests pass, the generator has finite fail-fast behavior, and safe cleanup tests prove that unknown content is never removed. No initial catalogue generation occurs until this stage passes.

**Escalate if:** a reader requires `built_at_commit` to remain a real commit hash; the dependency cannot install in the documented Python 3.12 environment; an existing output contains unknown or linked content; or the necessary narrow `.opencode/commands/commit.md` tracking exception is rejected.

### 2. **completed** - Add the catalogue signpost and integrate refresh into `AGENTS.md` and `/commit`

**Ordered actions**

1. Add `docs/graphify/README.md` as a short index linking each bundle’s report, HTML, graph JSON, analysis JSON, and manifest. Explain that Graphify is advisory only, source/Plans win, and agents need not open it for a small change in a known file.
2. Add an `AGENTS.md` section directing agents to the index only for orientation, dependency tracing, ownership discovery, or cross-boundary work. State that the core-data graph represents the complete core/worker Python package and database schema source, never live database records or other runtime data.
3. Update `.opencode/commands/commit.md` so the first action runs the repository-owned generator from the application environment before status/diff review. The command must say that generation is local-only and deterministic, must stop and report the failed layer/command on any failure, and must not proceed to review, `git add -A`, or commit after failure.
4. Preserve the existing whole-working-tree behavior: after successful generation, review the resulting source and graph changes, run `git add -A`, and commit. Do not add a Git hook or alter `opencode.jsonc`.

**Focused proof**

- Verify the signpost, six exact links, source-authority wording, and commit ordering with the focused tooling test: `timeout 120s .venv/Scripts/python.exe -m pytest tests/graphify/test_catalogue.py -q` (recommended Bash tool timeout: `130000` ms).
- Use a bounded text assertion only; do not run `/commit`, `git add`, or `git commit`: `timeout 30s .venv/Scripts/python.exe -c "from pathlib import Path; p=Path('AGENTS.md').read_text(); c=Path('.opencode/commands/commit.md').read_text(); assert 'docs/graphify/README.md' in p; assert c.index('graphify_catalogue') < c.index('git status') < c.index('git add -A')"` (recommended Bash tool timeout: `40000` ms).

**Acceptance and breakpoint**

Stage 2 is accepted when an agent can reach every approved bundle from the thin index, `AGENTS.md` gives the restricted consultation rule, and `/commit` visibly orders fail-fast regeneration before status/diff review and staging. The command remains unexecuted during this Plan.

**Escalate if:** the repository workflow requires partial commits, a Git hook, MCP, or a different commit ordering; or the catalogue must expose a feature graph before the six broad bundles demonstrate insufficiency.

### 3. **completed** - Generate, validate, repeat, and close the six initial bundles

**Ordered actions**

1. Run the generator once from the repository root after Stage 1 and Stage 2 are accepted. It must safely remove the known status-only root `graphify-out/` and create the six approved directories without touching unrelated files.
2. Validate every bundle contains exactly the five meaningful artifacts and no committed cache, query stamp, `.graphify_root`, label sidecar, stale marker, absolute machine-local path, live database or other runtime-data path, or self-indexed output path.
3. Validate all four provenance-bearing artifacts use the canonical complete pre-commit working-tree wording and that no final commit hash is claimed. Validate manifest hashes exist and remain usable for incremental detection.
4. Run the generator a second time without source changes. Confirm each layer takes the incremental path or safely recognizes no changes, no API/LLM backend is needed, no forbidden sidecars remain, canonical graph topology and manifest content hashes are unchanged, and the generator preserves prior clustering analysis/report/HTML bytes when that graph is unchanged. Permit only Graphify’s documented filesystem timestamp fields to vary when the filesystem changes them.
5. Remove all `.graphify_root` files from the generated bundles and run the generator again. This is the fresh-clone regeneration proof: explicit source roots and absolute outputs must be sufficient.
6. Do not run `/commit` or any commit operation. At closeout, perform one finite final scope audit against the Plan baseline, preserve unrelated changes, and record only accepted proof in the Plan’s ledgers.

**Focused proof**

- Initial and repeated generation: `timeout 10800s .venv/Scripts/python.exe src/tools/graphify_catalogue.py` (recommended Bash tool timeout: `10810000` ms) — run twice, not concurrently.
- After each generation, run the focused contract tests: `timeout 120s .venv/Scripts/python.exe -m pytest tests/graphify/test_catalogue.py -q` (recommended Bash tool timeout: `130000` ms).
- The contract test must inspect only generated JSON/HTML/report/manifest text and filesystem metadata; it must assert absence of `data/database/chess.db` and other runtime-data paths without opening, querying, exporting, or indexing the live database or runtime data.
- The focused tests must cover fail-fast behavior with a controlled failing child command and allowlist-only cleanup with both known-only and unknown-content fixtures.

**Acceptance and breakpoint**

Stage 3 is accepted when all six bundles pass the five-artifact, provenance, exclusion, and relative-path assertions; the core-data bundle covers the complete `src/` core/worker Python package and database schema source without opening, querying, exporting, or indexing the live database or other runtime data; repeated generation preserves deterministic graph results and manifest hashes; deleting machine-local markers does not prevent regeneration; and the root status-only output has been removed only through the allowlist. The Plan is then eligible for closeout.

**Escalate if:** any layer needs `--no-gitignore`, a semantic/API backend, a database connection or live runtime-data access, a composite staging tree, or a feature graph; any generated artifact cannot be made consistent with the approved provenance wording; or a finite local run exceeds the 900-second per-Graphify-operation bound.

## Progress and decisions

### Progress ledger

- **Stage 1:** completed - dependency, ignore rules, six-layer generator, provenance normalization, fail-fast behavior, and allowlist-only cleanup are implemented; all focused proof passed on 2026-09-15.
- **Stage 2:** completed - the thin catalogue index links all six five-artifact bundles, `AGENTS.md` carries the restricted advisory signpost, and `/commit` refreshes first with finite fail-closed behavior before review and staging; proof passed on 2026-09-15.
- **Stage 3:** completed - all six five-artifact bundles were generated, the legacy root output was removed through the allowlist, marker-free regeneration passed, and all 30 artifact hashes remained identical across the final unchanged run; accepted on 2026-09-15.

### Decision ledger

- **D1 - approved:** Graphify is advisory; source, `AGENTS.md`, and active Plans remain authoritative.
- **D2 - approved:** Use `graphifyy[sql,svg]==0.9.61` in application Python dependencies.
- **D3 - approved:** Use only `extract --code-only` and `cluster-only --no-label`; never invoke semantic extraction, APIs, MCP, hooks, or CI.
- **D4 - approved:** Use the six exact catalogue directory names and source roots recorded in Outcome.
- **D5 - implementation contract:** Use absolute `GRAPHIFY_OUT` per bundle, explicit source roots, nullable `built_at_commit`, and the canonical `graphify_provenance` value. Escalate only if a real Graphify consumer rejects this non-commit provenance representation.
- **D6 - approved safety rule:** Remove the known untracked root output only after an allowlist/type check; unknown content is preserved and blocks the run.
- **D7 - approved workflow:** Refresh all six bundles before `/commit` review and staging; a failed refresh blocks the remainder; no Git hook.
- **D8 - user scope correction:** All repository scripts belong under `src/`; the Graphify entry point therefore lives at `src/tools/graphify_catalogue.py`, outside the shipped application package but inside the approved core-data graph source root.
- **D9 - approved derived-output stability:** Graphify's local, no-AI clustering may vary small derived scores. When canonical `graph.json` is unchanged, preserve the prior analysis/report/HTML bytes; recompute those artifacts only after a real graph change.

### Proof ledger

- **P1:** passed - `timeout 900s .venv/Scripts/python.exe -m pip install -r requirements.txt` (Bash timeout `910000` ms), the pinned import check (Bash timeout `40000` ms), and `timeout 30s .venv/Scripts/python.exe -m graphify --version` (Bash timeout `40000` ms) established Graphify 0.9.61 with `tree_sitter_sql` and the generator's real module invocation. Carry forward until `requirements.txt`, Python version, or environment installation changes.
- **P2:** passed and refreshed - `timeout 120s .venv/Scripts/python.exe -m pytest tests/graphify/test_catalogue.py -q` (Bash timeout `130000` ms) passed 17 tests after the final ownership, stability, and report-normalization corrections. Coverage includes mappings, local-only flags, finite fail-fast behavior, provenance, artifact validation, manifest preservation, tracked `data/` acceptance, runtime database rejection, safe cleanup, catalogue links, authority wording, fail-closed `/commit` ordering, `src/tools` ownership, unchanged-graph preservation, changed-graph clustering, and repository-owned freshness guidance. Carry forward until those implementation or contract inputs change.
- **P3:** passed - repeated `timeout 10800s .venv/Scripts/python.exe src/tools/graphify_catalogue.py` runs (Bash timeout `10810000` ms) produced six exact five-artifact bundles with canonical provenance, relative paths, no forbidden sidecars/runtime database paths, and repository-owned refresh guidance. The final 30 artifacts total 30,280,393 bytes. Carry forward until source roots, ignore rules, artifact layout, generator, or normalizer changes.
- **P4:** passed - generation succeeded without `.graphify_root`, and a finite SHA-256 comparison established that all 30 artifact bytes were identical across the final unchanged marker-free run. Carry forward until the generator, Graphify version, output paths, source graph, or environment changes.

Passing proof remains valid until a later stage changes its command, inputs, exercised behavior, configuration, dependency, or environment. Rerun only invalidated proof.

## Proof

- No aggregate, product, browser, lint, formatting, type/build, source-size, Docker, or repository-hygiene checks are required.
- The only generation command is the finite `timeout 10800s .venv/Scripts/python.exe src/tools/graphify_catalogue.py`; the script itself enforces a finite 900-second timeout for each Graphify child.
- `/commit` itself is never run during implementation or proof because it can commit changes.
- No live database or runtime-data command is permitted. Database safety is proven by the `src/` core/worker source-root selection, ignore/exclusion assertions, and output-text assertions only; the live ignored `data/database/chess.db` and other runtime data are never opened, queried, exported, or indexed.

## Escalation boundaries

- Ask before changing the six approved source roots, directory names, artifact list, or top-level tests interpretation.
- Ask before adding MCP, a Git hook, CI, semantic extraction, an API/LLM backend, feature graphs, or a composite staging tree.
- Ask if an existing consumer requires a valid final commit hash rather than the approved complete-working-tree provenance.
- Stop without deleting anything if the legacy root or any owned bundle contains unknown, linked, non-regular, or otherwise unrecognized content.
- Stop if dependency installation, SQL AST support, or the finite Graphify timeout cannot be satisfied in the documented Windows/Python 3.12 environment.
- Preserve unrelated dirty changes; never commit, push, stash, branch, or create a worktree.

## Closeout

After every stage is accepted and the final finite scope audit confirms only approved paths and generated artifacts are in scope, update the ledgers and status to `done`. Then move this file, without creating a replacement or legacy lifecycle record, from:

`docs/plans/active/graphify-agent-signposting.md`

to:

`docs/plans/done/graphify-agent-signposting.md`

Closeout must not run `/commit`, create `DESIGN.md`, or alter unrelated worktree content.

## Visible result

> An agent can open `docs/graphify/README.md`, follow any of six current advisory graph bundles, and trust that `/commit` refreshes them locally before staging while refusing to commit after a generation failure.
