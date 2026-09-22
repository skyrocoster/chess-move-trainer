# Graph Report - src  (2026-09-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2361 nodes · 6120 edges · 137 communities (86 shown, 51 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 246 edges (avg confidence: 0.92)
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
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136

## God Nodes (most connected - your core abstractions)
1. `_assert_compatible_schema()` - 42 edges
2. `NormalizedPeriod` - 39 edges
3. `_open_connection()` - 37 edges
4. `_open_existing_connection()` - 36 edges
5. `canonicalize_fen()` - 35 edges
6. `StockfishEngine` - 32 edges
7. `PreferredMoveValidationError` - 29 edges
8. `BenchmarkRunner` - 26 edges
9. `RangeValidationError` - 25 edges
10. `PreferredMoveRepository` - 24 edges

## Surprising Connections (you probably didn't know these)
- `BulkRunner` --uses--> `DatabaseMutex`  [INFERRED]
  chess_move_trainer/database/stockfish/bulk.py → chess_move_trainer/database/stockfish/mutex.py
- `AnalysisObservationRepository` --uses--> `AnalysisReadError`  [INFERRED]
  chess_move_trainer/database/analysis/observation.py → chess_move_trainer/database/analysis/reading.py
- `AnalysisObservationRepository` --uses--> `PositionStorageError`  [INFERRED]
  chess_move_trainer/database/analysis/observation.py → chess_move_trainer/database/positions/repository.py
- `PreferredMoveMutationRequest` --uses--> `PreferredMoveValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/mutations.py → chess_move_trainer/database/preferred_moves/repository.py
- `PreferredMoveRemovalRequest` --uses--> `PreferredMoveValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/mutations.py → chess_move_trainer/database/preferred_moves/repository.py

