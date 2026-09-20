# Graph Report - frontend  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2365 nodes · 5312 edges · 120 communities (113 shown, 7 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.85)
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

## God Nodes (most connected - your core abstractions)
1. `react` - 83 edges
2. `vitest` - 77 edges
3. `@storybook/react-vite` - 57 edges
4. `@testing-library/react` - 49 edges
5. `RepertoireBuilderWorkspace()` - 35 edges
6. `storybook` - 33 edges
7. `chess.js` - 26 edges
8. `Fen` - 23 edges
9. `positionKeyFromFen()` - 23 edges
10. `@testing-library/user-event` - 22 edges

## Surprising Connections (you probably didn't know these)
- `StorybookQueryClientProvider()` --indirect_call--> `createTestQueryClient()`  [INFERRED]
  .storybook/preview.tsx → src/test-utils/QueryClientTestProvider.tsx
- `PreferredMoveDateValue()` --calls--> `formatUtcDate()`  [EXTRACTED]
  src/features/repertoire-builder/PreferredMovePrimitives.tsx → src/features/design-system/CalendarDateUtils.ts
- `handleKeyDown()` --indirect_call--> `model()`  [INFERRED]
  src/features/move-history/MoveHistory.tsx → src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx
- `TrainerPracticePage()` --indirect_call--> `readOpeningCatalogueSnapshot()`  [INFERRED]
  src/features/trainer-practice/TrainerPracticePage.tsx → src/features/trainer-practice/openingCatalogueStorage.ts
- `normalizePositionKey()` --calls--> `positionKeyFromFen()`  [EXTRACTED]
  src/api/queryKeys.ts → src/features/chess/chessPrimitives.ts

## Import Cycles
- None detected.

