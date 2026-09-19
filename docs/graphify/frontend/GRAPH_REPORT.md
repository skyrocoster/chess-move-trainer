# Graph Report - frontend  (2026-09-15)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2316 nodes · 5167 edges · 125 communities (116 shown, 7 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 67 edges (avg confidence: 0.85)
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

## God Nodes (most connected - your core abstractions)
1. `react` - 83 edges
2. `vitest` - 77 edges
3. `@storybook/react-vite` - 57 edges
4. `@testing-library/react` - 49 edges
5. `RepertoireBuilderWorkspace()` - 36 edges
6. `chess.js` - 26 edges
7. `positionKeyFromFen()` - 24 edges
8. `Fen` - 23 edges
9. `@testing-library/user-event` - 22 edges
10. `ChessSide` - 19 edges

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

## Communities (125 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (77): AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry, FailureFixture() (+69 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (68): @headless-tree/core, @headless-tree/react, LineLibrary(), nodeName(), sameIds(), selectionDescription(), Default, Empty (+60 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (65): GameDetailResponse, analysisPanelDisplay(), BranchMove, Ply, San, GameLoader(), handleSubmit(), GameLoaderFailureKind (+57 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (62): defaultPreferredMoveClient, deletePreferredMove(), failureFromOperation(), fetchPreferredMove(), formatUtcDate(), getPreferredMoveDateWindow(), hasExactKeys(), isCanonicalFen() (+54 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (55): AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse, ClientOptions, DeletePreferredMovesError (+47 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (36): lucide-react, react, AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport (+28 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (51): getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight(), getPreferredMoves() (+43 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (16): @chialab/vitest-axe, @testing-library/react, @testing-library/user-event, vitest, ExpectedDisplay, booleanFilterData, data, here (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (27): failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isChessSide(), isNonnegativeInteger(), isRecord(), JsonRecord (+19 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (29): CreateClientConfig, BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys (+21 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (27): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, Blank, calendarDayName(), CalendarFixtureProps, Clearable (+19 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (22): AnalysisLine, AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv(), formatScore(), formatWdl() (+14 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (23): AnalysisOperationResult, MoveResponseDistributionResult, PreferredMoveMutationResult, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, AFTER_NF3_FEN (+15 more)

