# Graph Report - src  (2026-09-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2292 nodes · 6041 edges · 118 communities (71 shown, 47 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 297 edges (avg confidence: 0.93)
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

## God Nodes (most connected - your core abstractions)
1. `NormalizedPeriod` - 42 edges
2. `_assert_compatible_schema()` - 42 edges
3. `_open_connection()` - 38 edges
4. `_open_existing_connection()` - 36 edges
5. `canonicalize_fen()` - 36 edges
6. `PreferredMoveValidationError` - 34 edges
7. `StockfishEngine` - 32 edges
8. `RangeValidationError` - 28 edges
9. `BenchmarkRunner` - 26 edges
10. `PreferredMoveRepository` - 25 edges

## Surprising Connections (you probably didn't know these)
- `list_preferred_moves()` --uses--> `PreferredMoveStorageError`  [INFERRED]
  chess_move_trainer/database/cli_preferred.py → chess_move_trainer/database/preferred_moves/repository.py
- `resolve_preferred_move()` --uses--> `PreferredMoveStorageError`  [INFERRED]
  chess_move_trainer/database/cli_preferred.py → chess_move_trainer/database/preferred_moves/repository.py
- `set_preferred_move()` --uses--> `PreferredMoveStorageError`  [INFERRED]
  chess_move_trainer/database/cli_preferred.py → chess_move_trainer/database/preferred_moves/repository.py
- `unset_preferred_move()` --uses--> `PreferredMoveStorageError`  [INFERRED]
  chess_move_trainer/database/cli_preferred.py → chess_move_trainer/database/preferred_moves/repository.py
- `list_preferred_moves()` --uses--> `PreferredMoveValidationError`  [INFERRED]
  chess_move_trainer/database/cli_preferred.py → chess_move_trainer/database/preferred_moves/repository.py

