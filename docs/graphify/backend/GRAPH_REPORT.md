# Graph Report - backend  (2026-09-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1465 nodes · 3496 edges · 101 communities (58 shown, 43 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 348 edges (avg confidence: 0.87)
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
- Community 57
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
- Community 78
- Community 79
- Community 80
- Community 85
- Community 86
- Community 91
- Community 92
- Community 93
- Community 94
- Community 100

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
- `test_preflight_counts_projection_and_hash_memory_without_mutation()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_corpus_preflight.py → app/features/analysis/repository.py
- `test_repository_reports_sqlite_busy_without_replacing_old_result()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_operator.py → app/features/analysis/repository.py
- `test_atomic_stale_replacement_rolls_back_to_old_parent_and_candidates()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/repository.py
- `test_persistence_and_profile_eligibility()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_persistence.py → app/features/analysis/repository.py
- `test_new_position_key_schema_dedupes_counter_variants()` --calls--> `AnalysisRepository`  [INFERRED]
  tests/features/analysis/test_position_key_migration.py → app/features/analysis/repository.py

## Import Cycles
- None detected.

## Communities (101 total, 43 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (76): Serialize one response model exactly like Starlette's JSONResponse., serialize_response_body(), get_rebuilt_database_path(), Path, Return the explicit clean database path for the current application process., ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse (+68 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (61): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+53 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (52): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, backend_tests_benchmarks_test_api_benchmark, math, needs_real_database, statistics, benchmark_client(), benchmark_database() (+44 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (44): api_context(), client(), create_preferred_moves_database(), delete_body(), put_body(), fixture, MonkeyPatch, Path (+36 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (42): backend_app_features_openings_catalogue_api_schemas, fixture, MonkeyPatch, parametrize, Path, TestClient, api_context(), create_openings_database() (+34 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (40): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResult, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisObservationErrorResponse (+32 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (35): AnalysisEngine, AnalysisRepository, EvaluationValidationError, ValueError, An evaluation request violates strict validation or the bounded size limits., _canonical(), _close_engine(), _drain() (+27 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (36): AnalysisSchemaError, The independently versioned analysis schema is absent or incompatible., _existing_tables(), initialize_analysis_schema(), migrate_position_key_schema(), Connection, Explicit initialization for the independent analysis schema., Create the analysis namespace only through this explicit operation. (+28 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (38): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+30 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (33): GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel, GamesResponse, GameSummaryResponse, OpeningSummaryResponse (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (31): backend_tests_features_analysis_observation_conftest, chess_move_trainer_database_stockfish, api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path (+23 more)

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (32): count_reader_calls(), Wrap one router-level reader so tests can count underlying invocations., MonkeyPatch, Path, TestClient, test_games_distinct_filters_use_distinct_keys(), test_games_equivalent_inputs_share_one_key(), test_games_error_responses_are_never_cached() (+24 more)

