# Graph Report - src  (2026-09-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2237 nodes · 5758 edges · 123 communities (71 shown, 52 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 241 edges (avg confidence: 0.92)
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

## God Nodes (most connected - your core abstractions)
1. `_assert_compatible_schema()` - 41 edges
2. `NormalizedPeriod` - 39 edges
3. `_open_existing_connection()` - 36 edges
4. `_open_connection()` - 36 edges
5. `canonicalize_fen()` - 35 edges
6. `StockfishEngine` - 32 edges
7. `PreferredMoveValidationError` - 29 edges
8. `BenchmarkRunner` - 26 edges
9. `RangeValidationError` - 25 edges
10. `PreferredMoveRepository` - 24 edges

## Surprising Connections (you probably didn't know these)
- `PreferredMoveMutationRequest` --uses--> `PreferredMoveValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/mutations.py → chess_move_trainer/database/preferred_moves/repository.py
- `PreferredMoveTimeline` --uses--> `RangeValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/ranges.py
- `PreferredMoveTimeline` --uses--> `PreferredMoveStorageError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/repository.py
- `PreferredMoveTimelineRepository` --uses--> `PreferredMoveRepository`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/repository.py
- `PreferredMoveTimelineRequest` --uses--> `RangeValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/ranges.py

## Import Cycles
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (123 total, 52 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (77): AnalysisStorageError, Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp() (+69 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (84): activity_statistics(), _average(), _categories(), _category(), data_quality_statistics(), _DatedGame, _duration_seconds(), game_statistics() (+76 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (72): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), NormalizationResult, NormalizationWarning (+64 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (75): BaseException, Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preference_from_options(), _preferred_period_json(), Shared CLI rendering and error helpers. (+67 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (58): argparse, ArgumentParser, _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database() (+50 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (58): AnalysisState, _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state() (+50 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (57): AcquisitionClock, AcquisitionResult, AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration() (+49 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (48): AcquireConfiguration, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url() (+40 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (52): DirEntry, re, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind() (+44 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (45): _is_lock_failure(), BaseException, _canonical_fen(), _eligible_evidence(), _load_current_aggregate(), date, Path, TrainerColor (+37 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (35): profile_for(), AnalysisQuality, The fixed Stockfish profiles supported by the first database worker., One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile (+27 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (33): Public preferred-move schedule values, operations, and storage services., PreferredMoveRemovalRequest, One complete parent FEN and one configured half-open interval to remove., PreferenceState, A state that can be stored for a configured period., PreferredMoveValidationError, ValueError, Raised when preferred-move input is invalid. (+25 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (36): _measurement_decision(), _median(), _plan_scans_alias(), print_direct_measurements(), Print only aggregate measurement facts and normalized plan details., DirectCapabilities, DirectMeasurementCorpus, DirectMeasurements (+28 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (32): _open_existing_connection(), Yield a configured read-write connection without creating a target., _background_result_eligibility_sql(), BulkTarget, BulkTargetSelector, InitialAnalysisTargetSelector, InitialTechnicalPosition, _load_route_moves() (+24 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (37): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+29 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (40): _validate_lock_timeout(), Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), inspect_schema() (+32 more)

### Community 16 - "Community 16"
Cohesion: 0.08
Nodes (34): AnalysisScoreKind, AnalysisLine, AnalysisQuality, AnalysisResultInput, AnalysisScoreKind, AnalysisTerminalKind, AnalysisValidationError, NotSavedReason (+26 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (32): Validated canonical chess-position identity services., ValueError, Validated read-only discovery controls., One globally scored canonical-position/preferred-move pair., Raised when a policy or discovery request is invalid., Immutable scoring inputs supplied by application configuration., TrainingRequirementItem, TrainingRequirementPolicy (+24 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (33): _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationState, AnalysisObservationStorageError (+25 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (29): _find_existing_position_id(), Find one canonical position without resolving or creating it., DateResolution, The immutable result of resolving one date., _canonicalize_four_field_fen(), _load_schedule(), PreferredMoveError, PreferredMoveLockError (+21 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (31): _load_occurrences(), _load_opening_matches(), _load_preferences(), _load_training_aggregates(), _PositionRecord, _PreferencePeriod, Database row loaders for training-requirement discovery., _TrainingAggregate (+23 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (23): _is_expected_stockfish(), Path, Verify one explicit executable and terminate it cleanly., verify_stockfish_identity(), The process did not complete the finite UCI startup handshake., The executable did not identify itself as the configured Stockfish version., The Stockfish child process stopped or could not accept a command., The verified identity reported by the UCI startup handshake. (+15 more)

### Community 23 - "Community 23"
Cohesion: 0.09
Nodes (26): canonicalize_fen(), Validate a complete six-field FEN and return its canonical identity., _canonical_fen(), delete_preferred_move(), _parse_mutation_date(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalResult (+18 more)

### Community 24 - "Community 24"
Cohesion: 0.12
Nodes (25): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+17 more)

### Community 25 - "Community 25"
Cohesion: 0.12
Nodes (27): _game_header(), _occurrence_from_row(), _parse_started_at_utc(), _position_sort_key(), PreferredMoveSetupError, PreferredMoveSetupRefused, PreferredMoveSetupResult, PreferredMoveSetupService (+19 more)

### Community 26 - "Community 26"
Cohesion: 0.10
Nodes (24): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions. (+16 more)

### Community 27 - "Community 27"
Cohesion: 0.10
Nodes (25): AnalysisObservationResult, AnalysisReadError, AnalysisReadRepository, AnalysisReadResult, _line_from_row(), _materialize_result(), AnalysisLine, Path (+17 more)

### Community 28 - "Community 28"
Cohesion: 0.10
Nodes (22): collect_direct_capabilities(), Path, Exercise real readers while retaining only bounded aggregate facts., MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path (+14 more)

### Community 29 - "Community 29"
Cohesion: 0.09
Nodes (22): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkFailure, BulkInputError, BulkOutcome, BulkRunner, _prepend() (+14 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (27): Open one validated connection for an independent import run., _assert_compatible_schema(), create_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Path, RuntimeError (+19 more)

### Community 31 - "Community 31"
Cohesion: 0.16
Nodes (28): _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached(), _load_routes_uncached() (+20 more)

### Community 32 - "Community 32"
Cohesion: 0.17
Nodes (25): _StoredAttempts, BenchmarkCompatibilityError, BenchmarkJob, StockfishProfile, Existing output state does not belong to the requested benchmark., A stable identity for one position/profile/round analysis., _checkpoint_payload(), _current_job_sets() (+17 more)

### Community 33 - "Community 33"
Cohesion: 0.12
Nodes (24): Build the successful publication outcome., AnalysisRepository, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput (+16 more)

### Community 34 - "Community 34"
Cohesion: 0.13
Nodes (17): CataloguePublication, import_opening_catalogue(), OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Atomic publication of normalized opening routes into the v1 catalogue tables. (+9 more)

### Community 35 - "Community 35"
Cohesion: 0.10
Nodes (20): opening_api_key(), OpeningKeyError, parse_opening_api_key(), ValueError, Stable public keys for persisted opening labels., Raised when an opening API key cannot be represented safely., Return the stable ``ECO:Name`` key used by API capabilities., Validate and split one stable ``ECO:Name`` key. (+12 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (24): ParsedUciInfo, RuntimeError, Stockfish error types and result dataclasses., Base class for bounded Stockfish process or protocol failures., Stockfish returned malformed or incomplete UCI analysis data., The per-analysis watchdog expired before Stockfish returned bestmove., One complete normalized ``info`` payload for a MultiPV line., Final engine-reported measurements retained by the benchmark. (+16 more)

### Community 37 - "Community 37"
Cohesion: 0.10
Nodes (23): AnalysisError, AnalysisStorageError, AnalysisValidationError, Immutable engine-independent analysis values and input validation., AnalysisError, AnalysisStorageError, Exception, RuntimeError (+15 more)

### Community 38 - "Community 38"
Cohesion: 0.13
Nodes (22): load_positions(), Any, Path, Benchmark loading and top-level invocation., Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark(), BenchmarkError (+14 more)

### Community 39 - "Community 39"
Cohesion: 0.12
Nodes (22): _load_games(), Row loaders used by the game search repository., _load_deepest_openings(), _opening_api_key(), comparable_timestamp(), normalize_timestamp_value(), optional_int(), optional_text() (+14 more)

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (21): _read_preference(), _intersects(), normalize_periods(), NormalizedPeriod, _overlay(), period_from_literals(), Preference, Enum (+13 more)

### Community 41 - "Community 41"
Cohesion: 0.12
Nodes (20): _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _line_from_info(), _metrics_for(), AnalysisLine, AnalysisResultInput (+12 more)

### Community 42 - "Community 42"
Cohesion: 0.15
Nodes (21): AnalysisTerminalKind, _classify_board(), classify_terminal_kind(), _neutral_board(), AnalysisLine, AnalysisResultInput, Board, CanonicalPosition (+13 more)

### Community 43 - "Community 43"
Cohesion: 0.15
Nodes (18): _compare(), _matches(), OpeningCatalogueEntry, OpeningCataloguePage, OpeningCatalogueQuery, OpeningCatalogueRepository, Path, One public ECO/name label and its distinct-game usage counts. (+10 more)

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (19): _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game, Path, ValueError (+11 more)

### Community 45 - "Community 45"
Cohesion: 0.19
Nodes (17): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), probe_connection(), Path, Synchronous, explicit-path SQLite connection boundary. (+9 more)

### Community 46 - "Community 46"
Cohesion: 0.30
Nodes (6): _ArtifactPaths, BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 47 - "Community 47"
Cohesion: 0.22
Nodes (16): chess, Replay one standard-start PGN and recognize reached opening endpoints., replay_pgn(), _collect_opening_capabilities(), Real-reader capability proof while retaining only aggregate facts., DirectPreflightError, Raised when fixed direct proof inputs are unavailable or unsafe., _board_for_moves() (+8 more)

### Community 48 - "Community 48"
Cohesion: 0.17
Nodes (13): GameSearchPage, GameSearchQuery, One finite, deterministic page of public game summaries., All approved collection filters and pagination controls., Read-only, explicit-path search over normalized schema-v1 games. Thin…, GameSearchRepository, Path, Search one explicit database path without exposing a connection handle. (+5 more)

### Community 49 - "Community 49"
Cohesion: 0.29
Nodes (14): GameSearchValidationError, ValueError, Raised when a game-search query is invalid., Game search query models., _normalize_fen(), _normalize_timestamp(), _parse_opening_key(), datetime (+6 more)

### Community 50 - "Community 50"
Cohesion: 0.21
Nodes (13): AnalysisRequest, AnalysisRequestRepository, AnalysisRequestResult, AnalysisQuality, Path, _quality_rank(), Compose one desired-result request through an explicit database path., Request one current analysis result atomically. (+5 more)

### Community 51 - "Community 51"
Cohesion: 0.19
Nodes (15): _coverage_state(), DeepestOpening, GameCoverage, The selected deepest opening classification for a game., Analysis and preferred-move coverage over distinct game positions., _aggregate_games(), _GameAggregates, _matches_aggregates() (+7 more)

### Community 52 - "Community 52"
Cohesion: 0.16
Nodes (13): _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path(), BaseException, OSError, Atomic artifact persistence for benchmarks. (+5 more)

### Community 53 - "Community 53"
Cohesion: 0.27
Nodes (13): _load_labels(), _load_usage(), OpeningCatalogueError, OpeningCatalogueSchemaError, OpeningCatalogueStorageError, _OpeningLabel, Read-only, explicit-path browsing of the schema-v1 opening catalogue., Base class for bounded opening-catalogue failures. (+5 more)

### Community 54 - "Community 54"
Cohesion: 0.21
Nodes (11): _compare_games(), _compare_nullable(), _matches(), Game search matching, sorting, and coverage., _GameData, GameSummary, A public game summary that deliberately contains no SQLite identifiers., _in_datetime_bounds() (+3 more)

### Community 55 - "Community 55"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 56 - "Community 56"
Cohesion: 0.26
Nodes (7): ArtifactWriter, AtomicArtifactWriter, Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 57 - "Community 57"
Cohesion: 0.21
Nodes (10): _build_recognition(), OpeningRecognition, One immutable label reached at one encountered ply., Return the explicit route or transposition match kind., An immutable ordered recognition timeline and its selected current label., Return the ordered recognition timeline., RecognizedOpening, _record_evidence() (+2 more)

### Community 58 - "Community 58"
Cohesion: 0.21
Nodes (8): position_transaction(), PositionRepository, Path, Open one opaque package-owned transaction for grouped position work., Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction., Canonicalize and persist one complete FEN in an owned transaction.

### Community 59 - "Community 59"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 60 - "Community 60"
Cohesion: 0.24
Nodes (10): CanonicalPosition, GameSearchError, GameSearchSchemaError, GameSearchStorageError, Exception, RuntimeError, Game search error types., Raised when a compatible game database cannot be read safely. (+2 more)

### Community 61 - "Community 61"
Cohesion: 0.24
Nodes (9): _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_inputs(), _MeasurementInputs, Any, Path, Measure the named SQL reads without retaining row data. The statements below… (+1 more)

### Community 62 - "Community 62"
Cohesion: 0.33
Nodes (5): _normalize_eco_bound(), OpeningCatalogueValidationError, Return one exact public-key entry, or ``None`` when it is absent., Raised when an opening-catalogue query is invalid., ValueError

### Community 63 - "Community 63"
Cohesion: 0.33
Nodes (7): Exception, RuntimeError, Base class for bounded training-requirement failures., Raised when persisted training state is newer than the requested date., TrainingRequirementError, TrainingRequirementSchemaError, TrainingRequirementStaleError

### Community 64 - "Community 64"
Cohesion: 0.29
Nodes (4): Return the compact adapter-ready shape with six-decimal derived numbers., One deterministic page of scored training requirements., _round_public(), TrainingRequirementPage

### Community 65 - "Community 65"
Cohesion: 0.29
Nodes (4): BenchmarkSpec, Any, Validated, deterministic matrix inputs for one benchmark run., Enumerate every job once in the recorded deterministic order.

### Community 66 - "Community 66"
Cohesion: 0.40
Nodes (3): _FrozenJsonObject, Any, A JSON-compatible dict whose ordinary mutation operations are disabled.

### Community 67 - "Community 67"
Cohesion: 0.40
Nodes (5): OpeningInputError, _parse_pgn_input(), Game, ValueError, Raised when a FEN or PGN query is not an accepted standard-chess input.

### Community 68 - "Community 68"
Cohesion: 0.40
Nodes (3): CanonicalPosition, Return the immutable four-field identity of the final position., Alias for the immutable final-position identity.

### Community 69 - "Community 69"
Cohesion: 0.40
Nodes (4): chunk_sorted_ids(), Small, dependency-neutral helpers for bounded database queries., Return sorted unique integer identifiers in non-empty bounded chunks., collections_abc

### Community 70 - "Community 70"
Cohesion: 0.40
Nodes (4): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis

## Knowledge Gaps
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_open_connection()` connect `Community 45` to `Community 1`, `Community 5`, `Community 12`, `Community 15`, `Community 48`, `Community 17`, `Community 47`, `Community 19`, `Community 51`, `Community 53`, `Community 21`, `Community 20`, `Community 27`, `Community 28`, `Community 61`, `Community 30`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `_assert_compatible_schema()` connect `Community 30` to `Community 0`, `Community 1`, `Community 2`, `Community 5`, `Community 9`, `Community 10`, `Community 12`, `Community 13`, `Community 17`, `Community 19`, `Community 20`, `Community 21`, `Community 25`, `Community 27`, `Community 28`, `Community 31`, `Community 33`, `Community 34`, `Community 48`, `Community 50`, `Community 53`, `Community 58`, `Community 61`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `_open_existing_connection()` connect `Community 13` to `Community 0`, `Community 33`, `Community 2`, `Community 34`, `Community 9`, `Community 10`, `Community 45`, `Community 15`, `Community 50`, `Community 20`, `Community 25`, `Community 58`, `Community 27`, `Community 30`, `Community 31`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `NormalizedPeriod` (e.g. with `_read_preference()` and `_PositionInference`) actually correct?**
  _`NormalizedPeriod` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05670103092783505 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07118967988533206 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.052941176470588235 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
