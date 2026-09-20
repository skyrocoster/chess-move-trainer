# Graph Report - backend  (2026-09-19)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1297 nodes · 3082 edges · 83 communities (56 shown, 27 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 344 edges (avg confidence: 0.87)
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
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
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

## God Nodes (most connected - your core abstractions)
1. `AnalysisProfile` - 38 edges
2. `AnalysisValidationError` - 34 edges
3. `AnalysisRepository` - 34 edges
4. `require_evaluation_schema()` - 29 edges
5. `get_or_compute()` - 29 edges
6. `enqueue()` - 28 edges
7. `initialized()` - 28 edges
8. `position_key_from_fen()` - 26 edges
9. `run_batch()` - 24 edges
10. `claim_next()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `FakeProcess` --uses--> `EngineIdentity`  [INFERRED]
  tests/features/analysis/test_engine.py → app/features/analysis/engine.py
- `_real_python_chess_process()` --uses--> `EngineIdentity`  [INFERRED]
  tests/features/analysis/test_engine.py → app/features/analysis/engine.py
- `_namespace()` --uses--> `ResponseCacheNamespace`  [INFERRED]
  tests/features/api_cache/test_cache_mechanics.py → app/caching.py
- `test_missing_database_file_never_gets_created()` --uses--> `ResponseCacheNamespace`  [INFERRED]
  tests/features/api_cache/test_cache_mechanics.py → app/caching.py
- `test_catalogue_response_rejects_extra_fields()` --calls--> `OpeningCatalogueResponse`  [INFERRED]
  tests/features/openings/test_catalogue_api.py → app/features/openings/catalogue_api_schemas.py

## Import Cycles
- None detected.

## Communities (83 total, 27 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (61): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (46): api_context(), client(), create_preferred_moves_database(), delete_body(), put_body(), fixture, MonkeyPatch, Path (+38 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (53): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, backend_tests_benchmarks_test_api_benchmark, math, needs_real_database, benchmark_client(), benchmark_database(), create_benchmark_database() (+45 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (45): EvaluationLockError, EvaluationQueueError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits., A queue state-machine transition is invalid for the current state. (+37 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (40): backend_app_features_openings_router, importlib, api_context(), client(), count_reader_calls(), create_cache_database(), _isolated_caches(), fixture (+32 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (35): AnalysisBusyError, A short coordinator SQLite transaction could not acquire its lock., AnalysisRepository, _begin_immediate(), FinalPositionFailure, _is_busy(), Connection, Error (+27 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (39): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+31 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (26): asyncio, backend_app_features_analysis_engine, chess_engine, _EventLoopTransportStub, FakeProcess, managed(), Board, Limit (+18 more)

### Community 8 - "Community 8"
Cohesion: 0.12
Nodes (32): _canonical(), inspect(), Connection, Path, Read and fully validate a persisted result; never computes., Return eligibility, persisted result, and queue state without computing., Perform one deliberate Analyze, Update, or Retry action., Own the shared analysis lock, requeue interrupted work, then drain the queue.… (+24 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (32): AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisRequestBody, AnalysisRequestErrorResponse, BaseModel, HTTP contracts for one desired current analysis request., Strict known request fields while tolerating future client fields., Stable error body for the desired-analysis operation. (+24 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (27): BaseException, backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult (+19 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (33): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+25 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (29): analysis_key(), _current_signature(), game_detail_key(), games_key(), opening_detail_key(), openings_catalogue_version(), position_insight_key(), preferred_moves_key() (+21 more)

### Community 13 - "Community 13"
Cohesion: 0.19
Nodes (26): backend_app_features_openings_catalogue_api_schemas, pydantic, api_context(), create_openings_database(), fixture, MonkeyPatch, Path, TestClient (+18 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (23): canonical_fen(), Return a strict canonical six-field FEN or reject it., candidate(), completed_at(), connection(), profile(), fixture, Path (+15 more)

### Community 15 - "Community 15"
Cohesion: 0.15
Nodes (19): _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences(), Connection, Path, Deterministic, strictly read-only selection of the frozen benchmark fixtures., Select four hash-ordered unique placements from each frozen ply band. (+11 more)

### Community 16 - "Community 16"
Cohesion: 0.24
Nodes (21): chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, client(), _database(), fixture, MonkeyPatch, parametrize, Path (+13 more)

### Community 17 - "Community 17"
Cohesion: 0.20
Nodes (22): Validate the v1 shape accepted by the one-time position-key transition., EvaluationSchemaError, The independently versioned evaluation queue schema is absent or incompatible., _existing_tables(), initialize_evaluation_schema(), _position_key_queue_index(), _position_key_queue_table(), Connection (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.16
Nodes (18): concurrent_futures, os, _namespace(), Path, test_concurrent_identical_misses_compute_once(), worker(), test_failed_leader_wakes_waiters_without_caching(), boom() (+10 more)

### Community 19 - "Community 19"
Cohesion: 0.14
Nodes (19): Any, _bounded_call(), _candidate(), close_process(), _engine_shutdown_poll(), EngineIdentity, _identity(), inspect_stockfish_executable() (+11 more)

### Community 20 - "Community 20"
Cohesion: 0.20
Nodes (18): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+10 more)

### Community 21 - "Community 21"
Cohesion: 0.15
Nodes (20): Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), ProvisionedStockfish, Path, Explicit, pinned, checksum-first Stockfish provisioning without import effects. (+12 more)

### Community 22 - "Community 22"
Cohesion: 0.30
Nodes (20): claim_next(), enqueue(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Return (queued, running) counts for observability and drain control., initialized(), Connection (+12 more)

### Community 23 - "Community 23"
Cohesion: 0.19
Nodes (15): Thin HTTP translation layer for current analysis observation., Thin HTTP translation layer for desired current analysis., Thin HTTP translation layer for package-owned game search., Thin HTTP translation layer for one position insight., create_app(), backend_app_caching, backend_app_dependencies, backend_app_features_games_api_schemas (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.15
Nodes (19): json_response(), openings_key(), Serialize one response model exactly like Starlette's JSONResponse., Canonical key from the validated catalogue query and resolved database., Wrap one cached or freshly computed payload in a fresh response., serialize_response_body(), get_rebuilt_database_path(), Path (+11 more)

### Community 25 - "Community 25"
Cohesion: 0.16
Nodes (14): backend_app_features_analysis_observation_router, json, MonkeyPatch, parametrize, Path, _queue(), _remove_result(), _target_position_id() (+6 more)

### Community 26 - "Community 26"
Cohesion: 0.16
Nodes (16): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+8 more)

### Community 27 - "Community 27"
Cohesion: 0.29
Nodes (16): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report() (+8 more)

### Community 28 - "Community 28"
Cohesion: 0.19
Nodes (14): _params(), MonkeyPatch, parametrize, Path, _target_position_id(), test_bad_values_give_clear_error(), test_injected_database_is_used_when_configured(), test_known_position_returns_full_insight_and_ignores_unknown_filters() (+6 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (15): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract. (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.17
Nodes (11): AnalysisLockError, AnalysisTimeoutError, EngineLifecycleError, RuntimeError, A node-limited engine call exceeded its independent wall-clock watchdog., A tracked engine process could not be started or stopped safely., Another top-level analysis operator owns the database lock., AnalysisRunLock (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.23
Nodes (15): AnalysisSchemaError, The independently versioned analysis schema is absent or incompatible., _existing_tables(), initialize_analysis_schema(), migrate_position_key_schema(), Connection, Explicit initialization for the independent analysis schema., Create the analysis namespace only through this explicit operation. (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.25
Nodes (12): Persisted backend analysis contracts., build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection. (+4 more)

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (15): GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesModel, GamesResponse, GameSummaryResponse, OpeningSummaryResponse, BaseModel (+7 more)

### Community 34 - "Community 34"
Cohesion: 0.17
Nodes (14): api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path, TestClient, Extend the shared position-insight fixture to a complete five-line result. (+6 more)

### Community 35 - "Community 35"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.16
Nodes (7): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisResult, AnalysisEngine, _close_engine(), _EngineRegistry, Protocol, _persist_with_busy_retry()

### Community 37 - "Community 37"
Cohesion: 0.15
Nodes (11): _close_engine(), dispatch(), _EngineRegistry, _evaluate_one(), BaseException, EngineFactory, Exception, A worker item failed permanently; no automatic retry is performed. (+3 more)

### Community 38 - "Community 38"
Cohesion: 0.28
Nodes (14): api_context(), client(), create_insight_database(), _game(), _install_analysis(), _install_opening(), _install_preferences(), _occurrence() (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 40 - "Community 40"
Cohesion: 0.23
Nodes (14): GamesErrorResponse, _detail_payload(), _games_error(), get_game(), get_games(), _page_response(), Depends, get (+6 more)

### Community 41 - "Community 41"
Cohesion: 0.24
Nodes (12): chess_move_trainer_database, chess_move_trainer_database_positions, api_context(), client(), create_training_database(), _game(), _occurrence(), Connection (+4 more)

### Community 42 - "Community 42"
Cohesion: 0.23
Nodes (11): AnalysisObservationErrorCode, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, ContractModel, BaseModel, Strict HTTP contracts for one current analysis observation. (+3 more)

### Community 43 - "Community 43"
Cohesion: 0.20
Nodes (5): EngineProcess, Board, Limit, Only the process operations the managed boundary is allowed to use., Protocol

### Community 44 - "Community 44"
Cohesion: 0.29
Nodes (10): backend_app_features_games_router, backend_app_features_position_insight_router, backend_tests_features_position_insight_conftest, fastapi_testclient, MonkeyPatch, Path, TestClient, test_repeated_analysis_reads_share_cached_payloads() (+2 more)

### Community 45 - "Community 45"
Cohesion: 0.27
Nodes (5): _convert_result(), ManagedStockfish, AnalysisProfile, AnalysisResult, One non-shareable engine instance intended to be owned by one future worker.

### Community 46 - "Community 46"
Cohesion: 0.22
Nodes (7): position_key_from_fen(), PositionKey, Return the internal identity without changing the public six-field FEN., Return the internal four-field identity for a valid canonical six-field FEN., PositionKey, PositionKey, Return the internal queue identity while retaining the public six-field FEN.

### Community 47 - "Community 47"
Cohesion: 0.24
Nodes (9): backend_app_features_analysis, backend_app_features_evaluation, chess, datetime, completed_at(), connection(), database_path(), fixture (+1 more)

### Community 48 - "Community 48"
Cohesion: 0.40
Nodes (9): ProjectionBasis, _basis(), _database(), _profile(), AnalysisProfile, Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen() (+1 more)

### Community 49 - "Community 49"
Cohesion: 0.28
Nodes (5): backend_app_main, _assert_expected_operation_ids(), Focused proof for the served API contract., test_docs_and_served_openapi_remain_available(), test_served_schema_remains_full_with_only_clean_operationid_changes()

### Community 50 - "Community 50"
Cohesion: 0.32
Nodes (8): AnalysisObservation, AnalysisObservationResponse, AnalysisObservationResult, AnalysisObservationResultResponse, observation_response(), Build the public observation body; shared with the request endpoint., _response(), _result_response()

### Community 51 - "Community 51"
Cohesion: 0.36
Nodes (4): ResultEligibility, PositionKey, Inspect many exact-FEN identities in bounded read-only queries., StrEnum

### Community 52 - "Community 52"
Cohesion: 0.33
Nodes (6): chess_move_trainer_database_lifecycle, pytest, sqlite3, MonkeyPatch, test_real_database_caro_reached_scope_includes_deeper_variation(), test_real_database_training_requirement_anchor()

### Community 53 - "Community 53"
Cohesion: 0.40
Nodes (5): _configured_float(), get_training_requirement_policy(), TrainingRequirementPolicy, Application dependencies for database capabilities., Return the configured policy, or ``None`` when the capability is unavailable.

### Community 55 - "Community 55"
Cohesion: 0.33
Nodes (6): get_analysis(), Depends, get, get_rebuilt_database_path, Path, Query

### Community 56 - "Community 56"
Cohesion: 0.33
Nodes (4): health(), get, HealthResponse, BaseModel

## Knowledge Gaps
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AnalysisProfile` connect `Community 15` to `Community 32`, `Community 3`, `Community 5`, `Community 37`, `Community 8`, `Community 14`, `Community 51`, `Community 20`, `Community 27`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `clear_caches()` connect `Community 2` to `Community 0`, `Community 4`, `Community 6`, `Community 9`, `Community 12`, `Community 18`, `Community 26`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `AnalysisRepository` (e.g. with `AnalysisBusyError` and `AnalysisProfile`) actually correct?**
  _`AnalysisRepository` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `require_evaluation_schema()` (e.g. with `test_v1_transition_resets_disposable_rows_and_preserves_history()` and `test_coexists_with_analysis_schema()`) actually correct?**
  _`require_evaluation_schema()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 20 INFERRED edges - model-reasoned connections that need verification._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
