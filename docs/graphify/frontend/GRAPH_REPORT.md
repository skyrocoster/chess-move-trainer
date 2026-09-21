# Graph Report - frontend  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2509 nodes · 5434 edges · 128 communities (122 shown, 6 thin omitted)
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
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125

## God Nodes (most connected - your core abstractions)
1. `react` - 86 edges
2. `vitest` - 78 edges
3. `@storybook/react-vite` - 58 edges
4. `@testing-library/react` - 49 edges
5. `RepertoireBuilderWorkspace()` - 36 edges
6. `storybook` - 35 edges
7. `chess.js` - 28 edges
8. `Fen` - 23 edges
9. `positionKeyFromFen()` - 23 edges
10. `@testing-library/user-event` - 22 edges

## Surprising Connections (you probably didn't know these)
- `StorybookQueryClientProvider()` --indirect_call--> `createTestQueryClient()`  [INFERRED]
  .storybook/StorybookQueryClientProvider.tsx → src/test-utils/QueryClientTestProvider.tsx
- `PreferredMoveDateValue()` --calls--> `formatUtcDate()`  [EXTRACTED]
  src/features/repertoire-builder/PreferredMovePrimitives.tsx → src/features/design-system/CalendarDateUtils.ts
- `RepertoireBuilderWorkspace()` --indirect_call--> `createFreshSession()`  [INFERRED]
  src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx → src/features/repertoire-builder/positionPickerSessionBoundary.ts
- `resetWorkspace()` --calls--> `resetSession()`  [EXTRACTED]
  src/features/repertoire-builder/RepertoireBuilderWorkspace.tsx → src/features/repertoire-builder/positionPickerSessionBoundary.ts
- `TrainerPracticePage()` --indirect_call--> `readOpeningCatalogueSnapshot()`  [INFERRED]
  src/features/trainer-practice/TrainerPracticePage.tsx → src/features/trainer-practice/openingCatalogueStorage.ts

## Import Cycles
- None detected.

