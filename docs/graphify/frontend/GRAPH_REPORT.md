# Graph Report - frontend  (2026-09-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2858 nodes · 6249 edges · 254 communities (127 shown, 127 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 95 edges (avg confidence: 0.85)
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
- Community 246
- Community 247
- Community 248
- Community 249
- Community 250
- Community 251

## God Nodes (most connected - your core abstractions)
1. `react` - 115 edges
2. `vitest` - 86 edges
3. `@storybook/react-vite` - 67 edges
4. `@testing-library/react` - 56 edges
5. `storybook` - 41 edges
6. `RepertoireBuilderWorkspace()` - 36 edges
7. `@base-ui/react` - 32 edges
8. `chess.js` - 28 edges
9. `@testing-library/user-event` - 27 edges
10. `Fen` - 23 edges

## Surprising Connections (you probably didn't know these)
- `StorybookQueryClientProvider()` --indirect_call--> `createTestQueryClient()`  [INFERRED]
  .storybook/StorybookQueryClientProvider.tsx → src/test-utils/QueryClientTestProvider.tsx
- `handleKeyDown()` --indirect_call--> `model()`  [INFERRED]
  src/features/move-history/MoveHistory.tsx → src/features/repertoire-builder/RepertoireSessionPanel.stories.tsx
- `PreferredMoveDateValue()` --calls--> `formatUtcDate()`  [EXTRACTED]
  src/features/repertoire-builder/PreferredMovePrimitives.tsx → src/features/design-system/CalendarDateUtils.ts
- `TrainerPracticePage()` --indirect_call--> `readOpeningCatalogueSnapshot()`  [INFERRED]
  src/features/trainer-practice/TrainerPracticePage.tsx → src/features/trainer-practice/openingCatalogueStorage.ts
- `SyntheticOpeningBrowserProps` --references--> `LineLibraryCommitDescription`  [EXTRACTED]
  src/features/openings/OpeningLineLibrary.stories.tsx → src/features/design-system/line-library/lineLibraryTypes.ts

## Import Cycles
- None detected.

## Communities (254 total, 127 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (83): ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse (+75 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (63): client, getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight() (+55 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (37): FeedbackCore(), MESSAGES, meta, SemanticVariants, SEVERITIES, Story, here, moduleCss (+29 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (44): src_api_client_deletepreferredmoves, src_api_client_getpreferredmoves, src_api_client_preferredmovesmutationresponse, src_api_client_preferredmovesremovalresponse, src_api_client_preferredmovesresponse, src_api_client_preferredmovessegmentresponse, src_api_client_putpreferredmoves, deletePreferredMove() (+36 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (34): src_features_design_system_form_controls_advancedformcontrols_module, CheckboxGroupExample, FieldsetExample, FormExample, meta, NumberFieldExample, OtpFieldExample, SliderExample (+26 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (37): @headless-tree/core, @headless-tree/react, LineLibrary(), nodeName(), sameIds(), selectionDescription(), booleanFilterData, data (+29 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (27): react, catalogueDemoShell(), AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (34): src_api_client_getanalysis, src_api_client_requestanalysis, AnalysisFailure, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis() (+26 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (38): src_api_generated_client_index_client, src_api_generated_client_index_clientmeta, src_api_generated_client_index_options, src_api_generated_client_index_requestresult, src_api_generated_client_index_tdatashape, requestAnalysis(), submitPositionTrainingAnswer(), DeletePreferredMovesData (+30 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (25): react-resizable-panels, clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage() (+17 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (34): src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+26 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (29): ContextMenu(), ContextMenuProps, Menu(), MenuProps, Menubar(), MenubarProps, MenuItemContent(), RenderableMenuItem (+21 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (29): CreateClientConfig, BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys (+21 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (31): AnalysisDashboard(), AnalysisDashboardProps, BreakdownList(), CategoryPerformance, CoverageCard(), DATA_QUALITY_LABELS, DataQuality(), src_features_analysis_overview_analysisdashboard_module (+23 more)

