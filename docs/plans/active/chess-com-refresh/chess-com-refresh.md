# Chess.com refresh pipeline - one repeatable command keeps the configured corpus and derived data current

> **Status:** stopped - User rejected this direction; no further implementation is authorized

- **Read trigger:** Read before implementing or validating the repeatable Chess.com refresh command, its fetch-status contract, or its ordered corpus/derived-data/analysis pipeline.
- **Upstream:** none

## Outcome

One user-invoked command refreshes games for the repository's configured Chess.com user, inserts valid new games once, publishes the current corpus, refreshes S3 classification and S4 recurrence/projections, resumes eligible Stockfish analysis with the existing qualified profile, reports each stage, and returns nonzero when the fetch or any required stage is incomplete or fails.

## Scope

- **Included:** A single orchestrator at `scripts/refresh_chess_com.py`; an observable fetch result that distinguishes complete from incomplete/failed fetches; ordered fetch, corpus, S3, S4, analysis preflight/run, and final-validation stages; reuse of existing Python APIs, configuration, deduplication, per-stage atomic publication, locks, signatures, and append-only histories; temporary-database/mock tests for new games, exclusions, reruns, interruption/resume, failure propagation, S3/S4 freshness, and analysis completion semantics; concise command usage and prerequisites.
- **Expected areas:** `scripts/refresh_chess_com.py`; bounded changes in `scripts/chess_com/{fetch_games.py,_cli.py,README.md}`; focused tests in `tests/chess_com/test_refresh.py`; read-only integration with `scripts/opening_catalog/{classification_persistence.py,recurrence_persistence.py}` and `backend/app/features/analysis/{selection.py,preflight.py,runner.py,provisioning.py}`.
- **Excluded:** Automatic or OS scheduling; frontend/API work; new dependencies; schema or migration changes; destructive cleanup; arbitrary-player or multiple-corpus support; S1/S2 source rebuilds; S5 tracked-player projections; retroactive metadata correction for existing UUIDs; cross-stage rollback; deletion of historical analysis failures or obsolete results; complete maintenance checks; live network fetches or full live Stockfish analysis as automated implementation proof.

## Stages

1. **completed - orchestrator contracts and fetch-status boundary.**
   - **Ordered actions:** Define the command configuration and stage-result/report shape around the existing username, subject UUID, database, engine, profile, worker, watchdog, and delay settings. Adapt the fetch seam only as needed so archive/month failures, rate limits, and successful completion are observable to the orchestrator while preserving UUID upserts, ETags, raw snapshots, and historical-month behavior. Make an incomplete fetch stop before corpus publication and return nonzero; do not invoke downstream stages in this stage.
   - **Focused proof:** Temporary/mocked fetch tests prove one UUID is inserted once, a rerun is unchanged, a non-429 month failure is reported as incomplete, a 429 fails fast, and the orchestrator does not call corpus or later stages after an incomplete fetch.
   - **Breakpoint:** None while existing source-field and historical-month semantics remain unchanged. Escalate any request to repair retroactive existing-UUID metadata.

2. **pending - ordered corpus and derived-data pipeline.**
   - **Ordered actions:** Invoke the existing fetch, `run_extraction`, `import_classification`, and `import_recurrence` APIs in order for the configured subject/corpus. Validate required accepted S1/S2 context and corpus prerequisites before dependent stages. Record each result and stop later stages after any corpus, S3, or S4 failure; retain the existing per-stage atomic behavior and explicitly do not add cross-stage rollback. Add temporary fixtures for accepted and excluded games, new/changed/removed corpus membership, safe reruns, injected stage failures, and S3/S4 signatures and output coverage matching the newly published corpus.
   - **Focused proof:** `test_refresh.py` verifies that a new accepted game reaches `games`, corpus occurrences, S3, and S4 exactly once; an excluded game does not; a no-change rerun reports unchanged/no-op behavior; and failure prevents unsafe downstream calls. Existing focused corpus, catalog, relationship, classification, and recurrence tests remain the regression guard for their individual atomic contracts.
   - **Breakpoint:** None while S1/S2 remain the accepted static source context and S3/S4 remain current-corpus derived namespaces. Escalate any requirement for all-stage atomic rollback or S1/S2 source refresh.

