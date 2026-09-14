import { describe, expect, it } from "vitest";

import {
  DEFAULT_ANSWER_MESSAGES,
  ILLEGAL_ATTEMPT_SQUARE_STYLE,
  answerInteractionAllowed,
  answerMessage,
  answerSquareStyles,
  boardSquareStyles,
  illegalAttemptSquareStyles,
} from "./answerPresentation";
import { lastMoveFromSquares } from "./lastMove";

describe("answerPresentation", () => {
  it("allows interaction only while awaiting input or without a presentation", () => {
    expect(answerInteractionAllowed(null)).toBe(true);
    expect(answerInteractionAllowed(undefined)).toBe(true);
    expect(answerInteractionAllowed({ status: "awaiting-input" })).toBe(true);
    for (const status of ["illegal", "incorrect", "correct", "revealed", "disabled"] as const) {
      expect(answerInteractionAllowed({ status })).toBe(false);
    }
  });

  it("falls back to the default message for each status", () => {
    for (const status of Object.keys(DEFAULT_ANSWER_MESSAGES) as Array<
      keyof typeof DEFAULT_ANSWER_MESSAGES
    >) {
      expect(answerMessage({ status })).toBe(DEFAULT_ANSWER_MESSAGES[status]);
    }
    expect(answerMessage({ status: "illegal", message: "Custom." })).toBe("Custom.");
  });

  it("returns no highlights while awaiting input or disabled", () => {
    expect(answerSquareStyles(null)).toEqual({});
    expect(answerSquareStyles({ status: "disabled" })).toEqual({});
    expect(
      answerSquareStyles({
        status: "disabled",
        attemptedMove: { sourceSquare: "e7", targetSquare: "e5" },
      }),
    ).toEqual({});
  });

  it("highlights the attempted move's source and target squares", () => {
    const styles = answerSquareStyles({
      status: "illegal",
      attemptedMove: { sourceSquare: "e7", targetSquare: "e5" },
    });
    expect(Object.keys(styles).sort()).toEqual(["e5", "e7"]);
    expect(styles.e7).toHaveProperty("backgroundColor");
    expect(styles.e7).toHaveProperty("boxShadow");
  });

  it("combines attempted and expected treatments on a shared square and rings expected squares", () => {
    const styles = answerSquareStyles({
      status: "incorrect",
      attemptedMove: { sourceSquare: "e7", targetSquare: "e5" },
      expectedMove: { sourceSquare: "e7", targetSquare: "e5" },
    });
    expect(Object.keys(styles).sort()).toEqual(["e5", "e7"]);
    for (const style of [styles.e5, styles.e7]) {
      expect(style?.boxShadow).toContain("inset 0 0 0 6px");
    }
  });

  it("keeps the last-move treatment distinct while awaiting input", () => {
    const styles = boardSquareStyles({ status: "awaiting-input" }, lastMoveFromSquares("e7", "e5"));
    expect(Object.keys(styles).sort()).toEqual(["e5", "e7"]);
    expect(styles.e7?.backgroundColor).toBe("rgba(250, 204, 21, 0.42)");
  });

  it("composes last-move context with answer highlights and answers win shared squares", () => {
    const styles = boardSquareStyles(
      {
        status: "correct",
        attemptedMove: { sourceSquare: "e7", targetSquare: "e5" },
      },
      lastMoveFromSquares("e7", "e5"),
    );
    expect(Object.keys(styles).sort()).toEqual(["e5", "e7"]);
    for (const style of [styles.e5, styles.e7]) {
      expect(style?.backgroundColor).not.toBe("rgba(250, 204, 21, 0.42)");
      expect(style?.backgroundColor).toContain("134, 239, 172");
    }
  });

  it("shows last-move highlights alone when a previous move exists without an answer", () => {
    const styles = boardSquareStyles(null, lastMoveFromSquares("a2", "a3"));
    expect(Object.keys(styles).sort()).toEqual(["a2", "a3"]);
    expect(styles.a2?.backgroundColor).toBe("rgba(250, 204, 21, 0.42)");
  });

  it("returns nothing when neither a last move nor an answer is given", () => {
    expect(boardSquareStyles(null, null)).toEqual({});
  });

  it("highlights a rejected illegal attempt without locking colors", () => {
    const styles = illegalAttemptSquareStyles(lastMoveFromSquares("e2", "e5"));
    expect(Object.keys(styles).sort()).toEqual(["e2", "e5"]);
    expect(styles.e2).toEqual(ILLEGAL_ATTEMPT_SQUARE_STYLE);
    expect(illegalAttemptSquareStyles(null)).toEqual({});
  });

  it("layers a rejected attempt over last move and an answer over both", () => {
    const layered = boardSquareStyles(null, lastMoveFromSquares("e2", "e4"), {
      sourceSquare: "e2",
      targetSquare: "e5",
    });
    expect(Object.keys(layered).sort()).toEqual(["e2", "e4", "e5"]);
    expect(layered.e5?.backgroundColor).toBe(ILLEGAL_ATTEMPT_SQUARE_STYLE.backgroundColor);

    const withAnswer = boardSquareStyles(
      {
        status: "correct",
        attemptedMove: { sourceSquare: "e2", targetSquare: "e4" },
      },
      lastMoveFromSquares("d2", "d4"),
      { sourceSquare: "e2", targetSquare: "e5" },
    );
    expect(withAnswer.e2?.backgroundColor).toContain("134, 239, 172");
    expect(withAnswer.e5?.backgroundColor).toBe(ILLEGAL_ATTEMPT_SQUARE_STYLE.backgroundColor);
  });
});
