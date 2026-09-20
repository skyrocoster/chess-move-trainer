# Graph Report - frontend  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2507 nodes · 5421 edges · 121 communities (115 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 83 edges (avg confidence: 0.85)
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

## God Nodes (most connected - your core abstractions)
1. `react` - 85 edges
2. `vitest` - 78 edges
3. `@storybook/react-vite` - 58 edges
4. `@testing-library/react` - 49 edges
5. `RepertoireBuilderWorkspace()` - 36 edges
6. `storybook` - 35 edges
7. `chess.js` - 27 edges
8. `Fen` - 23 edges
9. `positionKeyFromFen()` - 23 edges
10. `@testing-library/user-event` - 22 edges

## Surprising Connections (you probably didn't know these)
- `StorybookQueryClientProvider()` --indirect_call--> `createTestQueryClient()`  [INFERRED]
  .storybook/StorybookQueryClientProvider.tsx → src/test-utils/QueryClientTestProvider.tsx
- `handleKeyDown()` --indirect_call--> `model()`  [INFERRED]
  src/features/move-history/MoveHistory.tsx → src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx
- `PreferredMoveDateValue()` --calls--> `formatUtcDate()`  [EXTRACTED]
  src/features/repertoire-builder/PreferredMovePrimitives.tsx → src/features/design-system/CalendarDateUtils.ts
- `TrainerPracticePage()` --indirect_call--> `readOpeningCatalogueSnapshot()`  [INFERRED]
  src/features/trainer-practice/TrainerPracticePage.tsx → src/features/trainer-practice/openingCatalogueStorage.ts
- `normalizePositionKey()` --calls--> `positionKeyFromFen()`  [EXTRACTED]
  src/api/queryKeys.ts → src/features/chess/chessPrimitives.ts

## Import Cycles
- None detected.

## Communities (121 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (117): src_api_generated_index_analysisobservationerrorresponse, src_api_generated_index_analysisobservationlineresponse, src_api_generated_index_analysisobservationresponse, src_api_generated_index_analysisobservationresultresponse, src_api_generated_index_analysisrequestbody, src_api_generated_index_analysisrequesterrorresponse, src_api_generated_index_deletepreferredmoves, src_api_generated_index_deletepreferredmovesdata (+109 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (79): src_features_design_system_line_library_linelibrary_linelibraryprops, LineLibraryFilterKind, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult (+71 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (69): @headless-tree/core, @headless-tree/react, LineLibrary(), nodeName(), sameIds(), selectionDescription(), Default, Empty (+61 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (58): AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse, ClientOptions, DeletePreferredMovesError (+50 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (57): client, getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight() (+49 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (46): src_api_client_deletepreferredmoves, src_api_client_getpreferredmoves, src_api_client_preferredmovesmutationresponse, src_api_client_preferredmovesremovalresponse, src_api_client_preferredmovesresponse, src_api_client_preferredmovessegmentresponse, src_api_client_putpreferredmoves, deletePreferredMove() (+38 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (40): react-chessboard, clearPending(), isPromotionCandidate(), isPromotionTarget(), PendingPromotion, PickerLiveRegion(), PROMOTION_OPTIONS, PromotionColor (+32 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (31): @storybook/react-vite, src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story (+23 more)

