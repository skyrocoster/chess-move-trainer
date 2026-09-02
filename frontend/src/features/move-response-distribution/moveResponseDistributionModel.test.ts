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
    replies: [
      { rank: 2, child_uci: "d2d4", san: "d4", distinct_game_count: 3, opening_name: null },
      { rank: 1, child_uci: "e2e4", san: "e4", distinct_game_count: 4, opening_name: null },
      {
        rank: 3,
        child_uci: "c2c4",
        san: "c4",
        distinct_game_count: 2,
        opening_name: "English Opening",
      },
      { rank: 4, child_uci: "g1f3", san: "Nf3", distinct_game_count: 1, opening_name: null },
      { rank: 5, child_uci: "c2c3", san: "c3", distinct_game_count: 1, opening_name: null },
      { rank: 6, child_uci: "b2b3", san: "b3", distinct_game_count: 1, opening_name: null },
      { rank: 7, child_uci: "f2f4", san: "f4", distinct_game_count: 1, opening_name: null },
    ],
    ...overrides,
  };
}

describe("deriveMoveResponseDistributionModel", () => {
  it("orders by supplied stable rank, keeps five common replies, and groups the full tail", () => {
    const model = deriveMoveResponseDistributionModel(response());

    expect(model.state).toBe("available");
    expect(model.common.map((reply) => reply.child_uci)).toEqual([
      "e2e4",
      "d2d4",
      "c2c4",
      "g1f3",
      "c2c3",
    ]);
    expect(model.tail.map((reply) => reply.child_uci)).toEqual(["b2b3", "f2f4"]);
    expect(model.other).toMatchObject({
      distinct_game_count: 2,
      percentage: 50,
      percentageLabel: "50%",
    });
  });

  it("computes percentages from the matching-game denominator without clamping overlap", () => {
    const model = deriveMoveResponseDistributionModel(response());

    expect(model.common[0]).toMatchObject({
      child_uci: "e2e4",
      percentage: 100,
      percentageLabel: "100%",
    });
    expect(model.common[1]).toMatchObject({
      child_uci: "d2d4",
      percentage: 75,
      percentageLabel: "75%",
    });
    expect(model.overlapNote).toContain("one game may appear in more than one reply");
  });

  it("omits Other when all replies fit in the common list", () => {
    const model = deriveMoveResponseDistributionModel(
      response({ replies: response().replies.slice(0, 5) }),
    );

    expect(model.other).toBeNull();
    expect(model.tail).toEqual([]);
  });

  it("preserves nullable names and creates no placeholder for an unclassified reply", () => {
    const model = deriveMoveResponseDistributionModel(
      response({ replies: response().replies.slice(0, 3) }),
    );

    expect(model.common[0]?.opening_name).toBeNull();
    expect(model.common[2]).toMatchObject({ opening_name: "English Opening" });
    expect(model.common[0]?.accessibleLabel).not.toContain("undefined");
  });

  it.each([
    [0, [], "No matching White repertoire games"],
    [4, [], "No recorded replies"],
  ])(
    "returns no-games state for matching count %i and reply count %i",
    (count, replies, message) => {
      const model = deriveMoveResponseDistributionModel(
        response({ matching_game_count: count, replies }),
      );

      expect(model.state).toBe("no-games");
      expect(model.message).toContain(message);
      expect(model.other).toBeNull();
    },
  );
});
