# Graph Report - src  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2158 nodes · 5743 edges · 114 communities (73 shown, 41 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 300 edges (avg confidence: 0.93)
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

## God Nodes (most connected - your core abstractions)
1. `NormalizedPeriod` - 42 edges
2. `_assert_compatible_schema()` - 40 edges
3. `_open_connection()` - 38 edges
4. `_open_existing_connection()` - 36 edges
5. `canonicalize_fen()` - 35 edges
6. `PreferredMoveValidationError` - 34 edges
7. `StockfishEngine` - 32 edges
8. `RangeValidationError` - 28 edges
9. `BenchmarkRunner` - 26 edges
10. `PreferredMoveRepository` - 25 edges

## Surprising Connections (you probably didn't know these)
- `_setup_database()` --uses--> `AcquisitionClock`  [INFERRED]
  chess_move_trainer/database/lifecycle.py → chess_move_trainer/database/games/acquisition.py
- `_update_games()` --uses--> `AcquisitionClock`  [INFERRED]
  chess_move_trainer/database/lifecycle.py → chess_move_trainer/database/games/acquisition.py
- `_require_game_acquisition()` --uses--> `AcquisitionResult`  [INFERRED]
  chess_move_trainer/database/lifecycle.py → chess_move_trainer/database/games/acquisition.py
- `_setup_database()` --uses--> `JsonTransport`  [INFERRED]
  chess_move_trainer/database/lifecycle.py → chess_move_trainer/database/games/acquisition.py
- `_update_games()` --uses--> `JsonTransport`  [INFERRED]
  chess_move_trainer/database/lifecycle.py → chess_move_trainer/database/games/acquisition.py