## Communities (120 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (79): src_features_design_system_line_library_linelibrary_linelibraryprops, LineLibraryFilterKind, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult (+71 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (67): @headless-tree/core, @headless-tree/react, LineLibrary(), nodeName(), sameIds(), selectionDescription(), Default, Empty (+59 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (54): src_api_client_deletepreferredmoves, src_api_client_getpreferredmoves, src_api_client_preferredmovesmutationresponse, src_api_client_preferredmovesremovalresponse, src_api_client_preferredmovesresponse, src_api_client_preferredmovessegmentresponse, src_api_client_putpreferredmoves, deletePreferredMove() (+46 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (56): AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse, DeletePreferredMovesError, DeletePreferredMovesResponse (+48 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (38): @base-ui/react, lucide-react, react, AutocompleteStates, ComboboxStates, Docs, FieldStates, meta (+30 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (48): getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight(), getPositionTrainingRequirements() (+40 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (41): deletePreferredMoves(), Options, putPreferredMoves(), requestAnalysis(), submitPositionTrainingAnswer(), DeletePreferredMovesData, DeletePreferredMovesErrors, DeletePreferredMovesResponses (+33 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (31): @storybook/react-vite, src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story (+23 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (25): react-resizable-panels, clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage() (+17 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (31): src_api_client_getanalysis, src_api_client_requestanalysis, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis(), invalidFenResult() (+23 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (24): vitest, AnalysisClient, PreferredMoveMutationResult, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, AFTER_NF3_FEN (+16 more)

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (27): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+19 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (25): ref_node_fs, ref_node_path, ref_node_url, typescript, src_api_client_getpositiontrainingrequirements, ContractOperation, dirname, ALLOWED_RUNTIME_CLIENT_IMPORTS (+17 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (21): AnalysisLine, AnalysisObservation, analysisPanelDisplay(), AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv() (+13 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (23): PositionContextResponse, PositionReachFrequency(), PositionReachFrequencyProps, BasePositionReachFrequencyModel, boundedPercentage(), colorLabel(), derivePositionReachFrequencyModel(), percentageLabel() (+15 more)

### Community 15 - "Community 15"
Cohesion: 0.10
Nodes (21): src_api_client_openingcatalogueitemresponse, src_api_client_trainingrequirementresponse, ALL_OPENINGS_VALUE, filterOpeningCatalogue(), src_features_trainer_practice_openingsearchcombobox_module, OPENING_SEARCH_VISIBLE_LIMIT, openingLabel(), OpeningSearchCombobox() (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 17 - "Community 17"
Cohesion: 0.08
Nodes (26): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+18 more)

### Community 18 - "Community 18"
Cohesion: 0.13
Nodes (18): src_api_client_positioninsightresponse, ChessSide, Fen, PositionContextClient, PositionContextState, context(), Probe(), success() (+10 more)

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (26): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+18 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (17): ref_axe_core, react-error-boundary, AppShell(), AppShellProps, src_features_app_shell_appshell_module, ConstrainedClosed, ConstrainedOpen, Healthy (+9 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (24): GAME_UUID, Game, PROMOTION_GAME, DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR, DEFAULT_MOVE, moveFromRequest(), moveResponseData(), removalMutationResponse() (+16 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (13): @chialab/vitest-axe, @testing-library/react, @testing-library/user-event, { shouldThrow }, booleanFilterData, data, here, LoaderHarnessProps (+5 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (19): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+11 more)

### Community 24 - "Community 24"
Cohesion: 0.14
Nodes (25): GAME, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession() (+17 more)

### Community 25 - "Community 25"
Cohesion: 0.09
Nodes (26): expectPositionReachFrequency(), expectPositionSquares(), expectPreferredMoveState(), expectSessionBoundary(), sharedPositionSummary(), expectNoHorizontalOverflow(), Accessibility, CandidateActivation (+18 more)

### Community 26 - "Community 26"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 27 - "Community 27"
Cohesion: 0.09
Nodes (23): react-chessboard, PromotionColor, PromotionCommit, PromotionPresentation, Cancellation, ConstrainedDrawer, defaultArgs, ForcedColorsAndReducedMotion (+15 more)

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (23): buildUrl(), createQuerySerializer(), defaultHeaders, defaultQuerySerializer, ErrInterceptor, ReqInterceptor, ResInterceptor, ArraySeparatorStyle (+15 more)

### Community 29 - "Community 29"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (19): src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, MoveResponseDistributionReply, MoveResponseDistributionResponse, MoveResponseDistributionControls(), MoveResponseDistributionControlsProps, CommonReplies (+11 more)

### Community 31 - "Community 31"
Cohesion: 0.19
Nodes (23): applySessionMove(), atIndex(), branchWithMove(), createFreshSession(), createSession(), importedPositions(), loadImportedSession(), mainLinePositions() (+15 more)

### Community 32 - "Community 32"
Cohesion: 0.09
Nodes (22): engines, node, name, private, type, version, eslint, @eslint/js (+14 more)

### Community 33 - "Community 33"
Cohesion: 0.12
Nodes (16): @tanstack/react-query, src_api_client_gethealthoptions, PreferredMoveOutput(), Probe(), StatusPage(), Default, meta, queryClient (+8 more)

### Community 34 - "Community 34"
Cohesion: 0.12
Nodes (24): src_api_client_getopeningsdata, src_api_client_getpositiontrainingrequirementsdata, src_api_client_openingcatalogueresponse, abortError(), buildTrainingRequirementsQuery(), errorCode(), fetchOpeningChoices(), fetchOpeningPage() (+16 more)

### Community 35 - "Community 35"
Cohesion: 0.14
Nodes (21): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+13 more)

### Community 36 - "Community 36"
Cohesion: 0.15
Nodes (19): failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isChessSide(), isNonnegativeInteger(), isRecord(), JsonRecord (+11 more)

### Community 37 - "Community 37"
Cohesion: 0.17
Nodes (17): answerInteractionAllowed(), answerMessage(), BoardAnswerPresentation, BranchMove, BranchSnapshot, accessiblePieces, branchSan(), findSourceElement() (+9 more)

### Community 38 - "Community 38"
Cohesion: 0.16
Nodes (19): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+11 more)

### Community 39 - "Community 39"
Cohesion: 0.16
Nodes (17): src_api_client_getpositioninsight, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord, narrowInsightResponse() (+9 more)

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (19): BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys, Options (+11 more)

### Community 41 - "Community 41"
Cohesion: 0.09
Nodes (21): AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, CleanPreferredTimelineNovelParent, FirstChoice, FirstChoiceFromEmpty, Matching, meta (+13 more)

### Community 42 - "Community 42"
Cohesion: 0.15
Nodes (17): chess.js, clearPending(), isPromotionCandidate(), PendingPromotion, PickerLiveRegion(), PROMOTION_OPTIONS, PromotionController, PromotionControllerOptions (+9 more)

### Community 43 - "Community 43"
Cohesion: 0.14
Nodes (19): @fullcalendar/react, actionLabel(), formatDay(), formatRange(), src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction (+11 more)

### Community 44 - "Community 44"
Cohesion: 0.16
Nodes (16): src_api_client_getgame, src_features_board_adapter_boardadapter_boardorientation, useMoveResponseSelection(), PositionPickerSessionBoundary, SessionNavigation, SessionPosition, src_features_repertoire_builder_repertoirebuilderworkspace_module, cancelPromotionWithStatus() (+8 more)

### Community 45 - "Community 45"
Cohesion: 0.16
Nodes (12): AnalysisFailureCode, defaultAnalysisClient, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey(), AnalysisQueryError, DEFAULT_ANALYSIS_POLL_INTERVAL_MS, MAX_ANALYSIS_POLL_ATTEMPTS, PollState (+4 more)

### Community 46 - "Community 46"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 47 - "Community 47"
Cohesion: 0.15
Nodes (16): Ply, San, GameMainLineModel, GameMainLineOccurrence, GamePosition, mapGameDetailResponse(), sanFromFenAndUci(), SelectedTransition (+8 more)

### Community 48 - "Community 48"
Cohesion: 0.13
Nodes (14): Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story (+6 more)

### Community 49 - "Community 49"
Cohesion: 0.26
Nodes (18): invalidateAnalysisObservation(), invalidatePositionInsight(), AnalysisFailure, src_features_analysis_analysisapi_positionkeyfromfen, changedObservation(), failureMessage(), mergeObservation(), observationFingerprint() (+10 more)

### Community 50 - "Community 50"
Cohesion: 0.20
Nodes (15): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerSquareStyles(), BoardAnswerStatus, BoardSquareHighlight, boardSquareStyles(), DEFAULT_ANSWER_MESSAGES, ILLEGAL_ATTEMPT_SQUARE_STYLE (+7 more)

### Community 51 - "Community 51"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 52 - "Community 52"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 53 - "Community 53"
Cohesion: 0.16
Nodes (14): recharts, clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart() (+6 more)

### Community 54 - "Community 54"
Cohesion: 0.15
Nodes (12): src_api_client_getopenings, currentUtcDate(), isValidAsOf(), queryOpeningCatalogueSnapshot(), queryOpeningChoices(), queryTrainingRequirements(), OPENING, selectedFilters (+4 more)

### Community 55 - "Community 55"
Cohesion: 0.12
Nodes (16): BoardAdapter(), src_features_board_adapter_boardadapter_module, src_features_board_adapter_boardadapter_starting_fen, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition, ExpandedPositionDescription, HiddenCoordinates (+8 more)

### Community 56 - "Community 56"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 57 - "Community 57"
Cohesion: 0.17
Nodes (14): invalidatePreferredMove(), invalidateTrainingRequirements(), strictFen(), defaultPreferredMoveClient, moveFromUci(), PendingRefresh, PositionPickerMove, PreferredMoveDateCapability (+6 more)

### Community 58 - "Community 58"
Cohesion: 0.14
Nodes (13): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelDisplay, AnalysisPanelIntent, AnalysisPanelLine, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue (+5 more)

### Community 59 - "Community 59"
Cohesion: 0.21
Nodes (15): PositionContextFailureCode, contextFailureMessage(), failureMessage(), src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), statusLabel() (+7 more)

### Community 60 - "Community 60"
Cohesion: 0.15
Nodes (15): LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate, expectActiveSessionHistoryEntry() (+7 more)

### Community 61 - "Community 61"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 62 - "Community 62"
Cohesion: 0.17
Nodes (10): AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput, OptionalText, PositionInsightKeyInput, PreferredMoveKeyInput, queryKeyPrefixes (+2 more)

### Community 63 - "Community 63"
Cohesion: 0.14
Nodes (13): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+5 more)