### Community 13 - "Community 13"
Cohesion: 0.07
Nodes (29): client, deletePreferredMoves(), putPreferredMoves(), requestAnalysis(), DeletePreferredMovesData, DeletePreferredMovesResponses, GetAnalysisResponses, GetGameData (+21 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 15 - "Community 15"
Cohesion: 0.07
Nodes (29): devDependencies, @axe-core/playwright, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts (+21 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (26): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+18 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (27): expectActiveSessionHistoryEntry(), expectDateFreePreferredPanel(), expectPreferredActions(), expectSessionHistory(), expectSingleStagedStatus(), expectStagedStatus(), AbsentUnsavable, AccessibilityAndResponsive (+19 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (26): name, private, type, version, @axe-core/playwright, @base-ui/react, eslint, @eslint/js (+18 more)

### Community 19 - "Community 19"
Cohesion: 0.10
Nodes (21): react-resizable-panels, clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), panelSpaceForGroup(), panelSpaceForStage() (+13 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (17): react-router-dom, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps, ConstrainedClosed, ConstrainedOpen (+9 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (23): createQuerySerializer(), formDataBodySerializer, QuerySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArraySeparatorStyle, ArrayStyle, MatrixStyle (+15 more)

### Community 22 - "Community 22"
Cohesion: 0.14
Nodes (19): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+11 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (25): GAME, GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession() (+17 more)

### Community 24 - "Community 24"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 25 - "Community 25"
Cohesion: 0.09
Nodes (26): expectPositionReachFrequency(), expectPositionSquares(), expectPreferredMoveState(), expectSessionBoundary(), sharedPositionSummary(), expectNoHorizontalOverflow(), Accessibility, CandidateActivation (+18 more)

### Community 26 - "Community 26"
Cohesion: 0.09
Nodes (23): react-chessboard, PromotionColor, PromotionCommit, PromotionPresentation, Cancellation, ConstrainedDrawer, defaultArgs, ForcedColorsAndReducedMotion (+15 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (25): AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis(), invalidFenResult(), isCanonicalFen(), isFailureCode() (+17 more)

### Community 28 - "Community 28"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 29 - "Community 29"
Cohesion: 0.14
Nodes (21): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+13 more)

### Community 30 - "Community 30"
Cohesion: 0.15
Nodes (21): Fen, failureFromInsight(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord, narrowInsightResponse(), PositionContextClient (+13 more)

### Community 31 - "Community 31"
Cohesion: 0.14
Nodes (18): MoveResponseDistribution(), MoveResponseDistributionPanel, MoveResponseDistributionReply, MoveResponseDistributionResponse, MoveResponseDistributionControls(), MoveResponseDistributionControlsProps, CommonReplies, meta (+10 more)

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (22): createClient(), TODO: we probably want to return error and improve types, ReqInit, buildUrl(), checkForExistence(), createConfig(), createInterceptors(), defaultHeaders (+14 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (15): OpeningCatalogueItemResponse, ALL_OPENINGS_VALUE, filterOpeningCatalogue(), OPENING_SEARCH_VISIBLE_LIMIT, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, OpeningSelection (+7 more)

### Community 34 - "Community 34"
Cohesion: 0.14
Nodes (21): PreferredMoveClient, DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR, DEFAULT_MOVE, moveFromRequest(), moveResponseData(), mutationResponse(), STORY_BLACK_SUBJECT_GAME_DETAIL, STORY_GAME_DETAIL (+13 more)

### Community 35 - "Community 35"
Cohesion: 0.14
Nodes (22): abortError(), buildTrainingRequirementsQuery(), errorCode(), fetchOpeningChoices(), fetchOpeningPage(), fetchTrainingRequirements(), hasValidCataloguePage(), isAbortError() (+14 more)

### Community 36 - "Community 36"
Cohesion: 0.13
Nodes (17): recharts, clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart() (+9 more)

### Community 37 - "Community 37"
Cohesion: 0.18
Nodes (19): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerStatus, BoardSquareHighlight, boardSquareStyles() (+11 more)

### Community 38 - "Community 38"
Cohesion: 0.17
Nodes (18): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+10 more)

### Community 39 - "Community 39"
Cohesion: 0.14
Nodes (19): @fullcalendar/react, actionLabel(), formatDay(), formatRange(), oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction, PreferredMoveSchedulePeriod (+11 more)

### Community 40 - "Community 40"
Cohesion: 0.15
Nodes (13): AnalysisFailureCode, AnalysisObservation, defaultAnalysisClient, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey(), AnalysisQueryError, DEFAULT_ANALYSIS_POLL_INTERVAL_MS, MAX_ANALYSIS_POLL_ATTEMPTS (+5 more)

### Community 41 - "Community 41"
Cohesion: 0.15
Nodes (17): clearPending(), isPromotionCandidate(), isPromotionTarget(), PendingPromotion, PickerLiveRegion(), PROMOTION_OPTIONS, PromotionController, PromotionControllerOptions (+9 more)

### Community 42 - "Community 42"
Cohesion: 0.15
Nodes (14): currentUtcDate(), defaultTrainerPracticeApi, isValidAsOf(), queryOpeningCatalogueSnapshot(), queryOpeningChoices(), queryTrainingRequirements(), OPENING, selectedFilters (+6 more)

### Community 43 - "Community 43"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 44 - "Community 44"
Cohesion: 0.13
Nodes (14): Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story (+6 more)

### Community 45 - "Community 45"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 46 - "Community 46"
Cohesion: 0.17
Nodes (12): requestPositionInsight(), validatePositionContextFen(), currentUtcDate(), isValidRawInsight(), POSITION_INSIGHT_GC_TIME, POSITION_INSIGHT_STALE_TIME, PositionInsightQueryError, PositionInsightQueryErrorKind (+4 more)

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 48 - "Community 48"
Cohesion: 0.21
Nodes (11): BoardAnswerPresentation, BranchSnapshot, InteractiveBoardMoveIntent, InteractiveBoardHarness(), InteractiveBoardHarnessProps, terminalDescription(), deriveLastMove(), LAST_MOVE_SQUARE_STYLE (+3 more)

### Community 49 - "Community 49"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 50 - "Community 50"
Cohesion: 0.12
Nodes (17): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+9 more)

### Community 51 - "Community 51"
Cohesion: 0.21
Nodes (14): typescript, collectStoryFiles(), collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue() (+6 more)

### Community 52 - "Community 52"
Cohesion: 0.20
Nodes (11): ChessSide, PositionContextResponse, PositionReachFrequency(), PositionReachFrequencyProps, BasePositionReachFrequencyModel, boundedPercentage(), colorLabel(), derivePositionReachFrequencyModel() (+3 more)

### Community 53 - "Community 53"
Cohesion: 0.21
Nodes (15): contextFailureMessage(), failureMessage(), mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), statusLabel(), choiceBoxToneClass(), PanelError() (+7 more)

### Community 54 - "Community 54"
Cohesion: 0.21
Nodes (13): chess.js, invalidatePreferredMove(), invalidateTrainingRequirements(), strictFen(), moveFromUci(), PendingRefresh, PositionPickerMove, PreferredMoveWorkflowState (+5 more)

### Community 55 - "Community 55"
Cohesion: 0.17
Nodes (10): AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey(), OpeningsCatalogueKeyInput, OptionalText, PositionInsightKeyInput, PreferredMoveKeyInput, queryKeyPrefixes (+2 more)

### Community 56 - "Community 56"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 57 - "Community 57"
Cohesion: 0.12
Nodes (11): Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth, ForcedColorsAndReducedMotion, meta, PositiveBlack (+3 more)

### Community 58 - "Community 58"
Cohesion: 0.19
Nodes (13): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), ScrollState, scrollStateFor(), TabDefinition (+5 more)

### Community 59 - "Community 59"
Cohesion: 0.16
Nodes (12): CatalogueLink, DemoRow(), DemoRowProps, FamilyPage(), FamilyPageProps, storyHref(), Docs, meta (+4 more)

### Community 60 - "Community 60"
Cohesion: 0.15
Nodes (12): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+4 more)

### Community 61 - "Community 61"
Cohesion: 0.19
Nodes (12): sanFromFenAndUci(), SelectedTransition, PreferredMoveValue, colorLabel(), deriveRepertoirePositionModel(), PositionSaveability, PreferredMoveComparison, RepertoirePositionRelationship (+4 more)

### Community 62 - "Community 62"
Cohesion: 0.16
Nodes (7): react-error-boundary, PageContentBoundary(), PageContentBoundaryProps, HealthyContent, meta, Story, UnexpectedFailureTryAgain

### Community 63 - "Community 63"
Cohesion: 0.35
Nodes (12): @tanstack/react-query, invalidateAnalysisObservation(), invalidatePositionInsight(), AnalysisFailure, changedObservation(), failureMessage(), mergeObservation(), observationFingerprint() (+4 more)

### Community 64 - "Community 64"
Cohesion: 0.22
Nodes (13): AnalysisClient, AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient() (+5 more)

### Community 65 - "Community 65"
Cohesion: 0.18
Nodes (10): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelIntent, AnalysisPanelResult, AnalysisPanelResultMetadata, InlineWdl(), resultMetadataLabel(), WdlItem (+2 more)

### Community 66 - "Community 66"
Cohesion: 0.19
Nodes (11): AnalysisPanelLine, AnalysisPanelWdl, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay() (+3 more)

### Community 67 - "Community 67"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 68 - "Community 68"
Cohesion: 0.18
Nodes (12): RepertoireSessionPanel(), RepertoireSessionPanelProps, FrequencyAbsent, FrequencyUnavailable, FrequencyZero, LocalLineSession, meta, model() (+4 more)

### Community 69 - "Community 69"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 70 - "Community 70"
Cohesion: 0.19
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 71 - "Community 71"
Cohesion: 0.19
Nodes (9): InlineFeedback(), StatusView(), StatusViewProps, StatusViewState, Healthy, Loading, meta, Story (+1 more)

### Community 72 - "Community 72"
Cohesion: 0.15
Nodes (10): PositionPickerMoveRecord, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PREFERRED_MOVE_SOURCE_FEN, PreferredMoveRelationship, preferredMoveRelationshipFixtures (+2 more)

### Community 73 - "Community 73"
Cohesion: 0.18
Nodes (11): PreferredMovePanelProps, here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4 (+3 more)

### Community 74 - "Community 74"
Cohesion: 0.19
Nodes (10): OpeningCatalogueSnapshotResult, TrainingRequirementsResult, TrainerPracticeApi, createApi(), OPENING, page(), renderPage(), renderReady() (+2 more)

### Community 75 - "Community 75"
Cohesion: 0.20
Nodes (7): BoardAdapter(), BoardRender(), PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, stripPackageSemantics(), { shouldThrow }, PositionModel

### Community 76 - "Community 76"
Cohesion: 0.17
Nodes (11): BoardAdapterProps, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition, ExpandedPositionDescription, HiddenCoordinates, InvalidFen, meta (+3 more)

### Community 77 - "Community 77"
Cohesion: 0.17
Nodes (10): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+2 more)

