# Graph Report - ChessMoveTrainer  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 7302 nodes · 18554 edges · 338 communities (213 shown, 125 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 1259 edges (avg confidence: 0.88)
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
- Community 251
- Community 254
- Community 255
- Community 256
- Community 257
- Community 258
- Community 259
- Community 270
- Community 271
- Community 272
- Community 273
- Community 274
- Community 275
- Community 276
- Community 277
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
- Community 319
- Community 320
- Community 322
- Community 326
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
1. `create_schema()` - 110 edges
2. `react` - 85 edges
3. `vitest` - 78 edges
4. `@storybook/react-vite` - 58 edges
5. `@testing-library/react` - 49 edges
6. `PositionRepository` - 48 edges
7. `NormalizedPeriod` - 47 edges
8. `canonicalize_fen()` - 47 edges
9. `_assert_compatible_schema()` - 42 edges
10. `GameRepository` - 41 edges

## Surprising Connections (you probably didn't know these)
- `test_settings_accept_an_empty_or_arbitrary_json_object_without_required_keys()` --calls--> `validate_settings_object()`  [INFERRED]
  tests/database/analysis/test_models.py → src/chess_move_trainer/database/analysis/validation.py
- `get_position_training_requirements()` --calls--> `TrainingRequirementQuery`  [INFERRED]
  backend/app/features/position_training_requirements/router.py → src/chess_move_trainer/database/positions/training_requirements_models.py
- `_database()` --calls--> `GameRepository`  [INFERRED]
  backend/tests/features/games/test_api.py → src/chess_move_trainer/database/games/persistence_repository.py
- `test_correction_failure_at_each_boundary_preserves_prior_game()` --calls--> `GameRepository`  [INFERRED]
  tests/database/games/test_persistence.py → src/chess_move_trainer/database/games/persistence_repository.py
- `test_fresh_game_persists_exact_metadata_positions_and_occurrences()` --calls--> `GameRepository`  [INFERRED]
  tests/database/games/test_persistence.py → src/chess_move_trainer/database/games/persistence_repository.py

