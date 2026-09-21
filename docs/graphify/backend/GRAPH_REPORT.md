# Graph Report - backend  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1465 nodes · 3487 edges · 90 communities (47 shown, 43 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 349 edges (avg confidence: 0.87)
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
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
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
- Community 75
- Community 76
- Community 81
- Community 82
- Community 83
- Community 89

## God Nodes (most connected - your core abstractions)
1. `AnalysisValidationError` - 34 edges
2. `AnalysisProfile` - 32 edges
3. `get_or_compute()` - 31 edges
4. `ContractModel` - 28 edges
5. `require_evaluation_schema()` - 28 edges
6. `AnalysisRepository` - 27 edges
7. `enqueue()` - 27 edges
8. `initialized()` - 27 edges
9. `count_reader_calls()` - 26 edges
10. `position_key_from_fen()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `FakeProcess` --uses--> `EngineIdentity`  [INFERRED]
  tests/features/analysis/test_engine.py → app/features/analysis/engine.py
- `complete_result()` --calls--> `AnalysisCandidate`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/models.py
- `test_preflight_counts_projection_and_hash_memory_without_mutation()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_corpus_preflight.py → app/features/analysis/repository.py
- `test_repository_reports_sqlite_busy_without_replacing_old_result()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_operator.py → app/features/analysis/repository.py
- `test_new_position_key_schema_dedupes_counter_variants()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_position_key_migration.py → app/features/analysis/repository.py

## Import Cycles
- None detected.

