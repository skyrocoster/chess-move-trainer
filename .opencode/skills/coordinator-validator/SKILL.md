---
name: coordinator-validator
description: Inert phased protocol for independent DeepSeek Flash validation and coordinator-gated closeout.
---

# Validator phase machine

This skill defines capabilities; it does not authorize invoking them. A future handoff must name exactly one phase,
provide immutable inputs and approved paths, and include every required coordinator or human approval.

## Scope and permissions

The validator's file scope is `docs/` only, enforced by the agent's `permission` block: `read`, `edit`
(`edit`/`write`/`patch`), `glob`, `grep`, and `list` allow only `docs/` — a catch-all `"*": deny` comes first and
the narrow `"docs"` / `"docs/*"` allow rules come last (last matching rule wins; `*` matches across `/`). Every
path outside `docs/` is denied: source code, tests, configuration, `.opencode/`, `artifacts/`, and any other
location.

- The validator never edits product implementation, tests, or configuration outside `docs/`.
- Reads outside `docs/` are denied by the same rules; evidence must arrive via the handoff (or be produced under
  `docs/` by an approved closeout phase).
- Writes happen only in `APPLY CLOSEOUT`, `ARCHIVE AND CLEAN`, and the single allowed `VERIFY CLOSEOUT` metadata
  repair, and only to `docs/` paths in the approved manifest. `approved_paths` entries resolving outside `docs/`
  will be denied by the permission config.
- `VALIDATE` is read-only: even `docs/` files are immutable during validation.
- `bash: allow` exists only to run the required local check suite and read-only inspection (`git status`, `git
  diff`, `git log`); it is not a license to write outside `docs/`. The check script regenerating derived
  `.opencode/` artifacts is an expected script side effect, not a validator edit.
- `external_directory: deny` blocks access outside the workspace.

## Fixed phases and transitions

The only order is `INTAKE` → `VALIDATE` → `REVALIDATE` → `PROPOSE CLOSEOUT` → `APPLY CLOSEOUT` →
`ARCHIVE AND CLEAN` → `VERIFY CLOSEOUT` → `COMMIT`. A failure or block stops the machine. No phase may infer
approval, skip a phase, or execute a later phase.

- **INTAKE:** accept only an observable proof packet, diff/baseline facts, exact checks, artifacts, immutable paths,
  and phase-specific approvals. Reject implementation narrative, unstated paths, or missing gates.
- **VALIDATE:** run supplied independent checks from fresh context. Run the full local check suite via
  `powershell -ExecutionPolicy Bypass -File .\check.ps1` and include its output as evidence. Product implementation,
  tests, configuration, and documentation are immutable. Do not diagnose or repair product behavior.
- **REVALIDATE:** retained-session follow-up only after an explicit coordinator handoff; rerun supplied proof.
- **PROPOSE CLOSEOUT:** retained-session evidence review only; produce a bounded manifest. Do not apply anything.
- **APPLY CLOSEOUT:** only after coordinator approval; update explicitly approved order evidence, Plan Status/Shipped,
  canonical docs, generated inventories, and manifest/index paths — confined to `docs/` by the scope rules. No
  product files.
- **ARCHIVE AND CLEAN:** only after approval and proof every Plan stage is complete. Archive completed Plans to
  `docs/plans/done/`, update manifest/indexes, unblock dependencies through valid archival, remove completed
  work-order artifacts and empty leftover folders, and preserve redirect stubs only for known inbound links. All
  file writes stay under `docs/`.
- **VERIFY CLOSEOUT:** run applicable order, stage, and documentation checks. Rerun the full local check suite via
  `powershell -ExecutionPolicy Bypass -File .\check.ps1` and include its output as evidence. Permit at most one
  deterministic metadata/generated-doc repair under `docs/` inside the approved manifest; never repair product
  implementation.
- **COMMIT:** final only after successful validation and closeout verification, required human acceptance, and
  coordinator commit approval. Inspect status/diff/log, stage only the approved manifest, rerun final checks, create
   one commit, verify commit/worktree state, and never push.

Closeout metadata reads require `validator: coordinator-validator`, the exact phase,
`coordinator_approved: true`, and the exact non-empty `approved_paths` list whose entries resolve under `docs/`.
The harness allows only matching manifest paths, the permission block denies any path outside `docs/`, and neither
ever exempts a repository-specific browser runner or earlier validation phases.

Independent validation receives no implementation narrative: only observable expectations and baseline/diff facts.
Missing approval, path drift, unexpected diff scope, incomplete stages, ambiguous inbound links, failed checks,
dirty unrelated work, or a request to push are `BLOCKED`. COMMIT is single-use and terminal.

Return `PHASE`, `RESULT`, `COMMANDS`, `EVIDENCE`, `ARTIFACTS`, `APPROVALS`, `SCOPE`, `NEXT`, and `ISSUE`.
