# Graph Report - ChessMoveTrainer  (2026-09-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 6593 nodes · 17820 edges · 252 communities (197 shown, 34 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 1181 edges (avg confidence: 0.89)
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
- Community 197
- Community 198
- Community 199
- Community 200
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
- Community 212
- Community 213
- Community 214
- Community 215
- Community 216
- Community 217
- Community 218
- Community 220
- Community 221
- Community 223
- Community 224
- Community 225
- Community 226
- Community 227
- Community 228
- Community 242
- Community 243
- Community 244
- Community 249
- Community 250
- Community 251

## God Nodes (most connected - your core abstractions)
1. `create_schema()` - 115 edges
2. `react` - 83 edges
3. `vitest` - 77 edges
4. `SchemaIncompatibleError` - 74 edges
5. `canonicalize_fen()` - 72 edges
6. `_assert_compatible_schema()` - 71 edges
7. `AnalysisQuality` - 62 edges
8. `AnalysisProfile` - 61 edges
9. `CanonicalPosition` - 57 edges
10. `@storybook/react-vite` - 57 edges

## Surprising Connections (you probably didn't know these)
- `test_settings_accept_an_empty_or_arbitrary_json_object_without_required_keys()` --calls--> `validate_settings_object()`  [INFERRED]
  tests/database/analysis/test_models.py → src/chess_move_trainer/database/analysis/validation.py
- `put_preferred_moves()` --calls--> `PreferredMoveMutationRequest`  [INFERRED]
  backend/app/features/preferred_moves/router.py → src/chess_move_trainer/database/preferred_moves/mutations.py
- `test_standalone_write_creates_position_and_schedule_together()` --uses--> `DateResolution`  [INFERRED]
  tests/database/preferred_moves/test_repository.py → src/chess_move_trainer/database/preferred_moves/ranges.py
- `test_unknown_reads_are_empty_and_unconfigured_without_creating_rows()` --uses--> `DateResolution`  [INFERRED]
  tests/database/preferred_moves/test_repository.py → src/chess_move_trainer/database/preferred_moves/ranges.py
- `periods_for()` --uses--> `NormalizedPeriod`  [INFERRED]
  tests/database/preferred_moves/test_inference.py → src/chess_move_trainer/database/preferred_moves/ranges.py

