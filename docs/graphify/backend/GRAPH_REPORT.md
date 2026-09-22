# Graph Report - backend  (2026-09-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1414 nodes · 3358 edges · 99 communities (53 shown, 46 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 343 edges (avg confidence: 0.87)
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
- Community 74
- Community 75
- Community 76
- Community 77
- Community 81
- Community 82
- Community 87
- Community 88
- Community 90
- Community 91
- Community 92
- Community 93
- Community 98

## God Nodes (most connected - your core abstractions)
1. `AnalysisValidationError` - 34 edges
2. `AnalysisProfile` - 32 edges
3. `get_or_compute()` - 30 edges
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
- `FakeProcess` --uses--> `EngineIdentity`  [INFERRED]
  tests/features/analysis/test_engine.py → app/features/analysis/engine.py
- `complete_result()` --calls--> `AnalysisCandidate`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/models.py
- `_real_python_chess_process()` --uses--> `EngineIdentity`  [INFERRED]
  tests/features/analysis/test_engine.py → app/features/analysis/engine.py

## Import Cycles
- None detected.

## Communities (99 total, 46 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (61): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (52): Thin HTTP translation layer for desired current analysis., health(), get, HealthResponse, BaseModel, create_app(), backend_app_dependencies, backend_app_features_analysis_observation_router (+44 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (48): backend_app_features_preferred_moves_router, concurrent_futures, api_context(), client(), create_preferred_moves_database(), delete_body(), put_body(), fixture (+40 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (51): ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse, CategoryPerformanceResponse, ContractModel, DataQualityStatisticsResponse, GameStatisticsResponse, HourActivityResponse (+43 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (44): backend_app_features_openings_catalogue_api_schemas, backend_app_features_statistics_router, chess_move_trainer_database_reporting, fixture, MonkeyPatch, parametrize, Path, pydantic (+36 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (42): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResult, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisObservationErrorResponse (+34 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (41): EvaluationLockError, EvaluationQueueError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits., A queue state-machine transition is invalid for the current state. (+33 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (33): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisBusyError, AnalysisTimeoutError, EngineLifecycleError, RuntimeError, A node-limited engine call exceeded its independent wall-clock watchdog., A tracked engine process could not be started or stopped safely., A short coordinator SQLite transaction could not acquire its lock. (+25 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (40): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+32 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (34): AnalysisEngine, AnalysisRepository, _canonical(), _close_engine(), _drain(), dispatch(), _EngineRegistry, _evaluate_one() (+26 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (25): asyncio, backend_app_features_analysis_engine, _EventLoopTransportStub, FakeProcess, managed(), Board, Limit, parametrize (+17 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (34): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+26 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (33): analysis_key(), _current_signature(), game_detail_key(), games_key(), opening_detail_key(), openings_catalogue_version(), openings_key(), position_insight_key() (+25 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (27): BaseException, backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult (+19 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (28): Path, Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), backend_app_features_evaluation, completed_at(), connection(), database_path(), AnalysisResult (+20 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (30): Serialize one response model exactly like Starlette's JSONResponse., serialize_response_body(), OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel (+22 more)

### Community 16 - "Community 16"
Cohesion: 0.25
Nodes (30): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, statistics, _database_info(), _float_env(), _int_env(), _output_dir(), MonkeyPatch (+22 more)

### Community 17 - "Community 17"
Cohesion: 0.16
Nodes (23): get_or_compute(), Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., SingleFlightTimeoutError, _namespace(), Path, test_concurrent_identical_misses_compute_once(), worker() (+15 more)