## Communities (128 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (117): src_api_generated_index_analysisobservationerrorresponse, src_api_generated_index_analysisobservationlineresponse, src_api_generated_index_analysisobservationresponse, src_api_generated_index_analysisobservationresultresponse, src_api_generated_index_analysisrequestbody, src_api_generated_index_analysisrequesterrorresponse, src_api_generated_index_deletepreferredmoves, src_api_generated_index_deletepreferredmovesdata (+109 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (58): AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse, ClientOptions, DeletePreferredMovesError (+50 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (57): client, getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight() (+49 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (44): src_api_client_deletepreferredmoves, src_api_client_getpreferredmoves, src_api_client_preferredmovesmutationresponse, src_api_client_preferredmovesremovalresponse, src_api_client_preferredmovesresponse, src_api_client_preferredmovessegmentresponse, src_api_client_putpreferredmoves, deletePreferredMove() (+36 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (36): src_api_client_positioninsightresponse, failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isChessSide(), isNonnegativeInteger(), isRecord() (+28 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (37): @headless-tree/core, @headless-tree/react, LineLibrary(), nodeName(), sameIds(), selectionDescription(), booleanFilterData, data (+29 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (31): @storybook/react-vite, src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story (+23 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (29): src_api_client_getopenings, src_api_client_openingcatalogueitemresponse, src_api_client_submitpositiontraininganswer, src_api_client_trainingrequirementitemresponse, src_api_client_trainingrequirementresponse, currentUtcDate(), defaultTrainerPracticeApi, isValidAsOf() (+21 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (24): ref_axe_core, react-router-dom, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps, src_features_app_shell_appshell_module (+16 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (32): src_api_client_getanalysis, src_api_client_requestanalysis, AnalysisFailure, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis() (+24 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (34): src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+26 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (29): CreateClientConfig, BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys (+21 more)

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (33): deletePreferredMoves(), putPreferredMoves(), requestAnalysis(), submitPositionTrainingAnswer(), DeletePreferredMovesData, DeletePreferredMovesErrors, DeletePreferredMovesResponses, GetAnalysisErrors (+25 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (27): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+19 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (22): AnalysisLine, AnalysisObservation, AnalysisResult, analysisPanelDisplay(), AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage() (+14 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (21): PositionContextResponse, PositionReachFrequency(), PositionReachFrequencyProps, Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (23): AnalysisOperationResult, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, AFTER_NF3_FEN, BOARD_LABEL, CONTEXT (+15 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (18): AnalysisClient, AnalysisFailureCode, defaultAnalysisClient, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey(), AnalysisQueryError, DEFAULT_ANALYSIS_POLL_INTERVAL_MS, MAX_ANALYSIS_POLL_ATTEMPTS (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (25): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+17 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (28): expectPositionReachFrequency(), expectPositionSquares(), expectPreferredMoveState(), expectSessionBoundary(), expectSingleStagedStatus(), expectStagedStatus(), sharedPositionSummary(), verifyStandardWorkspace() (+20 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (22): chess.js, ChessSide, parseUciMove(), Ply, San, strictFen(), UciMove, GameMainLineOccurrence (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (28): src_api_client_getopeningsdata, src_api_client_getpositiontrainingrequirementsdata, src_api_client_openingcatalogueresponse, src_api_client_traininganswerresponse, abortError(), buildTrainingRequirementsQuery(), errorCode(), fetchOpeningChoices() (+20 more)

### Community 23 - "Community 23"
Cohesion: 0.11
Nodes (26): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+18 more)

### Community 24 - "Community 24"
Cohesion: 0.09
Nodes (21): react-resizable-panels, clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage() (+13 more)

### Community 25 - "Community 25"
Cohesion: 0.13
Nodes (21): src_api_client_getpositioninsight, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord, narrowInsightResponse() (+13 more)

### Community 26 - "Community 26"
Cohesion: 0.13
Nodes (23): createQuerySerializer(), formDataBodySerializer, QuerySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArraySeparatorStyle, ArrayStyle, MatrixStyle (+15 more)

### Community 27 - "Community 27"
Cohesion: 0.09
Nodes (23): engines, node, name, private, type, version, eslint, @eslint/js (+15 more)

### Community 28 - "Community 28"
Cohesion: 0.14
Nodes (25): GAME, GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession() (+17 more)

### Community 29 - "Community 29"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 30 - "Community 30"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 31 - "Community 31"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 32 - "Community 32"
Cohesion: 0.13
Nodes (19): src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, MoveResponseDistributionReply, MoveResponseDistributionResponse, MoveResponseDistributionControls(), MoveResponseDistributionControlsProps, CommonReplies (+11 more)

### Community 33 - "Community 33"
Cohesion: 0.14
Nodes (21): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+13 more)

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (24): booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys(), isRecord(), JsonRecord, NODE_KEYS, nodeBase() (+16 more)

### Community 35 - "Community 35"
Cohesion: 0.16
Nodes (22): createClient(), TODO: we probably want to return error and improve types, ReqInit, buildUrl(), checkForExistence(), createConfig(), createInterceptors(), defaultHeaders (+14 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (22): storyAnalysisClient(), PreferredMoveMutationResult, DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR, DEFAULT_MOVE, moveFromRequest(), moveResponseData(), removalMutationResponse(), saveMutationResponse() (+14 more)

### Community 37 - "Community 37"
Cohesion: 0.19
Nodes (22): GameMainLineModel, applySessionMove(), atIndex(), branchWithMove(), createFreshSession(), createSession(), importedPositions(), loadImportedSession() (+14 more)

### Community 38 - "Community 38"
Cohesion: 0.12
Nodes (21): SYNTHETIC_OPENING_RESPONSE, filterKind(), OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFailure, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType (+13 more)

### Community 39 - "Community 39"
Cohesion: 0.21
Nodes (16): @base-ui/react, lucide-react, react, AutocompleteProps, Combobox(), ComboboxProps, DropdownOptionContent(), DropdownOptionContentProps (+8 more)

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (19): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+11 more)

### Community 41 - "Community 41"
Cohesion: 0.11
Nodes (16): filterOpeningCatalogue(), src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, OpeningSelection, searchText(), TrainerColor (+8 more)

### Community 42 - "Community 42"
Cohesion: 0.16
Nodes (9): @chialab/vitest-axe, @testing-library/react, @testing-library/user-event, vitest, { shouldThrow }, here, LoaderHarnessProps, rawStyles (+1 more)

### Community 43 - "Community 43"
Cohesion: 0.13
Nodes (20): @fullcalendar/react, actionLabel(), formatDay(), formatRange(), src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction (+12 more)

### Community 44 - "Community 44"
Cohesion: 0.17
Nodes (17): src_api_client_getgame, useMoveResponseSelection(), PositionPickerSessionBoundary, SessionNavigation, SessionPosition, src_features_repertoire_builder_repertoirebuilderworkspace_module, RepertoireBuilderWorkspace(), resetWorkspace() (+9 more)

### Community 45 - "Community 45"
Cohesion: 0.12
Nodes (15): Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story (+7 more)

### Community 46 - "Community 46"
Cohesion: 0.14
Nodes (17): clearPending(), isPromotionCandidate(), PendingPromotion, PickerLiveRegion(), PROMOTION_OPTIONS, PromotionController, PromotionControllerOptions, promotionDescription() (+9 more)

### Community 47 - "Community 47"
Cohesion: 0.10
Nodes (14): catalogueDemoShell(), AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport, OPTIONS (+6 more)

### Community 48 - "Community 48"
Cohesion: 0.10
Nodes (20): AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, FirstChoice, FirstChoiceFromEmpty, Matching, meta, PendingRemove (+12 more)

### Community 49 - "Community 49"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 50 - "Community 50"
Cohesion: 0.15
Nodes (12): invalidatePreferredMove(), invalidateTrainingRequirements(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput, OptionalText, PositionInsightKeyInput (+4 more)

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (17): BoardAdapter(), BoardAdapterProps, src_features_board_adapter_boardadapter_module, src_features_board_adapter_boardadapter_starting_fen, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition, ExpandedPositionDescription (+9 more)

### Community 52 - "Community 52"
Cohesion: 0.12
Nodes (14): src_features_design_system_feedback_panelfeedback_module, PanelFeedback(), AllSeverities, meta, Story, meta, Story, TournamentAnalysisDesk (+6 more)

### Community 53 - "Community 53"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 54 - "Community 54"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 55 - "Community 55"
Cohesion: 0.13
Nodes (14): ref_node_fs, ref_node_path, ref_node_url, @storybook/addon-vitest, @vitest/browser-playwright, src_api_client_getpositiontrainingrequirements, ContractOperation, dirname (+6 more)

### Community 56 - "Community 56"
Cohesion: 0.16
Nodes (14): recharts, clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart() (+6 more)

### Community 57 - "Community 57"
Cohesion: 0.18
Nodes (11): @tanstack/react-query, src_api_client_gethealthoptions, StatusPage(), Default, meta, queryClient, Story, createTestQueryClient() (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.20
Nodes (16): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerStatus, BoardSquareHighlight, boardSquareStyles() (+8 more)

### Community 59 - "Community 59"
Cohesion: 0.22
Nodes (12): BoardAnswerPresentation, src_features_board_adapter_boardadapter_boardorientation, BranchMove, BranchSnapshot, InteractiveBoardMoveIntent, src_features_board_adapter_interactiveboardadapter_module, InteractiveBoardHarness(), InteractiveBoardHarnessProps (+4 more)

### Community 60 - "Community 60"
Cohesion: 0.19
Nodes (15): deriveLastMove(), lastMoveFromSquares(), lastMoveSquareStyles(), answerPresentation(), failureMessage(), learnerLabel(), src_features_trainer_practice_trainersession_module, MoveDetails (+7 more)

### Community 61 - "Community 61"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 62 - "Community 62"
Cohesion: 0.18
Nodes (14): react-chessboard, accessiblePieces, ChessboardPieceDropHandlerArgs, ChessboardSurface(), ChessboardSurfaceProps, findBoardSourceElement(), findBoardSquareElement(), PIECE_NAMES (+6 more)

### Community 63 - "Community 63"
Cohesion: 0.14
Nodes (12): react-error-boundary, PageContentBoundaryProps, src_features_design_system_feedback_pagefeedback_module, PageFeedback(), AllSeverities, meta, Story, ACCENT_TOKEN (+4 more)

### Community 64 - "Community 64"
Cohesion: 0.20
Nodes (14): typescript, collectStoryFiles(), collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue() (+6 more)

### Community 65 - "Community 65"
Cohesion: 0.14
Nodes (13): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelDisplay, AnalysisPanelIntent, AnalysisPanelLine, AnalysisPanelResult, AnalysisPanelResultMetadata, AnalysisPanelWdlValue (+5 more)

### Community 66 - "Community 66"
Cohesion: 0.22
Nodes (15): PositionContextFailureCode, contextFailureMessage(), failureMessage(), src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMovePanel(), statusLabel(), choiceBoxToneClass() (+7 more)

### Community 67 - "Community 67"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 68 - "Community 68"
Cohesion: 0.14
Nodes (13): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+5 more)

### Community 69 - "Community 69"
Cohesion: 0.25
Nodes (13): clampMoveHistoryPly(), findMoveHistoryEntry(), MoveHistoryControlledModel, MoveHistoryModel, navigateMoveHistory(), HISTORY, MoveHistoryBounds, MoveHistoryEntry (+5 more)

### Community 70 - "Community 70"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 71 - "Community 71"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 72 - "Community 72"
Cohesion: 0.25
Nodes (10): FeedbackCore(), here, moduleCss, SEVERITIES, TOKEN_SET, FEEDBACK_VARIANTS, FeedbackLiveRegionAttributes, FeedbackProps (+2 more)

### Community 73 - "Community 73"
Cohesion: 0.16
Nodes (7): MoveResponseDistributionResult, Probe(), useMoveResponseDistributionState(), Probe(), useInjectedPositionContextState(), usePositionContextState(), Consumers()

### Community 74 - "Community 74"
Cohesion: 0.22
Nodes (12): PreferredMoveFailureCode, PreferredMoveReader, PreferredMoveResponse, PreferredMoveResult, PreferredMoveQueryError, PreferredMoveReadState, queryPreferredMove(), PreferredMoveOutput() (+4 more)

### Community 75 - "Community 75"
Cohesion: 0.19
Nodes (11): src_api_client_gamedetailresponse, GameDetailQueryError, queryGameDetail(), useGameDetailQuery(), SessionMove, PreferredMoveClient, failureCode(), loadFailure() (+3 more)

### Community 76 - "Community 76"
Cohesion: 0.16
Nodes (9): Autocomplete(), RadioGroup(), RadioGroupProps, RadioOption, OPTIONS, Select(), TextInput(), TextInputProps (+1 more)

### Community 77 - "Community 77"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 78 - "Community 78"
Cohesion: 0.18
Nodes (12): RepertoireSessionPanel(), RepertoireSessionPanelProps, FrequencyAbsent, FrequencyUnavailable, FrequencyZero, LocalLineSession, meta, model() (+4 more)

### Community 79 - "Community 79"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 80 - "Community 80"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 81 - "Community 81"
Cohesion: 0.21
Nodes (10): AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay(), missingDisplay() (+2 more)

### Community 82 - "Community 82"
Cohesion: 0.15
Nodes (11): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+3 more)

### Community 83 - "Community 83"
Cohesion: 0.17
Nodes (10): GameLoader(), handleSubmit(), GameLoaderFailureKind, GameLoaderProps, GameLoaderStatus, GameLoaderValues, src_features_game_gameloader_module, validationMessage() (+2 more)

### Community 84 - "Community 84"
Cohesion: 0.15
Nodes (10): PositionPickerMoveRecord, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PREFERRED_MOVE_SOURCE_FEN, PreferredMoveRelationship, preferredMoveRelationshipFixtures (+2 more)

### Community 85 - "Community 85"
Cohesion: 0.19
Nodes (12): defaultPreferredMoveClient, PreferredMoveMutationKind, moveFromUci(), PendingRefresh, PositionPickerMove, PreferredMoveDateCapability, PreferredMoveWorkflowState, sessionMove() (+4 more)

### Community 86 - "Community 86"
Cohesion: 0.18
Nodes (11): PreferredMovePanelProps, here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4 (+3 more)

### Community 87 - "Community 87"
Cohesion: 0.17
Nodes (10): storybook, Available, meta, Story, expectDateFreePreferredPanel(), expectPreferredActions(), StoryPreferredMoveRequest, CleanPreferredTimelineNovelParent (+2 more)

### Community 88 - "Community 88"
Cohesion: 0.39
Nodes (11): invalidateAnalysisObservation(), invalidatePositionInsight(), src_features_analysis_analysisapi_positionkeyfromfen, changedObservation(), failureMessage(), mergeObservation(), observationFingerprint(), useDefaultAnalysisState() (+3 more)

### Community 89 - "Community 89"
Cohesion: 0.26
Nodes (11): AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), StoryAnalysisLifecycleEvent, storyCandidateAnalysisClient() (+3 more)

### Community 90 - "Community 90"
Cohesion: 0.26
Nodes (8): EvalBar(), EvalBarDisplayState, EvalBarProps, ExpectedDisplay, BoardEvalStage(), BoardEvalStageProps, boardVisualIn(), BoardOrientation

### Community 91 - "Community 91"
Cohesion: 0.17
Nodes (11): Cancellation, ConstrainedDrawer, defaultArgs, ForcedColorsAndReducedMotion, KeyboardSelection, meta, NativeKeyboardPromotionInitiation, StaleAndIllegalRejection (+3 more)

### Community 92 - "Community 92"
Cohesion: 0.17
Nodes (10): InlineFeedback(), HEADINGS, InlineMatrix, MESSAGES, meta, SEVERITIES, Story, here (+2 more)

### Community 93 - "Community 93"
Cohesion: 0.17
Nodes (11): LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate, expectActiveSessionHistoryEntry() (+3 more)

### Community 94 - "Community 94"
Cohesion: 0.20
Nodes (8): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent

### Community 95 - "Community 95"
Cohesion: 0.22
Nodes (7): meta, ResponsiveAccessibilityReview, Story, StorySpecimenAccessibilityReview(), here, moduleCss, tokenCss

### Community 96 - "Community 96"
Cohesion: 0.24
Nodes (10): createMoveHistoryRows(), KEY_NAVIGATION, src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow (+2 more)

### Community 97 - "Community 97"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 98 - "Community 98"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 99 - "Community 99"
Cohesion: 0.20
Nodes (4): ChartLabel, here, rawStyles, MoveResponseDistributionClient

### Community 100 - "Community 100"
Cohesion: 0.22
Nodes (7): StatusViewProps, StatusViewState, Healthy, Loading, meta, Story, Unavailable

### Community 101 - "Community 101"
Cohesion: 0.25
Nodes (6): BoardRender(), PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, stripPackageSemantics(), src_features_board_adapter_positiondescription_boardorientation, PositionModel

### Community 102 - "Community 102"
Cohesion: 0.28
Nodes (7): BoardControl(), BoardControlProps, InteractiveBoardAdapterProps, MoveHistoryControlledState, BoardContentProps, HistoryProps, RepertoireBoardLaneProps

### Community 103 - "Community 103"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 104 - "Community 104"
Cohesion: 0.22
Nodes (6): Constrained, HISTORY, Interactive, meta, Story, MoveHistoryInput

### Community 105 - "Community 105"
Cohesion: 0.22
Nodes (8): RepertoireBoardLane(), board, controls, evaluation, history, meta, Standard, Story

### Community 106 - "Community 106"
Cohesion: 0.22
Nodes (4): fixture(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 107 - "Community 107"
Cohesion: 0.29
Nodes (5): BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 108 - "Community 108"
Cohesion: 0.29
Nodes (7): actionClass(), RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story

### Community 110 - "Community 110"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 111 - "Community 111"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 112 - "Community 112"
Cohesion: 0.29
Nodes (4): HealthyContent, meta, Story, UnexpectedFailureTryAgain

### Community 113 - "Community 113"
Cohesion: 0.38
Nodes (4): PageNotFoundView(), Default, meta, Story

### Community 114 - "Community 114"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 115 - "Community 115"
Cohesion: 0.29
Nodes (4): here, HISTORY, moduleCss, MoveHistoryActivePlyChange

### Community 116 - "Community 116"
Cohesion: 0.87
Nodes (6): useInjectedAnalysisState(), fail(), observe(), poll(), schedulePoll(), stopTimer()

### Community 117 - "Community 117"
Cohesion: 0.33
Nodes (5): MESSAGES, meta, SemanticVariants, SEVERITIES, Story

### Community 118 - "Community 118"
Cohesion: 0.33
Nodes (5): FeedbackSeverity, here, moduleCss, SEVERITIES, TOKEN_SET

### Community 119 - "Community 119"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 120 - "Community 120"
Cohesion: 0.60
Nodes (3): GAME_UUID, Game, PROMOTION_GAME

### Community 121 - "Community 121"
Cohesion: 0.50
Nodes (3): @testing-library/jest-dom, elementProto, topLayerPseudoSelectors

### Community 122 - "Community 122"
Cohesion: 0.50
Nodes (3): FEEDBACK_TOKENS, here, tokenCss

## Knowledge Gaps
- **839 isolated node(s):** `Story`, `StatusViewProps`, `Story`, `BoardContentProps`, `HistoryProps` (+834 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1183 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 39` to `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 10`, `Community 13`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 23`, `Community 24`, `Community 25`, `Community 27`, `Community 32`, `Community 36`, `Community 41`, `Community 42`, `Community 43`, `Community 44`, `Community 45`, `Community 46`, `Community 47`, `Community 56`, `Community 57`, `Community 58`, `Community 59`, `Community 60`, `Community 62`, `Community 66`, `Community 70`, `Community 71`, `Community 72`, `Community 74`, `Community 76`, `Community 77`, `Community 81`, `Community 83`, `Community 85`, `Community 87`, `Community 88`, `Community 90`, `Community 94`, `Community 96`, `Community 101`, `Community 103`, `Community 104`, `Community 107`, `Community 112`, `Community 115`?**
  _High betweenness centrality (0.230) - this node is a cross-community bridge._
- **Why does `vitest` connect `Community 42` to `Community 3`, `Community 4`, `Community 5`, `Community 7`, `Community 8`, `Community 9`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 21`, `Community 23`, `Community 25`, `Community 27`, `Community 28`, `Community 32`, `Community 33`, `Community 37`, `Community 38`, `Community 40`, `Community 45`, `Community 46`, `Community 50`, `Community 52`, `Community 53`, `Community 55`, `Community 57`, `Community 58`, `Community 59`, `Community 60`, `Community 61`, `Community 63`, `Community 64`, `Community 68`, `Community 69`, `Community 72`, `Community 73`, `Community 74`, `Community 76`, `Community 81`, `Community 86`, `Community 90`, `Community 92`, `Community 95`, `Community 99`, `Community 106`, `Community 107`, `Community 111`, `Community 113`, `Community 114`, `Community 115`, `Community 118`, `Community 122`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `@storybook/react-vite` connect `Community 6` to `Community 5`, `Community 8`, `Community 10`, `Community 13`, `Community 15`, `Community 18`, `Community 19`, `Community 20`, `Community 23`, `Community 24`, `Community 27`, `Community 29`, `Community 31`, `Community 32`, `Community 33`, `Community 43`, `Community 45`, `Community 47`, `Community 48`, `Community 49`, `Community 51`, `Community 52`, `Community 53`, `Community 57`, `Community 62`, `Community 63`, `Community 68`, `Community 70`, `Community 77`, `Community 78`, `Community 82`, `Community 87`, `Community 91`, `Community 92`, `Community 93`, `Community 94`, `Community 95`, `Community 98`, `Community 100`, `Community 103`, `Community 104`, `Community 105`, `Community 108`, `Community 112`, `Community 113`, `Community 117`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `RepertoireBuilderWorkspace()` (e.g. with `PreferredMoveWorkflow.stories.tsx` and `createFreshSession()`) actually correct?**
  _`RepertoireBuilderWorkspace()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Story`, `StatusViewProps`, `Story` to the rest of the system?**
  _839 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.01694915254237288 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06610169491525424 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