## Import Cycles
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (137 total, 51 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (77): AnalysisStorageError, Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp() (+69 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (85): activity_statistics(), _average(), _categories(), _category(), data_quality_statistics(), _DatedGame, _duration_seconds(), game_statistics() (+77 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (71): BaseException, Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preference_from_options(), _preferred_period_json(), Shared CLI rendering and error helpers. (+63 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (58): AnalysisState, _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state() (+50 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (53): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+45 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (48): collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus() (+40 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (48): AcquireConfiguration, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url() (+40 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (47): _read_preference(), Public preferred-move schedule values, operations, and storage services., delete_preferred_move(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalRequest, PreferredMoveRemovalResult, put_preferred_move() (+39 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (52): DirEntry, re, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind() (+44 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (40): AnalysisError, AnalysisObservationResult, AnalysisStorageError, AnalysisValidationError, AnalysisReadResult, One current result with all of its ordered candidate lines., Return the Browser < Tool ordering., Return the current complete result for a canonical position. (+32 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (38): _is_lock_failure(), BaseException, _canonical_fen(), _eligible_evidence(), _load_current_aggregate(), date, Path, TrainerColor (+30 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (31): _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database(), MutexBusyError, MutexUnavailableError (+23 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (36): Immutable engine-independent analysis values and input validation., _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationSchemaError (+28 more)

### Community 13 - "Community 13"
Cohesion: 0.10
Nodes (39): Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), inspect_schema(), _pragma_rows() (+31 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (35): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+27 more)

### Community 15 - "Community 15"
Cohesion: 0.08
Nodes (28): PreferredMoveValidationError, ValueError, Raised when preferred-move input is invalid., _append_segment(), _materialize_timeline(), PreferredMoveTimeline, PreferredMoveTimelinePreference, PreferredMoveTimelineRepository (+20 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (29): Board, chess, chess_move_trainer_database_positions, _position_matches(), _provenance(), Resumable game-atomic extraction from a verified frozen snapshot., replay_game(), material() (+21 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (29): AnalysisScoreKind, AnalysisError, AnalysisLine, AnalysisResultInput, AnalysisStorageError, AnalysisValidationError, _FrozenJsonObject, Any (+21 more)

### Community 19 - "Community 19"
Cohesion: 0.14
Nodes (28): Validated canonical chess-position identity services., ValueError, Raised when a policy or discovery request is invalid., Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, TrainingRequirementValidationError, Public training-requirement composition shim., _coerce_date() (+20 more)

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (32): AcquisitionClock, _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Path, Fixed-destination lifecycle services. (+24 more)

### Community 21 - "Community 21"
Cohesion: 0.10
Nodes (27): _find_existing_position_id(), PositionStorageError, CanonicalPosition, RuntimeError, Raised when a compatible position database cannot be used safely., Resolve one canonical position on a caller-owned transaction. This is a…, Find one canonical position without resolving or creating it., _resolve_canonical_position() (+19 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (26): load_positions(), Any, Path, Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark(), BenchmarkError, BenchmarkInputError (+18 more)

### Community 23 - "Community 23"
Cohesion: 0.17
Nodes (24): _load_occurrences(), _load_opening_matches(), _load_preferences(), _load_training_aggregates(), _PositionRecord, _PreferencePeriod, Database row loaders for training-requirement discovery., _TrainingAggregate (+16 more)

### Community 24 - "Community 24"
Cohesion: 0.13
Nodes (17): CataloguePublication, import_opening_catalogue(), OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Atomic publication of normalized opening routes into the v1 catalogue tables. (+9 more)

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (26): argparse, ArgumentParser, Popen, subprocess, sys, build_steps(), classify_result(), _command_text() (+18 more)

### Community 26 - "Community 26"
Cohesion: 0.16
Nodes (26): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), normalize_game(), _normalize_game() (+18 more)

### Community 27 - "Community 27"
Cohesion: 0.17
Nodes (23): NormalizationResult, NormalizationWarning, import_normalized_games(), import_raw_games(), import_raw_month(), import_raw_months(), load_normalized_months(), normalize_raw_games() (+15 more)

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (23): _coverage_state(), DeepestOpening, GameCoverage, GameSearchPage, GameSearchQuery, The selected deepest opening classification for a game., Analysis and preferred-move coverage over distinct game positions., One finite, deterministic page of public game summaries. (+15 more)

### Community 29 - "Community 29"
Cohesion: 0.11
Nodes (19): MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError, TrainerColor, Direct, read-only statistics over normalized game occurrences. (+11 more)

### Community 30 - "Community 30"
Cohesion: 0.14
Nodes (24): _normalized_file_path(), _sha256_file(), _StoredAttempts, BenchmarkCompatibilityError, BenchmarkJob, StockfishProfile, Existing output state does not belong to the requested benchmark., A stable identity for one position/profile/round analysis. (+16 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (17): _is_expected_stockfish(), Path, Verify one explicit executable and terminate it cleanly., verify_stockfish_identity(), The process did not complete the finite UCI startup handshake., The executable did not identify itself as the configured Stockfish version., The verified identity reported by the UCI startup handshake., StockfishIdentity (+9 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (17): _background_result_eligibility_sql(), BulkTarget, BulkTargetSelector, _load_route_moves(), RuntimeError, On-demand, authority-defined Stockfish bulk target selection., Return the shared predicate for missing or stale browser results., Read stable bounded pages and never persist a target list. (+9 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (22): _compare(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCataloguePage, OpeningCatalogueQuery, OpeningCatalogueRepository, OpeningCatalogueValidationError (+14 more)

### Community 34 - "Community 34"
Cohesion: 0.14
Nodes (23): _build_recognition(), lookup_fen(), OpeningInputError, OpeningRecognition, _parse_fen_input(), _parse_pgn_input(), _push_stored_move(), Board (+15 more)

### Community 35 - "Community 35"
Cohesion: 0.11
Nodes (19): _finite_number(), _normalize_range(), parse_calendar_date(), _parse_date(), date, Validated models for read-only position training requirements., Validated read-only discovery controls., One globally scored canonical-position/preferred-move pair. (+11 more)

### Community 36 - "Community 36"
Cohesion: 0.16
Nodes (25): _assert_compatible_schema(), create_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Path, RuntimeError, Transactional creation, compatibility, and explicit schema upgrades. (+17 more)

### Community 37 - "Community 37"
Cohesion: 0.14
Nodes (22): AnalysisRepository, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput, CanonicalPosition (+14 more)

### Community 38 - "Community 38"
Cohesion: 0.12
Nodes (23): _load_games(), Row loaders used by the game search repository., _load_deepest_openings(), _opening_api_key(), _required_int(), comparable_timestamp(), normalize_timestamp_value(), optional_int() (+15 more)

### Community 39 - "Community 39"
Cohesion: 0.12
Nodes (15): _position_identity(), position_transaction(), PositionRepository, _PositionUnitOfWork, Path, PositionIdentity, Permanent canonical-position storage behind an opaque transaction boundary., Open one opaque package-owned transaction for grouped position work. (+7 more)

### Community 40 - "Community 40"
Cohesion: 0.12
Nodes (21): _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _line_from_info(), _metrics_for(), AnalysisLine, AnalysisResultInput (+13 more)

### Community 41 - "Community 41"
Cohesion: 0.13
Nodes (19): AbstractContextManager, binomial_interval(), calibrate(), Path, Seeded method checks with known truth. Not a certificate for the full pipeline., simulate_frame(), design(), fit_once() (+11 more)

### Community 42 - "Community 42"
Cohesion: 0.16
Nodes (21): _load_labels(), _load_usage(), OpeningCatalogueError, OpeningCatalogueSchemaError, OpeningCatalogueStorageError, _OpeningLabel, Read-only, explicit-path browsing of the schema-v1 opening catalogue., Base class for bounded opening-catalogue failures. (+13 more)

### Community 43 - "Community 43"
Cohesion: 0.15
Nodes (20): file_digest(), Path, write_json(), extract(), Path, main(), Finite offline commands; no service or worker lifecycle side effects., load_openings() (+12 more)

### Community 44 - "Community 44"
Cohesion: 0.16
Nodes (18): NormalizedGame, _game_metadata(), GamePersistenceError, GameRepository, _metadata_parameters(), PersistedGame, Any, PositionIdentity (+10 more)

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (16): DirectProof, DirectVerification, Read-only aggregate facts suitable for bounded direct evidence., Whether the retained canonical preference table is empty., Whether the fixed database exposes exactly the catalogue's ten tables., Whether every stored game has a complete ordered occurrence set., Whether every stored route has contiguous one-based move plies., Aggregate integrity facts for the fixed database proof target. (+8 more)

### Community 46 - "Community 46"
Cohesion: 0.17
Nodes (17): Budget, read_json(), build_audit(), category(), iter_records(), Path, Streaming census and measurement-limit report, without association testing., cluster_draw() (+9 more)

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (18): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), _open_existing_connection(), probe_connection(), Path (+10 more)

### Community 48 - "Community 48"
Cohesion: 0.13
Nodes (16): AnalysisQuality, AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, PublicationOutcome, Enum, str, Saved or expected not-saved result for the publication service. (+8 more)

### Community 49 - "Community 49"
Cohesion: 0.18
Nodes (21): _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached(), _load_routes_uncached() (+13 more)

### Community 50 - "Community 50"
Cohesion: 0.15
Nodes (19): _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game, Path, ValueError (+11 more)

### Community 51 - "Community 51"
Cohesion: 0.13
Nodes (14): canonicalize_fen(), Validate a complete six-field FEN and return its canonical identity., _canonical_fen(), _parse_mutation_date(), CanonicalPosition, date, parse_date_literal(), date (+6 more)

### Community 52 - "Community 52"
Cohesion: 0.13
Nodes (20): AnalysisTerminalKind, _classify_board(), classify_terminal_kind(), _neutral_board(), AnalysisLine, AnalysisResultInput, Board, CanonicalPosition (+12 more)

### Community 53 - "Community 53"
Cohesion: 0.18
Nodes (19): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+11 more)

### Community 54 - "Community 54"
Cohesion: 0.28
Nodes (7): _ArtifactPaths, _checkpoint_payload(), BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 55 - "Community 55"
Cohesion: 0.21
Nodes (16): ParsedUciInfo, Stockfish error types and result dataclasses., Stockfish returned malformed or incomplete UCI analysis data., One complete normalized ``info`` payload for a MultiPV line., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int() (+8 more)

### Community 56 - "Community 56"
Cohesion: 0.17
Nodes (15): Stockfish process and database-lock services., BackgroundTargetSelector, Select bounded, all-game-position browser targets in stable order., _finite_non_negative(), _finite_positive(), CanonicalPosition, datetime, Path (+7 more)

### Community 57 - "Community 57"
Cohesion: 0.12
Nodes (16): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkFailure, BulkInputError, _prepend(), AnalysisResultInput, RuntimeError (+8 more)

### Community 58 - "Community 58"
Cohesion: 0.20
Nodes (13): _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), BaseException, OSError, Atomic artifact persistence for benchmarks., Benchmark loading and top-level invocation. (+5 more)

### Community 59 - "Community 59"
Cohesion: 0.29
Nodes (14): GameSearchValidationError, ValueError, Raised when a game-search query is invalid., Game search query models., _normalize_fen(), _normalize_timestamp(), _parse_opening_key(), datetime (+6 more)

### Community 60 - "Community 60"
Cohesion: 0.23
Nodes (13): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions. (+5 more)

### Community 61 - "Community 61"
Cohesion: 0.26
Nodes (8): Any, Drain current queued/reclaimable work and then exit., Resolve the engine profile, pinning threads in parallel mode., Atomically claim one browser target after confirming the queue is empty., One isolated request failure retained only in the launch outcome., Drain queued requests with one engine process per worker runner., WorkerFailure, WorkerRunner

### Community 62 - "Community 62"
Cohesion: 0.19
Nodes (12): AnalysisReadError, AnalysisReadRepository, _line_from_row(), _materialize_result(), AnalysisLine, Path, RuntimeError, Read the complete current analysis result and candidate lines. (+4 more)

### Community 63 - "Community 63"
Cohesion: 0.21
Nodes (11): _compare_games(), _compare_nullable(), _matches(), Game search matching, sorting, and coverage., _GameData, GameSummary, A public game summary that deliberately contains no SQLite identifiers., _in_datetime_bounds() (+3 more)

### Community 64 - "Community 64"
Cohesion: 0.16
Nodes (10): BulkRunner, Any, Path, Analyze eligible targets one at a time and publish each result immediately., InitialAnalysisTargetSelector, Path, ValueError, Raised when target paging or limit input is invalid. (+2 more)

### Community 65 - "Community 65"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 66 - "Community 66"
Cohesion: 0.26
Nodes (7): ArtifactWriter, AtomicArtifactWriter, Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 67 - "Community 67"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 68 - "Community 68"
Cohesion: 0.26
Nodes (10): digest(), prepare_frame(), catalogue_inventory(), freeze_registry(), Path, Question, questions(), Closed, outcome-independent contrast registry and complete source inventory. (+2 more)

### Community 69 - "Community 69"
Cohesion: 0.24
Nodes (10): CanonicalPosition, GameSearchError, GameSearchSchemaError, GameSearchStorageError, Exception, RuntimeError, Game search error types., Raised when a compatible game database cannot be read safely. (+2 more)

### Community 70 - "Community 70"
Cohesion: 0.25
Nodes (9): discover_training_requirements(), Path, Discover scored requirements from one explicit existing database., Discover scored position/preferred-move pairs without writing storage., Return one deterministic page of globally scored current pairs., TrainingRequirementRepository, TrainingRequirementPage, TrainingRequirementPolicy (+1 more)

### Community 71 - "Community 71"
Cohesion: 0.18
Nodes (7): BulkOutcome, Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption., Observable result of one finite worker launch., Whether this finite launch completed without failures or interruption., WorkerOutcome

### Community 72 - "Community 72"
Cohesion: 0.27
Nodes (6): The Stockfish child process stopped or could not accept a command., StockfishProcessError, AnalysisQuality, CanonicalPosition, StockfishProfile, Analyze one canonical position with a fixed-node profile. The only chess search…

### Community 73 - "Community 73"
Cohesion: 0.22
Nodes (6): Finite budgets and explicit, atomic local artifact IO., Offline, reproducible chess evidence; never imported by the HTTP application., Protocol, Frozen defaults. Changing any definition changes the protocol identity., json, time

### Community 74 - "Community 74"
Cohesion: 0.20
Nodes (7): profile_for(), AnalysisQuality, One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile

### Community 75 - "Community 75"
Cohesion: 0.22
Nodes (7): InitialTechnicalPosition, Board, CanonicalPosition, Return the canonical position consumed by the engine., One stable technical representative in the initial-analysis preset., Return the canonical identity represented by the fixed FEN., _record_route_position()

### Community 76 - "Community 76"
Cohesion: 0.29
Nodes (5): _aggregate_games(), WHERE fragments and parameters derived from one validated query., Translate provably safe scalar and EXISTS filters into SQL., _sql_filter_clauses(), _SqlFilters

### Community 77 - "Community 77"
Cohesion: 0.33
Nodes (6): _clock_date(), date, UtcCalendarDateClock, Clock and SQLite lock helpers for training-answer submission., _utc_today(), datetime

### Community 78 - "Community 78"
Cohesion: 0.33
Nodes (7): Exception, RuntimeError, Base class for bounded training-requirement failures., Raised when persisted training state is newer than the requested date., TrainingRequirementError, TrainingRequirementSchemaError, TrainingRequirementStaleError

### Community 79 - "Community 79"
Cohesion: 0.29
Nodes (4): BenchmarkSpec, Any, Validated, deterministic matrix inputs for one benchmark run., Enumerate every job once in the recorded deterministic order.

### Community 80 - "Community 80"
Cohesion: 0.33
Nodes (6): AcquisitionResult, Raised internally when one setup composition step is incomplete., _require_game_acquisition(), _require_opening_acquisition(), SetupError, OpeningAcquisitionResult

### Community 81 - "Community 81"
Cohesion: 0.33
Nodes (4): _BulkImportAbort, Exception, Path, Carry one ordinary import failure out of the bulk transaction.

### Community 82 - "Community 82"
Cohesion: 0.33
Nodes (6): RuntimeError, Base class for bounded Stockfish process or protocol failures., The per-analysis watchdog expired before Stockfish returned bestmove., StockfishError, StockfishWatchdogError, TimeoutError

### Community 83 - "Community 83"
Cohesion: 0.40
Nodes (3): CanonicalPosition, Return the immutable four-field identity of the final position., Alias for the immutable final-position identity.

### Community 84 - "Community 84"
Cohesion: 0.40
Nodes (4): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis

### Community 85 - "Community 85"
Cohesion: 0.50
Nodes (3): chunk_sorted_ids(), Small, dependency-neutral helpers for bounded database queries., Return sorted unique integer identifiers in non-empty bounded chunks.

## Knowledge Gaps
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_assert_compatible_schema()` connect `Community 36` to `Community 0`, `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 9`, `Community 10`, `Community 12`, `Community 16`, `Community 21`, `Community 24`, `Community 28`, `Community 29`, `Community 32`, `Community 37`, `Community 39`, `Community 43`, `Community 44`, `Community 45`, `Community 47`, `Community 49`, `Community 56`, `Community 70`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `_open_connection()` connect `Community 47` to `Community 1`, `Community 3`, `Community 36`, `Community 5`, `Community 70`, `Community 7`, `Community 9`, `Community 43`, `Community 12`, `Community 13`, `Community 45`, `Community 16`, `Community 21`, `Community 28`, `Community 29`, `Community 62`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `DirectVerification` connect `Community 45` to `Community 5`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `NormalizedPeriod` (e.g. with `_read_preference()` and `_PositionInference`) actually correct?**
  _`NormalizedPeriod` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05670103092783505 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07012622720897616 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06693306693306693 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