### Community 18 - "Community 18"
Cohesion: 0.22
Nodes (23): get_rebuilt_database_path(), Path, Return the explicit clean database path for the current application process., chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, client(), _database(), MonkeyPatch (+15 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (24): AnalysisSchemaError, The independently versioned analysis schema is absent or incompatible., AnalysisCandidate, _existing_tables(), initialize_analysis_schema(), migrate_position_key_schema(), Connection, Explicit initialization for the independent analysis schema. (+16 more)

### Community 20 - "Community 20"
Cohesion: 0.13
Nodes (24): json_response(), Wrap one cached or freshly computed payload in a fresh response., _detail_payload(), _detail_response(), _games_error(), get_game(), get_games(), _page_response() (+16 more)

### Community 21 - "Community 21"
Cohesion: 0.14
Nodes (23): close_process(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, Bounded, idempotent graceful quit with a tracked-process-only fallback., sha256_file(), _download() (+15 more)

### Community 22 - "Community 22"
Cohesion: 0.15
Nodes (15): AnalysisProfile, _canonical_json(), position_key_from_fen(), PositionKey, Return the internal identity without changing the public six-field FEN., Return the internal four-field identity for a valid canonical six-field FEN., ResultEligibility, AnalysisRepository (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (15): AnalysisLockError, Another top-level analysis operator owns the database lock., AnalysisRunLock, Path, A single OS-owned lock for one top-level analysis invocation., Hold a one-byte lock whose lifetime is tied to an open OS file handle., InterruptController, EngineFactory (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.21
Nodes (21): EvaluationSchemaError, The independently versioned evaluation queue schema is absent or incompatible., _existing_tables(), initialize_evaluation_schema(), _position_key_queue_index(), _position_key_queue_table(), Connection, Explicit initialization for the independent evaluation queue schema. (+13 more)

### Community 25 - "Community 25"
Cohesion: 0.28
Nodes (22): claim_next(), enqueue(), observe(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Read-only queue state for one exact FEN; never computes., Return (queued, running) counts for observability and drain control. (+14 more)

### Community 26 - "Community 26"
Cohesion: 0.20
Nodes (18): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+10 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (17): canonical_fen(), Return a strict canonical six-field FEN or reject it., backend_app_features_analysis, completed_at(), connection(), profile(), fixture, Path (+9 more)

### Community 28 - "Community 28"
Cohesion: 0.21
Nodes (20): backend_tests_benchmarks_test_api_benchmark, math, needs_real_database, _open_real_client(), MonkeyPatch, Path, TestClient, Real-database API benchmarks (opt-in, read-only). Covers the gaps named in the… (+12 more)

### Community 29 - "Community 29"
Cohesion: 0.19
Nodes (17): backend_tests_features_analysis_observation_conftest, chess_move_trainer_database_stockfish, _position_id(), _post(), MonkeyPatch, parametrize, Path, _queue_row() (+9 more)

### Community 30 - "Community 30"
Cohesion: 0.19
Nodes (14): _params(), MonkeyPatch, parametrize, Path, _target_position_id(), test_bad_values_give_clear_error(), test_injected_database_is_used_when_configured(), test_known_position_returns_full_insight_and_ignores_unknown_filters() (+6 more)

### Community 31 - "Community 31"
Cohesion: 0.14
Nodes (15): AnalysisCandidate, Any, _bounded_call(), _candidate(), _convert_result(), AnalysisResult, Managed, per-owner Stockfish process and result-conversion boundary., _required_int() (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.21
Nodes (14): BenchmarkFixture, _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences(), Connection, Path, Deterministic, strictly read-only selection of the frozen benchmark fixtures. (+6 more)

### Community 33 - "Community 33"
Cohesion: 0.19
Nodes (12): MonkeyPatch, parametrize, Path, _queue(), _remove_result(), _target_position_id(), test_injected_database_is_used_when_configured(), test_missing_or_bad_position_gives_clear_error() (+4 more)

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (12): Persisted backend analysis contracts., build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection. (+4 more)

### Community 35 - "Community 35"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.16
Nodes (13): _configured_float(), get_training_requirement_policy(), TrainingRequirementPolicy, Application dependencies for database capabilities., Return the configured policy, or ``None`` when the capability is unavailable., chess_move_trainer_database_lifecycle, chess_move_trainer_database_positions, datetime (+5 more)

### Community 37 - "Community 37"
Cohesion: 0.34
Nodes (14): canonical_write(), _cleanup_proof(), execute_benchmark(), freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report(), _profile() (+6 more)

### Community 38 - "Community 38"
Cohesion: 0.28
Nodes (14): Connection, api_context(), client(), create_insight_database(), _game(), _install_analysis(), _install_opening(), _install_preferences() (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 40 - "Community 40"
Cohesion: 0.23
Nodes (13): GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel, GamesResponse, GameSummaryResponse, OpeningSummaryResponse (+5 more)

### Community 41 - "Community 41"
Cohesion: 0.22
Nodes (12): backend_app_caching, chess_move_trainer_database, sqlite3, api_context(), client(), create_cache_database(), _isolated_caches(), fixture (+4 more)

### Community 42 - "Community 42"
Cohesion: 0.21
Nodes (12): backend_tests_features_position_insight_conftest, chess, json, pathlib, api_context(), client(), _complete_analysis_result(), fixture (+4 more)

### Community 43 - "Community 43"
Cohesion: 0.20
Nodes (5): EngineProcess, Only the process operations the managed boundary is allowed to use., Board, Limit, Protocol

### Community 44 - "Community 44"
Cohesion: 0.31
Nodes (10): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+2 more)

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (5): _engine_shutdown_poll(), PythonChessProcess, Bounded synchronous proof that a python-chess child is shut down and exited.…, A tracked python-chess process; termination is limited to its own transport., SimpleEngine

### Community 46 - "Community 46"
Cohesion: 0.24
Nodes (6): backend_app_main, fastapi_testclient, _assert_expected_operation_ids(), Focused proof for the served API contract., test_docs_and_served_openapi_remain_available(), test_served_schema_remains_full_with_only_clean_operationid_changes()

### Community 47 - "Community 47"
Cohesion: 0.40
Nodes (9): ProjectionBasis, _basis(), _database(), _profile(), AnalysisProfile, Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen() (+1 more)

### Community 48 - "Community 48"
Cohesion: 0.22
Nodes (7): _discard_inflight(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table., ResponseCacheNamespace, Hashable

### Community 49 - "Community 49"
Cohesion: 0.28
Nodes (6): _begin_immediate(), _is_busy(), Connection, Error, Append one immutable batch summary and its final failures atomically., Atomically publish a completely validated result and all candidate rows.

### Community 50 - "Community 50"
Cohesion: 0.33
Nodes (3): ManagedStockfish, AnalysisProfile, One non-shareable engine instance intended to be owned by one future worker.

### Community 51 - "Community 51"
Cohesion: 0.38
Nodes (6): api_context(), client(), fixture, MonkeyPatch, Path, TestClient

### Community 52 - "Community 52"
Cohesion: 0.40
Nodes (5): benchmark_client(), benchmark_database(), create_benchmark_database(), fixture, Build one small database that serves every synthetic benchmark case.

## Knowledge Gaps
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `initialized()` connect `Community 25` to `Community 24`, `Community 9`, `Community 19`, `Community 14`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `run_session()` connect `Community 14` to `Community 6`, `Community 9`, `Community 19`, `Community 23`, `Community 24`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06144393241167435 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06927551560021153 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
