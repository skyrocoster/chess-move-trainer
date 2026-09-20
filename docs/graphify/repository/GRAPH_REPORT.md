# Graph Report - ChessMoveTrainer  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 6868 nodes · 17794 edges · 286 communities (213 shown, 73 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 1156 edges (avg confidence: 0.89)
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
- Community 211
- Community 213
- Community 214
- Community 215
- Community 217
- Community 218
- Community 219
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
- Community 258
- Community 259
- Community 260
- Community 261
- Community 262
- Community 263
- Community 264
- Community 265
- Community 266
- Community 267
- Community 268
- Community 269
- Community 270
- Community 271
- Community 272
- Community 273
- Community 274
- Community 278
- Community 280
- Community 281
- Community 282
- Community 283
- Community 284
- Community 285

## God Nodes (most connected - your core abstractions)
1. `create_schema()` - 115 edges
2. `react` - 83 edges
3. `vitest` - 77 edges
4. `SchemaIncompatibleError` - 73 edges
5. `_assert_compatible_schema()` - 71 edges
6. `canonicalize_fen()` - 65 edges
7. `@storybook/react-vite` - 57 edges
8. `CanonicalPosition` - 49 edges
9. `@testing-library/react` - 49 edges
10. `AnalysisQuality` - 47 edges

## Surprising Connections (you probably didn't know these)
- `_result()` --calls--> `AnalysisLine`  [INFERRED]
  tests/database/analysis/test_observation.py → src/chess_move_trainer/database/analysis/models.py
- `_result()` --calls--> `AnalysisLine`  [INFERRED]
  tests/database/analysis/test_transaction_composition.py → src/chess_move_trainer/database/analysis/models.py
- `_result()` --calls--> `AnalysisLine`  [INFERRED]
  tests/database/stockfish/test_queue.py → src/chess_move_trainer/database/analysis/models.py
- `get_analysis()` --calls--> `AnalysisObservationRequest`  [INFERRED]
  backend/app/features/analysis_observation/router.py → src/chess_move_trainer/database/analysis/observation.py
- `test_invalid_observation_fens_are_rejected_before_storage_access()` --calls--> `AnalysisObservationRequest`  [INFERRED]
  tests/database/analysis/test_observation.py → src/chess_move_trainer/database/analysis/observation.py