### Community 14 - "Community 14"
Cohesion: 0.10
Nodes (26): AnalysisLine, AnalysisResult, AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv(), formatScore() (+18 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (28): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, src_features_design_system_calendardate_module, Blank, calendarDayName(), CalendarFixtureProps (+20 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (24): vitest, PreferredMoveMutationResult, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, AFTER_NF3_FEN, BOARD_LABEL (+16 more)

### Community 17 - "Community 17"
Cohesion: 0.08
Nodes (28): PositionPickerMoveRecord, PreferredMoveValue, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PREFERRED_MOVE_SOURCE_FEN, PreferredMoveRelationship (+20 more)

### Community 18 - "Community 18"
Cohesion: 0.08
Nodes (28): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+20 more)

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (23): Dialog(), DialogCloseProps, DialogProps, src_features_design_system_overlays_overlayprimitives_module, DialogExample, meta, PreviewCardExample, Story (+15 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (23): PositionContextResponse, src_features_position_reach_frequency_positionreachfrequency_module, PositionReachFrequency(), PositionReachFrequencyProps, BasePositionReachFrequencyModel, boundedPercentage(), colorLabel(), derivePositionReachFrequencyModel() (+15 more)

### Community 21 - "Community 21"
Cohesion: 0.08
Nodes (19): ref_node_fs, ref_node_path, ref_node_url, @storybook/addon-vitest, @vitest/browser-playwright, ContractOperation, dirname, ALLOWED_RUNTIME_CLIENT_IMPORTS (+11 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (25): react-chessboard, findBoardSourceElement(), findBoardSquareElement(), accessiblePieces, ChessboardPieceDropHandlerArgs, ChessboardSurface(), ChessboardSurfaceProps, PIECE_NAMES (+17 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (26): src_api_client_getpositioninsight, src_api_client_positioninsightresponse, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord (+18 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (25): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+17 more)

### Community 25 - "Community 25"
Cohesion: 0.10
Nodes (28): expectPositionReachFrequency(), expectPositionSquares(), expectPreferredMoveState(), expectSessionBoundary(), expectSingleStagedStatus(), expectStagedStatus(), sharedPositionSummary(), verifyStandardWorkspace() (+20 more)

### Community 26 - "Community 26"
Cohesion: 0.09
Nodes (16): @chialab/vitest-axe, @testing-library/react, @testing-library/user-event, ExpectedDisplay, { shouldThrow }, here, LoaderHarnessProps, rawStyles (+8 more)

### Community 27 - "Community 27"
Cohesion: 0.08
Nodes (21): src_api_client_openingcatalogueitemresponse, filterOpeningCatalogue(), src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, OpeningSelection, searchText() (+13 more)

### Community 28 - "Community 28"
Cohesion: 0.11
Nodes (26): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+18 more)

### Community 29 - "Community 29"
Cohesion: 0.12
Nodes (27): src_api_client_getopeningsdata, src_api_client_getpositiontrainingrequirementsdata, src_api_client_openingcatalogueresponse, src_api_client_traininganswerresponse, abortError(), buildTrainingRequirementsQuery(), errorCode(), fetchOpeningChoices() (+19 more)

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (23): createQuerySerializer(), formDataBodySerializer, QuerySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArraySeparatorStyle, ArrayStyle, MatrixStyle (+15 more)

### Community 31 - "Community 31"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 32 - "Community 32"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 33 - "Community 33"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 34 - "Community 34"
Cohesion: 0.15
Nodes (24): GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession() (+16 more)

### Community 35 - "Community 35"
Cohesion: 0.10
Nodes (15): ChartLabel, here, rawStyles, MoveResponseDistributionClient, MoveResponseDistributionFailureCode, MoveResponseDistributionResponse, MoveResponseDistributionResult, InternalState (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.19
Nodes (23): applySessionMove(), atIndex(), branchWithMove(), createFreshSession(), createSession(), importedPositions(), loadImportedSession(), mainLinePositions() (+15 more)

### Community 37 - "Community 37"
Cohesion: 0.14
Nodes (19): @base-ui/react, Accordion(), AccordionItemDefinition, AccordionProps, Avatar(), AvatarProps, AvatarSize, src_features_design_system_contentprimitives_module (+11 more)

### Community 38 - "Community 38"
Cohesion: 0.09
Nodes (17): react-error-boundary, ConstrainedClosed, ConstrainedOpen, Healthy, Loading, meta, Story, Unavailable (+9 more)

### Community 39 - "Community 39"
Cohesion: 0.10
Nodes (19): src_api_client_statisticsoverviewresponse, DashboardOpenings, DashboardPerformance, DashboardPreparation, Filters, FiltersConstrained, FiltersValidation, initialDraft (+11 more)

### Community 40 - "Community 40"
Cohesion: 0.14
Nodes (21): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+13 more)

### Community 41 - "Community 41"
Cohesion: 0.25
Nodes (24): booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys(), isRecord(), JsonRecord, NODE_KEYS, nodeBase() (+16 more)

### Community 42 - "Community 42"
Cohesion: 0.09
Nodes (21): engines, node, name, private, type, version, eslint, @eslint/js (+13 more)

### Community 43 - "Community 43"
Cohesion: 0.12
Nodes (20): src_api_client_trainingrequirementitemresponse, src_api_client_trainingrequirementresponse, currentUtcDate(), OpeningCatalogueSnapshotResult, OpeningChoicesResult, TrainerPracticeFailureCode, TrainingRequirementsResult, TrainerPracticeApi (+12 more)

### Community 44 - "Community 44"
Cohesion: 0.16
Nodes (22): createClient(), TODO: we probably want to return error and improve types, ReqInit, buildUrl(), checkForExistence(), createConfig(), createInterceptors(), defaultHeaders (+14 more)

### Community 45 - "Community 45"
Cohesion: 0.14
Nodes (19): ChessSide, src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, MoveResponseDistributionReply, MoveResponseDistributionControls(), MoveResponseDistributionControlsProps, CommonReplies (+11 more)

### Community 46 - "Community 46"
Cohesion: 0.12
Nodes (21): SYNTHETIC_OPENING_RESPONSE, filterKind(), OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFailure, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType (+13 more)

### Community 47 - "Community 47"
Cohesion: 0.09
Nodes (22): AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, FirstChoice, FirstChoiceFromEmpty, Matching, meta, PendingRemove (+14 more)

### Community 48 - "Community 48"
Cohesion: 0.17
Nodes (14): AnalysisClient, AnalysisFailureCode, AnalysisObservation, defaultAnalysisClient, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey(), AnalysisQueryError, DEFAULT_ANALYSIS_POLL_INTERVAL_MS (+6 more)

### Community 49 - "Community 49"
Cohesion: 0.13
Nodes (18): parseUciMove(), Ply, San, GameMainLineModel, GameMainLineOccurrence, mapGameDetailResponse(), sanFromFenAndUci(), DETAIL (+10 more)

### Community 50 - "Community 50"
Cohesion: 0.17
Nodes (17): failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isChessSide(), isNonnegativeInteger(), isRecord(), JsonRecord (+9 more)

### Community 51 - "Community 51"
Cohesion: 0.12
Nodes (13): chess.js, Fen, UciMove, PositionContextClient, PositionContextResult, context(), Probe(), success() (+5 more)

### Community 52 - "Community 52"
Cohesion: 0.13
Nodes (17): recharts, clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart() (+9 more)

### Community 53 - "Community 53"
Cohesion: 0.10
Nodes (17): GameLoader(), handleSubmit(), GameLoaderFailureKind, GameLoaderProps, GameLoaderStatus, GameLoaderValues, src_features_game_gameloader_module, CorpusUnavailable (+9 more)

### Community 54 - "Community 54"
Cohesion: 0.17
Nodes (18): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+10 more)

### Community 55 - "Community 55"
Cohesion: 0.14
Nodes (19): @fullcalendar/react, actionLabel(), formatDay(), formatRange(), src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction (+11 more)

### Community 56 - "Community 56"
Cohesion: 0.14
Nodes (17): clearPending(), isPromotionCandidate(), PendingPromotion, PickerLiveRegion(), PROMOTION_OPTIONS, PromotionController, PromotionControllerOptions, promotionDescription() (+9 more)

### Community 57 - "Community 57"
Cohesion: 0.15
Nodes (17): defaultTrainerPracticeApi, isValidAsOf(), src_features_trainer_practice_trainerpracticeapi_queryopeningcataloguesnapshot, src_features_trainer_practice_trainerpracticeapi_querytrainingrequirements, TrainerColor, TrainerPracticeFilters, TrainingAnswerInput, TrainingAnswerResult (+9 more)

### Community 58 - "Community 58"
Cohesion: 0.17
Nodes (18): typescript, collectFeatureComponents(), collectStoryFiles(), collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), parseSourceFile() (+10 more)

### Community 59 - "Community 59"
Cohesion: 0.16
Nodes (16): src_api_client_getgame, analysisPanelDisplay(), useMoveResponseSelection(), PositionPickerSessionBoundary, SessionNavigation, SessionPosition, src_features_repertoire_builder_repertoirebuilderworkspace_module, cancelPromotionWithStatus() (+8 more)

### Community 60 - "Community 60"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 61 - "Community 61"
Cohesion: 0.16
Nodes (13): PreferredMoveResult, PreferredMoveOutput(), Probe(), response(), success(), usePreferredMoveState(), storybookViewports, src_styles_material_material_theme_builder_css_export_css_dark (+5 more)

### Community 62 - "Community 62"
Cohesion: 0.15
Nodes (11): ref_axe_core, lucide-react, react-router-dom, AnalysisPage, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell() (+3 more)

### Community 63 - "Community 63"
Cohesion: 0.11
Nodes (17): BoardAdapter(), BoardAdapterProps, src_features_board_adapter_boardadapter_module, src_features_board_adapter_boardadapter_starting_fen, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition, ExpandedPositionDescription (+9 more)

### Community 64 - "Community 64"
Cohesion: 0.12
Nodes (13): ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story, VariantMatrix (+5 more)

### Community 65 - "Community 65"
Cohesion: 0.19
Nodes (17): Button(), contextFailureMessage(), failureMessage(), src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), statusLabel() (+9 more)