## Import Cycles
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`

## Communities (338 total, 125 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (90): frontend_src_api_client_getanalysis, frontend_src_api_client_requestanalysis, invalidatePositionInsight(), AnalysisClient, AnalysisFailure, AnalysisFailureCode, AnalysisLine, AnalysisObservation (+82 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (117): frontend_src_api_generated_index_analysisobservationerrorresponse, frontend_src_api_generated_index_analysisobservationlineresponse, frontend_src_api_generated_index_analysisobservationresponse, frontend_src_api_generated_index_analysisobservationresultresponse, frontend_src_api_generated_index_analysisrequestbody, frontend_src_api_generated_index_analysisrequesterrorresponse, frontend_src_api_generated_index_deletepreferredmoves, frontend_src_api_generated_index_deletepreferredmovesdata (+109 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (99): chess_move_trainer_database_positions, Exception, RuntimeError, activity_statistics(), _average(), _categories(), _category(), data_quality_statistics() (+91 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (91): CoverageState, GameSearchSort, GameSearchError, GameSearchSchemaError, GameSearchStorageError, GameSearchValidationError, Exception, RuntimeError (+83 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (69): frontend_src_api_client_getpositioninsight, frontend_src_api_client_positioninsightresponse, ChartLabel, here, rawStyles, failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen() (+61 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (75): Immutable engine-independent analysis values and input validation., AnalysisResultInput, A complete engine-independent result payload without position or terminal…, _analysis_state(), AnalysisObservation, AnalysisObservationError, AnalysisObservationRepository, AnalysisObservationRequest (+67 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (90): deletePreferredMoves(), putPreferredMoves(), requestAnalysis(), submitPositionTrainingAnswer(), AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse (+82 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (68): Color, _board_for_position(), _classify_terminal(), _fen_for_position(), _finite_timeout(), _is_expected_stockfish(), _line_from_info(), _metrics_for() (+60 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (72): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerPresentation, BoardAnswerStatus, BoardSquareHighlight (+64 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (63): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+55 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (60): AnalysisCandidate, _bounded_call(), _candidate(), close_process(), _convert_result(), _engine_shutdown_poll(), EngineIdentity, EngineProcess (+52 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (67): get_rebuilt_database_path(), Path, Return the explicit clean database path for the current application process., client(), _database(), fixture, MonkeyPatch, parametrize (+59 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (73): create(), inspect(), command, Path, Lifecycle and schema commands., Inspect any readable SQLite database and emit deterministic Markdown., Create the fixed direct database through the package lifecycle service., Refresh the fixed direct database's game data. (+65 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (66): _read_preference(), Public preferred-move schedule values, operations, and storage services., DateResolution, _intersects(), normalize_periods(), NormalizedPeriod, _overlay(), parse_date_literal() (+58 more)

### Community 14 - "Community 14"
Cohesion: 0.05
Nodes (63): frontend_src_api_client_getopenings, frontend_src_api_client_getopeningsdata, frontend_src_api_client_getpositiontrainingrequirementsdata, frontend_src_api_client_openingcatalogueitemresponse, frontend_src_api_client_openingcatalogueresponse, frontend_src_api_client_submitpositiontraininganswer, frontend_src_api_client_traininganswerresponse, frontend_src_api_client_trainingrequirementitemresponse (+55 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (58): createClient(), TODO: we probably want to return error and improve types, ReqInit, client, CreateClientConfig, BuildUrlFn, Client, ClientOptions (+50 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (52): api_context(), client(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path, TestClient (+44 more)

### Community 17 - "Community 17"
Cohesion: 0.06
Nodes (59): analysis_key(), _current_signature(), json_response(), opening_detail_key(), openings_catalogue_version(), openings_key(), position_insight_key(), preferred_moves_key() (+51 more)

### Community 18 - "Community 18"
Cohesion: 0.07
Nodes (56): collections_abc, random, _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path(), BaseException (+48 more)

### Community 19 - "Community 19"
Cohesion: 0.05
Nodes (54): ChessSide, Fen, parseUciMove(), Ply, San, UciMove, GameMainLineOccurrence, mapGameDetailResponse() (+46 more)

### Community 20 - "Community 20"
Cohesion: 0.06
Nodes (59): Path, Read one FEN observation from an explicit app database path., read_analysis_observation(), position_transaction(), PositionRepository, Path, Open one opaque package-owned transaction for grouped position work., Resolve canonical positions using package-owned connections and transactions. (+51 more)

### Community 21 - "Community 21"
Cohesion: 0.05
Nodes (48): EvalBar(), EvalBarProps, ExpectedDisplay, BoardRender(), PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, stripPackageSemantics(), { shouldThrow } (+40 more)

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (57): PublicationOutcome, Saved or expected not-saved result for the publication service., Build the successful publication outcome., Build an expected not-saved outcome with its explicit reason., _line(), _lines(), AnalysisLine, AnalysisQuality (+49 more)

### Community 23 - "Community 23"
Cohesion: 0.08
Nodes (52): frontend_src_api_client_gamedetailresponse, frontend_src_api_client_getgame, frontend_src_features_board_adapter_boardadapter_boardorientation, BranchMove, GameMainLineModel, GameDetailQueryError, queryGameDetail(), useGameDetailQuery() (+44 more)

### Community 24 - "Community 24"
Cohesion: 0.09
Nodes (56): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences() (+48 more)

### Community 25 - "Community 25"
Cohesion: 0.08
Nodes (48): _mutation_preference(), PreferredMovesMutationRequest, _preference_from_options(), Preference, The immutable value stored in a configured schedule period., _canonicalize_four_field_fen(), _load_schedule(), PreferredMoveError (+40 more)

### Community 26 - "Community 26"
Cohesion: 0.09
Nodes (53): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+45 more)

### Community 27 - "Community 27"
Cohesion: 0.06
Nodes (50): AnalysisError, AnalysisLine, AnalysisQuality, AnalysisScoreKind, AnalysisStorageError, AnalysisTerminalKind, AnalysisValidationError, _FrozenJsonObject (+42 more)

### Community 28 - "Community 28"
Cohesion: 0.06
Nodes (41): backend_app_features_analysis, AnalysisCandidate, AnalysisProfile, canonical_fen(), _canonical_json(), position_key_from_fen(), Return the internal identity without changing the public six-field FEN., Return a strict canonical six-field FEN or reject it. (+33 more)

### Community 29 - "Community 29"
Cohesion: 0.07
Nodes (44): AnalysisBusyError, A short coordinator SQLite transaction could not acquire its lock., AnalysisResult, AnalysisRepository, _begin_immediate(), FinalPositionFailure, _is_busy(), Connection (+36 more)

### Community 30 - "Community 30"
Cohesion: 0.09
Nodes (48): _position_sort_key(), PreferredMoveInferenceResult, CanonicalPosition, Return a read-only position-to-period view for downstream consumers., All configured position schedules produced by one pure inference run., Return the per-position schedules using the storage-facing name., _game_header(), _occurrence_from_row() (+40 more)

### Community 31 - "Community 31"
Cohesion: 0.05
Nodes (56): getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight(), getPositionTrainingRequirements() (+48 more)

### Community 32 - "Community 32"
Cohesion: 0.07
Nodes (38): catalogueDemoShell(), AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport, OPTIONS (+30 more)

### Community 33 - "Community 33"
Cohesion: 0.06
Nodes (42): MeasurementDecision, sqlalchemy, _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_decision(), _measurement_inputs(), _MeasurementInputs (+34 more)

### Community 34 - "Community 34"
Cohesion: 0.07
Nodes (44): _configured_float(), get_training_requirement_policy(), Application dependencies for database capabilities., Return the configured policy, or ``None`` when the capability is unavailable., api_context(), client(), _complete_analysis_result(), fixture (+36 more)

### Community 35 - "Community 35"
Cohesion: 0.08
Nodes (50): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+42 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (50): benchmark_client(), benchmark_database(), create_benchmark_database(), _database_info(), _float_env(), _int_env(), _output_dir(), fixture (+42 more)

### Community 37 - "Community 37"
Cohesion: 0.11
Nodes (49): ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisStatisticsResponse, CategoryPerformanceResponse, ContractModel, DataQualityStatisticsResponse, GameStatisticsResponse, HourActivityResponse (+41 more)

### Community 38 - "Community 38"
Cohesion: 0.06
Nodes (32): frontend_src_api_client_gethealthoptions, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps, frontend_src_features_app_shell_appshell_module, ConstrainedClosed (+24 more)

### Community 39 - "Community 39"
Cohesion: 0.10
Nodes (40): AnalysisStorageError, Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp() (+32 more)

### Community 40 - "Community 40"
Cohesion: 0.12
Nodes (45): _canonical_fen(), delete_preferred_move(), _parse_mutation_date(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalRequest, PreferredMoveRemovalResult, put_preferred_move() (+37 more)

### Community 41 - "Community 41"
Cohesion: 0.09
Nodes (45): frontend_src_api_client_deletepreferredmoves, frontend_src_api_client_getpreferredmoves, frontend_src_api_client_preferredmovesmutationresponse, frontend_src_api_client_preferredmovesremovalresponse, frontend_src_api_client_preferredmovesresponse, frontend_src_api_client_preferredmovessegmentresponse, frontend_src_api_client_putpreferredmoves, deletePreferredMove() (+37 more)

### Community 42 - "Community 42"
Cohesion: 0.08
Nodes (33): FEEDBACK_TOKENS, here, tokenCss, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, AFTER_NF3_FEN (+25 more)

### Community 43 - "Community 43"
Cohesion: 0.07
Nodes (38): invalidateAnalysisObservation(), invalidatePreferredMove(), invalidateTrainingRequirements(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput, OptionalText (+30 more)

### Community 44 - "Community 44"
Cohesion: 0.07
Nodes (37): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+29 more)

### Community 45 - "Community 45"
Cohesion: 0.07
Nodes (37): Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story (+29 more)

### Community 46 - "Community 46"
Cohesion: 0.10
Nodes (38): math, Validated canonical chess-position identity services., Raised when the requested answer date predates persisted credit., Raised when SQLite cannot acquire the bounded writer lock., TrainingAnswerLockError, TrainingAnswerStaleError, Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy (+30 more)

### Community 47 - "Community 47"
Cohesion: 0.10
Nodes (42): AcquisitionClock, Injectable UTC clock used to select the current archive month., _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum (+34 more)

### Community 48 - "Community 48"
Cohesion: 0.06
Nodes (26): asyncio, ManagedStockfish, One non-shareable engine instance intended to be owned by one future worker., _EventLoopTransportStub, FakeProcess, managed(), Board, Limit (+18 more)

### Community 49 - "Community 49"
Cohesion: 0.08
Nodes (30): ctypes, hashlib, _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database() (+22 more)

### Community 50 - "Community 50"
Cohesion: 0.07
Nodes (41): StoryAnalysisLifecycleEvent, LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate (+33 more)

### Community 51 - "Community 51"
Cohesion: 0.09
Nodes (34): createMoveHistoryRows(), KEY_NAVIGATION, frontend_src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow (+26 more)

### Community 52 - "Community 52"
Cohesion: 0.09
Nodes (37): OpeningCatalogueSort, _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError (+29 more)

### Community 53 - "Community 53"
Cohesion: 0.08
Nodes (34): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+26 more)

### Community 54 - "Community 54"
Cohesion: 0.12
Nodes (37): _eligible_evidence(), TrainerColor, Exception, RuntimeError, Base class for bounded training-requirement failures., One deterministic page of scored training requirements., Raised when a compatible database contains unusable training data., Raised when persisted training state is newer than the requested date. (+29 more)

### Community 55 - "Community 55"
Cohesion: 0.10
Nodes (30): BulkFailure, BulkRunner, _prepend(), Serial direct Tool analysis over the live on-demand target selection., Run the next eligible targets, or all eligible targets when unlimited., One isolated target failure retained only in the in-memory outcome., Analyze eligible targets one at a time and publish each result immediately., Stockfish process and database-lock services. (+22 more)

### Community 56 - "Community 56"
Cohesion: 0.07
Nodes (31): frontend_src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story, CatalogueLink (+23 more)

### Community 57 - "Community 57"
Cohesion: 0.10
Nodes (31): _canonical_fen(), _materialize_timeline(), PreferredMoveTimeline, PreferredMoveTimelineRepository, PreferredMoveTimelineRequest, Path, A complete exact-cover timeline for one finite request window., Return the strict timeline start date. (+23 more)

### Community 58 - "Community 58"
Cohesion: 0.07
Nodes (38): AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorCode, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse (+30 more)

### Community 59 - "Community 59"
Cohesion: 0.09
Nodes (38): game_detail_key(), games_key(), Canonical key from the validated games query and resolved database., Canonical key for one immutable game-detail read., GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse (+30 more)

### Community 60 - "Community 60"
Cohesion: 0.09
Nodes (30): AnalysisLockError, AnalysisSchemaError, AnalysisTimeoutError, RuntimeError, TimeoutError, A node-limited engine call exceeded its independent wall-clock watchdog., Another top-level analysis operator owns the database lock., The independently versioned analysis schema is absent or incompatible. (+22 more)

### Community 61 - "Community 61"
Cohesion: 0.10
Nodes (37): EvaluationQueueError, EvaluationValidationError, ValueError, An evaluation request violates strict validation or the bounded size limits., A queue state-machine transition is invalid for the current state., Browser-evaluation service boundary over the durable queue and analysis storage., EvaluationQueueItem, InspectResult (+29 more)

### Community 62 - "Community 62"
Cohesion: 0.13
Nodes (34): OpeningCatalogueErrorResponse, OpeningCatalogueItemResponse, OpeningCatalogueResponse, OpeningDetailErrorResponse, OpeningsModel, BaseModel, Strict HTTP models for the opening catalogue collection., Base model that rejects fields outside the catalogue contract. (+26 more)

### Community 63 - "Community 63"
Cohesion: 0.14
Nodes (35): collections, _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves() (+27 more)

### Community 64 - "Community 64"
Cohesion: 0.14
Nodes (34): LineLibrary(), nodeName(), sameIds(), selectionDescription(), LineLibraryTree(), LineLibraryTreeProps, nodeName(), Default (+26 more)

### Community 65 - "Community 65"
Cohesion: 0.12
Nodes (30): _discard_inflight(), get_or_compute(), _Inflight, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside…, A single-flight leader did not finish within the bounded wait., Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table. (+22 more)

### Community 66 - "Community 66"
Cohesion: 0.08
Nodes (31): httpx, acquire_incremental_months(), AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url(), ArchiveMonth, _current_month() (+23 more)

### Community 67 - "Community 67"
Cohesion: 0.09
Nodes (30): AnalysisEngine, _canonical(), _close_engine(), _drain(), dispatch(), _EngineRegistry, _evaluate_one(), inspect() (+22 more)

### Community 68 - "Community 68"
Cohesion: 0.11
Nodes (31): backend_app_features_evaluation, Path, Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), completed_at(), AnalysisProfile, AnalysisResult, result_for() (+23 more)

### Community 69 - "Community 69"
Cohesion: 0.13
Nodes (33): count_reader_calls(), Wrap one router-level reader so tests can count underlying invocations., MonkeyPatch, Path, TestClient, test_games_distinct_filters_use_distinct_keys(), test_games_equivalent_inputs_share_one_key(), test_games_error_responses_are_never_cached() (+25 more)

### Community 70 - "Community 70"
Cohesion: 0.08
Nodes (34): frontend_src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+26 more)

### Community 71 - "Community 71"
Cohesion: 0.11
Nodes (32): AcquireConfiguration, _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any (+24 more)

### Community 72 - "Community 72"
Cohesion: 0.09
Nodes (27): chess_move_trainer_database_statistics, RuntimeError, Raised when an existing database is not the exact supported schema., SchemaIncompatibleError, MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader (+19 more)

### Community 73 - "Community 73"
Cohesion: 0.10
Nodes (30): CanonicalPosition, Dependency-neutral immutable value for canonical position identity., The four-field immutable identity used by the app database., canonicalize_board(), canonicalize_fen(), PositionValidationError, Board, ValueError (+22 more)

### Community 74 - "Community 74"
Cohesion: 0.13
Nodes (31): _analysis_state(), Read analysis through the caller's already validated connection., _read_analysis_result(), _canonical_fen(), PositionInsight, PositionInsightAnalysis, PositionInsightError, PositionInsightPreference (+23 more)

### Community 75 - "Community 75"
Cohesion: 0.12
Nodes (35): _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text(), generate_catalogue(), _html_without_stale_commit_claim(), _known_ephemeral() (+27 more)

### Community 76 - "Community 76"
Cohesion: 0.14
Nodes (25): BenchmarkRunner, BenchmarkSpec, load_positions(), Any, Path, Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark() (+17 more)

### Community 77 - "Community 77"
Cohesion: 0.08
Nodes (26): frontend_src_api_client_getpositiontrainingrequirements, ContractOperation, dirname, ALLOWED_RUNTIME_CLIENT_IMPORTS, dirname, SOURCE_EXTENSIONS, srcDir, collectViewportReferences() (+18 more)

### Community 78 - "Community 78"
Cohesion: 0.12
Nodes (29): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+21 more)

### Community 79 - "Community 79"
Cohesion: 0.10
Nodes (28): LookupError, _clock_date(), _is_lock_failure(), BaseException, date, UtcCalendarDateClock, Clock and SQLite lock helpers for training-answer submission., _utc_today() (+20 more)

### Community 80 - "Community 80"
Cohesion: 0.10
Nodes (30): sqlalchemy_engine, Open one validated connection for an independent import run., _assert_compatible_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Connection, Path (+22 more)

### Community 81 - "Community 81"
Cohesion: 0.12
Nodes (28): itertools, NormalizationResult, NormalizationWarning, import_normalized_games(), import_raw_games(), import_raw_month(), import_raw_months(), load_normalized_months() (+20 more)

### Community 82 - "Community 82"
Cohesion: 0.15
Nodes (31): ArgumentParser, src_tools, build_steps(), classify_result(), _command_text(), _configure_output_streams(), _documented_storybook_teardown(), execute_step() (+23 more)

### Community 83 - "Community 83"
Cohesion: 0.12
Nodes (26): build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection, Path, Strictly read-only corpus-wide selection and resource projection., Inspect the corpus and analysis rows without opening a writer transaction. (+18 more)

### Community 84 - "Community 84"
Cohesion: 0.13
Nodes (30): chess_pgn, csv, io, _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception (+22 more)

### Community 85 - "Community 85"
Cohesion: 0.15
Nodes (30): MatchKind, _build_recognition(), lookup_fen(), OpeningRecognition, One immutable label reached at one encountered ply., Return the explicit route or transposition match kind., An immutable ordered recognition timeline and its selected current label., Return the ordered recognition timeline. (+22 more)

### Community 86 - "Community 86"
Cohesion: 0.18
Nodes (23): _database(), _FakeClock, _FakeEngine, _FakeMutex, Any, Path, _queue_row(), _runner() (+15 more)

### Community 87 - "Community 87"
Cohesion: 0.09
Nodes (21): PositionContextResponse, PositionReachFrequency(), PositionReachFrequencyProps, Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth (+13 more)

### Community 88 - "Community 88"
Cohesion: 0.13
Nodes (31): functools, _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached() (+23 more)

### Community 89 - "Community 89"
Cohesion: 0.08
Nodes (12): Queue, _FakeFactory, _FakeProcess, _FakeStdin, _FakeStdout, Any, test_engine_applies_fixed_options_clears_hash_and_returns_complete_pvs(), test_identity_failure_terminates_the_child() (+4 more)

### Community 90 - "Community 90"
Cohesion: 0.13
Nodes (18): _counts(), FixedClock, _game_fixture(), GameTransport, OpeningTransport, Any, datetime, MonkeyPatch (+10 more)

### Community 91 - "Community 91"
Cohesion: 0.11
Nodes (30): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+22 more)

### Community 92 - "Community 92"
Cohesion: 0.07
Nodes (23): HealthyContent, meta, Story, UnexpectedFailureTryAgain, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault (+15 more)

### Community 93 - "Community 93"
Cohesion: 0.13
Nodes (20): MonkeyPatch, Path, sys, _artifact_fixture(), _assert_relative_catalogue_path(), _graph_path_values(), _single_layer_catalogue(), test_allowlist_cleanup_removes_known_tree_but_refuses_unknown_content() (+12 more)

### Community 94 - "Community 94"
Cohesion: 0.15
Nodes (27): AccessMode, sqlalchemy_pool, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), _open_existing_connection(), probe_connection() (+19 more)

### Community 95 - "Community 95"
Cohesion: 0.08
Nodes (25): engines, node, name, private, type, version, elementProto, topLayerPseudoSelectors (+17 more)

### Community 96 - "Community 96"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 97 - "Community 97"
Cohesion: 0.09
Nodes (25): PreferredMoveClient, PreferredMoveMutationResult, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PREFERRED_MOVE_SOURCE_FEN, PreferredMoveRelationship (+17 more)

### Community 98 - "Community 98"
Cohesion: 0.14
Nodes (27): _atomic_replace(), load_month(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files. (+19 more)

### Community 99 - "Community 99"
Cohesion: 0.11
Nodes (18): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Atomic publication of normalized opening routes into the v1 catalogue tables., Raised when a compatible database cannot publish the opening catalogue. (+10 more)

### Community 100 - "Community 100"
Cohesion: 0.17
Nodes (23): _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult, Path, _result(), test_eligibility_stale_reuse_and_idempotent_resume() (+15 more)

### Community 101 - "Community 101"
Cohesion: 0.19
Nodes (28): OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryNode, booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys() (+20 more)

### Community 102 - "Community 102"
Cohesion: 0.30
Nodes (25): acquire_months(), Discover listed months and acquire every eligible raw month. With…, _archive_url(), _config(), FixedClock, _fixture(), _month_url(), AcquireConfiguration (+17 more)

### Community 103 - "Community 103"
Cohesion: 0.13
Nodes (22): MutexBusyError, A finite wait expired because another process owns the mutex., _analysis_result(), _finite_non_negative(), _finite_positive(), AnalysisResultInput, Any, CanonicalPosition (+14 more)

### Community 104 - "Community 104"
Cohesion: 0.07
Nodes (21): frontend_src_features_design_system_feedback_pagefeedback_module, AllSeverities, meta, Story, frontend_src_features_design_system_feedback_panelfeedback_module, AllSeverities, meta, Story (+13 more)

### Community 105 - "Community 105"
Cohesion: 0.11
Nodes (25): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+17 more)

### Community 106 - "Community 106"
Cohesion: 0.14
Nodes (26): Headers, _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), _normalize_game() (+18 more)

### Community 107 - "Community 107"
Cohesion: 0.21
Nodes (26): Validated read-only discovery controls., TrainingRequirementQuery, discover_training_requirements(), Path, Discover scored requirements from one explicit existing database., _add_black_training_item(), _fixture(), _game() (+18 more)

### Community 108 - "Community 108"
Cohesion: 0.17
Nodes (25): checkA11y(), DistributionLabelBox, expectActiveSessionHistoryEntry(), expectBothRelationshipBoxes(), expectDateFreePreferredPanel(), expectDistributionChartAndControlsClean(), expectNoHorizontalOverflow(), expectPanelMinimums() (+17 more)

### Community 109 - "Community 109"
Cohesion: 0.17
Nodes (24): Validate the v1 shape accepted by the one-time position-key transition., EvaluationLockError, EvaluationSchemaError, RuntimeError, Typed errors for the browser-evaluation service boundary., The evaluation worker session could not acquire the shared analysis lock., The independently versioned evaluation queue schema is absent or incompatible., _existing_tables() (+16 more)

### Community 110 - "Community 110"
Cohesion: 0.07
Nodes (23): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+15 more)

### Community 111 - "Community 111"
Cohesion: 0.14
Nodes (25): GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession() (+17 more)

### Community 112 - "Community 112"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 113 - "Community 113"
Cohesion: 0.21
Nodes (25): Path, TrainerColor, Read one position insight from an explicit database path., read_position_insight(), _database(), _game(), _install_analysis(), _install_opening() (+17 more)

### Community 114 - "Community 114"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 115 - "Community 115"
Cohesion: 0.11
Nodes (23): cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient(), storyCandidateAnalysisClient(), storySelectedPositionAnalysisClient(), GAME (+15 more)

### Community 116 - "Community 116"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 117 - "Community 117"
Cohesion: 0.20
Nodes (19): GameRepository, Persist complete normalized games without exposing database handles., _count(), _game_snapshot(), MonkeyPatch, Path, _raw(), test_batched_occurrence_writes_preserve_exact_rows() (+11 more)

### Community 118 - "Community 118"
Cohesion: 0.14
Nodes (20): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, api_context(), client(), create_statistics_database(), _insert_game(), _params(), Connection (+12 more)

### Community 119 - "Community 119"
Cohesion: 0.08
Nodes (23): STORY_PROMOTION_GAME_DETAIL, AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, FirstChoice, FirstChoiceFromEmpty, Matching, meta (+15 more)

### Community 120 - "Community 120"
Cohesion: 0.20
Nodes (22): AnalysisRequest, AnalysisRequestRepository, Path, Compose one desired-result request through an explicit database path., Request one desired analysis through an explicit app database path., One canonical public FEN and its fixed desired quality., request_analysis(), _database() (+14 more)

### Community 121 - "Community 121"
Cohesion: 0.14
Nodes (22): Path, Position insight helpers., _read_opening(), _read_queue_state(), _read_statistics_count(), _read_statistics_flag(), _validate_stored_move(), PositionInsightExperience (+14 more)

### Community 122 - "Community 122"
Cohesion: 0.16
Nodes (16): _database(), _FakeEngine, _FakeMutex, AnalysisResultInput, Path, PublicationOutcome, _RecordingPublisher, _runner() (+8 more)

### Community 123 - "Community 123"
Cohesion: 0.17
Nodes (22): chess, collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., DirectCapabilities, DirectPreflightError (+14 more)

### Community 124 - "Community 124"
Cohesion: 0.23
Nodes (22): chess_move_trainer_database_openings_keys, OpeningCatalogueQuery, OpeningCatalogueRepository, Path, Browse normalized openings without exposing a database connection., Read one exact public opening key from an explicit database path., The filters, ordering, and pagination controls for one catalogue read., read_opening() (+14 more)

### Community 125 - "Community 125"
Cohesion: 0.11
Nodes (16): clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), frontend_src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage(), RepertoireResponsiveStage() (+8 more)

### Community 126 - "Community 126"
Cohesion: 0.29
Nodes (22): claim_next(), enqueue(), observe(), pending_count(), Accept evaluation work with exact-FEN dedupe; never duplicates queued/running…, Claim the oldest queued item for a worker; FIFO by position, atomically., Read-only queue state for one exact FEN; never computes., Return (queued, running) counts for observability and drain control. (+14 more)

### Community 127 - "Community 127"
Cohesion: 0.16
Nodes (16): chess_move_trainer_database_preferred_moves, _period_values(), parametrize, Path, _run_serialized_delete_and_put(), delete_mutation(), first_target(), put_mutation() (+8 more)

### Community 128 - "Community 128"
Cohesion: 0.10
Nodes (15): Disclosure(), DisclosureProps, GameLoader(), handleSubmit(), GameLoaderFailureKind, GameLoaderProps, GameLoaderStatus, GameLoaderValues (+7 more)

### Community 129 - "Community 129"
Cohesion: 0.16
Nodes (19): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+11 more)

### Community 130 - "Community 130"
Cohesion: 0.13
Nodes (19): _LiveQueueRequest, RuntimeError, QueueCompletionOutcome, QueueError, QueueQualityError, QueueStorageError, Queue errors, claims, and live-request views., Result of one matching-token completion attempt. (+11 more)

### Community 131 - "Community 131"
Cohesion: 0.15
Nodes (17): contextlib, NormalizedGame, _game_metadata(), GamePersistenceError, _metadata_parameters(), PersistedGame, Any, PositionIdentity (+9 more)

### Community 132 - "Community 132"
Cohesion: 0.16
Nodes (20): dataclasses, NotSavedReason, sqlalchemy_exc, _load_current_result(), _load_position(), _not_saved_reason(), _prepare_publication(), _publish_in_transaction() (+12 more)

### Community 133 - "Community 133"
Cohesion: 0.26
Nodes (19): datetime, Judge and persist one answer in an existing compatible database., TrainingAnswerRepository, _balance(), _fixture(), _game(), _occurrence(), Connection (+11 more)

### Community 134 - "Community 134"
Cohesion: 0.09
Nodes (21): allowScripts, esbuild@0.25.12, esbuild@0.28.2, devDependencies, @axe-core/playwright, @playwright/mcp, @playwright/test, vite (+13 more)

### Community 135 - "Community 135"
Cohesion: 0.17
Nodes (19): createQuerySerializer(), ArraySeparatorStyle, ArrayStyle, MatrixStyle, ObjectSeparatorStyle, ObjectStyle, separatorArrayExplode(), separatorArrayNoExplode() (+11 more)

### Community 136 - "Community 136"
Cohesion: 0.14
Nodes (19): actionLabel(), formatDay(), formatRange(), frontend_src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction, PreferredMoveSchedulePeriod (+11 more)

### Community 137 - "Community 137"
Cohesion: 0.14
Nodes (17): AnalysisReadError, AnalysisReadRepository, AnalysisReadResult, _line_from_row(), _materialize_result(), AnalysisLine, Path, RuntimeError (+9 more)

### Community 138 - "Community 138"
Cohesion: 0.26
Nodes (8): _ArtifactPaths, BenchmarkPersistenceError, An artifact could not be persisted safely after bounded retries., BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 139 - "Community 139"
Cohesion: 0.21
Nodes (19): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse, PositionInsightObservedMoveTotalsResponse (+11 more)

### Community 140 - "Community 140"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 141 - "Community 141"
Cohesion: 0.14
Nodes (17): SYNTHETIC_OPENING_RESPONSE, filterKind(), OpeningLineLibraryFailure, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType, OpeningLineLibraryGroupNode, OpeningLineLibraryLineNode, OpeningLineLibraryNodeBase (+9 more)

### Community 142 - "Community 142"
Cohesion: 0.15
Nodes (10): @axe-core/playwright, checkA11y(), STORY_IDS, isAxeBusyError(), retryAxeWhenBusy(), waitForStorybookRender(), checkA11y(), assertFixtureStates() (+2 more)

### Community 143 - "Community 143"
Cohesion: 0.34
Nodes (18): Path, QueueService, Own the live queue lifecycle without holding SQLite during engine work., AnalysisQuality, Path, _queue_row(), _result(), _setup() (+10 more)

### Community 144 - "Community 144"
Cohesion: 0.25
Nodes (15): _catalogue_snapshot(), MonkeyPatch, Path, _rows(), _source_dir(), test_deletion_checkpoint_order_is_child_first(), test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(), test_first_publication_writes_labels_routes_and_contiguous_children() (+7 more)

### Community 145 - "Community 145"
Cohesion: 0.24
Nodes (15): copy, _count(), FixedClock, _fixture(), _game_url(), _month_url(), Any, datetime (+7 more)

### Community 146 - "Community 146"
Cohesion: 0.11
Nodes (17): BoardAdapter(), BoardAdapterProps, frontend_src_features_board_adapter_boardadapter_module, frontend_src_features_board_adapter_boardadapter_starting_fen, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition, ExpandedPositionDescription (+9 more)

### Community 147 - "Community 147"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 148 - "Community 148"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 149 - "Community 149"
Cohesion: 0.31
Nodes (18): ValidatedAnalysisResult, Validate terminal policy and complete legal candidate lines from a neutral root., validate_analysis_position(), _line(), _position(), AnalysisLine, AnalysisTerminalKind, parametrize (+10 more)

### Community 150 - "Community 150"
Cohesion: 0.22
Nodes (15): _position_id(), _post(), MonkeyPatch, parametrize, Path, _queue_row(), test_bad_values_give_clear_error(), test_finished_analysis_is_reused_and_ignores_unknown_fields() (+7 more)

### Community 151 - "Community 151"
Cohesion: 0.19
Nodes (14): _params(), MonkeyPatch, parametrize, Path, _target_position_id(), test_bad_values_give_clear_error(), test_injected_database_is_used_when_configured(), test_known_position_returns_full_insight_and_ignores_unknown_filters() (+6 more)

### Community 152 - "Community 152"
Cohesion: 0.18
Nodes (14): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+6 more)

### Community 153 - "Community 153"
Cohesion: 0.25
Nodes (16): normalize_game(), Return a fully validated game, or one ordinary warning for a skipped input., _fixture(), parametrize, test_draw_mapping_and_pgn_termination_fallback(), test_ineligible_malformed_and_illegal_inputs_are_ordinary_skips(), test_invalid_required_raw_fields_are_skipped(), test_non_unique_trainer_and_non_normal_start_are_skipped() (+8 more)

### Community 154 - "Community 154"
Cohesion: 0.14
Nodes (6): ast, Path, _python_sources(), test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin(), test_database_package_has_no_legacy_or_production_import_direction(), test_package_contains_no_runtime_wrapper_or_copied_legacy_generator()

### Community 155 - "Community 155"
Cohesion: 0.21
Nodes (16): DirEntry, _entry_kind(), Read a complete bundle without changing any of its files., _read_and_validate_bundle(), visit(), _assert_safe_path(), GraphifyError, _load_json() (+8 more)

### Community 156 - "Community 156"
Cohesion: 0.13
Nodes (14): booleanFilterData, data, LineLibraryCommitDescription, LineLibraryFilterKind, LineLibraryFilterOption, LineLibraryNodeKind, LineLibraryNodeSelectionDeclaration, LineLibraryRowContext (+6 more)

### Community 157 - "Community 157"
Cohesion: 0.24
Nodes (13): shutil, _catalogue_snapshot(), _copy_sources(), _fixture_game(), _game_snapshot(), _latest_files(), OpeningTransport, BaseException (+5 more)

### Community 158 - "Community 158"
Cohesion: 0.26
Nodes (13): _normalized(), MonkeyPatch, parametrize, Path, _raw(), _rows(), test_correction_failure_at_each_boundary_preserves_prior_game(), test_fresh_game_persists_exact_metadata_positions_and_occurrences() (+5 more)

### Community 159 - "Community 159"
Cohesion: 0.18
Nodes (9): _common_fens(), _database(), _FakeEngine, _FakeMutex, Path, test_initial_analysis_is_serial_resumable_direct_and_queue_free(), engine_factory(), mutex_factory() (+1 more)

### Community 160 - "Community 160"
Cohesion: 0.21
Nodes (15): _add_black_training_item(), _answer(), parametrize, Path, _query(), test_answer_is_backend_judged_and_returns_the_resulting_item(), test_answer_validation_returns_422_without_writing(), test_discovery_accepts_overridden_policy_and_paired_opening_filter() (+7 more)

### Community 161 - "Community 161"
Cohesion: 0.19
Nodes (11): decimal, _finite_number(), _normalize_range(), _parse_date(), date, ValueError, Validated models for read-only position training requirements., Raised when a policy or discovery request is invalid. (+3 more)

### Community 162 - "Community 162"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 163 - "Community 163"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 164 - "Community 164"
Cohesion: 0.21
Nodes (14): argparse, fnmatch, count_lines(), is_excluded(), is_test_file(), main(), print_report(), Path (+6 more)

### Community 165 - "Community 165"
Cohesion: 0.22
Nodes (11): CliRunner, PreferredMoveSetupResult, The fixed summary units produced by one setup operation., Exception, MonkeyPatch, parametrize, _runner(), test_preferred_moves_setup_forwards_fixed_path_without_reading_prompt() (+3 more)

### Community 166 - "Community 166"
Cohesion: 0.16
Nodes (11): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelIntent, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue, InlineWdl(), resultMetadataLabel() (+3 more)

### Community 167 - "Community 167"
Cohesion: 0.17
Nodes (12): AnalysisPanelDisplay, AnalysisPanelLine, AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides (+4 more)

### Community 168 - "Community 168"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 169 - "Community 169"
Cohesion: 0.16
Nodes (13): PreferredMovePanelProps, RepertoireSessionPanel(), RepertoireSessionPanelProps, FrequencyAbsent, FrequencyUnavailable, FrequencyZero, LocalLineSession, meta (+5 more)

### Community 170 - "Community 170"
Cohesion: 0.32
Nodes (13): _add_game_occurrences(), _add_route(), _database(), _position_ids(), AnalysisQuality, MonkeyPatch, parametrize, Path (+5 more)

### Community 171 - "Community 171"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 172 - "Community 172"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 173 - "Community 173"
Cohesion: 0.23
Nodes (7): ArtifactWriter, AtomicArtifactWriter, Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 174 - "Community 174"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 175 - "Community 175"
Cohesion: 0.15
Nodes (6): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver

### Community 176 - "Community 176"
Cohesion: 0.15
Nodes (9): boardLane, Boundary1039, Boundary1040, Boundary699, Boundary700, engineLane, meta, sessionLane (+1 more)

### Community 177 - "Community 177"
Cohesion: 0.15
Nodes (11): Return the current result value for callers using a result/read shape., _analysis_result(), BulkError, BulkInputError, AnalysisResultInput, Any, Path, RuntimeError (+3 more)

### Community 178 - "Community 178"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 179 - "Community 179"
Cohesion: 0.17
Nodes (11): Cancellation, ConstrainedDrawer, defaultArgs, ForcedColorsAndReducedMotion, KeyboardSelection, meta, NativeKeyboardPromotionInitiation, StaleAndIllegalRejection (+3 more)

### Community 180 - "Community 180"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 181 - "Community 181"
Cohesion: 0.20
Nodes (10): here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4, SELECTED_E4 (+2 more)

### Community 182 - "Community 182"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 183 - "Community 183"
Cohesion: 0.18
Nodes (6): fulfillJson(), mockCatalogue(), OPENING_ITEMS, TRAINING_ERROR, TRAINING_ITEM, TRAINING_RESPONSE_BASE

### Community 184 - "Community 184"
Cohesion: 0.24
Nodes (11): PositionInsightErrorResponse, _error(), get_position_insight(), Depends, get, get_rebuilt_database_path, JSONResponse, Path (+3 more)

### Community 185 - "Community 185"
Cohesion: 0.24
Nodes (7): filterOpeningCatalogue(), frontend_src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, OpeningSelection, searchText()

### Community 186 - "Community 186"
Cohesion: 0.18
Nodes (7): BulkOutcome, Observable result of one serial bulk launch., Return the later CLI-compatible status for this service outcome., Whether the launch completed without isolated failures or interruption., Observable result of one finite worker launch., Whether this finite launch completed without failures or interruption., WorkerOutcome

### Community 187 - "Community 187"
Cohesion: 0.38
Nodes (10): _child_process(), _open_keeper(), Any, Path, Popen, Open one extra handle so the named mutex survives its crashed owner., test_abandoned_child_acquisition_is_reported_as_acquired(), test_clean_release_allows_the_next_owner() (+2 more)

### Community 188 - "Community 188"
Cohesion: 0.20
Nodes (7): _item_response(), Return the resulting scored item using an explicit adapter-friendly name., One globally scored canonical-position/preferred-move pair., Return the compact adapter-ready shape with six-decimal derived numbers., _round_public(), TrainingRequirementItem, TrainingRequirementItemResponse

### Community 189 - "Community 189"
Cohesion: 0.40
Nodes (9): _basis(), _database(), _profile(), AnalysisProfile, Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen(), test_preflight_counts_projection_and_hash_memory_without_mutation() (+1 more)

### Community 190 - "Community 190"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 191 - "Community 191"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 192 - "Community 192"
Cohesion: 0.22
Nodes (5): page(), successfulRequirements(), @playwright/test, constrainedWidths, desktopWidths

### Community 193 - "Community 193"
Cohesion: 0.20
Nodes (7): profile_for(), AnalysisQuality, One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., Resolve one of the approved fixed profiles., StockfishProfile

### Community 194 - "Community 194"
Cohesion: 0.31
Nodes (8): chess_move_trainer_database_stockfish, _median(), print_direct_measurements(), Print only aggregate measurement facts and normalized plan details., _database(), Path, test_measurement_output_is_aggregate_only(), test_real_direct_database_records_query_plans_and_timings()

### Community 195 - "Community 195"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 196 - "Community 196"
Cohesion: 0.28
Nodes (5): expectDescriptionAssociation(), expectStaticGraphic(), expectValidSurface(), RICH_SPOKEN_DESCRIPTION, STORY_IDS

### Community 197 - "Community 197"
Cohesion: 0.25
Nodes (4): expectApplicationAxeClean(), openStory(), STORY_IDS, storyUrl()

### Community 198 - "Community 198"
Cohesion: 0.43
Nodes (7): chess_move_trainer_database_games_configuration, _assert_same_key_set(), _assert_same_mapping(), _database(), Path, test_real_direct_database_capabilities(), test_real_direct_database_matches_the_retained_source_ledger()

### Community 199 - "Community 199"
Cohesion: 0.29
Nodes (6): AnalysisResultInput, Construct one normalized result payload without database or chess checks., validate_analysis_result(), Path, _result(), test_public_publish_delegates_to_private_transaction_participant()

### Community 200 - "Community 200"
Cohesion: 0.29
Nodes (7): APP_TEST_FILES, appWebServers, profile, selectedTestFiles(), serverProfile(), STORYBOOK_TEST_FILES, storybookWebServer

### Community 201 - "Community 201"
Cohesion: 0.38
Nodes (5): health(), get, HealthResponse, BaseModel, HealthResponse

### Community 202 - "Community 202"
Cohesion: 0.29
Nodes (6): engines, node, name, private, type, version

### Community 203 - "Community 203"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 204 - "Community 204"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 205 - "Community 205"
Cohesion: 0.38
Nodes (4): PageNotFoundView(), Default, meta, Story

### Community 206 - "Community 206"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 207 - "Community 207"
Cohesion: 0.38
Nodes (6): re, _normalized_sql(), Connection, Path, test_canonical_resource_is_installed_and_schema_is_exact(), test_unique_constraints_are_exact_and_internal_autoindexes_only()

### Community 208 - "Community 208"
Cohesion: 0.29
Nodes (5): Board, CanonicalPosition, Return the canonical position consumed by the engine., Return the canonical identity represented by the fixed FEN., _record_route_position()

### Community 209 - "Community 209"
Cohesion: 0.60
Nodes (4): _assert_expected_operation_ids(), Focused proof for the served API contract., test_docs_and_served_openapi_remain_available(), test_served_schema_remains_full_with_only_clean_operationid_changes()

### Community 211 - "Community 211"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 213 - "Community 213"
Cohesion: 0.83
Nodes (3): execute(), globFiles(), resolveRg()

### Community 214 - "Community 214"
Cohesion: 0.83
Nodes (3): AnalysisQuality, AnalysisResultInput, _result()

## Knowledge Gaps
- **883 isolated node(s):** `AnalysisRequest`, `AnalysisScoreKind`, `AnalysisTerminalKind`, `JsonRecord`, `AnalysisPanelDisplayOptions` (+878 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2697 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **125 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PositionKey` connect `Community 28` to `Community 0`?**
  _High betweenness centrality (0.463) - this node is a cross-community bridge._