## Import Cycles
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/openings/recognition.py`

## Communities (286 total, 73 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (103): frontend_src_api_client_gamedetailresponse, frontend_src_api_client_getgame, RepertoireBuilderWorkspace, frontend_src_features_board_adapter_boardadapter_boardorientation, isPromotionTarget(), Ply, San, strictFen() (+95 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (106): Immutable engine-independent analysis values and input validation., AnalysisError, AnalysisLine, AnalysisQuality, AnalysisScoreKind, AnalysisStorageError, AnalysisTerminalKind, Enum (+98 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (93): AnalysisTerminalKind, chess, collections_abc, Color, dataclasses, os, Queue, re (+85 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (100): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preferred_period_json(), BaseException, Exception, Shared CLI rendering and error helpers. (+92 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (100): AnalysisOperationResult, AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient() (+92 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (99): Options, requestAnalysis(), submitPositionTrainingAnswer(), AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody (+91 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (70): frontend_src_api_client_positioninsightresponse, ChessSide, frontend_src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, AvailableWithoutTail, AvailableWithTail, ConstrainedWidth (+62 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (83): position_key_from_fen(), Return the internal four-field identity for a valid canonical six-field FEN., EvaluationLockError, EvaluationQueueError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary. (+75 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (74): _preference_from_options(), PreferredMoveMutationResult, PreferredMoveRemovalResult, Package-owned preferred-move mutation values and operation., The removed interval and complete configured schedule after DELETE., The applied interval and complete configured schedule after one PUT., DateResolution, _intersects() (+66 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (75): CoverageState, DeepestOpening, _GameData, GameSearchPage, GameSearchSort, GameSummary, GameSearchError, GameSearchSchemaError (+67 more)

### Community 10 - "Community 10"
Cohesion: 0.04
Nodes (51): frontend_src_api_client_gethealthoptions, App(), AppShell(), AppShellProps, frontend_src_features_app_shell_appshell_module, ConstrainedClosed, ConstrainedOpen, Healthy (+43 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (69): DirEntry, shutil, _assert_safe_path(), _atomic_write_batch(), build_graphify_command(), _canonical_graph(), _capture_prior_derived_artifacts(), _command_text() (+61 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (70): Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), _pragma_rows(), Connection (+62 more)

### Community 13 - "Community 13"
Cohesion: 0.04
Nodes (57): frontend_src_api_client_getpositioninsight, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord, narrowInsightResponse() (+49 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (58): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+50 more)

### Community 15 - "Community 15"
Cohesion: 0.06
Nodes (54): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisBusyError, AnalysisLockError, EngineLifecycleError, RuntimeError, A tracked engine process could not be started or stopped safely., Another top-level analysis operator owns the database lock., A short coordinator SQLite transaction could not acquire its lock. (+46 more)

### Community 16 - "Community 16"
Cohesion: 0.08
Nodes (59): Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp(), _oldest_claimable() (+51 more)

### Community 17 - "Community 17"
Cohesion: 0.05
Nodes (54): frontend_src_api_client_getanalysis, frontend_src_api_client_requestanalysis, AnalysisFailure, AnalysisLine, AnalysisObservation, AnalysisRequest, AnalysisResult, AnalysisScoreKind (+46 more)

### Community 18 - "Community 18"
Cohesion: 0.05
Nodes (44): { shouldThrow }, BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers, PromotionPiece, FEEDBACK_TOKENS (+36 more)

### Community 19 - "Community 19"
Cohesion: 0.06
Nodes (54): _finite_number(), _normalize_range(), _parse_date(), date, Exception, RuntimeError, ValueError, Validated models for read-only position training requirements. (+46 more)

### Community 20 - "Community 20"
Cohesion: 0.08
Nodes (61): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences() (+53 more)

### Community 21 - "Community 21"
Cohesion: 0.06
Nodes (47): _bounded_call(), close_process(), _engine_shutdown_poll(), EngineIdentity, EngineProcess, _identity(), inspect_stockfish_executable(), Board (+39 more)

### Community 22 - "Community 22"
Cohesion: 0.07
Nodes (46): invalidateAnalysisObservation(), invalidatePositionInsight(), invalidatePreferredMove(), invalidateTrainingRequirements(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput (+38 more)

### Community 23 - "Community 23"
Cohesion: 0.05
Nodes (46): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResult, AnalysisRequestErrorCode, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse (+38 more)

### Community 24 - "Community 24"
Cohesion: 0.07
Nodes (57): frontend_src_api_client_deletepreferredmoves, frontend_src_api_client_getpreferredmoves, frontend_src_api_client_preferredmovesmutationresponse, frontend_src_api_client_preferredmovesremovalresponse, frontend_src_api_client_preferredmovesresponse, frontend_src_api_client_preferredmovessegmentresponse, frontend_src_api_client_putpreferredmoves, Fen (+49 more)

### Community 25 - "Community 25"
Cohesion: 0.07
Nodes (46): position_transaction(), Open one opaque package-owned transaction for grouped position work., _analysis_result(), BulkError, BulkFailure, BulkOutcome, _prepend(), RuntimeError (+38 more)

### Community 26 - "Community 26"
Cohesion: 0.06
Nodes (55): analysis_key(), _current_signature(), game_detail_key(), json_response(), opening_detail_key(), openings_catalogue_version(), openings_key(), position_insight_key() (+47 more)

### Community 27 - "Community 27"
Cohesion: 0.09
Nodes (51): OpeningCatalogueSort, _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError (+43 more)

### Community 28 - "Community 28"
Cohesion: 0.06
Nodes (38): AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport, OPTIONS, RADIO_OPTIONS (+30 more)

### Community 29 - "Community 29"
Cohesion: 0.06
Nodes (47): AnalysisSchemaError, The independently versioned analysis schema is absent or incompatible., AnalysisCandidate, canonical_fen(), Return a strict canonical six-field FEN or reject it., _existing_tables(), initialize_analysis_schema(), migrate_position_key_schema() (+39 more)

### Community 30 - "Community 30"
Cohesion: 0.07
Nodes (44): MeasurementDecision, _open_connection(), Yield one configured SQLAlchemy Core connection for package internals., _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_decision(), _measurement_inputs() (+36 more)

### Community 31 - "Community 31"
Cohesion: 0.07
Nodes (34): Public preferred-move schedule values, operations, and storage services., _canonical_fen(), _parse_mutation_date(), date, parse_date_literal(), PreferenceState, Parse exactly one literal ``YYYY-MM-DD`` calendar date., A state that can be stored for a configured period. (+26 more)

### Community 32 - "Community 32"
Cohesion: 0.10
Nodes (45): PreferredMoveInferenceResult, Return a read-only position-to-period view for downstream consumers., All configured position schedules produced by one pure inference run., PreferredMoveError, Exception, Base error for bounded preferred-move failures., _game_header(), _occurrence_from_row() (+37 more)

### Community 33 - "Community 33"
Cohesion: 0.13
Nodes (50): benchmark_client(), benchmark_database(), create_benchmark_database(), _database_info(), _float_env(), _int_env(), _output_dir(), fixture (+42 more)

### Community 34 - "Community 34"
Cohesion: 0.07
Nodes (44): MonkeyPatch, Path, TestClient, test_repeated_analysis_reads_share_cached_payloads(), test_repeated_insight_reads_share_cached_payloads(), test_repeated_preferred_move_and_game_detail_reads_share_cached_payloads(), _assert_expected_operation_ids(), Focused proof for the served API contract. (+36 more)

### Community 35 - "Community 35"
Cohesion: 0.09
Nodes (34): AnalysisProfile, _canonical_json(), ResultEligibility, build_preflight(), CorpusPreflight, load_projection_basis(), ProjectionBasis, Connection (+26 more)

### Community 36 - "Community 36"
Cohesion: 0.08
Nodes (40): BaseException, LookupError, Validated canonical chess-position identity services., _canonical_fen(), _clock_date(), _is_lock_failure(), _load_current_aggregate(), CanonicalPosition (+32 more)

### Community 37 - "Community 37"
Cohesion: 0.06
Nodes (36): chess_move_trainer_database, chess_move_trainer_database_preferred_moves_repository, chess_move_trainer_database_preferred_moves_setup, chess_move_trainer_database_stockfish, CliRunner, Exception, json, pathlib (+28 more)

### Community 38 - "Community 38"
Cohesion: 0.07
Nodes (37): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+29 more)

### Community 39 - "Community 39"
Cohesion: 0.07
Nodes (46): getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight(), getPositionTrainingRequirements() (+38 more)

### Community 40 - "Community 40"
Cohesion: 0.06
Nodes (34): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent (+26 more)

### Community 41 - "Community 41"
Cohesion: 0.06
Nodes (27): asyncio, ManagedStockfish, One non-shareable engine instance intended to be owned by one future worker., _EventLoopTransportStub, FakeProcess, managed(), Board, Limit (+19 more)

### Community 42 - "Community 42"
Cohesion: 0.10
Nodes (39): api_context(), client(), count_reader_calls(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path (+31 more)

### Community 43 - "Community 43"
Cohesion: 0.10
Nodes (40): _database_sidecars(), _failure(), LifecycleOperation, LifecycleResult, _path_exists(), Enum, OSError, Path (+32 more)

### Community 44 - "Community 44"
Cohesion: 0.08
Nodes (34): canonicalize_board(), canonicalize_fen(), PositionValidationError, Board, ValueError, From-scratch validation and canonicalization of chess positions., Raised when an input does not describe an acceptable chess position., Validate a complete six-field FEN and return its canonical identity. (+26 more)

### Community 45 - "Community 45"
Cohesion: 0.07
Nodes (31): frontend_src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story, CatalogueLink (+23 more)

### Community 46 - "Community 46"
Cohesion: 0.13
Nodes (35): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+27 more)

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (32): clear_caches(), _discard_inflight(), get_or_compute(), _Inflight, TimeoutError, Drop every cached payload and advance the generation. This is the sanctioned…, Remove ``inflight`` only while it is still the registered entry for ``key``. A…, Return the cached payload or compute it once per key. ``compute`` runs outside… (+24 more)

### Community 48 - "Community 48"
Cohesion: 0.09
Nodes (33): _configured_float(), get_training_requirement_policy(), Application dependencies for database capabilities., Return the configured policy, or ``None`` when the capability is unavailable., api_context(), client(), _complete_analysis_result(), fixture (+25 more)

### Community 49 - "Community 49"
Cohesion: 0.12
Nodes (33): backend_app_features_analysis, backend_app_features_evaluation, Path, Own the shared analysis lock, requeue interrupted work, then drain the queue.…, run_session(), completed_at(), connection(), database_path() (+25 more)

### Community 50 - "Community 50"
Cohesion: 0.14
Nodes (34): LineLibrary(), nodeName(), sameIds(), selectionDescription(), LineLibraryTree(), LineLibraryTreeProps, nodeName(), Default (+26 more)

### Community 51 - "Community 51"
Cohesion: 0.08
Nodes (33): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story (+25 more)

### Community 52 - "Community 52"
Cohesion: 0.09
Nodes (30): NormalizationResult, NormalizationWarning, import_normalized_games(), import_raw_month(), import_raw_months(), load_normalized_months(), normalize_raw_games(), Path (+22 more)

### Community 53 - "Community 53"
Cohesion: 0.17
Nodes (36): delete_preferred_move(), PreferredMoveMutationRequest, PreferredMoveRemovalRequest, put_preferred_move(), Path, Atomically apply one ordinary preferred-move mutation value., Atomically remove one ordinary preferred-move interval value., One complete parent FEN and one configured half-open interval. (+28 more)

### Community 54 - "Community 54"
Cohesion: 0.15
Nodes (27): datetime, _database(), _FakeClock, _FakeEngine, _FakeMutex, AnalysisQuality, AnalysisResultInput, Any (+19 more)

### Community 55 - "Community 55"
Cohesion: 0.09
Nodes (31): frontend_src_api_client_getopenings, frontend_src_api_client_getopeningsdata, frontend_src_api_client_getpositiontrainingrequirementsdata, frontend_src_api_client_openingcatalogueresponse, abortError(), buildTrainingRequirementsQuery(), currentUtcDate(), errorCode() (+23 more)

### Community 56 - "Community 56"
Cohesion: 0.08
Nodes (34): frontend_src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+26 more)

### Community 57 - "Community 57"
Cohesion: 0.12
Nodes (33): PositionInsightOpening, sqlalchemy, _analysis_state(), Path, PositionInsightPreference, PositionInsightResult, Position insight helpers., Read analysis through the caller's already validated connection. (+25 more)

### Community 58 - "Community 58"
Cohesion: 0.11
Nodes (30): acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url(), ArchiveMonth (+22 more)

### Community 59 - "Community 59"
Cohesion: 0.11
Nodes (29): createMoveHistoryRows(), KEY_NAVIGATION, frontend_src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow (+21 more)

### Community 60 - "Community 60"
Cohesion: 0.13
Nodes (32): math, _eligible_evidence(), TrainerColor, Raised when a compatible database contains unusable training data., TrainingRequirementStorageError, validate_uci(), _active_preference(), _current_scoped_groups() (+24 more)

### Community 61 - "Community 61"
Cohesion: 0.13
Nodes (30): _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any, Path (+22 more)

### Community 62 - "Community 62"
Cohesion: 0.11
Nodes (33): alias, preferred_moves_key(), Canonical key for one validated preferred-move timeline., delete_preferred_moves(), _error(), get_preferred_moves(), _mutation_period_response(), _mutation_preference() (+25 more)

### Community 63 - "Community 63"
Cohesion: 0.11
Nodes (32): games_key(), GameSearchQuery, Canonical key from the validated games query and resolved database., GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel (+24 more)

### Community 64 - "Community 64"
Cohesion: 0.17
Nodes (28): _normalized_file_path(), _sha256_file(), _StoredAttempts, Benchmark loading and top-level invocation., BenchmarkCompatibilityError, BenchmarkJob, BenchmarkOutcome, A stable identity for one position/profile/round analysis. (+20 more)

### Community 65 - "Community 65"
Cohesion: 0.13
Nodes (27): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+19 more)

### Community 66 - "Community 66"
Cohesion: 0.10
Nodes (26): AnalysisValidationError, _FrozenJsonObject, Any, ValueError, Raised when normalized analysis input is outside the catalogue domain., A JSON-compatible dict whose ordinary mutation operations are disabled., _classify_board(), classify_terminal_kind() (+18 more)

### Community 67 - "Community 67"
Cohesion: 0.11
Nodes (31): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+23 more)

### Community 68 - "Community 68"
Cohesion: 0.12
Nodes (29): functools, sqlalchemy_engine, _assert_compatible_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Connection, RuntimeError (+21 more)

### Community 69 - "Community 69"
Cohesion: 0.12
Nodes (26): AnalysisResultInput, NotSavedReason, PublicationOutcome, A complete engine-independent result payload without position or terminal…, A result whose terminal kind and candidate lines passed position validation., Saved or expected not-saved result for the publication service., Build an expected not-saved outcome with its explicit reason., Expected reasons a later publication operation may decline a result. (+18 more)

### Community 70 - "Community 70"
Cohesion: 0.12
Nodes (27): create_schema(), Path, Create schema v2 or accept an exactly compatible existing database., _remove_new_target(), _normalized_sql(), Connection, Path, test_canonical_resource_is_installed_and_schema_is_exact() (+19 more)

### Community 71 - "Community 71"
Cohesion: 0.10
Nodes (23): MoveResponseDistribution, MoveResponseDistributionReader, PositionContext, PositionContextReader, Path, RuntimeError, TrainerColor, Direct, read-only statistics over normalized game occurrences. (+15 more)

### Community 72 - "Community 72"
Cohesion: 0.14
Nodes (18): _counts(), FixedClock, _game_fixture(), GameTransport, OpeningTransport, Any, datetime, MonkeyPatch (+10 more)

### Community 73 - "Community 73"
Cohesion: 0.17
Nodes (29): argparse, ArgumentParser, src_tools, build_steps(), classify_result(), _command_text(), _documented_storybook_teardown(), execute_step() (+21 more)

### Community 74 - "Community 74"
Cohesion: 0.08
Nodes (26): engines, node, name, private, type, version, dirname, eslint (+18 more)

### Community 75 - "Community 75"
Cohesion: 0.10
Nodes (25): frontend_src_api_client_getpositiontrainingrequirements, ContractOperation, dirname, ALLOWED_RUNTIME_CLIENT_IMPORTS, collectProductionSourceFiles(), dirname, SOURCE_EXTENSIONS, srcDir (+17 more)

### Community 76 - "Community 76"
Cohesion: 0.10
Nodes (23): GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game(), _occurrence_from_row(), _optional_int(), _optional_text() (+15 more)

### Community 77 - "Community 77"
Cohesion: 0.17
Nodes (29): PositionInsightRequest, The complete position, trainer-color, and date context for one read., PositionInsightRepository, Path, TrainerColor, Read one position insight from an explicit database path., Compose one insight using only an explicit, compatible database path., read_position_insight() (+21 more)

### Community 78 - "Community 78"
Cohesion: 0.13
Nodes (25): AccessMode, _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_existing_connection(), probe_connection(), Connection, Path (+17 more)

### Community 79 - "Community 79"
Cohesion: 0.16
Nodes (24): _database(), FakeEngine, _profile(), AnalysisProfile, AnalysisResult, Path, _result(), test_eligibility_stale_reuse_and_idempotent_resume() (+16 more)

### Community 80 - "Community 80"
Cohesion: 0.19
Nodes (26): api_context(), create_openings_database(), fixture, MonkeyPatch, Path, TestClient, _create_encoded_key_database(), _create_rebuilt_database() (+18 more)

### Community 81 - "Community 81"
Cohesion: 0.17
Nodes (20): BenchmarkRunner, BenchmarkSpec, csv, _fake_analysis(), _FakeEngine, _FakeFactory, _InjectedWriter, Any (+12 more)

### Community 82 - "Community 82"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 83 - "Community 83"
Cohesion: 0.14
Nodes (27): _atomic_replace(), load_month(), merge_current_month(), publish_month(), Any, Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files. (+19 more)

### Community 84 - "Community 84"
Cohesion: 0.15
Nodes (26): _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Path, ValueError, Strict, storage-independent normalization of opening source routes. (+18 more)

### Community 85 - "Community 85"
Cohesion: 0.12
Nodes (27): TrainingRequirementPolicy, TrainingRequirementQuery, Canonical key from the validated query, resolved database, and policy., training_requirements_key(), HTTP contracts for position training requirements., _answer_response(), _error(), get_position_training_requirements() (+19 more)

### Community 86 - "Community 86"
Cohesion: 0.17
Nodes (28): chess_move_trainer_database_openings_persistence, chess_move_trainer_database_openings_source, Game, lookup_fen(), OpeningInputError, _parse_pgn_input(), Replay one standard-start PGN and recognize reached opening endpoints., Raised when a FEN or PGN query is not an accepted standard-chess input. (+20 more)

### Community 87 - "Community 87"
Cohesion: 0.19
Nodes (28): OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryNode, booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys() (+20 more)

### Community 88 - "Community 88"
Cohesion: 0.11
Nodes (26): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+18 more)

### Community 89 - "Community 89"
Cohesion: 0.08
Nodes (26): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+18 more)

### Community 90 - "Community 90"
Cohesion: 0.20
Nodes (24): Build the successful publication outcome., Construct one normalized result payload without database or chess checks., validate_analysis_result(), _line(), _lines(), AnalysisLine, AnalysisRepository, Path (+16 more)

### Community 91 - "Community 91"
Cohesion: 0.17
Nodes (26): checkA11y(), DistributionLabelBox, expectActiveSessionHistoryEntry(), expectBothRelationshipBoxes(), expectDateFreePreferredPanel(), expectDistributionChartAndControlsClean(), expectNoHorizontalOverflow(), expectPanelMinimums() (+18 more)

### Community 92 - "Community 92"
Cohesion: 0.20
Nodes (21): import_raw_games(), Normalize first, then commit accepted games independently in source order., GameRepository, Persist complete normalized games without exposing database handles., _count(), _game_snapshot(), MonkeyPatch, Path (+13 more)

### Community 93 - "Community 93"
Cohesion: 0.22
Nodes (26): GameSearchPage, GameSearchQuery, One finite, deterministic page of public game summaries., All approved collection filters and pagination controls., GameSearchRepository, Path, Search normalized games using one explicit read-only schema-v1 path., _add_coverage() (+18 more)

### Community 94 - "Community 94"
Cohesion: 0.21
Nodes (26): Validated read-only discovery controls., TrainingRequirementQuery, discover_training_requirements(), Path, Discover scored requirements from one explicit existing database., _add_black_training_item(), _fixture(), _game() (+18 more)

### Community 95 - "Community 95"
Cohesion: 0.12
Nodes (25): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+17 more)

### Community 96 - "Community 96"
Cohesion: 0.17
Nodes (26): collections, _canonical_endpoint(), _database_signature(), _endpoint_map(), _load_catalogue(), _load_endpoint_map_cached(), _load_routes(), _load_routes_cached() (+18 more)

### Community 97 - "Community 97"
Cohesion: 0.13
Nodes (23): BoardAdapter(), PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation() (+15 more)

### Community 98 - "Community 98"
Cohesion: 0.15
Nodes (25): Headers, _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), _normalize_game() (+17 more)

### Community 99 - "Community 99"
Cohesion: 0.12
Nodes (16): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Raised when a compatible database cannot publish the opening catalogue., Immutable counts describing one successfully committed catalogue replacement. (+8 more)

### Community 100 - "Community 100"
Cohesion: 0.15
Nodes (17): BulkRunner, PublicationOutcome, _database(), _FakeEngine, _FakeMutex, AnalysisResultInput, Path, _RecordingPublisher (+9 more)

### Community 101 - "Community 101"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 102 - "Community 102"
Cohesion: 0.10
Nodes (18): frontend_src_api_client_openingcatalogueitemresponse, frontend_src_api_client_trainingrequirementresponse, ALL_OPENINGS_VALUE, filterOpeningCatalogue(), frontend_src_features_trainer_practice_openingsearchcombobox_module, OPENING_SEARCH_VISIBLE_LIMIT, openingLabel(), OpeningSearchCombobox() (+10 more)

### Community 103 - "Community 103"
Cohesion: 0.15
Nodes (23): buildUrl(), createQuerySerializer(), defaultHeaders, defaultQuerySerializer, ErrInterceptor, ReqInterceptor, ResInterceptor, ArraySeparatorStyle (+15 more)

### Community 104 - "Community 104"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 105 - "Community 105"
Cohesion: 0.37
Nodes (22): _archive_url(), _config(), FixedClock, _fixture(), _month_url(), Any, datetime, Path (+14 more)

### Community 106 - "Community 106"
Cohesion: 0.14
Nodes (19): api_context(), client(), create_preferred_moves_database(), put_body(), fixture, MonkeyPatch, Path, TestClient (+11 more)

### Community 107 - "Community 107"
Cohesion: 0.10
Nodes (22): PromotionColor, PromotionPresentation, Cancellation, ConstrainedDrawer, defaultArgs, ForcedColorsAndReducedMotion, KeyboardSelection, meta (+14 more)

### Community 108 - "Community 108"
Cohesion: 0.16
Nodes (23): appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession(), playAndStagePositionPickerMove() (+15 more)

### Community 109 - "Community 109"
Cohesion: 0.16
Nodes (19): PreferredMoveRepository, Path, Read and amend preferred moves without exposing database handles., Path, _period_values(), parametrize, Path, _run_serialized_delete_and_put() (+11 more)

### Community 110 - "Community 110"
Cohesion: 0.13
Nodes (20): _close_handle(), DatabaseMutexError, _finite_wait(), _lock_file_for_database(), mutex_name_for_database(), MutexUnavailableError, normalize_database_path(), Any (+12 more)

### Community 111 - "Community 111"
Cohesion: 0.14
Nodes (23): ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse, PreferredMovesMutationRequest (+15 more)

### Community 112 - "Community 112"
Cohesion: 0.26
Nodes (20): client(), _database(), fixture, MonkeyPatch, parametrize, Path, TestClient, test_browsing_list_does_not_modify_database() (+12 more)

### Community 113 - "Community 113"
Cohesion: 0.12
Nodes (19): frontend_src_api_client_trainingrequirementitemresponse, TrainerPracticePage, defaultTrainerPracticeApi, OpeningCatalogueSnapshotResult, queryOpeningCatalogueSnapshot(), queryOpeningChoices(), queryTrainingRequirements(), TrainerPracticeQueryError (+11 more)

### Community 114 - "Community 114"
Cohesion: 0.12
Nodes (20): _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), BaseException, OSError, Atomic artifact persistence for benchmarks., BenchmarkError (+12 more)

### Community 115 - "Community 115"
Cohesion: 0.11
Nodes (15): PageContentBoundaryProps, Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES (+7 more)

### Community 116 - "Community 116"
Cohesion: 0.19
Nodes (21): collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., DirectCapabilities, DirectPreflightError, ValueError (+13 more)

### Community 117 - "Community 117"
Cohesion: 0.23
Nodes (19): concurrent_futures, Path, Request one desired analysis through an explicit app database path., request_analysis(), _database(), _position_with_result(), AnalysisQuality, Path (+11 more)

### Community 118 - "Community 118"
Cohesion: 0.16
Nodes (19): BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys, Options (+11 more)

### Community 119 - "Community 119"
Cohesion: 0.18
Nodes (19): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerStatus, BoardSquareHighlight, boardSquareStyles() (+11 more)

### Community 120 - "Community 120"
Cohesion: 0.17
Nodes (18): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+10 more)

### Community 121 - "Community 121"
Cohesion: 0.18
Nodes (21): AnalysisLine, Construct one normalized line after pure scalar/domain validation., Validate and freeze one JSON object without requiring any setting keys., validate_analysis_line(), validate_settings_object(), _line(), AnalysisLine, parametrize (+13 more)

### Community 122 - "Community 122"
Cohesion: 0.25
Nodes (19): EvaluationSchemaError, The independently versioned evaluation queue schema is absent or incompatible., _existing_tables(), initialize_evaluation_schema(), Connection, Explicit initialization for the independent evaluation queue schema., Create the evaluation queue namespace only through this explicit operation., Require the complete supported evaluation schema without creating or repairing… (+11 more)

### Community 123 - "Community 123"
Cohesion: 0.10
Nodes (17): BoardAdapterProps, BoardRender(), frontend_src_features_board_adapter_boardadapter_module, PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition (+9 more)

### Community 124 - "Community 124"
Cohesion: 0.10
Nodes (16): frontend_src_features_design_system_feedback_pagefeedback_module, AllSeverities, meta, Story, frontend_src_features_design_system_feedback_panelfeedback_module, AllSeverities, meta, Story (+8 more)

### Community 125 - "Community 125"
Cohesion: 0.14
Nodes (19): actionLabel(), formatDay(), formatRange(), frontend_src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction, PreferredMoveSchedulePeriod (+11 more)

### Community 126 - "Community 126"
Cohesion: 0.14
Nodes (15): PositionRepository, Path, Canonicalize and persist one complete FEN in an owned transaction., Resolve canonical positions using package-owned connections and transactions., Yield an opaque all-or-nothing unit of work for one existing v1 database., Canonicalize and persist one board in an owned transaction., Path, test_concurrent_writers_resolve_one_stable_id_and_one_row() (+7 more)

### Community 127 - "Community 127"
Cohesion: 0.10
Nodes (4): _FakeProcess, _FakeStdin, _FakeStdout, Any

### Community 128 - "Community 128"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 129 - "Community 129"
Cohesion: 0.18
Nodes (13): BoardAnswerPresentation, BranchMove, BranchSnapshot, InteractiveBoardMoveIntent, InteractiveBoardHarness(), InteractiveBoardHarnessProps, terminalDescription(), deriveLastMove() (+5 more)

### Community 130 - "Community 130"
Cohesion: 0.14
Nodes (17): SYNTHETIC_OPENING_RESPONSE, filterKind(), OpeningLineLibraryFailure, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType, OpeningLineLibraryGroupNode, OpeningLineLibraryLineNode, OpeningLineLibraryNodeBase (+9 more)

### Community 131 - "Community 131"
Cohesion: 0.16
Nodes (9): @playwright/test, checkA11y(), STORY_IDS, isAxeBusyError(), retryAxeWhenBusy(), waitForStorybookRender(), assertFixtureStates(), checkA11y() (+1 more)

### Community 132 - "Community 132"
Cohesion: 0.12
Nodes (17): PositionInsightAnalysis, PositionInsightError, PositionInsightPreference, PositionInsightSchemaError, PositionInsightValidationError, Exception, RuntimeError, ValueError (+9 more)

### Community 133 - "Community 133"
Cohesion: 0.25
Nodes (15): _catalogue_snapshot(), MonkeyPatch, Path, _rows(), _source_dir(), test_deletion_checkpoint_order_is_child_first(), test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(), test_first_publication_writes_labels_routes_and_contiguous_children() (+7 more)

### Community 134 - "Community 134"
Cohesion: 0.27
Nodes (17): _balance(), _fixture(), _game(), _occurrence(), Connection, parametrize, Path, TrainingAnswerRequest (+9 more)

### Community 135 - "Community 135"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 136 - "Community 136"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 137 - "Community 137"
Cohesion: 0.32
Nodes (18): PreferredMoveTimelineRepository, Read one preferred-move timeline from an explicit database path., _configured_database(), _database(), parametrize, Path, _request(), _segment_values() (+10 more)

### Community 138 - "Community 138"
Cohesion: 0.30
Nodes (6): _ArtifactPaths, BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 139 - "Community 139"
Cohesion: 0.20
Nodes (14): delete_body(), MonkeyPatch, parametrize, Path, test_delete_bad_values_give_clear_error(), test_delete_locked_database_gives_unavailable_without_changing_file(), test_delete_makes_get_and_insight_show_unconfigured(), test_delete_missing_or_broken_database_gives_unavailable_without_creating_file() (+6 more)

### Community 140 - "Community 140"
Cohesion: 0.13
Nodes (15): BoardControl(), BoardControlProps, BoardEvalStageProps, InteractiveBoardAdapterProps, BoardContentProps, HistoryProps, RepertoireBoardLane(), RepertoireBoardLaneProps (+7 more)

### Community 141 - "Community 141"
Cohesion: 0.18
Nodes (14): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+6 more)

### Community 142 - "Community 142"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 143 - "Community 143"
Cohesion: 0.12
Nodes (10): page(), successfulRequirements(), checkA11y(), expectDescriptionAssociation(), expectStaticGraphic(), expectValidSurface(), RICH_SPOKEN_DESCRIPTION, STORY_IDS (+2 more)

### Community 144 - "Community 144"
Cohesion: 0.34
Nodes (17): Validate terminal policy and complete legal candidate lines from a neutral root., validate_analysis_position(), _line(), _position(), AnalysisLine, AnalysisTerminalKind, parametrize, _result() (+9 more)

### Community 145 - "Community 145"
Cohesion: 0.25
Nodes (16): normalize_game(), Return a fully validated game, or one ordinary warning for a skipped input., _fixture(), parametrize, test_draw_mapping_and_pgn_termination_fallback(), test_ineligible_malformed_and_illegal_inputs_are_ordinary_skips(), test_invalid_required_raw_fields_are_skipped(), test_non_unique_trainer_and_non_normal_start_are_skipped() (+8 more)

### Community 146 - "Community 146"
Cohesion: 0.28
Nodes (14): _count(), FixedClock, _fixture(), _game_url(), _month_url(), Any, datetime, Path (+6 more)

### Community 147 - "Community 147"
Cohesion: 0.14
Nodes (9): AnalysisEngine, Protocol, _close_engine(), _EngineRegistry, EngineFactory, Exception, A worker item failed permanently; no automatic retry is performed., One engine per worker thread; workers never receive the SQLite connection. (+1 more)

### Community 148 - "Community 148"
Cohesion: 0.19
Nodes (12): MonkeyPatch, parametrize, Path, _queue(), _remove_result(), _target_position_id(), test_injected_database_is_used_when_configured(), test_missing_or_bad_position_gives_clear_error() (+4 more)

### Community 149 - "Community 149"
Cohesion: 0.14
Nodes (13): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelDisplay, AnalysisPanelIntent, AnalysisPanelLine, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue (+5 more)

### Community 150 - "Community 150"
Cohesion: 0.15
Nodes (15): clearPending(), isPromotionCandidate(), PendingPromotion, PickerLiveRegion(), PROMOTION_OPTIONS, PromotionController, PromotionControllerOptions, promotionDescription() (+7 more)

### Community 151 - "Community 151"
Cohesion: 0.13
Nodes (14): booleanFilterData, data, LineLibraryCommitDescription, LineLibraryFilterKind, LineLibraryFilterOption, LineLibraryNodeKind, LineLibraryNodeSelectionDeclaration, LineLibraryRowContext (+6 more)

### Community 152 - "Community 152"
Cohesion: 0.12
Nodes (16): allowScripts, esbuild@0.25.12, esbuild@0.28.2, engines, node, vite, vitest, name (+8 more)

### Community 153 - "Community 153"
Cohesion: 0.17
Nodes (13): Return the current result value for callers using a result/read shape., _analysis_result(), _finite_non_negative(), _finite_positive(), datetime, Path, RuntimeError, ValueError (+5 more)

### Community 154 - "Community 154"
Cohesion: 0.26
Nodes (13): _normalized(), MonkeyPatch, parametrize, Path, _raw(), _rows(), test_correction_failure_at_each_boundary_preserves_prior_game(), test_fresh_game_persists_exact_metadata_positions_and_occurrences() (+5 more)

### Community 155 - "Community 155"
Cohesion: 0.27
Nodes (15): BaseException, parametrize, Path, repository(), test_boundary_requires_exactly_four_valid_fen_fields(), test_failed_replacement_restores_the_preexisting_schedule(), test_failure_or_interruption_rolls_back_standalone_position_and_period(), checkpoint() (+7 more)

### Community 156 - "Community 156"
Cohesion: 0.23
Nodes (13): request_params(), MonkeyPatch, parametrize, Path, test_bad_values_give_clear_error(), test_empty_schedule_and_en_passant_position_returns_unconfigured(), test_injected_database_is_used_when_configured(), test_known_timeline_returns_full_segments_and_ignores_unknown_filters() (+5 more)

### Community 157 - "Community 157"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 158 - "Community 158"
Cohesion: 0.18
Nodes (11): EvalBar(), EvalBarDisplayState, EvalBarProps, ExpectedDisplay, frontend_src_features_board_adapter_boardadapter_starting_fen, BoardEvalStage(), boardVisualIn(), meta (+3 more)

### Community 159 - "Community 159"
Cohesion: 0.29
Nodes (14): Path, Read one FEN observation from an explicit app database path., read_analysis_observation(), _database(), parametrize, Path, _queue(), _result() (+6 more)

### Community 160 - "Community 160"
Cohesion: 0.15
Nodes (5): Path, _python_sources(), test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin(), test_database_package_has_no_legacy_or_production_import_direction(), test_package_contains_no_runtime_wrapper_or_copied_legacy_generator()

### Community 161 - "Community 161"
Cohesion: 0.26
Nodes (12): _catalogue_snapshot(), _copy_sources(), _fixture_game(), _game_snapshot(), _latest_files(), OpeningTransport, BaseException, parametrize (+4 more)

### Community 162 - "Community 162"
Cohesion: 0.22
Nodes (14): createClient(), TODO: we probably want to return error and improve types, ReqInit, checkForExistence(), createConfig(), createInterceptors(), getParseAs(), headersEntries() (+6 more)

### Community 163 - "Community 163"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 164 - "Community 164"
Cohesion: 0.15
Nodes (12): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+4 more)

### Community 165 - "Community 165"
Cohesion: 0.19
Nodes (12): clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), frontend_src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage(), RepertoireResponsiveStage() (+4 more)

### Community 166 - "Community 166"
Cohesion: 0.50
Nodes (14): Path, _queue_row(), _result(), _setup(), _stored_analysis(), test_browser_completion_after_tool_promotion_publishes_then_releases(), test_claim_is_fifo_and_replaces_a_stale_token_with_fresh_uuid(), test_completion_publishes_and_deletes_matching_claim_in_one_lifecycle() (+6 more)

### Community 167 - "Community 167"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 168 - "Community 168"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 169 - "Community 169"
Cohesion: 0.23
Nodes (11): NormalizedGame, _game_metadata(), _metadata_parameters(), PersistedGame, Any, PositionIdentity, Persist one game in its own transaction on an already validated connection., Persist one game while the caller owns the active transaction. (+3 more)

### Community 170 - "Community 170"
Cohesion: 0.23
Nodes (7): ArtifactWriter, AtomicArtifactWriter, Any, Path, Protocol, The small persistence seam used by the runner and focused tests., Write benchmark artifacts atomically, keeping temporary files local.

### Community 171 - "Community 171"
Cohesion: 0.24
Nodes (12): ContractModel, MutationRequestModel, BaseModel, Strict HTTP contracts for position training requirements., Base model that rejects fields outside the public contract., Base model for forward-compatible mutation input., TrainingAnswerRequest, TrainingAnswerResponse (+4 more)

### Community 172 - "Community 172"
Cohesion: 0.24
Nodes (11): Auth, AuthToken, BodySerializer, QuerySerializer, QuerySerializerOptions, Client, ClientMeta, Config (+3 more)

### Community 173 - "Community 173"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 174 - "Community 174"
Cohesion: 0.21
Nodes (10): AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay(), missingDisplay() (+2 more)

### Community 175 - "Community 175"
Cohesion: 0.15
Nodes (11): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+3 more)

### Community 176 - "Community 176"
Cohesion: 0.15
Nodes (9): boardLane, Boundary1039, Boundary1040, Boundary699, Boundary700, engineLane, meta, sessionLane (+1 more)

### Community 177 - "Community 177"
Cohesion: 0.23
Nodes (11): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, Read one public game detail from an explicit database path., One public replay occurrence without SQLite identity fields., One public game detail with replayable occurrences., read_game(), Path (+3 more)

### Community 178 - "Community 178"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 179 - "Community 179"
Cohesion: 0.21
Nodes (6): DatabaseMutex, Release ownership and close the kernel handle whenever possible., Best-effort close, releasing ownership first when necessary., Acquire and release one database-specific Stockfish mutex. Windows keeps the…, Whether this instance currently owns the mutex., Whether the successful acquisition recovered an abandoned owner.

### Community 180 - "Community 180"
Cohesion: 0.26
Nodes (12): count_lines(), is_excluded(), is_test_file(), main(), print_report(), Path, Count lines in a file, tolerating unusual characters., Walk the repo and measure every script file. Returns one row per file. (+4 more)

### Community 181 - "Community 181"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 182 - "Community 182"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 183 - "Community 183"
Cohesion: 0.18
Nodes (6): fulfillJson(), mockCatalogue(), OPENING_ITEMS, TRAINING_ERROR, TRAINING_ITEM, TRAINING_RESPONSE_BASE

### Community 184 - "Community 184"
Cohesion: 0.20
Nodes (9): load_positions(), Any, Path, Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark(), BenchmarkPosition, One validated position from the explicit benchmark input file. (+1 more)

### Community 185 - "Community 185"
Cohesion: 0.36
Nodes (6): Any, Drain current queued/reclaimable work and then exit., One isolated request failure retained only in the launch outcome., Drain queued requests with one sequential engine process at a time., WorkerFailure, WorkerRunner

### Community 186 - "Community 186"
Cohesion: 0.40
Nodes (9): _basis(), _database(), _profile(), AnalysisProfile, Path, _result(), test_all_selection_deduplicates_and_tie_breaks_by_exact_fen(), test_preflight_counts_projection_and_hash_memory_without_mutation() (+1 more)

### Community 187 - "Community 187"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 188 - "Community 188"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 189 - "Community 189"
Cohesion: 0.20
Nodes (6): DirectProof, Read-only aggregate facts suitable for bounded direct evidence., Whether the retained canonical preference table is empty., Whether the fixed database exposes exactly the catalogue's ten tables., Whether every stored game has a complete ordered occurrence set., Whether every stored route has contiguous one-based move plies.

### Community 190 - "Community 190"
Cohesion: 0.22
Nodes (6): formDataBodySerializer, jsonBodySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArrayStyle, ObjectStyle

### Community 191 - "Community 191"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 192 - "Community 192"
Cohesion: 0.22
Nodes (4): fixture(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 193 - "Community 193"
Cohesion: 0.28
Nodes (7): MatchKind, _build_recognition(), One immutable label reached at one encountered ply., Return the explicit route or transposition match kind., Return the ordered recognition timeline., RecognizedOpening, _select_current()

### Community 194 - "Community 194"
Cohesion: 0.50
Nodes (8): Popen, _child_process(), Path, test_abandoned_child_acquisition_is_reported_as_acquired(), test_clean_release_allows_the_next_owner(), test_mutex_name_uses_one_normalized_database_identity(), test_real_child_owner_is_busy_then_kernel_releases_on_process_death(), _wait_for_signal()

### Community 195 - "Community 195"
Cohesion: 0.25
Nodes (4): expectApplicationAxeClean(), openStory(), STORY_IDS, storyUrl()

### Community 196 - "Community 196"
Cohesion: 0.29
Nodes (6): _convert_result(), AnalysisProfile, AnalysisResult, AnalysisTimeoutError, TimeoutError, A node-limited engine call exceeded its independent wall-clock watchdog.

### Community 197 - "Community 197"
Cohesion: 0.25
Nodes (5): Constrained, HISTORY, Interactive, meta, Story

### Community 198 - "Community 198"
Cohesion: 0.29
Nodes (7): APP_TEST_FILES, appWebServers, profile, selectedTestFiles(), serverProfile(), STORYBOOK_TEST_FILES, storybookWebServer

### Community 199 - "Community 199"
Cohesion: 0.29
Nodes (6): engines, node, name, private, type, version

### Community 201 - "Community 201"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 202 - "Community 202"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 203 - "Community 203"
Cohesion: 0.29
Nodes (5): OpeningAcquisitionTransport, Protocol, Return one text response., Minimal transport required by commit resolution and file retrieval., Return one decoded JSON response.

### Community 204 - "Community 204"
Cohesion: 0.29
Nodes (4): BenchmarkSpec, Any, Validated, deterministic matrix inputs for one benchmark run., Enumerate every job once in the recorded deterministic order.

### Community 205 - "Community 205"
Cohesion: 0.29
Nodes (4): Return the later CLI-compatible status for this service outcome., Observable result of one finite worker launch., Whether this finite launch completed without failures or interruption., WorkerOutcome

### Community 206 - "Community 206"
Cohesion: 0.62
Nodes (6): _assert_same_key_set(), _assert_same_mapping(), _database(), Path, test_real_direct_database_capabilities(), test_real_direct_database_matches_the_retained_source_ledger()

### Community 208 - "Community 208"
Cohesion: 0.33
Nodes (6): devDependencies, @axe-core/playwright, @playwright/mcp, @playwright/test, vite, vitest

### Community 209 - "Community 209"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 210 - "Community 210"
Cohesion: 0.50
Nodes (5): parse_month_selection(), Parse an exact zero-padded YYYY-MM calendar month selection., parametrize, test_month_selection_parses_only_exact_zero_padded_calendar_months(), test_month_selection_rejects_malformed_or_invalid_months()

### Community 211 - "Community 211"
Cohesion: 0.40
Nodes (3): MutexBusyError, A finite wait expired because another process owns the mutex., Try to acquire ownership, returning false for a finite busy wait.

### Community 213 - "Community 213"
Cohesion: 0.50
Nodes (3): client, CreateClientConfig, ClientOptions

### Community 214 - "Community 214"
Cohesion: 0.50
Nodes (3): elementProto, topLayerPseudoSelectors, @testing-library/jest-dom

### Community 215 - "Community 215"
Cohesion: 0.83
Nodes (3): execute(), globFiles(), resolveRg()

## Knowledge Gaps
- **884 isolated node(s):** `GameLoaderFailureKind`, `GameLoaderProps`, `GameMainLineOccurrence`, `TemporaryBranch`, `PreferredMoveStoryFixture` (+879 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2475 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **73 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `position_key_from_fen()` connect `Community 7` to `Community 35`, `Community 79`, `Community 15`, `Community 17`, `Community 29`?**
  _High betweenness centrality (0.443) - this node is a cross-community bridge._
- **Why does `PositionKey` connect `Community 17` to `Community 35`, `Community 7`?**
  _High betweenness centrality (0.442) - this node is a cross-community bridge._
- **Why does `react` connect `Community 10` to `Community 0`, `Community 129`, `Community 4`, `Community 6`, `Community 141`, `Community 13`, `Community 18`, `Community 22`, `Community 150`, `Community 151`, `Community 24`, `Community 28`, `Community 158`, `Community 163`, `Community 165`, `Community 38`, `Community 167`, `Community 40`, `Community 45`, `Community 174`, `Community 176`, `Community 50`, `Community 51`, `Community 56`, `Community 59`, `Community 191`, `Community 65`, `Community 197`, `Community 74`, `Community 82`, `Community 88`, `Community 102`, `Community 107`, `Community 113`, `Community 115`, `Community 119`, `Community 123`, `Community 125`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 63 inferred relationships involving `create_schema()` (e.g. with `create_benchmark_database()` and `create_cache_database()`) actually correct?**
  _`create_schema()` has 63 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `SchemaIncompatibleError` (e.g. with `get_game()` and `AnalysisObservationRepository`) actually correct?**
  _`SchemaIncompatibleError` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `GameLoaderFailureKind`, `GameLoaderProps`, `GameMainLineOccurrence` to the rest of the system?**
  _884 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.03517460317460318 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