## Import Cycles
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 4-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_helpers.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_models.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_readers.py -> src/chess_move_trainer/database/openings/recognition.py`
- 5-file cycle: `src/chess_move_trainer/database/openings/recognition.py -> src/chess_move_trainer/database/openings/source.py -> src/chess_move_trainer/database/positions/__init__.py -> src/chess_move_trainer/database/positions/insight.py -> src/chess_move_trainer/database/positions/insight_repository.py -> src/chess_move_trainer/database/openings/recognition.py`

## Communities (252 total, 34 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (98): Public preferred-move schedule values, operations, and storage services., _canonical_fen(), _parse_mutation_date(), PreferredMoveMutationRequest, PreferredMoveMutationResult, PreferredMoveRemovalRequest, PreferredMoveRemovalResult, date (+90 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (97): Color, Queue, AnalysisLine, AnalysisQuality, AnalysisResultInput, AnalysisScoreKind, AnalysisTerminalKind, Enum (+89 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (96): Exception, _translate_storage_error(), _begin_immediate(), _checked_connection(), _claim_identity(), _enqueue_in_transaction(), _format_timestamp(), _oldest_claimable() (+88 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (97): AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient(), StoryAnalysisLifecycleEvent (+89 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (99): Typer application objects., _interrupted(), _is_schema_error(), _operational_error(), _preference_from_options(), _preferred_period_json(), BaseException, Exception (+91 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (79): AnalysisBusyError, AnalysisValidationError, ValueError, A short coordinator SQLite transaction could not acquire its lock., An analysis profile or complete result violates the persistence contract., Persisted backend analysis contracts., A single OS-owned lock for one top-level analysis invocation., AnalysisProfile (+71 more)

### Community 6 - "Community 6"
Cohesion: 0.03
Nodes (55): ALLOWED_RUNTIME_CLIENT_IMPORTS, dirname, SOURCE_EXTENSIONS, srcDir, AnalysisOperationResult, { shouldThrow }, FEEDBACK_TOKENS, here (+47 more)

### Community 7 - "Community 7"
Cohesion: 0.04
Nodes (80): MatchKind, _build_recognition(), _canonical_endpoint(), _endpoint_map(), _load_routes(), lookup_fen(), _materialize_routes(), OpeningRecognitionError (+72 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (75): Immutable engine-independent analysis values and input validation., AnalysisError, AnalysisStorageError, Exception, RuntimeError, Base class for bounded analysis-package failures., Reserved category for an unexpected analysis storage failure., _analysis_state() (+67 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (86): requestAnalysis(), AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse, DeletePreferredMovesData (+78 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (71): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerPresentation, BoardAnswerStatus, BoardSquareHighlight (+63 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (62): AccessMode, Read the complete current analysis result and candidate lines., _required_text(), _configure_sqlite_connection(), ConnectionProbe, _create_sqlite_connection(), _open_connection(), _open_existing_connection() (+54 more)

### Community 12 - "Community 12"
Cohesion: 0.08
Nodes (75): position_key_from_fen(), Return the internal four-field identity for a valid canonical six-field FEN., EvaluationLockError, EvaluationQueueError, EvaluationValidationError, RuntimeError, ValueError, Typed errors for the browser-evaluation service boundary. (+67 more)

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (68): Any, DirEntry, MonkeyPatch, RuntimeError, _assert_safe_path(), _atomic_write_batch(), build_graphify_command(), _canonical_graph() (+60 more)

### Community 14 - "Community 14"
Cohesion: 0.05
Nodes (56): _bounded_call(), _candidate(), close_process(), _convert_result(), _engine_shutdown_poll(), EngineIdentity, EngineProcess, _identity() (+48 more)

### Community 15 - "Community 15"
Cohesion: 0.04
Nodes (53): App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps, ConstrainedClosed, ConstrainedOpen, Healthy (+45 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (56): Popen, Poll quietly and spin the engine up only while work is claimed. Resting usage…, _run_worker_loop(), Stockfish process and database-lock services., _close_handle(), DatabaseMutex, DatabaseMutexError, _finite_wait() (+48 more)

### Community 17 - "Community 17"
Cohesion: 0.07
Nodes (62): PromotionPiece, ChessSide, Fen, Ply, San, GameLoader(), handleSubmit(), GameLoaderFailureKind (+54 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (67): AnalysisReadError, AnalysisReadRepository, Path, RuntimeError, Raised when a current analysis result is incomplete or malformed., Read one complete current result through a package-owned read path., Validate and freeze one JSON object without requiring any setting keys., validate_settings_object() (+59 more)

### Community 19 - "Community 19"
Cohesion: 0.08
Nodes (58): acquire_openings(), _atomic_replace(), _atomic_replace_content(), _capture_prior_state(), _extract_resolved_commit(), HttpxOpeningAcquisitionTransport, OpeningAcquisitionError, OpeningAcquisitionFailure (+50 more)

### Community 20 - "Community 20"
Cohesion: 0.07
Nodes (59): deletePreferredMoves(), putPreferredMoves(), invalidatePreferredMove(), invalidateTrainingRequirements(), SessionMove, defaultPreferredMoveClient, deletePreferredMove(), failureFromOperation() (+51 more)

### Community 21 - "Community 21"
Cohesion: 0.05
Nodes (51): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+43 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (56): _choose_initial_signal(), _choose_replacement_signal(), _compare_evidence(), _deduplicate_candidate_signals(), _has_conflicting_evidence(), _infer_position(), infer_preferred_moves(), _latest_signal_for_move() (+48 more)

### Community 23 - "Community 23"
Cohesion: 0.09
Nodes (55): Build the successful publication outcome., Build an expected not-saved outcome with its explicit reason., _line(), _lines(), AnalysisLine, AnalysisRepository, Path, _repository() (+47 more)

### Community 24 - "Community 24"
Cohesion: 0.07
Nodes (45): invalidateAnalysisObservation(), invalidatePositionInsight(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput, OptionalText, PositionInsightKeyInput (+37 more)

### Community 25 - "Community 25"
Cohesion: 0.08
Nodes (56): _validate_lock_timeout(), Package-owned database connection services., _cell(), _column_kind(), _foreign_keys(), _heading_text(), _inspect_connection(), inspect_schema() (+48 more)

### Community 26 - "Community 26"
Cohesion: 0.06
Nodes (46): AnalysisObservation, AnalysisObservationErrorCode, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestErrorCode, get_rebuilt_database_path(), Path, Return the explicit clean database path for the current application process. (+38 more)

### Community 27 - "Community 27"
Cohesion: 0.07
Nodes (46): api_context(), client(), create_preferred_moves_database(), delete_body(), put_body(), fixture, MonkeyPatch, Path (+38 more)

### Community 28 - "Community 28"
Cohesion: 0.09
Nodes (53): canonical_write(), _cleanup_proof(), execute_benchmark(), BenchmarkFixture, _connect_read_only(), _database_guard(), _exact_fen_count(), _minimum_occurrences() (+45 more)

### Community 29 - "Community 29"
Cohesion: 0.09
Nodes (54): ContractModel, MovePreferenceResponse, NoPreferenceResponse, PositionInsightAnalysisResponse, PositionInsightErrorResponse, PositionInsightExperienceResponse, PositionInsightLineResponse, PositionInsightObservedMoveResponse (+46 more)

### Community 30 - "Community 30"
Cohesion: 0.09
Nodes (48): CoverageState, GameSearchSort, GameSearchError, GameSearchSchemaError, GameSearchStorageError, Exception, RuntimeError, Raised when a compatible game database cannot be read safely. (+40 more)

### Community 31 - "Community 31"
Cohesion: 0.11
Nodes (47): delete_preferred_move(), put_preferred_move(), Path, Atomically apply one ordinary preferred-move mutation value., Atomically remove one ordinary preferred-move interval value., _period_values(), parametrize, Path (+39 more)

### Community 32 - "Community 32"
Cohesion: 0.08
Nodes (42): collect_direct_capabilities(), _collect_opening_capabilities(), Path, Real-reader capability proof while retaining only aggregate facts., Exercise real readers while retaining only bounded aggregate facts., DirectCapabilities, DirectPreflightError, DirectVerification (+34 more)

### Community 33 - "Community 33"
Cohesion: 0.09
Nodes (50): alias, ContractModel, MovePreferenceResponse, MutationMovePreferenceRequest, MutationNoPreferenceRequest, MutationRequestModel, NoPreferenceResponse, PreferredMovesErrorResponse (+42 more)

### Community 34 - "Community 34"
Cohesion: 0.07
Nodes (34): AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport, OPTIONS, RADIO_OPTIONS (+26 more)

### Community 35 - "Community 35"
Cohesion: 0.08
Nodes (41): AnalysisValidationError, _FrozenJsonObject, NotSavedReason, PublicationOutcome, Any, ValueError, Immutable normalized analysis values and bounded outcome categories., A result whose terminal kind and candidate lines passed position validation. (+33 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (49): benchmark_client(), benchmark_database(), create_benchmark_database(), _database_info(), _float_env(), _int_env(), _output_dir(), fixture (+41 more)

### Community 37 - "Community 37"
Cohesion: 0.08
Nodes (40): OpeningCatalogueItemResponse, TrainingRequirementResponse, calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName() (+32 more)

### Community 38 - "Community 38"
Cohesion: 0.08
Nodes (36): AnalysisLockError, Another top-level analysis operator owns the database lock., AnalysisRunLock, BaseException, Path, Hold a one-byte lock whose lifetime is tied to an open OS file handle., InterruptController, Own the top-level lock, read selected games, then coordinate safe writes. (+28 more)

### Community 39 - "Community 39"
Cohesion: 0.09
Nodes (39): NormalizationResult, NormalizationWarning, NormalizedGame, import_normalized_games(), import_raw_month(), import_raw_months(), load_normalized_months(), normalize_raw_games() (+31 more)

### Community 40 - "Community 40"
Cohesion: 0.07
Nodes (45): getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getPositionInsight(), getPositionTrainingRequirements(), getPreferredMoves() (+37 more)

### Community 41 - "Community 41"
Cohesion: 0.10
Nodes (39): OpeningCatalogueSort, _compare(), _load_labels(), _load_usage(), _matches(), _normalize_eco_bound(), OpeningCatalogueEntry, OpeningCatalogueError (+31 more)

### Community 42 - "Community 42"
Cohesion: 0.10
Nodes (39): _canonical(), inspect(), AnalysisRepository, Connection, Path, Read and fully validate a persisted result; never computes., Return eligibility, persisted result, and queue state without computing., Perform one deliberate Analyze, Update, or Retry action. (+31 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (37): LineLibrary(), nodeName(), sameIds(), selectionDescription(), booleanFilterData, data, LineLibraryTree(), LineLibraryTreeProps (+29 more)

### Community 44 - "Community 44"
Cohesion: 0.08
Nodes (34): Game acquisition, persistence, reading, and public search services., GameDetail, GameDetailOccurrence, GameOccurrenceRead, GameRead, GameReadError, GameReadRepository, _materialize_game() (+26 more)

### Community 45 - "Community 45"
Cohesion: 0.11
Nodes (36): Validated canonical chess-position identity services., ValueError, Raised when a policy or discovery request is invalid., Immutable scoring inputs supplied by application configuration., TrainingRequirementPolicy, TrainingRequirementValidationError, Public training-requirement composition shim., _coerce_date() (+28 more)

### Community 46 - "Community 46"
Cohesion: 0.11
Nodes (38): _canonical_fen(), _clock_date(), _eligible_evidence(), _is_lock_failure(), _load_current_aggregate(), BaseException, date, Atomic backend-judged training-answer submission. (+30 more)

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (37): api_context(), client(), count_reader_calls(), create_cache_database(), _isolated_caches(), fixture, MonkeyPatch, Path (+29 more)

### Community 48 - "Community 48"
Cohesion: 0.08
Nodes (36): getOpenings(), getOpeningsOptions(), OpeningCatalogueResponse, TrainingRequirementItemResponse, abortError(), buildTrainingRequirementsQuery(), currentUtcDate(), defaultTrainerPracticeApi (+28 more)

### Community 49 - "Community 49"
Cohesion: 0.10
Nodes (33): createMoveHistoryRows(), KEY_NAVIGATION, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow, Constrained (+25 more)

### Community 50 - "Community 50"
Cohesion: 0.09
Nodes (35): acquire_incremental_months(), acquire_months(), AcquisitionClock, AcquisitionError, AcquisitionFailure, AcquisitionResult, _archive_url(), ArchiveMonth (+27 more)

### Community 51 - "Community 51"
Cohesion: 0.09
Nodes (39): _current_signature(), json_response(), opening_detail_key(), openings_catalogue_version(), openings_key(), Path, Return a bounded opaque version for the database and SQLite sidecars., Serialize one response model exactly like Starlette's JSONResponse. (+31 more)

### Community 52 - "Community 52"
Cohesion: 0.09
Nodes (34): _configured_float(), Application dependencies for database capabilities., api_context(), client(), _complete_analysis_result(), fixture, MonkeyPatch, Path (+26 more)

### Community 53 - "Community 53"
Cohesion: 0.08
Nodes (35): ButtonProps, actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave (+27 more)

### Community 54 - "Community 54"
Cohesion: 0.07
Nodes (30): Docs, meta, Story, Docs, meta, Story, CatalogueLink, CatalogueSection (+22 more)

### Community 55 - "Community 55"
Cohesion: 0.07
Nodes (37): LineLibraryProps, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+29 more)

### Community 56 - "Community 56"
Cohesion: 0.11
Nodes (36): clear_caches(), Drop every cached payload and advance the generation. This is the sanctioned…, Canonical key from the validated query, resolved database, and policy., training_requirements_key(), get_training_requirement_policy(), Return the configured policy, or ``None`` when the capability is unavailable., ContractModel, MutationRequestModel (+28 more)

### Community 57 - "Community 57"
Cohesion: 0.12
Nodes (35): AnalysisSchemaError, RuntimeError, The independently versioned analysis schema is absent or incompatible., _existing_tables(), migrate_position_key_schema(), Connection, Explicit initialization for the independent analysis schema., Validate the v1 shape accepted by the one-time position-key transition. (+27 more)

### Community 58 - "Community 58"
Cohesion: 0.07
Nodes (23): _EventLoopTransportStub, FakeProcess, managed(), Board, Limit, parametrize, Minimal asyncio.SubprocessTransport-shaped stub with a mutable return code., Real asyncio event that fails loudly if lifecycle code ever awaits it. (+15 more)

### Community 59 - "Community 59"
Cohesion: 0.12
Nodes (31): _materialize_timeline(), PreferredMoveTimeline, PreferredMoveTimelineRepository, PreferredMoveTimelineRequest, Path, A complete exact-cover timeline for one finite request window., Return the strict timeline start date., Return the strict timeline end date. (+23 more)

### Community 60 - "Community 60"
Cohesion: 0.11
Nodes (29): AnalysisCandidate, AnalysisResult, canonical_fen(), Return the internal identity without changing the public six-field FEN., Return a strict canonical six-field FEN or reject it., initialize_analysis_schema(), Create the analysis namespace only through this explicit operation., candidate() (+21 more)

### Community 61 - "Community 61"
Cohesion: 0.08
Nodes (27): position_transaction(), PositionRepository, Path, Canonicalize and persist one complete FEN in an owned transaction., Open one opaque package-owned transaction for grouped position work., Resolve canonical positions using package-owned connections and transactions., Canonicalize and persist one board in an owned transaction., Path (+19 more)

### Community 62 - "Community 62"
Cohesion: 0.10
Nodes (32): create_schema(), _execute_schema_resource(), _execute_schema_statement(), _is_truly_empty(), Connection, Path, RuntimeError, Ordinary data describing one schema creation request. (+24 more)

### Community 63 - "Community 63"
Cohesion: 0.11
Nodes (26): failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isNonnegativeInteger(), isRecord(), JsonRecord, legalMoveFromUci() (+18 more)

### Community 64 - "Community 64"
Cohesion: 0.13
Nodes (30): _finite_number(), GamesConfigurationError, ImportConfiguration, load_acquire_configuration(), load_import_configuration(), _load_yaml_mapping(), Any, Path (+22 more)

### Community 65 - "Community 65"
Cohesion: 0.08
Nodes (25): _analysis_result(), BulkError, BulkFailure, BulkInputError, BulkOutcome, _prepend(), Any, Path (+17 more)

### Community 66 - "Community 66"
Cohesion: 0.09
Nodes (21): MoveResponseDistribution(), MoveResponseDistributionPanel, ChartLabel, here, rawStyles, MoveResponseDistributionReply, MoveResponseDistributionResponse, MoveResponseDistributionControls() (+13 more)

### Community 67 - "Community 67"
Cohesion: 0.13
Nodes (24): get_or_compute(), _Inflight, Process-local cache for safe repeated backend reads. Two bounded…, Record the current signature; on change for a known path, clear all and return…, Return the cached payload or compute it once per key. ``compute`` runs outside…, Single-flight state for one cache key being computed., One bounded TTL namespace with its own single-flight table., _refresh_signature_locked() (+16 more)

### Community 68 - "Community 68"
Cohesion: 0.12
Nodes (28): api_context(), client(), create_insight_database(), _game(), _install_analysis(), _install_opening(), _install_preferences(), _occurrence() (+20 more)

### Community 69 - "Community 69"
Cohesion: 0.11
Nodes (28): AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis(), invalidFenResult(), isCanonicalFen(), isFailureCode() (+20 more)

### Community 70 - "Community 70"
Cohesion: 0.13
Nodes (30): _database_sidecars(), _failure(), LifecycleOperation, _path_exists(), Enum, OSError, Path, RuntimeError (+22 more)

### Community 71 - "Community 71"
Cohesion: 0.12
Nodes (24): failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord, narrowInsightResponse(), PositionContextClient (+16 more)

### Community 72 - "Community 72"
Cohesion: 0.10
Nodes (27): MeasurementDecision, _bulk_page_parameters(), collect_direct_measurements(), _measurement_corpus(), _measurement_decision(), _measurement_inputs(), _MeasurementInputs, _median() (+19 more)

### Community 73 - "Community 73"
Cohesion: 0.14
Nodes (18): _counts(), FixedClock, _game_fixture(), GameTransport, OpeningTransport, Any, datetime, MonkeyPatch (+10 more)

### Community 74 - "Community 74"
Cohesion: 0.14
Nodes (29): games_key(), Canonical key from the validated games query and resolved database., GameCoverageResponse, GameDetailOccurrenceResponse, GameDetailResponse, GamesErrorResponse, GamesModel, GamesResponse (+21 more)

### Community 75 - "Community 75"
Cohesion: 0.07
Nodes (28): engines, node, name, private, type, version, @base-ui/react, eslint (+20 more)

### Community 76 - "Community 76"
Cohesion: 0.12
Nodes (21): AnalysisLine, AnalysisObservation, analysisPanelDisplay(), AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv() (+13 more)

### Community 77 - "Community 77"
Cohesion: 0.19
Nodes (28): booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys(), isErrorCode(), isRecord(), JsonRecord, NODE_KEYS (+20 more)

### Community 78 - "Community 78"
Cohesion: 0.15
Nodes (27): _parse_pgn_input(), _consume_header(), _ErrorCollectingGameBuilder, load_opening_sources(), OpeningSourceError, Exception, Path, ValueError (+19 more)

### Community 79 - "Community 79"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 80 - "Community 80"
Cohesion: 0.09
Nodes (24): mapGameDetailResponse(), sanFromFenAndUci(), PositionPickerMoveRecord, SelectedTransition, PreferredMoveResponse, PreferredMoveValue, D4_MOVE, D4_STAGED_MOVE (+16 more)

### Community 81 - "Community 81"
Cohesion: 0.10
Nodes (22): PositionContextResponse, PositionReachFrequency(), PositionReachFrequencyProps, BasePositionReachFrequencyModel, boundedPercentage(), colorLabel(), derivePositionReachFrequencyModel(), percentageLabel() (+14 more)

### Community 82 - "Community 82"
Cohesion: 0.11
Nodes (26): contextFailureMessage(), failureMessage(), mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), PreferredMovePanelProps, statusLabel(), here (+18 more)

### Community 83 - "Community 83"
Cohesion: 0.18
Nodes (22): import_raw_games(), Normalize first, then commit accepted games independently in source order., GameRepository, Path, Persist complete normalized games without exposing database handles., _count(), _game_snapshot(), MonkeyPatch (+14 more)

### Community 84 - "Community 84"
Cohesion: 0.07
Nodes (29): devDependencies, @axe-core/playwright, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts (+21 more)

### Community 85 - "Community 85"
Cohesion: 0.13
Nodes (26): strictFen(), GAME, GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession() (+18 more)

### Community 86 - "Community 86"
Cohesion: 0.11
Nodes (24): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+16 more)

### Community 87 - "Community 87"
Cohesion: 0.17
Nodes (26): checkA11y(), DistributionLabelBox, expectActiveSessionHistoryEntry(), expectBothRelationshipBoxes(), expectDateFreePreferredPanel(), expectDistributionChartAndControlsClean(), expectNoHorizontalOverflow(), expectPanelMinimums() (+18 more)

### Community 88 - "Community 88"
Cohesion: 0.22
Nodes (24): api_context(), create_openings_database(), fixture, MonkeyPatch, Path, TestClient, _create_encoded_key_database(), _create_rebuilt_database() (+16 more)

### Community 89 - "Community 89"
Cohesion: 0.10
Nodes (21): clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), panelSpaceForGroup(), panelSpaceForStage(), RepertoireResponsiveStage() (+13 more)

### Community 90 - "Community 90"
Cohesion: 0.13
Nodes (18): ArtifactWriter, AtomicArtifactWriter, _bounded_message(), _is_transient_artifact_error(), _is_within(), _normalized_directory(), _normalized_file_path(), Any (+10 more)

### Community 91 - "Community 91"
Cohesion: 0.21
Nodes (24): _StoredAttempts, Benchmark loading and top-level invocation., BenchmarkCompatibilityError, BenchmarkJob, A stable identity for one position/profile/round analysis., Existing output state does not belong to the requested benchmark., _checkpoint_payload(), _current_job_sets() (+16 more)

### Community 92 - "Community 92"
Cohesion: 0.12
Nodes (25): api_context(), client(), create_training_database(), _game(), _occurrence(), Connection, fixture, MonkeyPatch (+17 more)

### Community 93 - "Community 93"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 94 - "Community 94"
Cohesion: 0.15
Nodes (25): Headers, _end_timestamp(), _format_utc(), GameNormalizationError, GameOccurrence, _header_timestamp(), _informative_termination(), _normalize_game() (+17 more)

### Community 95 - "Community 95"
Cohesion: 0.11
Nodes (21): LookupError, Raised when the requested current training pair does not exist., TrainingAnswerNotFoundError, Exception, RuntimeError, Base class for bounded training-requirement failures., One globally scored canonical-position/preferred-move pair., Return the compact adapter-ready shape with six-decimal derived numbers. (+13 more)

### Community 96 - "Community 96"
Cohesion: 0.15
Nodes (23): buildUrl(), createQuerySerializer(), defaultHeaders, defaultQuerySerializer, ErrInterceptor, ReqInterceptor, ResInterceptor, ArraySeparatorStyle (+15 more)

### Community 97 - "Community 97"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 98 - "Community 98"
Cohesion: 0.25
Nodes (24): GameSearchQuery, All approved collection filters and pagination controls., GameSearchRepository, Path, Search normalized games using one explicit read-only schema-v1 path., _add_coverage(), _database(), _install_openings() (+16 more)

### Community 99 - "Community 99"
Cohesion: 0.24
Nodes (25): Validated read-only discovery controls., TrainingRequirementQuery, discover_training_requirements(), Discover scored requirements from one explicit existing database., _add_black_training_item(), _fixture(), _game(), _item() (+17 more)

### Community 100 - "Community 100"
Cohesion: 0.37
Nodes (22): _archive_url(), _config(), FixedClock, _fixture(), _month_url(), Any, datetime, Path (+14 more)

### Community 101 - "Community 101"
Cohesion: 0.10
Nodes (13): Immediately terminate this tracked child for the second Ctrl+C level., AnalysisEngine, _close_engine(), _EngineRegistry, EngineFactory, Protocol, _close_engine(), _EngineRegistry (+5 more)

### Community 102 - "Community 102"
Cohesion: 0.09
Nodes (20): BoardAdapter(), BoardAdapterProps, BoardRender(), PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition (+12 more)

### Community 103 - "Community 103"
Cohesion: 0.16
Nodes (22): _atomic_replace(), publish_month(), Path, RuntimeError, Validation, merge, and atomic publication for raw Chess.com month files., Raised when a raw month cannot be validated or published safely., Return games when candidate passes the exact object/list/unique-UUID gate., Validate fully, then publish through a flushed same-directory temporary file. (+14 more)

### Community 104 - "Community 104"
Cohesion: 0.13
Nodes (15): CataloguePublication, OpeningCatalogueRepository, OpeningPersistenceError, _prepare_routes(), Path, RuntimeError, Raised when a compatible database cannot publish the opening catalogue., Immutable counts describing one successfully committed catalogue replacement. (+7 more)

### Community 105 - "Community 105"
Cohesion: 0.23
Nodes (16): _FakeEngine, _FakeFactory, _InjectedWriter, Any, Path, _runner(), _small_spec(), test_default_matrix_is_exact_and_deterministically_shuffled() (+8 more)

### Community 106 - "Community 106"
Cohesion: 0.13
Nodes (21): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+13 more)

### Community 107 - "Community 107"
Cohesion: 0.28
Nodes (19): client(), _database(), fixture, MonkeyPatch, parametrize, Path, TestClient, test_browsing_list_does_not_modify_database() (+11 more)

### Community 108 - "Community 108"
Cohesion: 0.16
Nodes (19): BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys, Options (+11 more)

### Community 109 - "Community 109"
Cohesion: 0.13
Nodes (17): clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart(), renderLabel() (+9 more)

### Community 110 - "Community 110"
Cohesion: 0.17
Nodes (18): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+10 more)

### Community 111 - "Community 111"
Cohesion: 0.26
Nodes (19): Judge and persist one answer in an existing compatible database., TrainingAnswerRepository, _balance(), _fixture(), _game(), _occurrence(), Connection, parametrize (+11 more)

### Community 112 - "Community 112"
Cohesion: 0.15
Nodes (14): isChessSide(), validateMoveResponseDistributionColor(), requestPositionInsight(), validatePositionContextFen(), currentUtcDate(), isValidRawInsight(), POSITION_INSIGHT_GC_TIME, POSITION_INSIGHT_STALE_TIME (+6 more)

### Community 113 - "Community 113"
Cohesion: 0.15
Nodes (9): @playwright/test, checkA11y(), STORY_IDS, isAxeBusyError(), retryAxeWhenBusy(), waitForStorybookRender(), assertFixtureStates(), checkA11y() (+1 more)

### Community 114 - "Community 114"
Cohesion: 0.27
Nodes (19): OpeningCatalogueRepository, Path, Browse normalized openings without exposing a database connection., Read one exact public opening key from an explicit database path., read_opening(), _keys(), _make_database(), parametrize (+11 more)

### Community 115 - "Community 115"
Cohesion: 0.10
Nodes (4): _FakeProcess, _FakeStdin, _FakeStdout, Any

### Community 116 - "Community 116"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 117 - "Community 117"
Cohesion: 0.15
Nodes (18): actionLabel(), formatDay(), formatRange(), oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction, PreferredMoveSchedulePeriod, PreferredMoveSchedulePrototype() (+10 more)

### Community 118 - "Community 118"
Cohesion: 0.26
Nodes (17): Path, Request one desired analysis through an explicit app database path., request_analysis(), _database(), _position_with_result(), Path, _queue_row(), test_concurrent_mixed_quality_requests_create_one_position_and_queue_row() (+9 more)

### Community 119 - "Community 119"
Cohesion: 0.25
Nodes (15): _catalogue_snapshot(), MonkeyPatch, Path, _rows(), _source_dir(), test_deletion_checkpoint_order_is_child_first(), test_existing_endpoint_is_reused_and_unrelated_position_survives_replacement(), test_first_publication_writes_labels_routes_and_contiguous_children() (+7 more)

### Community 120 - "Community 120"
Cohesion: 0.22
Nodes (13): _database(), _FakeEngine, _FakeMutex, Path, _RecordingPublisher, _runner(), test_ctrl_c_discards_only_current_result_and_releases_bulk_mutex(), test_direct_tool_profile_is_used_for_every_serial_engine_call() (+5 more)

### Community 121 - "Community 121"
Cohesion: 0.15
Nodes (12): EvalBar(), EvalBarDisplayState, EvalBarProps, ExpectedDisplay, BoardEvalStage(), boardVisualIn(), BoardFixture(), display() (+4 more)

### Community 122 - "Community 122"
Cohesion: 0.13
Nodes (13): Button(), ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story, VariantMatrix (+5 more)

### Community 123 - "Community 123"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 124 - "Community 124"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 125 - "Community 125"
Cohesion: 0.26
Nodes (15): GameSearchValidationError, ValueError, Game search error types., Raised when a game-search query is invalid., Game search query models., _normalize_fen(), _normalize_timestamp(), _parse_opening_key() (+7 more)

### Community 126 - "Community 126"
Cohesion: 0.30
Nodes (6): _ArtifactPaths, BenchmarkRunner, Any, BaseException, Path, Run and resume one deterministic benchmark matrix.

### Community 127 - "Community 127"
Cohesion: 0.25
Nodes (15): BulkTargetSelector, Path, Read stable bounded pages and never persist a target list., _add_game_occurrences(), _add_route(), _database(), _position_ids(), MonkeyPatch (+7 more)

### Community 128 - "Community 128"
Cohesion: 0.13
Nodes (15): BoardControl(), BoardControlProps, BoardEvalStageProps, InteractiveBoardAdapterProps, BoardContentProps, HistoryProps, RepertoireBoardLane(), RepertoireBoardLaneProps (+7 more)

### Community 129 - "Community 129"
Cohesion: 0.25
Nodes (16): normalize_game(), Return a fully validated game, or one ordinary warning for a skipped input., _fixture(), parametrize, test_draw_mapping_and_pgn_termination_fallback(), test_ineligible_malformed_and_illegal_inputs_are_ordinary_skips(), test_invalid_required_raw_fields_are_skipped(), test_non_unique_trainer_and_non_normal_start_are_skipped() (+8 more)

### Community 130 - "Community 130"
Cohesion: 0.28
Nodes (14): _count(), FixedClock, _fixture(), _game_url(), _month_url(), Any, datetime, Path (+6 more)

### Community 131 - "Community 131"
Cohesion: 0.19
Nodes (12): MonkeyPatch, parametrize, Path, _queue(), _remove_result(), _target_position_id(), test_injected_database_is_used_when_configured(), test_missing_or_bad_position_gives_clear_error() (+4 more)

### Community 132 - "Community 132"
Cohesion: 0.12
Nodes (17): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+9 more)

### Community 133 - "Community 133"
Cohesion: 0.20
Nodes (13): collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue(), sourceRoot, statusTagByRoot (+5 more)

### Community 134 - "Community 134"
Cohesion: 0.32
Nodes (16): Replay one standard-start PGN and recognize reached opening endpoints., replay_pgn(), _database_rows(), _publish(), parametrize, Path, _repository(), _summary() (+8 more)

### Community 135 - "Community 135"
Cohesion: 0.16
Nodes (14): BenchmarkError, BenchmarkInputError, BenchmarkInterrupted, BenchmarkPersistenceError, BenchmarkPosition, _positive_int_tuple(), RuntimeError, ValueError (+6 more)

### Community 136 - "Community 136"
Cohesion: 0.26
Nodes (13): _normalized(), MonkeyPatch, parametrize, Path, _raw(), _rows(), test_correction_failure_at_each_boundary_preserves_prior_game(), test_fresh_game_persists_exact_metadata_positions_and_occurrences() (+5 more)

### Community 137 - "Community 137"
Cohesion: 0.27
Nodes (15): BaseException, parametrize, Path, repository(), test_boundary_requires_exactly_four_valid_fen_fields(), test_failed_replacement_restores_the_preexisting_schedule(), test_failure_or_interruption_rolls_back_standalone_position_and_period(), checkpoint() (+7 more)

### Community 138 - "Community 138"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 139 - "Community 139"
Cohesion: 0.12
Nodes (11): Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth, ForcedColorsAndReducedMotion, meta, PositiveBlack (+3 more)

### Community 140 - "Community 140"
Cohesion: 0.29
Nodes (14): Path, Read one FEN observation from an explicit app database path., read_analysis_observation(), _database(), parametrize, Path, _queue(), _result() (+6 more)

### Community 141 - "Community 141"
Cohesion: 0.37
Nodes (15): _line(), _position(), AnalysisLine, AnalysisTerminalKind, parametrize, _result(), _starting_lines(), test_candidate_root_moves_must_be_distinct_and_legal() (+7 more)

### Community 142 - "Community 142"
Cohesion: 0.19
Nodes (9): _common_fens(), _database(), _FakeEngine, _FakeMutex, Path, test_initial_analysis_is_serial_resumable_direct_and_queue_free(), engine_factory(), mutex_factory() (+1 more)

### Community 143 - "Community 143"
Cohesion: 0.15
Nodes (5): Path, _python_sources(), test_canonical_sql_is_the_only_executable_ddl_owner_and_cli_is_thin(), test_database_package_has_no_legacy_or_production_import_direction(), test_package_contains_no_runtime_wrapper_or_copied_legacy_generator()

### Community 144 - "Community 144"
Cohesion: 0.26
Nodes (12): _catalogue_snapshot(), _copy_sources(), _fixture_game(), _game_snapshot(), _latest_files(), OpeningTransport, BaseException, parametrize (+4 more)

### Community 145 - "Community 145"
Cohesion: 0.22
Nodes (14): createClient(), TODO: we probably want to return error and improve types, ReqInit, checkForExistence(), createConfig(), createInterceptors(), getParseAs(), headersEntries() (+6 more)

### Community 146 - "Community 146"
Cohesion: 0.16
Nodes (11): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelIntent, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue, InlineWdl(), resultMetadataLabel() (+3 more)

### Community 147 - "Community 147"
Cohesion: 0.17
Nodes (12): AnalysisPanelDisplay, AnalysisPanelLine, AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides (+4 more)

### Community 148 - "Community 148"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 149 - "Community 149"
Cohesion: 0.15
Nodes (12): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+4 more)

### Community 150 - "Community 150"
Cohesion: 0.16
Nodes (14): OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFailure, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType, OpeningLineLibraryGroupNode, OpeningLineLibraryLineNode (+6 more)

### Community 151 - "Community 151"
Cohesion: 0.25
Nodes (13): Upgrade one existing exact v1 database to v2, or leave exact v2 unchanged., Ordinary data describing one explicit schema upgrade request., SchemaUpgradeResult, upgrade_schema(), _create_v1_database(), _data_snapshot(), MonkeyPatch, parametrize (+5 more)

### Community 152 - "Community 152"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 153 - "Community 153"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 154 - "Community 154"
Cohesion: 0.21
Nodes (9): _finite_number(), _normalize_range(), parse_calendar_date(), _parse_date(), date, Validated models for read-only position training requirements., Parse one strict calendar-date value for scoring and storage checks., A normalized inclusive/exclusive requirement range. (+1 more)

### Community 155 - "Community 155"
Cohesion: 0.24
Nodes (11): Auth, AuthToken, BodySerializer, QuerySerializer, QuerySerializerOptions, Client, ClientMeta, Config (+3 more)

### Community 156 - "Community 156"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 157 - "Community 157"
Cohesion: 0.15
Nodes (12): devDependencies, @axe-core/playwright, @mermaid-js/mermaid-cli, @playwright/test, engines, node, @axe-core/playwright, name (+4 more)

### Community 158 - "Community 158"
Cohesion: 0.29
Nodes (12): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+4 more)

### Community 159 - "Community 159"
Cohesion: 0.26
Nodes (12): count_lines(), is_excluded(), is_test_file(), main(), print_report(), Path, Count lines in a file, tolerating unusual characters., Walk the repo and measure every script file. Returns one row per file. (+4 more)

### Community 160 - "Community 160"
Cohesion: 0.27
Nodes (10): CliRunner, Exception, MonkeyPatch, parametrize, _runner(), test_preferred_moves_setup_forwards_fixed_path_without_reading_prompt(), setup(), test_preferred_moves_setup_help_registers_exact_command_without_options() (+2 more)

### Community 161 - "Community 161"
Cohesion: 0.17
Nodes (10): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+2 more)

### Community 162 - "Community 162"
Cohesion: 0.21
Nodes (8): Combobox(), ALL_OPENINGS_VALUE, filterOpeningCatalogue(), OPENING_SEARCH_VISIBLE_LIMIT, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, searchText()

### Community 163 - "Community 163"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 164 - "Community 164"
Cohesion: 0.32
Nodes (11): datasource_game, datasource_opening, datasource_preferred_move_period, derived_analysis_line, derived_analysis_queue, derived_analysis_result, derived_game_position, derived_game_position_position_idx (+3 more)

### Community 165 - "Community 165"
Cohesion: 0.18
Nodes (6): fulfillJson(), mockCatalogue(), OPENING_ITEMS, TRAINING_ERROR, TRAINING_ITEM, TRAINING_RESPONSE_BASE

### Community 166 - "Community 166"
Cohesion: 0.20
Nodes (8): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent

### Community 167 - "Community 167"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 168 - "Community 168"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 169 - "Community 169"
Cohesion: 0.22
Nodes (7): Path, The backend judgment and the newly scored training item., Return the resulting scored item using an explicit adapter-friendly name., Submit one validated answer against one explicit existing database., submit_training_answer(), TrainingAnswerResult, UtcCalendarDateClock

### Community 170 - "Community 170"
Cohesion: 0.20
Nodes (6): DirectProof, Read-only aggregate facts suitable for bounded direct evidence., Whether the retained canonical preference table is empty., Whether the fixed database exposes exactly the catalogue's ten tables., Whether every stored game has a complete ordered occurrence set., Whether every stored route has contiguous one-based move plies.

### Community 171 - "Community 171"
Cohesion: 0.24
Nodes (6): checkA11y(), expectDescriptionAssociation(), expectStaticGraphic(), expectValidSurface(), RICH_SPOKEN_DESCRIPTION, STORY_IDS

### Community 172 - "Community 172"
Cohesion: 0.22
Nodes (6): formDataBodySerializer, jsonBodySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArrayStyle, ObjectStyle

### Community 173 - "Community 173"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 174 - "Community 174"
Cohesion: 0.25
Nodes (8): load_positions(), Any, Path, Load and structurally validate explicit JSON benchmark positions., Run one explicit matrix, resuming only compatible output state., run_benchmark(), BenchmarkOutcome, Observable result of one bounded benchmark invocation.

### Community 175 - "Community 175"
Cohesion: 0.25
Nodes (4): expectApplicationAxeClean(), openStory(), STORY_IDS, storyUrl()

### Community 176 - "Community 176"
Cohesion: 0.25
Nodes (4): One immutable, result-affecting Stockfish search profile., Return the UCI options applied before a search., Return the complete normalized settings stored with an analysis., StockfishProfile

### Community 177 - "Community 177"
Cohesion: 0.29
Nodes (7): APP_TEST_FILES, appWebServers, profile, selectedTestFiles(), serverProfile(), STORYBOOK_TEST_FILES, storybookWebServer

### Community 178 - "Community 178"
Cohesion: 0.38
Nodes (5): health(), get, HealthResponse, BaseModel, HealthResponse

### Community 179 - "Community 179"
Cohesion: 0.29
Nodes (6): engines, node, name, private, type, version

### Community 181 - "Community 181"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 182 - "Community 182"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 183 - "Community 183"
Cohesion: 0.29
Nodes (4): HealthyContent, meta, Story, UnexpectedFailureTryAgain

### Community 184 - "Community 184"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 185 - "Community 185"
Cohesion: 0.29
Nodes (4): BenchmarkSpec, Any, Validated, deterministic matrix inputs for one benchmark run., Enumerate every job once in the recorded deterministic order.

### Community 186 - "Community 186"
Cohesion: 0.62
Nodes (6): _assert_same_key_set(), _assert_same_mapping(), _database(), Path, test_real_direct_database_capabilities(), test_real_direct_database_matches_the_retained_source_ledger()

### Community 187 - "Community 187"
Cohesion: 0.29
Nodes (4): parametrize, test_lifecycle_adapter_rejects_a_service_destination_override(), test_lifecycle_adapters_forward_fixed_path_service_results(), test_lifecycle_adapters_preserve_service_exit_mapping()

### Community 188 - "Community 188"
Cohesion: 0.33
Nodes (4): dirname, vite, @vitejs/plugin-react, @vitest/browser-playwright

### Community 189 - "Community 189"
Cohesion: 0.33
Nodes (4): MoveResponseDistribution, Occurrence and outgoing-move counts with actor derived at read time., Return occurrences that have an outgoing move., Return the separately reported final-occurrence count.

### Community 190 - "Community 190"
Cohesion: 0.53
Nodes (5): CompletedProcess, Path, _run(), _smoke_arguments(), test_one_position_real_benchmark_is_contained_and_completed_run_is_noop()

### Community 191 - "Community 191"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 192 - "Community 192"
Cohesion: 0.50
Nodes (5): parse_month_selection(), Parse an exact zero-padded YYYY-MM calendar month selection., parametrize, test_month_selection_parses_only_exact_zero_padded_calendar_months(), test_month_selection_rejects_malformed_or_invalid_months()

### Community 193 - "Community 193"
Cohesion: 0.70
Nodes (4): _create_v1_database(), Path, test_schema_upgrade_cli_does_not_create_a_missing_target(), test_schema_upgrade_cli_is_explicit_and_existing_only()

### Community 194 - "Community 194"
Cohesion: 0.80
Nodes (4): _database_with_synthetic_occurrences(), Path, test_move_response_distribution_separates_trainer_and_opponent(), test_position_context_counts_distinct_games_and_test_actor()

### Community 197 - "Community 197"
Cohesion: 0.50
Nodes (3): client, CreateClientConfig, ClientOptions

### Community 198 - "Community 198"
Cohesion: 0.83
Nodes (3): execute(), globFiles(), resolveRg()

### Community 200 - "Community 200"
Cohesion: 0.50
Nodes (3): PositionContext, Distinct-game context for one canonical position., Return the distinct game count under the selected color filter.

## Knowledge Gaps
- **879 isolated node(s):** `BoardSquareHighlight`, `InteractiveBoardHarnessProps`, `PromotionController`, `PromotionControllerOptions`, `PromotionPickerProps` (+874 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2339 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PositionKey` connect `Community 5` to `Community 12`, `Community 69`?**
  _High betweenness centrality (0.448) - this node is a cross-community bridge._
