import { describe, expect, it } from "vitest";

import { positionKeyFromFen } from "../features/chess/chessPrimitives";
import { queryKeys } from "./queryKeys";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const DISTINCT_POSITION_FEN =
  "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";

describe("queryKeys", () => {
  it("uses one key for the complete sorted openings snapshot", () => {
    expect(queryKeys.openingsCatalogueSnapshot()).toEqual(["openingsCatalogueSnapshot"]);
  });

  it("normalizes the opening catalogue without losing fixed response inputs", () => {
    expect(
      queryKeys.openingsCatalogue({ search: "  sicilian ", pageSize: 100, sort: "name_asc" }),
    ).toEqual(["openingsCatalogue", { search: "sicilian", pageSize: 100, sort: "name_asc" }]);
    expect(
      queryKeys.openingsCatalogue({ search: "", pageSize: 100, sort: "name_asc" }),
    ).toEqual(queryKeys.openingsCatalogue({ search: "   ", pageSize: 100, sort: "name_asc" }));
  });

  it("normalizes complete training filters and keeps opening policy coherent", () => {
    const base = queryKeys.trainingRequirements({
      asOf: " 2026-09-14 ",
      trainerColor: " white ",
      openingKey: " sicilian ",
      openingMatch: "reached",
      trainingRequirementLt: 0,
      pageSize: 100,
    });

    expect(base).toEqual([
      "trainingRequirements",
      {
        asOf: "2026-09-14",
        trainerColor: "white",
        openingKey: "sicilian",
        openingMatch: "reached",
        trainingRequirementLt: 0,
        pageSize: 100,
      },
    ]);
    expect(
      queryKeys.trainingRequirements({
        asOf: "2026-09-14",
        trainerColor: "",
        openingKey: "",
        openingMatch: "reached",
        trainingRequirementLt: 0,
        pageSize: 100,
      }),
    ).toEqual([
      "trainingRequirements",
      {
        asOf: "2026-09-14",
        trainerColor: null,
        openingKey: null,
        openingMatch: null,
        trainingRequirementLt: 0,
        pageSize: 100,
      },
    ]);
  });

  it("normalizes game identity and includes the preferred UTC date window", () => {
    expect(queryKeys.gameDetail({ gameUuid: " game-uuid " })).toEqual(["gameDetail", "game-uuid"]);
    expect(
      queryKeys.preferredMove({
        positionKey: ` ${positionKeyFromFen(FEN)} `,
        today: " 2026-09-14 ",
        tomorrow: " 2026-09-15 ",
      }),
    ).toEqual([
      "preferredMove",
      positionKeyFromFen(FEN),
      { today: "2026-09-14", tomorrow: "2026-09-15" },
    ]);
  });

  it("shares counter-only FEN variants and separates actual positions", () => {
    const insightKey = (fen: string) =>
      queryKeys.positionInsight({
        positionKey: positionKeyFromFen(fen),
        trainerColor: "white",
        asOf: "2026-09-14",
      });

    expect(insightKey(FEN)).toEqual(insightKey(COUNTER_VARIANT_FEN));
    expect(insightKey(FEN)).not.toEqual(insightKey(DISTINCT_POSITION_FEN));
    expect(
      queryKeys.positionInsight({
        positionKey: positionKeyFromFen(FEN),
        trainerColor: "",
        asOf: " 2026-09-14 ",
      }),
    ).toEqual([
      "positionInsight",
      positionKeyFromFen(FEN),
      { trainerColor: null, asOf: "2026-09-14" },
    ]);
  });

  it("keeps analysis observations structural and query-input order independent", () => {
    expect(
      queryKeys.analysisObservation({ positionKey: ` ${positionKeyFromFen(FEN)} ` }),
    ).toEqual(["analysisObservation", positionKeyFromFen(FEN)]);
    expect(
      queryKeys.trainingRequirements({
        asOf: "2026-09-14",
        trainerColor: "white",
        openingKey: "sicilian",
        openingMatch: "reached",
        trainingRequirementLt: 0,
        pageSize: 100,
      }),
    ).toEqual(
      queryKeys.trainingRequirements({
        pageSize: 100,
        trainingRequirementLt: 0,
        openingMatch: "reached",
        openingKey: "sicilian",
        trainerColor: "white",
        asOf: "2026-09-14",
      }),
    );
  });
});
