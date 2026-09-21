# Graph Report - frontend  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2813 nodes · 6160 edges · 249 communities (125 shown, 124 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.85)
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

## God Nodes (most connected - your core abstractions)
1. `react` - 112 edges
2. `vitest` - 86 edges
3. `@storybook/react-vite` - 64 edges
4. `@testing-library/react` - 56 edges
5. `storybook` - 37 edges
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
- `normalizePositionKey()` --calls--> `positionKeyFromFen()`  [EXTRACTED]
  src/api/queryKeys.ts → src/features/chess/chessPrimitives.ts
- `PreferredMoveDateValue()` --calls--> `formatUtcDate()`  [EXTRACTED]
  src/features/repertoire-builder/PreferredMovePrimitives.tsx → src/features/design-system/CalendarDateUtils.ts
- `Probe()` --indirect_call--> `QueryClientTestProvider()`  [INFERRED]
  src/features/repertoire-builder/preferredMoveState.test.ts → src/test-utils/QueryClientTestProvider.tsx

## Import Cycles
- None detected.

## Communities (249 total, 124 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (87): ActivityPeriodResponse, ActivityStatisticsResponse, AnalysisObservationErrorResponse, AnalysisObservationLineResponse, AnalysisObservationResponse, AnalysisObservationResultResponse, AnalysisRequestBody, AnalysisRequestErrorResponse (+79 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (70): getAnalysis(), getGame(), getGames(), getHealth(), getOpeningByKey(), getOpenings(), getPositionInsight(), getPositionTrainingRequirements() (+62 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (56): src_api_client_deletepreferredmoves, src_api_client_getpreferredmoves, src_api_client_preferredmovesmutationresponse, src_api_client_preferredmovesremovalresponse, src_api_client_preferredmovesresponse, src_api_client_preferredmovessegmentresponse, src_api_client_putpreferredmoves, deletePreferredMove() (+48 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (37): react, catalogueDemoShell(), AutocompleteStates, ComboboxStates, Docs, FieldStates, meta, NarrowViewport (+29 more)