### Community 78 - "Community 78"
Cohesion: 0.20
Nodes (8): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent

### Community 79 - "Community 79"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 80 - "Community 80"
Cohesion: 0.20
Nodes (8): here, HISTORY, moduleCss, MoveHistoryActivePlyChange, MoveHistoryInitialPosition, MoveHistoryMove, Ply, San

### Community 81 - "Community 81"
Cohesion: 0.29
Nodes (10): clampMoveHistoryPly(), createMoveHistoryModel(), findMoveHistoryEntry(), MoveHistoryControlledModel, moveHistoryEntries(), MoveHistoryModel, navigateMoveHistory(), HISTORY (+2 more)

### Community 82 - "Community 82"
Cohesion: 0.27
Nodes (8): EvalBar(), EvalBarProps, BoardEvalStage(), boardVisualIn(), meta, StartingPosition, Story, BoardOrientation

### Community 83 - "Community 83"
Cohesion: 0.18
Nodes (9): PageFeedback(), AllSeverities, meta, Story, ACCENT_TOKEN, CONTAINER_TOKEN, here, moduleCss (+1 more)

### Community 84 - "Community 84"
Cohesion: 0.22
Nodes (7): meta, ResponsiveAccessibilityReview, Story, StorySpecimenAccessibilityReview(), here, moduleCss, tokenCss

