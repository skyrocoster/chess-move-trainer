# Graph Report - src  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2066 nodes · 5425 edges · 112 communities (71 shown, 41 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 289 edges (avg confidence: 0.93)
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

## God Nodes (most connected - your core abstractions)
1. `NormalizedPeriod` - 42 edges
2. `_assert_compatible_schema()` - 39 edges
3. `_open_connection()` - 37 edges
4. `_open_existing_connection()` - 36 edges
5. `canonicalize_fen()` - 35 edges
6. `PreferredMoveValidationError` - 34 edges
7. `StockfishEngine` - 32 edges
8. `RangeValidationError` - 28 edges
9. `BenchmarkRunner` - 26 edges
10. `PreferredMoveRepository` - 25 edges

## Surprising Connections (you probably didn't know these)
- `_setup_database()` --calls--> `GameRepository`  [INFERRED]
  chess_move_trainer/database/lifecycle.py → chess_move_trainer/database/games/persistence_repository.py
- `_update_games()` --calls--> `GameRepository`  [INFERRED]
  chess_move_trainer/database/lifecycle.py → chess_move_trainer/database/games/persistence_repository.py
- `PreferredMoveInferenceResult` --uses--> `NormalizedPeriod`  [INFERRED]
  chess_move_trainer/database/preferred_moves/inference.py → chess_move_trainer/database/preferred_moves/ranges.py
- `setup_preferred_moves_command()` --uses--> `PreferredMoveSetupError`  [INFERRED]
  chess_move_trainer/database/cli_preferred.py → chess_move_trainer/database/preferred_moves/setup.py
- `_render_preferred_setup()` --uses--> `PreferredMoveSetupResult`  [INFERRED]
  chess_move_trainer/database/cli_helpers.py → chess_move_trainer/database/preferred_moves/setup.py

