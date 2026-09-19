# Graph Report - src  (2026-09-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1887 nodes · 5836 edges · 57 communities (50 shown, 7 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 335 edges (avg confidence: 0.94)
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

## God Nodes (most connected - your core abstractions)
1. `_assert_compatible_schema()` - 69 edges
2. `SchemaIncompatibleError` - 66 edges
3. `canonicalize_fen()` - 60 edges
4. `CanonicalPosition` - 55 edges
5. `AnalysisQuality` - 53 edges
6. `NormalizedPeriod` - 49 edges
7. `_open_connection()` - 46 edges
8. `_open_existing_connection()` - 39 edges
9. `PreferredMoveValidationError` - 38 edges
10. `RangeValidationError` - 34 edges

## Surprising Connections (you probably didn't know these)
- `BenchmarkJob` --uses--> `StockfishProfile`  [INFERRED]
  chess_move_trainer/database/stockfish/benchmark_models.py → chess_move_trainer/database/stockfish/configuration.py
- `BenchmarkRunner` --uses--> `StockfishProfile`  [INFERRED]
  chess_move_trainer/database/stockfish/benchmark_runner.py → chess_move_trainer/database/stockfish/configuration.py
- `BulkRunner` --uses--> `DatabaseMutex`  [INFERRED]
  chess_move_trainer/database/stockfish/bulk.py → chess_move_trainer/database/stockfish/mutex.py
- `WorkerRunner` --uses--> `DatabaseMutex`  [INFERRED]
  chess_move_trainer/database/stockfish/worker.py → chess_move_trainer/database/stockfish/mutex.py
- `WorkerRunner` --uses--> `MutexBusyError`  [INFERRED]
  chess_move_trainer/database/stockfish/worker.py → chess_move_trainer/database/stockfish/mutex.py