3. **pending - analysis integration, final validation, and usage documentation.**
   - **Ordered actions:** Run the existing read-only analysis preflight, then the existing full accepted-corpus runner using profile `mp09-balanced-nodes-v2-200000`, its engine verification, worker limits, lock, retry, interruption, and resume behavior. Integrate the Python APIs rather than inheriting the standalone CLI's `clear_port(5666)` side effect. Treat a run as successful only when no current target remains eligible/unprocessed and the run has no failures or interruption; preserve historical append-only failure rows. Recheck S3/S4 input signatures and current output coverage, produce a concise stage summary, return the final exit code, and document one repeatable invocation plus schema/engine prerequisites.
   - **Focused proof:** Mock-engine tests prove eligible results are skipped, missing/stale work resumes, failures and interruption return nonzero, and a successful run satisfies completion semantics. A read-only preflight proves no database mutation. CLI help and README checks prove the single invocation and prerequisites are discoverable.
   - **Breakpoint:** A full live corpus analysis is a separate runtime authorization point because it is long-running and resource-intensive; it is not required for automated Plan proof.

Stages are sequential; no stages run in parallel. A passing proof item remains valid until a later stage changes its command, inputs, exercised behavior, configuration, dependencies, or environment.

## Progress and decisions

- **Stage 1:** completed - fetch results expose complete/incomplete status, month failures, unchanged counts, and rate limits; the orchestrator returns nonzero and stops before downstream hooks after incomplete fetch. Focused proof: `timeout 120s ".venv/Scripts/python.exe" -m pytest tests/chess_com/test_fetcher.py tests/chess_com/test_refresh.py -k "fetch or incomplete or stop" -q` passed 10 tests with 1 deselected (tool timeout `120000` ms).
- **Stage 2:** pending - ordered corpus/S3/S4 publication and failure gating; proof is focused temporary-database pipeline behavior; breakpoint is cross-stage rollback or S1/S2 refresh.
- **Stage 3:** pending - resumable analysis, final consistency validation, and documentation; proof is mock-engine/preflight/CLI behavior; breakpoint is separately authorized live full-corpus execution.
- **Settled decisions:** “Regularly and easily” means a repeatable user-invoked command; the configured `skyrocoster` identity and subject UUID remain authoritative; normal refreshes use accepted S1/S2 and refresh only corpus-dependent S3/S4; failures stop unsafe downstream work but do not roll back already committed earlier stages.
- **Stopped direction:** The earlier pre-corpus clearing decision was withdrawn before execution. The user rejected stage-number terminology and requested a table-by-table data-flow and destructive-effects review before any new implementation direction.

## Proof

- `timeout 120s ".venv/Scripts/python.exe" -m pytest tests/chess_com/test_fetcher.py tests/chess_com/test_refresh.py -k "fetch or incomplete or stop" -q` — bash tool timeout: `120000` ms.
- `timeout 180s ".venv/Scripts/python.exe" -m pytest tests/chess_com/test_refresh.py tests/chess_com/test_extract_corpus.py tests/opening_catalog/test_classification.py tests/opening_catalog/test_recurrence.py -k "refresh or incremental or rerun or failure or freshness" -q` — bash tool timeout: `180000` ms.
- `timeout 180s ".venv/Scripts/python.exe" -m pytest tests/chess_com/test_refresh.py backend/tests/features/analysis/test_corpus_preflight.py backend/tests/features/analysis/test_operator.py -k "analysis or resume or complete or preflight" -q` — bash tool timeout: `180000` ms.
- `timeout 30s ".venv/Scripts/python.exe" scripts/refresh_chess_com.py --help` — bash tool timeout: `30000` ms.
- `timeout 120s ".venv/Scripts/python.exe" scripts/stockfish_analysis/analyze_positions.py --all --preflight-only --workers 1` — bash tool timeout: `120000` ms; read-only only.

No live network fetch or full live Stockfish corpus run is required for implementation proof. Complete maintenance checks are separate work.

## Escalation boundaries

- Any change to product behavior, command contract, configuration ownership, arbitrary users/corpora, or automatic scheduling.
- Any retroactive metadata correction policy for existing UUIDs, S1/S2 source rebuild, S5 projection, schema/migration/dependency change, destructive cleanup, deletion of historical analysis records, or cross-stage rollback.
- Any different Stockfish engine/profile, analysis target identity, resource policy, or requirement to run while taking ownership of the backend port.
- Any need to change accepted corpus rules, derived-table semantics, API/frontend behavior, or unrelated worktree/database content.

## Visible result

> Running one documented command refreshes the configured Chess.com corpus and reports a successful, current corpus/S3/S4/Stockfish state—or clearly reports the failed stage and exits nonzero.
