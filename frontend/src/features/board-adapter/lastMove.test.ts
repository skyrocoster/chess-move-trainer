import { describe, expect, it } from "vitest";

import { deriveLastMove, lastMoveFromSquares, lastMoveSquareStyles } from "./lastMove";

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

describe("last move", () => {
  it.each([
    ["a regular move", STARTING_FEN, "e4", "e2", "e4"],
    ["castling", "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", "O-O", "e1", "g1"],
    ["promotion", "k7/4P3/8/8/8/8/8/4K3 w - - 0 1", "e8=Q+", "e7", "e8"],
    ["en-passant", "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2", "exd6", "e5", "d6"],
  ] as const)("derives source and destination for %s", (_, previousFen, san, source, target) => {
    expect(deriveLastMove(previousFen, san)).toEqual(lastMoveFromSquares(source, target));
  });

  it("returns no move for an initial, missing, or invalid historical position", () => {
    expect(deriveLastMove(STARTING_FEN, null)).toBeNull();
    expect(deriveLastMove(null, "e4")).toBeNull();
    expect(deriveLastMove(STARTING_FEN, "not SAN")).toBeNull();
  });

  it("styles exactly the source and destination squares and leaves an empty board unchanged", () => {
    expect(lastMoveSquareStyles(null)).toEqual({});

    const styles = lastMoveSquareStyles(lastMoveFromSquares("e2", "e4"));
    expect(Object.keys(styles)).toEqual(["e2", "e4"]);
    expect(styles.e2).toEqual(styles.e4);
    expect(styles.e2).toMatchObject({
      backgroundColor: "rgba(250, 204, 21, 0.42)",
      boxShadow: "inset 0 0 0 3px rgba(146, 94, 0, 0.42)",
    });
  });
});