### Community 66 - "Community 66"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 67 - "Community 67"
Cohesion: 0.22
Nodes (16): clampMoveHistoryPly(), createMoveHistoryModel(), findMoveHistoryEntry(), MoveHistoryControlledModel, moveHistoryEntries(), MoveHistoryModel, navigateMoveHistory(), HISTORY (+8 more)

### Community 68 - "Community 68"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 69 - "Community 69"
Cohesion: 0.12
Nodes (13): PageNotFoundView(), Default, meta, Story, src_features_design_system_feedback_pagefeedback_module, AllSeverities, meta, Story (+5 more)

### Community 70 - "Community 70"
Cohesion: 0.20
Nodes (16): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerStatus, BoardSquareHighlight, boardSquareStyles() (+8 more)

### Community 71 - "Community 71"
Cohesion: 0.22
Nodes (12): BoardAnswerPresentation, src_features_board_adapter_boardadapter_boardorientation, BranchMove, BranchSnapshot, InteractiveBoardMoveIntent, src_features_board_adapter_interactiveboardadapter_module, InteractiveBoardHarness(), InteractiveBoardHarnessProps (+4 more)

### Community 72 - "Community 72"
Cohesion: 0.19
Nodes (15): deriveLastMove(), lastMoveFromSquares(), lastMoveSquareStyles(), answerPresentation(), failureMessage(), learnerLabel(), src_features_trainer_practice_trainersession_module, MoveDetails (+7 more)

