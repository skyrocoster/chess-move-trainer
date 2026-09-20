import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { getPositionTrainingRequirements } from "./client";
import * as generatedSdk from "./generated/sdk.gen";

const dirname = path.dirname(fileURLToPath(import.meta.url));
type ContractOperation = {
  operationId?: string;
  responses?: Record<string, { content?: { "application/json"?: { schema?: unknown } } }>;
};

describe("generated SDK surface", () => {
  it("exports exactly the approved operation request functions", () => {
    const functionExports = Object.keys(generatedSdk).filter(
      (key) => typeof (generatedSdk as Record<string, unknown>)[key] === "function",
    );
    expect(functionExports).toEqual([
      "getHealth",
      "getGames",
      "getGame",
      "getAnalysis",
      "requestAnalysis",
      "deletePreferredMoves",
      "getPreferredMoves",
      "putPreferredMoves",
      "getPositionInsight",
      "getPositionTrainingRequirements",
      "submitPositionTrainingAnswer",
      "getOpenings",
      "getOpeningByKey",
    ]);
    expect(getPositionTrainingRequirements).toBe(generatedSdk.getPositionTrainingRequirements);
  });

  it("checked-in contract contains only the approved clean operations", () => {
    // Read the checked-in contract from disk so the test does not depend on
    // JSON module resolution settings.
    const contractPath = path.resolve(dirname, "generated", "openapi.json");
    const contract = JSON.parse(readFileSync(contractPath, "utf8")) as {
      paths: Record<string, Record<string, ContractOperation>>;
      components: { schemas: Record<string, unknown> };
    };

    expect(Object.keys(contract.paths)).toEqual([
      "/api/health",
      "/api/games",
      "/api/games/{game_uuid}",
      "/api/analysis",
      "/api/analysis-requests",
      "/api/preferred-moves",
      "/api/positions/insight",
      "/api/positions/training-requirements",
      "/api/positions/training-requirements/answers",
      "/api/openings",
      "/api/openings/{opening_key}",
    ]);
    expect(Object.keys(contract.paths["/api/analysis"])).toEqual(["get"]);
    expect(contract.paths["/api/analysis"].get?.operationId).toBe("getAnalysis");
    expect(Object.keys(contract.paths["/api/analysis-requests"])).toEqual(["post"]);
    expect(contract.paths["/api/analysis-requests"].post?.operationId).toBe("requestAnalysis");
    expect(Object.keys(contract.paths["/api/health"])).toEqual(["get"]);
    expect(contract.paths["/api/health"].get?.operationId).toBe("getHealth");
    expect(Object.keys(contract.paths["/api/games"])).toEqual(["get"]);
    expect(contract.paths["/api/games"].get?.operationId).toBe("getGames");
    expect(Object.keys(contract.paths["/api/games/{game_uuid}"])).toEqual(["get"]);
    expect(contract.paths["/api/games/{game_uuid}"].get?.operationId).toBe("getGame");
    expect(Object.keys(contract.paths["/api/openings"])).toEqual(["get"]);
    expect(contract.paths["/api/openings"].get?.operationId).toBe("getOpenings");
    expect(Object.keys(contract.paths["/api/openings/{opening_key}"])).toEqual(["get"]);
    expect(contract.paths["/api/openings/{opening_key}"].get?.operationId).toBe("getOpeningByKey");
    expect(Object.keys(contract.paths["/api/positions/insight"])).toEqual(["get"]);
    expect(contract.paths["/api/positions/insight"].get?.operationId).toBe("getPositionInsight");
    expect(Object.keys(contract.paths["/api/positions/training-requirements"])).toEqual(["get"]);
    expect(contract.paths["/api/positions/training-requirements"].get?.operationId).toBe(
      "getPositionTrainingRequirements",
    );
    expect(contract.paths["/api/positions/training-requirements/answers"].post?.operationId).toBe(
      "submitPositionTrainingAnswer",
    );
    expect(
      Object.keys(contract.paths["/api/positions/training-requirements"].get?.responses ?? {}),
    ).toEqual(["200", "409", "422", "500", "503"]);
    for (const status of ["422", "409", "500", "503"]) {
      expect(
        contract.paths["/api/positions/training-requirements"].get?.responses?.[status]?.content?.[
          "application/json"
        ]?.schema,
      ).toEqual({ $ref: "#/components/schemas/TrainingRequirementErrorResponse" });
    }
    expect(Object.keys(contract.paths["/api/preferred-moves"])).toEqual(["get", "put", "delete"]);
    expect(contract.paths["/api/preferred-moves"].get?.operationId).toBe("getPreferredMoves");
    expect(contract.paths["/api/preferred-moves"].put?.operationId).toBe("putPreferredMoves");
    expect(contract.paths["/api/preferred-moves"].delete?.operationId).toBe("deletePreferredMoves");
    expect(Object.keys(contract.components.schemas)).toEqual([
      "AnalysisObservationErrorResponse",
      "AnalysisObservationLineResponse",
      "AnalysisObservationResponse",
      "AnalysisObservationResultResponse",
      "AnalysisRequestBody",
      "AnalysisRequestErrorResponse",
      "GameCoverageResponse",
      "GameDetailOccurrenceResponse",
      "GameDetailResponse",
      "GameSummaryResponse",
      "GamesErrorResponse",
      "GamesResponse",
      "HTTPValidationError",
      "HealthResponse",
      "MovePreferenceResponse",
      "MutationMovePreferenceRequest",
      "MutationNoPreferenceRequest",
      "NoPreferenceResponse",
      "OpeningCatalogueErrorResponse",
      "OpeningCatalogueItemResponse",
      "OpeningCatalogueResponse",
      "OpeningDetailErrorResponse",
      "OpeningSummaryResponse",
      "PositionInsightAnalysisResponse",
      "PositionInsightErrorResponse",
      "PositionInsightExperienceResponse",
      "PositionInsightLineResponse",
      "PositionInsightObservedMoveResponse",
      "PositionInsightObservedMoveTotalsResponse",
      "PositionInsightOpeningResponse",
      "PositionInsightResponse",
      "PositionInsightResultResponse",
      "PositionInsightTerminalTotalsResponse",
      "PreferredMovesErrorResponse",
      "PreferredMovesMutationRequest",
      "PreferredMovesMutationResponse",
      "PreferredMovesPeriodResponse",
      "PreferredMovesRemovalRequest",
      "PreferredMovesRemovalResponse",
      "PreferredMovesResponse",
      "PreferredMovesSegmentResponse",
      "TrainingAnswerRequest",
      "TrainingAnswerResponse",
      "TrainingRequirementErrorResponse",
      "TrainingRequirementItemResponse",
      "TrainingRequirementPolicyResponse",
      "TrainingRequirementResponse",
      "UnconfiguredPreferenceResponse",
      "ValidationError",
    ]);
  });
});
