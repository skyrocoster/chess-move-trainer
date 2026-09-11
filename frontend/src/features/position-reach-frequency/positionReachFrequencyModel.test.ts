import { describe, expect, it } from "vitest";

import type { PositionContextResponse } from "../position-context/positionContextApi";
import { derivePositionReachFrequencyModel } from "./positionReachFrequencyModel";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return {
    fen: FEN,
    trainerColor: "white",
    observedInGames: true,
    distinctGameCount: 2,
    totalGameCount: 5,
    ...overrides,
  };
}

describe("derivePositionReachFrequencyModel", () => {
  it("uses the trainer color's distinct game count and total without another colour input", () => {
    expect(derivePositionReachFrequencyModel(context(), "white")).toMatchObject({
      selectedColor: "white",
      state: "available",
      reached: 2,
      total: 5,
      percentage: 40,
      meterValue: 40,
      fractionLabel: "2 / 5 games",
      percentageLabel: "40%",
    });
  });

  it("uses an independently loaded Black insight for its distinct count and total", () => {
    expect(
      derivePositionReachFrequencyModel(
        context({ trainerColor: "black", distinctGameCount: 3, totalGameCount: 7 }),
        "black",
      ),
    ).toMatchObject({
      selectedColor: "black",
      state: "available",
      reached: 3,
      total: 7,
      percentage: 42.857142857142854,
      fractionLabel: "3 / 7 games",
      percentageLabel: "42.9%",
    });
  });

  it("keeps an existing zero distinct-game count available at zero percent", () => {
    expect(
      derivePositionReachFrequencyModel(context({ distinctGameCount: 0 }), "white"),
    ).toMatchObject({
      state: "available",
      reached: 0,
      total: 5,
      percentage: 0,
      meterValue: 0,
      fractionLabel: "0 / 5 games",
      percentageLabel: "0%",
    });
  });

  it("keeps a globally unseen position distinct from an available zero", () => {
    expect(
      derivePositionReachFrequencyModel(
        context({ observedInGames: false, distinctGameCount: 0, totalGameCount: 0 }),
        "white",
      ),
    ).toMatchObject({
      state: "absent",
      reached: null,
      total: null,
      percentage: null,
      meterValue: 0,
      fractionLabel: null,
      percentageLabel: null,
    });
  });

  it("keeps unavailable data distinct from both position states", () => {
    expect(derivePositionReachFrequencyModel(null, "black")).toMatchObject({
      selectedColor: "black",
      state: "unavailable",
      reached: null,
      total: null,
      percentage: null,
      fractionLabel: null,
      percentageLabel: null,
    });
  });

  it("bounds an unsafe percentage and avoids division by zero", () => {
    expect(
      derivePositionReachFrequencyModel(
        context({ distinctGameCount: 9, totalGameCount: 4 }),
        "white",
      ).percentage,
    ).toBe(100);
    expect(
      derivePositionReachFrequencyModel(
        context({ distinctGameCount: 1, totalGameCount: 0 }),
        "white",
      ).percentage,
    ).toBe(0);
  });
});
