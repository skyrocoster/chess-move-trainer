# Graph Report - frontend  (2026-09-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2370 nodes · 5349 edges · 109 communities (103 shown, 6 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 81 edges (avg confidence: 0.85)
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

## God Nodes (most connected - your core abstractions)
1. `react` - 84 edges
2. `vitest` - 78 edges
3. `@storybook/react-vite` - 58 edges
4. `@testing-library/react` - 49 edges
5. `RepertoireBuilderWorkspace()` - 36 edges
6. `storybook` - 35 edges
7. `chess.js` - 26 edges
8. `Fen` - 23 edges
9. `positionKeyFromFen()` - 23 edges
10. `@testing-library/user-event` - 22 edges

## Surprising Connections (you probably didn't know these)
- `StorybookQueryClientProvider()` --indirect_call--> `createTestQueryClient()`  [INFERRED]
  .storybook/StorybookQueryClientProvider.tsx → src/test-utils/QueryClientTestProvider.tsx
- `RepertoireBuilderWorkspace()` --indirect_call--> `createFreshSession()`  [INFERRED]
  src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx → src/features/repertoire-builder/positionPickerSessionBoundary.ts
- `resetWorkspace()` --calls--> `resetSession()`  [EXTRACTED]
  src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx → src/features/repertoire-builder/positionPickerSessionBoundary.ts
- `handleKeyDown()` --indirect_call--> `model()`  [INFERRED]
  src/features/move-history/MoveHistory.tsx → src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx
- `TrainerPracticePage()` --indirect_call--> `readOpeningCatalogueSnapshot()`  [INFERRED]
  src/features/trainer-practice/TrainerPracticePage.tsx → src/features/trainer-practice/openingCatalogueStorage.ts

## Import Cycles
- None detected.

## Communities (109 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (79): src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+71 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (67): @headless-tree/core, @headless-tree/react, LineLibrary(), nodeName(), sameIds(), selectionDescription(), Default, Empty (+59 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (46): @base-ui/react, react, catalogueDemoShell(), AutocompleteStates, ComboboxStates, Docs, FieldStates, meta (+38 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (56): src_api_client_deletepreferredmoves, src_api_client_getpreferredmoves, src_api_client_preferredmovesmutationresponse, src_api_client_preferredmovesremovalresponse, src_api_client_preferredmovesresponse, src_api_client_preferredmovessegmentresponse, src_api_client_putpreferredmoves, defaultPreferredMoveClient (+48 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (59): AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse, ClientOptions, DeletePreferredMovesError (+51 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (53): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+45 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (56): getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight(), getPositionTrainingRequirements() (+48 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (37): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+29 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (33): chess.js, ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerPresentation, BoardAnswerStatus (+25 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (34): src_api_client_positioninsightresponse, failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isChessSide(), isNonnegativeInteger(), isRecord() (+26 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (31): @storybook/react-vite, src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story (+23 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (25): ref_axe_core, lucide-react, react-router-dom, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps (+17 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (25): react-resizable-panels, clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage() (+17 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (29): src_api_client_gamedetailresponse, src_api_client_getgame, src_features_board_adapter_boardadapter_boardorientation, GameDetailQueryError, queryGameDetail(), useGameDetailQuery(), useMoveResponseSelection(), PositionPickerSessionBoundary (+21 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (31): src_api_client_getanalysis, src_api_client_requestanalysis, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis(), invalidFenResult() (+23 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (23): src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, ChartLabel, here, rawStyles, MoveResponseDistributionClient, MoveResponseDistributionReply (+15 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (29): CreateClientConfig, BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys (+21 more)

