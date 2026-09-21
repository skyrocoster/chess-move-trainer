# Graph Report - src  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2159 nodes · 5686 edges · 104 communities (72 shown, 32 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 277 edges (avg confidence: 0.93)
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

## God Nodes (most connected - your core abstractions)
1. `NormalizedPeriod` - 42 edges
2. `_assert_compatible_schema()` - 40 edges
3. `_open_connection()` - 36 edges
4. `_open_existing_connection()` - 35 edges
5. `canonicalize_fen()` - 35 edges
6. `PreferredMoveValidationError` - 34 edges
7. `StockfishEngine` - 32 edges
8. `RangeValidationError` - 28 edges
9. `BenchmarkRunner` - 26 edges
10. `PreferredMoveRepository` - 25 edges

## Surprising Connections (you probably didn't know these)
- `PreferredMoveTimeline` --uses--> `RangeValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/ranges.py
- `PreferredMoveTimeline` --uses--> `PreferredMoveStorageError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/repository.py
- `PreferredMoveTimelinePreference` --uses--> `PreferredMoveValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/repository.py
- `PreferredMoveTimelineRepository` --uses--> `PreferredMoveRepository`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/repository.py
- `PreferredMoveTimelineRepository` --uses--> `PreferredMoveValidationError`  [INFERRED]
  chess_move_trainer/database/preferred_moves/timeline.py → chess_move_trainer/database/preferred_moves/repository.py

## Import Cycles
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (104 total, 32 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (88): activity_statistics(), _average(), _categories(), _category(), data_quality_statistics(), _DatedGame, _duration_seconds(), game_statistics() (+80 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (72): GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError, Exception, RuntimeError, ValueError, Game search error types. (+64 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (65): chess, collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., _bulk_page_parameters(), collect_direct_measurements() (+57 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (70): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), NormalizationResult, NormalizationWarning (+62 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (69): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+61 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (58): AnalysisState, _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state() (+50 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (43): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+35 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (51): DirEntry, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind(), generate_catalogue() (+43 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (42): _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError, OpeningCataloguePage (+34 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (33): BulkFailure, BulkOutcome, One isolated target failure retained only in the in-memory outcome., Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption., Stockfish process and database-lock services., MutexBusyError (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (40): _validate_lock_timeout(), Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), inspect_schema() (+32 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (28): Public preferred-move schedule values, operations, and storage services., PreferenceState, A state that can be stored for a configured period., _append_segment(), _materialize_timeline(), PreferredMoveTimeline, PreferredMoveTimelinePreference, PreferredMoveTimelineRepository (+20 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (34): AcquireConfiguration, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url() (+26 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (29): BulkRunner, _prepend(), Any, Path, Run the next eligible targets, or all eligible targets when unlimited., Analyze eligible targets one at a time and publish each result immediately., BulkTarget, BulkTargetSelector (+21 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (33): CanonicalPosition, Validated canonical chess-position identity services., _is_lock_failure(), BaseException, _canonical_fen(), _load_current_aggregate(), date, Path (+25 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (27): _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database(), MutexUnavailableError, normalize_database_path() (+19 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (33): AnalysisError, AnalysisLine, AnalysisResultInput, AnalysisStorageError, AnalysisValidationError, _FrozenJsonObject, Any, Exception (+25 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (26): Atomic publication of one complete current analysis per position., Synchronous, explicit-path SQLite connection boundary., Per-game repository and persistence models., Validation, merge, and atomic publication for raw Chess.com month files., Atomic publication of normalized opening routes into the v1 catalogue tables., Permanent canonical-position storage behind an opaque transaction boundary., Clock and SQLite lock helpers for training-answer submission., Read-only cross-game evidence and scored-position discovery. (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (33): AnalysisRequest, AnalysisRequestDisposition, AnalysisRequestError, AnalysisRequestRepository, AnalysisRequestResult, AnalysisRequestSchemaError, AnalysisRequestStorageError, AnalysisRequestValidationError (+25 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (33): _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationState, AnalysisObservationStorageError (+25 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (36): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+28 more)

### Community 21 - "Community 21"
Cohesion: 0.11
Nodes (30): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+22 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (25): Open one validated connection for an independent import run., _assert_compatible_schema(), RuntimeError, Assert exact v2 compatibility without changing the open target., Raised when an existing database is not the exact supported schema., SchemaIncompatibleError, MoveResponseDistribution, MoveResponseDistributionReader (+17 more)

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (27): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+19 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (25): DateResolution, The immutable result of resolving one date., _canonicalize_four_field_fen(), _load_schedule(), PreferredMoveError, PreferredMoveLockError, PreferredMoveRepository, PreferredMoveStorageError (+17 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (32): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), _open_existing_connection(), probe_connection(), Connection (+24 more)

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (27): _preference_from_options(), _read_preference(), PreferredMoveMutationResult, PreferredMoveRemovalResult, Package-owned preferred-move mutation values and operation., The removed interval and complete configured schedule after DELETE., The applied interval and complete configured schedule after one PUT., _intersects() (+19 more)

### Community 27 - "Community 27"
Cohesion: 0.10
Nodes (21): _find_existing_position_id(), _position_identity(), position_transaction(), PositionRepository, PositionStorageError, _PositionUnitOfWork, CanonicalPosition, Path (+13 more)

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (24): Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, Public training-requirement composition shim., _coerce_date(), effective_training_balance(), _finite_float(), _finite_result(), game_balance() (+16 more)

### Community 29 - "Community 29"
Cohesion: 0.15
Nodes (25): _bounded_message(), BaseException, _StoredAttempts, BenchmarkCompatibilityError, BenchmarkJob, StockfishProfile, Existing output state does not belong to the requested benchmark., A stable identity for one position/profile/round analysis. (+17 more)

### Community 30 - "Community 30"
Cohesion: 0.11
Nodes (17): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Raised when a compatible database cannot publish the opening catalogue., Immutable counts describing one successfully committed catalogue replacement. (+9 more)

### Community 31 - "Community 31"
Cohesion: 0.16
Nodes (27): argparse, ArgumentParser, hashlib, Popen, subprocess, sys, build_steps(), classify_result() (+19 more)

### Community 32 - "Community 32"
Cohesion: 0.14
Nodes (25): _eligible_evidence(), TrainerColor, Raised when a compatible database contains unusable training data., TrainingRequirementStorageError, validate_uci(), _active_preference(), _current_scoped_groups(), _EvidenceGroup (+17 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (22): load_positions(), Any, Path, Benchmark loading and top-level invocation., Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark(), BenchmarkError (+14 more)

### Community 34 - "Community 34"
Cohesion: 0.12
Nodes (22): _finite_number(), _normalize_range(), parse_calendar_date(), _parse_date(), date, Exception, RuntimeError, ValueError (+14 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (17): _is_expected_stockfish(), Path, Verify one explicit executable and terminate it cleanly., verify_stockfish_identity(), The process did not complete the finite UCI startup handshake., The executable did not identify itself as the configured Stockfish version., The verified identity reported by the UCI startup handshake., StockfishIdentity (+9 more)

### Community 36 - "Community 36"
Cohesion: 0.12
Nodes (21): canonicalize_fen(), Validate a complete six-field FEN and return its canonical identity., _canonical_fen(), delete_preferred_move(), _parse_mutation_date(), PreferredMoveMutationRequest, PreferredMoveRemovalRequest, put_preferred_move() (+13 more)

### Community 37 - "Community 37"
Cohesion: 0.13
Nodes (22): _game_header(), _occurrence_from_row(), _parse_started_at_utc(), PreferredMoveSetupError, PreferredMoveSetupRefused, PreferredMoveSetupResult, PreferredMoveSetupService, PreferredMoveSetupValidationError (+14 more)

### Community 38 - "Community 38"
Cohesion: 0.14
Nodes (22): _build_recognition(), lookup_fen(), OpeningInputError, OpeningRecognition, _parse_fen_input(), _parse_pgn_input(), Game, ValueError (+14 more)

### Community 39 - "Community 39"
Cohesion: 0.12
Nodes (21): _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _line_from_info(), _metrics_for(), AnalysisLine, AnalysisResultInput (+13 more)

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (22): _claim_identity(), _enqueue_in_transaction(), _format_timestamp(), _oldest_claimable(), _parse_timestamp(), AnalysisQuality, Collection, datetime (+14 more)

### Community 41 - "Community 41"
Cohesion: 0.13
Nodes (18): Immutable engine-independent analysis values and input validation., AnalysisQuality, AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, PublicationOutcome, Enum, str (+10 more)

### Community 42 - "Community 42"
Cohesion: 0.16
Nodes (23): _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached(), _load_routes_uncached() (+15 more)

### Community 43 - "Community 43"
Cohesion: 0.14
Nodes (17): AnalysisReadError, AnalysisReadRepository, AnalysisReadResult, _line_from_row(), _materialize_result(), AnalysisLine, Path, RuntimeError (+9 more)

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (19): _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game, Path, ValueError (+11 more)

### Community 45 - "Community 45"
Cohesion: 0.15
Nodes (16): _checked_connection(), Exception, Path, _translate_queue_error(), RuntimeError, QueueError, QueueStorageError, Base class for bounded analysis-queue failures. (+8 more)

### Community 46 - "Community 46"
Cohesion: 0.15
Nodes (18): Build the successful publication outcome., _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput, CanonicalPosition (+10 more)

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (19): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+11 more)

### Community 48 - "Community 48"
Cohesion: 0.29
Nodes (7): _ArtifactPaths, BenchmarkPersistenceError, An artifact could not be persisted safely after bounded retries., BenchmarkRunner, Any, Path, Run and resume one deterministic benchmark matrix.

### Community 49 - "Community 49"
Cohesion: 0.21
Nodes (16): ParsedUciInfo, Stockfish error types and result dataclasses., Stockfish returned malformed or incomplete UCI analysis data., One complete normalized ``info`` payload for a MultiPV line., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int() (+8 more)

### Community 50 - "Community 50"
Cohesion: 0.20
Nodes (14): _atomic_replace(), load_month(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Raised when a raw month cannot be validated or published safely. (+6 more)

### Community 51 - "Community 51"
Cohesion: 0.20
Nodes (12): _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path(), OSError, Atomic artifact persistence for benchmarks., _sha256_file(), BenchmarkInputError (+4 more)

### Community 52 - "Community 52"
Cohesion: 0.20
Nodes (9): _begin_immediate(), _rollback_if_active(), QueueClaim, The worker-local ticket and quality captured by one queue claim., AnalysisQuality, Release a matching running ticket back to queued work., Delete a matching running ticket after completed or skipped work., Apply matching-token failure handling without retaining a failure record. (+1 more)

### Community 53 - "Community 53"
Cohesion: 0.22
Nodes (13): _classify_board(), classify_terminal_kind(), _neutral_board(), AnalysisResultInput, AnalysisTerminalKind, Board, CanonicalPosition, ValidatedAnalysisResult (+5 more)

### Community 54 - "Community 54"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 55 - "Community 55"
Cohesion: 0.26
Nodes (7): ArtifactWriter, AtomicArtifactWriter, Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 56 - "Community 56"
Cohesion: 0.21
Nodes (11): _LiveQueueRequest, _normalize_quality(), AnalysisQuality, Queue errors, claims, and live-request views., The immutable quality captured when this ticket was issued., Read and validate one live queue row without changing it., Validated live queue data for package-internal composition., Read one validated live request without changing it. (+3 more)

### Community 57 - "Community 57"
Cohesion: 0.17
Nodes (11): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkInputError, AnalysisResultInput, RuntimeError, ValueError, Base class for direct bulk-analysis failures. (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 59 - "Community 59"
Cohesion: 0.25
Nodes (9): discover_training_requirements(), Path, TrainingRequirementPolicy, Return one deterministic page of globally scored current pairs., Discover scored requirements from one explicit existing database., Discover scored position/preferred-move pairs without writing storage., TrainingRequirementRepository, TrainingRequirementPage (+1 more)

### Community 60 - "Community 60"
Cohesion: 0.27
Nodes (6): The Stockfish child process stopped or could not accept a command., StockfishProcessError, AnalysisQuality, CanonicalPosition, StockfishProfile, Analyze one canonical position with a fixed-node profile. The only chess search…

### Community 61 - "Community 61"
Cohesion: 0.20
Nodes (8): AnalysisStorageError, Exception, _translate_storage_error(), QueueCompletionOutcome, Result of one matching-token completion attempt., Whether the worker ticket no longer owns the queue row., AnalysisResultInput, Publish and finalize one matching ticket in one immediate transaction.

### Community 62 - "Community 62"
Cohesion: 0.20
Nodes (7): profile_for(), AnalysisQuality, One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile

### Community 63 - "Community 63"
Cohesion: 0.22
Nodes (6): One globally scored canonical-position/preferred-move pair., Return the compact adapter-ready shape with six-decimal derived numbers., One deterministic page of scored training requirements., _round_public(), TrainingRequirementItem, TrainingRequirementPage

### Community 64 - "Community 64"
Cohesion: 0.25
Nodes (5): BenchmarkSpec, Any, Validated, deterministic matrix inputs for one benchmark run., Enumerate every job once in the recorded deterministic order., _profile_blocks()

### Community 65 - "Community 65"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response., Return one text response.

### Community 66 - "Community 66"
Cohesion: 0.33
Nodes (5): date, ValueError, RangeValidationError, Raised when a date, range, or normalized schedule is invalid., _require_date()

### Community 67 - "Community 67"
Cohesion: 0.53
Nodes (5): _position_sort_key(), CanonicalPosition, _validate_canonical_position(), _validate_complete_result(), _validate_legal_move()

### Community 68 - "Community 68"
Cohesion: 0.33
Nodes (6): RuntimeError, Base class for bounded Stockfish process or protocol failures., The per-analysis watchdog expired before Stockfish returned bestmove., StockfishError, StockfishWatchdogError, TimeoutError

### Community 69 - "Community 69"
Cohesion: 0.40
Nodes (4): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis

### Community 70 - "Community 70"
Cohesion: 0.50
Nodes (3): AnalysisRepository, Path, Publish normalized analysis through an opaque package-owned transaction.

### Community 71 - "Community 71"
Cohesion: 0.50
Nodes (4): _clock_date(), date, UtcCalendarDateClock, _utc_today()

## Knowledge Gaps
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_open_existing_connection()` connect `Community 25` to `Community 3`, `Community 37`, `Community 38`, `Community 40`, `Community 9`, `Community 10`, `Community 42`, `Community 45`, `Community 46`, `Community 14`, `Community 13`, `Community 17`, `Community 18`, `Community 22`, `Community 24`, `Community 27`, `Community 30`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `StockfishEngine` connect `Community 35` to `Community 68`, `Community 69`, `Community 39`, `Community 9`, `Community 13`, `Community 49`, `Community 60`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `_open_connection()` connect `Community 25` to `Community 0`, `Community 1`, `Community 2`, `Community 5`, `Community 6`, `Community 8`, `Community 10`, `Community 43`, `Community 17`, `Community 19`, `Community 22`, `Community 24`, `Community 59`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `NormalizedPeriod` (e.g. with `_preferred_period_json()` and `_render_preferred_periods()`) actually correct?**
  _`NormalizedPeriod` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0668859649122807 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.058549931600547195 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.051189400782896716 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
