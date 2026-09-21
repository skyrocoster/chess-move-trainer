# Graph Report - backend  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1409 nodes · 3339 edges · 89 communities (51 shown, 38 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 342 edges (avg confidence: 0.87)
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
- Community 71
- Community 72
- Community 73
- Community 82
- Community 83
- Community 84

## God Nodes (most connected - your core abstractions)
1. `AnalysisValidationError` - 34 edges
2. `AnalysisProfile` - 32 edges
3. `get_or_compute()` - 30 edges
4. `ContractModel` - 28 edges
5. `require_evaluation_schema()` - 28 edges
6. `AnalysisRepository` - 27 edges
7. `enqueue()` - 27 edges
8. `initialized()` - 27 edges
9. `position_key_from_fen()` - 26 edges
10. `count_reader_calls()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_typed_score_wdl_and_canonical_fen_validation()` --calls--> `canonical_fen()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/models.py
- `test_incompatible_schema_is_refused_without_repair()` --calls--> `initialize_analysis_schema()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/schema.py
- `test_run_and_failure_records_are_append_only()` --calls--> `initialize_analysis_schema()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/schema.py
- `test_preflight_counts_projection_and_hash_memory_without_mutation()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_corpus_preflight.py → app/features/analysis/repository.py
- `test_repository_reports_sqlite_busy_without_replacing_old_result()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_operator.py → app/features/analysis/repository.py

## Import Cycles
- None detected.

## Communities (89 total, 38 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (64): json_response(), Serialize one response model exactly like Starlette's JSONResponse., Wrap one cached or freshly computed payload in a fresh response., serialize_response_body(), GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse (+56 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (61): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+53 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (44): api_context(), client(), create_preferred_moves_database(), delete_body(), put_body(), fixture, MonkeyPatch, Path (+36 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (50): ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse, CategoryPerformanceResponse, ContractModel, DataQualityStatisticsResponse, GameStatisticsResponse, HourActivityResponse (+42 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (49): needs_real_database, statistics, benchmark_client(), benchmark_database(), create_benchmark_database(), _database_info(), _float_env(), _int_env() (+41 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (43): EvaluationLockError, EvaluationQueueError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits., A queue state-machine transition is invalid for the current state. (+35 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (40): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResult, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisObservationErrorResponse (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (37): backend_app_features_openings_router, importlib, count_reader_calls(), Wrap one router-level reader so tests can count underlying invocations., MonkeyPatch, Path, TestClient, test_games_distinct_filters_use_distinct_keys() (+29 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (26): asyncio, backend_app_features_analysis_engine, chess_engine, _EventLoopTransportStub, FakeProcess, managed(), Board, Limit (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (33): AnalysisEngine, AnalysisRepository, _canonical(), _close_engine(), _drain(), dispatch(), _EngineRegistry, _evaluate_one() (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (31): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+23 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (38): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+30 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (36): analysis_key(), _current_signature(), game_detail_key(), games_key(), opening_detail_key(), openings_catalogue_version(), openings_key(), position_insight_key() (+28 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (31): backend_tests_features_analysis_observation_conftest, chess_move_trainer_database_stockfish, api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path (+23 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (30): backend_app_features_analysis, ProjectionBasis, candidate(), completed_at(), connection(), profile(), fixture, Path (+22 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (21): AnalysisCandidate, AnalysisProfile, canonical_fen(), _canonical_json(), position_key_from_fen(), PositionKey, Validated value objects for persisted Stockfish analysis., Return the internal identity without changing the public six-field FEN. (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (33): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+25 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (26): BaseException, backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (27): AnalysisBusyError, A short coordinator SQLite transaction could not acquire its lock., AnalysisResult, AnalysisRepository, _begin_immediate(), FinalPositionFailure, _is_busy(), Connection (+19 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (27): backend_app_features_openings_catalogue_api_schemas, MonkeyPatch, parametrize, Path, pydantic, api_context(), create_openings_database(), fixture (+19 more)

### Community 20 - "Community 20"
Cohesion: 0.13
Nodes (26): close_process(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, Bounded, idempotent graceful quit with a tracked-process-only fallback., sha256_file(), Pinned Stockfish provisioning or executable verification failed safely. (+18 more)

### Community 21 - "Community 21"
Cohesion: 0.16
Nodes (22): Path, Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), _db(), _factory(), factory(), FakeEngine, AnalysisProfile (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.24
Nodes (21): chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, client(), _database(), fixture, MonkeyPatch, parametrize, Path (+13 more)

### Community 23 - "Community 23"
Cohesion: 0.20
Nodes (22): Validate the v1 shape accepted by the one-time position-key transition., EvaluationSchemaError, The independently versioned evaluation queue schema is absent or incompatible., _existing_tables(), initialize_evaluation_schema(), _position_key_queue_index(), _position_key_queue_table(), Connection (+14 more)

### Community 24 - "Community 24"
Cohesion: 0.16
Nodes (18): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, Connection, fixture, TestClient, api_context(), client(), create_statistics_database() (+10 more)

### Community 25 - "Community 25"
Cohesion: 0.24
Nodes (19): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report() (+11 more)

### Community 26 - "Community 26"
Cohesion: 0.19
Nodes (16): Thin HTTP translation layer for current analysis observation., Thin HTTP translation layer for desired current analysis., HTTP routes for the opening catalogue., Thin HTTP translation layer for one position insight., HTTP contracts for position training requirements., Thin HTTP translation layer for scored position training requirements., create_app(), backend_app_caching (+8 more)

### Community 27 - "Community 27"
Cohesion: 0.20
Nodes (18): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+10 more)

### Community 28 - "Community 28"
Cohesion: 0.30
Nodes (20): claim_next(), enqueue(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Return (queued, running) counts for observability and drain control., initialized(), Connection (+12 more)

### Community 29 - "Community 29"
Cohesion: 0.13
Nodes (15): backend_app_main, backend_tests_benchmarks_test_api_benchmark, chess_move_trainer_database_lifecycle, fastapi_testclient, math, os, sqlite3, Real-database API benchmarks (opt-in, read-only). Covers the gaps named in the… (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.12
Nodes (13): backend_app_features_analysis_requests_router, backend_app_features_games_router, backend_app_features_health_router, backend_app_features_position_insight_router, backend_app_features_position_training_requirements_router, backend_app_features_preferred_moves_router, backend_app_features_statistics_router, backend_tests_features_position_insight_conftest (+5 more)

### Community 31 - "Community 31"
Cohesion: 0.19
Nodes (14): _params(), MonkeyPatch, parametrize, Path, _target_position_id(), test_bad_values_give_clear_error(), test_injected_database_is_used_when_configured(), test_known_position_returns_full_insight_and_ignores_unknown_filters() (+6 more)

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (11): AnalysisLockError, AnalysisTimeoutError, EngineLifecycleError, RuntimeError, A node-limited engine call exceeded its independent wall-clock watchdog., A tracked engine process could not be started or stopped safely., Another top-level analysis operator owns the database lock., AnalysisRunLock (+3 more)

### Community 33 - "Community 33"
Cohesion: 0.19
Nodes (12): MonkeyPatch, parametrize, Path, _queue(), _remove_result(), _target_position_id(), test_injected_database_is_used_when_configured(), test_missing_or_bad_position_gives_clear_error() (+4 more)

### Community 34 - "Community 34"
Cohesion: 0.23
Nodes (15): AnalysisSchemaError, The independently versioned analysis schema is absent or incompatible., _existing_tables(), initialize_analysis_schema(), migrate_position_key_schema(), Connection, Explicit initialization for the independent analysis schema., Create the analysis namespace only through this explicit operation. (+7 more)

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (12): Persisted backend analysis contracts., build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection. (+4 more)

### Community 36 - "Community 36"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 37 - "Community 37"
Cohesion: 0.16
Nodes (13): AnalysisCandidate, Any, _bounded_call(), _candidate(), _convert_result(), AnalysisResult, Managed, per-owner Stockfish process and result-conversion boundary., _required_int() (+5 more)

### Community 38 - "Community 38"
Cohesion: 0.28
Nodes (14): api_context(), client(), create_insight_database(), _game(), _install_analysis(), _install_opening(), _install_preferences(), _occurrence() (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 40 - "Community 40"
Cohesion: 0.19
Nodes (9): InterruptController, EngineFactory, Path, Own the top-level lock, read selected games, then coordinate safe writes., Run the complete accepted-corpus queue after a separately confirmed preflight., Convert the first two SIGINT events into bounded drain and force levels., run_all_positions(), run_selected_games() (+1 more)

### Community 41 - "Community 41"
Cohesion: 0.20
Nodes (5): EngineProcess, Only the process operations the managed boundary is allowed to use., Board, Limit, Protocol

### Community 42 - "Community 42"
Cohesion: 0.22
Nodes (5): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisEngine, _close_engine(), _EngineRegistry, Protocol

### Community 43 - "Community 43"
Cohesion: 0.24
Nodes (10): backend_app_features_evaluation, datetime, completed_at(), connection(), database_path(), AnalysisProfile, AnalysisResult, fixture (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.27
Nodes (10): chess_move_trainer_database, api_context(), client(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path (+2 more)

### Community 45 - "Community 45"
Cohesion: 0.31
Nodes (10): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+2 more)

### Community 46 - "Community 46"
Cohesion: 0.38
Nodes (9): _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences(), Connection, Path, Deterministic, strictly read-only selection of the frozen benchmark fixtures., Select four hash-ordered unique placements from each frozen ply band. (+1 more)

### Community 47 - "Community 47"
Cohesion: 0.22
Nodes (5): _engine_shutdown_poll(), PythonChessProcess, Bounded synchronous proof that a python-chess child is shut down and exited.…, A tracked python-chess process; termination is limited to its own transport., SimpleEngine

### Community 48 - "Community 48"
Cohesion: 0.25
Nodes (8): _configured_float(), get_rebuilt_database_path(), get_training_requirement_policy(), Path, TrainingRequirementPolicy, Application dependencies for database capabilities., Return the explicit clean database path for the current application process., Return the configured policy, or ``None`` when the capability is unavailable.

### Community 49 - "Community 49"
Cohesion: 0.33
Nodes (3): ManagedStockfish, AnalysisProfile, One non-shareable engine instance intended to be owned by one future worker.

### Community 50 - "Community 50"
Cohesion: 0.33
Nodes (4): health(), get, HealthResponse, BaseModel

## Knowledge Gaps
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PythonChessProcess` connect `Community 47` to `Community 37`, `Community 8`, `Community 41`, `Community 20`, `Community 25`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `position_key_from_fen()` connect `Community 15` to `Community 34`, `Community 35`, `Community 5`, `Community 9`, `Community 17`, `Community 18`, `Community 27`, `Community 28`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `get_game()` connect `Community 0` to `Community 10`, `Community 12`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05110809588421529 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
