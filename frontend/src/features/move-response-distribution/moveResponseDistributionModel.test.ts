import { describe, expect, it } from "vitest";

import type { MoveResponseDistributionResponse } from "./moveResponseDistributionApi";
import { deriveMoveResponseDistributionModel } from "./moveResponseDistributionModel";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function response(
  overrides: Partial<MoveResponseDistributionResponse> = {},
): MoveResponseDistributionResponse {
  return {
    fen: FEN,
    color: "white",
    matching_game_count: 4,
    outgoing_occurrence_count: 14,
    replies: [
      { rank: 2, child_uci: "d2d4", san: "d4", occurrence_count: 3 },
      { rank: 1, child_uci: "e2e4", san: "e4", occurrence_count: 5 },
      { rank: 3, child_uci: "c2c4", san: "c4", occurrence_count: 2 },
      { rank: 7, child_uci: "g1f3", san: "Nf3", occurrence_count: 1 },
      { rank: 5, child_uci: "c2c3", san: "c3", occurrence_count: 1 },
      { rank: 4, child_uci: "b2b3", san: "b3", occurrence_count: 1 },
      { rank: 6, child_uci: "f2f4", san: "f4", occurrence_count: 1 },
    ],
    ...overrides,
  };
}

describe("deriveMoveResponseDistributionModel", () => {
  it("ranks by occurrence count, breaks ties by UCI, keeps five common moves, and groups the tail", () => {
    const model = deriveMoveResponseDistributionModel(response());

    expect(model.state).toBe("available");
    expect(model.common.map((reply) => reply.child_uci)).toEqual([
      "e2e4",
      "d2d4",
      "c2c4",
      "b2b3",
      "c2c3",
    ]);
    expect(model.common.map((reply) => reply.rank)).toEqual([1, 2, 3, 4, 5]);
    expect(model.tail.map((reply) => reply.child_uci)).toEqual(["f2f4", "g1f3"]);
    expect(model.other).toMatchObject({
      occurrence_count: 2,
      percentage: (2 / 14) * 100,
      percentageLabel: "14.3%",
    });
  });

  it("computes percentages from the outgoing-occurrence denominator", () => {
    const model = deriveMoveResponseDistributionModel(response());

    expect(model).toMatchObject({ matchingGameCount: 4, outgoingOccurrenceCount: 14 });
    expect(model.common[0]).toMatchObject({
      child_uci: "e2e4",
      occurrence_count: 5,
      percentage: (5 / 14) * 100,
      percentageLabel: "35.7%",
      accessibleLabel: "e4, 5 occurrences, 35.7% of outgoing move occurrences",
    });
    expect(
      [...model.common, ...(model.other ? [model.other] : [])].reduce(
        (total, reply) => total + reply.percentage,
        0,
      ),
    ).toBeCloseTo(100, 10);
  });

  it("omits Other when all moves fit in the common list", () => {
    const replies = response().replies.slice(0, 5);
    const model = deriveMoveResponseDistributionModel(
      response({ replies, outgoing_occurrence_count: 11 }),
    );

    expect(model.other).toBeNull();
    expect(model.tail).toEqual([]);
  });

  it.each([
    [0, 0, "no-games", "No matching White repertoire games"],
    [4, 0, "no-moves", "No recorded next moves"],
  ] as const)(
    "distinguishes no matching games from matching games without next moves",
    (matchingGameCount, outgoingOccurrenceCount, state, message) => {
      const model = deriveMoveResponseDistributionModel(
        response({
          matching_game_count: matchingGameCount,
          outgoing_occurrence_count: outgoingOccurrenceCount,
          replies: [],
        }),
      );

      expect(model.state).toBe(state);
      expect(model.message).toContain(message);
      expect(model.other).toBeNull();
    },
  );
});
