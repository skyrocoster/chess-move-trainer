# Graph Report - ChessMoveTrainer  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 6980 nodes · 17885 edges · 338 communities (213 shown, 125 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 1224 edges (avg confidence: 0.88)
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
- Community 204
- Community 205
- Community 206
- Community 207
- Community 208
- Community 209
- Community 210
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
- Community 227
- Community 228
- Community 229
- Community 230
- Community 231
- Community 232
- Community 234
- Community 235
- Community 237
- Community 238
- Community 239
- Community 240
- Community 241
- Community 242
- Community 243
- Community 244
- Community 245
- Community 246
- Community 247
- Community 248
- Community 249
- Community 250
- Community 253
- Community 254
- Community 255
- Community 256
- Community 257
- Community 258
- Community 268
- Community 269
- Community 270
- Community 271
- Community 272
- Community 273
- Community 274
- Community 275
- Community 276
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
- Community 313
- Community 314
- Community 315
- Community 316
- Community 317
- Community 318
- Community 319
- Community 321
- Community 322
- Community 324
- Community 327
- Community 328
- Community 329
- Community 330
- Community 331
- Community 332
- Community 333
- Community 334
- Community 335
- Community 336
- Community 337

## God Nodes (most connected - your core abstractions)
1. `create_schema()` - 108 edges
2. `react` - 84 edges
3. `vitest` - 78 edges
4. `@storybook/react-vite` - 58 edges
5. `@testing-library/react` - 49 edges
6. `NormalizedPeriod` - 47 edges
7. `canonicalize_fen()` - 47 edges
8. `PositionRepository` - 45 edges
9. `GameRepository` - 41 edges
10. `_assert_compatible_schema()` - 41 edges

## Surprising Connections (you probably didn't know these)
- `_fake_analysis()` --calls--> `SearchMetrics`  [INFERRED]
  tests/database/stockfish/test_benchmark.py → src/chess_move_trainer/database/stockfish/engine_models.py
- `test_corrupt_persisted_route_fails_as_operational_error()` --uses--> `OpeningRecognitionError`  [INFERRED]
  tests/database/openings/test_recognition.py → src/chess_move_trainer/database/openings/recognition.py
- `test_missing_and_incompatible_databases_are_operational_failures_with_schema_distinct()` --uses--> `OpeningRecognitionError`  [INFERRED]
  tests/database/openings/test_recognition.py → src/chess_move_trainer/database/openings/recognition.py
- `test_route_cache_reloads_after_database_change()` --uses--> `OpeningRecognitionError`  [INFERRED]
  tests/database/openings/test_recognition.py → src/chess_move_trainer/database/openings/recognition.py
- `put_preferred_moves()` --calls--> `PreferredMoveMutationRequest`  [INFERRED]
  backend/app/features/preferred_moves/router.py → src/chess_move_trainer/database/preferred_moves/mutations.py