### Community 73 - "Community 73"
Cohesion: 0.19
Nodes (15): @tanstack/react-query, invalidatePositionInsight(), invalidatePreferredMove(), invalidateTrainingRequirements(), strictFen(), defaultPreferredMoveClient, moveFromUci(), PendingRefresh (+7 more)

### Community 74 - "Community 74"
Cohesion: 0.16
Nodes (11): invalidateAnalysisObservation(), AnalysisObservationKeyInput, GameDetailKeyInput, OpeningsCatalogueKeyInput, OptionalText, PositionInsightKeyInput, PreferredMoveKeyInput, queryKeyPrefixes (+3 more)

### Community 75 - "Community 75"
Cohesion: 0.15
Nodes (13): CatalogueLink, DemoRow(), DemoRowProps, FamilyPage(), FamilyPageProps, storyHref(), FormControlsCatalogueDocs(), Docs (+5 more)

### Community 76 - "Community 76"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 77 - "Community 77"
Cohesion: 0.17
Nodes (14): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), src_features_design_system_tabs_module, ScrollState, scrollStateFor() (+6 more)

### Community 78 - "Community 78"
Cohesion: 0.21
Nodes (13): AnalysisOverviewFailure, AnalysisOverviewFilters, AnalysisOverviewQueryError, buildStatisticsOverviewQuery(), failureFrom(), fetchAnalysisOverview(), isAbortError(), isRecord() (+5 more)