### Community 64 - "Community 64"
Cohesion: 0.24
Nodes (13): createMoveHistoryModel(), findMoveHistoryEntry(), MoveHistoryControlledModel, moveHistoryEntries(), MoveHistoryModel, HISTORY, MoveHistoryBounds, MoveHistoryEntry (+5 more)

### Community 65 - "Community 65"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 66 - "Community 66"
Cohesion: 0.20
Nodes (13): MoveResponseDistributionClient, MoveResponseDistributionFailureCode, MoveResponseDistributionResult, InternalState, isEmptyResponse(), MoveResponseDistributionState, requestKey(), Probe() (+5 more)

### Community 67 - "Community 67"
Cohesion: 0.12
Nodes (11): Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth, ForcedColorsAndReducedMotion, meta, PositiveBlack (+3 more)

### Community 68 - "Community 68"
Cohesion: 0.19
Nodes (12): src_api_client_gamedetailresponse, GameDetailQueryError, queryGameDetail(), useGameDetailQuery(), SessionMove, PreferredMoveClient, failureCode(), GameDetailClient (+4 more)

### Community 69 - "Community 69"
Cohesion: 0.22
Nodes (14): createClient(), TODO: we probably want to return error and improve types, ReqInit, checkForExistence(), createConfig(), createInterceptors(), getParseAs(), headersEntries() (+6 more)