### Community 12 - "Community 12"
Cohesion: 0.13
Nodes (27): BaseException, backend_app_features_analysis_selection, Event, _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult (+19 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (33): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+25 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (32): analysis_key(), game_detail_key(), games_key(), opening_detail_key(), openings_key(), position_insight_key(), preferred_moves_key(), BlunderPolicy (+24 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (28): AnalysisBusyError, A short coordinator SQLite transaction could not acquire its lock., AnalysisResult, AnalysisRepository, _begin_immediate(), FinalPositionFailure, _is_busy(), Connection (+20 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (23): backend_app_features_analysis_requests_router, backend_app_features_games_router, backend_app_features_health_router, backend_app_features_openings_router, backend_app_features_position_insight_router, backend_app_features_position_training_requirements_router, backend_app_features_statistics_router, backend_app_features_trainer_blunders_router (+15 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (22): AnalysisLockError, AnalysisTimeoutError, EngineLifecycleError, RuntimeError, A node-limited engine call exceeded its independent wall-clock watchdog., A tracked engine process could not be started or stopped safely., Another top-level analysis operator owns the database lock., Persisted backend analysis contracts. (+14 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (28): EvaluationQueueError, A queue state-machine transition is invalid for the current state., EvaluationQueueItem, PositionKey, Return the internal queue identity while retaining the public six-field FEN., _begin_immediate(), _canonical(), operation() (+20 more)

### Community 19 - "Community 19"
Cohesion: 0.14
Nodes (25): inspect(), Return eligibility, persisted result, and queue state without computing., InspectResult, completed_at(), AnalysisResult, result_for(), _db(), _factory() (+17 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (21): asyncio, backend_app_features_analysis_engine, _EventLoopTransportStub, managed(), parametrize, Minimal asyncio.SubprocessTransport-shaped stub with a mutable return code., Real asyncio event that fails loudly if lifecycle code ever awaits it., SimpleEngine-shaped stub whose shutdown flag is a real asyncio.Event. (+13 more)

### Community 21 - "Community 21"
Cohesion: 0.24
Nodes (21): chess_move_trainer_database_games_normalization, chess_move_trainer_database_games_persistence, client(), _database(), fixture, MonkeyPatch, parametrize, Path (+13 more)

### Community 22 - "Community 22"
Cohesion: 0.13
Nodes (20): AnalysisCandidate, Any, _bounded_call(), _candidate(), close_process(), EngineIdentity, _identity(), inspect_stockfish_executable() (+12 more)

### Community 23 - "Community 23"
Cohesion: 0.28
Nodes (22): claim_next(), enqueue(), observe(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Read-only queue state for one exact FEN; never computes., Return (queued, running) counts for observability and drain control. (+14 more)

### Community 24 - "Community 24"
Cohesion: 0.19
Nodes (16): Thin HTTP translation layer for current analysis observation., Thin HTTP translation layer for desired current analysis., HTTP routes for the opening catalogue., Thin HTTP translation layer for one position insight., HTTP contracts for position training requirements., Thin HTTP translation layer for scored position training requirements., create_app(), backend_app_caching (+8 more)

### Community 25 - "Community 25"
Cohesion: 0.19
Nodes (17): Strictly read-only corpus-wide selection and resource projection., _accepted_game(), _game_occurrences(), GameSelectionError, Connection, RuntimeError, Read-only accepted-game selection and PositionKey eligibility inspection., Build one PositionKey queue from every ply of explicit accepted games. (+9 more)

### Community 26 - "Community 26"
Cohesion: 0.15
Nodes (20): Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), ProvisionedStockfish, Path, Explicit, pinned, checksum-first Stockfish provisioning without import effects. (+12 more)

### Community 27 - "Community 27"
Cohesion: 0.16
Nodes (13): AnalysisProfile, position_key_from_fen(), PositionKey, Return the internal identity without changing the public six-field FEN., Return the internal four-field identity for a valid canonical six-field FEN., ResultEligibility, PositionKey, Inspect many exact-FEN identities in bounded read-only queries. (+5 more)

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (17): EvaluationLockError, EvaluationSchemaError, RuntimeError, Typed errors for the browser-evaluation service boundary., The evaluation worker session could not acquire the shared analysis lock., The independently versioned evaluation queue schema is absent or incompatible., Browser-evaluation service boundary over the durable queue and analysis storage., InspectResult (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.15
Nodes (17): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+9 more)

### Community 30 - "Community 30"
Cohesion: 0.17
Nodes (19): json_response(), Wrap one cached or freshly computed payload in a fresh response., _catalogue_error(), _catalogue_item_response(), _catalogue_page_response(), _detail_payload(), get_opening_by_key(), get_openings() (+11 more)

### Community 31 - "Community 31"
Cohesion: 0.21
Nodes (14): concurrent_futures, _namespace(), Path, test_concurrent_identical_misses_compute_once(), worker(), test_failed_leader_wakes_waiters_without_caching(), boom(), worker() (+6 more)

### Community 32 - "Community 32"
Cohesion: 0.29
Nodes (16): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, freeze_from_v1_report(), freeze_report(), _install_metadata(), load_frozen_report() (+8 more)

### Community 33 - "Community 33"
Cohesion: 0.27
Nodes (17): Validate the v1 shape accepted by the one-time position-key transition., _existing_tables(), initialize_evaluation_schema(), Connection, Create the evaluation queue namespace only through this explicit operation., Require the complete supported evaluation schema without creating or repairing…, require_evaluation_schema(), _require_legacy_evaluation_schema() (+9 more)

### Community 34 - "Community 34"
Cohesion: 0.19
Nodes (14): _params(), MonkeyPatch, parametrize, Path, _target_position_id(), test_bad_values_give_clear_error(), test_injected_database_is_used_when_configured(), test_known_position_returns_full_insight_and_ignores_unknown_filters() (+6 more)

### Community 35 - "Community 35"
Cohesion: 0.18
Nodes (11): _convert_result(), AnalysisResult, AnalysisValidationError, ValueError, An analysis profile or complete result violates the persistence contract., AnalysisCandidate, canonical_fen(), _canonical_json() (+3 more)

### Community 36 - "Community 36"
Cohesion: 0.19
Nodes (12): MonkeyPatch, parametrize, Path, _queue(), _remove_result(), _target_position_id(), test_injected_database_is_used_when_configured(), test_missing_or_bad_position_gives_clear_error() (+4 more)

### Community 37 - "Community 37"
Cohesion: 0.16
Nodes (14): _configured_float(), get_blunder_policy(), get_training_requirement_policy(), BlunderPolicy, TrainingRequirementPolicy, Application dependencies for database capabilities., Return the configured policy, or ``None`` when the capability is unavailable., Return the configured blunder threshold, or ``None`` when invalid. (+6 more)

### Community 38 - "Community 38"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 39 - "Community 39"
Cohesion: 0.25
Nodes (12): backend_app_features_trainer_blunders, _params(), MonkeyPatch, Path, test_black_filter_excludes_white_trainer_game(), test_configured_threshold_controls_discovery(), test_discovery_returns_trainer_ready_blunder_without_writing(), test_identical_reads_are_cached_but_pagination_uses_a_distinct_key() (+4 more)

### Community 40 - "Community 40"
Cohesion: 0.28
Nodes (14): Connection, api_context(), client(), create_insight_database(), _game(), _install_analysis(), _install_opening(), _install_preferences() (+6 more)

### Community 41 - "Community 41"
Cohesion: 0.36
Nodes (13): duration_summary(), evaluate_runs(), _mate_winner(), nearest_rank(), Any, Versioned Stockfish qualification calculations., Apply the frozen v2 gate using only reference evaluations for loss., _repeatable() (+5 more)

### Community 42 - "Community 42"
Cohesion: 0.20
Nodes (5): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisEngine, _close_engine(), _EngineRegistry, Protocol

### Community 43 - "Community 43"
Cohesion: 0.26
Nodes (10): build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Inspect the corpus and analysis rows without opening a writer transaction., Open a database with SQLite's read-only immutable URI and perform no locking or… (+2 more)

### Community 44 - "Community 44"
Cohesion: 0.20
Nodes (5): EngineProcess, Only the process operations the managed boundary is allowed to use., Board, Limit, Protocol

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
Cohesion: 0.29
Nodes (9): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract. (+1 more)

### Community 49 - "Community 49"
Cohesion: 0.20
Nodes (4): backend_app_features_preferred_moves_router, backend_app_main, parametrize, test_put_bad_values_give_clear_error()

### Community 50 - "Community 50"
Cohesion: 0.40
Nodes (9): ProjectionBasis, _basis(), _database(), _profile(), AnalysisProfile, Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen() (+1 more)

### Community 51 - "Community 51"
Cohesion: 0.31
Nodes (9): api_context(), client(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path, TestClient (+1 more)

### Community 52 - "Community 52"
Cohesion: 0.22
Nodes (4): FakeProcess, Board, Limit, test_process_checksum_identity_is_required()

### Community 53 - "Community 53"
Cohesion: 0.32
Nodes (7): backend_app_features_evaluation, chess, datetime, connection(), database_path(), fixture, Path

### Community 54 - "Community 54"
Cohesion: 0.33
Nodes (3): ManagedStockfish, AnalysisProfile, One non-shareable engine instance intended to be owned by one future worker.

### Community 55 - "Community 55"
Cohesion: 0.52
Nodes (6): _add_analysis(), api_context(), create_blunder_database(), MonkeyPatch, Path, _raw_game()

### Community 56 - "Community 56"
Cohesion: 0.33
Nodes (6): _current_signature(), openings_catalogue_version(), Fingerprint the database main file and SQLite sidecars without creating…, Return a bounded opaque version for the database and SQLite sidecars., Record the current signature; on change for a known path, clear all and return…, _refresh_signature_locked()

### Community 57 - "Community 57"
Cohesion: 0.33
Nodes (4): health(), get, HealthResponse, BaseModel

## Knowledge Gaps
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `position_key_from_fen()` connect `Community 27` to `Community 35`, `Community 6`, `Community 7`, `Community 12`, `Community 15`, `Community 17`, `Community 18`, `Community 23`, `Community 25`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `_complete_analysis_result()` connect `Community 10` to `Community 16`, `Community 36`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `_response()` connect `Community 13` to `Community 24`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AnalysisValidationError` (e.g. with `AnalysisCandidate` and `AnalysisProfile`) actually correct?**
  _`AnalysisValidationError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `AnalysisProfile` (e.g. with `_run_budget()` and `AnalysisValidationError`) actually correct?**
  _`AnalysisProfile` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `get_or_compute()` (e.g. with `get_analysis()` and `get_game()`) actually correct?**
  _`get_or_compute()` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06550632911392405 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
