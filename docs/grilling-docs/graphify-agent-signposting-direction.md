# Graphify agent-signposting direction

Confirmed with the user on 2026-09-15.

## Goal

Use Graphify to give AI coding agents a fast, repository-backed map of code structure and relationships. Graphify is an advisory navigation layer. Source code, `AGENTS.md`, and active Plans remain authoritative when they disagree with generated output.

The graph-generation process must not use AI. It must be local, deterministic AST extraction without an LLM, API key, semantic inference, or AI-generated labels. Inputs that Graphify cannot process under that rule are excluded rather than handled by an AI service.

## Coverage and layers

Start with these broad graphs:

1. Full repository
2. Backend
3. Frontend
4. Core worker and database schema
5. Tests
6. `.opencode` agent workflow and tooling

The full-repository graph covers Git-visible files that Graphify can parse deterministically. Graphify must respect `.gitignore`; ignored secrets, logs, dependencies, caches, generated runtime data, and database files are not inputs. The committed graph-output tree must also be excluded from extraction so that graphs do not index themselves.

Feature-level graphs are adaptive. Add one only after work in that area demonstrates that the broad graph is insufficient.

Markdown and YAML are not graph inputs because Graphify 0.9.61 skips them in code-only mode. They may still signpost the graph bundles in normal repository documentation.

## Database boundary

Represent database structure only through deterministic parsing of the repository's Python schema modules and SQL schema and migration files. Do not open, inspect, export, or index `data/database/chess.db`. Do not generate row counts, statistics, or record-derived graph data.

The Graphify dependency therefore needs both SQL and SVG support and is pinned as `graphifyy[sql,svg]==0.9.61` in the application's Python dependency set.

## Stored artifacts

Store the graph catalogue under `docs/graphify/`, with a short `README.md` linking the broad layers. Commit the meaningful generated bundle for each layer:

- Markdown report
- Interactive HTML graph
- Graph JSON
- Analysis JSON
- Incremental manifest

Do not commit Graphify caches, query stamps, or `.graphify_root` files containing machine-local absolute paths.

Generated provenance must not claim that the graph was built from the final commit hash: that hash cannot exist until after the graph itself is committed. Normalize that metadata to state that the graph was generated from the complete pre-commit working tree. Per-file manifest hashes remain the content-level evidence.

## Agent usage

`AGENTS.md` points agents to `docs/graphify/README.md`. Agents consult the catalogue when orienting themselves, locating ownership, following dependencies, or working across repository boundaries. A small change in a known file does not require opening Graphify.

## Commit behavior

The repository's `/commit` OpenCode command remains the integration point; do not add a Git hook. Before reviewing, staging, and committing, `/commit`:

1. Updates all six graph layers from the complete local working tree.
2. Uses only local code-only extraction and deterministic SQL parsing.
3. Normalizes generated provenance.
4. Stops immediately and reports the failed layer and command if any graph operation fails.
5. Reviews the resulting source and graph changes.
6. Runs `git add -A` and commits all committable local changes together.

This deliberately supports whole-working-tree commits rather than partial commits. A raw `git commit` remains outside this Graphify-maintained workflow.

## Accepted tradeoffs

- Meaningful generated artifacts are committed even though they may total several megabytes and produce generated diffs.
- All six layers update on every `/commit` for predictable behavior; path-sensitive optimization is intentionally avoided.
- Deterministic coverage is preferred over broader semantic coverage.
- Graphify is installed with application Python dependencies rather than as a separate global or `uvx`-managed tool.

This record captures direction and constraints. It is not an implementation Plan or proof that the setup exists.