### Community 79 - "Community 79"
Cohesion: 0.29
Nodes (10): AutocompleteProps, ComboboxProps, DropdownOptionContent(), DropdownOptionContentProps, src_features_design_system_form_controls_formcontrols_module, DropdownItemBody(), DropdownMessage(), DropdownOptionDefinition (+2 more)

### Community 80 - "Community 80"
Cohesion: 0.14
Nodes (13): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+5 more)

### Community 81 - "Community 81"
Cohesion: 0.19
Nodes (13): GAME, GAME_UUID, Game, PROMOTION_GAME, moveResponseData(), storyMoveResponseDistributionClient(), storyPositionContextClient(), StoryPreferredMoveOptions (+5 more)

### Community 82 - "Community 82"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 83 - "Community 83"
Cohesion: 0.12
Nodes (11): Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth, ForcedColorsAndReducedMotion, meta, PositiveBlack (+3 more)

### Community 84 - "Community 84"
Cohesion: 0.20
Nodes (14): storybook, AnalysisQuality, AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent() (+6 more)

### Community 85 - "Community 85"
Cohesion: 0.19
Nodes (12): src_api_client_gamedetailresponse, GameDetailQueryError, queryGameDetail(), useGameDetailQuery(), SessionMove, PreferredMoveClient, failureCode(), GameDetailClient (+4 more)

### Community 86 - "Community 86"
Cohesion: 0.31
Nodes (15): normalizePositionKey(), changedObservation(), failureMessage(), mergeObservation(), observationFingerprint(), useDefaultAnalysisState(), requestAnalysis(), useInjectedAnalysisState() (+7 more)

### Community 87 - "Community 87"
Cohesion: 0.16
Nodes (11): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelIntent, AnalysisPanelResult, AnalysisPanelResultMetadata, InlineWdl(), src_features_analysis_analysispanel_module, resultMetadataLabel() (+3 more)

### Community 88 - "Community 88"
Cohesion: 0.19
Nodes (10): EvalBar(), EvalBarProps, BoardEvalStage(), boardVisualIn(), BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock (+2 more)

### Community 89 - "Community 89"
Cohesion: 0.18
Nodes (10): src_features_design_system_outcometrack_module, OutcomeTrack(), OutcomeTrackProps, OutcomeTrackValues, share(), Compact, meta, Story (+2 more)

### Community 90 - "Community 90"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 91 - "Community 91"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 92 - "Community 92"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 93 - "Community 93"
Cohesion: 0.21
Nodes (10): AnalysisPanelLine, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay(), missingDisplay() (+2 more)