### Community 17 - "Community 17"
Cohesion: 0.06
Nodes (33): client, deletePreferredMoves(), putPreferredMoves(), requestAnalysis(), submitPositionTrainingAnswer(), DeletePreferredMovesData, DeletePreferredMovesErrors, DeletePreferredMovesResponses (+25 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (24): @chialab/vitest-axe, BoardAdapter(), BoardAdapterProps, BoardRender(), src_features_board_adapter_boardadapter_module, PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, src_features_board_adapter_boardadapter_starting_fen (+16 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (21): AnalysisLine, AnalysisObservation, analysisPanelDisplay(), AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv() (+13 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (23): ChessSide, PositionContextResponse, PositionReachFrequency(), PositionReachFrequencyProps, BasePositionReachFrequencyModel, boundedPercentage(), colorLabel(), derivePositionReachFrequencyModel() (+15 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (23): src_api_client_getpositioninsight, Fen, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord (+15 more)

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 23 - "Community 23"
Cohesion: 0.13
Nodes (23): createQuerySerializer(), formDataBodySerializer, QuerySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArraySeparatorStyle, ArrayStyle, MatrixStyle (+15 more)

### Community 24 - "Community 24"
Cohesion: 0.09
Nodes (23): engines, node, name, private, type, version, eslint, @eslint/js (+15 more)

### Community 25 - "Community 25"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 26 - "Community 26"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (25): src_api_client_getopeningsdata, src_api_client_getpositiontrainingrequirementsdata, src_api_client_openingcatalogueresponse, abortError(), buildTrainingRequirementsQuery(), errorCode(), fetchOpeningChoices(), fetchOpeningPage() (+17 more)

### Community 28 - "Community 28"
Cohesion: 0.13
Nodes (24): storyAnalysisClient(), formatUtcDate(), getPreferredMoveDateWindow(), DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR, DEFAULT_MOVE, moveFromRequest(), moveResponseData(), removalMutationResponse() (+16 more)

### Community 29 - "Community 29"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (22): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+14 more)

### Community 31 - "Community 31"
Cohesion: 0.10
Nodes (22): react-chessboard, PromotionColor, PromotionPresentation, Cancellation, ConstrainedDrawer, defaultArgs, ForcedColorsAndReducedMotion, KeyboardSelection (+14 more)

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (23): appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession(), playAndStagePositionPickerMove() (+15 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (16): react-error-boundary, PageContentBoundaryProps, Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta (+8 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (16): src_api_client_openingcatalogueitemresponse, src_api_client_trainingrequirementresponse, filterOpeningCatalogue(), src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, OpeningSelection (+8 more)

### Community 35 - "Community 35"
Cohesion: 0.16
Nodes (22): createClient(), TODO: we probably want to return error and improve types, ReqInit, buildUrl(), checkForExistence(), createConfig(), createInterceptors(), defaultHeaders (+14 more)

### Community 36 - "Community 36"
Cohesion: 0.19
Nodes (22): GameMainLineModel, applySessionMove(), atIndex(), branchWithMove(), createFreshSession(), createSession(), importedPositions(), loadImportedSession() (+14 more)

### Community 37 - "Community 37"
Cohesion: 0.11
Nodes (15): @testing-library/react, src_api_client_gethealthoptions, StatusPage(), Default, meta, queryClient, Story, StatusView() (+7 more)

### Community 38 - "Community 38"
Cohesion: 0.09
Nodes (22): expectSingleStagedStatus(), expectStagedStatus(), AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, FirstChoice, FirstChoiceFromEmpty, Matching (+14 more)

### Community 39 - "Community 39"
Cohesion: 0.09
Nodes (21): Accessibility, CandidateActivation, Constrained, ConstrainedStoredPrefixAndLocalLine, FlipCancellation, KeyboardAndAccessibility, Medium, meta (+13 more)

### Community 40 - "Community 40"
Cohesion: 0.17
Nodes (18): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+10 more)

### Community 41 - "Community 41"
Cohesion: 0.14
Nodes (19): @fullcalendar/react, actionLabel(), formatDay(), formatRange(), src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction (+11 more)

### Community 42 - "Community 42"
Cohesion: 0.15
Nodes (14): src_api_client_getopenings, defaultTrainerPracticeApi, isValidAsOf(), queryOpeningCatalogueSnapshot(), queryOpeningChoices(), queryTrainingRequirements(), OPENING, selectedFilters (+6 more)

### Community 43 - "Community 43"
Cohesion: 0.15
Nodes (17): clearPending(), isPromotionCandidate(), isPromotionTarget(), PendingPromotion, PickerLiveRegion(), PROMOTION_OPTIONS, PromotionController, PromotionControllerOptions (+9 more)

### Community 44 - "Community 44"
Cohesion: 0.11
Nodes (16): Ply, San, GameLoader(), handleSubmit(), GameLoaderFailureKind, GameLoaderProps, GameLoaderStatus, GameLoaderValues (+8 more)

### Community 45 - "Community 45"
Cohesion: 0.10
Nodes (16): src_features_design_system_feedback_pagefeedback_module, AllSeverities, meta, Story, src_features_design_system_feedback_panelfeedback_module, AllSeverities, meta, Story (+8 more)

### Community 46 - "Community 46"
Cohesion: 0.16
Nodes (12): AnalysisFailureCode, defaultAnalysisClient, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey(), AnalysisQueryError, DEFAULT_ANALYSIS_POLL_INTERVAL_MS, MAX_ANALYSIS_POLL_ATTEMPTS, PollState (+4 more)

### Community 47 - "Community 47"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 48 - "Community 48"
Cohesion: 0.26
Nodes (18): invalidateAnalysisObservation(), invalidatePositionInsight(), AnalysisFailure, src_features_analysis_analysisapi_positionkeyfromfen, changedObservation(), failureMessage(), mergeObservation(), observationFingerprint() (+10 more)

### Community 49 - "Community 49"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 50 - "Community 50"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 51 - "Community 51"
Cohesion: 0.13
Nodes (14): ref_node_fs, ref_node_path, ref_node_url, @storybook/addon-vitest, @vitest/browser-playwright, src_api_client_getpositiontrainingrequirements, ContractOperation, dirname (+6 more)

### Community 52 - "Community 52"
Cohesion: 0.16
Nodes (14): recharts, clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart() (+6 more)

### Community 53 - "Community 53"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 54 - "Community 54"
Cohesion: 0.20
Nodes (16): contextFailureMessage(), failureMessage(), src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), statusLabel(), choiceBoxToneClass() (+8 more)

### Community 55 - "Community 55"
Cohesion: 0.19
Nodes (13): @tanstack/react-query, invalidatePreferredMove(), invalidateTrainingRequirements(), strictFen(), moveFromUci(), PendingRefresh, PositionPickerMove, PreferredMoveWorkflowState (+5 more)

### Community 56 - "Community 56"
Cohesion: 0.20
Nodes (14): typescript, collectStoryFiles(), collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue() (+6 more)

### Community 57 - "Community 57"
Cohesion: 0.18
Nodes (12): AnalysisOperationResult, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_NF3_FEN, GAME_DETAIL, src_features_repertoire_builder_repertoirebuildertesthelpers_game_uuid, gameClient(), noAnalysisClient() (+4 more)

### Community 58 - "Community 58"
Cohesion: 0.14
Nodes (13): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelDisplay, AnalysisPanelIntent, AnalysisPanelLine, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue (+5 more)

### Community 59 - "Community 59"
Cohesion: 0.14
Nodes (9): MoveResponseDistributionResult, Probe(), useMoveResponseDistributionState(), Probe(), useInjectedPositionContextState(), usePositionContextState(), POSITION_INSIGHT_GC_TIME, POSITION_INSIGHT_STALE_TIME (+1 more)

### Community 60 - "Community 60"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 61 - "Community 61"
Cohesion: 0.17
Nodes (10): AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput, OptionalText, PositionInsightKeyInput, PreferredMoveKeyInput, queryKeyPrefixes (+2 more)

### Community 62 - "Community 62"
Cohesion: 0.14
Nodes (13): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+5 more)

### Community 63 - "Community 63"
Cohesion: 0.17
Nodes (13): sanFromFenAndUci(), SelectedTransition, PreferredMoveValue, colorLabel(), deriveRepertoirePositionModel(), PositionSaveability, PreferredMoveComparison, RepertoirePositionRelationship (+5 more)

### Community 64 - "Community 64"
Cohesion: 0.24
Nodes (13): createMoveHistoryModel(), findMoveHistoryEntry(), MoveHistoryControlledModel, moveHistoryEntries(), MoveHistoryModel, HISTORY, MoveHistoryBounds, MoveHistoryEntry (+5 more)

### Community 65 - "Community 65"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 66 - "Community 66"
Cohesion: 0.12
Nodes (11): Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth, ForcedColorsAndReducedMotion, meta, PositiveBlack (+3 more)

### Community 67 - "Community 67"
Cohesion: 0.20
Nodes (14): PREFERRED_MOVE_SOURCE_FEN, expectDateFreePreferredPanel(), expectPositionReachFrequency(), expectPositionSquares(), expectPreferredActions(), expectPreferredMoveState(), expectSessionBoundary(), sharedPositionSummary() (+6 more)

### Community 68 - "Community 68"
Cohesion: 0.16
Nodes (8): @testing-library/user-event, vitest, booleanFilterData, data, here, LoaderHarnessProps, rawStyles, STARTING_FEN

### Community 69 - "Community 69"
Cohesion: 0.16
Nodes (12): src_api_client_trainingrequirementitemresponse, currentUtcDate(), OpeningCatalogueSnapshotResult, TrainingRequirementsResult, TrainerPracticeApi, createApi(), OPENING, page() (+4 more)

### Community 70 - "Community 70"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 71 - "Community 71"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 72 - "Community 72"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 73 - "Community 73"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 74 - "Community 74"
Cohesion: 0.21
Nodes (10): AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay(), missingDisplay() (+2 more)

### Community 75 - "Community 75"
Cohesion: 0.15
Nodes (11): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+3 more)

### Community 76 - "Community 76"
Cohesion: 0.19
Nodes (11): PreferredMoveClient, PreferredMoveMutationResult, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, BOARD_LABEL, CONTEXT, moveResponseDistributionResponse(), mutationResponse() (+3 more)

### Community 77 - "Community 77"
Cohesion: 0.26
Nodes (11): AnalysisClient, AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), StoryAnalysisLifecycleEvent (+3 more)

### Community 78 - "Community 78"
Cohesion: 0.26
Nodes (8): EvalBar(), EvalBarDisplayState, EvalBarProps, ExpectedDisplay, BoardEvalStage(), BoardEvalStageProps, boardVisualIn(), BoardOrientation

### Community 79 - "Community 79"
Cohesion: 0.23
Nodes (8): BoardControl(), BoardControlProps, InteractiveBoardAdapterProps, MoveHistoryControlledState, BoardContentProps, HistoryProps, RepertoireBoardLane(), RepertoireBoardLaneProps

### Community 80 - "Community 80"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 81 - "Community 81"
Cohesion: 0.17
Nodes (9): PositionPickerMoveRecord, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PreferredMoveRelationship, preferredMoveRelationshipFixtures, PreferredMoveStoryFixture (+1 more)

### Community 82 - "Community 82"
Cohesion: 0.20
Nodes (10): PreferredMovePanelProps, here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4 (+2 more)

### Community 83 - "Community 83"
Cohesion: 0.17
Nodes (11): LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate, expectActiveSessionHistoryEntry() (+3 more)

### Community 84 - "Community 84"
Cohesion: 0.23
Nodes (6): storybookViewports, src_styles_material_material_theme_builder_css_export_css_dark, createTestQueryClient(), QueryClientTestProviderProps, preview, StorybookQueryClientProvider()

### Community 85 - "Community 85"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 86 - "Community 86"
Cohesion: 0.24
Nodes (10): createMoveHistoryRows(), KEY_NAVIGATION, src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow (+2 more)

### Community 87 - "Community 87"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 88 - "Community 88"
Cohesion: 0.29
Nodes (8): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story

### Community 89 - "Community 89"
Cohesion: 0.25
Nodes (5): AnalysisResult, StateProbe(), Probe(), RESULT, useAnalysisState()

### Community 90 - "Community 90"
Cohesion: 0.29
Nodes (5): BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 91 - "Community 91"
Cohesion: 0.25
Nodes (5): Constrained, HISTORY, Interactive, meta, Story

### Community 92 - "Community 92"
Cohesion: 0.25
Nodes (5): here, HISTORY, moduleCss, MoveHistoryActivePlyChange, Ply

### Community 93 - "Community 93"
Cohesion: 0.25
Nodes (7): board, controls, evaluation, history, meta, Standard, Story

### Community 95 - "Community 95"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 96 - "Community 96"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 97 - "Community 97"
Cohesion: 0.38
Nodes (4): PageNotFoundView(), Default, meta, Story

### Community 98 - "Community 98"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 99 - "Community 99"
Cohesion: 0.47
Nodes (4): GAME, GAME_UUID, Game, PROMOTION_GAME

### Community 100 - "Community 100"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 101 - "Community 101"
Cohesion: 0.40
Nodes (4): storybook, Available, meta, Story

### Community 102 - "Community 102"
Cohesion: 0.50
Nodes (3): @testing-library/jest-dom, elementProto, topLayerPseudoSelectors

### Community 103 - "Community 103"
Cohesion: 0.50
Nodes (3): FEEDBACK_TOKENS, here, tokenCss

## Knowledge Gaps
- **835 isolated node(s):** `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind`, `OpeningLineLibraryResult`, `JsonRecord` (+830 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1061 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 13`, `Community 15`, `Community 18`, `Community 20`, `Community 21`, `Community 22`, `Community 24`, `Community 28`, `Community 31`, `Community 33`, `Community 34`, `Community 39`, `Community 41`, `Community 42`, `Community 43`, `Community 44`, `Community 46`, `Community 48`, `Community 52`, `Community 54`, `Community 55`, `Community 65`, `Community 66`, `Community 67`, `Community 68`, `Community 70`, `Community 71`, `Community 74`, `Community 76`, `Community 78`, `Community 84`, `Community 86`, `Community 89`, `Community 90`, `Community 91`, `Community 92`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Why does `vitest` connect `Community 68` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 11`, `Community 12`, `Community 14`, `Community 15`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 24`, `Community 30`, `Community 32`, `Community 33`, `Community 36`, `Community 37`, `Community 40`, `Community 42`, `Community 43`, `Community 44`, `Community 45`, `Community 46`, `Community 49`, `Community 51`, `Community 53`, `Community 55`, `Community 56`, `Community 57`, `Community 59`, `Community 61`, `Community 62`, `Community 63`, `Community 64`, `Community 69`, `Community 74`, `Community 76`, `Community 78`, `Community 79`, `Community 80`, `Community 82`, `Community 84`, `Community 85`, `Community 89`, `Community 90`, `Community 92`, `Community 96`, `Community 97`, `Community 98`, `Community 103`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Why does `@storybook/react-vite` connect `Community 10` to `Community 0`, `Community 1`, `Community 2`, `Community 5`, `Community 7`, `Community 11`, `Community 12`, `Community 15`, `Community 18`, `Community 20`, `Community 22`, `Community 24`, `Community 25`, `Community 29`, `Community 30`, `Community 31`, `Community 33`, `Community 37`, `Community 38`, `Community 39`, `Community 41`, `Community 45`, `Community 47`, `Community 49`, `Community 62`, `Community 65`, `Community 66`, `Community 67`, `Community 71`, `Community 75`, `Community 80`, `Community 83`, `Community 84`, `Community 85`, `Community 88`, `Community 91`, `Community 93`, `Community 97`, `Community 101`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `RepertoireBuilderWorkspace()` (e.g. with `PreferredMoveWorkflow.stories.tsx` and `createFreshSession()`) actually correct?**
  _`RepertoireBuilderWorkspace()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind` to the rest of the system?**
  _835 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05143638850889193 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06004543979227524 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