## Import Cycles
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`

## Communities (338 total, 125 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (87): AnalysisBusyError, AnalysisLockError, AnalysisSchemaError, RuntimeError, Another top-level analysis operator owns the database lock., The independently versioned analysis schema is absent or incompatible., A short coordinator SQLite transaction could not acquire its lock., Persisted backend analysis contracts. (+79 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (77): frontend_src_api_client_positioninsightresponse, frontend_src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster (+69 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (93): chess_move_trainer_database_games_reading, CoverageState, GameSearchSort, re, GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError (+85 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (97): Options, submitPositionTrainingAnswer(), AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse (+89 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (83): EvaluationLockError, EvaluationQueueError, EvaluationSchemaError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary., An evaluation request violates strict validation or the bounded size limits. (+75 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (72): chess_move_trainer_database_stockfish, MeasurementDecision, _open_connection(), Yield one configured SQLAlchemy Core connection for package internals., collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts. (+64 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (70): itertools, NormalizationResult, NormalizationWarning, NormalizedGame, import_normalized_games(), import_raw_games(), import_raw_month(), import_raw_months() (+62 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (71): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerPresentation, BoardAnswerStatus, BoardSquareHighlight (+63 more)

### Community 8 - "Community 8"
Cohesion: 0.04
Nodes (57): App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps, frontend_src_features_app_shell_appshell_module, ConstrainedClosed, ConstrainedOpen (+49 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (73): analysis_key(), clear_caches(), _current_signature(), _discard_inflight(), games_key(), get_or_compute(), _Inflight, opening_detail_key() (+65 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (68): frontend_src_api_client_gamedetailresponse, frontend_src_api_client_getgame, frontend_src_features_board_adapter_boardadapter_boardorientation, Fen, Ply, San, GameLoader(), handleSubmit() (+60 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (67): get_rebuilt_database_path(), Path, Return the explicit clean database path for the current application process., client(), _database(), fixture, MonkeyPatch, parametrize (+59 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (66): AnalysisEngine, backend_app_features_analysis, backend_app_features_evaluation, _canonical(), _close_engine(), _drain(), dispatch(), _EngineRegistry (+58 more)

### Community 13 - "Community 13"
Cohesion: 0.04
Nodes (58): frontend_src_api_client_getpositioninsight, ChessSide, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord (+50 more)

### Community 14 - "Community 14"
Cohesion: 0.07
Nodes (67): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+59 more)

### Community 15 - "Community 15"
Cohesion: 0.07
Nodes (61): _mutation_preference(), PreferredMovesMutationRequest, _preference_from_options(), Public preferred-move schedule values, operations, and storage services., PreferredMoveMutationResult, PreferredMoveRemovalResult, The removed interval and complete configured schedule after DELETE., The applied interval and complete configured schedule after one PUT. (+53 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (43): dirname, pythonPath, repoRoot, { shouldThrow }, FEEDBACK_TOKENS, here, tokenCss, here (+35 more)

### Community 17 - "Community 17"
Cohesion: 0.05
Nodes (50): frontend_src_api_client_gethealthoptions, invalidateAnalysisObservation(), invalidatePositionInsight(), invalidatePreferredMove(), invalidateTrainingRequirements(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey() (+42 more)

### Community 18 - "Community 18"
Cohesion: 0.05
Nodes (57): EvalBar(), EvalBarDisplayState, EvalBarProps, ExpectedDisplay, BoardAdapter(), BoardAdapterProps, BoardRender(), frontend_src_features_board_adapter_boardadapter_module (+49 more)

### Community 19 - "Community 19"
Cohesion: 0.08
Nodes (62): AnalysisCandidate, canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, _connect_read_only(), _database_guard(), _exact_fen_count() (+54 more)

### Community 20 - "Community 20"
Cohesion: 0.07
Nodes (62): sqlalchemy_engine, _validate_lock_timeout(), Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection() (+54 more)

### Community 21 - "Community 21"
Cohesion: 0.07
Nodes (51): api_context(), client(), count_reader_calls(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path (+43 more)

### Community 22 - "Community 22"
Cohesion: 0.07
Nodes (45): Managed, per-owner Stockfish process and result-conversion boundary., chess, chess_move_trainer_database_stockfish_configuration, collections_abc, contextlib, dataclasses, pathlib, sqlalchemy (+37 more)

### Community 23 - "Community 23"
Cohesion: 0.06
Nodes (44): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+36 more)

### Community 24 - "Community 24"
Cohesion: 0.07
Nodes (45): chess_move_trainer_database_schema, position_transaction(), PositionRepository, Path, Open one opaque package-owned transaction for grouped position work., Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction. (+37 more)

### Community 25 - "Community 25"
Cohesion: 0.06
Nodes (45): AnalysisCandidate, position_key_from_fen(), Return the internal identity without changing the public six-field FEN., Return the internal four-field identity for a valid canonical six-field FEN., _existing_tables(), initialize_analysis_schema(), migrate_position_key_schema(), Connection (+37 more)

### Community 26 - "Community 26"
Cohesion: 0.07
Nodes (51): game_detail_key(), json_response(), position_insight_key(), Serialize one response model exactly like Starlette's JSONResponse., Canonical key for one immutable game-detail read., Canonical key for one validated position insight., Wrap one cached or freshly computed payload in a fresh response., serialize_response_body() (+43 more)

### Community 27 - "Community 27"
Cohesion: 0.06
Nodes (45): _configured_float(), get_training_requirement_policy(), Application dependencies for database capabilities., Return the configured policy, or ``None`` when the capability is unavailable., api_context(), client(), create_training_database(), _game() (+37 more)

### Community 28 - "Community 28"
Cohesion: 0.08
Nodes (44): LookupError, Validated canonical chess-position identity services., _clock_date(), _is_lock_failure(), BaseException, date, UtcCalendarDateClock, Clock and SQLite lock helpers for training-answer submission. (+36 more)

### Community 29 - "Community 29"
Cohesion: 0.08
Nodes (50): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+42 more)

### Community 30 - "Community 30"
Cohesion: 0.08
Nodes (41): close_process(), _engine_shutdown_poll(), EngineIdentity, _identity(), inspect_stockfish_executable(), Path, PythonChessProcess, Bounded, idempotent graceful quit with a tracked-process-only fallback. (+33 more)

### Community 31 - "Community 31"
Cohesion: 0.09
Nodes (50): DirEntry, _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), _entry_kind(), generate_catalogue() (+42 more)

### Community 32 - "Community 32"
Cohesion: 0.14
Nodes (49): benchmark_client(), benchmark_database(), create_benchmark_database(), _database_info(), _float_env(), _int_env(), _output_dir(), fixture (+41 more)

### Community 33 - "Community 33"
Cohesion: 0.06
Nodes (49): client, CreateClientConfig, getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings() (+41 more)

### Community 34 - "Community 34"
Cohesion: 0.10
Nodes (40): AnalysisStorageError, Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp() (+32 more)

### Community 35 - "Community 35"
Cohesion: 0.08
Nodes (45): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+37 more)

### Community 36 - "Community 36"
Cohesion: 0.12
Nodes (41): PublicationOutcome, Saved or expected not-saved result for the publication service., Build the successful publication outcome., Build an expected not-saved outcome with its explicit reason., _line(), _lines(), AnalysisLine, AnalysisQuality (+33 more)

### Community 37 - "Community 37"
Cohesion: 0.11
Nodes (42): _analysis_state(), Path, Position insight helpers., Read analysis through the caller's already validated connection., _read_analysis_result(), _read_opening(), _read_preference(), _read_queue_state() (+34 more)

### Community 38 - "Community 38"
Cohesion: 0.10
Nodes (34): AnalysisClient, AnalysisFailureCode, AnalysisObservation, AnalysisOperationResult, defaultAnalysisClient, frontend_src_features_analysis_analysisapi_positionkeyfromfen, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey() (+26 more)

### Community 39 - "Community 39"
Cohesion: 0.07
Nodes (40): AnalysisError, AnalysisLine, AnalysisResultInput, AnalysisStorageError, AnalysisValidationError, _FrozenJsonObject, Any, Exception (+32 more)

### Community 40 - "Community 40"
Cohesion: 0.10
Nodes (45): frontend_src_api_client_deletepreferredmoves, frontend_src_api_client_getpreferredmoves, frontend_src_api_client_preferredmovesmutationresponse, frontend_src_api_client_preferredmovesremovalresponse, frontend_src_api_client_preferredmovesresponse, frontend_src_api_client_preferredmovessegmentresponse, frontend_src_api_client_putpreferredmoves, defaultPreferredMoveClient (+37 more)

### Community 41 - "Community 41"
Cohesion: 0.09
Nodes (42): Headers, _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), normalize_game() (+34 more)

### Community 42 - "Community 42"
Cohesion: 0.06
Nodes (27): asyncio, ManagedStockfish, One non-shareable engine instance intended to be owned by one future worker., _EventLoopTransportStub, FakeProcess, managed(), Board, Limit (+19 more)

### Community 43 - "Community 43"
Cohesion: 0.09
Nodes (37): _canonicalize_four_field_fen(), _load_schedule(), PreferredMoveError, PreferredMoveLockError, PreferredMoveRepository, PreferredMoveSchemaError, PreferredMoveStorageError, CanonicalPosition (+29 more)

### Community 44 - "Community 44"
Cohesion: 0.09
Nodes (34): createMoveHistoryRows(), KEY_NAVIGATION, frontend_src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow (+26 more)

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (37): OpeningCatalogueSort, _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError (+29 more)

### Community 46 - "Community 46"
Cohesion: 0.08
Nodes (34): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+26 more)

### Community 47 - "Community 47"
Cohesion: 0.07
Nodes (40): LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate, expectActiveSessionHistoryEntry() (+32 more)

### Community 48 - "Community 48"
Cohesion: 0.08
Nodes (33): json, random, _bounded_message(), _normalized_directory(), BaseException, Atomic artifact persistence for benchmarks., _sha256_file(), load_positions() (+25 more)

### Community 49 - "Community 49"
Cohesion: 0.09
Nodes (34): Immutable engine-independent analysis values and input validation., _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest, AnalysisObservationResult, AnalysisObservationSchemaError (+26 more)

### Community 50 - "Community 50"
Cohesion: 0.07
Nodes (31): frontend_src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story, CatalogueLink (+23 more)

### Community 51 - "Community 51"
Cohesion: 0.09
Nodes (32): _position_sort_key(), PreferredMoveInferenceResult, CanonicalPosition, Return a read-only position-to-period view for downstream consumers., All configured position schedules produced by one pure inference run., Return the per-position schedules using the storage-facing name., _game_header(), _occurrence_from_row() (+24 more)

### Community 52 - "Community 52"
Cohesion: 0.16
Nodes (27): _fake_files(), FakeTransport, _file_urls(), _parent_snapshot(), BaseException, MonkeyPatch, parametrize, Path (+19 more)

### Community 53 - "Community 53"
Cohesion: 0.07
Nodes (38): AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse (+30 more)

### Community 54 - "Community 54"
Cohesion: 0.08
Nodes (33): httpx, acquire_incremental_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url(), ArchiveMonth (+25 more)

### Community 55 - "Community 55"
Cohesion: 0.13
Nodes (34): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract. (+26 more)

### Community 56 - "Community 56"
Cohesion: 0.14
Nodes (35): collections, _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves() (+27 more)

### Community 57 - "Community 57"
Cohesion: 0.14
Nodes (34): LineLibrary(), nodeName(), sameIds(), selectionDescription(), LineLibraryTree(), LineLibraryTreeProps, nodeName(), Default (+26 more)

### Community 58 - "Community 58"
Cohesion: 0.06
Nodes (33): PositionPickerMoveRecord, EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading (+25 more)

### Community 59 - "Community 59"
Cohesion: 0.08
Nodes (34): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story (+26 more)

### Community 60 - "Community 60"
Cohesion: 0.06
Nodes (26): HealthyContent, meta, Story, UnexpectedFailureTryAgain, PageNotFoundView(), Default, meta, Story (+18 more)

### Community 61 - "Community 61"
Cohesion: 0.11
Nodes (32): math, Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, _coerce_date(), effective_training_balance(), _finite_float(), _finite_result(), game_balance() (+24 more)

### Community 62 - "Community 62"
Cohesion: 0.12
Nodes (30): _materialize_timeline(), PreferredMoveTimeline, PreferredMoveTimelineRepository, PreferredMoveTimelineRequest, Path, A complete exact-cover timeline for one finite request window., Return the strict timeline start date., Return the strict timeline end date. (+22 more)

### Community 63 - "Community 63"
Cohesion: 0.09
Nodes (22): Path, Verify one explicit executable and terminate it cleanly., verify_stockfish_identity(), The process did not complete the finite UCI startup handshake., The Stockfish child process stopped or could not accept a command., The verified identity reported by the UCI startup handshake., StockfishIdentity, StockfishProcessError (+14 more)

### Community 64 - "Community 64"
Cohesion: 0.10
Nodes (32): frontend_src_api_client_getanalysis, frontend_src_api_client_requestanalysis, requestAnalysis(), AnalysisFailure, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse() (+24 more)

### Community 65 - "Community 65"
Cohesion: 0.09
Nodes (31): frontend_src_api_client_getopenings, frontend_src_api_client_getopeningsdata, frontend_src_api_client_getpositiontrainingrequirements, frontend_src_api_client_getpositiontrainingrequirementsdata, frontend_src_api_client_openingcatalogueresponse, abortError(), buildTrainingRequirementsQuery(), currentUtcDate() (+23 more)

### Community 66 - "Community 66"
Cohesion: 0.08
Nodes (34): frontend_src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+26 more)

### Community 67 - "Community 67"
Cohesion: 0.11
Nodes (32): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+24 more)

### Community 68 - "Community 68"
Cohesion: 0.19
Nodes (34): delete_preferred_move(), PreferredMoveRemovalRequest, put_preferred_move(), Path, Atomically apply one ordinary preferred-move mutation value., Atomically remove one ordinary preferred-move interval value., One complete parent FEN and one configured half-open interval to remove., _database() (+26 more)

### Community 69 - "Community 69"
Cohesion: 0.09
Nodes (27): chess_move_trainer_database_statistics, RuntimeError, Raised when an existing database is not the exact supported schema., SchemaIncompatibleError, MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader (+19 more)

### Community 70 - "Community 70"
Cohesion: 0.11
Nodes (31): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+23 more)

### Community 71 - "Community 71"
Cohesion: 0.10
Nodes (30): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), canonicalize_fen(), PositionValidationError, Board, ValueError (+22 more)

### Community 72 - "Community 72"
Cohesion: 0.08
Nodes (19): health(), get, HealthResponse, BaseModel, create_app(), MonkeyPatch, parametrize, Path (+11 more)

### Community 73 - "Community 73"
Cohesion: 0.11
Nodes (29): api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path, TestClient, Extend the shared position-insight fixture to a complete five-line result. (+21 more)

### Community 74 - "Community 74"
Cohesion: 0.15
Nodes (31): ArgumentParser, src_tools, build_steps(), classify_result(), _command_text(), _configure_output_streams(), _documented_storybook_teardown(), execute_step() (+23 more)

### Community 75 - "Community 75"
Cohesion: 0.12
Nodes (28): api_context(), client(), create_insight_database(), _game(), _install_analysis(), _install_opening(), _install_preferences(), _occurrence() (+20 more)

### Community 76 - "Community 76"
Cohesion: 0.13
Nodes (30): chess_pgn, csv, io, _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception (+22 more)

### Community 77 - "Community 77"
Cohesion: 0.13
Nodes (27): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+19 more)

### Community 78 - "Community 78"
Cohesion: 0.09
Nodes (27): AnalysisQuality, AnalysisScoreKind, AnalysisTerminalKind, NotSavedReason, Enum, str, The two approved analysis quality levels., The two approved score representations. (+19 more)

### Community 79 - "Community 79"
Cohesion: 0.18
Nodes (23): _database(), _FakeClock, _FakeEngine, _FakeMutex, Any, Path, _queue_row(), _runner() (+15 more)

### Community 80 - "Community 80"
Cohesion: 0.08
Nodes (12): Queue, _FakeFactory, _FakeProcess, _FakeStdin, _FakeStdout, Any, test_engine_applies_fixed_options_clears_hash_and_returns_complete_pvs(), test_identity_failure_terminates_the_child() (+4 more)

### Community 81 - "Community 81"
Cohesion: 0.14
Nodes (21): normalize_and_validate(), Normalize provenance, validate paths, and enforce the five-file contract., _artifact_fixture(), _assert_relative_catalogue_path(), _graph_path_values(), MonkeyPatch, Path, _single_layer_catalogue() (+13 more)

### Community 82 - "Community 82"
Cohesion: 0.13
Nodes (18): _counts(), FixedClock, _game_fixture(), GameTransport, OpeningTransport, Any, datetime, MonkeyPatch (+10 more)

### Community 83 - "Community 83"
Cohesion: 0.12
Nodes (21): AnalysisLine, AnalysisResult, analysisPanelDisplay(), AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv() (+13 more)

### Community 84 - "Community 84"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 85 - "Community 85"
Cohesion: 0.11
Nodes (26): contextFailureMessage(), failureMessage(), frontend_src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), PreferredMovePanelProps, statusLabel() (+18 more)

### Community 86 - "Community 86"
Cohesion: 0.11
Nodes (20): BulkRunner, Any, Path, Analyze eligible targets one at a time and publish each result immediately., BulkTarget, BulkTargetSelector, InitialAnalysisTargetSelector, Path (+12 more)

### Community 87 - "Community 87"
Cohesion: 0.17
Nodes (23): _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult, Path, _result(), test_eligibility_stale_reuse_and_idempotent_resume() (+15 more)

### Community 88 - "Community 88"
Cohesion: 0.18
Nodes (19): BenchmarkRunner, BenchmarkSpec, _fake_analysis(), _FakeEngine, _FakeFactory, _InjectedWriter, Any, Path (+11 more)

### Community 89 - "Community 89"
Cohesion: 0.10
Nodes (19): decimal, _finite_number(), _normalize_range(), _parse_date(), date, ValueError, Validated models for read-only position training requirements., Return the compact adapter-ready shape with six-decimal derived numbers. (+11 more)

### Community 90 - "Community 90"
Cohesion: 0.12
Nodes (25): storyAnalysisClient(), GAME, GAME_UUID, Game, PROMOTION_GAME, PreferredMoveMutationResult, DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR, DEFAULT_MOVE (+17 more)

### Community 91 - "Community 91"
Cohesion: 0.19
Nodes (28): OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryNode, booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys() (+20 more)

### Community 92 - "Community 92"
Cohesion: 0.30
Nodes (25): acquire_months(), Discover listed months and acquire every eligible raw month. With…, _archive_url(), _config(), FixedClock, _fixture(), _month_url(), AcquireConfiguration (+17 more)

### Community 93 - "Community 93"
Cohesion: 0.17
Nodes (28): lookup_fen(), OpeningInputError, OpeningRecognition, _parse_pgn_input(), Game, ValueError, Raised when a FEN or PGN query is not an accepted standard-chess input., An immutable ordered recognition timeline and its selected current label. (+20 more)

### Community 94 - "Community 94"
Cohesion: 0.18
Nodes (25): _eligible_evidence(), TrainerColor, Raised when a compatible database contains unusable training data., TrainingRequirementStorageError, validate_uci(), _active_preference(), _current_scoped_groups(), _EvidenceGroup (+17 more)

### Community 95 - "Community 95"
Cohesion: 0.14
Nodes (26): _assert_compatible_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Connection, Path, Transactional creation, compatibility, and explicit schema upgrades., Upgrade one existing exact v1 database to v2, or leave exact v2 unchanged. (+18 more)

### Community 96 - "Community 96"
Cohesion: 0.17
Nodes (25): _normalized_file_path(), _StoredAttempts, BenchmarkCompatibilityError, BenchmarkJob, StockfishProfile, Existing output state does not belong to the requested benchmark., A stable identity for one position/profile/round analysis., _checkpoint_payload() (+17 more)

### Community 97 - "Community 97"
Cohesion: 0.17
Nodes (26): checkA11y(), DistributionLabelBox, expectActiveSessionHistoryEntry(), expectBothRelationshipBoxes(), expectDateFreePreferredPanel(), expectDistributionChartAndControlsClean(), expectNoHorizontalOverflow(), expectPanelMinimums() (+18 more)

### Community 98 - "Community 98"
Cohesion: 0.08
Nodes (24): engines, node, name, private, type, version, eslint, @eslint/js (+16 more)

### Community 99 - "Community 99"
Cohesion: 0.11
Nodes (17): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Raised when a compatible database cannot publish the opening catalogue., Immutable counts describing one successfully committed catalogue replacement. (+9 more)

### Community 100 - "Community 100"
Cohesion: 0.13
Nodes (24): _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _is_expected_stockfish(), _line_from_info(), _metrics_for(), AnalysisLine (+16 more)

### Community 101 - "Community 101"
Cohesion: 0.17
Nodes (26): functools, _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached() (+18 more)

### Community 102 - "Community 102"
Cohesion: 0.10
Nodes (18): _canonical_fen(), _parse_mutation_date(), PreferredMoveMutationRequest, CanonicalPosition, date, One complete parent FEN and one configured half-open interval., PreferredMoveValidationError, ValueError (+10 more)

### Community 103 - "Community 103"
Cohesion: 0.14
Nodes (23): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_existing_connection(), probe_connection(), Connection, Path (+15 more)

### Community 104 - "Community 104"
Cohesion: 0.15
Nodes (24): Canonical key from the validated query, resolved database, and policy., training_requirements_key(), HTTP contracts for position training requirements., _answer_response(), _error(), get_position_training_requirements(), _item_response(), _page_response() (+16 more)

### Community 105 - "Community 105"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 106 - "Community 106"
Cohesion: 0.11
Nodes (20): frontend_src_api_client_trainingrequirementitemresponse, defaultTrainerPracticeApi, OpeningCatalogueSnapshotResult, queryOpeningCatalogueSnapshot(), queryOpeningChoices(), queryTrainingRequirements(), TrainerPracticeFilters, TrainerPracticeQueryError (+12 more)

### Community 107 - "Community 107"
Cohesion: 0.15
Nodes (23): buildUrl(), createQuerySerializer(), defaultHeaders, defaultQuerySerializer, ErrInterceptor, ReqInterceptor, ResInterceptor, ArraySeparatorStyle (+15 more)

### Community 108 - "Community 108"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 109 - "Community 109"
Cohesion: 0.15
Nodes (24): GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession() (+16 more)

### Community 110 - "Community 110"
Cohesion: 0.08
Nodes (20): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkFailure, BulkInputError, BulkOutcome, _prepend(), AnalysisResultInput (+12 more)

### Community 111 - "Community 111"
Cohesion: 0.24
Nodes (25): Validated read-only discovery controls., TrainingRequirementQuery, discover_training_requirements(), Discover scored requirements from one explicit existing database., _add_black_training_item(), _fixture(), _game(), _item() (+17 more)

### Community 112 - "Community 112"
Cohesion: 0.08
Nodes (20): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent (+12 more)

### Community 113 - "Community 113"
Cohesion: 0.23
Nodes (24): TrainerColor, Read one position insight from an explicit database path., read_position_insight(), _database(), _game(), _install_analysis(), _install_opening(), _install_preference() (+16 more)

### Community 114 - "Community 114"
Cohesion: 0.23
Nodes (22): chess_move_trainer_database_openings_keys, OpeningCatalogueQuery, OpeningCatalogueRepository, Path, Browse normalized openings without exposing a database connection., Read one exact public opening key from an explicit database path., The filters, ordering, and pagination controls for one catalogue read., read_opening() (+14 more)

### Community 115 - "Community 115"
Cohesion: 0.11
Nodes (16): PageContentBoundaryProps, Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES (+8 more)

### Community 116 - "Community 116"
Cohesion: 0.09
Nodes (22): AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, FirstChoice, FirstChoiceFromEmpty, Matching, meta, PendingRemove (+14 more)

### Community 117 - "Community 117"
Cohesion: 0.12
Nodes (20): AnalysisRequest, AnalysisRequestError, AnalysisRequestResult, AnalysisRequestStorageError, AnalysisRequestValidationError, _canonicalize_request_fen(), AnalysisError, AnalysisQuality (+12 more)

### Community 118 - "Community 118"
Cohesion: 0.17
Nodes (22): merge_current_month(), publish_month(), Any, RuntimeError, Raised when a raw month cannot be validated or published safely., Return games when candidate passes the exact object/list/unique-UUID gate., Merge a valid current response over a valid local month by game UUID., Validate fully, then publish through a flushed same-directory temporary file. (+14 more)

### Community 119 - "Community 119"
Cohesion: 0.16
Nodes (16): chess_move_trainer_database_preferred_moves, _period_values(), parametrize, Path, _run_serialized_delete_and_put(), delete_mutation(), first_target(), put_mutation() (+8 more)

### Community 120 - "Community 120"
Cohesion: 0.11
Nodes (16): frontend_src_api_client_openingcatalogueitemresponse, frontend_src_api_client_trainingrequirementresponse, Combobox(), filterOpeningCatalogue(), frontend_src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps (+8 more)

### Community 121 - "Community 121"
Cohesion: 0.22
Nodes (20): AnalysisRequestRepository, Path, Compose one desired-result request through an explicit database path., Request one desired analysis through an explicit app database path., request_analysis(), _database(), _position_with_result(), AnalysisQuality (+12 more)

### Community 122 - "Community 122"
Cohesion: 0.22
Nodes (10): _ArtifactPaths, _is_transient_artifact_error(), OSError, BenchmarkPersistenceError, An artifact could not be persisted safely after bounded retries., BenchmarkRunner, Any, BaseException (+2 more)

### Community 123 - "Community 123"
Cohesion: 0.13
Nodes (19): _LiveQueueRequest, RuntimeError, QueueCompletionOutcome, QueueError, QueueQualityError, QueueStorageError, Queue errors, claims, and live-request views., Result of one matching-token completion attempt. (+11 more)

### Community 124 - "Community 124"
Cohesion: 0.18
Nodes (15): _database(), _FakeEngine, _FakeMutex, AnalysisResultInput, Path, PublicationOutcome, _RecordingPublisher, _runner() (+7 more)

### Community 125 - "Community 125"
Cohesion: 0.14
Nodes (17): ctypes, hashlib, Stockfish process and database-lock services., DatabaseMutexError, _lock_file_for_database(), mutex_name_for_database(), MutexUnavailableError, normalize_database_path() (+9 more)

### Community 126 - "Community 126"
Cohesion: 0.26
Nodes (19): datetime, Judge and persist one answer in an existing compatible database., TrainingAnswerRepository, _balance(), _fixture(), _game(), _occurrence(), Connection (+11 more)

### Community 127 - "Community 127"
Cohesion: 0.16
Nodes (19): BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys, Options (+11 more)

### Community 128 - "Community 128"
Cohesion: 0.17
Nodes (18): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+10 more)

### Community 129 - "Community 129"
Cohesion: 0.13
Nodes (13): _close_handle(), DatabaseMutex, _finite_wait(), Any, OSError, Release ownership and close the kernel handle whenever possible., Best-effort close, releasing ownership first when necessary., Acquire and release one database-specific Stockfish mutex. Windows keeps the… (+5 more)

### Community 130 - "Community 130"
Cohesion: 0.11
Nodes (12): _bounded_call(), _convert_result(), EngineProcess, AnalysisProfile, AnalysisResult, Board, Protocol, Only the process operations the managed boundary is allowed to use. (+4 more)

### Community 131 - "Community 131"
Cohesion: 0.20
Nodes (20): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+12 more)

### Community 132 - "Community 132"
Cohesion: 0.14
Nodes (19): actionLabel(), formatDay(), formatRange(), frontend_src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction, PreferredMoveSchedulePeriod (+11 more)

### Community 133 - "Community 133"
Cohesion: 0.14
Nodes (18): AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), StoryAnalysisLifecycleEvent, storyCandidateAnalysisClient() (+10 more)

### Community 134 - "Community 134"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 135 - "Community 135"
Cohesion: 0.14
Nodes (17): SYNTHETIC_OPENING_RESPONSE, filterKind(), OpeningLineLibraryFailure, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType, OpeningLineLibraryGroupNode, OpeningLineLibraryLineNode, OpeningLineLibraryNodeBase (+9 more)

### Community 136 - "Community 136"
Cohesion: 0.19
Nodes (18): NotSavedReason, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction(), AnalysisResultInput, CanonicalPosition (+10 more)

### Community 137 - "Community 137"
Cohesion: 0.16
Nodes (9): @playwright/test, checkA11y(), STORY_IDS, isAxeBusyError(), retryAxeWhenBusy(), waitForStorybookRender(), assertFixtureStates(), checkA11y() (+1 more)

### Community 138 - "Community 138"
Cohesion: 0.39
Nodes (18): PreferredMoveSetupService, Infer and atomically initialize an empty preferred-move schedule., _count_periods(), _database(), _game(), _position(), Connection, Path (+10 more)

### Community 139 - "Community 139"
Cohesion: 0.34
Nodes (18): Path, QueueService, Own the live queue lifecycle without holding SQLite during engine work., AnalysisQuality, Path, _queue_row(), _result(), _setup() (+10 more)

### Community 140 - "Community 140"
Cohesion: 0.25
Nodes (15): _catalogue_snapshot(), MonkeyPatch, Path, _rows(), _source_dir(), test_deletion_checkpoint_order_is_child_first(), test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(), test_first_publication_writes_labels_routes_and_contiguous_children() (+7 more)

### Community 141 - "Community 141"
Cohesion: 0.24
Nodes (15): copy, _count(), FixedClock, _fixture(), _game_url(), _month_url(), Any, datetime (+7 more)

### Community 142 - "Community 142"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 143 - "Community 143"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 144 - "Community 144"
Cohesion: 0.31
Nodes (18): ValidatedAnalysisResult, Validate terminal policy and complete legal candidate lines from a neutral root., validate_analysis_position(), _line(), _position(), AnalysisLine, AnalysisTerminalKind, parametrize (+10 more)

### Community 145 - "Community 145"
Cohesion: 0.22
Nodes (18): Validate and freeze one JSON object without requiring any setting keys., validate_settings_object(), _line(), AnalysisLine, parametrize, _result(), test_configuration_version_must_be_an_integer_at_least_one(), test_depth_must_be_a_nonnegative_integer() (+10 more)

### Community 146 - "Community 146"
Cohesion: 0.18
Nodes (14): CliRunner, Exception, MonkeyPatch, parametrize, _runner(), test_preferred_moves_setup_forwards_fixed_path_without_reading_prompt(), test_preferred_moves_setup_help_registers_exact_command_without_options(), test_preferred_moves_setup_maps_failures_to_stderr_status() (+6 more)

### Community 147 - "Community 147"
Cohesion: 0.18
Nodes (14): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+6 more)

### Community 148 - "Community 148"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 149 - "Community 149"
Cohesion: 0.16
Nodes (14): clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart(), renderLabel() (+6 more)

### Community 150 - "Community 150"
Cohesion: 0.12
Nodes (10): page(), successfulRequirements(), checkA11y(), expectDescriptionAssociation(), expectStaticGraphic(), expectValidSurface(), RICH_SPOKEN_DESCRIPTION, STORY_IDS (+2 more)

### Community 151 - "Community 151"
Cohesion: 0.14
Nodes (6): ast, Path, _python_sources(), test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin(), test_database_package_has_no_legacy_or_production_import_direction(), test_package_contains_no_runtime_wrapper_or_copied_legacy_generator()

### Community 152 - "Community 152"
Cohesion: 0.14
Nodes (13): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelDisplay, AnalysisPanelIntent, AnalysisPanelLine, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue (+5 more)

### Community 153 - "Community 153"
Cohesion: 0.12
Nodes (14): BoardControl(), BoardControlProps, Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar (+6 more)

### Community 154 - "Community 154"
Cohesion: 0.13
Nodes (14): booleanFilterData, data, LineLibraryCommitDescription, LineLibraryFilterKind, LineLibraryFilterOption, LineLibraryNodeKind, LineLibraryNodeSelectionDeclaration, LineLibraryRowContext (+6 more)

### Community 155 - "Community 155"
Cohesion: 0.12
Nodes (16): allowScripts, esbuild@0.25.12, esbuild@0.28.2, engines, node, vite, vitest, name (+8 more)

### Community 156 - "Community 156"
Cohesion: 0.24
Nodes (13): shutil, _catalogue_snapshot(), _copy_sources(), _fixture_game(), _game_snapshot(), _latest_files(), OpeningTransport, BaseException (+5 more)

### Community 157 - "Community 157"
Cohesion: 0.18
Nodes (14): _analysis_result(), _finite_non_negative(), _finite_positive(), AnalysisResultInput, CanonicalPosition, datetime, Path, RuntimeError (+6 more)

### Community 158 - "Community 158"
Cohesion: 0.26
Nodes (13): _normalized(), MonkeyPatch, parametrize, Path, _raw(), _rows(), test_correction_failure_at_each_boundary_preserves_prior_game(), test_fresh_game_persists_exact_metadata_positions_and_occurrences() (+5 more)

### Community 159 - "Community 159"
Cohesion: 0.18
Nodes (9): _common_fens(), _database(), _FakeEngine, _FakeMutex, Path, test_initial_analysis_is_serial_resumable_direct_and_queue_free(), engine_factory(), mutex_factory() (+1 more)

### Community 160 - "Community 160"
Cohesion: 0.25
Nodes (14): Color, Stockfish returned malformed or incomplete UCI analysis data., StockfishProtocolError, normalize_score(), normalize_wdl(), _parse_int(), parse_uci_info(), AnalysisScoreKind (+6 more)

### Community 161 - "Community 161"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 162 - "Community 162"
Cohesion: 0.17
Nodes (13): sanFromFenAndUci(), SelectedTransition, PreferredMoveValue, colorLabel(), deriveRepertoirePositionModel(), PositionSaveability, PreferredMoveComparison, RepertoirePositionRelationship (+5 more)

### Community 163 - "Community 163"
Cohesion: 0.22
Nodes (12): collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue(), sourceRoot, statusTagByRoot (+4 more)

### Community 164 - "Community 164"
Cohesion: 0.29
Nodes (14): Path, Read one FEN observation from an explicit app database path., read_analysis_observation(), _database(), parametrize, Path, _queue(), _result() (+6 more)

### Community 165 - "Community 165"
Cohesion: 0.21
Nodes (14): argparse, fnmatch, count_lines(), is_excluded(), is_test_file(), main(), print_report(), Path (+6 more)

### Community 166 - "Community 166"
Cohesion: 0.22
Nodes (14): createClient(), TODO: we probably want to return error and improve types, ReqInit, checkForExistence(), createConfig(), createInterceptors(), getParseAs(), headersEntries() (+6 more)

### Community 167 - "Community 167"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 168 - "Community 168"
Cohesion: 0.15
Nodes (12): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+4 more)

### Community 169 - "Community 169"
Cohesion: 0.19
Nodes (12): clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), frontend_src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage(), RepertoireResponsiveStage() (+4 more)

### Community 170 - "Community 170"
Cohesion: 0.15
Nodes (13): _canonical_fen(), PositionInsightError, PositionInsightSchemaError, PositionInsightValidationError, CanonicalPosition, Exception, RuntimeError, ValueError (+5 more)

### Community 171 - "Community 171"
Cohesion: 0.21
Nodes (8): ArtifactWriter, AtomicArtifactWriter, _is_within(), Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 172 - "Community 172"
Cohesion: 0.24
Nodes (9): MutexBusyError, A finite wait expired because another process owns the mutex., Whether the successful acquisition recovered an abandoned owner., Any, Drain current queued/reclaimable work and then exit., One isolated request failure retained only in the launch outcome., Drain queued requests with one sequential engine process at a time., WorkerFailure (+1 more)

### Community 173 - "Community 173"
Cohesion: 0.32
Nodes (13): _add_game_occurrences(), _add_route(), _database(), _position_ids(), AnalysisQuality, MonkeyPatch, parametrize, Path (+5 more)

### Community 174 - "Community 174"
Cohesion: 0.15
Nodes (10): ALLOWED_RUNTIME_CLIENT_IMPORTS, dirname, SOURCE_EXTENSIONS, srcDir, dirname, ref_node_fs, ref_node_path, ref_node_url (+2 more)

### Community 175 - "Community 175"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 176 - "Community 176"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 177 - "Community 177"
Cohesion: 0.24
Nodes (12): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+4 more)

### Community 178 - "Community 178"
Cohesion: 0.24
Nodes (11): Auth, AuthToken, BodySerializer, QuerySerializer, QuerySerializerOptions, Client, ClientMeta, Config (+3 more)

### Community 179 - "Community 179"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 180 - "Community 180"
Cohesion: 0.21
Nodes (10): AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay(), missingDisplay() (+2 more)

### Community 181 - "Community 181"
Cohesion: 0.15
Nodes (9): boardLane, Boundary1039, Boundary1040, Boundary699, Boundary700, engineLane, meta, sessionLane (+1 more)

### Community 182 - "Community 182"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 183 - "Community 183"
Cohesion: 0.20
Nodes (5): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisEngine, _close_engine(), _EngineRegistry, Protocol

### Community 184 - "Community 184"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 185 - "Community 185"
Cohesion: 0.18
Nodes (8): profile_for(), AnalysisQuality, The fixed Stockfish profiles supported by the first database worker., One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile

### Community 186 - "Community 186"
Cohesion: 0.18
Nodes (6): fulfillJson(), mockCatalogue(), OPENING_ITEMS, TRAINING_ERROR, TRAINING_ITEM, TRAINING_RESPONSE_BASE

### Community 187 - "Community 187"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 188 - "Community 188"
Cohesion: 0.38
Nodes (10): _child_process(), _open_keeper(), Any, Path, Popen, Open one extra handle so the named mutex survives its crashed owner., test_abandoned_child_acquisition_is_reported_as_acquired(), test_clean_release_allows_the_next_owner() (+2 more)

### Community 189 - "Community 189"
Cohesion: 0.40
Nodes (9): _basis(), _database(), _profile(), AnalysisProfile, Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen(), test_preflight_counts_projection_and_hash_memory_without_mutation() (+1 more)

### Community 190 - "Community 190"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 191 - "Community 191"
Cohesion: 0.22
Nodes (6): formDataBodySerializer, jsonBodySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArrayStyle, ObjectStyle

### Community 192 - "Community 192"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 193 - "Community 193"
Cohesion: 0.22
Nodes (4): fixture(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 194 - "Community 194"
Cohesion: 0.28
Nodes (7): MatchKind, _build_recognition(), One immutable label reached at one encountered ply., Return the explicit route or transposition match kind., Return the ordered recognition timeline., RecognizedOpening, _select_current()

### Community 195 - "Community 195"
Cohesion: 0.22
Nodes (7): InitialTechnicalPosition, Board, CanonicalPosition, Return the canonical position consumed by the engine., One stable technical representative in the initial-analysis preset., Return the canonical identity represented by the fixed FEN., _record_route_position()

### Community 196 - "Community 196"
Cohesion: 0.25
Nodes (4): expectApplicationAxeClean(), openStory(), STORY_IDS, storyUrl()

### Community 197 - "Community 197"
Cohesion: 0.43
Nodes (7): chess_move_trainer_database_games_configuration, _assert_same_key_set(), _assert_same_mapping(), _database(), Path, test_real_direct_database_capabilities(), test_real_direct_database_matches_the_retained_source_ledger()

### Community 198 - "Community 198"
Cohesion: 0.29
Nodes (5): BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 199 - "Community 199"
Cohesion: 0.29
Nodes (6): AnalysisResultInput, Construct one normalized result payload without database or chess checks., validate_analysis_result(), Path, _result(), test_public_publish_delegates_to_private_transaction_participant()

### Community 200 - "Community 200"
Cohesion: 0.36
Nodes (7): subprocess, sys, CompletedProcess, Path, _run(), _smoke_arguments(), test_one_position_real_benchmark_is_contained_and_completed_run_is_noop()

### Community 201 - "Community 201"
Cohesion: 0.29
Nodes (7): APP_TEST_FILES, appWebServers, profile, selectedTestFiles(), serverProfile(), STORYBOOK_TEST_FILES, storybookWebServer

### Community 202 - "Community 202"
Cohesion: 0.29
Nodes (6): engines, node, name, private, type, version

### Community 204 - "Community 204"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 205 - "Community 205"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 206 - "Community 206"
Cohesion: 0.33
Nodes (5): AnalysisLine, Expose candidate lines without requiring callers to unwrap the result., A normalized result ready for the engine-independent publisher., StockfishAnalysis, _tool_analysis()

### Community 208 - "Community 208"
Cohesion: 0.33
Nodes (6): devDependencies, @axe-core/playwright, @playwright/mcp, @playwright/test, vite, vitest

### Community 209 - "Community 209"
Cohesion: 0.33
Nodes (6): RuntimeError, TimeoutError, Base class for bounded Stockfish process or protocol failures., The per-analysis watchdog expired before Stockfish returned bestmove., StockfishError, StockfishWatchdogError

### Community 210 - "Community 210"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 212 - "Community 212"
Cohesion: 0.50
Nodes (3): elementProto, topLayerPseudoSelectors, @testing-library/jest-dom

### Community 213 - "Community 213"
Cohesion: 0.83
Nodes (3): execute(), globFiles(), resolveRg()

### Community 214 - "Community 214"
Cohesion: 0.83
Nodes (3): AnalysisQuality, AnalysisResultInput, _result()

### Community 219 - "Community 219"
Cohesion: 0.67
Nodes (3): Enum, Every possible result of resolving a schedule date., ResolutionState

## Knowledge Gaps
- **880 isolated node(s):** `MoveResponseDistributionControlsProps`, `Story`, `Story`, `ChartLabel`, `JsonRecord` (+875 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2545 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **125 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PositionKey` connect `Community 25` to `Community 0`, `Community 64`?**
  _High betweenness centrality (0.427) - this node is a cross-community bridge._
