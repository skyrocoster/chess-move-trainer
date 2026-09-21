# Graph Report - backend  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1465 nodes · 3486 edges · 88 communities (48 shown, 40 thin omitted)
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
- Community 47
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
- Community 79
- Community 80
- Community 81
- Community 87

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
- `test_incompatible_schema_is_refused_without_repair()` --calls--> `initialize_analysis_schema()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/schema.py
- `test_run_and_failure_records_are_append_only()` --calls--> `initialize_analysis_schema()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/schema.py
- `test_typed_score_wdl_and_canonical_fen_validation()` --calls--> `canonical_fen()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/models.py
- `FakeProcess` --uses--> `EngineIdentity`  [INFERRED]
  tests/features/analysis/test_engine.py → app/features/analysis/engine.py
- `test_lock_refuses_concurrent_operator_and_is_released_on_close()` --calls--> `AnalysisRunLock`  [INFERRED]
  tests/features/analysis/test_operator.py → app/features/analysis/locking.py

## Import Cycles
- None detected.

## Communities (88 total, 40 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (68): Thin HTTP translation layer for desired current analysis., health(), get, HealthResponse, BaseModel, create_app(), backend_app_caching, backend_app_features_analysis_observation_router (+60 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (72): ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse, CategoryPerformanceResponse, ContractModel, DataQualityStatisticsResponse, GameStatisticsResponse, HourActivityResponse (+64 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (67): _configured_float(), get_blunder_policy(), get_rebuilt_database_path(), get_training_requirement_policy(), BlunderPolicy, Path, TrainingRequirementPolicy, Application dependencies for database capabilities. (+59 more)

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
Cohesion: 0.09
Nodes (47): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, backend_app_features_openings_catalogue_api_schemas, backend_app_features_statistics_router, chess_move_trainer_database_reporting, Connection, fixture, MonkeyPatch (+39 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (42): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResult, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisObservationErrorResponse (+34 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (40): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+32 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (30): Immediately terminate this tracked child for the second Ctrl+C level., EngineLifecycleError, A tracked engine process could not be started or stopped safely., AnalysisResult, FinalPositionFailure, _analyse_one(), AnalysisEngine, BatchRunResult (+22 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (38): analysis_key(), _current_signature(), game_detail_key(), games_key(), opening_detail_key(), openings_catalogue_version(), openings_key(), position_insight_key() (+30 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (30): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+22 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (32): backend_app_features_analysis, ProjectionBasis, candidate(), completed_at(), connection(), profile(), fixture, Path (+24 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (29): BaseException, Own the top-level lock, read selected games, then coordinate safe writes., run_selected_games(), backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile() (+21 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (34): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+26 more)

### Community 15 - "Community 15"
Cohesion: 0.16
Nodes (29): chess_move_trainer_database, chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, chess_move_trainer_database_games_reading, client(), _database(), fixture, MonkeyPatch (+21 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (25): AnalysisEngine, AnalysisRepository, _close_engine(), _drain(), dispatch(), _EngineRegistry, _evaluate_one(), _persist_with_busy_retry() (+17 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (26): inspect(), AnalysisProfile, Path, Return eligibility, persisted result, and queue state without computing., Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), InspectResult, _db() (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (21): asyncio, backend_app_features_analysis_engine, FakeProcess, managed(), Board, Limit, parametrize, SimpleEngine-shaped stub whose shutdown flag is a real asyncio.Event. (+13 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (26): json_response(), Serialize one response model exactly like Starlette's JSONResponse., Wrap one cached or freshly computed payload in a fresh response., serialize_response_body(), _detail_payload(), _detail_response(), _games_error(), get_game() (+18 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (19): AnalysisLockError, AnalysisSchemaError, Another top-level analysis operator owns the database lock., The independently versioned analysis schema is absent or incompatible., Persisted backend analysis contracts., AnalysisRunLock, Path, A single OS-owned lock for one top-level analysis invocation. (+11 more)

### Community 21 - "Community 21"
Cohesion: 0.16
Nodes (26): EvaluationQueueError, A queue state-machine transition is invalid for the current state., EvaluationQueueItem, _begin_immediate(), _canonical(), operation(), complete(), operation() (+18 more)

### Community 22 - "Community 22"
Cohesion: 0.20
Nodes (22): migrate_position_key_schema(), Validate the v1 shape accepted by the one-time position-key transition., Reset disposable v1 analysis and queue rows in one transaction., _existing_tables(), initialize_evaluation_schema(), _position_key_queue_index(), _position_key_queue_table(), Connection (+14 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (21): EvaluationLockError, EvaluationSchemaError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits., The evaluation worker session could not acquire the shared analysis lock. (+13 more)

### Community 24 - "Community 24"
Cohesion: 0.23
Nodes (19): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report() (+11 more)

### Community 25 - "Community 25"
Cohesion: 0.14
Nodes (22): sha256_file(), RuntimeError, Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), ProvisionedStockfish (+14 more)

### Community 26 - "Community 26"
Cohesion: 0.28
Nodes (22): claim_next(), enqueue(), observe(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Read-only queue state for one exact FEN; never computes., Return (queued, running) counts for observability and drain control. (+14 more)

### Community 27 - "Community 27"
Cohesion: 0.20
Nodes (18): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+10 more)

### Community 28 - "Community 28"
Cohesion: 0.19
Nodes (12): AnalysisCandidate, AnalysisProfile, _canonical_json(), Validated value objects for persisted Stockfish analysis., ResultEligibility, AnalysisRepository, PositionKey, Inspect many exact-FEN identities in bounded read-only queries. (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.18
Nodes (18): backend_app_features_analysis_requests_router, backend_tests_features_analysis_observation_conftest, chess_move_trainer_database_stockfish, _position_id(), _post(), MonkeyPatch, parametrize, Path (+10 more)

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (17): _catalogue_error(), _catalogue_item_response(), _catalogue_page_response(), _detail_payload(), get_opening_by_key(), get_openings(), _opening_detail_error(), Depends (+9 more)

### Community 31 - "Community 31"
Cohesion: 0.17
Nodes (11): close_process(), _engine_shutdown_poll(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, PythonChessProcess, Bounded, idempotent graceful quit with a tracked-process-only fallback. (+3 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (14): AnalysisCandidate, Any, _bounded_call(), _candidate(), _convert_result(), AnalysisResult, Managed, per-owner Stockfish process and result-conversion boundary., _required_int() (+6 more)

### Community 33 - "Community 33"
Cohesion: 0.14
Nodes (12): AnalysisTimeoutError, A node-limited engine call exceeded its independent wall-clock watchdog., canonical_fen(), position_key_from_fen(), PositionKey, Return the internal identity without changing the public six-field FEN., Return a strict canonical six-field FEN or reject it., Return the internal four-field identity for a valid canonical six-field FEN. (+4 more)

### Community 34 - "Community 34"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (12): backend_app_features_trainer_blunders, _params(), MonkeyPatch, Path, test_black_filter_excludes_white_trainer_game(), test_configured_threshold_controls_discovery(), test_discovery_returns_trainer_ready_blunder_without_writing(), test_identical_reads_are_cached_but_pagination_uses_a_distinct_key() (+4 more)

### Community 36 - "Community 36"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 37 - "Community 37"
Cohesion: 0.25
Nodes (11): build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection., Inspect the corpus and analysis rows without opening a writer transaction. (+3 more)

### Community 38 - "Community 38"
Cohesion: 0.23
Nodes (13): GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel, GamesResponse, GameSummaryResponse, OpeningSummaryResponse (+5 more)

### Community 39 - "Community 39"
Cohesion: 0.23
Nodes (9): AnalysisBusyError, A short coordinator SQLite transaction could not acquire its lock., _begin_immediate(), _is_busy(), Connection, Error, Append one immutable batch summary and its final failures atomically., Atomically publish a completely validated result and all candidate rows. (+1 more)

### Community 40 - "Community 40"
Cohesion: 0.20
Nodes (5): EngineProcess, Only the process operations the managed boundary is allowed to use., Board, Limit, Protocol

### Community 41 - "Community 41"
Cohesion: 0.31
Nodes (10): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+2 more)

### Community 42 - "Community 42"
Cohesion: 0.38
Nodes (9): _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences(), Connection, Path, Deterministic, strictly read-only selection of the frozen benchmark fixtures., Select four hash-ordered unique placements from each frozen ply band. (+1 more)

### Community 43 - "Community 43"
Cohesion: 0.29
Nodes (9): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract. (+1 more)

### Community 44 - "Community 44"
Cohesion: 0.27
Nodes (9): backend_app_features_evaluation, chess, completed_at(), connection(), database_path(), AnalysisResult, fixture, Path (+1 more)

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (6): backend_app_main, pytest, sqlite3, MonkeyPatch, test_real_database_caro_reached_scope_includes_deeper_variation(), test_real_database_training_requirement_anchor()

### Community 46 - "Community 46"
Cohesion: 0.22
Nodes (4): _EventLoopTransportStub, Minimal asyncio.SubprocessTransport-shaped stub with a mutable return code., Real asyncio event that fails loudly if lifecycle code ever awaits it., _StrictAsyncioEvent

### Community 47 - "Community 47"
Cohesion: 0.33
Nodes (3): ManagedStockfish, AnalysisProfile, One non-shareable engine instance intended to be owned by one future worker.

## Knowledge Gaps
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `initialized()` connect `Community 26` to `Community 17`, `Community 44`, `Community 20`, `Community 22`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `create_insight_database()` connect `Community 3` to `Community 0`, `Community 44`, `Community 29`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `run_session()` connect `Community 17` to `Community 16`, `Community 20`, `Community 21`, `Community 22`, `Community 23`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05379746835443038 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