## Import Cycles
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (112 total, 41 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (78): _ArtifactPaths, ArtifactWriter, AtomicArtifactWriter, _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path() (+70 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (74): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), NormalizationResult, NormalizationWarning (+66 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (73): GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError, Exception, RuntimeError, ValueError, Game search error types. (+65 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (58): AnalysisState, _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state() (+50 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (46): _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_decision(), _measurement_inputs(), _MeasurementInputs, _median(), _plan_scans_alias() (+38 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (49): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), BaseException, Exception, Shared CLI rendering and error helpers., Run one fixed-path service and render only its ordinary result data. (+41 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (46): _preference_from_options(), _read_preference(), Public preferred-move schedule values, operations, and storage services., delete_preferred_move(), PreferredMoveMutationResult, PreferredMoveRemovalRequest, PreferredMoveRemovalResult, put_preferred_move() (+38 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (51): DirEntry, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind(), generate_catalogue() (+43 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (31): PreferenceState, A state that can be stored for a configured period., PreferredMoveValidationError, ValueError, Raised when preferred-move input is invalid., _append_segment(), _canonical_fen(), _materialize_timeline() (+23 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (39): _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError, OpeningCataloguePage (+31 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (37): infer_preferred_moves(), _position_sort_key(), PreferredMoveInferenceResult, PreferredMoveObservation, CanonicalPosition, Return a read-only position-to-period view for downstream consumers., Infer normalized preferred-move schedules from eligible observations. Every…, One eligible trainer move leaving one canonical position on one date. (+29 more)

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (36): Immutable engine-independent analysis values and input validation., _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationSchemaError (+28 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (40): _validate_lock_timeout(), Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), inspect_schema() (+32 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (35): AnalysisError, AnalysisLine, AnalysisResultInput, AnalysisStorageError, AnalysisValidationError, _FrozenJsonObject, Any, Exception (+27 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (34): AcquireConfiguration, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url() (+26 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (33): AnalysisRequest, AnalysisRequestDisposition, AnalysisRequestError, AnalysisRequestRepository, AnalysisRequestResult, AnalysisRequestSchemaError, AnalysisRequestStorageError, AnalysisRequestValidationError (+25 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (36): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+28 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (30): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+22 more)

### Community 19 - "Community 19"
Cohesion: 0.09
Nodes (23): _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), MutexUnavailableError, Any, OSError (+15 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (24): _open_existing_connection(), Yield a configured read-write connection without creating a target., position_transaction(), Open one opaque package-owned transaction for grouped position work., BulkTarget, BulkTargetSelector, InitialAnalysisTargetSelector, _load_route_moves() (+16 more)

### Community 21 - "Community 21"
Cohesion: 0.11
Nodes (23): MutexBusyError, A finite wait expired because another process owns the mutex., Whether the successful acquisition recovered an abandoned owner., _analysis_result(), _finite_non_negative(), _finite_positive(), AnalysisResultInput, Any (+15 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (27): _clock_date(), _is_lock_failure(), BaseException, date, UtcCalendarDateClock, _utc_today(), _canonical_fen(), _eligible_evidence() (+19 more)

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (18): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Atomic publication of normalized opening routes into the v1 catalogue tables., Raised when a compatible database cannot publish the opening catalogue. (+10 more)

### Community 24 - "Community 24"
Cohesion: 0.16
Nodes (25): Validated read-only discovery controls., Raised when a compatible database contains unusable training data., TrainingRequirementQuery, TrainingRequirementStorageError, validate_uci(), _current_scoped_groups(), _EvidenceGroup, _group_matches_opening() (+17 more)

### Community 25 - "Community 25"
Cohesion: 0.14
Nodes (26): Open one validated connection for an independent import run., _assert_compatible_schema(), create_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Path, RuntimeError (+18 more)

### Community 26 - "Community 26"
Cohesion: 0.17
Nodes (27): _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached(), _load_routes_uncached() (+19 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (19): _begin_immediate(), _claim_identity(), _rollback_if_active(), QueueClaim, QueueStorageError, Raised when the queue cannot safely use its compatible database., The worker-local ticket and quality captured by one queue claim., AnalysisResultInput (+11 more)

### Community 28 - "Community 28"
Cohesion: 0.17
Nodes (26): argparse, ArgumentParser, Popen, subprocess, sys, build_steps(), classify_result(), _command_text() (+18 more)

### Community 29 - "Community 29"
Cohesion: 0.13
Nodes (23): Build the successful publication outcome., AnalysisRepository, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput (+15 more)

### Community 30 - "Community 30"
Cohesion: 0.11
Nodes (19): MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError, TrainerColor, Direct, read-only statistics over normalized game occurrences. (+11 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (17): _is_expected_stockfish(), Path, Verify one explicit executable and terminate it cleanly., verify_stockfish_identity(), The process did not complete the finite UCI startup handshake., The executable did not identify itself as the configured Stockfish version., The verified identity reported by the UCI startup handshake., StockfishIdentity (+9 more)

### Community 32 - "Community 32"
Cohesion: 0.11
Nodes (22): chess, _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _line_from_info(), _metrics_for(), AnalysisLine (+14 more)

### Community 33 - "Community 33"
Cohesion: 0.19
Nodes (23): Validated canonical chess-position identity services., Public training-requirement composition shim., _coerce_date(), effective_training_balance(), _finite_float(), _finite_result(), game_balance(), minimum_additional_correct_answers() (+15 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (20): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkFailure, BulkInputError, BulkRunner, _prepend(), AnalysisResultInput (+12 more)

### Community 35 - "Community 35"
Cohesion: 0.12
Nodes (19): _canonicalize_four_field_fen(), _load_schedule(), PreferredMoveError, PreferredMoveLockError, PreferredMoveStorageError, CanonicalPosition, Exception, RuntimeError (+11 more)

### Community 36 - "Community 36"
Cohesion: 0.16
Nodes (22): _preferred_period_json(), Render only the five ordinary setup summary counts., _render_preferred_periods(), _render_preferred_resolution(), _render_preferred_setup(), list_preferred_moves(), command, Path (+14 more)

### Community 37 - "Community 37"
Cohesion: 0.14
Nodes (21): _parse_pgn_input(), Game, _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game (+13 more)

### Community 38 - "Community 38"
Cohesion: 0.19
Nodes (20): collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., DirectCapabilities, DirectPreflightError, ValueError (+12 more)

### Community 39 - "Community 39"
Cohesion: 0.14
Nodes (17): AnalysisReadError, AnalysisReadRepository, AnalysisReadResult, _line_from_row(), _materialize_result(), AnalysisLine, Path, RuntimeError (+9 more)

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (17): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), canonicalize_fen(), PositionValidationError, Board, ValueError (+9 more)

### Community 41 - "Community 41"
Cohesion: 0.14
Nodes (15): Clock and SQLite lock helpers for training-answer submission., _finite_number(), _normalize_range(), _parse_date(), date, ValueError, Validated models for read-only position training requirements., Raised when a policy or discovery request is invalid. (+7 more)

### Community 42 - "Community 42"
Cohesion: 0.18
Nodes (19): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+11 more)

### Community 43 - "Community 43"
Cohesion: 0.17
Nodes (14): _find_existing_position_id(), _position_identity(), PositionStorageError, _PositionUnitOfWork, CanonicalPosition, PositionIdentity, RuntimeError, Permanent canonical-position storage behind an opaque transaction boundary. (+6 more)

### Community 44 - "Community 44"
Cohesion: 0.19
Nodes (17): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), _latest_signal_for_move(), _PositionInference (+9 more)

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (17): _enqueue_in_transaction(), _format_timestamp(), _oldest_claimable(), _parse_timestamp(), AnalysisQuality, Collection, datetime, _quality_rank() (+9 more)

### Community 46 - "Community 46"
Cohesion: 0.14
Nodes (13): profile_for(), AnalysisQuality, One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile, Stockfish process and database-lock services. (+5 more)

### Community 47 - "Community 47"
Cohesion: 0.16
Nodes (16): _atomic_replace(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files., Raised when a raw month cannot be validated or published safely. (+8 more)

### Community 48 - "Community 48"
Cohesion: 0.15
Nodes (15): _build_recognition(), OpeningInputError, OpeningRecognition, ValueError, Raised when a FEN or PGN query is not an accepted standard-chess input., One immutable label reached at one encountered ply., Return the explicit route or transposition match kind., An immutable ordered recognition timeline and its selected current label. (+7 more)

### Community 49 - "Community 49"
Cohesion: 0.23
Nodes (15): ParsedUciInfo, Stockfish returned malformed or incomplete UCI analysis data., One complete normalized ``info`` payload for a MultiPV line., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int(), parse_uci_info() (+7 more)

### Community 50 - "Community 50"
Cohesion: 0.17
Nodes (14): _LiveQueueRequest, QueueCompletionOutcome, QueueQualityError, Queue errors, claims, and live-request views., Result of one matching-token completion attempt., Whether the worker ticket no longer owns the queue row., Read and validate one live queue row without changing it., Validated live queue data for package-internal composition. (+6 more)

### Community 51 - "Community 51"
Cohesion: 0.23
Nodes (15): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), probe_connection(), Connection, Path (+7 more)

### Community 52 - "Community 52"
Cohesion: 0.17
Nodes (13): AnalysisQuality, AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, PublicationOutcome, Enum, str, Saved or expected not-saved result for the publication service. (+5 more)

### Community 53 - "Community 53"
Cohesion: 0.19
Nodes (11): Path, UtcCalendarDateClock, The server judgment and the newly scored training item., Return the resulting scored item using an explicit adapter-friendly name., Judge and persist one answer in an existing compatible database., Submit one validated answer against one explicit existing database., submit_training_answer(), TrainingAnswerRepository (+3 more)

### Community 54 - "Community 54"
Cohesion: 0.22
Nodes (13): _classify_board(), classify_terminal_kind(), _neutral_board(), AnalysisResultInput, AnalysisTerminalKind, Board, CanonicalPosition, ValidatedAnalysisResult (+5 more)

### Community 55 - "Community 55"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 56 - "Community 56"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 57 - "Community 57"
Cohesion: 0.18
Nodes (7): BulkOutcome, Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption., Observable result of one finite worker launch., Whether this finite launch completed without failures or interruption., WorkerOutcome

### Community 58 - "Community 58"
Cohesion: 0.24
Nodes (9): RuntimeError, Stockfish error types and result dataclasses., Base class for bounded Stockfish process or protocol failures., The Stockfish child process stopped or could not accept a command., The per-analysis watchdog expired before Stockfish returned bestmove., StockfishError, StockfishProcessError, StockfishWatchdogError (+1 more)

### Community 59 - "Community 59"
Cohesion: 0.24
Nodes (6): PositionRepository, Path, Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction., Canonicalize and persist one complete FEN in an owned transaction.

### Community 60 - "Community 60"
Cohesion: 0.22
Nodes (10): Raised when the requested current training pair does not exist., TrainingAnswerNotFoundError, Exception, RuntimeError, Base class for bounded training-requirement failures., Raised when persisted training state is newer than the requested date., TrainingRequirementError, TrainingRequirementSchemaError (+2 more)

### Community 61 - "Community 61"
Cohesion: 0.20
Nodes (5): Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, discover_training_requirements(), Path, Discover scored requirements from one explicit existing database.

### Community 62 - "Community 62"
Cohesion: 0.22
Nodes (7): InitialTechnicalPosition, Board, CanonicalPosition, Return the canonical position consumed by the engine., One stable technical representative in the initial-analysis preset., Return the canonical identity represented by the fixed FEN., _record_route_position()

### Community 63 - "Community 63"
Cohesion: 0.29
Nodes (6): _canonical_fen(), _parse_mutation_date(), PreferredMoveMutationRequest, CanonicalPosition, date, One complete parent FEN and one configured half-open interval.

### Community 64 - "Community 64"
Cohesion: 0.36
Nodes (4): AnalysisQuality, CanonicalPosition, StockfishProfile, Analyze one canonical position with a fixed-node profile. The only chess search…

### Community 65 - "Community 65"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response., Return one text response.

### Community 66 - "Community 66"
Cohesion: 0.33
Nodes (6): OpeningKeyError, parse_opening_api_key(), ValueError, Stable public keys for persisted opening labels., Raised when an opening API key cannot be represented safely., Validate and split one stable ``ECO:Name`` key.

### Community 67 - "Community 67"
Cohesion: 0.29
Nodes (4): Return the compact adapter-ready shape with six-decimal derived numbers., One deterministic page of scored training requirements., _round_public(), TrainingRequirementPage

### Community 68 - "Community 68"
Cohesion: 0.33
Nodes (7): _checked_connection(), Exception, Path, _translate_queue_error(), RuntimeError, QueueError, Base class for bounded analysis-queue failures.

### Community 69 - "Community 69"
Cohesion: 0.33
Nodes (5): AnalysisStorageError, Exception, _translate_storage_error(), AnalysisQuality, Insert or promote one live request without disturbing an active claim.

### Community 70 - "Community 70"
Cohesion: 0.40
Nodes (4): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis

## Knowledge Gaps
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_assert_compatible_schema()` connect `Community 25` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 9`, `Community 10`, `Community 11`, `Community 15`, `Community 16`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 24`, `Community 26`, `Community 29`, `Community 30`, `Community 35`, `Community 38`, `Community 39`, `Community 59`, `Community 68`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `_open_connection()` connect `Community 51` to `Community 2`, `Community 3`, `Community 35`, `Community 4`, `Community 6`, `Community 39`, `Community 38`, `Community 9`, `Community 11`, `Community 12`, `Community 16`, `Community 24`, `Community 25`, `Community 30`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `canonicalize_fen()` connect `Community 40` to `Community 0`, `Community 2`, `Community 3`, `Community 35`, `Community 6`, `Community 8`, `Community 10`, `Community 11`, `Community 43`, `Community 15`, `Community 22`, `Community 23`, `Community 26`, `Community 62`, `Community 63`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `NormalizedPeriod` (e.g. with `_preferred_period_json()` and `_render_preferred_periods()`) actually correct?**
  _`NormalizedPeriod` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05126945126945127 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.051590483827853514 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.05747126436781609 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