- **Why does `position_key_from_fen()` connect `Community 12` to `Community 42`, `Community 60`, `Community 5`, `Community 38`?**
  _High betweenness centrality (0.436) - this node is a cross-community bridge._
- **Why does `react` connect `Community 34` to `Community 3`, `Community 6`, `Community 10`, `Community 138`, `Community 139`, `Community 15`, `Community 17`, `Community 147`, `Community 148`, `Community 21`, `Community 20`, `Community 24`, `Community 152`, `Community 162`, `Community 37`, `Community 166`, `Community 43`, `Community 173`, `Community 49`, `Community 53`, `Community 54`, `Community 183`, `Community 55`, `Community 63`, `Community 66`, `Community 71`, `Community 75`, `Community 79`, `Community 81`, `Community 82`, `Community 86`, `Community 89`, `Community 102`, `Community 109`, `Community 117`, `Community 121`, `Community 122`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 63 inferred relationships involving `create_schema()` (e.g. with `create_benchmark_database()` and `create_cache_database()`) actually correct?**
  _`create_schema()` has 63 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `SchemaIncompatibleError` (e.g. with `get_game()` and `AnalysisObservationRepository`) actually correct?**
  _`SchemaIncompatibleError` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `canonicalize_fen()` (e.g. with `CanonicalPosition` and `_position()`) actually correct?**
  _`canonicalize_fen()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `BoardSquareHighlight`, `InteractiveBoardHarnessProps`, `PromotionController` to the rest of the system?**
  _879 weakly-connected nodes found - possible documentation gaps or missing edges._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
