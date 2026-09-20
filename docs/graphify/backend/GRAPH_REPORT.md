# Graph Report - backend  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1320 nodes · 3104 edges · 85 communities (52 shown, 33 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 330 edges (avg confidence: 0.87)
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
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73

## God Nodes (most connected - your core abstractions)
1. `AnalysisValidationError` - 34 edges
2. `AnalysisProfile` - 32 edges
3. `get_or_compute()` - 29 edges
4. `require_evaluation_schema()` - 28 edges
5. `AnalysisRepository` - 27 edges
6. `enqueue()` - 27 edges
7. `initialized()` - 27 edges
8. `position_key_from_fen()` - 26 edges
9. `count_reader_calls()` - 26 edges
10. `run_batch()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `test_typed_score_wdl_and_canonical_fen_validation()` --calls--> `canonical_fen()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/models.py
- `test_incompatible_schema_is_refused_without_repair()` --calls--> `initialize_analysis_schema()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/schema.py
- `test_run_and_failure_records_are_append_only()` --calls--> `initialize_analysis_schema()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/schema.py
- `complete_result()` --calls--> `AnalysisCandidate`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/models.py
- `test_preflight_counts_projection_and_hash_memory_without_mutation()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_corpus_preflight.py → app/features/analysis/repository.py

## Import Cycles
- None detected.

## Communities (85 total, 33 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (61): analysis_key(), _current_signature(), _discard_inflight(), game_detail_key(), games_key(), get_or_compute(), _Inflight, opening_detail_key() (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (54): api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path, TestClient, Extend the shared position-insight fixture to a complete five-line result. (+46 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (61): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+53 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (49): backend_app_features_preferred_moves_router, concurrent_futures, json, api_context(), client(), create_preferred_moves_database(), delete_body(), put_body() (+41 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (54): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, backend_tests_benchmarks_test_api_benchmark, math, needs_real_database, statistics, benchmark_client(), benchmark_database() (+46 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (38): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisBusyError, AnalysisLockError, EngineLifecycleError, RuntimeError, A tracked engine process could not be started or stopped safely., Another top-level analysis operator owns the database lock., A short coordinator SQLite transaction could not acquire its lock. (+30 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (45): EvaluationLockError, EvaluationQueueError, EvaluationSchemaError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits. (+37 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (40): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+32 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (25): asyncio, backend_app_features_analysis_engine, _EventLoopTransportStub, FakeProcess, managed(), Board, Limit, parametrize (+17 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (33): AnalysisEngine, AnalysisRepository, _canonical(), _close_engine(), _drain(), dispatch(), _EngineRegistry, _evaluate_one() (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (26): _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences(), Connection, Path, Deterministic, strictly read-only selection of the frozen benchmark fixtures., Select four hash-ordered unique placements from each frozen ply band. (+18 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (30): inspect(), Return eligibility, persisted result, and queue state without computing., backend_app_features_evaluation, datetime, InspectResult, sqlite3, completed_at(), connection() (+22 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (34): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+26 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (27): BaseException, backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult (+19 more)

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (26): backend_app_features_openings_catalogue_api_schemas, pydantic, api_context(), create_openings_database(), fixture, MonkeyPatch, Path, TestClient (+18 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (15): AnalysisProfile, ResultEligibility, AnalysisRepository, _begin_immediate(), _is_busy(), Connection, Error, PositionKey (+7 more)

### Community 16 - "Community 16"
Cohesion: 0.24
Nodes (21): chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, client(), _database(), fixture, MonkeyPatch, parametrize, Path (+13 more)

### Community 17 - "Community 17"
Cohesion: 0.17
Nodes (19): AnalysisSchemaError, AnalysisTimeoutError, A node-limited engine call exceeded its independent wall-clock watchdog., The independently versioned analysis schema is absent or incompatible., Persisted backend analysis contracts., A single OS-owned lock for one top-level analysis invocation., Transactional persistence for complete current analysis results., _existing_tables() (+11 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (22): Serialize one response model exactly like Starlette's JSONResponse., serialize_response_body(), _detail_payload(), _detail_response(), _games_error(), get_game(), get_games(), _page_response() (+14 more)

### Community 19 - "Community 19"
Cohesion: 0.16
Nodes (21): json_response(), Wrap one cached or freshly computed payload in a fresh response., _catalogue_error(), _catalogue_item_response(), _catalogue_page_response(), _detail_payload(), get_opening_by_key(), get_openings() (+13 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (21): sha256_file(), Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), ProvisionedStockfish, Path (+13 more)

### Community 21 - "Community 21"
Cohesion: 0.22
Nodes (20): Validate the v1 shape accepted by the one-time position-key transition., _existing_tables(), initialize_evaluation_schema(), _position_key_queue_index(), _position_key_queue_table(), Connection, Explicit initialization for the independent evaluation queue schema., Create the evaluation queue namespace only through this explicit operation. (+12 more)

### Community 22 - "Community 22"
Cohesion: 0.20
Nodes (18): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+10 more)

### Community 23 - "Community 23"
Cohesion: 0.29
Nodes (21): claim_next(), enqueue(), observe(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Read-only queue state for one exact FEN; never computes., initialized(), Connection (+13 more)

### Community 24 - "Community 24"
Cohesion: 0.18
Nodes (18): backend_app_features_analysis_requests_router, backend_tests_features_analysis_observation_conftest, chess_move_trainer_database_stockfish, _position_id(), _post(), MonkeyPatch, parametrize, Path (+10 more)

### Community 25 - "Community 25"
Cohesion: 0.29
Nodes (16): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report() (+8 more)

### Community 26 - "Community 26"
Cohesion: 0.17
Nodes (11): close_process(), _engine_shutdown_poll(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, PythonChessProcess, Bounded, idempotent graceful quit with a tracked-process-only fallback. (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.17
Nodes (11): backend_app_dependencies, backend_app_features_position_insight_router, backend_app_main, backend_tests_features_position_insight_conftest, chess_move_trainer_database_lifecycle, fastapi_testclient, os, pytest (+3 more)

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (15): AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisRequestBody, AnalysisRequestErrorResponse, BaseModel, HTTP contracts for one desired current analysis request., Strict known request fields while tolerating future client fields., Stable error body for the desired-analysis operation. (+7 more)

### Community 29 - "Community 29"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.17
Nodes (14): AnalysisObservationErrorCode, AnalysisObservationResult, AnalysisObservationResultResponse, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, ContractModel (+6 more)

### Community 31 - "Community 31"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 32 - "Community 32"
Cohesion: 0.25
Nodes (11): build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection., Inspect the corpus and analysis rows without opening a writer transaction. (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.23
Nodes (13): GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel, GamesResponse, GameSummaryResponse, OpeningSummaryResponse (+5 more)

### Community 34 - "Community 34"
Cohesion: 0.20
Nodes (12): candidate(), connection(), profile(), fixture, Path, _create_v1_schema(), Connection, fixture (+4 more)

### Community 35 - "Community 35"
Cohesion: 0.37
Nodes (12): count_reader_calls(), Wrap one router-level reader so tests can count underlying invocations., MonkeyPatch, Path, TestClient, # NOTE: the feature package __init__ re-exports `router` (the APIRouter), so a, test_database_file_replacement_invalidates_cached_read(), test_distinct_pages_and_policies_use_distinct_keys() (+4 more)

### Community 36 - "Community 36"
Cohesion: 0.23
Nodes (10): Thin HTTP translation layer for current analysis observation., Thin HTTP translation layer for desired current analysis., create_app(), backend_app_caching, backend_app_features_analysis_observation_router, chess_move_trainer_database_analysis, FastAPI, fastapi_responses (+2 more)

### Community 37 - "Community 37"
Cohesion: 0.24
Nodes (12): chess_move_trainer_database, chess_move_trainer_database_positions, api_context(), client(), create_training_database(), _game(), _occurrence(), Connection (+4 more)

### Community 38 - "Community 38"
Cohesion: 0.20
Nodes (11): AnalysisCandidate, Any, _candidate(), Managed, per-owner Stockfish process and result-conversion boundary., _required_int(), _score(), chess_engine, chess_move_trainer_database_stockfish_configuration (+3 more)

### Community 39 - "Community 39"
Cohesion: 0.21
Nodes (6): _bounded_call(), _convert_result(), ManagedStockfish, AnalysisProfile, AnalysisResult, One non-shareable engine instance intended to be owned by one future worker.

### Community 40 - "Community 40"
Cohesion: 0.20
Nodes (10): backend_app_features_analysis, completed_at(), AnalysisCandidate, parametrize, test_illegal_full_pv_is_refused_after_complete_candidate_shape(), test_incompatible_schema_is_refused_without_repair(), test_partial_or_illegal_nonterminal_serialization_is_refused(), test_run_and_failure_records_are_append_only() (+2 more)

### Community 41 - "Community 41"
Cohesion: 0.30
Nodes (11): backend_app_features_openings_router, importlib, MonkeyPatch, Path, TestClient, # NOTE: see test_training_cache.py — the package __init__ shadows `.router`., test_failed_writes_do_not_invalidate_cached_reads(), test_opening_detail_repeat_and_missing_key_behavior() (+3 more)

### Community 42 - "Community 42"
Cohesion: 0.24
Nodes (11): AnalysisObservation, AnalysisObservationResponse, get_analysis(), observation_response(), Depends, get, get_rebuilt_database_path, Path (+3 more)

### Community 43 - "Community 43"
Cohesion: 0.20
Nodes (5): EngineProcess, Only the process operations the managed boundary is allowed to use., Board, Limit, Protocol

### Community 44 - "Community 44"
Cohesion: 0.40
Nodes (9): backend_app_features_games_router, MonkeyPatch, Path, TestClient, test_games_distinct_filters_use_distinct_keys(), test_games_equivalent_inputs_share_one_key(), test_games_error_responses_are_never_cached(), test_games_repeat_reads_underlying_reader_once() (+1 more)

### Community 45 - "Community 45"
Cohesion: 0.35
Nodes (10): chess, ProjectionBasis, _basis(), _database(), _profile(), AnalysisProfile, Path, _result() (+2 more)

### Community 46 - "Community 46"
Cohesion: 0.25
Nodes (8): _configured_float(), get_rebuilt_database_path(), get_training_requirement_policy(), Path, TrainingRequirementPolicy, Application dependencies for database capabilities., Return the explicit clean database path for the current application process., Return the configured policy, or ``None`` when the capability is unavailable.

### Community 47 - "Community 47"
Cohesion: 0.33
Nodes (8): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract.

### Community 48 - "Community 48"
Cohesion: 0.28
Nodes (9): api_context(), client(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path, TestClient (+1 more)

### Community 49 - "Community 49"
Cohesion: 0.33
Nodes (4): health(), get, HealthResponse, BaseModel

### Community 50 - "Community 50"
Cohesion: 0.60
Nodes (6): MonkeyPatch, Path, TestClient, test_repeated_analysis_reads_share_cached_payloads(), test_repeated_insight_reads_share_cached_payloads(), test_repeated_preferred_move_and_game_detail_reads_share_cached_payloads()

### Community 51 - "Community 51"
Cohesion: 0.60
Nodes (4): _assert_expected_operation_ids(), Focused proof for the served API contract., test_docs_and_served_openapi_remain_available(), test_served_schema_remains_full_with_only_clean_operationid_changes()

## Knowledge Gaps
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `position_key_from_fen()` connect `Community 10` to `Community 34`, `Community 6`, `Community 9`, `Community 13`, `Community 15`, `Community 17`, `Community 53`, `Community 22`, `Community 23`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `create_insight_database()` connect `Community 1` to `Community 24`, `Community 50`, `Community 11`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `AnalysisValidationError` connect `Community 10` to `Community 38`, `Community 39`, `Community 15`, `Community 17`, `Community 22`, `Community 25`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `require_evaluation_schema()` (e.g. with `test_v1_transition_resets_disposable_rows_and_preserves_history()` and `test_coexists_with_analysis_schema()`) actually correct?**
  _`require_evaluation_schema()` has 9 INFERRED edges - model-reasoned connections that need verification._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