- **Why does `position_key_from_fen()` connect `Community 28` to `Community 67`, `Community 100`, `Community 29`, `Community 83`, `Community 60`, `Community 61`, `Community 126`?**
  _High betweenness centrality (0.461) - this node is a cross-community bridge._
- **Why does `react` connect `Community 38` to `Community 0`, `Community 128`, `Community 4`, `Community 8`, `Community 136`, `Community 14`, `Community 19`, `Community 21`, `Community 23`, `Community 152`, `Community 156`, `Community 32`, `Community 163`, `Community 167`, `Community 168`, `Community 42`, `Community 171`, `Community 44`, `Community 45`, `Community 43`, `Community 176`, `Community 50`, `Community 51`, `Community 56`, `Community 185`, `Community 64`, `Community 195`, `Community 70`, `Community 78`, `Community 87`, `Community 92`, `Community 95`, `Community 96`, `Community 97`, `Community 105`, `Community 115`, `Community 125`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Are the 93 inferred relationships involving `create_schema()` (e.g. with `create_benchmark_database()` and `create_cache_database()`) actually correct?**
  _`create_schema()` has 93 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AnalysisRequest`, `AnalysisScoreKind`, `AnalysisTerminalKind` to the rest of the system?**
  _883 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.03774391112377154 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.01694915254237288 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
