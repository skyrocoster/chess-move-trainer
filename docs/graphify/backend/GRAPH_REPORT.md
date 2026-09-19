# Graph Report - backend  (2026-09-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1174 nodes · 2853 edges · 68 communities (42 shown, 13 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 345 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- This report represents the complete pre-commit working tree, including local changes.
- See `manifest.json` for per-file content hashes.
- Refresh all layers with `timeout 10800s .venv/Scripts/python.exe src/tools/graphify_catalogue.py` (or invoke `/commit`, which runs it first).
## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 42
- Community 43
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56

## God Nodes (most connected - your core abstractions)
1. `AnalysisProfile` - 53 edges
2. `AnalysisValidationError` - 36 edges
3. `AnalysisRepository` - 34 edges
4. `AnalysisResult` - 31 edges
5. `require_evaluation_schema()` - 29 edges
6. `enqueue()` - 28 edges
7. `initialized()` - 28 edges
8. `position_key_from_fen()` - 26 edges
9. `run_batch()` - 24 edges
10. `claim_next()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `test_catalogue_response_rejects_extra_fields()` --uses--> `OpeningCatalogueResponse`  [INFERRED]
  tests/features/openings/test_catalogue_api.py → app/features/openings/catalogue_api_schemas.py
- `test_profile_serialization_and_eligibility_identity_are_deterministic()` --calls--> `AnalysisProfile`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/models.py
- `_result()` --calls--> `AnalysisCandidate`  [INFERRED]
  tests/features/analysis/test_operator.py → app/features/analysis/models.py
- `complete_result()` --calls--> `AnalysisCandidate`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/models.py
- `result_for()` --calls--> `AnalysisCandidate`  [INFERRED]
  tests/features/evaluation/conftest.py → app/features/analysis/models.py

## Import Cycles
- None detected.

## Communities (68 total, 13 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (61): _current_signature(), get_or_compute(), _Inflight, json_response(), opening_detail_key(), openings_catalogue_version(), openings_key(), Path (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (54): api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path, TestClient, Extend the shared position-insight fixture to a complete five-line result. (+46 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (46): api_context(), client(), create_preferred_moves_database(), delete_body(), put_body(), fixture, MonkeyPatch, Path (+38 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (55): alias, get_rebuilt_database_path(), Path, Return the explicit clean database path for the current application process., ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest (+47 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (51): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, needs_real_database, benchmark_client(), benchmark_database(), create_benchmark_database(), _database_info(), _float_env() (+43 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (42): TrainingRequirementPolicy, Canonical key from the validated query, resolved database, and policy., training_requirements_key(), _configured_float(), get_training_requirement_policy(), TrainingRequirementPolicy, Application dependencies for database capabilities., Return the configured policy, or ``None`` when the capability is unavailable. (+34 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (31): AnalysisBusyError, AnalysisLockError, RuntimeError, Another top-level analysis operator owns the database lock., A short coordinator SQLite transaction could not acquire its lock., Persisted backend analysis contracts., AnalysisRunLock, Path (+23 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (37): api_context(), client(), count_reader_calls(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path (+29 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (35): EvaluationLockError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits., The evaluation worker session could not acquire the shared analysis lock., Browser-evaluation service boundary over the durable queue and analysis storage. (+27 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (23): _EventLoopTransportStub, FakeProcess, managed(), Board, Limit, parametrize, Minimal asyncio.SubprocessTransport-shaped stub with a mutable return code., Real asyncio event that fails loudly if lifecycle code ever awaits it. (+15 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (29): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResult, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, ContractModel (+21 more)

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (28): Path, Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), completed_at(), connection(), database_path(), profile(), fixture (+20 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (28): AnalysisRequestErrorCode, AnalysisRequestBody, AnalysisRequestErrorResponse, BaseModel, HTTP contracts for one desired current analysis request., Strict known request fields while tolerating future client fields., Stable error body for the desired-analysis operation., _error() (+20 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (31): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+23 more)

### Community 14 - "Community 14"
Cohesion: 0.14
Nodes (27): games_key(), Canonical key from the validated games query and resolved database., GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel, GamesResponse (+19 more)

### Community 15 - "Community 15"
Cohesion: 0.16
Nodes (28): EvaluationQueueError, A queue state-machine transition is invalid for the current state., EvaluationQueueItem, _begin_immediate(), _canonical(), operation(), complete(), operation() (+20 more)

### Community 16 - "Community 16"
Cohesion: 0.20
Nodes (25): api_context(), create_openings_database(), fixture, MonkeyPatch, Path, TestClient, _create_encoded_key_database(), _create_rebuilt_database() (+17 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (22): BaseException, Event, profile(), _database(), FakeEngine, _profile(), Path, test_eligibility_stale_reuse_and_idempotent_resume() (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (25): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+17 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (24): migrate_position_key_schema(), Validate the v1 shape accepted by the one-time position-key transition., Reset disposable v1 analysis and queue rows in one transaction., EvaluationSchemaError, The independently versioned evaluation queue schema is absent or incompatible., _existing_tables(), initialize_evaluation_schema(), _position_key_queue_index() (+16 more)

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (20): AnalysisCandidate, candidate(), completed_at(), connection(), fixture, Path, _create_v1_schema(), Connection (+12 more)

### Community 21 - "Community 21"
Cohesion: 0.28
Nodes (19): client(), _database(), fixture, MonkeyPatch, parametrize, Path, TestClient, test_browsing_list_does_not_modify_database() (+11 more)

### Community 22 - "Community 22"
Cohesion: 0.20
Nodes (12): AnalysisProfile, _canonical_json(), ResultEligibility, AnalysisRepository, PositionKey, Inspect many exact-FEN identities in bounded read-only queries., Recheck current eligibility immediately before dispatching work., work_positions() (+4 more)

### Community 23 - "Community 23"
Cohesion: 0.22
Nodes (16): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+8 more)

### Community 24 - "Community 24"
Cohesion: 0.16
Nodes (13): close_process(), _engine_shutdown_poll(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, PythonChessProcess, Bounded, idempotent graceful quit with a tracked-process-only fallback. (+5 more)

### Community 25 - "Community 25"
Cohesion: 0.35
Nodes (18): claim_next(), enqueue(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., initialized(), Connection, test_claim_is_fifo_and_marks_running(), test_complete_rejects_result_fen_mismatch() (+10 more)

### Community 26 - "Community 26"
Cohesion: 0.29
Nodes (16): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report() (+8 more)

### Community 27 - "Community 27"
Cohesion: 0.20
Nodes (13): _bounded_call(), _candidate(), _convert_result(), Any, Managed, per-owner Stockfish process and result-conversion boundary., _required_int(), _score(), AnalysisTimeoutError (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.27
Nodes (14): sha256_file(), Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), ProvisionedStockfish, Path (+6 more)

### Community 29 - "Community 29"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 30 - "Community 30"
Cohesion: 0.25
Nodes (13): AnalysisSchemaError, The independently versioned analysis schema is absent or incompatible., _existing_tables(), initialize_analysis_schema(), Connection, Explicit initialization for the independent analysis schema., Create the analysis namespace only through this explicit operation., Require the complete supported schema without creating or repairing it. (+5 more)

### Community 31 - "Community 31"
Cohesion: 0.19
Nodes (10): AnalysisResult, canonical_fen(), position_key_from_fen(), PositionKey, Return the internal identity without changing the public six-field FEN., Return a strict canonical six-field FEN or reject it., Return the internal four-field identity for a valid canonical six-field FEN., PositionKey (+2 more)

### Community 32 - "Community 32"
Cohesion: 0.25
Nodes (11): build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection., Inspect the corpus and analysis rows without opening a writer transaction. (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (6): AnalysisEngine, Protocol, _close_engine(), _EngineRegistry, EngineFactory, One engine per worker thread; workers never receive the SQLite connection.

### Community 34 - "Community 34"
Cohesion: 0.20
Nodes (5): EngineProcess, Board, Limit, Protocol, Only the process operations the managed boundary is allowed to use.

### Community 35 - "Community 35"
Cohesion: 0.38
Nodes (9): _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences(), Connection, Path, Deterministic, strictly read-only selection of the frozen benchmark fixtures., Select four hash-ordered unique placements from each frozen ply band. (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.22
Nodes (8): _analyse_one(), _close_engine(), _EngineRegistry, _error_code(), BaseException, Exception, dispatch(), _WorkerFailure

### Community 37 - "Community 37"
Cohesion: 0.28
Nodes (6): _begin_immediate(), _is_busy(), Connection, Error, Append one immutable batch summary and its final failures atomically., Atomically publish a completely validated result and all candidate rows.

### Community 38 - "Community 38"
Cohesion: 0.29
Nodes (3): ManagedStockfish, One non-shareable engine instance intended to be owned by one future worker., Immediately terminate this tracked child for the second Ctrl+C level.

### Community 39 - "Community 39"
Cohesion: 0.57
Nodes (7): _basis(), _database(), _profile(), Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen(), test_preflight_counts_projection_and_hash_memory_without_mutation()

### Community 40 - "Community 40"
Cohesion: 0.60
Nodes (4): _assert_expected_operation_ids(), Focused proof for the served API contract., test_docs_and_served_openapi_remain_available(), test_served_schema_remains_full_with_only_clean_operationid_changes()

### Community 42 - "Community 42"
Cohesion: 0.67
Nodes (3): MonkeyPatch, test_real_database_caro_reached_scope_includes_deeper_variation(), test_real_database_training_requirement_anchor()

## Knowledge Gaps
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_rebuilt_database_path()` connect `Community 3` to `Community 0`, `Community 5`, `Community 10`, `Community 12`, `Community 13`, `Community 14`, `Community 21`?**
  _High betweenness centrality (0.305) - this node is a cross-community bridge._
- **Why does `get_game()` connect `Community 14` to `Community 3`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `AnalysisProfile` connect `Community 22` to `Community 32`, `Community 36`, `Community 38`, `Community 6`, `Community 8`, `Community 39`, `Community 11`, `Community 17`, `Community 20`, `Community 23`, `Community 26`, `Community 27`, `Community 31`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `_convert_result()`) actually correct?**
  _`AnalysisProfile` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `AnalysisValidationError` (e.g. with `ManagedStockfish` and `AnalysisCandidate`) actually correct?**
  _`AnalysisValidationError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `AnalysisRepository` (e.g. with `AnalysisBusyError` and `AnalysisProfile`) actually correct?**
  _`AnalysisRepository` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AnalysisResult` (e.g. with `_serialize_result()` and `ManagedStockfish`) actually correct?**
  _`AnalysisResult` has 11 INFERRED edges - model-reasoned connections that need verification._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
