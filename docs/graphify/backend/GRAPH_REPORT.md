# Graph Report - backend  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1408 nodes · 3338 edges · 82 communities (47 shown, 35 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 341 edges (avg confidence: 0.87)
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
- `test_typed_score_wdl_and_canonical_fen_validation()` --calls--> `canonical_fen()`  [INFERRED]
  tests/features/analysis/test_schema_and_models.py → app/features/analysis/models.py
- `test_preflight_counts_projection_and_hash_memory_without_mutation()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_corpus_preflight.py → app/features/analysis/repository.py
- `test_repository_reports_sqlite_busy_without_replacing_old_result()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_operator.py → app/features/analysis/repository.py
- `test_atomic_stale_replacement_rolls_back_to_old_parent_and_candidates()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/repository.py
- `test_persistence_and_profile_eligibility()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/repository.py

## Import Cycles
- None detected.

## Communities (82 total, 35 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (61): backend_app_features_analysis_observation_router, backend_app_features_analysis_requests_router, backend_app_features_games_router, backend_app_features_health_router, backend_app_features_openings_router, backend_app_features_position_insight_router, backend_app_features_position_training_requirements_router, backend_app_features_preferred_moves_router (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (55): pytest, api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path, TestClient (+47 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (58): backend_app_main, backend_tests_benchmarks_test_api_benchmark, chess_move_trainer_database_lifecycle, math, needs_real_database, os, statistics, benchmark_client() (+50 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (61): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+53 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (51): AnalysisCandidate, Any, canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, _connect_read_only(), _database_guard() (+43 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (47): concurrent_futures, api_context(), client(), create_preferred_moves_database(), delete_body(), put_body(), fixture, MonkeyPatch (+39 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (51): ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse, CategoryPerformanceResponse, ContractModel, DataQualityStatisticsResponse, GameStatisticsResponse, HourActivityResponse (+43 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (40): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+32 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (26): asyncio, backend_app_features_analysis_engine, chess_engine, _EventLoopTransportStub, FakeProcess, managed(), Board, Limit (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (37): EvaluationQueueError, EvaluationValidationError, ValueError, An evaluation request violates strict validation or the bounded size limits., A queue state-machine transition is invalid for the current state., Browser-evaluation service boundary over the durable queue and analysis storage., EvaluationQueueItem, InspectResult (+29 more)

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (30): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+22 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (35): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+27 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (30): ProjectionBasis, sqlite3, candidate(), completed_at(), connection(), profile(), fixture, Path (+22 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (28): AnalysisEngine, AnalysisRepository, _canonical(), _close_engine(), _drain(), dispatch(), _EngineRegistry, _evaluate_one() (+20 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (21): AnalysisCandidate, AnalysisProfile, canonical_fen(), _canonical_json(), position_key_from_fen(), PositionKey, Validated value objects for persisted Stockfish analysis., Return the internal identity without changing the public six-field FEN. (+13 more)

### Community 15 - "Community 15"
Cohesion: 0.13
Nodes (26): BaseException, backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult (+18 more)

### Community 16 - "Community 16"
Cohesion: 0.13
Nodes (26): AnalysisBusyError, A short coordinator SQLite transaction could not acquire its lock., AnalysisResult, AnalysisRepository, _begin_immediate(), FinalPositionFailure, _is_busy(), Connection (+18 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (28): migrate_position_key_schema(), Validate the v1 shape accepted by the one-time position-key transition., Reset disposable v1 analysis and queue rows in one transaction., EvaluationLockError, EvaluationSchemaError, RuntimeError, Typed errors for the browser-evaluation service boundary., The evaluation worker session could not acquire the shared analysis lock. (+20 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (26): inspect(), AnalysisProfile, Path, Return eligibility, persisted result, and queue state without computing., Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), InspectResult, _db() (+18 more)

### Community 19 - "Community 19"
Cohesion: 0.18
Nodes (26): backend_app_features_openings_catalogue_api_schemas, pydantic, api_context(), create_openings_database(), fixture, MonkeyPatch, Path, TestClient (+18 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (29): analysis_key(), game_detail_key(), games_key(), opening_detail_key(), openings_key(), position_insight_key(), preferred_moves_key(), Path (+21 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (26): chess_move_trainer_database, api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture (+18 more)

### Community 22 - "Community 22"
Cohesion: 0.14
Nodes (22): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, chess_move_trainer_database_reporting, Connection, fixture, MonkeyPatch, parametrize, TestClient (+14 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (22): AnalysisLockError, AnalysisSchemaError, AnalysisTimeoutError, EngineLifecycleError, RuntimeError, A node-limited engine call exceeded its independent wall-clock watchdog., A tracked engine process could not be started or stopped safely., Another top-level analysis operator owns the database lock. (+14 more)

### Community 24 - "Community 24"
Cohesion: 0.24
Nodes (21): chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, client(), _database(), fixture, MonkeyPatch, parametrize, Path (+13 more)

### Community 25 - "Community 25"
Cohesion: 0.28
Nodes (22): claim_next(), enqueue(), observe(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Read-only queue state for one exact FEN; never computes., Return (queued, running) counts for observability and drain control. (+14 more)

### Community 26 - "Community 26"
Cohesion: 0.20
Nodes (18): _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games., Build the opening-first PositionKey queue for the complete accepted subject… (+10 more)

### Community 27 - "Community 27"
Cohesion: 0.18
Nodes (20): Serialize one response model exactly like Starlette's JSONResponse., serialize_response_body(), _catalogue_error(), _catalogue_item_response(), _catalogue_page_response(), _detail_payload(), get_opening_by_key(), get_openings() (+12 more)

### Community 28 - "Community 28"
Cohesion: 0.17
Nodes (19): sha256_file(), Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), ProvisionedStockfish, Path (+11 more)

### Community 29 - "Community 29"
Cohesion: 0.19
Nodes (17): backend_tests_features_analysis_observation_conftest, chess_move_trainer_database_stockfish, _position_id(), _post(), MonkeyPatch, parametrize, Path, _queue_row() (+9 more)

### Community 30 - "Community 30"
Cohesion: 0.14
Nodes (13): AnalysisRunLock, Path, Hold a one-byte lock whose lifetime is tied to an open OS file handle., BatchRunResult, InterruptController, EngineFactory, Path, Own the top-level lock, read selected games, then coordinate safe writes. (+5 more)

### Community 31 - "Community 31"
Cohesion: 0.18
Nodes (17): json_response(), Wrap one cached or freshly computed payload in a fresh response., GamesErrorResponse, _detail_payload(), _games_error(), get_game(), get_games(), _page_response() (+9 more)

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (14): _bounded_call(), close_process(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, Managed, per-owner Stockfish process and result-conversion boundary., Bounded, idempotent graceful quit with a tracked-process-only fallback. (+6 more)

### Community 33 - "Community 33"
Cohesion: 0.14
Nodes (15): AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisRequestBody, AnalysisRequestErrorResponse, BaseModel, HTTP contracts for one desired current analysis request., Strict known request fields while tolerating future client fields., Stable error body for the desired-analysis operation. (+7 more)

### Community 34 - "Community 34"
Cohesion: 0.18
Nodes (13): Thin HTTP translation layer for current analysis observation., Thin HTTP translation layer for desired current analysis., Thin HTTP translation layer for package-owned game search., create_app(), backend_app_caching, backend_app_dependencies, backend_app_features_games_api_schemas, chess_move_trainer_database_analysis (+5 more)

### Community 35 - "Community 35"
Cohesion: 0.18
Nodes (15): GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesModel, GamesResponse, GameSummaryResponse, OpeningSummaryResponse, BaseModel (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (14): AnalysisObservationErrorCode, AnalysisObservationResult, AnalysisObservationResultResponse, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, ContractModel (+6 more)

### Community 37 - "Community 37"
Cohesion: 0.25
Nodes (11): build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection., Inspect the corpus and analysis rows without opening a writer transaction. (+3 more)

### Community 38 - "Community 38"
Cohesion: 0.19
Nodes (12): backend_app_features_analysis, backend_app_features_evaluation, chess, datetime, completed_at(), connection(), database_path(), AnalysisProfile (+4 more)

### Community 39 - "Community 39"
Cohesion: 0.20
Nodes (5): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisEngine, _close_engine(), _EngineRegistry, Protocol

### Community 40 - "Community 40"
Cohesion: 0.24
Nodes (11): AnalysisObservation, AnalysisObservationResponse, get_analysis(), observation_response(), Depends, get, get_rebuilt_database_path, Path (+3 more)

### Community 41 - "Community 41"
Cohesion: 0.20
Nodes (5): EngineProcess, Only the process operations the managed boundary is allowed to use., Board, Limit, Protocol

### Community 42 - "Community 42"
Cohesion: 0.22
Nodes (5): _engine_shutdown_poll(), PythonChessProcess, Bounded synchronous proof that a python-chess child is shut down and exited.…, A tracked python-chess process; termination is limited to its own transport., SimpleEngine

### Community 43 - "Community 43"
Cohesion: 0.25
Nodes (8): _configured_float(), get_rebuilt_database_path(), get_training_requirement_policy(), Path, TrainingRequirementPolicy, Application dependencies for database capabilities., Return the explicit clean database path for the current application process., Return the configured policy, or ``None`` when the capability is unavailable.

### Community 44 - "Community 44"
Cohesion: 0.33
Nodes (8): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract.

### Community 45 - "Community 45"
Cohesion: 0.33
Nodes (6): _current_signature(), openings_catalogue_version(), Fingerprint the database main file and SQLite sidecars without creating…, Return a bounded opaque version for the database and SQLite sidecars., Record the current signature; on change for a known path, clear all and return…, _refresh_signature_locked()

### Community 46 - "Community 46"
Cohesion: 0.33
Nodes (4): health(), get, HealthResponse, BaseModel

## Knowledge Gaps
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_or_compute()` connect `Community 10` to `Community 3`, `Community 6`, `Community 7`, `Community 40`, `Community 11`, `Community 45`, `Community 20`, `Community 27`, `Community 31`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `AnalysisRunLock` connect `Community 30` to `Community 16`, `Community 18`, `Community 15`, `Community 23`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `position_key_from_fen()` connect `Community 14` to `Community 9`, `Community 12`, `Community 13`, `Community 15`, `Community 16`, `Community 23`, `Community 25`, `Community 26`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06252587991718427 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