### Community 70 - "Community 70"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 71 - "Community 71"
Cohesion: 0.18
Nodes (11): src_api_client_trainingrequirementitemresponse, OpeningCatalogueSnapshotResult, TrainingRequirementsResult, TrainerPracticeApi, createApi(), OPENING, page(), renderPage() (+3 more)

### Community 72 - "Community 72"
Cohesion: 0.22
Nodes (13): AnalysisOperationResult, AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient() (+5 more)

### Community 73 - "Community 73"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 74 - "Community 74"
Cohesion: 0.14
Nodes (11): PreferredMoveValue, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PREFERRED_MOVE_SOURCE_FEN, PreferredMoveRelationship, preferredMoveRelationshipFixtures (+3 more)

### Community 75 - "Community 75"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 76 - "Community 76"
Cohesion: 0.24
Nodes (11): Auth, AuthToken, BodySerializer, QuerySerializer, QuerySerializerOptions, Client, ClientMeta, Config (+3 more)

### Community 77 - "Community 77"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 78 - "Community 78"
Cohesion: 0.21
Nodes (10): AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay(), missingDisplay() (+2 more)

### Community 79 - "Community 79"
Cohesion: 0.15
Nodes (11): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+3 more)

### Community 80 - "Community 80"
Cohesion: 0.17
Nodes (10): GameLoader(), handleSubmit(), GameLoaderFailureKind, GameLoaderProps, GameLoaderStatus, GameLoaderValues, src_features_game_gameloader_module, validationMessage() (+2 more)

### Community 81 - "Community 81"
Cohesion: 0.18
Nodes (11): PreferredMovePanelProps, here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4 (+3 more)

### Community 82 - "Community 82"
Cohesion: 0.26
Nodes (8): EvalBar(), EvalBarDisplayState, EvalBarProps, ExpectedDisplay, BoardEvalStage(), BoardEvalStageProps, boardVisualIn(), BoardOrientation

### Community 83 - "Community 83"
Cohesion: 0.17
Nodes (8): HealthyContent, meta, Story, UnexpectedFailureTryAgain, Default, meta, Story, src_styles_cmt_tokens

### Community 84 - "Community 84"
Cohesion: 0.23
Nodes (8): BoardControl(), BoardControlProps, InteractiveBoardAdapterProps, MoveHistoryControlledState, BoardContentProps, HistoryProps, RepertoireBoardLane(), RepertoireBoardLaneProps

### Community 85 - "Community 85"
Cohesion: 0.20
Nodes (8): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent

### Community 86 - "Community 86"
Cohesion: 0.17
Nodes (10): src_features_design_system_feedback_pagefeedback_module, PageFeedback(), AllSeverities, meta, Story, ACCENT_TOKEN, CONTAINER_TOKEN, here (+2 more)

### Community 87 - "Community 87"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 88 - "Community 88"
Cohesion: 0.20
Nodes (8): InlineFeedback(), StatusViewProps, StatusViewState, Healthy, Loading, meta, Story, Unavailable

### Community 89 - "Community 89"
Cohesion: 0.18
Nodes (9): src_features_design_system_feedback_panelfeedback_module, PanelFeedback(), AllSeverities, meta, Story, here, moduleCss, SEVERITIES (+1 more)

### Community 90 - "Community 90"
Cohesion: 0.22
Nodes (7): meta, ResponsiveAccessibilityReview, Story, StorySpecimenAccessibilityReview(), here, moduleCss, tokenCss

### Community 91 - "Community 91"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 92 - "Community 92"
Cohesion: 0.24
Nodes (10): createMoveHistoryRows(), KEY_NAVIGATION, src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow (+2 more)

### Community 93 - "Community 93"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 94 - "Community 94"
Cohesion: 0.29
Nodes (6): react-router-dom, App(), RepertoireBuilderWorkspace, TrainerPracticePage, PageNotFoundView(), queryClient

### Community 95 - "Community 95"
Cohesion: 0.29
Nodes (8): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story

### Community 96 - "Community 96"
Cohesion: 0.22
Nodes (6): formDataBodySerializer, jsonBodySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArrayStyle, ObjectStyle

### Community 97 - "Community 97"
Cohesion: 0.25
Nodes (5): AnalysisResult, StateProbe(), Probe(), RESULT, useAnalysisState()

### Community 98 - "Community 98"
Cohesion: 0.25
Nodes (6): BoardAdapterProps, BoardRender(), PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, stripPackageSemantics(), PositionModel

