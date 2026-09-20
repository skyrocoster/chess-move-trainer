# Graph Report - ChessMoveTrainer  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 7170 nodes · 18485 edges · 331 communities (206 shown, 125 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 1257 edges (avg confidence: 0.88)
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
- Community 137
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151
- Community 152
- Community 153
- Community 154
- Community 155
- Community 156
- Community 157
- Community 158
- Community 159
- Community 160
- Community 161
- Community 162
- Community 163
- Community 164
- Community 165
- Community 166
- Community 167
- Community 168
- Community 169
- Community 170
- Community 171
- Community 172
- Community 173
- Community 174
- Community 175
- Community 176
- Community 177
- Community 178
- Community 179
- Community 180
- Community 181
- Community 182
- Community 183
- Community 184
- Community 185
- Community 186
- Community 187
- Community 188
- Community 189
- Community 190
- Community 191
- Community 192
- Community 193
- Community 194
- Community 195
- Community 196
- Community 197
- Community 198
- Community 199
- Community 200
- Community 201
- Community 202
- Community 203
- Community 206
- Community 207
- Community 208
- Community 209
- Community 210
- Community 211
- Community 212
- Community 213
- Community 214
- Community 215
- Community 216
- Community 217
- Community 218
- Community 219
- Community 220
- Community 221
- Community 222
- Community 223
- Community 224
- Community 225
- Community 226
- Community 228
- Community 229
- Community 231
- Community 232
- Community 233
- Community 234
- Community 235
- Community 236
- Community 237
- Community 238
- Community 239
- Community 240
- Community 241
- Community 242
- Community 243
- Community 244
- Community 245
- Community 248
- Community 249
- Community 250
- Community 251
- Community 252
- Community 253
- Community 264
- Community 265
- Community 266
- Community 267
- Community 268
- Community 269
- Community 270
- Community 271
- Community 274
- Community 275
- Community 276
- Community 277
- Community 278
- Community 279
- Community 280
- Community 281
- Community 282
- Community 283
- Community 284
- Community 285
- Community 286
- Community 287
- Community 288
- Community 289
- Community 290
- Community 291
- Community 292
- Community 293
- Community 294
- Community 295
- Community 296
- Community 297
- Community 298
- Community 299
- Community 300
- Community 301
- Community 302
- Community 303
- Community 304
- Community 305
- Community 306
- Community 307
- Community 308
- Community 309
- Community 310
- Community 311
- Community 312
- Community 314
- Community 315
- Community 317
- Community 321
- Community 322
- Community 323
- Community 324
- Community 325
- Community 326
- Community 327
- Community 328
- Community 329
- Community 330

## God Nodes (most connected - your core abstractions)
1. `create_schema()` - 110 edges
2. `react` - 84 edges
3. `vitest` - 78 edges
4. `@storybook/react-vite` - 58 edges
5. `@testing-library/react` - 49 edges
6. `PositionRepository` - 48 edges
7. `NormalizedPeriod` - 47 edges
8. `canonicalize_fen()` - 47 edges
9. `_assert_compatible_schema()` - 42 edges
10. `GameRepository` - 41 edges

## Surprising Connections (you probably didn't know these)
- `test_raw_four_field_storage_input_is_not_accepted()` --calls--> `canonicalize_fen()`  [INFERRED]
  tests/database/test_position_canonicalization.py → src/chess_move_trainer/database/positions/canonicalization.py
- `submit_position_training_answer()` --calls--> `TrainingAnswerRepository`  [INFERRED]
  backend/app/features/position_training_requirements/router.py → src/chess_move_trainer/database/positions/training_answers.py
- `test_answer_decays_signed_credit_before_applying_one()` --calls--> `TrainingAnswerRepository`  [INFERRED]
  tests/database/positions/test_training_answers.py → src/chess_move_trainer/database/positions/training_answers.py
- `test_correct_wrong_and_same_day_answers_move_credit_by_one()` --calls--> `TrainingAnswerRepository`  [INFERRED]
  tests/database/positions/test_training_answers.py → src/chess_move_trainer/database/positions/training_answers.py
- `test_failed_submission_rolls_back_the_upsert()` --calls--> `TrainingAnswerRepository`  [INFERRED]
  tests/database/positions/test_training_answers.py → src/chess_move_trainer/database/positions/training_answers.py