- **Why does `position_key_from_fen()` connect `Community 25` to `Community 0`, `Community 4`, `Community 12`, `Community 87`?**
  _High betweenness centrality (0.425) - this node is a cross-community bridge._
- **Why does `react` connect `Community 8` to `Community 1`, `Community 132`, `Community 133`, `Community 7`, `Community 10`, `Community 13`, `Community 16`, `Community 17`, `Community 18`, `Community 147`, `Community 149`, `Community 23`, `Community 154`, `Community 38`, `Community 167`, `Community 169`, `Community 44`, `Community 175`, `Community 47`, `Community 50`, `Community 180`, `Community 181`, `Community 57`, `Community 59`, `Community 60`, `Community 192`, `Community 66`, `Community 198`, `Community 77`, `Community 84`, `Community 85`, `Community 90`, `Community 98`, `Community 106`, `Community 112`, `Community 115`, `Community 120`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 91 inferred relationships involving `create_schema()` (e.g. with `create_benchmark_database()` and `create_cache_database()`) actually correct?**
  _`create_schema()` has 91 INFERRED edges - model-reasoned connections that need verification._
- **What connects `MoveResponseDistributionControlsProps`, `Story`, `Story` to the rest of the system?**
  _880 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.046713822575891545 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.03482840638803941 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