### Community 85 - "Community 85"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 86 - "Community 86"
Cohesion: 0.27
Nodes (7): BoardControl(), BoardControlProps, BoardEvalStageProps, InteractiveBoardAdapterProps, BoardContentProps, HistoryProps, RepertoireBoardLaneProps

### Community 87 - "Community 87"
Cohesion: 0.20
Nodes (8): PanelFeedback(), AllSeverities, meta, Story, here, moduleCss, SEVERITIES, TOKEN_SET

### Community 88 - "Community 88"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 89 - "Community 89"
Cohesion: 0.29
Nodes (8): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story

### Community 90 - "Community 90"
Cohesion: 0.20
Nodes (9): LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate, loadGame() (+1 more)

### Community 91 - "Community 91"
Cohesion: 0.25
Nodes (5): AnalysisResult, StateProbe(), Probe(), RESULT, useAnalysisState()

### Community 92 - "Community 92"
Cohesion: 0.22
Nodes (8): RepertoireBoardLane(), board, controls, evaluation, history, meta, Standard, Story

### Community 93 - "Community 93"
Cohesion: 0.25
Nodes (4): generatedRequestAnalysisMock, getAnalysisMock, LINE, RESULT

### Community 94 - "Community 94"
Cohesion: 0.29
Nodes (5): BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 95 - "Community 95"
Cohesion: 0.25
Nodes (5): Constrained, HISTORY, Interactive, meta, Story

### Community 96 - "Community 96"
Cohesion: 0.32
Nodes (4): fetchPositionContext(), requestAsOf(), jsonResponse(), resolveInsightResult()

### Community 97 - "Community 97"
Cohesion: 0.29
Nodes (5): @storybook/react-vite, Docs, meta, Story, config

### Community 99 - "Community 99"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 100 - "Community 100"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 101 - "Community 101"
Cohesion: 0.33
Nodes (5): ALLOWED_RUNTIME_CLIENT_IMPORTS, collectProductionSourceFiles(), dirname, SOURCE_EXTENSIONS, srcDir

### Community 102 - "Community 102"
Cohesion: 0.38
Nodes (4): PageNotFoundView(), Default, meta, Story

### Community 103 - "Community 103"
Cohesion: 0.29
Nodes (6): HEADINGS, InlineMatrix, MESSAGES, meta, SEVERITIES, Story

### Community 104 - "Community 104"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 105 - "Community 105"
Cohesion: 0.43
Nodes (6): KEY_NAVIGATION, MoveHistoryProps, MoveHistoryRow, MoveHistoryControlledState, MoveHistoryEntry, MoveHistoryInput

### Community 106 - "Community 106"
Cohesion: 0.33
Nodes (4): vite, @vitejs/plugin-react, @vitest/browser-playwright, dirname

