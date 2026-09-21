# Graph Report - src  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2245 nodes · 5940 edges · 107 communities (73 shown, 34 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.93)
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

## God Nodes (most connected - your core abstractions)
1. `NormalizedPeriod` - 42 edges
2. `_assert_compatible_schema()` - 41 edges
3. `_open_connection()` - 38 edges
4. `canonicalize_fen()` - 36 edges
5. `_open_existing_connection()` - 35 edges
6. `PreferredMoveValidationError` - 34 edges
7. `StockfishEngine` - 32 edges
8. `RangeValidationError` - 28 edges
9. `BenchmarkRunner` - 26 edges
10. `PreferredMoveRepository` - 25 edges

## Surprising Connections (you probably didn't know these)
- `QueueService` --uses--> `QueueError`  [INFERRED]
  chess_move_trainer/database/stockfish/queue_service.py → chess_move_trainer/database/stockfish/queue_models.py
- `QueueService` --uses--> `QueueValidationError`  [INFERRED]
  chess_move_trainer/database/stockfish/queue_service.py → chess_move_trainer/database/stockfish/queue_models.py
- `_prepend()` --uses--> `BulkTarget`  [INFERRED]
  chess_move_trainer/database/stockfish/bulk.py → chess_move_trainer/database/stockfish/targets.py
- `BulkRunner` --uses--> `BulkTargetSelector`  [INFERRED]
  chess_move_trainer/database/stockfish/bulk.py → chess_move_trainer/database/stockfish/targets.py
- `BulkRunner` --uses--> `InitialAnalysisTargetSelector`  [INFERRED]
  chess_move_trainer/database/stockfish/bulk.py → chess_move_trainer/database/stockfish/targets.py