## Import Cycles
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (118 total, 47 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (79): AnalysisStorageError, Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp() (+71 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (79): CanonicalPosition, GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError, Exception, RuntimeError, ValueError (+71 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (85): activity_statistics(), _average(), _categories(), _category(), data_quality_statistics(), _DatedGame, _duration_seconds(), game_statistics() (+77 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (65): BlunderError, BlunderSchemaError, BlunderStorageError, BlunderValidationError, Blunder discovery error types., Raised when a blunder query or policy value is invalid., Raised when a compatible blunder database cannot be read safely., Base class for bounded blunder-discovery failures. (+57 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (69): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+61 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (58): argparse, ArgumentParser, _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database() (+50 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (53): _board_for_position(), _classify_terminal(), _fen_for_position(), _is_expected_stockfish(), _line_from_info(), _metrics_for(), AnalysisLine, AnalysisResultInput (+45 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (58): AnalysisState, _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state() (+50 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (45): position_transaction(), Open one opaque package-owned transaction for grouped position work., BulkFailure, BulkRunner, _prepend(), Any, Path, Serial direct Tool analysis over the live on-demand target selection. (+37 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (52): DirEntry, re, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind() (+44 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (36): Public preferred-move schedule values, operations, and storage services., parse_date_literal(), Parse exactly one literal ``YYYY-MM-DD`` calendar date., PreferredMoveLockError, PreferredMoveStorageError, PreferredMoveValidationError, ValueError, Raised when preferred-move input is invalid. (+28 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (44): _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError, OpeningCataloguePage (+36 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (39): _preference_from_options(), _read_preference(), PreferredMoveMutationResult, put_preferred_move(), Package-owned preferred-move mutation values and operation., Atomically apply one ordinary preferred-move mutation value., The applied interval and complete configured schedule after one PUT., _intersects() (+31 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (43): _build_recognition(), _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached() (+35 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (41): AnalysisScoreKind, AnalysisTerminalKind, AnalysisError, AnalysisLine, AnalysisResultInput, AnalysisStorageError, AnalysisValidationError, Exception (+33 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (38): collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus() (+30 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (37): Immutable engine-independent analysis values and input validation., _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationSchemaError (+29 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (40): _validate_lock_timeout(), Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), inspect_schema() (+32 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (33): AnalysisError, AnalysisObservationResult, AnalysisStorageError, AnalysisValidationError, AnalysisRequest, AnalysisRequestDisposition, AnalysisRequestError, AnalysisRequestRepository (+25 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (32): AcquireConfiguration, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, _archive_url(), ArchiveMonth (+24 more)

### Community 21 - "Community 21"
Cohesion: 0.08
Nodes (32): _canonical_fen(), _eligible_evidence(), _load_current_aggregate(), date, Path, TrainerColor, TrainingRequirementItem, TrainingRequirementPolicy (+24 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (27): _analysis_result(), _finite_non_negative(), _finite_positive(), AnalysisResultInput, Any, CanonicalPosition, datetime, Path (+19 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (35): AcquisitionResult, _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError (+27 more)

### Community 24 - "Community 24"
Cohesion: 0.09
Nodes (30): _sha256_file(), load_positions(), Any, Path, Benchmark loading and top-level invocation., Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark() (+22 more)

### Community 25 - "Community 25"
Cohesion: 0.14
Nodes (28): Validated canonical chess-position identity services., ValueError, Raised when a policy or discovery request is invalid., Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, TrainingRequirementValidationError, Public training-requirement composition shim., _coerce_date() (+20 more)

### Community 26 - "Community 26"
Cohesion: 0.11
Nodes (30): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+22 more)

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (30): PreferredMoveError, Exception, Base error for bounded preferred-move failures., _game_header(), _occurrence_from_row(), _parse_started_at_utc(), _position_sort_key(), PreferredMoveSetupError (+22 more)

### Community 28 - "Community 28"
Cohesion: 0.11
Nodes (27): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+19 more)

### Community 29 - "Community 29"
Cohesion: 0.11
Nodes (20): CataloguePublication, import_opening_catalogue(), OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Atomic publication of normalized opening routes into the v1 catalogue tables. (+12 more)

### Community 30 - "Community 30"
Cohesion: 0.17
Nodes (24): _load_occurrences(), _load_opening_matches(), _load_preferences(), _load_training_aggregates(), _PositionRecord, _PreferencePeriod, Database row loaders for training-requirement discovery., _TrainingAggregate (+16 more)

### Community 31 - "Community 31"
Cohesion: 0.18
Nodes (24): _StoredAttempts, BenchmarkCompatibilityError, BenchmarkJob, StockfishProfile, Existing output state does not belong to the requested benchmark., A stable identity for one position/profile/round analysis., _checkpoint_payload(), _current_job_sets() (+16 more)

### Community 32 - "Community 32"
Cohesion: 0.17
Nodes (23): NormalizationResult, NormalizationWarning, normalize_game(), Return a fully validated game, or one ordinary warning for a skipped input., import_normalized_games(), import_raw_games(), import_raw_month(), import_raw_months() (+15 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (19): MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError, TrainerColor, Direct, read-only statistics over normalized game occurrences. (+11 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (19): _finite_number(), _normalize_range(), parse_calendar_date(), _parse_date(), date, Validated models for read-only position training requirements., Validated read-only discovery controls., One globally scored canonical-position/preferred-move pair. (+11 more)

### Community 35 - "Community 35"
Cohesion: 0.14
Nodes (22): AnalysisRepository, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput, CanonicalPosition (+14 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (24): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), _normalize_game(), _optional_integer() (+16 more)

### Community 37 - "Community 37"
Cohesion: 0.11
Nodes (18): AnalysisQuality, AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, PublicationOutcome, Enum, str, A result whose terminal kind and candidate lines passed position validation. (+10 more)

### Community 38 - "Community 38"
Cohesion: 0.14
Nodes (21): _parse_pgn_input(), Game, _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game (+13 more)

### Community 39 - "Community 39"
Cohesion: 0.17
Nodes (22): create_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Path, RuntimeError, Transactional creation, compatibility, and explicit schema upgrades., Upgrade one existing exact v1 database to v2, or leave exact v2 unchanged. (+14 more)

### Community 40 - "Community 40"
Cohesion: 0.14
Nodes (15): ArtifactWriter, AtomicArtifactWriter, _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path(), Any (+7 more)

### Community 41 - "Community 41"
Cohesion: 0.14
Nodes (17): AnalysisReadError, AnalysisReadRepository, AnalysisReadResult, _line_from_row(), _materialize_result(), AnalysisLine, Path, RuntimeError (+9 more)

### Community 42 - "Community 42"
Cohesion: 0.14
Nodes (18): _measurement_decision(), _plan_scans_alias(), QueryPlanMeasurement, Aggregate query-plan and elapsed-time evidence without row data., Return the number of timed executions represented by this value., _measure_query(), Any, Shared query-plan measurement helper. (+10 more)

### Community 43 - "Community 43"
Cohesion: 0.18
Nodes (19): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+11 more)

### Community 44 - "Community 44"
Cohesion: 0.23
Nodes (17): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), _open_existing_connection(), probe_connection(), Path (+9 more)

### Community 45 - "Community 45"
Cohesion: 0.18
Nodes (14): NormalizedGame, _game_metadata(), GameRepository, _metadata_parameters(), PersistedGame, Any, PositionIdentity, Open one validated connection for an independent import run. (+6 more)

### Community 46 - "Community 46"
Cohesion: 0.18
Nodes (17): _atomic_replace(), load_month(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files. (+9 more)

### Community 47 - "Community 47"
Cohesion: 0.20
Nodes (15): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), canonicalize_fen(), PositionValidationError, Board, ValueError (+7 more)

### Community 48 - "Community 48"
Cohesion: 0.28
Nodes (6): _ArtifactPaths, BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 49 - "Community 49"
Cohesion: 0.15
Nodes (13): DateResolution, PreferenceState, date, Enum, ValueError, RangeValidationError, Pure date-range behavior for the current preferred-move schedule., Raised when a date, range, or normalized schedule is invalid. (+5 more)

### Community 50 - "Community 50"
Cohesion: 0.20
Nodes (9): Per-game repository and persistence models., _position_identity(), _PositionUnitOfWork, PositionIdentity, Permanent canonical-position storage behind an opaque transaction boundary., Opaque position operations bound to one package-owned transaction., Return IDs that may be promoted after the owning transaction commits., contextlib (+1 more)

### Community 51 - "Community 51"
Cohesion: 0.14
Nodes (13): _canonical_fen(), delete_preferred_move(), _parse_mutation_date(), PreferredMoveMutationRequest, PreferredMoveRemovalRequest, PreferredMoveRemovalResult, CanonicalPosition, date (+5 more)

### Community 52 - "Community 52"
Cohesion: 0.16
Nodes (12): _clock_date(), _is_lock_failure(), BaseException, date, UtcCalendarDateClock, Clock and SQLite lock helpers for training-answer submission., _utc_today(), Judge one answer and atomically update its aggregate credit. (+4 more)

### Community 53 - "Community 53"
Cohesion: 0.15
Nodes (10): profile_for(), AnalysisQuality, Any, quality_settings_match(), Whether stored settings satisfy a profile's result quality. Threads and Hash…, One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis. (+2 more)

### Community 54 - "Community 54"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 55 - "Community 55"
Cohesion: 0.24
Nodes (11): chess, normalize_score(), normalize_wdl(), _parse_int(), parse_uci_info(), AnalysisScoreKind, UCI info parsing and score normalization., Convert Stockfish's side-to-move score to signed White POV. (+3 more)

### Community 56 - "Community 56"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 57 - "Community 57"
Cohesion: 0.25
Nodes (9): discover_training_requirements(), Path, Discover scored requirements from one explicit existing database., Discover scored position/preferred-move pairs without writing storage., Return one deterministic page of globally scored current pairs., TrainingRequirementRepository, TrainingRequirementPage, TrainingRequirementPolicy (+1 more)

### Community 58 - "Community 58"
Cohesion: 0.20
Nodes (9): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkInputError, AnalysisResultInput, RuntimeError, ValueError, Base class for direct bulk-analysis failures. (+1 more)

### Community 59 - "Community 59"
Cohesion: 0.24
Nodes (6): PositionRepository, Path, Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction., Canonicalize and persist one complete FEN in an owned transaction.

### Community 60 - "Community 60"
Cohesion: 0.20
Nodes (6): DirectProof, Read-only aggregate facts suitable for bounded direct evidence., Whether the retained canonical preference table is empty., Whether the fixed database exposes exactly the catalogue's ten tables., Whether every stored game has a complete ordered occurrence set., Whether every stored route has contiguous one-based move plies.

### Community 61 - "Community 61"
Cohesion: 0.32
Nodes (8): _find_existing_position_id(), PositionStorageError, CanonicalPosition, RuntimeError, Raised when a compatible position database cannot be used safely., Resolve one canonical position on a caller-owned transaction. This is a…, Find one canonical position without resolving or creating it., _resolve_canonical_position()

### Community 62 - "Community 62"
Cohesion: 0.25
Nodes (5): DirectVerification, Aggregate integrity facts for the fixed database proof target., Whether the opening catalogue has its required data., Whether imported games and occurrences are present., Whether the fixed database passes the aggregate readiness checks.

### Community 63 - "Community 63"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response., Return one text response.

### Community 64 - "Community 64"
Cohesion: 0.33
Nodes (7): Exception, RuntimeError, Base class for bounded training-requirement failures., Raised when persisted training state is newer than the requested date., TrainingRequirementError, TrainingRequirementSchemaError, TrainingRequirementStaleError

### Community 65 - "Community 65"
Cohesion: 0.29
Nodes (4): BenchmarkSpec, Any, Validated, deterministic matrix inputs for one benchmark run., Enumerate every job once in the recorded deterministic order.

### Community 66 - "Community 66"
Cohesion: 0.29
Nodes (4): BulkOutcome, Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption.

### Community 67 - "Community 67"
Cohesion: 0.33
Nodes (4): _BulkImportAbort, Exception, Path, Carry one ordinary import failure out of the bulk transaction.

### Community 68 - "Community 68"
Cohesion: 0.40
Nodes (3): _FrozenJsonObject, Any, A JSON-compatible dict whose ordinary mutation operations are disabled.

### Community 69 - "Community 69"
Cohesion: 0.40
Nodes (4): GamePersistenceError, RuntimeError, Raised when one normalized game cannot be persisted atomically., Verify that the configured target is an existing compatible v1 database.

### Community 70 - "Community 70"
Cohesion: 0.50
Nodes (3): _finite_timeout(), Any, Path

## Knowledge Gaps
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_assert_compatible_schema()` connect `Community 42` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 7`, `Community 8`, `Community 11`, `Community 12`, `Community 13`, `Community 15`, `Community 16`, `Community 18`, `Community 19`, `Community 22`, `Community 27`, `Community 29`, `Community 33`, `Community 35`, `Community 39`, `Community 41`, `Community 44`, `Community 45`, `Community 52`, `Community 53`, `Community 57`, `Community 59`, `Community 69`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `_open_existing_connection()` connect `Community 44` to `Community 0`, `Community 35`, `Community 69`, `Community 39`, `Community 27`, `Community 8`, `Community 12`, `Community 45`, `Community 13`, `Community 17`, `Community 18`, `Community 50`, `Community 52`, `Community 53`, `Community 22`, `Community 59`, `Community 29`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `_open_connection()` connect `Community 44` to `Community 1`, `Community 2`, `Community 3`, `Community 33`, `Community 7`, `Community 39`, `Community 41`, `Community 42`, `Community 11`, `Community 12`, `Community 15`, `Community 16`, `Community 17`, `Community 19`, `Community 57`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `NormalizedPeriod` (e.g. with `_preferred_period_json()` and `_render_preferred_periods()`) actually correct?**
  _`NormalizedPeriod` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.055040197897340756 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05101807366735301 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.07035998129967275 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