## Import Cycles
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`

## Communities (331 total, 125 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (122): datetime, decimal, LookupError, math, Validated canonical chess-position identity services., _clock_date(), _is_lock_failure(), BaseException (+114 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (122): Immutable engine-independent analysis values and input validation., AnalysisError, AnalysisLine, AnalysisQuality, AnalysisResultInput, AnalysisScoreKind, AnalysisStorageError, AnalysisTerminalKind (+114 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (107): AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient(), StoryAnalysisLifecycleEvent (+99 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (89): _preference_from_options(), _read_preference(), Public preferred-move schedule values, operations, and storage services., _canonical_fen(), _parse_mutation_date(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalRequest (+81 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (89): chess, chess_move_trainer_database_stockfish, MeasurementDecision, pathlib, sqlalchemy, sqlalchemy_pool, sqlite3, _open_connection() (+81 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (79): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisBusyError, EngineLifecycleError, RuntimeError, A tracked engine process could not be started or stopped safely., A short coordinator SQLite transaction could not acquire its lock., Persisted backend analysis contracts., AnalysisProfile (+71 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (99): test_successful_overview_matches_core_calculations(), Exception, RuntimeError, activity_statistics(), _average(), _categories(), _category(), data_quality_statistics() (+91 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (93): CoverageState, functools, GameSearchSort, re, GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError (+85 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (102): deletePreferredMoves(), Options, putPreferredMoves(), requestAnalysis(), submitPositionTrainingAnswer(), AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse (+94 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (76): api_context(), client(), count_reader_calls(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path (+68 more)

### Community 10 - "Community 10"
Cohesion: 0.04
Nodes (65): PageNotFoundView(), Default, meta, Story, FeedbackCore(), MESSAGES, meta, SemanticVariants (+57 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (78): _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_queue_state(), _read_statistics_count() (+70 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (74): createClient(), TODO: we probably want to return error and improve types, ReqInit, CreateClientConfig, BuildUrlFn, Client, ClientOptions, Config (+66 more)

### Community 13 - "Community 13"
Cohesion: 0.04
Nodes (50): frontend_src_api_client_gamedetailresponse, FEEDBACK_TOKENS, here, tokenCss, FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story (+42 more)

### Community 14 - "Community 14"
Cohesion: 0.07
Nodes (63): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+55 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (70): DirEntry, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind(), generate_catalogue() (+62 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (60): frontend_src_api_client_positioninsightresponse, frontend_src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci() (+52 more)

### Community 17 - "Community 17"
Cohesion: 0.05
Nodes (60): frontend_src_api_client_getpositioninsight, ChessSide, Fen, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord() (+52 more)

### Community 18 - "Community 18"
Cohesion: 0.07
Nodes (69): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+61 more)

### Community 19 - "Community 19"
Cohesion: 0.05
Nodes (56): collections_abc, dataclasses, _open_existing_connection(), Yield a configured read-write connection without creating a target., Atomic publication of normalized opening routes into the v1 catalogue tables., position_transaction(), Open one opaque package-owned transaction for grouped position work., _analysis_result() (+48 more)

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (62): frontend_src_api_client_getgame, analysisPanelDisplay(), frontend_src_features_board_adapter_boardadapter_boardorientation, PromotionPiece, San, GameLoader(), handleSubmit(), GameLoaderFailureKind (+54 more)

### Community 21 - "Community 21"
Cohesion: 0.04
Nodes (46): frontend_src_api_client_gethealthoptions, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps, frontend_src_features_app_shell_appshell_module, ConstrainedClosed (+38 more)

### Community 22 - "Community 22"
Cohesion: 0.06
Nodes (59): AnalysisEngine, backend_app_features_analysis, backend_app_features_evaluation, _canonical(), _close_engine(), _drain(), dispatch(), _EngineRegistry (+51 more)

### Community 23 - "Community 23"
Cohesion: 0.09
Nodes (66): EvaluationLockError, EvaluationQueueError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits., A queue state-machine transition is invalid for the current state. (+58 more)

### Community 24 - "Community 24"
Cohesion: 0.07
Nodes (64): Canonical key from the validated query, resolved database, and policy., training_requirements_key(), ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input. (+56 more)

### Community 25 - "Community 25"
Cohesion: 0.08
Nodes (61): AnalysisCandidate, canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, _connect_read_only(), _database_guard(), _exact_fen_count() (+53 more)

### Community 26 - "Community 26"
Cohesion: 0.06
Nodes (57): sqlalchemy_engine, _validate_lock_timeout(), Open one validated connection for an independent import run., Verify that the configured target is an existing compatible v1 database., Package-owned database connection services., _cell(), _column_kind(), _foreign_keys() (+49 more)

### Community 27 - "Community 27"
Cohesion: 0.04
Nodes (50): HealthyContent, meta, Story, UnexpectedFailureTryAgain, Constrained, Empty, FinalBoundary, InitialBoundary (+42 more)

### Community 28 - "Community 28"
Cohesion: 0.06
Nodes (52): frontend_src_api_client_getopenings, frontend_src_api_client_getopeningsdata, frontend_src_api_client_getpositiontrainingrequirementsdata, frontend_src_api_client_openingcatalogueitemresponse, frontend_src_api_client_openingcatalogueresponse, frontend_src_api_client_trainingrequirementitemresponse, frontend_src_api_client_trainingrequirementresponse, writeOpeningCatalogueSnapshot() (+44 more)

### Community 29 - "Community 29"
Cohesion: 0.06
Nodes (46): ctypes, os, _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database() (+38 more)

### Community 30 - "Community 30"
Cohesion: 0.05
Nodes (47): AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, AnalysisObservationErrorResponse (+39 more)

### Community 31 - "Community 31"
Cohesion: 0.07
Nodes (56): frontend_src_api_client_deletepreferredmoves, frontend_src_api_client_getpreferredmoves, frontend_src_api_client_preferredmovesmutationresponse, frontend_src_api_client_preferredmovesremovalresponse, frontend_src_api_client_preferredmovesresponse, frontend_src_api_client_preferredmovessegmentresponse, frontend_src_api_client_putpreferredmoves, deletePreferredMove() (+48 more)

### Community 32 - "Community 32"
Cohesion: 0.05
Nodes (47): BoardAdapter(), BoardAdapterProps, BoardRender(), frontend_src_features_board_adapter_boardadapter_module, PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, frontend_src_features_board_adapter_boardadapter_starting_fen, BlackOrientation (+39 more)

### Community 33 - "Community 33"
Cohesion: 0.06
Nodes (44): CliRunner, _position_sort_key(), PreferredMoveInferenceResult, CanonicalPosition, Return a read-only position-to-period view for downstream consumers., All configured position schedules produced by one pure inference run., Return the per-position schedules using the storage-facing name., PreferenceState (+36 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (51): Canonical key from the validated statistics overview query and resolved…, statistics_overview_key(), ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse, CategoryPerformanceResponse, ContractModel, DataQualityStatisticsResponse (+43 more)

### Community 35 - "Community 35"
Cohesion: 0.14
Nodes (49): benchmark_client(), benchmark_database(), create_benchmark_database(), _database_info(), _float_env(), _int_env(), _output_dir(), fixture (+41 more)

### Community 36 - "Community 36"
Cohesion: 0.10
Nodes (40): AnalysisStorageError, Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp() (+32 more)

### Community 37 - "Community 37"
Cohesion: 0.07
Nodes (32): catalogueDemoShell(), AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport, OPTIONS (+24 more)

### Community 38 - "Community 38"
Cohesion: 0.08
Nodes (42): httpx, acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url() (+34 more)

### Community 39 - "Community 39"
Cohesion: 0.09
Nodes (42): ArgumentParser, Process-local cache for safe repeated backend reads. Bounded…, Managed, per-owner Stockfish process and result-conversion boundary., Explicit, pinned, checksum-first Stockfish provisioning without import effects., cachetools, chess_move_trainer_database_stockfish_configuration, hashlib, json (+34 more)

### Community 40 - "Community 40"
Cohesion: 0.07
Nodes (47): client, getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight() (+39 more)

### Community 41 - "Community 41"
Cohesion: 0.05
Nodes (37): EvalBar(), EvalBarDisplayState, EvalBarProps, BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp (+29 more)

### Community 42 - "Community 42"
Cohesion: 0.10
Nodes (34): AnalysisClient, AnalysisFailureCode, AnalysisObservation, AnalysisOperationResult, defaultAnalysisClient, frontend_src_features_analysis_analysisapi_positionkeyfromfen, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey() (+26 more)

### Community 43 - "Community 43"
Cohesion: 0.07
Nodes (36): AnalysisCandidate, canonical_fen(), position_key_from_fen(), Return the internal identity without changing the public six-field FEN., Return a strict canonical six-field FEN or reject it., Return the internal four-field identity for a valid canonical six-field FEN., initialize_analysis_schema(), Create the analysis namespace only through this explicit operation. (+28 more)

### Community 44 - "Community 44"
Cohesion: 0.10
Nodes (44): _classify_board(), classify_terminal_kind(), _neutral_board(), AnalysisLine, AnalysisTerminalKind, Board, CanonicalPosition, ValidatedAnalysisResult (+36 more)

### Community 45 - "Community 45"
Cohesion: 0.07
Nodes (37): clearPending(), isPromotionCandidate(), PickerLiveRegion(), PROMOTION_OPTIONS, PromotionColor, PromotionCommit, PromotionController, PromotionControllerOptions (+29 more)

### Community 46 - "Community 46"
Cohesion: 0.08
Nodes (37): sanFromFenAndUci(), SelectedTransition, PreferredMoveValue, contextFailureMessage(), failureMessage(), frontend_src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMovePanel() (+29 more)

### Community 47 - "Community 47"
Cohesion: 0.09
Nodes (34): createMoveHistoryRows(), KEY_NAVIGATION, frontend_src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow (+26 more)

### Community 48 - "Community 48"
Cohesion: 0.09
Nodes (37): OpeningCatalogueSort, _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError (+29 more)

### Community 49 - "Community 49"
Cohesion: 0.10
Nodes (40): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+32 more)

### Community 50 - "Community 50"
Cohesion: 0.08
Nodes (41): analysis_key(), _current_signature(), opening_detail_key(), openings_catalogue_version(), openings_key(), Path, Fingerprint the database main file and SQLite sidecars without creating…, Return a bounded opaque version for the database and SQLite sidecars. (+33 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (33): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerPresentation, BoardAnswerStatus, BoardSquareHighlight (+25 more)

### Community 52 - "Community 52"
Cohesion: 0.09
Nodes (40): game_detail_key(), games_key(), json_response(), Serialize one response model exactly like Starlette's JSONResponse., Canonical key from the validated games query and resolved database., Canonical key for one immutable game-detail read., Wrap one cached or freshly computed payload in a fresh response., serialize_response_body() (+32 more)

### Community 53 - "Community 53"
Cohesion: 0.08
Nodes (28): Return the current result value for callers using a result/read shape., Return the later CLI-compatible status for this service outcome., MutexBusyError, A finite wait expired because another process owns the mutex., Whether the successful acquisition recovered an abandoned owner., _analysis_result(), _finite_non_negative(), _finite_positive() (+20 more)

### Community 54 - "Community 54"
Cohesion: 0.07
Nodes (32): Button(), ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story, VariantMatrix (+24 more)

### Community 55 - "Community 55"
Cohesion: 0.08
Nodes (35): ButtonProps, actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave (+27 more)

### Community 56 - "Community 56"
Cohesion: 0.06
Nodes (34): PositionPickerMoveRecord, EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading (+26 more)

### Community 57 - "Community 57"
Cohesion: 0.14
Nodes (35): collections, _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves() (+27 more)

### Community 58 - "Community 58"
Cohesion: 0.14
Nodes (34): LineLibrary(), nodeName(), sameIds(), selectionDescription(), LineLibraryTree(), LineLibraryTreeProps, nodeName(), Default (+26 more)

### Community 59 - "Community 59"
Cohesion: 0.12
Nodes (30): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+22 more)

### Community 60 - "Community 60"
Cohesion: 0.11
Nodes (33): chess_move_trainer_database_games_configuration, AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping() (+25 more)

### Community 61 - "Community 61"
Cohesion: 0.07
Nodes (29): frontend_src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story, CatalogueLink (+21 more)

### Community 62 - "Community 62"
Cohesion: 0.10
Nodes (23): RuntimeError, TimeoutError, Base class for bounded Stockfish process or protocol failures., The process did not complete the finite UCI startup handshake., The Stockfish child process stopped or could not accept a command., The per-analysis watchdog expired before Stockfish returned bestmove., The verified identity reported by the UCI startup handshake., StockfishError (+15 more)

### Community 63 - "Community 63"
Cohesion: 0.13
Nodes (34): AnalysisSchemaError, The independently versioned analysis schema is absent or incompatible., _existing_tables(), migrate_position_key_schema(), Connection, Explicit initialization for the independent analysis schema., Validate the v1 shape accepted by the one-time position-key transition., Reset disposable v1 analysis and queue rows in one transaction. (+26 more)

### Community 64 - "Community 64"
Cohesion: 0.10
Nodes (32): frontend_src_api_client_getanalysis, frontend_src_api_client_requestanalysis, AnalysisFailure, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis() (+24 more)

### Community 65 - "Community 65"
Cohesion: 0.08
Nodes (34): frontend_src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+26 more)

### Community 66 - "Community 66"
Cohesion: 0.11
Nodes (31): itertools, NormalizationResult, NormalizationWarning, import_normalized_games(), import_raw_games(), import_raw_month(), import_raw_months(), load_normalized_months() (+23 more)

### Community 67 - "Community 67"
Cohesion: 0.12
Nodes (34): alias, preferred_moves_key(), Canonical key for one validated preferred-move timeline., delete_preferred_moves(), _error(), get_preferred_moves(), _mutation_period_response(), _mutation_preference() (+26 more)

### Community 68 - "Community 68"
Cohesion: 0.13
Nodes (29): Own the top-level lock, read selected games, then coordinate safe writes., run_selected_games(), _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult, Path (+21 more)

### Community 69 - "Community 69"
Cohesion: 0.20
Nodes (32): delete_preferred_move(), put_preferred_move(), Path, Atomically apply one ordinary preferred-move mutation value., Atomically remove one ordinary preferred-move interval value., _database(), _period_values(), parametrize (+24 more)

### Community 70 - "Community 70"
Cohesion: 0.13
Nodes (28): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+20 more)

### Community 71 - "Community 71"
Cohesion: 0.09
Nodes (25): random, load_positions(), Any, Path, Benchmark loading and top-level invocation., Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark() (+17 more)

### Community 72 - "Community 72"
Cohesion: 0.11
Nodes (32): position_insight_key(), Canonical key for one validated position insight., ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse (+24 more)

### Community 73 - "Community 73"
Cohesion: 0.09
Nodes (25): invalidateAnalysisObservation(), invalidatePositionInsight(), invalidatePreferredMove(), invalidateTrainingRequirements(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput (+17 more)

### Community 74 - "Community 74"
Cohesion: 0.18
Nodes (23): _database(), _FakeClock, _FakeEngine, _FakeMutex, Any, Path, _queue_row(), _runner() (+15 more)

### Community 75 - "Community 75"
Cohesion: 0.11
Nodes (22): AnalysisLine, AnalysisResult, AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv(), formatScore() (+14 more)

### Community 76 - "Community 76"
Cohesion: 0.08
Nodes (12): Queue, _FakeFactory, _FakeProcess, _FakeStdin, _FakeStdout, Any, test_engine_applies_fixed_options_clears_hash_and_returns_complete_pvs(), test_identity_failure_terminates_the_child() (+4 more)

### Community 77 - "Community 77"
Cohesion: 0.13
Nodes (18): _counts(), FixedClock, _game_fixture(), GameTransport, OpeningTransport, Any, datetime, MonkeyPatch (+10 more)

### Community 78 - "Community 78"
Cohesion: 0.12
Nodes (28): Ply, strictFen(), GAME, GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession() (+20 more)

### Community 79 - "Community 79"
Cohesion: 0.11
Nodes (27): _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _is_expected_stockfish(), _line_from_info(), _metrics_for(), AnalysisLine (+19 more)

### Community 80 - "Community 80"
Cohesion: 0.13
Nodes (28): chess_pgn, Headers, io, _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp() (+20 more)

### Community 81 - "Community 81"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 82 - "Community 82"
Cohesion: 0.14
Nodes (29): Enum, Overlay one configured preference on an ordered current schedule., Remove configuration from a half-open range., Every possible result of resolving a schedule date., ResolutionState, set_preference(), unset_preference(), period() (+21 more)

### Community 83 - "Community 83"
Cohesion: 0.18
Nodes (19): BenchmarkRunner, BenchmarkSpec, _fake_analysis(), _FakeEngine, _FakeFactory, _InjectedWriter, Any, Path (+11 more)

### Community 84 - "Community 84"
Cohesion: 0.19
Nodes (28): OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryNode, booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys() (+20 more)

### Community 85 - "Community 85"
Cohesion: 0.11
Nodes (22): GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game(), _occurrence_from_row(), _optional_int(), _optional_text() (+14 more)

### Community 86 - "Community 86"
Cohesion: 0.11
Nodes (17): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Raised when a compatible database cannot publish the opening catalogue., Immutable counts describing one successfully committed catalogue replacement. (+9 more)

### Community 87 - "Community 87"
Cohesion: 0.17
Nodes (28): lookup_fen(), OpeningInputError, OpeningRecognition, _parse_pgn_input(), Game, ValueError, Raised when a FEN or PGN query is not an accepted standard-chess input., An immutable ordered recognition timeline and its selected current label. (+20 more)

### Community 88 - "Community 88"
Cohesion: 0.09
Nodes (21): clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), frontend_src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage(), RepertoireResponsiveStage() (+13 more)

### Community 89 - "Community 89"
Cohesion: 0.17
Nodes (25): checkA11y(), DistributionLabelBox, expectActiveSessionHistoryEntry(), expectBothRelationshipBoxes(), expectDateFreePreferredPanel(), expectDistributionChartAndControlsClean(), expectNoHorizontalOverflow(), expectPanelMinimums() (+17 more)

### Community 90 - "Community 90"
Cohesion: 0.09
Nodes (23): engines, node, name, private, type, version, eslint, @eslint/js (+15 more)

### Community 91 - "Community 91"
Cohesion: 0.09
Nodes (18): Combobox(), RadioGroup(), RadioGroupProps, RadioOption, filterOpeningCatalogue(), frontend_src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox() (+10 more)

### Community 92 - "Community 92"
Cohesion: 0.22
Nodes (23): PublicationOutcome, Saved or expected not-saved result for the publication service., Build the successful publication outcome., Build an expected not-saved outcome with its explicit reason., test_public_validation_outcomes_distinguish_expected_not_saved_reasons(), _line(), _lines(), AnalysisLine (+15 more)

### Community 93 - "Community 93"
Cohesion: 0.16
Nodes (25): _atomic_write(), publish_schema(), Path, ValueError, Raised when publication would replace the selected database., Inspect a database and atomically publish its deterministic Markdown., SchemaPublicationCollisionError, _validate_output_path() (+17 more)

### Community 94 - "Community 94"
Cohesion: 0.31
Nodes (23): _archive_url(), _config(), FixedClock, _fixture(), _month_url(), AcquireConfiguration, Any, datetime (+15 more)

### Community 95 - "Community 95"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 96 - "Community 96"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 97 - "Community 97"
Cohesion: 0.20
Nodes (19): GameRepository, Persist complete normalized games without exposing database handles., _count(), _game_snapshot(), MonkeyPatch, Path, _raw(), test_batched_occurrence_writes_preserve_exact_rows() (+11 more)

### Community 98 - "Community 98"
Cohesion: 0.18
Nodes (25): _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached(), _load_routes_uncached() (+17 more)

### Community 99 - "Community 99"
Cohesion: 0.15
Nodes (22): create_schema(), Path, Create schema v2 or accept an exactly compatible existing database., _remove_new_target(), Path, test_grouped_resolution_rolls_back_when_later_work_fails(), test_position_remains_after_a_focused_reference_is_removed(), test_successful_multiple_resolution_composes_through_opaque_unit_of_work() (+14 more)

### Community 100 - "Community 100"
Cohesion: 0.14
Nodes (17): contextlib, Per-game repository and persistence models., _find_existing_position_id(), _position_identity(), PositionStorageError, _PositionUnitOfWork, CanonicalPosition, PositionIdentity (+9 more)

### Community 101 - "Community 101"
Cohesion: 0.19
Nodes (22): csv, _StoredAttempts, BenchmarkCompatibilityError, BenchmarkJob, Existing output state does not belong to the requested benchmark., A stable identity for one position/profile/round analysis., _current_job_sets(), _job_fields() (+14 more)

### Community 102 - "Community 102"
Cohesion: 0.18
Nodes (24): _consume_header(), load_opening_sources(), OpeningSourceError, Game, Path, ValueError, Reject movetext that the permissive PGN reader would silently skip., Raised when the complete five-file opening source cannot be accepted. (+16 more)

### Community 103 - "Community 103"
Cohesion: 0.10
Nodes (18): MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError, TrainerColor, Count outgoing moves and derive trainer/opponent actors from stored facts. (+10 more)

### Community 104 - "Community 104"
Cohesion: 0.12
Nodes (21): _configured_float(), get_rebuilt_database_path(), get_training_requirement_policy(), Path, Application dependencies for database capabilities., Return the explicit clean database path for the current application process., Return the configured policy, or ``None`` when the capability is unavailable., api_context() (+13 more)

### Community 105 - "Community 105"
Cohesion: 0.26
Nodes (20): client(), _database(), fixture, MonkeyPatch, parametrize, Path, TestClient, test_browsing_list_does_not_modify_database() (+12 more)

### Community 106 - "Community 106"
Cohesion: 0.15
Nodes (20): api_context(), client(), create_preferred_moves_database(), fixture, MonkeyPatch, Path, TestClient, request_params() (+12 more)

### Community 107 - "Community 107"
Cohesion: 0.15
Nodes (19): api_context(), client(), create_statistics_database(), _insert_game(), _params(), Connection, parametrize, Path (+11 more)

### Community 108 - "Community 108"
Cohesion: 0.23
Nodes (22): chess_move_trainer_database_openings_keys, OpeningCatalogueQuery, OpeningCatalogueRepository, Path, Browse normalized openings without exposing a database connection., Read one exact public opening key from an explicit database path., The filters, ordering, and pagination controls for one catalogue read., read_opening() (+14 more)

### Community 109 - "Community 109"
Cohesion: 0.14
Nodes (21): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions. (+13 more)

### Community 110 - "Community 110"
Cohesion: 0.16
Nodes (16): chess_move_trainer_database_preferred_moves, _period_values(), parametrize, Path, _run_serialized_delete_and_put(), delete_mutation(), first_target(), put_mutation() (+8 more)

### Community 111 - "Community 111"
Cohesion: 0.13
Nodes (19): _LiveQueueRequest, RuntimeError, QueueCompletionOutcome, QueueError, QueueQualityError, QueueStorageError, Queue errors, claims, and live-request views., Result of one matching-token completion attempt. (+11 more)

### Community 112 - "Community 112"
Cohesion: 0.27
Nodes (18): _line(), _lines(), AnalysisLine, AnalysisQuality, Path, _repository(), _result(), _snapshot() (+10 more)

### Community 113 - "Community 113"
Cohesion: 0.18
Nodes (15): _database(), _FakeEngine, _FakeMutex, AnalysisResultInput, Path, PublicationOutcome, _RecordingPublisher, _runner() (+7 more)

### Community 114 - "Community 114"
Cohesion: 0.16
Nodes (20): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), probe_connection(), Connection, Path, Ordinary data describing the settings verified on an opened database. (+12 more)

### Community 115 - "Community 115"
Cohesion: 0.09
Nodes (21): allowScripts, esbuild@0.25.12, esbuild@0.28.2, devDependencies, @axe-core/playwright, @playwright/mcp, @playwright/test, vite (+13 more)

### Community 116 - "Community 116"
Cohesion: 0.13
Nodes (18): PositionRepository, Path, Resolve canonical positions using package-owned connections and transactions., Canonicalize and persist one board in an owned transaction., Canonicalize and persist one complete FEN in an owned transaction., CompletedProcess, Path, _run_worker() (+10 more)

### Community 117 - "Community 117"
Cohesion: 0.24
Nodes (9): _ArtifactPaths, BenchmarkPersistenceError, An artifact could not be persisted safely after bounded retries., _checkpoint_payload(), BenchmarkRunner, Any, BaseException, Path (+1 more)

### Community 118 - "Community 118"
Cohesion: 0.17
Nodes (20): ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse, PreferredMovesMutationRequest (+12 more)

### Community 119 - "Community 119"
Cohesion: 0.18
Nodes (19): NotSavedReason, sqlalchemy_exc, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput (+11 more)

### Community 120 - "Community 120"
Cohesion: 0.25
Nodes (18): Path, Request one desired analysis through an explicit app database path., request_analysis(), _database(), _position_with_result(), AnalysisQuality, Path, _queue_row() (+10 more)

### Community 121 - "Community 121"
Cohesion: 0.27
Nodes (18): PreferredMoveTimelineRepository, Path, Read one preferred-move timeline from an explicit database path., _configured_database(), _database(), parametrize, Path, _request() (+10 more)

### Community 122 - "Community 122"
Cohesion: 0.14
Nodes (17): SYNTHETIC_OPENING_RESPONSE, filterKind(), OpeningLineLibraryFailure, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType, OpeningLineLibraryGroupNode, OpeningLineLibraryLineNode, OpeningLineLibraryNodeBase (+9 more)

### Community 123 - "Community 123"
Cohesion: 0.18
Nodes (16): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+8 more)

### Community 124 - "Community 124"
Cohesion: 0.15
Nodes (10): @axe-core/playwright, checkA11y(), STORY_IDS, isAxeBusyError(), retryAxeWhenBusy(), waitForStorybookRender(), checkA11y(), assertFixtureStates() (+2 more)

### Community 125 - "Community 125"
Cohesion: 0.39
Nodes (18): PreferredMoveSetupService, Infer and atomically initialize an empty preferred-move schedule., _count_periods(), _database(), _game(), _position(), Connection, Path (+10 more)

### Community 126 - "Community 126"
Cohesion: 0.34
Nodes (18): Path, QueueService, Own the live queue lifecycle without holding SQLite during engine work., AnalysisQuality, Path, _queue_row(), _result(), _setup() (+10 more)

### Community 127 - "Community 127"
Cohesion: 0.25
Nodes (15): _catalogue_snapshot(), MonkeyPatch, Path, _rows(), _source_dir(), test_deletion_checkpoint_order_is_child_first(), test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(), test_first_publication_writes_labels_routes_and_contiguous_children() (+7 more)

### Community 128 - "Community 128"
Cohesion: 0.15
Nodes (16): chess_move_trainer_database, chess_move_trainer_database_analysis, chess_move_trainer_database_statistics, AnalysisQuality, AnalysisResultInput, Path, _result(), test_analysis_reader_returns_complete_current_result() (+8 more)

### Community 129 - "Community 129"
Cohesion: 0.24
Nodes (15): copy, _count(), FixedClock, _fixture(), _game_url(), _month_url(), Any, datetime (+7 more)

### Community 130 - "Community 130"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 131 - "Community 131"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 132 - "Community 132"
Cohesion: 0.29
Nodes (16): _balance(), _fixture(), _game(), _occurrence(), Connection, parametrize, Path, _request() (+8 more)

### Community 133 - "Community 133"
Cohesion: 0.18
Nodes (15): asyncio, managed(), parametrize, _real_python_chess_process(), test_engine_instance_refuses_concurrent_worker_sharing(), test_engine_serializes_mate_given_separately_from_mate_zero(), test_hard_watchdog_terminates_only_tracked_engine_and_proves_pid_exit(), test_managed_engine_configures_multipv_only_on_analysis_and_isolates_order() (+7 more)

### Community 134 - "Community 134"
Cohesion: 0.22
Nodes (15): _position_id(), _post(), MonkeyPatch, parametrize, Path, _queue_row(), test_bad_values_give_clear_error(), test_finished_analysis_is_reused_and_ignores_unknown_fields() (+7 more)

### Community 135 - "Community 135"
Cohesion: 0.19
Nodes (14): _params(), MonkeyPatch, parametrize, Path, _target_position_id(), test_bad_values_give_clear_error(), test_injected_database_is_used_when_configured(), test_known_position_returns_full_insight_and_ignores_unknown_filters() (+6 more)

### Community 136 - "Community 136"
Cohesion: 0.20
Nodes (14): delete_body(), MonkeyPatch, parametrize, Path, test_delete_bad_values_give_clear_error(), test_delete_locked_database_gives_unavailable_without_changing_file(), test_delete_makes_get_and_insight_show_unconfigured(), test_delete_missing_or_broken_database_gives_unavailable_without_creating_file() (+6 more)

### Community 137 - "Community 137"
Cohesion: 0.17
Nodes (13): put_body(), MonkeyPatch, parametrize, Path, test_concurrent_puts_both_succeed_and_get_shows_both(), test_put_bad_values_give_clear_error(), test_put_locked_database_gives_unavailable_without_changing_file(), test_put_missing_or_broken_database_gives_unavailable_without_creating_file() (+5 more)

### Community 138 - "Community 138"
Cohesion: 0.14
Nodes (15): chess_move_trainer_database_games, chess_move_trainer_database_games_reading, Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, Path, Read one public game detail from an explicit database path., One public replay occurrence without SQLite identity fields. (+7 more)

### Community 139 - "Community 139"
Cohesion: 0.18
Nodes (15): chess_move_trainer_database_schema, _normalized_sql(), Connection, Path, test_canonical_resource_is_installed_and_schema_is_exact(), test_unique_constraints_are_exact_and_internal_autoindexes_only(), _create_v1_database(), _data_snapshot() (+7 more)

### Community 140 - "Community 140"
Cohesion: 0.13
Nodes (13): frontend_src_api_client_getpositiontrainingrequirements, ContractOperation, dirname, ALLOWED_RUNTIME_CLIENT_IMPORTS, dirname, SOURCE_EXTENSIONS, srcDir, dirname (+5 more)

### Community 141 - "Community 141"
Cohesion: 0.18
Nodes (14): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+6 more)

### Community 142 - "Community 142"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 143 - "Community 143"
Cohesion: 0.16
Nodes (14): clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart(), renderLabel() (+6 more)

### Community 144 - "Community 144"
Cohesion: 0.25
Nodes (16): normalize_game(), Return a fully validated game, or one ordinary warning for a skipped input., _fixture(), parametrize, test_draw_mapping_and_pgn_termination_fallback(), test_ineligible_malformed_and_illegal_inputs_are_ordinary_skips(), test_invalid_required_raw_fields_are_skipped(), test_non_unique_trainer_and_non_normal_start_are_skipped() (+8 more)

### Community 145 - "Community 145"
Cohesion: 0.14
Nodes (6): ast, Path, _python_sources(), test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin(), test_database_package_has_no_legacy_or_production_import_direction(), test_package_contains_no_runtime_wrapper_or_copied_legacy_generator()

### Community 146 - "Community 146"
Cohesion: 0.19
Nodes (12): MonkeyPatch, parametrize, Path, _queue(), _remove_result(), _target_position_id(), test_injected_database_is_used_when_configured(), test_missing_or_bad_position_gives_clear_error() (+4 more)

### Community 147 - "Community 147"
Cohesion: 0.13
Nodes (14): booleanFilterData, data, LineLibraryCommitDescription, LineLibraryFilterKind, LineLibraryFilterOption, LineLibraryNodeKind, LineLibraryNodeSelectionDeclaration, LineLibraryRowContext (+6 more)

### Community 148 - "Community 148"
Cohesion: 0.20
Nodes (13): collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue(), sourceRoot, statusTagByRoot (+5 more)

### Community 149 - "Community 149"
Cohesion: 0.24
Nodes (13): shutil, _catalogue_snapshot(), _copy_sources(), _fixture_game(), _game_snapshot(), _latest_files(), OpeningTransport, BaseException (+5 more)

### Community 150 - "Community 150"
Cohesion: 0.21
Nodes (15): RuntimeError, Raised when a raw month cannot be validated or published safely., RawMonthError, _fixture(), BaseException, parametrize, Path, test_current_merge_replaces_adds_and_retains_in_deterministic_order() (+7 more)

### Community 151 - "Community 151"
Cohesion: 0.26
Nodes (13): _normalized(), MonkeyPatch, parametrize, Path, _raw(), _rows(), test_correction_failure_at_each_boundary_preserves_prior_game(), test_fresh_game_persists_exact_metadata_positions_and_occurrences() (+5 more)

### Community 152 - "Community 152"
Cohesion: 0.27
Nodes (15): BaseException, parametrize, Path, repository(), test_boundary_requires_exactly_four_valid_fen_fields(), test_failed_replacement_restores_the_preexisting_schedule(), test_failure_or_interruption_rolls_back_standalone_position_and_period(), checkpoint() (+7 more)

### Community 153 - "Community 153"
Cohesion: 0.18
Nodes (9): _common_fens(), _database(), _FakeEngine, _FakeMutex, Path, test_initial_analysis_is_serial_resumable_direct_and_queue_free(), engine_factory(), mutex_factory() (+1 more)

### Community 154 - "Community 154"
Cohesion: 0.19
Nodes (14): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+6 more)

### Community 155 - "Community 155"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 156 - "Community 156"
Cohesion: 0.25
Nodes (14): Color, Stockfish returned malformed or incomplete UCI analysis data., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int(), parse_uci_info(), AnalysisScoreKind (+6 more)

### Community 157 - "Community 157"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 158 - "Community 158"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 159 - "Community 159"
Cohesion: 0.29
Nodes (14): Path, Read one FEN observation from an explicit app database path., read_analysis_observation(), _database(), parametrize, Path, _queue(), _result() (+6 more)

### Community 160 - "Community 160"
Cohesion: 0.17
Nodes (14): _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path(), BaseException, OSError, Atomic artifact persistence for benchmarks. (+6 more)

### Community 161 - "Community 161"
Cohesion: 0.24
Nodes (12): _archive(), _fake_verifier(), parametrize, Path, test_checksum_failure_happens_before_extraction_and_cleans_everything(), test_explicit_override_verifies_identity_and_checksum_without_install(), test_pinned_setup_is_checksum_first_atomic_and_cleans_staging(), download() (+4 more)

### Community 162 - "Community 162"
Cohesion: 0.21
Nodes (14): argparse, fnmatch, count_lines(), is_excluded(), is_test_file(), main(), print_report(), Path (+6 more)

### Community 163 - "Community 163"
Cohesion: 0.28
Nodes (14): api_context(), client(), create_insight_database(), _game(), _install_analysis(), _install_opening(), _install_preferences(), _occurrence() (+6 more)

### Community 164 - "Community 164"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 165 - "Community 165"
Cohesion: 0.32
Nodes (13): _add_game_occurrences(), _add_route(), _database(), _position_ids(), AnalysisQuality, MonkeyPatch, parametrize, Path (+5 more)

### Community 166 - "Community 166"
Cohesion: 0.19
Nodes (8): AnalysisLockError, Another top-level analysis operator owns the database lock., AnalysisRunLock, BaseException, Path, A single OS-owned lock for one top-level analysis invocation., Hold a one-byte lock whose lifetime is tied to an open OS file handle., TracebackType

### Community 167 - "Community 167"
Cohesion: 0.18
Nodes (10): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelIntent, AnalysisPanelResult, AnalysisPanelResultMetadata, InlineWdl(), resultMetadataLabel(), WdlItem (+2 more)

### Community 168 - "Community 168"
Cohesion: 0.19
Nodes (11): AnalysisPanelDisplay, AnalysisPanelLine, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay() (+3 more)

### Community 169 - "Community 169"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 170 - "Community 170"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 171 - "Community 171"
Cohesion: 0.23
Nodes (11): NormalizedGame, _game_metadata(), _metadata_parameters(), PersistedGame, Any, PositionIdentity, Persist one game in its own transaction on an already validated connection., Persist one game while the caller owns the active transaction. (+3 more)

### Community 172 - "Community 172"
Cohesion: 0.23
Nodes (7): ArtifactWriter, AtomicArtifactWriter, Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 173 - "Community 173"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 174 - "Community 174"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 175 - "Community 175"
Cohesion: 0.27
Nodes (10): _bounded_call(), close_process(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, Bounded, idempotent graceful quit with a tracked-process-only fallback., sha256_file() (+2 more)

### Community 176 - "Community 176"
Cohesion: 0.17
Nodes (6): _EventLoopTransportStub, Minimal asyncio.SubprocessTransport-shaped stub with a mutable return code., Real asyncio event that fails loudly if lifecycle code ever awaits it., SimpleEngine-shaped stub whose shutdown flag is a real asyncio.Event., _SimpleEngineStub, _StrictAsyncioEvent

### Community 177 - "Community 177"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 178 - "Community 178"
Cohesion: 0.18
Nodes (6): fulfillJson(), mockCatalogue(), OPENING_ITEMS, TRAINING_ERROR, TRAINING_ITEM, TRAINING_RESPONSE_BASE

### Community 179 - "Community 179"
Cohesion: 0.20
Nodes (5): EngineProcess, Board, Protocol, Only the process operations the managed boundary is allowed to use., Limit

### Community 180 - "Community 180"
Cohesion: 0.27
Nodes (8): canonicalize_fen(), Validate a complete six-field FEN and return its canonical identity., _canonical_fen(), parametrize, test_board_input_does_not_mutate_classic_en_passant_state(), test_impossible_en_passant_geometry_is_rejected_instead_of_repaired(), test_legal_only_en_passant_normalization(), test_malformed_en_passant_target_is_rejected()

### Community 181 - "Community 181"
Cohesion: 0.22
Nodes (5): _engine_shutdown_poll(), PythonChessProcess, Bounded synchronous proof that a python-chess child is shut down and exited.…, A tracked python-chess process; termination is limited to its own transport., SimpleEngine

### Community 182 - "Community 182"
Cohesion: 0.29
Nodes (10): Pinned Stockfish provisioning or executable verification failed safely., StockfishSetupError, _download(), _extract_safely(), provision_stockfish(), Path, Download only when explicitly called, then safely and atomically install., _safe_member() (+2 more)

### Community 183 - "Community 183"
Cohesion: 0.40
Nodes (9): _basis(), _database(), _profile(), AnalysisProfile, Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen(), test_preflight_counts_projection_and_hash_memory_without_mutation() (+1 more)

### Community 184 - "Community 184"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 185 - "Community 185"
Cohesion: 0.22
Nodes (5): page(), successfulRequirements(), @playwright/test, constrainedWidths, desktopWidths

### Community 186 - "Community 186"
Cohesion: 0.20
Nodes (7): profile_for(), AnalysisQuality, One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile

### Community 187 - "Community 187"
Cohesion: 0.22
Nodes (3): FakeProcess, Board, Limit

### Community 188 - "Community 188"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 189 - "Community 189"
Cohesion: 0.28
Nodes (7): MatchKind, _build_recognition(), One immutable label reached at one encountered ply., Return the explicit route or transposition match kind., Return the ordered recognition timeline., RecognizedOpening, _select_current()

### Community 190 - "Community 190"
Cohesion: 0.28
Nodes (5): expectDescriptionAssociation(), expectStaticGraphic(), expectValidSurface(), RICH_SPOKEN_DESCRIPTION, STORY_IDS

### Community 191 - "Community 191"
Cohesion: 0.25
Nodes (4): expectApplicationAxeClean(), openStory(), STORY_IDS, storyUrl()

### Community 192 - "Community 192"
Cohesion: 0.29
Nodes (6): _convert_result(), AnalysisProfile, AnalysisResult, AnalysisTimeoutError, TimeoutError, A node-limited engine call exceeded its independent wall-clock watchdog.

### Community 193 - "Community 193"
Cohesion: 0.29
Nodes (7): APP_TEST_FILES, appWebServers, profile, selectedTestFiles(), serverProfile(), STORYBOOK_TEST_FILES, storybookWebServer

### Community 194 - "Community 194"
Cohesion: 0.38
Nodes (5): health(), get, HealthResponse, BaseModel, HealthResponse

### Community 195 - "Community 195"
Cohesion: 0.29
Nodes (6): engines, node, name, private, type, version

### Community 197 - "Community 197"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 198 - "Community 198"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 199 - "Community 199"
Cohesion: 0.29
Nodes (6): AnalysisResultInput, Construct one normalized result payload without database or chess checks., validate_analysis_result(), Path, _result(), test_public_publish_delegates_to_private_transaction_participant()

### Community 200 - "Community 200"
Cohesion: 0.33
Nodes (5): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis, _tool_analysis()

### Community 201 - "Community 201"
Cohesion: 0.40
Nodes (3): ManagedStockfish, One non-shareable engine instance intended to be owned by one future worker., test_process_checksum_identity_is_required()

### Community 202 - "Community 202"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 203 - "Community 203"
Cohesion: 0.50
Nodes (5): parse_month_selection(), Parse an exact zero-padded YYYY-MM calendar month selection., parametrize, test_month_selection_parses_only_exact_zero_padded_calendar_months(), test_month_selection_rejects_malformed_or_invalid_months()

### Community 206 - "Community 206"
Cohesion: 0.50
Nodes (3): elementProto, topLayerPseudoSelectors, @testing-library/jest-dom

### Community 207 - "Community 207"
Cohesion: 0.83
Nodes (3): execute(), globFiles(), resolveRg()

### Community 208 - "Community 208"
Cohesion: 0.83
Nodes (3): AnalysisQuality, AnalysisResultInput, _result()

## Knowledge Gaps
- **879 isolated node(s):** `Story`, `FeedbackVariant`, `FeedbackVariantTokens`, `Story`, `Story` (+874 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2579 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **125 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PositionKey` connect `Community 64` to `Community 43`, `Community 5`?**
  _High betweenness centrality (0.453) - this node is a cross-community bridge._
- **Why does `position_key_from_fen()` connect `Community 43` to `Community 64`, `Community 68`, `Community 5`, `Community 22`, `Community 23`?**
  _High betweenness centrality (0.451) - this node is a cross-community bridge._
- **Why does `react` connect `Community 45` to `Community 2`, `Community 10`, `Community 141`, `Community 13`, `Community 143`, `Community 16`, `Community 17`, `Community 147`, `Community 20`, `Community 21`, `Community 27`, `Community 28`, `Community 158`, `Community 31`, `Community 32`, `Community 164`, `Community 37`, `Community 168`, `Community 41`, `Community 42`, `Community 169`, `Community 46`, `Community 47`, `Community 51`, `Community 54`, `Community 55`, `Community 58`, `Community 188`, `Community 61`, `Community 65`, `Community 70`, `Community 73`, `Community 81`, `Community 88`, `Community 90`, `Community 91`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 93 inferred relationships involving `create_schema()` (e.g. with `create_benchmark_database()` and `create_cache_database()`) actually correct?**
  _`create_schema()` has 93 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Story`, `FeedbackVariant`, `FeedbackVariantTokens` to the rest of the system?**
  _879 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.03920529801324504 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.028840921458371124 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