## Import Cycles
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (57 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (75): _ArtifactPaths, ArtifactWriter, AtomicArtifactWriter, _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path() (+67 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (65): profile_for(), One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile, _board_for_position(), _classify_terminal() (+57 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (74): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), NormalizationResult, NormalizationWarning (+66 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (81): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preference_from_options(), _preferred_period_json(), BaseException, Exception (+73 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (53): Public preferred-move schedule values, operations, and storage services., _canonical_fen(), delete_preferred_move(), _parse_mutation_date(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalRequest, PreferredMoveRemovalResult (+45 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (56): Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp(), _oldest_claimable() (+48 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (56): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), probe_connection(), Connection, Path, Synchronous, explicit-path SQLite connection boundary. (+48 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (39): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkFailure, BulkOutcome, _prepend(), Any, Path (+31 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (48): Immutable engine-independent analysis values and input validation., AnalysisError, AnalysisStorageError, Exception, RuntimeError, Base class for bounded analysis-package failures., Reserved category for an unexpected analysis storage failure., AnalysisObservationError (+40 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (45): _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError, OpeningCataloguePage (+37 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (33): _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database(), MutexBusyError, MutexUnavailableError (+25 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (48): Any, DirEntry, Path, RuntimeError, _assert_safe_path(), _atomic_write_batch(), build_graphify_command(), _canonical_graph() (+40 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (33): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Atomic publication of normalized opening routes into the v1 catalogue tables., Raised when a compatible database cannot publish the opening catalogue. (+25 more)

### Community 13 - "Community 13"
Cohesion: 0.10
Nodes (40): GameSearchError, GameSearchSchemaError, GameSearchStorageError, Exception, RuntimeError, Game search error types., Raised when a compatible game database cannot be read safely., Base class for bounded game-search failures. (+32 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (36): DateResolution, _intersects(), normalize_periods(), NormalizedPeriod, _overlay(), period_from_literals(), Preference, PreferenceState (+28 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (35): PreferredMoveError, PreferredMoveLockError, PreferredMoveSchemaError, Exception, RuntimeError, Read one canonical position schedule through a read-only connection., Base error for bounded preferred-move failures., Raised when the finite SQLite writer reservation cannot be acquired. (+27 more)

### Community 16 - "Community 16"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (29): AnalysisValidationError, _FrozenJsonObject, Any, ValueError, Immutable normalized analysis values and bounded outcome categories., A result whose terminal kind and candidate lines passed position validation., Raised when normalized analysis input is outside the catalogue domain., A JSON-compatible dict whose ordinary mutation operations are disabled. (+21 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (25): _open_connection(), Yield one configured SQLAlchemy Core connection for package internals., DirectProof, DirectVerification, QueryPlanMeasurement, Read-only aggregate facts suitable for bounded direct evidence., Whether the retained canonical preference table is empty., Whether the fixed database exposes exactly the catalogue's ten tables. (+17 more)

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (29): acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, _archive_url(), ArchiveMonth, _current_month() (+21 more)

### Community 20 - "Community 20"
Cohesion: 0.17
Nodes (29): Validate and freeze one JSON object without requiring any setting keys., validate_settings_object(), Position insight helpers., _read_analysis_result(), _read_preference(), _read_queue_state(), _read_statistics_count(), _read_statistics_flag() (+21 more)

### Community 21 - "Community 21"
Cohesion: 0.11
Nodes (29): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+21 more)

### Community 22 - "Community 22"
Cohesion: 0.14
Nodes (31): AcquisitionResult, _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError (+23 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (30): _build_recognition(), _canonical_endpoint(), _endpoint_map(), _load_routes(), lookup_fen(), _materialize_routes(), OpeningRecognitionError, _parse_fen_input() (+22 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (26): _analysis_state(), AnalysisObservation, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationSchemaError, AnalysisObservationState, AnalysisObservationStorageError, AnalysisObservationValidationError (+18 more)

### Community 25 - "Community 25"
Cohesion: 0.12
Nodes (27): AnalysisState, _analysis_state(), PositionInsight, PositionInsightAnalysis, PositionInsightError, PositionInsightRequest, PositionInsightSchemaError, PositionInsightValidationError (+19 more)

### Community 26 - "Community 26"
Cohesion: 0.12
Nodes (25): AnalysisQuality, AnalysisResultInput, NotSavedReason, PublicationOutcome, Enum, A complete engine-independent result payload without position or terminal…, Saved or expected not-saved result for the publication service., Build the successful publication outcome. (+17 more)

### Community 27 - "Community 27"
Cohesion: 0.13
Nodes (24): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+16 more)

### Community 28 - "Community 28"
Cohesion: 0.12
Nodes (24): AnalysisLine, AnalysisScoreKind, AnalysisTerminalKind, str, The two approved score representations., Terminal outcomes derived from a canonical neutral root., One normalized candidate line before terminal or chess-legality checks., AnalysisReadError (+16 more)

### Community 29 - "Community 29"
Cohesion: 0.14
Nodes (25): _canonical_fen(), _clock_date(), _eligible_evidence(), _is_lock_failure(), _load_current_aggregate(), BaseException, date, TrainerColor (+17 more)

### Community 30 - "Community 30"
Cohesion: 0.10
Nodes (27): create(), inspect(), command, Path, Refresh the fixed direct database's opening data., Upgrade an existing exact schema v1 database to schema v2., Inspect any readable SQLite database and emit deterministic Markdown., Create the fixed direct database through the package lifecycle service. (+19 more)

### Community 31 - "Community 31"
Cohesion: 0.11
Nodes (21): Dependency-neutral immutable value for canonical position identity., canonicalize_board(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions., Raised when an input does not describe an acceptable chess position., Validate a board without mutating it and return its legal-only identity. (+13 more)

### Community 32 - "Community 32"
Cohesion: 0.11
Nodes (19): MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError, TrainerColor, Direct, read-only statistics over normalized game occurrences. (+11 more)

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (21): GameSearchValidationError, ValueError, Raised when a game-search query is invalid., GameSearchQuery, Game search query models., All approved collection filters and pagination controls., Translate provably safe scalar and EXISTS filters into SQL., _sql_filter_clauses() (+13 more)

### Community 34 - "Community 34"
Cohesion: 0.19
Nodes (23): Validated canonical chess-position identity services., Public training-requirement composition shim., _coerce_date(), effective_training_balance(), _finite_float(), _finite_result(), game_balance(), minimum_additional_correct_answers() (+15 more)

### Community 35 - "Community 35"
Cohesion: 0.13
Nodes (16): _finite_number(), _normalize_range(), _parse_date(), date, ValueError, Validated models for read-only position training requirements., Validated read-only discovery controls., Raised when a policy or discovery request is invalid. (+8 more)

### Community 36 - "Community 36"
Cohesion: 0.21
Nodes (21): collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., DirectCapabilities, DirectPreflightError, ValueError (+13 more)

### Community 37 - "Community 37"
Cohesion: 0.13
Nodes (20): _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_decision(), _measurement_inputs(), _MeasurementInputs, _median(), _plan_scans_alias() (+12 more)

### Community 38 - "Community 38"
Cohesion: 0.13
Nodes (16): _open_existing_connection(), Yield a configured read-write connection without creating a target., Open one validated connection for an independent import run., Verify that the configured target is an existing compatible v1 database., Yield an opaque all-or-nothing unit of work for one existing v1 database., _assert_compatible_schema(), Assert exact v2 compatibility without changing the open target., _analysis_result() (+8 more)

### Community 39 - "Community 39"
Cohesion: 0.21
Nodes (18): _active_preference(), _current_scoped_groups(), _EvidenceGroup, _group_matches_opening(), _item_sort_key(), _load_occurrences(), _load_opening_matches(), _load_training_aggregates() (+10 more)

### Community 40 - "Community 40"
Cohesion: 0.18
Nodes (19): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+11 more)

### Community 41 - "Community 41"
Cohesion: 0.21
Nodes (15): _atomic_replace(), load_month(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files. (+7 more)

### Community 42 - "Community 42"
Cohesion: 0.16
Nodes (12): Path, The backend judgment and the newly scored training item., Return the resulting scored item using an explicit adapter-friendly name., Judge and persist one answer in an existing compatible database., Submit one validated answer against one explicit existing database., submit_training_answer(), TrainingAnswerRepository, TrainingAnswerResult (+4 more)

### Community 43 - "Community 43"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 44 - "Community 44"
Cohesion: 0.20
Nodes (7): Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, discover_training_requirements(), Path, Discover scored requirements from one explicit existing database., Discover scored position/preferred-move pairs without writing storage., TrainingRequirementRepository

### Community 45 - "Community 45"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 46 - "Community 46"
Cohesion: 0.27
Nodes (10): _compare_games(), _compare_nullable(), _matches(), Game search matching, sorting, and coverage., GameSummary, A public game summary that deliberately contains no SQLite identifiers., _in_datetime_bounds(), _in_numeric_bounds() (+2 more)

### Community 47 - "Community 47"
Cohesion: 0.22
Nodes (10): Raised when the requested current training pair does not exist., TrainingAnswerNotFoundError, Exception, RuntimeError, Base class for bounded training-requirement failures., Raised when persisted training state is newer than the requested date., TrainingRequirementError, TrainingRequirementSchemaError (+2 more)

### Community 48 - "Community 48"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Return one text response., Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response.

### Community 49 - "Community 49"
Cohesion: 0.29
Nodes (7): OpeningInputError, ValueError, Raised when a FEN or PGN query is not an accepted standard-chess input., Path, _read_opening(), PositionInsightOpening, The current public opening label reached at this position.

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SchemaIncompatibleError` connect `Community 31` to `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 20`, `Community 23`, `Community 24`, `Community 25`, `Community 26`, `Community 28`, `Community 29`, `Community 30`, `Community 32`, `Community 33`, `Community 38`, `Community 39`, `Community 42`, `Community 44`, `Community 46`, `Community 49`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `_assert_compatible_schema()` connect `Community 38` to `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 18`, `Community 20`, `Community 23`, `Community 24`, `Community 25`, `Community 26`, `Community 28`, `Community 29`, `Community 31`, `Community 32`, `Community 33`, `Community 35`, `Community 36`, `Community 37`, `Community 39`, `Community 46`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `canonicalize_fen()` connect `Community 33` to `Community 0`, `Community 34`, `Community 2`, `Community 4`, `Community 7`, `Community 8`, `Community 12`, `Community 13`, `Community 46`, `Community 14`, `Community 15`, `Community 20`, `Community 23`, `Community 24`, `Community 25`, `Community 28`, `Community 29`, `Community 31`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `SchemaIncompatibleError` (e.g. with `AnalysisObservationRepository` and `AnalysisReadRepository`) actually correct?**
  _`SchemaIncompatibleError` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `CanonicalPosition` (e.g. with `classify_terminal_kind()` and `_neutral_board()`) actually correct?**
  _`CanonicalPosition` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AnalysisQuality` (e.g. with `AnalysisObservationResult` and `AnalysisReadResult`) actually correct?**
  _`AnalysisQuality` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05691471287801563 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