## Import Cycles
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (107 total, 34 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (77): GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError, Exception, RuntimeError, ValueError, Game search error types. (+69 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (84): activity_statistics(), _average(), _categories(), _category(), data_quality_statistics(), _DatedGame, _duration_seconds(), game_statistics() (+76 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (74): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), NormalizationResult, NormalizationWarning (+66 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (78): argparse, ArgumentParser, DirEntry, Popen, re, subprocess, sys, build_steps() (+70 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (64): BlunderError, BlunderSchemaError, BlunderStorageError, BlunderValidationError, Blunder discovery error types., Raised when a blunder query or policy value is invalid., Raised when a compatible blunder database cannot be read safely., Base class for bounded blunder-discovery failures. (+56 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (69): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+61 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (58): AnalysisState, _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state() (+50 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (44): _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_decision(), _measurement_inputs(), _MeasurementInputs, _median(), _plan_scans_alias() (+36 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (39): CanonicalPosition, _stored_position(), _clock_date(), _is_lock_failure(), BaseException, date, UtcCalendarDateClock, Clock and SQLite lock helpers for training-answer submission. (+31 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (41): _validate_lock_timeout(), Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), inspect_schema() (+33 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (32): _begin_immediate(), _claim_identity(), _rollback_if_active(), _LiveQueueRequest, QueueClaim, QueueCompletionOutcome, QueueQualityError, QueueStorageError (+24 more)

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (31): _open_existing_connection(), Yield a configured read-write connection without creating a target., position_transaction(), Open one opaque package-owned transaction for grouped position work., BulkTarget, BulkTargetSelector, InitialAnalysisTargetSelector, InitialTechnicalPosition (+23 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (36): _eligible_evidence(), date, TrainerColor, Raised when a compatible database contains unusable training data., TrainingRequirementStorageError, validate_uci(), _active_preference(), _current_scoped_groups() (+28 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (36): Immutable engine-independent analysis values and input validation., _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationSchemaError (+28 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (37): _preference_from_options(), _read_preference(), Public preferred-move schedule values, operations, and storage services., delete_preferred_move(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalRequest, PreferredMoveRemovalResult (+29 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (34): AcquireConfiguration, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url() (+26 more)

### Community 16 - "Community 16"
Cohesion: 0.10
Nodes (35): _load_labels(), _load_usage(), OpeningCatalogueEntry, OpeningCatalogueError, OpeningCataloguePage, OpeningCatalogueRepository, OpeningCatalogueSchemaError, OpeningCatalogueStorageError (+27 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (33): AnalysisRequest, AnalysisRequestDisposition, AnalysisRequestError, AnalysisRequestRepository, AnalysisRequestResult, AnalysisRequestSchemaError, AnalysisRequestStorageError, AnalysisRequestValidationError (+25 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (30): load_positions(), Any, Path, Benchmark loading and top-level invocation., Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark(), BenchmarkError (+22 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (36): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+28 more)

### Community 21 - "Community 21"
Cohesion: 0.11
Nodes (28): DateResolution, The immutable result of resolving one date., _canonicalize_four_field_fen(), _load_schedule(), PreferredMoveError, PreferredMoveLockError, PreferredMoveRepository, PreferredMoveStorageError (+20 more)

### Community 22 - "Community 22"
Cohesion: 0.13
Nodes (35): _build_recognition(), _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached() (+27 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (29): AnalysisError, AnalysisLine, AnalysisResultInput, AnalysisStorageError, AnalysisValidationError, _FrozenJsonObject, Any, Exception (+21 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (30): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+22 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (28): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+20 more)

### Community 26 - "Community 26"
Cohesion: 0.09
Nodes (23): PreferenceState, A state that can be stored for a configured period., _append_segment(), _materialize_timeline(), PreferredMoveTimeline, PreferredMoveTimelinePreference, PreferredMoveTimelineRepository, PreferredMoveTimelineRequest (+15 more)

### Community 27 - "Community 27"
Cohesion: 0.14
Nodes (31): _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_file_path(), BaseException, OSError, Atomic artifact persistence for benchmarks., _sha256_file() (+23 more)

### Community 28 - "Community 28"
Cohesion: 0.10
Nodes (26): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions. (+18 more)

### Community 29 - "Community 29"
Cohesion: 0.15
Nodes (25): Validated canonical chess-position identity services., Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, Public training-requirement composition shim., _coerce_date(), effective_training_balance(), _finite_float(), _finite_result() (+17 more)

### Community 30 - "Community 30"
Cohesion: 0.10
Nodes (24): _assert_compatible_schema(), RuntimeError, Assert exact v2 compatibility without changing the open target., Raised when an existing database is not the exact supported schema., SchemaIncompatibleError, MoveResponseDistribution, MoveResponseDistributionReader, PositionContext (+16 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (26): _game_header(), _occurrence_from_row(), _parse_started_at_utc(), _position_sort_key(), PreferredMoveSetupError, PreferredMoveSetupRefused, PreferredMoveSetupResult, PreferredMoveSetupValidationError (+18 more)

### Community 32 - "Community 32"
Cohesion: 0.14
Nodes (27): _checked_connection(), _enqueue_in_transaction(), _format_timestamp(), _oldest_claimable(), _parse_timestamp(), AnalysisQuality, Collection, datetime (+19 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (17): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Raised when a compatible database cannot publish the opening catalogue., Immutable counts describing one successfully committed catalogue replacement. (+9 more)

### Community 34 - "Community 34"
Cohesion: 0.12
Nodes (25): AnalysisRepository, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput, AnalysisStorageError (+17 more)

### Community 35 - "Community 35"
Cohesion: 0.10
Nodes (18): canonicalize_fen(), Validate a complete six-field FEN and return its canonical identity., _canonical_fen(), _parse_mutation_date(), CanonicalPosition, date, parse_date_literal(), date (+10 more)

### Community 36 - "Community 36"
Cohesion: 0.12
Nodes (17): _is_expected_stockfish(), Path, Verify one explicit executable and terminate it cleanly., verify_stockfish_identity(), The process did not complete the finite UCI startup handshake., The executable did not identify itself as the configured Stockfish version., The verified identity reported by the UCI startup handshake., StockfishIdentity (+9 more)

### Community 37 - "Community 37"
Cohesion: 0.12
Nodes (21): _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _line_from_info(), _metrics_for(), AnalysisLine, AnalysisResultInput (+13 more)

### Community 38 - "Community 38"
Cohesion: 0.18
Nodes (21): chess, collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., DirectCapabilities, DirectPreflightError (+13 more)

### Community 39 - "Community 39"
Cohesion: 0.14
Nodes (21): _parse_pgn_input(), Game, _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game (+13 more)

### Community 40 - "Community 40"
Cohesion: 0.12
Nodes (16): AnalysisQuality, AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, PublicationOutcome, Enum, str, A result whose terminal kind and candidate lines passed position validation. (+8 more)

### Community 41 - "Community 41"
Cohesion: 0.14
Nodes (17): _load_current_aggregate(), _finite_number(), _normalize_range(), parse_calendar_date(), _parse_date(), date, ValueError, Validated models for read-only position training requirements. (+9 more)

### Community 42 - "Community 42"
Cohesion: 0.14
Nodes (17): AnalysisReadError, AnalysisReadRepository, AnalysisReadResult, _line_from_row(), _materialize_result(), AnalysisLine, Path, RuntimeError (+9 more)

### Community 43 - "Community 43"
Cohesion: 0.18
Nodes (20): create_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Path, Transactional creation, compatibility, and explicit schema upgrades., Upgrade one existing exact v1 database to v2, or leave exact v2 unchanged., Build each immutable bundled-schema snapshot once per process. Compatibility… (+12 more)

### Community 44 - "Community 44"
Cohesion: 0.13
Nodes (18): _analysis_result(), BulkError, BulkFailure, BulkInputError, BulkRunner, _prepend(), AnalysisResultInput, Any (+10 more)

### Community 45 - "Community 45"
Cohesion: 0.18
Nodes (19): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+11 more)

### Community 46 - "Community 46"
Cohesion: 0.15
Nodes (15): Return the current result value for callers using a result/read shape., _analysis_result(), _finite_non_negative(), _finite_positive(), AnalysisResultInput, CanonicalPosition, datetime, Path (+7 more)

### Community 47 - "Community 47"
Cohesion: 0.30
Nodes (6): _ArtifactPaths, BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 48 - "Community 48"
Cohesion: 0.21
Nodes (16): ParsedUciInfo, Stockfish error types and result dataclasses., Stockfish returned malformed or incomplete UCI analysis data., One complete normalized ``info`` payload for a MultiPV line., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int() (+8 more)

### Community 49 - "Community 49"
Cohesion: 0.16
Nodes (15): Stockfish process and database-lock services., _close_handle(), DatabaseMutexError, MutexBusyError, MutexUnavailableError, Any, RuntimeError, Database Stockfish work mutex. Windows uses a kernel-owned named mutex. Other… (+7 more)

### Community 50 - "Community 50"
Cohesion: 0.16
Nodes (8): DatabaseMutex, OSError, Release ownership and close the kernel handle whenever possible., Best-effort close, releasing ownership first when necessary., Acquire and release one database-specific Stockfish mutex. Windows keeps the…, Whether this instance currently owns the mutex., Try to acquire ownership, returning false for a finite busy wait., _windows_error()

### Community 51 - "Community 51"
Cohesion: 0.16
Nodes (17): _classify_board(), classify_terminal_kind(), _neutral_board(), AnalysisLine, AnalysisResultInput, AnalysisTerminalKind, Board, CanonicalPosition (+9 more)

### Community 52 - "Community 52"
Cohesion: 0.16
Nodes (16): _atomic_replace(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files., Raised when a raw month cannot be validated or published safely. (+8 more)

### Community 53 - "Community 53"
Cohesion: 0.23
Nodes (8): ArtifactWriter, AtomicArtifactWriter, _normalized_directory(), Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 54 - "Community 54"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 55 - "Community 55"
Cohesion: 0.28
Nodes (7): Whether the successful acquisition recovered an abandoned owner., Any, Drain current queued/reclaimable work and then exit., One isolated request failure retained only in the launch outcome., Drain queued requests with one sequential engine process at a time., WorkerFailure, WorkerRunner

### Community 56 - "Community 56"
Cohesion: 0.30
Nodes (12): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), probe_connection(), Path, Ordinary data describing the settings verified on an opened database. (+4 more)

### Community 57 - "Community 57"
Cohesion: 0.26
Nodes (9): Synchronous, explicit-path SQLite connection boundary., Atomic publication of normalized opening routes into the v1 catalogue tables., Permanent canonical-position storage behind an opaque transaction boundary., collections_abc, contextlib, pathlib, sqlalchemy, sqlalchemy_pool (+1 more)

### Community 58 - "Community 58"
Cohesion: 0.21
Nodes (10): _compare(), _matches(), _normalize_eco_bound(), OpeningCatalogueQuery, OpeningCatalogueValidationError, Return the finite page matching every supplied catalogue filter., Raised when an opening-catalogue query is invalid., The filters, ordering, and pagination controls for one catalogue read. (+2 more)

### Community 59 - "Community 59"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 60 - "Community 60"
Cohesion: 0.18
Nodes (8): profile_for(), AnalysisQuality, The fixed Stockfish profiles supported by the first database worker., One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile

### Community 61 - "Community 61"
Cohesion: 0.18
Nodes (7): BulkOutcome, Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption., Observable result of one finite worker launch., Whether this finite launch completed without failures or interruption., WorkerOutcome

### Community 62 - "Community 62"
Cohesion: 0.27
Nodes (6): The Stockfish child process stopped or could not accept a command., StockfishProcessError, AnalysisQuality, CanonicalPosition, StockfishProfile, Analyze one canonical position with a fixed-node profile. The only chess search…

### Community 63 - "Community 63"
Cohesion: 0.24
Nodes (6): PositionRepository, Path, Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction., Canonicalize and persist one complete FEN in an owned transaction.

### Community 64 - "Community 64"
Cohesion: 0.22
Nodes (6): One globally scored canonical-position/preferred-move pair., Return the compact adapter-ready shape with six-decimal derived numbers., One deterministic page of scored training requirements., _round_public(), TrainingRequirementItem, TrainingRequirementPage

### Community 65 - "Community 65"
Cohesion: 0.28
Nodes (8): _finite_wait(), _lock_file_for_database(), mutex_name_for_database(), normalize_database_path(), Path, Return the sidecar lock file used on non-Windows platforms., Return the absolute, normalized path used as mutex identity input., Derive a bounded Windows named-mutex name from one database path.

### Community 66 - "Community 66"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response., Return one text response.

### Community 67 - "Community 67"
Cohesion: 0.33
Nodes (7): Exception, RuntimeError, Base class for bounded training-requirement failures., Raised when persisted training state is newer than the requested date., TrainingRequirementError, TrainingRequirementSchemaError, TrainingRequirementStaleError

### Community 68 - "Community 68"
Cohesion: 0.29
Nodes (4): BenchmarkJob, StockfishProfile, Enumerate every job once in the recorded deterministic order., A stable identity for one position/profile/round analysis.

### Community 69 - "Community 69"
Cohesion: 0.33
Nodes (4): One immutable label reached at one encountered ply., Return the explicit route or transposition match kind., Return the ordered recognition timeline., RecognizedOpening

### Community 70 - "Community 70"
Cohesion: 0.33
Nodes (6): RuntimeError, Base class for bounded Stockfish process or protocol failures., The per-analysis watchdog expired before Stockfish returned bestmove., StockfishError, StockfishWatchdogError, TimeoutError

### Community 71 - "Community 71"
Cohesion: 0.40
Nodes (4): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis

### Community 72 - "Community 72"
Cohesion: 0.67
Nodes (3): OpeningInputError, ValueError, Raised when a FEN or PGN query is not an accepted standard-chess input.

## Knowledge Gaps
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_open_connection()` connect `Community 56` to `Community 0`, `Community 1`, `Community 4`, `Community 6`, `Community 38`, `Community 7`, `Community 9`, `Community 42`, `Community 43`, `Community 12`, `Community 13`, `Community 16`, `Community 18`, `Community 21`, `Community 57`, `Community 30`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `_assert_compatible_schema()` connect `Community 30` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 11`, `Community 12`, `Community 13`, `Community 16`, `Community 17`, `Community 18`, `Community 21`, `Community 22`, `Community 31`, `Community 32`, `Community 33`, `Community 34`, `Community 38`, `Community 42`, `Community 43`, `Community 46`, `Community 56`, `Community 63`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `DatabaseMutexError` connect `Community 49` to `Community 50`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `NormalizedPeriod` (e.g. with `_preferred_period_json()` and `_render_preferred_periods()`) actually correct?**
  _`NormalizedPeriod` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05255613951266125 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07118967988533206 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.05041797283176593 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
