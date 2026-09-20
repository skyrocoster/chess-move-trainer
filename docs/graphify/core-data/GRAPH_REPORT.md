# Graph Report - src  (2026-09-19)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1989 nodes · 5541 edges · 76 communities (64 shown, 12 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 284 edges (avg confidence: 0.94)
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

## God Nodes (most connected - your core abstractions)
1. `_assert_compatible_schema()` - 69 edges
2. `SchemaIncompatibleError` - 65 edges
3. `canonicalize_fen()` - 53 edges
4. `CanonicalPosition` - 47 edges
5. `AnalysisQuality` - 43 edges
6. `NormalizedPeriod` - 43 edges
7. `_open_connection()` - 39 edges
8. `PreferredMoveValidationError` - 36 edges
9. `_open_existing_connection()` - 36 edges
10. `StockfishEngine` - 32 edges

## Surprising Connections (you probably didn't know these)
- `BenchmarkJob` --uses--> `StockfishProfile`  [INFERRED]
  chess_move_trainer/database/stockfish/benchmark_models.py → chess_move_trainer/database/stockfish/configuration.py
- `BenchmarkRunner` --uses--> `StockfishProfile`  [INFERRED]
  chess_move_trainer/database/stockfish/benchmark_runner.py → chess_move_trainer/database/stockfish/configuration.py
- `AnalysisObservationRepository` --uses--> `SchemaIncompatibleError`  [INFERRED]
  chess_move_trainer/database/analysis/observation.py → chess_move_trainer/database/schema.py
- `AnalysisReadRepository` --uses--> `SchemaIncompatibleError`  [INFERRED]
  chess_move_trainer/database/analysis/reading.py → chess_move_trainer/database/schema.py
- `AnalysisRepository` --uses--> `SchemaIncompatibleError`  [INFERRED]
  chess_move_trainer/database/analysis/repository.py → chess_move_trainer/database/schema.py

## Import Cycles
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_models.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_readers.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_repository.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `chess_move_trainer/database/openings/recognition.py -> chess_move_trainer/database/openings/source.py -> chess_move_trainer/database/positions/__init__.py -> chess_move_trainer/database/positions/insight.py -> chess_move_trainer/database/positions/insight_helpers.py -> chess_move_trainer/database/openings/recognition.py`

## Communities (76 total, 12 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (74): _ArtifactPaths, ArtifactWriter, AtomicArtifactWriter, _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path() (+66 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (71): Typer application objects., _is_schema_error(), BaseException, Shared CLI rendering and error helpers., Run one fixed-path service and render only its ordinary result data., Render only the five ordinary setup summary counts., _render_preferred_resolution(), _render_preferred_setup() (+63 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (61): _prepare_publication(), Exception, Validate one result against an existing position on a package-owned connection., _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction() (+53 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (56): _preference_from_options(), Public preferred-move schedule values, operations, and storage services., delete_preferred_move(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalResult, put_preferred_move(), Path (+48 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (62): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_existing_connection(), probe_connection(), Connection, Path (+54 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (46): BaseException, Validated canonical chess-position identity services., _canonical_fen(), _clock_date(), _eligible_evidence(), _is_lock_failure(), _load_current_aggregate(), CanonicalPosition (+38 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (35): _canonical_fen(), _parse_mutation_date(), PreferredMoveRemovalRequest, date, One complete parent FEN and one configured half-open interval to remove., parse_date_literal(), Parse exactly one literal ``YYYY-MM-DD`` calendar date., PreferredMoveValidationError (+27 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (49): DirEntry, shutil, _assert_safe_path(), _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text() (+41 more)