### Community 94 - "Community 94"
Cohesion: 0.21
Nodes (9): BoardControl(), BoardControlProps, BoardEvalStageProps, InteractiveBoardAdapterProps, MoveHistoryControlledState, BoardContentProps, HistoryProps, RepertoireBoardLane() (+1 more)

### Community 95 - "Community 95"
Cohesion: 0.15
Nodes (11): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+3 more)

### Community 96 - "Community 96"
Cohesion: 0.18
Nodes (11): PreferredMovePanelProps, here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4 (+3 more)

### Community 97 - "Community 97"
Cohesion: 0.17
Nodes (7): src_api_client_getopenings, src_api_client_getpositiontrainingrequirements, src_api_client_submitpositiontraininganswer, src_features_trainer_practice_trainerpracticeapi_queryopeningchoices, OPENING, selectedFilters, src_features_trainer_practice_trainerpracticeapi_trainerpracticequeryerror

### Community 98 - "Community 98"
Cohesion: 0.18
Nodes (10): activeCountLabel(), AnalysisFilterDraft, AnalysisFilters(), AnalysisFiltersInvalid, AnalysisFiltersProps, COLOR_OPTIONS, src_features_analysis_overview_analysisfilters_module, TIME_CLASS_OPTIONS (+2 more)

### Community 99 - "Community 99"
Cohesion: 0.33
Nodes (11): src_features_analysis_overview_analysisoverview_module, activeFilterCount(), filterScopeLabel(), formatReportDate(), AnalysisPage(), applyFilters(), resetFilters(), errorMessage() (+3 more)

### Community 100 - "Community 100"
Cohesion: 0.20
Nodes (8): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent

### Community 101 - "Community 101"
Cohesion: 0.21
Nodes (8): clamp(), src_features_design_system_progressmeter_module, ProgressMeter(), ProgressMeterProps, Determinate, meta, Story, Unavailable

### Community 102 - "Community 102"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 103 - "Community 103"
Cohesion: 0.17
Nodes (11): LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate, expectActiveSessionHistoryEntry() (+3 more)

### Community 104 - "Community 104"
Cohesion: 0.18
Nodes (8): @storybook/react-vite, Docs, meta, Story, Docs, meta, Story, config

### Community 105 - "Community 105"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 106 - "Community 106"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 107 - "Community 107"
Cohesion: 0.20
Nodes (7): meta, ResponsiveAccessibilityReview, Story, StorySpecimenAccessibilityReview(), here, moduleCss, tokenCss

### Community 108 - "Community 108"
Cohesion: 0.29
Nodes (8): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story

### Community 109 - "Community 109"
Cohesion: 0.25
Nodes (5): AnalysisOperationResult, StateProbe(), Probe(), RESULT, useAnalysisState()

### Community 110 - "Community 110"
Cohesion: 0.25
Nodes (6): BoardRender(), PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, stripPackageSemantics(), src_features_board_adapter_positiondescription_boardorientation, PositionModel

### Community 111 - "Community 111"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 112 - "Community 112"
Cohesion: 0.28
Nodes (8): createMoveHistoryRows(), KEY_NAVIGATION, src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow

### Community 113 - "Community 113"
Cohesion: 0.29
Nodes (6): src_api_client_gethealthoptions, StatusPage(), Default, meta, queryClient, Story

### Community 114 - "Community 114"
Cohesion: 0.25
Nodes (5): Constrained, HISTORY, Interactive, meta, Story

### Community 115 - "Community 115"
Cohesion: 0.32
Nodes (6): PreferredMoveFailureCode, PreferredMoveReader, PreferredMoveResponse, PreferredMoveQueryError, PreferredMoveReadState, queryPreferredMove()

### Community 116 - "Community 116"
Cohesion: 0.25
Nodes (7): board, controls, evaluation, history, meta, Standard, Story

