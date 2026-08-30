import { describe, expect, it } from "vitest";

import type { PositionContextResponse } from "../viewer/positionContextApi";
import { derivePositionReachFrequencyModel } from "./positionReachFrequencyModel";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return {
    fen: FEN,
    overall_exists: true,
    white_count: 2,
    black_count: 3,
    white_total: 5,
    black_total: 7,
    ...overrides,
  };
}

describe("derivePositionReachFrequencyModel", () => {
  it("selects White's reached count and denominator without another colour input", () => {
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

  it("selects Black's independent reached count and denominator", () => {
    expect(derivePositionReachFrequencyModel(context(), "black")).toMatchObject({
      selectedColor: "black",
      state: "available",
      reached: 3,
      total: 7,
      percentage: 42.857142857142854,
      fractionLabel: "3 / 7 games",
      percentageLabel: "42.9%",
    });
  });

  it("keeps an existing zero-count position available at zero percent", () => {
    expect(
      derivePositionReachFrequencyModel(context({ white_count: 0 }), "white"),
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

  it("keeps an absent position distinct from an available zero", () => {
    expect(
      derivePositionReachFrequencyModel(
        context({ overall_exists: false, white_count: 0, black_count: 0 }),
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
        context({ white_count: 9, white_total: 4 }),
        "white",
      ).percentage,
    ).toBe(100);
    expect(
      derivePositionReachFrequencyModel(
        context({ black_count: 1, black_total: 0 }),
        "black",
      ).percentage,
    ).toBe(0);
  });
});