### Community 8 - "Community 8"
Cohesion: 0.10
Nodes (31): src_api_client_getanalysis, src_api_client_requestanalysis, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis(), invalidFenResult() (+23 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (29): CreateClientConfig, BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys (+21 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (22): src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, ChartLabel, here, rawStyles, MoveResponseDistributionReply, MoveResponseDistributionResponse (+14 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (33): deletePreferredMoves(), putPreferredMoves(), requestAnalysis(), submitPositionTrainingAnswer(), DeletePreferredMovesData, DeletePreferredMovesErrors, DeletePreferredMovesResponses, GetAnalysisErrors (+25 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (25): src_api_client_getpositioninsight, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord, narrowInsightResponse() (+17 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (27): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+19 more)

### Community 14 - "Community 14"
Cohesion: 0.14
Nodes (24): chess.js, react, BoardAnswerPresentation, BranchSnapshot, InteractiveBoardHarness(), InteractiveBoardHarnessProps, terminalDescription(), deriveLastMove() (+16 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (22): src_api_client_positioninsightresponse, Fen, MoveResponseDistributionClient, MoveResponseDistributionFailureCode, MoveResponseDistributionResult, InternalState, isEmptyResponse(), MoveResponseDistributionState (+14 more)

### Community 16 - "Community 16"
Cohesion: 0.14
Nodes (20): @base-ui/react, Autocomplete(), AutocompleteProps, Combobox(), ComboboxProps, DropdownOptionContent(), DropdownOptionContentProps, Field() (+12 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (21): AnalysisLine, AnalysisObservation, analysisPanelDisplay(), AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv() (+13 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (21): @tanstack/react-query, PreferredMoveFailureCode, PreferredMoveReader, PreferredMoveResponse, PreferredMoveQueryError, PreferredMoveReadState, queryPreferredMove(), PreferredMoveOutput() (+13 more)

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (29): src_api_client_getopeningsdata, src_api_client_getpositiontrainingrequirementsdata, src_api_client_openingcatalogueresponse, src_api_client_traininganswerresponse, abortError(), buildTrainingRequirementsQuery(), defaultTrainerPracticeApi, errorCode() (+21 more)

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (24): src_api_client_openingcatalogueitemresponse, src_api_client_trainingrequirementresponse, OpeningCatalogueSnapshotResult, TrainerColor, TrainerPracticeFilters, TrainingAnswerInput, TrainingAnswerResult, TrainingRequirementsResult (+16 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (23): AnalysisOperationResult, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, AFTER_NF3_FEN, BOARD_LABEL, CONTEXT (+15 more)

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (28): expectPositionReachFrequency(), expectPositionSquares(), expectPreferredMoveState(), expectSessionBoundary(), expectSingleStagedStatus(), expectStagedStatus(), sharedPositionSummary(), verifyStandardWorkspace() (+20 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (26): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+18 more)

### Community 25 - "Community 25"
Cohesion: 0.13
Nodes (23): createQuerySerializer(), formDataBodySerializer, QuerySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArraySeparatorStyle, ArrayStyle, MatrixStyle (+15 more)

### Community 26 - "Community 26"
Cohesion: 0.09
Nodes (23): engines, node, name, private, type, version, eslint, @eslint/js (+15 more)

### Community 27 - "Community 27"
Cohesion: 0.18
Nodes (24): applySessionMove(), atIndex(), branchWithMove(), createFreshSession(), createSession(), importedPositions(), loadImportedSession(), mainLinePositions() (+16 more)

### Community 28 - "Community 28"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 29 - "Community 29"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (20): src_api_client_gamedetailresponse, src_api_client_getgame, GameLoaderStatus, GameDetailQueryError, queryGameDetail(), useGameDetailQuery(), useMoveResponseSelection(), PositionPickerSessionBoundary (+12 more)

### Community 31 - "Community 31"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (20): failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isChessSide(), isNonnegativeInteger(), isRecord(), JsonRecord (+12 more)

### Community 33 - "Community 33"
Cohesion: 0.12
Nodes (11): @chialab/vitest-axe, @testing-library/react, @testing-library/user-event, vitest, here, LoaderHarnessProps, rawStyles, fixture() (+3 more)

### Community 34 - "Community 34"
Cohesion: 0.09
Nodes (17): react-error-boundary, ConstrainedClosed, ConstrainedOpen, Healthy, Loading, meta, Story, Unavailable (+9 more)

### Community 35 - "Community 35"
Cohesion: 0.15
Nodes (22): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerStatus, BoardSquareHighlight, boardSquareStyles() (+14 more)

### Community 36 - "Community 36"
Cohesion: 0.10
Nodes (19): BoardAdapter(), BoardAdapterProps, BoardRender(), src_features_board_adapter_boardadapter_module, PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, BlackOrientation, ConstrainedWidth (+11 more)

### Community 37 - "Community 37"
Cohesion: 0.13
Nodes (22): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+14 more)

### Community 38 - "Community 38"
Cohesion: 0.09
Nodes (17): catalogueDemoShell(), AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport, OPTIONS (+9 more)

### Community 39 - "Community 39"
Cohesion: 0.16
Nodes (23): appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession(), playAndStagePositionPickerMove() (+15 more)

### Community 40 - "Community 40"
Cohesion: 0.12
Nodes (13): ref_axe_core, react-router-dom, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps, src_features_app_shell_appshell_module (+5 more)

### Community 41 - "Community 41"
Cohesion: 0.16
Nodes (22): createClient(), TODO: we probably want to return error and improve types, ReqInit, buildUrl(), checkForExistence(), createConfig(), createInterceptors(), defaultHeaders (+14 more)

### Community 42 - "Community 42"
Cohesion: 0.17
Nodes (18): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+10 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (16): Ply, San, GameLoader(), handleSubmit(), GameLoaderFailureKind, GameLoaderProps, GameLoaderValues, src_features_game_gameloader_module (+8 more)

### Community 44 - "Community 44"
Cohesion: 0.17
Nodes (19): DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR, DEFAULT_MOVE, moveFromRequest(), moveResponseData(), removalMutationResponse(), saveMutationResponse(), STORY_GAME_DETAIL, STORY_PROMOTION_GAME_DETAIL (+11 more)

### Community 45 - "Community 45"
Cohesion: 0.10
Nodes (20): AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, FirstChoice, FirstChoiceFromEmpty, Matching, meta, PendingRemove (+12 more)

### Community 46 - "Community 46"
Cohesion: 0.15
Nodes (13): invalidateAnalysisObservation(), invalidatePreferredMove(), invalidateTrainingRequirements(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput, OptionalText (+5 more)

### Community 47 - "Community 47"
Cohesion: 0.16
Nodes (12): AnalysisFailureCode, defaultAnalysisClient, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey(), AnalysisQueryError, DEFAULT_ANALYSIS_POLL_INTERVAL_MS, MAX_ANALYSIS_POLL_ATTEMPTS, PollState (+4 more)

### Community 48 - "Community 48"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 49 - "Community 49"
Cohesion: 0.13
Nodes (14): Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story (+6 more)

### Community 50 - "Community 50"
Cohesion: 0.14
Nodes (13): src_api_client_getopenings, src_api_client_submitpositiontraininganswer, src_api_client_trainingrequirementitemresponse, currentUtcDate(), isValidAsOf(), queryOpeningCatalogueSnapshot(), queryOpeningChoices(), queryTrainingRequirements() (+5 more)

### Community 51 - "Community 51"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 52 - "Community 52"
Cohesion: 0.12
Nodes (16): GAME, GAME_UUID, Game, PROMOTION_GAME, LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate (+8 more)

### Community 53 - "Community 53"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 54 - "Community 54"
Cohesion: 0.13
Nodes (14): ref_node_fs, ref_node_path, ref_node_url, @storybook/addon-vitest, @vitest/browser-playwright, src_api_client_getpositiontrainingrequirements, ContractOperation, dirname (+6 more)

### Community 55 - "Community 55"
Cohesion: 0.16
Nodes (14): recharts, clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart() (+6 more)

### Community 56 - "Community 56"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 57 - "Community 57"
Cohesion: 0.22
Nodes (15): clampMoveHistoryPly(), createMoveHistoryModel(), findMoveHistoryEntry(), MoveHistoryControlledModel, moveHistoryEntries(), MoveHistoryModel, navigateMoveHistory(), HISTORY (+7 more)

### Community 58 - "Community 58"
Cohesion: 0.20
Nodes (14): typescript, collectStoryFiles(), collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue() (+6 more)

### Community 59 - "Community 59"
Cohesion: 0.17
Nodes (12): EvalBar(), EvalBarDisplayState, EvalBarProps, ExpectedDisplay, src_features_board_adapter_boardadapter_starting_fen, BoardEvalStage(), BoardEvalStageProps, boardVisualIn() (+4 more)

### Community 60 - "Community 60"
Cohesion: 0.20
Nodes (11): ChessSide, PositionContextResponse, PositionReachFrequency(), PositionReachFrequencyProps, BasePositionReachFrequencyModel, boundedPercentage(), colorLabel(), derivePositionReachFrequencyModel() (+3 more)

### Community 61 - "Community 61"
Cohesion: 0.21
Nodes (15): contextFailureMessage(), failureMessage(), src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), statusLabel(), choiceBoxToneClass() (+7 more)

### Community 62 - "Community 62"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 63 - "Community 63"
Cohesion: 0.17
Nodes (9): src_api_client_gethealthoptions, StatusView(), StatusViewProps, StatusViewState, Healthy, Loading, meta, Story (+1 more)

### Community 64 - "Community 64"
Cohesion: 0.17
Nodes (13): sanFromFenAndUci(), SelectedTransition, PreferredMoveValue, colorLabel(), deriveRepertoirePositionModel(), PositionSaveability, PreferredMoveComparison, RepertoirePositionRelationship (+5 more)

### Community 65 - "Community 65"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 66 - "Community 66"
Cohesion: 0.12
Nodes (11): Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth, ForcedColorsAndReducedMotion, meta, PositiveBlack (+3 more)

### Community 67 - "Community 67"
Cohesion: 0.15
Nodes (14): PreferredMovePanelProps, RepertoireSessionPanel(), RepertoireSessionPanelProps, FrequencyAbsent, FrequencyUnavailable, FrequencyZero, LocalLineSession, meta (+6 more)

### Community 68 - "Community 68"
Cohesion: 0.19
Nodes (12): react-resizable-panels, clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage() (+4 more)

### Community 69 - "Community 69"
Cohesion: 0.16
Nodes (11): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelIntent, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue, InlineWdl(), resultMetadataLabel() (+3 more)

### Community 70 - "Community 70"
Cohesion: 0.17
Nodes (12): AnalysisPanelDisplay, AnalysisPanelLine, AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides (+4 more)

### Community 71 - "Community 71"
Cohesion: 0.19
Nodes (12): strictFen(), UciMove, defaultPreferredMoveClient, moveFromUci(), PendingRefresh, PositionPickerMove, PreferredMoveWorkflowState, sessionMove() (+4 more)

### Community 72 - "Community 72"
Cohesion: 0.15
Nodes (12): PreferredMoveSchedulePeriod, CalendarWithDraft, meta, NarrowCalendar, OpenEndedDraft, PERIODS, Story, storybookViewports (+4 more)

### Community 73 - "Community 73"
Cohesion: 0.21
Nodes (12): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+4 more)

### Community 74 - "Community 74"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 75 - "Community 75"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 76 - "Community 76"
Cohesion: 0.26
Nodes (12): @fullcalendar/react, actionLabel(), formatDay(), formatRange(), src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction (+4 more)

### Community 77 - "Community 77"
Cohesion: 0.15
Nodes (11): storybook, Available, meta, Story, PREFERRED_MOVE_SOURCE_FEN, expectDateFreePreferredPanel(), expectPreferredActions(), StoryPreferredMoveRequest (+3 more)

### Community 78 - "Community 78"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 79 - "Community 79"
Cohesion: 0.24
Nodes (12): AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient(), StoryAnalysisLifecycleEvent (+4 more)

### Community 80 - "Community 80"
Cohesion: 0.15
Nodes (11): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+3 more)

### Community 81 - "Community 81"
Cohesion: 0.15
Nodes (9): boardLane, Boundary1039, Boundary1040, Boundary699, Boundary700, engineLane, meta, sessionLane (+1 more)

### Community 82 - "Community 82"
Cohesion: 0.38
Nodes (11): invalidatePositionInsight(), AnalysisFailure, src_features_analysis_analysisapi_positionkeyfromfen, changedObservation(), failureMessage(), mergeObservation(), observationFingerprint(), useDefaultAnalysisState() (+3 more)

### Community 83 - "Community 83"
Cohesion: 0.17
Nodes (10): src_features_design_system_feedback_pagefeedback_module, PageFeedback(), AllSeverities, meta, Story, ACCENT_TOKEN, CONTAINER_TOKEN, here (+2 more)

### Community 84 - "Community 84"
Cohesion: 0.20
Nodes (8): meta, ResponsiveAccessibilityReview, Story, StorySpecimenAccessibilityReview(), here, moduleCss, tokenCss, src_styles_cmt_tokens

### Community 85 - "Community 85"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 86 - "Community 86"
Cohesion: 0.17
Nodes (9): PositionPickerMoveRecord, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PreferredMoveRelationship, preferredMoveRelationshipFixtures, PreferredMoveStoryFixture (+1 more)

### Community 87 - "Community 87"
Cohesion: 0.20
Nodes (8): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent

### Community 88 - "Community 88"
Cohesion: 0.20
Nodes (9): here, moduleCss, SEVERITIES, TOKEN_SET, FEEDBACK_VARIANTS, FeedbackSeverity, here, moduleCss (+1 more)

### Community 89 - "Community 89"
Cohesion: 0.18
Nodes (9): src_features_design_system_feedback_panelfeedback_module, PanelFeedback(), AllSeverities, meta, Story, here, moduleCss, SEVERITIES (+1 more)

### Community 90 - "Community 90"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 91 - "Community 91"
Cohesion: 0.22
Nodes (9): here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4, SELECTED_E4 (+1 more)

### Community 92 - "Community 92"
Cohesion: 0.24
Nodes (7): filterOpeningCatalogue(), src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, OpeningSelection, searchText()

### Community 93 - "Community 93"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 94 - "Community 94"
Cohesion: 0.24
Nodes (8): lucide-react, BoardControl(), BoardControlProps, InteractiveBoardAdapterProps, MoveHistoryControlledState, BoardContentProps, HistoryProps, RepertoireBoardLaneProps

### Community 95 - "Community 95"
Cohesion: 0.22
Nodes (6): AnalysisClient, AnalysisResult, StateProbe(), Probe(), RESULT, useAnalysisState()

### Community 96 - "Community 96"
Cohesion: 0.24
Nodes (9): src_features_board_adapter_boardadapter_boardorientation, BranchMove, SessionPosition, boardLabel(), branchMoves(), moveFromUci(), orientationDescription(), promotionPiece() (+1 more)

### Community 97 - "Community 97"
Cohesion: 0.44
Nodes (5): FeedbackCore(), FeedbackLiveRegionAttributes, FeedbackProps, FeedbackVariant, FeedbackVariantTokens

### Community 98 - "Community 98"
Cohesion: 0.29
Nodes (8): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story

### Community 99 - "Community 99"
Cohesion: 0.25
Nodes (7): CompleteTypescale, meta, Story, StorySpecimenTypescale(), TYPESCALE_ROLES, TypescaleRole, src_styles_cmt_typescale

### Community 100 - "Community 100"
Cohesion: 0.28
Nodes (8): createMoveHistoryRows(), KEY_NAVIGATION, src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow

### Community 101 - "Community 101"
Cohesion: 0.22
Nodes (6): Constrained, HISTORY, Interactive, meta, Story, MoveHistoryInput

### Community 102 - "Community 102"
Cohesion: 0.22
Nodes (8): RepertoireBoardLane(), board, controls, evaluation, history, meta, Standard, Story

### Community 103 - "Community 103"
Cohesion: 0.29
Nodes (5): BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 104 - "Community 104"
Cohesion: 0.25
Nodes (7): InlineFeedback(), HEADINGS, InlineMatrix, MESSAGES, meta, SEVERITIES, Story

### Community 106 - "Community 106"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 107 - "Community 107"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 108 - "Community 108"
Cohesion: 0.29
Nodes (6): here, moduleCss, SCALE_NAMES, SIZE_NAMES, tokenCss, TYPESCALE_ROLES

### Community 109 - "Community 109"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 110 - "Community 110"
Cohesion: 0.29
Nodes (4): here, HISTORY, moduleCss, MoveHistoryActivePlyChange

### Community 111 - "Community 111"
Cohesion: 0.87
Nodes (6): useInjectedAnalysisState(), fail(), observe(), poll(), schedulePoll(), stopTimer()

### Community 112 - "Community 112"
Cohesion: 0.33
Nodes (5): MESSAGES, meta, SemanticVariants, SEVERITIES, Story

### Community 113 - "Community 113"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 114 - "Community 114"
Cohesion: 0.50
Nodes (3): @testing-library/jest-dom, elementProto, topLayerPseudoSelectors

### Community 115 - "Community 115"
Cohesion: 0.50
Nodes (3): FEEDBACK_TOKENS, here, tokenCss

## Knowledge Gaps
- **839 isolated node(s):** `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind`, `OpeningLineLibraryResult`, `JsonRecord` (+834 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1182 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 14` to `Community 1`, `Community 2`, `Community 6`, `Community 7`, `Community 10`, `Community 12`, `Community 13`, `Community 15`, `Community 16`, `Community 18`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 24`, `Community 26`, `Community 30`, `Community 33`, `Community 34`, `Community 35`, `Community 36`, `Community 38`, `Community 40`, `Community 43`, `Community 44`, `Community 47`, `Community 49`, `Community 55`, `Community 59`, `Community 60`, `Community 61`, `Community 65`, `Community 66`, `Community 68`, `Community 70`, `Community 71`, `Community 73`, `Community 74`, `Community 76`, `Community 77`, `Community 81`, `Community 82`, `Community 87`, `Community 92`, `Community 95`, `Community 97`, `Community 100`, `Community 101`, `Community 103`, `Community 110`?**
  _High betweenness centrality (0.228) - this node is a cross-community bridge._
- **Why does `vitest` connect `Community 33` to `Community 1`, `Community 2`, `Community 5`, `Community 6`, `Community 8`, `Community 10`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 20`, `Community 21`, `Community 24`, `Community 26`, `Community 27`, `Community 32`, `Community 35`, `Community 36`, `Community 39`, `Community 40`, `Community 42`, `Community 43`, `Community 46`, `Community 47`, `Community 49`, `Community 50`, `Community 51`, `Community 54`, `Community 56`, `Community 57`, `Community 58`, `Community 59`, `Community 60`, `Community 63`, `Community 64`, `Community 70`, `Community 71`, `Community 83`, `Community 84`, `Community 85`, `Community 88`, `Community 89`, `Community 90`, `Community 91`, `Community 95`, `Community 103`, `Community 107`, `Community 108`, `Community 109`, `Community 110`, `Community 115`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Why does `@storybook/react-vite` connect `Community 7` to `Community 1`, `Community 2`, `Community 6`, `Community 10`, `Community 13`, `Community 18`, `Community 22`, `Community 23`, `Community 24`, `Community 26`, `Community 28`, `Community 31`, `Community 34`, `Community 36`, `Community 37`, `Community 38`, `Community 40`, `Community 45`, `Community 48`, `Community 49`, `Community 51`, `Community 52`, `Community 59`, `Community 63`, `Community 65`, `Community 66`, `Community 67`, `Community 72`, `Community 74`, `Community 77`, `Community 80`, `Community 81`, `Community 83`, `Community 84`, `Community 85`, `Community 87`, `Community 89`, `Community 90`, `Community 98`, `Community 99`, `Community 101`, `Community 102`, `Community 104`, `Community 112`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `RepertoireBuilderWorkspace()` (e.g. with `PreferredMoveWorkflow.stories.tsx` and `createFreshSession()`) actually correct?**
  _`RepertoireBuilderWorkspace()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind` to the rest of the system?**
  _839 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.01694915254237288 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05116279069767442 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