### Community 4 - "Community 4"
Cohesion: 0.11
Nodes (40): src_api_client_getgame, analysisPanelDisplay(), GameMainLineModel, useMoveResponseSelection(), applySessionMove(), atIndex(), branchWithMove(), createFreshSession() (+32 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (34): src_features_design_system_form_controls_advancedformcontrols_module, CheckboxGroupExample, FieldsetExample, FormExample, meta, NumberFieldExample, OtpFieldExample, SliderExample (+26 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (37): @headless-tree/core, @headless-tree/react, LineLibrary(), nodeName(), sameIds(), selectionDescription(), booleanFilterData, data (+29 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (32): @storybook/react-vite, src_features_design_system_catalogue_catalogue_module, Docs, meta, Story, Docs, meta, Story (+24 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (42): src_api_generated_client_index_client, src_api_generated_client_index_clientmeta, src_api_generated_client_index_options, src_api_generated_client_index_requestresult, src_api_generated_client_index_tdatashape, deletePreferredMoves(), putPreferredMoves(), requestAnalysis() (+34 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (30): ANSWER_SQUARE_FILL, ANSWER_SQUARE_RING, answerInteractionAllowed(), answerMessage(), answerSquareStyles(), BoardAnswerPresentation, BoardAnswerStatus, BoardSquareHighlight (+22 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (30): @base-ui/react, ContextMenu(), ContextMenuProps, Menu(), MenuProps, Menubar(), MenubarProps, MenuItemContent() (+22 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (32): src_api_client_getanalysis, src_api_client_requestanalysis, AnalysisFailure, AnalysisRequest, AnalysisScoreKind, AnalysisTerminalKind, failureFromResponse(), fetchAnalysis() (+24 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (30): accessiblePieces, ChessboardPieceDropHandlerArgs, ChessboardSurface(), ChessboardSurfaceProps, findBoardSourceElement(), findBoardSquareElement(), PIECE_NAMES, clearPending() (+22 more)

### Community 13 - "Community 13"
Cohesion: 0.08
Nodes (34): src_features_design_system_line_library_linelibrary_linelibraryprops, AcceptedCorpusScenario, BrowserSelectionAndCommit, DeclaredSyntheticSelectionLimit, DisabledAndTranspositionReference, EcoRangeScenario, EmptyResult, FailureAndRetry (+26 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (32): AnalysisDashboardProps, BreakdownList(), CategoryPerformance, CoverageCard(), DATA_QUALITY_LABELS, DataQuality(), src_features_analysis_overview_analysisdashboard_module, MonthlyActivity() (+24 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (27): @tanstack/react-query, invalidateAnalysisObservation(), invalidatePositionInsight(), invalidatePreferredMove(), invalidateTrainingRequirements(), AnalysisObservationKeyInput, GameDetailKeyInput, normalizePositionKey() (+19 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (28): calendarClassNames, CalendarDate(), CalendarDateProps, CalendarDateValue, src_features_design_system_calendardate_module, Blank, calendarDayName(), CalendarFixtureProps (+20 more)

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (25): failureFromInsight(), fetchMoveResponseDistribution(), isCanonicalFen(), isCanonicalUci(), isNonnegativeInteger(), isRecord(), JsonRecord, legalMoveFromUci() (+17 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (24): AnalysisClient, AnalysisObservation, AnalysisOperationResult, AFTER_D4_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_E8_KNIGHT_FEN, AFTER_NF3_FEN (+16 more)

### Community 19 - "Community 19"
Cohesion: 0.10
Nodes (22): AnalysisLine, AnalysisPanelDisplayOptions, displayPv(), formatAccessiblePercentage(), formatPercentage(), formatPv(), formatScore(), formatWdl() (+14 more)

### Community 20 - "Community 20"
Cohesion: 0.11
Nodes (23): Dialog(), DialogCloseProps, DialogProps, src_features_design_system_overlays_overlayprimitives_module, DialogExample, meta, PreviewCardExample, Story (+15 more)

### Community 21 - "Community 21"
Cohesion: 0.11
Nodes (29): src_api_client_getopeningsdata, src_api_client_getpositiontrainingrequirementsdata, src_api_client_openingcatalogueresponse, src_api_client_traininganswerresponse, abortError(), buildTrainingRequirementsQuery(), defaultTrainerPracticeApi, errorCode() (+21 more)

### Community 22 - "Community 22"
Cohesion: 0.14
Nodes (21): AnalysisFailureCode, defaultAnalysisClient, src_features_analysis_analysisapi_positionkeyfromfen, ANALYSIS_OBSERVATION_GC_TIME, analysisObservationQueryKey(), AnalysisQueryError, DEFAULT_ANALYSIS_POLL_INTERVAL_MS, MAX_ANALYSIS_POLL_ATTEMPTS (+13 more)

### Community 23 - "Community 23"
Cohesion: 0.08
Nodes (26): Accessibility, ActiveWithResult, CandidateActivation, completeDisplay(), ConstrainedReady, DEFAULT_ACTIONS, DISPLAY_LINES, displayFor() (+18 more)

### Community 24 - "Community 24"
Cohesion: 0.13
Nodes (21): FeedbackCore(), here, moduleCss, SEVERITIES, TOKEN_SET, FEEDBACK_VARIANTS, FeedbackLiveRegionAttributes, FeedbackProps (+13 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (25): filterValueAsString(), LineLibraryFilterBarProps, LineLibraryFilters(), definitions, Disabled, ExplicitApply, FilterFixtureProps, ImmediateApply (+17 more)

### Community 26 - "Community 26"
Cohesion: 0.10
Nodes (28): expectPositionReachFrequency(), expectPositionSquares(), expectPreferredMoveState(), expectSessionBoundary(), expectSingleStagedStatus(), expectStagedStatus(), sharedPositionSummary(), verifyStandardWorkspace() (+20 more)

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (26): actionCss, here, primitiveCss, choiceBoxEmptyTitle(), consequenceText(), ICON_CLASS, joinClasses(), PreferredMoveActionLayout() (+18 more)

### Community 28 - "Community 28"
Cohesion: 0.08
Nodes (24): engines, node, name, private, type, version, eslint, @eslint/js (+16 more)

### Community 29 - "Community 29"
Cohesion: 0.09
Nodes (21): react-resizable-panels, clamp(), defaultLayout(), layoutFromPixels(), Mode, modeForWidth(), src_features_repertoire_builder_repertoireresponsivestage_module, panelSpaceForStage() (+13 more)

### Community 30 - "Community 30"
Cohesion: 0.09
Nodes (22): src_api_client_gamedetailresponse, PromotionPiece, GameLoader(), handleSubmit(), GameLoaderFailureKind, GameLoaderProps, GameLoaderStatus, GameLoaderValues (+14 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (20): src_api_client_openingcatalogueitemresponse, src_api_client_trainingrequirementresponse, filterOpeningCatalogue(), src_features_trainer_practice_openingsearchcombobox_module, openingLabel(), OpeningSearchCombobox(), OpeningSearchComboboxProps, OpeningSelection (+12 more)

### Community 32 - "Community 32"
Cohesion: 0.13
Nodes (20): chess.js, ChessSide, Ply, San, strictFen(), UciMove, GameMainLineOccurrence, mapGameDetailResponse() (+12 more)

### Community 33 - "Community 33"
Cohesion: 0.15
Nodes (23): src_api_client_getpositioninsight, Fen, failureFromInsight(), fetchPositionContext(), isCanonicalFen(), isNonnegativeInteger(), isRecord(), JsonRecord (+15 more)

### Community 34 - "Community 34"
Cohesion: 0.09
Nodes (24): EmptyEmpty, expectDateFreePanel(), expectFooterActions(), expectNoPanelOverflow(), expectPromotionOverflowCase(), FirstChoice, Loading, Matching (+16 more)

### Community 35 - "Community 35"
Cohesion: 0.08
Nodes (26): devDependencies, @chialab/vitest-axe, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, @hey-api/openapi-ts, jsdom (+18 more)

### Community 36 - "Community 36"
Cohesion: 0.15
Nodes (23): buildUrl(), createQuerySerializer(), defaultHeaders, defaultQuerySerializer, ErrInterceptor, ReqInterceptor, ResInterceptor, ArraySeparatorStyle (+15 more)

### Community 37 - "Community 37"
Cohesion: 0.08
Nodes (21): ActionDisabled, AnswerAwaitingInput, AnswerCorrect, AnswerDisabled, AnswerIllegal, AnswerIncorrect, AnswerRevealed, answerStoryArgs (+13 more)

### Community 38 - "Community 38"
Cohesion: 0.15
Nodes (24): GamePosition, appendMove(), applyPositionPickerMove(), commitStagedMove(), createStandardStartSession(), createStoredGameSession(), flipPositionPickerSession(), navigatePositionPickerSession() (+16 more)

### Community 39 - "Community 39"
Cohesion: 0.09
Nodes (18): ConstrainedClosed, ConstrainedOpen, Healthy, Loading, meta, Story, Unavailable, UnexpectedFailureBrowserProof (+10 more)

### Community 40 - "Community 40"
Cohesion: 0.13
Nodes (22): PositionDescription(), meta, RichBlackOrientation, Story, VisiblePositionSummary(), castlingDescription(), castlingNotation(), CastlingRights (+14 more)

### Community 41 - "Community 41"
Cohesion: 0.25
Nodes (24): booleanValue(), contractFailure(), FILTER_TYPES, hasExactKeys(), isRecord(), JsonRecord, NODE_KEYS, nodeBase() (+16 more)

### Community 42 - "Community 42"
Cohesion: 0.11
Nodes (19): lucide-react, Accordion(), AccordionItemDefinition, AccordionProps, Avatar(), AvatarProps, AvatarSize, src_features_design_system_contentprimitives_module (+11 more)

### Community 43 - "Community 43"
Cohesion: 0.14
Nodes (17): src_features_move_response_distribution_moveresponsedistribution_module, MoveResponseDistribution(), MoveResponseDistributionPanel, MoveResponseDistributionReply, MoveResponseDistributionResponse, MoveResponseDistributionControls(), MoveResponseDistributionControlsProps, CommonReplies (+9 more)

### Community 44 - "Community 44"
Cohesion: 0.12
Nodes (21): SYNTHETIC_OPENING_RESPONSE, filterKind(), OpeningLineLibraryErrorCode, OpeningLineLibraryErrorResponse, OpeningLineLibraryFailure, OpeningLineLibraryFilterDeclaration, OpeningLineLibraryFilterOption, OpeningLineLibraryFilterType (+13 more)

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (22): AbsentUnsavable, AccessibilityAndResponsive, AssignedUnsavable, FirstChoice, FirstChoiceFromEmpty, Matching, meta, PendingRemove (+14 more)

### Community 46 - "Community 46"
Cohesion: 0.14
Nodes (18): StatisticsOverviewResponse, AnalysisOverviewClient, AnalysisOverviewFailure, AnalysisOverviewFilters, AnalysisOverviewQueryError, buildStatisticsOverviewQuery(), failureFrom(), fetchAnalysisOverview() (+10 more)

### Community 47 - "Community 47"
Cohesion: 0.16
Nodes (19): discardInvalidSnapshot(), hasExactFields(), isFiniteInteger(), isNonemptyString(), isOpeningCatalogueItem(), isOpeningCatalogueSnapshot(), isRecord(), ITEM_FIELDS (+11 more)

### Community 48 - "Community 48"
Cohesion: 0.14
Nodes (11): @chialab/vitest-axe, @testing-library/react, @testing-library/user-event, vitest, ExpectedDisplay, FEEDBACK_TOKENS, here, tokenCss (+3 more)

### Community 49 - "Community 49"
Cohesion: 0.14
Nodes (15): src_api_client_positioninsightresponse, isChessSide(), validateMoveResponseDistributionColor(), requestPositionInsight(), validatePositionContextFen(), currentUtcDate(), isValidRawInsight(), POSITION_INSIGHT_GC_TIME (+7 more)

### Community 50 - "Community 50"
Cohesion: 0.16
Nodes (19): BuildUrlFn, Client, ClientOptions, Config, CreateClientConfig, MethodFn, OmitKeys, Options (+11 more)

### Community 51 - "Community 51"
Cohesion: 0.14
Nodes (19): @fullcalendar/react, actionLabel(), formatDay(), formatRange(), src_features_repertoire_builder_preferredmovescheduleprototype_module, oneYearAfter(), parseIsoDay(), PreferredMoveScheduleAction (+11 more)

### Community 52 - "Community 52"
Cohesion: 0.13
Nodes (13): src_api_client_gethealthoptions, StatusPage(), Default, meta, queryClient, Story, storybookViewports, src_styles_material_material_theme_builder_css_export_css_dark (+5 more)

### Community 53 - "Community 53"
Cohesion: 0.10
Nodes (16): src_features_design_system_feedback_pagefeedback_module, AllSeverities, meta, Story, src_features_design_system_feedback_panelfeedback_module, AllSeverities, meta, Story (+8 more)

### Community 54 - "Community 54"
Cohesion: 0.14
Nodes (16): recharts, clampLabelStack(), computePieLabelLayouts(), isMoveChartItem(), LabelSideEntry, labelText(), MoveChartItem, MoveResponseDistributionChart() (+8 more)

### Community 55 - "Community 55"
Cohesion: 0.10
Nodes (18): BestLine, ClampedMaximum, ClampedMinimum, CompletedMateGiven, CompletedNegativeCp, CompletedNegativeMate, CompletedPositiveMate, ExpectedDisplay (+10 more)

### Community 56 - "Community 56"
Cohesion: 0.13
Nodes (14): Button(), ButtonProps, ButtonSize, ButtonVariant, SIZE_CLASS, meta, SIZES, Story (+6 more)

### Community 57 - "Community 57"
Cohesion: 0.14
Nodes (13): src_api_client_getopenings, src_api_client_getpositiontrainingrequirements, src_api_client_submitpositiontraininganswer, currentUtcDate(), isValidAsOf(), queryOpeningCatalogueSnapshot(), queryOpeningChoices(), queryTrainingRequirements() (+5 more)

### Community 58 - "Community 58"
Cohesion: 0.12
Nodes (14): ELEVATIONS, RADII, SPACING_CLASSES, SPACING_STEPS, Foundations, meta, Story, StorySpecimenFoundation() (+6 more)

### Community 59 - "Community 59"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+10 more)

### Community 60 - "Community 60"
Cohesion: 0.16
Nodes (10): ref_axe_core, react-router-dom, AnalysisPage, App(), RepertoireBuilderWorkspace, TrainerPracticePage, AppShell(), AppShellProps (+2 more)

### Community 61 - "Community 61"
Cohesion: 0.11
Nodes (7): BASE_TABS, DISABLED_TABS, here, moduleCss, OVERFLOW_TABS, TestMutationObserver, TestResizeObserver

### Community 62 - "Community 62"
Cohesion: 0.22
Nodes (15): clampMoveHistoryPly(), createMoveHistoryModel(), findMoveHistoryEntry(), MoveHistoryControlledModel, moveHistoryEntries(), MoveHistoryModel, navigateMoveHistory(), HISTORY (+7 more)

### Community 63 - "Community 63"
Cohesion: 0.20
Nodes (16): PositionContextFailureCode, contextFailureMessage(), failureMessage(), src_features_repertoire_builder_preferredmovepanel_module, mutationLabel(), PreferredMoveMutationKind, PreferredMovePanel(), statusLabel() (+8 more)

### Community 64 - "Community 64"
Cohesion: 0.20
Nodes (14): typescript, collectStoryFiles(), collectViewportReferences(), visit(), defaultMeta(), exportedStoryObjects(), propertyName(), propertyValue() (+6 more)

### Community 65 - "Community 65"
Cohesion: 0.19
Nodes (11): PositionContextResponse, src_features_position_reach_frequency_positionreachfrequency_module, PositionReachFrequency(), PositionReachFrequencyProps, BasePositionReachFrequencyModel, boundedPercentage(), colorLabel(), derivePositionReachFrequencyModel() (+3 more)

### Community 66 - "Community 66"
Cohesion: 0.12
Nodes (16): dependencies, @base-ui/react, chess.js, @fullcalendar/react, @headless-tree/core, @headless-tree/react, lucide-react, react (+8 more)

### Community 67 - "Community 67"
Cohesion: 0.17
Nodes (14): AnalysisPanelProps, domIdFor(), enabledTabsFrom(), INITIAL_SCROLL_STATE, initialSelection(), src_features_design_system_tabs_module, ScrollState, scrollStateFor() (+6 more)

### Community 68 - "Community 68"
Cohesion: 0.14
Nodes (13): CompleteTypescale, meta, Story, StorySpecimenTypescale(), here, moduleCss, SCALE_NAMES, SIZE_NAMES (+5 more)

### Community 69 - "Community 69"
Cohesion: 0.13
Nodes (13): AvailableWithoutTail, AvailableWithTail, ConstrainedWidth, DenseTinySectorCluster, KeyboardAndDisclosure, Loading, MatchingGamesWithoutNextMoves, meta (+5 more)

### Community 70 - "Community 70"
Cohesion: 0.12
Nodes (11): Absent, Accessibility, AvailableZero, BLACK_CONTEXT, ConstrainedWidth, ForcedColorsAndReducedMotion, meta, PositiveBlack (+3 more)

### Community 71 - "Community 71"
Cohesion: 0.15
Nodes (14): PreferredMovePanelProps, RepertoireSessionPanel(), RepertoireSessionPanelProps, FrequencyAbsent, FrequencyUnavailable, FrequencyZero, LocalLineSession, meta (+6 more)

### Community 72 - "Community 72"
Cohesion: 0.22
Nodes (14): createClient(), TODO: we probably want to return error and improve types, ReqInit, checkForExistence(), createConfig(), createInterceptors(), getParseAs(), headersEntries() (+6 more)

### Community 73 - "Community 73"
Cohesion: 0.22
Nodes (11): AnalysisResult, StateProbe(), Probe(), RESULT, useAnalysisState(), useInjectedAnalysisState(), fail(), observe() (+3 more)

### Community 74 - "Community 74"
Cohesion: 0.16
Nodes (11): AnalysisPanel(), AnalysisPanelCandidateIntent, AnalysisPanelIntent, AnalysisPanelResult, AnalysisPanelResultMetadata, InlineWdl(), src_features_analysis_analysispanel_module, resultMetadataLabel() (+3 more)

### Community 75 - "Community 75"
Cohesion: 0.20
Nodes (12): GAME, GAME_UUID, Game, PROMOTION_GAME, storyPositionContextClient(), StoryPositionContextOptions, StoryPreferredMoveOptions, assignedWorkspace() (+4 more)

### Community 76 - "Community 76"
Cohesion: 0.18
Nodes (14): PreferredMoveMutationResult, DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR, DEFAULT_MOVE, moveFromRequest(), moveResponseData(), removalMutationResponse(), saveMutationResponse(), STORY_BLACK_SUBJECT_GAME_DETAIL (+6 more)

### Community 77 - "Community 77"
Cohesion: 0.15
Nodes (11): ref_node_fs, ref_node_path, ref_node_url, @storybook/addon-vitest, @vitest/browser-playwright, ALLOWED_RUNTIME_CLIENT_IMPORTS, collectProductionSourceFiles(), dirname (+3 more)

### Community 78 - "Community 78"
Cohesion: 0.16
Nodes (7): react-error-boundary, PageContentBoundary(), PageContentBoundaryProps, HealthyContent, meta, Story, UnexpectedFailureTryAgain

### Community 79 - "Community 79"
Cohesion: 0.19
Nodes (12): src_api_client_trainingrequirementitemresponse, OpeningCatalogueSnapshotResult, TrainingRequirementsResult, TrainerPracticeApi, createApi(), item(), OPENING, page() (+4 more)

### Community 80 - "Community 80"
Cohesion: 0.19
Nodes (11): AnalysisPanelDisplay, AnalysisPanelLine, completeDisplay(), DEFAULT_ACTIONS, DISPLAY_LINES, displayFor(), DisplayOverrides, errorDisplay() (+3 more)

### Community 81 - "Community 81"
Cohesion: 0.21
Nodes (13): parseUciMove(), answerPresentation(), failureMessage(), learnerLabel(), src_features_trainer_practice_trainersession_module, MoveDetails, moveFromSnapshot(), SessionFeedback() (+5 more)

### Community 82 - "Community 82"
Cohesion: 0.18
Nodes (10): src_features_design_system_outcometrack_module, OutcomeTrack(), OutcomeTrackProps, OutcomeTrackValues, share(), Compact, meta, Story (+2 more)

### Community 83 - "Community 83"
Cohesion: 0.14
Nodes (9): Controlled, Default, Disabled, DISABLED_TABS, FITTING_TABS, meta, Overflow, OVERFLOW_TABS (+1 more)

### Community 84 - "Community 84"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 85 - "Community 85"
Cohesion: 0.15
Nodes (11): storybook, Available, meta, Story, PREFERRED_MOVE_SOURCE_FEN, expectDateFreePreferredPanel(), expectPreferredActions(), StoryPreferredMoveRequest (+3 more)

### Community 86 - "Community 86"
Cohesion: 0.24
Nodes (11): Auth, AuthToken, BodySerializer, QuerySerializer, QuerySerializerOptions, Client, ClientMeta, Config (+3 more)

### Community 87 - "Community 87"
Cohesion: 0.18
Nodes (11): buildClientParams(), buildKeyMap(), extraPrefixes, extraPrefixesMap, Field, Fields, FieldsConfig, KeyMap (+3 more)

### Community 88 - "Community 88"
Cohesion: 0.24
Nodes (12): AnalysisStateValue, AnalysisSuccess, cleanLine(), cleanObservation(), cleanResult(), emitLifecycleEvent(), storyAnalysisClient(), StoryAnalysisLifecycleEvent (+4 more)

### Community 89 - "Community 89"
Cohesion: 0.18
Nodes (8): BoardAdapter(), BoardAdapterProps, BoardRender(), PACKAGE_SEMANTIC_ATTRIBUTES, PACKAGE_SEMANTIC_SELECTOR, stripPackageSemantics(), { shouldThrow }, src_features_board_adapter_positiondescription_boardorientation

### Community 90 - "Community 90"
Cohesion: 0.15
Nodes (11): Constrained, Empty, FinalBoundary, InitialBoundary, Intermediate, KeyboardToolbar, Loading, meta (+3 more)

### Community 91 - "Community 91"
Cohesion: 0.15
Nodes (10): PositionPickerMoveRecord, D4_MOVE, D4_STAGED_MOVE, E4_MOVE, E4_STAGED_MOVE, PreferredMoveRelationship, preferredMoveRelationshipFixtures, PreferredMoveStoryFixture (+2 more)

### Community 92 - "Community 92"
Cohesion: 0.24
Nodes (9): EvalBar(), EvalBarProps, src_features_board_adapter_boardadapter_starting_fen, BoardEvalStage(), boardVisualIn(), meta, StartingPosition, Story (+1 more)

### Community 93 - "Community 93"
Cohesion: 0.18
Nodes (10): activeCountLabel(), AnalysisFilterDraft, AnalysisFilters(), AnalysisFiltersInvalid, AnalysisFiltersProps, COLOR_OPTIONS, src_features_analysis_overview_analysisfilters_module, TIME_CLASS_OPTIONS (+2 more)

### Community 94 - "Community 94"
Cohesion: 0.17
Nodes (11): src_features_board_adapter_boardadapter_module, BlackOrientation, ConstrainedWidth, DefaultValidStartingPosition, ExpandedPositionDescription, HiddenCoordinates, InvalidFen, meta (+3 more)

### Community 95 - "Community 95"
Cohesion: 0.17
Nodes (11): Cancellation, ConstrainedDrawer, defaultArgs, ForcedColorsAndReducedMotion, KeyboardSelection, meta, NativeKeyboardPromotionInitiation, StaleAndIllegalRejection (+3 more)

### Community 96 - "Community 96"
Cohesion: 0.21
Nodes (8): clamp(), src_features_design_system_progressmeter_module, ProgressMeter(), ProgressMeterProps, Determinate, meta, Story, Unavailable

### Community 97 - "Community 97"
Cohesion: 0.20
Nodes (8): meta, Story, TournamentAnalysisDesk, StorySpecimenCombinedComposition(), here, moduleCss, tokenCss, typescaleCss

### Community 98 - "Community 98"
Cohesion: 0.20
Nodes (10): here, model(), panelArgs(), panelCss, SAVED_FACT, savedModel(), SELECTED_D4, SELECTED_E4 (+2 more)

### Community 99 - "Community 99"
Cohesion: 0.33
Nodes (10): AnalysisDashboard(), src_features_analysis_overview_analysisoverview_module, activeFilterCount(), AnalysisPage(), applyFilters(), resetFilters(), errorMessage(), filtersFromDraft() (+2 more)

### Community 100 - "Community 100"
Cohesion: 0.20
Nodes (8): Disclosure(), DisclosureProps, CollapsedByDefault, LONG_CONTENT, meta, OpenByDefault, Story, WithLongContent

### Community 101 - "Community 101"
Cohesion: 0.22
Nodes (6): FEEDBACK_GROUPS, FixedDarkTokenSource, meta, Story, StorySpecimenTokenOverview(), SYSTEM_ROLES

### Community 102 - "Community 102"
Cohesion: 0.18
Nodes (10): LoadingGate, meta, OpponentLocalOnly, OpponentTurnGate, ReadErrors, Story, UnsavableGate, expectActiveSessionHistoryEntry() (+2 more)

### Community 103 - "Community 103"
Cohesion: 0.20
Nodes (10): scripts, build, build-storybook, dev, format, format:check, lint, storybook (+2 more)

### Community 104 - "Community 104"
Cohesion: 0.24
Nodes (8): BoardControl(), BoardControlProps, BoardEvalStageProps, InteractiveBoardAdapterProps, MoveHistoryControlledState, BoardContentProps, HistoryProps, RepertoireBoardLaneProps

### Community 105 - "Community 105"
Cohesion: 0.20
Nodes (4): ChartLabel, here, rawStyles, MoveResponseDistributionClient

### Community 106 - "Community 106"
Cohesion: 0.29
Nodes (8): actionClass(), PreferredMoveActionButtonProps, RemovePreferredMoveButton(), SavePreferredMoveButton(), ActionButtons, meta, PendingSave, Story

### Community 107 - "Community 107"
Cohesion: 0.22
Nodes (6): formDataBodySerializer, jsonBodySerializer, QuerySerializerOptionsObject, urlSearchParamsBodySerializer, ArrayStyle, ObjectStyle

### Community 108 - "Community 108"
Cohesion: 0.22
Nodes (7): Default, Empty, ErrorState, Loading, meta, sampleData, Story

### Community 109 - "Community 109"
Cohesion: 0.28
Nodes (8): createMoveHistoryRows(), KEY_NAVIGATION, src_features_move_history_movehistory_module, MoveHistory(), handleKeyDown(), renderEntry(), MoveHistoryProps, MoveHistoryRow

### Community 110 - "Community 110"
Cohesion: 0.22
Nodes (6): Constrained, HISTORY, Interactive, meta, Story, MoveHistoryInput

### Community 111 - "Community 111"
Cohesion: 0.22
Nodes (8): RepertoireBoardLane(), board, controls, evaluation, history, meta, Standard, Story

### Community 112 - "Community 112"
Cohesion: 0.22
Nodes (4): fixture(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 113 - "Community 113"
Cohesion: 0.29
Nodes (5): BoardFixture(), display(), ResizeObserverInstance, ResizeObserverMock, resizeObservers

### Community 115 - "Community 115"
Cohesion: 0.48
Nodes (6): isPlainObject(), JsonValue, queryKeyJsonReplacer(), serializeQueryKeyValue(), serializeSearchParams(), stringifyToJsonValue()

### Community 116 - "Community 116"
Cohesion: 0.29
Nodes (3): dirname, pythonPath, repoRoot

### Community 117 - "Community 117"
Cohesion: 0.38
Nodes (4): PageNotFoundView(), Default, meta, Story

### Community 118 - "Community 118"
Cohesion: 0.29
Nodes (6): HEADINGS, InlineMatrix, MESSAGES, meta, SEVERITIES, Story

### Community 119 - "Community 119"
Cohesion: 0.29
Nodes (5): here, materialDir, previewPath, provenance, SIX_MEMBERS

### Community 120 - "Community 120"
Cohesion: 0.29
Nodes (4): here, HISTORY, moduleCss, MoveHistoryActivePlyChange

### Community 121 - "Community 121"
Cohesion: 0.33
Nodes (5): MESSAGES, meta, SemanticVariants, SEVERITIES, Story

### Community 122 - "Community 122"
Cohesion: 0.33
Nodes (5): ACCENT_TOKEN, CONTAINER_TOKEN, here, moduleCss, SEVERITIES

### Community 124 - "Community 124"
Cohesion: 0.40
Nodes (4): printWidth, semi, singleQuote, trailingComma

### Community 125 - "Community 125"
Cohesion: 0.50
Nodes (3): @testing-library/jest-dom, elementProto, topLayerPseudoSelectors

### Community 126 - "Community 126"
Cohesion: 0.50
Nodes (3): client, CreateClientConfig, ClientOptions

## Knowledge Gaps
- **937 isolated node(s):** `QueryKey`, `ContractOperation`, `RenderableMenuItem`, `Story`, `MenuActionItemDefinition` (+932 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1306 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **124 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 3` to `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 9`, `Community 10`, `Community 12`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 20`, `Community 22`, `Community 23`, `Community 24`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 29`, `Community 30`, `Community 31`, `Community 33`, `Community 39`, `Community 42`, `Community 43`, `Community 48`, `Community 51`, `Community 52`, `Community 54`, `Community 56`, `Community 60`, `Community 63`, `Community 65`, `Community 67`, `Community 69`, `Community 70`, `Community 73`, `Community 75`, `Community 78`, `Community 80`, `Community 81`, `Community 82`, `Community 83`, `Community 85`, `Community 89`, `Community 92`, `Community 93`, `Community 96`, `Community 99`, `Community 100`, `Community 108`, `Community 109`, `Community 110`, `Community 113`, `Community 120`?**
  _High betweenness centrality (0.258) - this node is a cross-community bridge._
- **Why does `vitest` connect `Community 48` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 22`, `Community 24`, `Community 27`, `Community 28`, `Community 32`, `Community 33`, `Community 38`, `Community 39`, `Community 43`, `Community 44`, `Community 46`, `Community 47`, `Community 49`, `Community 52`, `Community 53`, `Community 56`, `Community 57`, `Community 58`, `Community 60`, `Community 61`, `Community 62`, `Community 64`, `Community 65`, `Community 68`, `Community 73`, `Community 77`, `Community 78`, `Community 79`, `Community 80`, `Community 82`, `Community 89`, `Community 96`, `Community 97`, `Community 98`, `Community 101`, `Community 105`, `Community 112`, `Community 113`, `Community 116`, `Community 117`, `Community 119`, `Community 120`, `Community 122`, `Community 123`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `@storybook/react-vite` connect `Community 7` to `Community 3`, `Community 5`, `Community 6`, `Community 10`, `Community 12`, `Community 13`, `Community 16`, `Community 20`, `Community 23`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 29`, `Community 34`, `Community 37`, `Community 39`, `Community 40`, `Community 42`, `Community 43`, `Community 45`, `Community 51`, `Community 52`, `Community 53`, `Community 55`, `Community 56`, `Community 58`, `Community 68`, `Community 69`, `Community 70`, `Community 71`, `Community 78`, `Community 82`, `Community 83`, `Community 85`, `Community 90`, `Community 92`, `Community 94`, `Community 95`, `Community 96`, `Community 97`, `Community 100`, `Community 101`, `Community 102`, `Community 106`, `Community 108`, `Community 110`, `Community 111`, `Community 117`, `Community 118`, `Community 121`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **What connects `QueryKey`, `ContractOperation`, `RenderableMenuItem` to the rest of the system?**
  _937 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05892634207240949 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.04107981220657277 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06944444444444445 - nodes in this community are weakly interconnected._

This graph represents the complete pre-commit working tree, including local changes. See manifest.json for per-file content hashes.