### Community 107 - "Community 107"
Cohesion: 0.33
Nodes (5): getPositionTrainingRequirements(), getPositionTrainingRequirementsOptions(), getPositionTrainingRequirementsQueryKey(), ContractOperation, dirname

### Community 108 - "Community 108"
Cohesion: 0.93
Nodes (6): useInjectedAnalysisState(), fail(), observe(), poll(), schedulePoll(), stopTimer()

### Community 109 - "Community 109"
Cohesion: 0.33
Nodes (4): Docs, meta, Story, CatalogueSection

### Community 110 - "Community 110"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 111 - "Community 111"
Cohesion: 0.60
Nodes (3): GAME_UUID, Game, PROMOTION_GAME

### Community 112 - "Community 112"
Cohesion: 0.50
Nodes (3): Docs, meta, Story

### Community 113 - "Community 113"
Cohesion: 0.50
Nodes (3): Docs, meta, Story

### Community 114 - "Community 114"
Cohesion: 0.50
Nodes (3): Docs, meta, Story

### Community 115 - "Community 115"
Cohesion: 0.50
Nodes (3): FEEDBACK_TOKENS, here, tokenCss

### Community 116 - "Community 116"
Cohesion: 0.67
Nodes (4): createMoveHistoryRows(), MoveHistory(), handleKeyDown(), renderEntry()

## Knowledge Gaps
- **844 isolated node(s):** `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind`, `OpeningLineLibraryResult`, `JsonRecord` (+839 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1039 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 7`, `Community 8`, `Community 10`, `Community 12`, `Community 14`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 25`, `Community 26`, `Community 30`, `Community 31`, `Community 33`, `Community 34`, `Community 36`, `Community 37`, `Community 39`, `Community 40`, `Community 41`, `Community 42`, `Community 44`, `Community 48`, `Community 52`, `Community 53`, `Community 54`, `Community 56`, `Community 57`, `Community 58`, `Community 59`, `Community 62`, `Community 63`, `Community 66`, `Community 67`, `Community 75`, `Community 78`, `Community 80`, `Community 82`, `Community 91`, `Community 94`, `Community 95`, `Community 105`?**
  _High betweenness centrality (0.274) - this node is a cross-community bridge._
- **Why does `vitest` connect `Community 7` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 8`, `Community 10`, `Community 11`, `Community 12`, `Community 16`, `Community 18`, `Community 20`, `Community 22`, `Community 23`, `Community 29`, `Community 30`, `Community 31`, `Community 37`, `Community 38`, `Community 40`, `Community 41`, `Community 42`, `Community 44`, `Community 45`, `Community 46`, `Community 48`, `Community 49`, `Community 51`, `Community 52`, `Community 54`, `Community 55`, `Community 60`, `Community 61`, `Community 62`, `Community 63`, `Community 66`, `Community 71`, `Community 73`, `Community 74`, `Community 75`, `Community 78`, `Community 79`, `Community 80`, `Community 81`, `Community 83`, `Community 84`, `Community 86`, `Community 87`, `Community 91`, `Community 93`, `Community 94`, `Community 96`, `Community 100`, `Community 101`, `Community 102`, `Community 104`, `Community 107`, `Community 115`?**
  _High betweenness centrality (0.180) - this node is a cross-community bridge._
- **Why does `@storybook/react-vite` connect `Community 97` to `Community 0`, `Community 1`, `Community 3`, `Community 5`, `Community 10`, `Community 14`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 24`, `Community 25`, `Community 26`, `Community 28`, `Community 29`, `Community 31`, `Community 36`, `Community 39`, `Community 43`, `Community 44`, `Community 45`, `Community 56`, `Community 57`, `Community 59`, `Community 60`, `Community 62`, `Community 67`, `Community 68`, `Community 71`, `Community 76`, `Community 77`, `Community 78`, `Community 79`, `Community 82`, `Community 83`, `Community 84`, `Community 87`, `Community 88`, `Community 89`, `Community 90`, `Community 92`, `Community 95`, `Community 102`, `Community 103`, `Community 109`, `Community 112`, `Community 113`, `Community 114`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `RepertoireBuilderWorkspace()` (e.g. with `PreferredMoveWorkflow.stories.tsx` and `createFreshSession()`) actually correct?**
  _`RepertoireBuilderWorkspace()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Story`, `OpeningLineLibraryFailure`, `OpeningLineLibraryNodeKind` to the rest of the system?**
  _844 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.053069420539300055 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05949367088607595 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