## Communities (90 total, 43 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (74): Serialize one response model exactly like Starlette's JSONResponse., serialize_response_body(), ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse, CategoryPerformanceResponse, ContractModel, DataQualityStatisticsResponse (+66 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (66): health(), get, HealthResponse, BaseModel, create_app(), backend_app_features_analysis_requests_router, backend_app_features_games_router, backend_app_features_health_router (+58 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (64): _configured_float(), get_blunder_policy(), get_rebuilt_database_path(), get_training_requirement_policy(), BlunderPolicy, Path, TrainingRequirementPolicy, Application dependencies for database capabilities. (+56 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (54): api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path, TestClient, Extend the shared position-insight fixture to a complete five-line result. (+46 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (61): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+53 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (49): backend_app_features_preferred_moves_router, concurrent_futures, json, api_context(), client(), create_preferred_moves_database(), delete_body(), put_body() (+41 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (49): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, backend_app_features_openings_catalogue_api_schemas, backend_app_features_statistics_router, chess_move_trainer_database_reporting, Connection, fixture, MonkeyPatch (+41 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (45): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResult, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisObservationErrorResponse (+37 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (33): AnalysisBusyError, AnalysisLockError, Another top-level analysis operator owns the database lock., A short coordinator SQLite transaction could not acquire its lock., AnalysisRunLock, Path, A single OS-owned lock for one top-level analysis invocation., Hold a one-byte lock whose lifetime is tied to an open OS file handle. (+25 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (40): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+32 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (25): asyncio, backend_app_features_analysis_engine, _EventLoopTransportStub, FakeProcess, managed(), Board, Limit, parametrize (+17 more)

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (36): AnalysisRepository, Browser-evaluation service boundary over the durable queue and analysis storage., EvaluationQueueItem, InspectResult, Value objects for the durable evaluation queue and evaluation service., A read-only view of one position; never triggers computation., The outcome of one deliberate Analyze, Update, or Retry action., One bounded worker session over the durable queue. (+28 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (38): analysis_key(), _current_signature(), game_detail_key(), games_key(), opening_detail_key(), openings_catalogue_version(), openings_key(), position_insight_key() (+30 more)

### Community 13 - "Community 13"
Cohesion: 0.10
Nodes (35): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+27 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (32): EvaluationLockError, EvaluationQueueError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits., A queue state-machine transition is invalid for the current state. (+24 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (32): GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel, GamesResponse, GameSummaryResponse, OpeningSummaryResponse (+24 more)

### Community 16 - "Community 16"
Cohesion: 0.13
Nodes (26): BaseException, backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult (+18 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (26): Path, Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), completed_at(), AnalysisProfile, AnalysisResult, result_for(), _db() (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (23): _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences(), Connection, Path, Deterministic, strictly read-only selection of the frozen benchmark fixtures., Select four hash-ordered unique placements from each frozen ply band. (+15 more)

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (18): AnalysisProfile, ResultEligibility, AnalysisRepository, _begin_immediate(), _is_busy(), Connection, Error, PositionKey (+10 more)

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (24): migrate_position_key_schema(), Validate the v1 shape accepted by the one-time position-key transition., Reset disposable v1 analysis and queue rows in one transaction., EvaluationSchemaError, The independently versioned evaluation queue schema is absent or incompatible., _existing_tables(), initialize_evaluation_schema(), _position_key_queue_index() (+16 more)

### Community 21 - "Community 21"
Cohesion: 0.28
Nodes (19): client(), _database(), fixture, MonkeyPatch, parametrize, Path, TestClient, test_browsing_list_does_not_modify_database() (+11 more)

### Community 22 - "Community 22"
Cohesion: 0.15
Nodes (21): EngineIdentity, Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), ProvisionedStockfish, Path (+13 more)

### Community 23 - "Community 23"
Cohesion: 0.20
Nodes (18): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+10 more)

### Community 24 - "Community 24"
Cohesion: 0.30
Nodes (20): claim_next(), enqueue(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Return (queued, running) counts for observability and drain control., initialized(), Connection (+12 more)

### Community 25 - "Community 25"
Cohesion: 0.15
Nodes (17): AnalysisCandidate, Any, _bounded_call(), _candidate(), close_process(), _identity(), inspect_stockfish_executable(), Path (+9 more)

### Community 26 - "Community 26"
Cohesion: 0.15
Nodes (17): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+9 more)

### Community 27 - "Community 27"
Cohesion: 0.16
Nodes (19): json_response(), Wrap one cached or freshly computed payload in a fresh response., _catalogue_item_response(), _catalogue_page_response(), _detail_payload(), get_opening_by_key(), get_openings(), Depends (+11 more)

### Community 28 - "Community 28"
Cohesion: 0.19
Nodes (17): backend_tests_features_analysis_observation_conftest, chess_move_trainer_database_stockfish, _position_id(), _post(), MonkeyPatch, parametrize, Path, _queue_row() (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.15
Nodes (18): candidate(), completed_at(), connection(), profile(), fixture, Path, _create_v1_schema(), Connection (+10 more)

### Community 30 - "Community 30"
Cohesion: 0.18
Nodes (17): backend_app_features_analysis, backend_app_features_evaluation, chess, datetime, ProjectionBasis, _basis(), _database(), _profile() (+9 more)

### Community 31 - "Community 31"
Cohesion: 0.29
Nodes (16): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report() (+8 more)

### Community 32 - "Community 32"
Cohesion: 0.14
Nodes (13): backend_app_dependencies, backend_app_main, chess_move_trainer_database, chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, chess_move_trainer_database_games_reading, MonkeyPatch, test_real_database_caro_reached_scope_includes_deeper_variation() (+5 more)

### Community 33 - "Community 33"
Cohesion: 0.23
Nodes (13): _namespace(), Path, test_concurrent_identical_misses_compute_once(), worker(), test_failed_leader_wakes_waiters_without_caching(), boom(), worker(), test_invalidation_during_inflight_read_prevents_stale_publication() (+5 more)

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (12): Persisted backend analysis contracts., build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection. (+4 more)

### Community 35 - "Community 35"
Cohesion: 0.23
Nodes (13): backend_app_features_trainer_blunders, pytest, _params(), MonkeyPatch, Path, test_black_filter_excludes_white_trainer_game(), test_configured_threshold_controls_discovery(), test_discovery_returns_trainer_ready_blunder_without_writing() (+5 more)

### Community 36 - "Community 36"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 37 - "Community 37"
Cohesion: 0.20
Nodes (12): AnalysisSchemaError, RuntimeError, The independently versioned analysis schema is absent or incompatible., _existing_tables(), initialize_analysis_schema(), Connection, Explicit initialization for the independent analysis schema., Create the analysis namespace only through this explicit operation. (+4 more)

### Community 38 - "Community 38"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 39 - "Community 39"
Cohesion: 0.19
Nodes (8): Immediately terminate this tracked child for the second Ctrl+C level., EngineLifecycleError, A tracked engine process could not be started or stopped safely., AnalysisResult, AnalysisEngine, _close_engine(), _EngineRegistry, Protocol

### Community 40 - "Community 40"
Cohesion: 0.18
Nodes (8): AnalysisEngine, _close_engine(), _EngineRegistry, A worker item failed permanently; no automatic retry is performed., One engine per worker thread; workers never receive the SQLite connection., _WorkerFailure, EngineFactory, Exception

### Community 41 - "Community 41"
Cohesion: 0.22
Nodes (12): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract. (+4 more)

### Community 42 - "Community 42"
Cohesion: 0.20
Nodes (5): EngineProcess, Only the process operations the managed boundary is allowed to use., Board, Limit, Protocol

### Community 43 - "Community 43"
Cohesion: 0.31
Nodes (10): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.22
Nodes (5): _engine_shutdown_poll(), PythonChessProcess, Bounded synchronous proof that a python-chess child is shut down and exited.…, A tracked python-chess process; termination is limited to its own transport., SimpleEngine

### Community 45 - "Community 45"
Cohesion: 0.29
Nodes (6): position_key_from_fen(), PositionKey, Return the internal identity without changing the public six-field FEN., Return the internal four-field identity for a valid canonical six-field FEN., PositionKey, test_position_key_normalizes_only_counters_and_requires_public_six_fields()

### Community 46 - "Community 46"
Cohesion: 0.33
Nodes (3): ManagedStockfish, AnalysisProfile, One non-shareable engine instance intended to be owned by one future worker.

## Knowledge Gaps
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AnalysisValidationError` connect `Community 18` to `Community 34`, `Community 39`, `Community 8`, `Community 46`, `Community 19`, `Community 23`, `Community 25`, `Community 31`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `create_insight_database()` connect `Community 3` to `Community 1`, `Community 28`, `Community 30`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `position_key_from_fen()` connect `Community 45` to `Community 34`, `Community 11`, `Community 14`, `Community 48`, `Community 16`, `Community 18`, `Community 19`, `Community 23`, `Community 24`, `Community 29`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06926406926406926 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
