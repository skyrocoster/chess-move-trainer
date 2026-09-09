import { client } from "./generated/client.gen";
import { getHealthOptions } from "./generated/@tanstack/react-query.gen";

/**
 * Central handwritten configuration for the generated API client.
 *
 * This module is the single import surface for the SETUP-02 generated client:
 * it applies the existing API base URL convention in one place and re-exports
 * the approved generated entrypoint and its clean response types. It is never
 * overwritten by generation (the generator cleans only `./generated/`).
 *
 * CONSUMER-01 makes this module the approved import surface for the Status
 * feature beginning in Stage 3: it re-exports the single generated TanStack
 * query option Status consumes (`getHealthOptions`). The generated TanStack
 * artifact is not exported through the generated entrypoint, so `getHealthOptions`
 * is exported explicitly from the TanStack artifact import, separate from the
 * generated entrypoint re-exports below.
 */
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5666";
client.setConfig({ baseUrl });

export { getHealthOptions };
export {
  deletePreferredMoves,
  getAnalysis,
  getGame,
  getGames,
  getHealth,
  getOpeningByKey,
  getOpenings,
  getPreferredMoves,
  getPositionInsight,
  putPreferredMoves,
  requestAnalysis,
} from "./generated/index";
export type {
  AnalysisRequestBody,
  AnalysisRequestErrorResponse,
  AnalysisObservationErrorResponse,
  AnalysisObservationLineResponse,
  AnalysisObservationResponse,
  AnalysisObservationResultResponse,
  GameCoverageResponse,
  GameDetailOccurrenceResponse,
  GameDetailResponse,
  GameSummaryResponse,
  GamesErrorResponse,
  GamesResponse,
  GetGameData,
  GetGameError,
  GetGameErrors,
  GetGameResponse,
  GetGameResponses,
  GetAnalysisData,
  GetAnalysisError,
  GetAnalysisErrors,
  GetAnalysisResponse,
  GetAnalysisResponses,
  GetGamesData,
  GetGamesError,
  GetGamesErrors,
  GetGamesResponse,
  GetGamesResponses,
  GetHealthData,
  GetHealthResponse,
  GetHealthResponses,
  HealthResponse,
  GetOpeningByKeyData,
  GetOpeningByKeyError,
  GetOpeningByKeyErrors,
  GetOpeningByKeyResponse,
  GetOpeningByKeyResponses,
  GetOpeningsData,
  GetOpeningsError,
  GetOpeningsErrors,
  GetOpeningsResponse,
  GetOpeningsResponses,
  GetPreferredMovesData,
  GetPreferredMovesError,
  GetPreferredMovesErrors,
  GetPreferredMovesResponse,
  GetPreferredMovesResponses,
  DeletePreferredMovesData,
  DeletePreferredMovesError,
  DeletePreferredMovesErrors,
  DeletePreferredMovesResponse,
  DeletePreferredMovesResponses,
  GetPositionInsightData,
  GetPositionInsightError,
  GetPositionInsightErrors,
  GetPositionInsightResponse,
  GetPositionInsightResponses,
  OpeningCatalogueErrorResponse,
  OpeningCatalogueItemResponse,
  OpeningCatalogueResponse,
  OpeningDetailErrorResponse,
  OpeningSummaryResponse,
  MovePreferenceResponse,
  MutationMovePreferenceRequest,
  MutationNoPreferenceRequest,
  NoPreferenceResponse,
  PositionInsightAnalysisResponse,
  PositionInsightErrorResponse,
  PositionInsightExperienceResponse,
  PositionInsightLineResponse,
  PositionInsightObservedMoveResponse,
  PositionInsightOpeningResponse,
  PositionInsightResponse,
  PositionInsightResultResponse,
  PreferredMovesErrorResponse,
  PreferredMovesMutationRequest,
  PreferredMovesMutationResponse,
  PreferredMovesPeriodResponse,
  PreferredMovesRemovalRequest,
  PreferredMovesRemovalResponse,
  PreferredMovesResponse,
  PreferredMovesSegmentResponse,
  PutPreferredMovesData,
  PutPreferredMovesError,
  PutPreferredMovesErrors,
  PutPreferredMovesResponse,
  PutPreferredMovesResponses,
  RequestAnalysisData,
  RequestAnalysisError,
  RequestAnalysisErrors,
  RequestAnalysisResponse,
  RequestAnalysisResponses,
  UnconfiguredPreferenceResponse,
} from "./generated/index";