### Community 8 - "Community 8"
Cohesion: 0.10
Nodes (41): AnalysisResultInput, AnalysisTerminalKind, profile_for(), AnalysisQuality, The fixed Stockfish profiles supported by the first database worker., Resolve one of the approved fixed profiles., _board_for_position(), _classify_terminal() (+33 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (36): Immutable engine-independent analysis values and input validation., AnalysisObservationError, Base class for bounded FEN-observation failures., AnalysisRequest, AnalysisRequestDisposition, AnalysisRequestError, AnalysisRequestRepository, AnalysisRequestResult (+28 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (34): acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url(), ArchiveMonth (+26 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (38): _build_recognition(), _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached() (+30 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (27): _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database(), MutexUnavailableError, normalize_database_path() (+19 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (24): RuntimeError, Base class for bounded Stockfish process or protocol failures., The process did not complete the finite UCI startup handshake., The Stockfish child process stopped or could not accept a command., The per-analysis watchdog expired before Stockfish returned bestmove., The verified identity reported by the UCI startup handshake., StockfishError, StockfishIdentity (+16 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (30): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+22 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (28): AnalysisLine, A normalized result ready for the engine-independent publisher., Expose candidate lines without requiring callers to unwrap the result., StockfishAnalysis, Stockfish process and database-lock services., MutexBusyError, A finite wait expired because another process owns the mutex., _analysis_result() (+20 more)

### Community 16 - "Community 16"
Cohesion: 0.13
Nodes (37): _interrupted(), _operational_error(), _preferred_period_json(), Exception, _render_preferred_periods(), _render_stockfish_outcome(), _stockfish_operational_error(), _usage_error() (+29 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (31): _coverage_state(), GameCoverage, Analysis and preferred-move coverage over distinct game positions., Read-only, explicit-path search over normalized schema-v1 games. Thin…, _aggregate_games(), _GameAggregates, GameSearchRepository, _load_deepest_openings() (+23 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (29): AnalysisLine, AnalysisValidationError, _FrozenJsonObject, Any, ValueError, Immutable normalized analysis values and bounded outcome categories., A result whose terminal kind and candidate lines passed position validation., Raised when normalized analysis input is outside the catalogue domain. (+21 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (32): GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError, Exception, RuntimeError, ValueError, Game search error types. (+24 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (29): AnalysisError, AnalysisQuality, AnalysisResultInput, AnalysisStorageError, PublicationOutcome, Exception, RuntimeError, A complete engine-independent result payload without position or terminal… (+21 more)

### Community 21 - "Community 21"
Cohesion: 0.10
Nodes (30): PreferenceState, Enum, A state that can be stored for a configured period., Every possible result of resolving a schedule date., ResolutionState, PreferredMoveError, Exception, Base error for bounded preferred-move failures. (+22 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (29): _analysis_state(), AnalysisObservation, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationSchemaError, AnalysisObservationState, AnalysisObservationStorageError (+21 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (29): NormalizationResult, NormalizationWarning, normalize_game(), Return a fully validated game, or one ordinary warning for a skipped input., import_normalized_games(), import_raw_games(), import_raw_month(), import_raw_months() (+21 more)

### Community 24 - "Community 24"
Cohesion: 0.10
Nodes (22): Acquire and publish one complete latest opening catalogue., Dispatch the fixed-path direct opening-update operation., update_openings(), CataloguePublication, import_opening_catalogue(), OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes() (+14 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (29): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+21 more)

### Community 26 - "Community 26"
Cohesion: 0.16
Nodes (29): AnalysisState, chess, _analysis_state(), Path, PositionInsightPreference, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result() (+21 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (27): _finite_number(), ValueError, Raised when a policy or discovery request is invalid., Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, TrainingRequirementValidationError, _coerce_date(), effective_training_balance() (+19 more)

### Community 28 - "Community 28"
Cohesion: 0.13
Nodes (27): Raised when a compatible database contains unusable training data., TrainingRequirementStorageError, _current_scoped_groups(), discover_training_requirements(), _EvidenceGroup, _group_matches_opening(), _item_sort_key(), _load_occurrences() (+19 more)

### Community 29 - "Community 29"
Cohesion: 0.14
Nodes (27): _opening_api_key(), _load_labels(), _load_usage(), _normalize_eco_bound(), OpeningCatalogueError, OpeningCatalogueSchemaError, OpeningCatalogueStorageError, OpeningCatalogueValidationError (+19 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (24): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+16 more)

### Community 31 - "Community 31"
Cohesion: 0.09
Nodes (23): _normalize_range(), parse_calendar_date(), _parse_date(), date, Exception, RuntimeError, Validated models for read-only position training requirements., Validated read-only discovery controls. (+15 more)

### Community 32 - "Community 32"
Cohesion: 0.11
Nodes (25): _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_decision(), _measurement_inputs(), _MeasurementInputs, _median(), _plan_scans_alias() (+17 more)

### Community 33 - "Community 33"
Cohesion: 0.09
Nodes (20): _open_connection(), Yield one configured SQLAlchemy Core connection for package internals., DirectProof, DirectVerification, Read-only aggregate proof helpers for the direct-database boundary., Read-only aggregate facts suitable for bounded direct evidence., Whether the retained canonical preference table is empty., Whether the fixed database exposes exactly the catalogue's ten tables. (+12 more)

### Community 34 - "Community 34"
Cohesion: 0.17
Nodes (28): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+20 more)

### Community 35 - "Community 35"
Cohesion: 0.10
Nodes (21): _assert_compatible_schema(), Assert exact v2 compatibility without changing the open target., MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError (+13 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (24): _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), _normalize_game(), _optional_integer() (+16 more)

### Community 37 - "Community 37"
Cohesion: 0.08
Nodes (23): PositionInsight, PositionInsightError, PositionInsightExperience, PositionInsightObservedMove, PositionInsightObservedMoveTotals, PositionInsightOpening, PositionInsightPreference, PositionInsightSchemaError (+15 more)

### Community 38 - "Community 38"
Cohesion: 0.20
Nodes (23): argparse, ArgumentParser, hashlib, Popen, build_steps(), classify_result(), _command_text(), _documented_storybook_teardown() (+15 more)

### Community 39 - "Community 39"
Cohesion: 0.17
Nodes (21): collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., DirectCapabilities, DirectPreflightError, ValueError (+13 more)

### Community 40 - "Community 40"
Cohesion: 0.14
Nodes (18): _compare(), _matches(), OpeningCatalogueEntry, OpeningCataloguePage, OpeningCatalogueQuery, OpeningCatalogueRepository, Path, One public ECO/name label and its distinct-game usage counts. (+10 more)

### Community 41 - "Community 41"
Cohesion: 0.15
Nodes (16): AnalysisReadError, AnalysisReadRepository, AnalysisReadResult, _line_from_row(), _materialize_result(), Path, RuntimeError, Read the complete current analysis result and candidate lines. (+8 more)

### Community 42 - "Community 42"
Cohesion: 0.18
Nodes (16): _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Game, Path, ValueError (+8 more)

### Community 43 - "Community 43"
Cohesion: 0.21
Nodes (17): _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any, Path (+9 more)

### Community 44 - "Community 44"
Cohesion: 0.18
Nodes (14): NormalizedGame, _game_metadata(), GameRepository, _metadata_parameters(), PersistedGame, Any, PositionIdentity, Persist one game in its own transaction on an already validated connection. (+6 more)

### Community 45 - "Community 45"
Cohesion: 0.20
Nodes (15): canonicalize_board(), canonicalize_fen(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions., Raised when an input does not describe an acceptable chess position., Validate a complete six-field FEN and return its canonical identity. (+7 more)

### Community 46 - "Community 46"
Cohesion: 0.16
Nodes (16): PositionInsightAnalysis, PositionInsightValidationError, ValueError, Current queue state and, when available, the complete current result., Raised when a position-insight request is invalid., PositionInsightRepository, Path, PositionInsightRequest (+8 more)

### Community 47 - "Community 47"
Cohesion: 0.18
Nodes (10): BulkTarget, RuntimeError, Yield game targets followed by route-only targets in stable order., Raised when the live database cannot provide valid bulk targets., Yield the stable initial set, skipping already-current analyses., One eligible canonical position and its imported-game frequency., Return the canonical position consumed by the engine., _target_from_row() (+2 more)

### Community 48 - "Community 48"
Cohesion: 0.19
Nodes (12): AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, Enum, str, The two approved score representations., Terminal outcomes derived from a canonical neutral root., Expected reasons a later publication operation may decline a result. (+4 more)

### Community 49 - "Community 49"
Cohesion: 0.22
Nodes (13): _atomic_replace(), load_month(), merge_current_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files., Raised when a raw month cannot be validated or published safely. (+5 more)

### Community 50 - "Community 50"
Cohesion: 0.21
Nodes (11): _compare_games(), _compare_nullable(), _matches(), Game search matching, sorting, and coverage., _GameData, GameSummary, A public game summary that deliberately contains no SQLite identifiers., _in_datetime_bounds() (+3 more)

### Community 51 - "Community 51"
Cohesion: 0.19
Nodes (10): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkFailure, _prepend(), RuntimeError, Serial direct Tool analysis over the live on-demand target selection., Run the next eligible targets, or all eligible targets when unlimited. (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.19
Nodes (8): position_transaction(), PositionRepository, Path, Canonicalize and persist one complete FEN in an owned transaction., Open one opaque package-owned transaction for grouped position work., Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction.

### Community 53 - "Community 53"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 54 - "Community 54"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 55 - "Community 55"
Cohesion: 0.29
Nodes (11): Stockfish returned malformed or incomplete UCI analysis data., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int(), parse_uci_info(), UCI info parsing and score normalization., Convert Stockfish's side-to-move score to signed White POV. (+3 more)

### Community 56 - "Community 56"
Cohesion: 0.22
Nodes (8): InitialTechnicalPosition, _load_route_moves(), Board, On-demand, authority-defined Stockfish bulk target selection., One stable technical representative in the initial-analysis preset., Return the canonical identity represented by the fixed FEN., _record_route_position(), _RouteMove

### Community 57 - "Community 57"
Cohesion: 0.29
Nodes (5): _position_identity(), _PositionUnitOfWork, PositionIdentity, Opaque position operations bound to one package-owned transaction., Return IDs that may be promoted after the owning transaction commits.

### Community 58 - "Community 58"
Cohesion: 0.24
Nodes (7): Any, Path, BulkTargetSelector, InitialAnalysisTargetSelector, Path, Read stable bounded pages and never persist a target list., Select the fixed 20-common plus five-technical initial mixture.

### Community 59 - "Community 59"
Cohesion: 0.25
Nodes (4): One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., StockfishProfile

### Community 60 - "Community 60"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Return one text response., Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response.

### Community 61 - "Community 61"
Cohesion: 0.29
Nodes (4): BulkOutcome, Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption.

### Community 62 - "Community 62"
Cohesion: 0.33
Nodes (5): _load_position(), CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., _canonical_fen()

### Community 63 - "Community 63"
Cohesion: 0.33
Nodes (6): OpeningInputError, _parse_fen_input(), _parse_pgn_input(), Raised when a FEN or PGN query is not an accepted standard-chess input., Game, ValueError

## Knowledge Gaps
- **1 isolated node(s):** `_PositionInsightStatistics`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 734 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_assert_compatible_schema()` connect `Community 35` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 9`, `Community 11`, `Community 14`, `Community 15`, `Community 17`, `Community 19`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 24`, `Community 26`, `Community 28`, `Community 29`, `Community 32`, `Community 33`, `Community 37`, `Community 39`, `Community 40`, `Community 41`, `Community 44`, `Community 45`, `Community 46`, `Community 47`, `Community 50`, `Community 52`, `Community 56`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `SchemaIncompatibleError` connect `Community 1` to `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 9`, `Community 11`, `Community 14`, `Community 16`, `Community 17`, `Community 19`, `Community 20`, `Community 21`, `Community 22`, `Community 24`, `Community 26`, `Community 28`, `Community 29`, `Community 35`, `Community 37`, `Community 40`, `Community 41`, `Community 45`, `Community 46`, `Community 50`, `Community 52`, `Community 56`, `Community 58`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `canonicalize_fen()` connect `Community 45` to `Community 0`, `Community 3`, `Community 5`, `Community 6`, `Community 9`, `Community 11`, `Community 17`, `Community 19`, `Community 21`, `Community 22`, `Community 24`, `Community 37`, `Community 42`, `Community 46`, `Community 50`, `Community 56`, `Community 57`, `Community 62`, `Community 63`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `SchemaIncompatibleError` (e.g. with `AnalysisObservationRepository` and `AnalysisReadRepository`) actually correct?**
  _`SchemaIncompatibleError` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `canonicalize_fen()` (e.g. with `_sql_filter_clauses()` and `_canonical_endpoint()`) actually correct?**
  _`canonicalize_fen()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `CanonicalPosition` (e.g. with `classify_terminal_kind()` and `_neutral_board()`) actually correct?**
  _`CanonicalPosition` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AnalysisQuality` (e.g. with `AnalysisObservationResult` and `AnalysisReadResult`) actually correct?**
  _`AnalysisQuality` has 10 INFERRED edges - model-reasoned connections that need verification._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