## Import Cycles
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (114 total, 41 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (87): activity_statistics(), _average(), _categories(), _category(), data_quality_statistics(), _DatedGame, _duration_seconds(), game_statistics() (+79 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (73): GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError, Exception, RuntimeError, ValueError, Game search error types. (+65 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (67): chess, _open_connection(), Yield one configured SQLAlchemy Core connection for package internals., collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts. (+59 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (65): AnalysisStorageError, Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp() (+57 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (68): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+60 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (58): AnalysisState, _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state() (+50 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (40): canonicalize_fen(), Validate a complete six-field FEN and return its canonical identity., _canonical_fen(), _parse_mutation_date(), CanonicalPosition, date, parse_date_literal(), date (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (48): _preference_from_options(), _read_preference(), Public preferred-move schedule values, operations, and storage services., delete_preferred_move(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalRequest, PreferredMoveRemovalResult (+40 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (51): DirEntry, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind(), generate_catalogue() (+43 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (38): _analysis_state(), AnalysisObservationResult, AnalysisObservationState, _canonical_fen(), _materialize_observation(), _observation_result(), CanonicalPosition, Enum (+30 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (34): AcquireConfiguration, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url() (+26 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (35): _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError, OpeningCataloguePage (+27 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (35): AnalysisLine, AnalysisResultInput, AnalysisValidationError, ValueError, Immutable normalized analysis values and bounded outcome categories., A complete engine-independent result payload without position or terminal…, Raised when normalized analysis input is outside the catalogue domain., One normalized candidate line before terminal or chess-legality checks. (+27 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (31): _normalized_directory(), _normalized_file_path(), Atomic artifact persistence for benchmarks., load_positions(), Any, Path, Benchmark loading and top-level invocation., Load and structurally validate explicit JSON benchmark positions. (+23 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (26): _open_existing_connection(), Yield a configured read-write connection without creating a target., BulkTarget, BulkTargetSelector, InitialAnalysisTargetSelector, _load_route_moves(), Board, CanonicalPosition (+18 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (36): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+28 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (31): PreferredMoveError, PreferredMoveSchemaError, RuntimeError, Base error for bounded preferred-move failures., _game_header(), _occurrence_from_row(), _parse_started_at_utc(), _position_sort_key() (+23 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (30): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+22 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (23): _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), MutexUnavailableError, Any, OSError (+15 more)

### Community 20 - "Community 20"
Cohesion: 0.16
Nodes (29): _eligible_evidence(), _load_current_aggregate(), date, TrainerColor, parse_calendar_date(), Parse one strict calendar-date value for scoring and storage checks., Raised when a compatible database contains unusable training data., TrainingRequirementStorageError (+21 more)

### Community 21 - "Community 21"
Cohesion: 0.11
Nodes (27): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+19 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (23): MutexBusyError, A finite wait expired because another process owns the mutex., Whether the successful acquisition recovered an abandoned owner., _analysis_result(), _finite_non_negative(), _finite_positive(), AnalysisResultInput, Any (+15 more)

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (18): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Atomic publication of normalized opening routes into the v1 catalogue tables., Raised when a compatible database cannot publish the opening catalogue. (+10 more)

### Community 24 - "Community 24"
Cohesion: 0.13
Nodes (28): Open one validated connection for an independent import run., _assert_compatible_schema(), create_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Path, RuntimeError (+20 more)

### Community 25 - "Community 25"
Cohesion: 0.15
Nodes (27): Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), _pragma_rows(), Connection (+19 more)

### Community 26 - "Community 26"
Cohesion: 0.15
Nodes (27): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), NormalizationWarning, normalize_game() (+19 more)

### Community 27 - "Community 27"
Cohesion: 0.17
Nodes (25): Validated canonical chess-position identity services., Raised when SQLite cannot acquire the bounded writer lock., TrainingAnswerLockError, Public training-requirement composition shim., _coerce_date(), effective_training_balance(), _finite_float(), _finite_result() (+17 more)

### Community 28 - "Community 28"
Cohesion: 0.17
Nodes (24): _StoredAttempts, BenchmarkCompatibilityError, BenchmarkJob, StockfishProfile, Existing output state does not belong to the requested benchmark., A stable identity for one position/profile/round analysis., _checkpoint_payload(), _current_job_sets() (+16 more)

### Community 29 - "Community 29"
Cohesion: 0.17
Nodes (26): argparse, ArgumentParser, Popen, subprocess, sys, build_steps(), classify_result(), _command_text() (+18 more)

### Community 30 - "Community 30"
Cohesion: 0.11
Nodes (19): MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError, TrainerColor, Direct, read-only statistics over normalized game occurrences. (+11 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (17): _is_expected_stockfish(), Path, Verify one explicit executable and terminate it cleanly., verify_stockfish_identity(), The process did not complete the finite UCI startup handshake., The executable did not identify itself as the configured Stockfish version., The verified identity reported by the UCI startup handshake., StockfishIdentity (+9 more)

### Community 32 - "Community 32"
Cohesion: 0.17
Nodes (22): NormalizationResult, import_normalized_games(), import_raw_games(), import_raw_month(), import_raw_months(), load_normalized_months(), normalize_raw_games(), Path (+14 more)

### Community 33 - "Community 33"
Cohesion: 0.14
Nodes (22): AnalysisRepository, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput, CanonicalPosition (+14 more)

### Community 34 - "Community 34"
Cohesion: 0.18
Nodes (24): _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached(), _load_routes_uncached() (+16 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (18): _find_existing_position_id(), Find one canonical position without resolving or creating it., _canonicalize_four_field_fen(), PreferredMoveLockError, PreferredMoveRepository, CanonicalPosition, Exception, Path (+10 more)

### Community 36 - "Community 36"
Cohesion: 0.12
Nodes (21): _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _line_from_info(), _metrics_for(), AnalysisLine, AnalysisResultInput (+13 more)

### Community 37 - "Community 37"
Cohesion: 0.11
Nodes (18): AnalysisQuality, AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, PublicationOutcome, Enum, str, A result whose terminal kind and candidate lines passed position validation. (+10 more)

### Community 38 - "Community 38"
Cohesion: 0.11
Nodes (20): AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationStorageError, AnalysisObservationValidationError, AnalysisError, AnalysisStorageError (+12 more)

### Community 39 - "Community 39"
Cohesion: 0.16
Nodes (18): NormalizedGame, _game_metadata(), GamePersistenceError, GameRepository, _metadata_parameters(), PersistedGame, Any, PositionIdentity (+10 more)

### Community 40 - "Community 40"
Cohesion: 0.10
Nodes (16): BulkOutcome, Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption., Stockfish process and database-lock services., mutex_name_for_database(), normalize_database_path(), Path (+8 more)

### Community 41 - "Community 41"
Cohesion: 0.11
Nodes (20): Immutable engine-independent analysis values and input validation., AnalysisError, AnalysisStorageError, Exception, RuntimeError, Base class for bounded analysis-package failures., Reserved category for an unexpected analysis storage failure., AnalysisObservationSchemaError (+12 more)

### Community 42 - "Community 42"
Cohesion: 0.12
Nodes (18): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkFailure, BulkInputError, BulkRunner, _prepend(), AnalysisResultInput (+10 more)

### Community 43 - "Community 43"
Cohesion: 0.14
Nodes (18): AnalysisRequest, AnalysisRequestRepository, AnalysisRequestResult, AnalysisRequestValidationError, _canonicalize_request_fen(), AnalysisQuality, AnalysisValidationError, CanonicalPosition (+10 more)

### Community 44 - "Community 44"
Cohesion: 0.14
Nodes (17): Synchronous, explicit-path SQLite connection boundary., Permanent canonical-position storage behind an opaque transaction boundary., _clock_date(), _is_lock_failure(), BaseException, date, UtcCalendarDateClock, Clock and SQLite lock helpers for training-answer submission. (+9 more)

### Community 45 - "Community 45"
Cohesion: 0.13
Nodes (20): _build_recognition(), lookup_fen(), OpeningInputError, OpeningRecognition, _parse_fen_input(), _parse_pgn_input(), Game, ValueError (+12 more)

### Community 46 - "Community 46"
Cohesion: 0.12
Nodes (15): _canonical_fen(), CanonicalPosition, Path, UtcCalendarDateClock, Judge and persist one answer in an existing compatible database., Judge one answer and atomically update its aggregate credit., Submit one validated answer against one explicit existing database., Raised when an answer request is invalid. (+7 more)

### Community 47 - "Community 47"
Cohesion: 0.15
Nodes (19): _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game, Path, ValueError (+11 more)

### Community 48 - "Community 48"
Cohesion: 0.18
Nodes (19): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+11 more)

### Community 49 - "Community 49"
Cohesion: 0.30
Nodes (6): _ArtifactPaths, BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 50 - "Community 50"
Cohesion: 0.21
Nodes (16): ParsedUciInfo, Stockfish error types and result dataclasses., Stockfish returned malformed or incomplete UCI analysis data., One complete normalized ``info`` payload for a MultiPV line., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int() (+8 more)

### Community 51 - "Community 51"
Cohesion: 0.16
Nodes (16): _atomic_replace(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files., Raised when a raw month cannot be validated or published safely. (+8 more)

### Community 52 - "Community 52"
Cohesion: 0.23
Nodes (13): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions. (+5 more)

### Community 53 - "Community 53"
Cohesion: 0.21
Nodes (9): ArtifactWriter, AtomicArtifactWriter, _is_within(), Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local. (+1 more)

### Community 54 - "Community 54"
Cohesion: 0.23
Nodes (13): _validate_lock_timeout(), inspect_schema(), Path, Read generic SQLite metadata without creating or changing the database., _atomic_write(), publish_schema(), Path, ValueError (+5 more)

### Community 55 - "Community 55"
Cohesion: 0.21
Nodes (11): Validated read-only discovery controls., One deterministic page of scored training requirements., TrainingRequirementPage, TrainingRequirementQuery, TrainingRequirementSchemaError, discover_training_requirements(), Path, Return one deterministic page of globally scored current pairs. (+3 more)

### Community 56 - "Community 56"
Cohesion: 0.23
Nodes (8): _position_identity(), _PositionUnitOfWork, CanonicalPosition, PositionIdentity, Opaque position operations bound to one package-owned transaction., Return IDs that may be promoted after the owning transaction commits., Resolve one canonical position on a caller-owned transaction. This is a…, _resolve_canonical_position()

### Community 57 - "Community 57"
Cohesion: 0.21
Nodes (9): _finite_number(), _normalize_range(), _parse_date(), date, ValueError, Raised when a policy or discovery request is invalid., A normalized inclusive/exclusive requirement range., TrainingRequirementRange (+1 more)

### Community 58 - "Community 58"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 59 - "Community 59"
Cohesion: 0.21
Nodes (8): position_transaction(), PositionRepository, Path, Open one opaque package-owned transaction for grouped position work., Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction., Canonicalize and persist one complete FEN in an owned transaction.

### Community 60 - "Community 60"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 61 - "Community 61"
Cohesion: 0.18
Nodes (8): profile_for(), AnalysisQuality, The fixed Stockfish profiles supported by the first database worker., One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile

### Community 62 - "Community 62"
Cohesion: 0.29
Nodes (9): Opening recognition services and internal source/persistence modules., opening_api_key(), OpeningKeyError, parse_opening_api_key(), ValueError, Stable public keys for persisted opening labels., Raised when an opening API key cannot be represented safely., Return the stable ``ECO:Name`` key used by API capabilities. (+1 more)

### Community 63 - "Community 63"
Cohesion: 0.20
Nodes (7): The server judgment and the newly scored training item., Return the resulting scored item using an explicit adapter-friendly name., TrainingAnswerResult, One globally scored canonical-position/preferred-move pair., Return the compact adapter-ready shape with six-decimal derived numbers., _round_public(), TrainingRequirementItem

### Community 64 - "Community 64"
Cohesion: 0.18
Nodes (11): Raised when the requested current training pair does not exist., Raised when the requested answer date predates persisted credit., TrainingAnswerNotFoundError, TrainingAnswerStaleError, Exception, RuntimeError, Base class for bounded training-requirement failures., Raised when persisted training state is newer than the requested date. (+3 more)

### Community 65 - "Community 65"
Cohesion: 0.27
Nodes (6): The Stockfish child process stopped or could not accept a command., StockfishProcessError, AnalysisQuality, CanonicalPosition, StockfishProfile, Analyze one canonical position with a fixed-node profile. The only chess search…

### Community 66 - "Community 66"
Cohesion: 0.29
Nodes (10): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), probe_connection(), Connection, Path, Ordinary data describing the settings verified on an opened database. (+2 more)

### Community 67 - "Community 67"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response., Return one text response.

### Community 68 - "Community 68"
Cohesion: 0.29
Nodes (4): BenchmarkSpec, Any, Validated, deterministic matrix inputs for one benchmark run., Enumerate every job once in the recorded deterministic order.

### Community 69 - "Community 69"
Cohesion: 0.33
Nodes (4): _BulkImportAbort, Exception, Path, Carry one ordinary import failure out of the bulk transaction.

### Community 70 - "Community 70"
Cohesion: 0.33
Nodes (6): RuntimeError, Base class for bounded Stockfish process or protocol failures., The per-analysis watchdog expired before Stockfish returned bestmove., StockfishError, StockfishWatchdogError, TimeoutError

### Community 71 - "Community 71"
Cohesion: 0.40
Nodes (3): _FrozenJsonObject, Any, A JSON-compatible dict whose ordinary mutation operations are disabled.

### Community 72 - "Community 72"
Cohesion: 0.40
Nodes (4): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis

## Knowledge Gaps
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_open_connection()` connect `Community 2` to `Community 0`, `Community 1`, `Community 66`, `Community 35`, `Community 5`, `Community 38`, `Community 7`, `Community 9`, `Community 11`, `Community 44`, `Community 13`, `Community 20`, `Community 54`, `Community 55`, `Community 24`, `Community 25`, `Community 30`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `BenchmarkJob` connect `Community 28` to `Community 49`, `Community 68`, `Community 14`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `StockfishProfile` connect `Community 61` to `Community 40`, `Community 49`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `NormalizedPeriod` (e.g. with `_preferred_period_json()` and `_render_preferred_periods()`) actually correct?**
  _`NormalizedPeriod` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06763717805151176 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05747126436781609 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.051061388410786 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