### Community 99 - "Community 99"
Cohesion: 0.29
Nodes (5): BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 100 - "Community 100"
Cohesion: 0.25
Nodes (5): Constrained, HISTORY, Interactive, meta, Story

### Community 101 - "Community 101"
Cohesion: 0.25
Nodes (5): here, HISTORY, moduleCss, MoveHistoryActivePlyChange, Ply

### Community 102 - "Community 102"
Cohesion: 0.25
Nodes (7): board, controls, evaluation, history, meta, Standard, Story

### Community 104 - "Community 104"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 105 - "Community 105"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 106 - "Community 106"
Cohesion: 0.29
Nodes (6): HEADINGS, InlineMatrix, MESSAGES, meta, SEVERITIES, Story

### Community 107 - "Community 107"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 108 - "Community 108"
Cohesion: 0.33
Nodes (4): vite, @vitejs/plugin-react, @vitest/browser-playwright, dirname

### Community 109 - "Community 109"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 110 - "Community 110"
Cohesion: 0.40
Nodes (4): storybook, Available, meta, Story

### Community 111 - "Community 111"
Cohesion: 0.50
Nodes (3): @testing-library/jest-dom, elementProto, topLayerPseudoSelectors

### Community 112 - "Community 112"
Cohesion: 0.50
Nodes (3): client, CreateClientConfig, ClientOptions

### Community 113 - "Community 113"
Cohesion: 0.50
Nodes (3): FEEDBACK_TOKENS, here, tokenCss

## Knowledge Gaps
- **838 isolated node(s):** `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind`, `OpeningLineLibraryResult`, `JsonRecord` (+833 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1065 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 7`, `Community 8`, `Community 10`, `Community 11`, `Community 14`, `Community 15`, `Community 16`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 25`, `Community 27`, `Community 30`, `Community 32`, `Community 33`, `Community 37`, `Community 41`, `Community 42`, `Community 43`, `Community 44`, `Community 45`, `Community 48`, `Community 49`, `Community 50`, `Community 53`, `Community 57`, `Community 59`, `Community 65`, `Community 66`, `Community 67`, `Community 70`, `Community 73`, `Community 78`, `Community 80`, `Community 82`, `Community 83`, `Community 85`, `Community 92`, `Community 94`, `Community 97`, `Community 98`, `Community 99`, `Community 100`, `Community 101`?**
  _High betweenness centrality (0.273) - this node is a cross-community bridge._
- **Why does `vitest` connect `Community 10` to `Community 0`, `Community 2`, `Community 4`, `Community 8`, `Community 9`, `Community 11`, `Community 12`, `Community 13`, `Community 14`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 23`, `Community 24`, `Community 30`, `Community 31`, `Community 32`, `Community 33`, `Community 35`, `Community 36`, `Community 37`, `Community 38`, `Community 39`, `Community 42`, `Community 45`, `Community 47`, `Community 48`, `Community 50`, `Community 51`, `Community 54`, `Community 56`, `Community 57`, `Community 62`, `Community 63`, `Community 64`, `Community 66`, `Community 71`, `Community 78`, `Community 81`, `Community 82`, `Community 84`, `Community 85`, `Community 86`, `Community 87`, `Community 89`, `Community 90`, `Community 91`, `Community 94`, `Community 97`, `Community 99`, `Community 101`, `Community 105`, `Community 107`, `Community 113`, `Community 114`?**
  _High betweenness centrality (0.191) - this node is a cross-community bridge._
- **Why does `@storybook/react-vite` connect `Community 7` to `Community 0`, `Community 1`, `Community 4`, `Community 8`, `Community 11`, `Community 14`, `Community 16`, `Community 17`, `Community 19`, `Community 20`, `Community 23`, `Community 25`, `Community 27`, `Community 29`, `Community 30`, `Community 32`, `Community 33`, `Community 35`, `Community 41`, `Community 43`, `Community 46`, `Community 48`, `Community 51`, `Community 55`, `Community 60`, `Community 63`, `Community 65`, `Community 67`, `Community 73`, `Community 79`, `Community 83`, `Community 85`, `Community 86`, `Community 87`, `Community 88`, `Community 89`, `Community 90`, `Community 91`, `Community 95`, `Community 100`, `Community 102`, `Community 106`, `Community 110`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `RepertoireBuilderWorkspace()` (e.g. with `PreferredMoveWorkflow.stories.tsx` and `createFreshSession()`) actually correct?**
  _`RepertoireBuilderWorkspace()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind` to the rest of the system?**
  _838 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05116279069767442 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06037000973709834 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
