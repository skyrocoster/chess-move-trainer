import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import * as generatedSdk from "./generated/sdk.gen";

const dirname = path.dirname(fileURLToPath(import.meta.url));

describe("SETUP-02 generated SDK surface", () => {
  it("exports exactly the approved operation request functions", () => {
    const functionExports = Object.keys(generatedSdk).filter(
      (key) => typeof (generatedSdk as Record<string, unknown>)[key] === "function",
    );
    expect(functionExports).toEqual([
      "getAnalysis",
      "requestAnalysis",
      "getGames",
      "getGame",
      "getHealth",
      "getOpenings",
      "getOpeningByKey",
      "getPositionInsight",
      "deletePreferredMoves",
      "getPreferredMoves",
      "putPreferredMoves",
    ]);
    expect(typeof generatedSdk.deletePreferredMoves).toBe("function");
    expect(typeof generatedSdk.getAnalysis).toBe("function");
    expect(typeof generatedSdk.requestAnalysis).toBe("function");
    expect(typeof generatedSdk.getHealth).toBe("function");
    expect(typeof generatedSdk.getGames).toBe("function");
    expect(typeof generatedSdk.getGame).toBe("function");
    expect(typeof generatedSdk.getOpenings).toBe("function");
    expect(typeof generatedSdk.getOpeningByKey).toBe("function");
    expect(typeof generatedSdk.getPositionInsight).toBe("function");
    expect(typeof generatedSdk.getPreferredMoves).toBe("function");
    expect(typeof generatedSdk.putPreferredMoves).toBe("function");
  });

  it("checked-in contract contains only the approved clean operations", () => {
    // Read the checked-in contract from disk so the test does not depend on
    // JSON module resolution settings.
    const contractPath = path.resolve(dirname, "generated", "openapi.json");
    const contract = JSON.parse(readFileSync(contractPath, "utf8")) as {
      paths: Record<string, Record<string, { operationId?: string }>>;
      components: { schemas: Record<string, unknown> };
    };

    expect(Object.keys(contract.paths)).toEqual([
      "/api/analysis",
      "/api/analysis-requests",
      "/api/games",
      "/api/games/{game_uuid}",
      "/api/health",
      "/api/openings",
      "/api/openings/{opening_key}",
      "/api/positions/insight",
      "/api/preferred-moves",
    ]);
    expect(Object.keys(contract.paths["/api/analysis"])).toEqual(["get"]);
    expect(contract.paths["/api/analysis"].get?.operationId).toBe("getAnalysis");
    expect(Object.keys(contract.paths["/api/analysis-requests"])).toEqual(["post"]);
    expect(contract.paths["/api/analysis-requests"].post?.operationId).toBe(
      "requestAnalysis",
    );
    expect(Object.keys(contract.paths["/api/health"])).toEqual(["get"]);
    expect(contract.paths["/api/health"].get?.operationId).toBe("getHealth");
    expect(Object.keys(contract.paths["/api/games"])).toEqual(["get"]);
    expect(contract.paths["/api/games"].get?.operationId).toBe("getGames");
    expect(Object.keys(contract.paths["/api/games/{game_uuid}"])).toEqual(["get"]);
    expect(contract.paths["/api/games/{game_uuid}"].get?.operationId).toBe("getGame");
    expect(Object.keys(contract.paths["/api/openings"])).toEqual(["get"]);
    expect(contract.paths["/api/openings"].get?.operationId).toBe("getOpenings");
    expect(Object.keys(contract.paths["/api/openings/{opening_key}"])).toEqual(["get"]);
    expect(contract.paths["/api/openings/{opening_key}"].get?.operationId).toBe(
      "getOpeningByKey",
    );
    expect(Object.keys(contract.paths["/api/positions/insight"])).toEqual(["get"]);
    expect(contract.paths["/api/positions/insight"].get?.operationId).toBe(
      "getPositionInsight",
    );
    expect(Object.keys(contract.paths["/api/preferred-moves"])).toEqual([
      "delete",
      "get",
      "put",
    ]);
    expect(contract.paths["/api/preferred-moves"].get?.operationId).toBe(
      "getPreferredMoves",
    );
    expect(contract.paths["/api/preferred-moves"].put?.operationId).toBe(
      "putPreferredMoves",
    );
    expect(contract.paths["/api/preferred-moves"].delete?.operationId).toBe(
      "deletePreferredMoves",
    );
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
      "PositionInsightOpeningResponse",
      "PositionInsightResponse",
      "PositionInsightResultResponse",
      "PreferredMovesErrorResponse",
      "PreferredMovesMutationRequest",
      "PreferredMovesMutationResponse",
      "PreferredMovesPeriodResponse",
      "PreferredMovesRemovalRequest",
      "PreferredMovesRemovalResponse",
      "PreferredMovesResponse",
      "PreferredMovesSegmentResponse",
      "UnconfiguredPreferenceResponse",
      "ValidationError",
    ]);
  });

  it("does not adopt the preferred-moves client in production source", () => {
    const sourceRoot = path.resolve(dirname, "..");
    const productionFiles: string[] = [];

    const collect = (directory: string) => {
      for (const entry of readdirSync(directory, { withFileTypes: true })) {
        const entryPath = path.join(directory, entry.name);
        if (entry.isDirectory()) {
          if (entry.name !== "api") collect(entryPath);
        } else if (/\.(ts|tsx)$/.test(entry.name) && !entry.name.endsWith(".test.ts")) {
          productionFiles.push(entryPath);
        }
      }
    };

    collect(sourceRoot);
    const adoption = productionFiles.filter((filePath) => {
      const source = readFileSync(filePath, "utf8");
      return (
        source.includes("getPreferredMoves") ||
        source.includes("putPreferredMoves") ||
        source.includes("deletePreferredMoves")
      );
    });
    expect(adoption).toEqual([]);
  });
});