### Community 118 - "Community 118"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 119 - "Community 119"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 120 - "Community 120"
Cohesion: 0.29
Nodes (5): src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, CatalogueSection

### Community 121 - "Community 121"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 122 - "Community 122"
Cohesion: 0.29
Nodes (4): here, HISTORY, moduleCss, MoveHistoryActivePlyChange

### Community 125 - "Community 125"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 127 - "Community 127"
Cohesion: 0.50
Nodes (3): @testing-library/jest-dom, elementProto, topLayerPseudoSelectors

### Community 128 - "Community 128"
Cohesion: 0.50
Nodes (3): Docs, meta, Story

### Community 129 - "Community 129"
Cohesion: 0.50
Nodes (3): Docs, meta, Story

### Community 130 - "Community 130"
Cohesion: 0.50
Nodes (3): FEEDBACK_TOKENS, here, tokenCss

## Knowledge Gaps
- **968 isolated node(s):** `QueryKey`, `Story`, `DisclosureProps`, `Story`, `ProgressMeterProps` (+963 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1338 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **127 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 6` to `Community 2`, `Community 4`, `Community 5`, `Community 9`, `Community 10`, `Community 11`, `Community 13`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 23`, `Community 24`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 35`, `Community 37`, `Community 38`, `Community 39`, `Community 42`, `Community 45`, `Community 48`, `Community 51`, `Community 52`, `Community 53`, `Community 55`, `Community 56`, `Community 57`, `Community 59`, `Community 61`, `Community 62`, `Community 64`, `Community 65`, `Community 70`, `Community 71`, `Community 72`, `Community 73`, `Community 75`, `Community 77`, `Community 79`, `Community 81`, `Community 82`, `Community 83`, `Community 88`, `Community 89`, `Community 90`, `Community 93`, `Community 98`, `Community 99`, `Community 100`, `Community 101`, `Community 109`, `Community 110`, `Community 111`, `Community 112`, `Community 114`, `Community 115`, `Community 122`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `vitest` connect `Community 16` to `Community 130`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 9`, `Community 11`, `Community 14`, `Community 15`, `Community 19`, `Community 20`, `Community 21`, `Community 26`, `Community 28`, `Community 34`, `Community 35`, `Community 36`, `Community 37`, `Community 39`, `Community 40`, `Community 42`, `Community 43`, `Community 46`, `Community 48`, `Community 49`, `Community 50`, `Community 51`, `Community 54`, `Community 56`, `Community 58`, `Community 61`, `Community 62`, `Community 64`, `Community 66`, `Community 67`, `Community 69`, `Community 70`, `Community 71`, `Community 72`, `Community 73`, `Community 74`, `Community 78`, `Community 80`, `Community 88`, `Community 89`, `Community 93`, `Community 94`, `Community 96`, `Community 97`, `Community 100`, `Community 101`, `Community 102`, `Community 105`, `Community 107`, `Community 109`, `Community 119`, `Community 121`, `Community 122`, `Community 123`, `Community 124`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `@storybook/react-vite` connect `Community 104` to `Community 128`, `Community 129`, `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 9`, `Community 10`, `Community 11`, `Community 15`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 24`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 31`, `Community 33`, `Community 37`, `Community 38`, `Community 39`, `Community 40`, `Community 42`, `Community 45`, `Community 47`, `Community 52`, `Community 53`, `Community 55`, `Community 60`, `Community 61`, `Community 63`, `Community 64`, `Community 66`, `Community 69`, `Community 75`, `Community 80`, `Community 82`, `Community 83`, `Community 89`, `Community 90`, `Community 95`, `Community 100`, `Community 101`, `Community 102`, `Community 103`, `Community 105`, `Community 107`, `Community 108`, `Community 111`, `Community 113`, `Community 114`, `Community 116`, `Community 120`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **What connects `QueryKey`, `Story`, `DisclosureProps` to the rest of the system?**
  _968 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06101231190150479 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.046130952380952384 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.07397959183673469 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
