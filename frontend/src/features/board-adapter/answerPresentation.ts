import type { Square } from "chess.js";
import type { CSSProperties } from "react";

import { LAST_MOVE_SQUARE_STYLE, type LastMove } from "./lastMove";

/**
 * Semantic answer states the board can present. The trainer (or any caller)
 * decides which state the board is in; the board only renders it.
 */
export type BoardAnswerStatus =
  | "awaiting-input"
  | "illegal"
  | "incorrect"
  | "correct"
  | "revealed"
  | "disabled";

/**
 * A board-level answer presentation: the semantic status plus the attempted
 * (played or rejected) move and, when applicable, the expected move to reveal.
 */
export type BoardAnswerPresentation = {
  status: BoardAnswerStatus;
  attemptedMove?: LastMove | null;
  expectedMove?: LastMove | null;
  /** Optional override for the board-level status announcement. */
  message?: string;
};

export type BoardSquareHighlight = Record<string, CSSProperties>;

const ANSWER_SQUARE_FILL: Record<
  Exclude<BoardAnswerStatus, "awaiting-input" | "disabled">,
  string
> = {
  illegal: "rgba(248, 113, 113, 0.45)",
  incorrect: "rgba(251, 146, 60, 0.42)",
  correct: "rgba(134, 239, 172, 0.45)",
  revealed: "rgba(147, 197, 253, 0.42)",
};

const ANSWER_SQUARE_RING: Record<
  Exclude<BoardAnswerStatus, "awaiting-input" | "disabled">,
  string
> = {
  illegal: "inset 0 0 0 3px rgba(127, 29, 29, 0.5)",
  incorrect: "inset 0 0 0 3px rgba(124, 45, 18, 0.5)",
  correct: "inset 0 0 0 3px rgba(20, 83, 45, 0.5)",
  revealed: "inset 0 0 0 3px rgba(30, 64, 175, 0.5)",
};

export const DEFAULT_ANSWER_MESSAGES: Record<BoardAnswerStatus, string> = {
  "awaiting-input": "Awaiting your move.",
  illegal: "That move is illegal here.",
  incorrect: "That move is legal but not the expected move.",
  correct: "Correct move.",
  revealed: "The expected move is highlighted on the board.",
  disabled: "The board is locked while the position updates.",
};

/**
 * Non-locking illegal-attempt treatment for a directly rejected drag/drop.
 * It reuses the locked illegal answer colors so users see the same red
 * source/target highlight, but the board stays interactive so they can
 * immediately try a different move.
 */
export const ILLEGAL_ATTEMPT_SQUARE_STYLE: CSSProperties = {
  backgroundColor: ANSWER_SQUARE_FILL.illegal,
  boxShadow: ANSWER_SQUARE_RING.illegal,
};

export function illegalAttemptSquareStyles(
  attemptedMove: LastMove | null | undefined,
): BoardSquareHighlight {
  if (!attemptedMove) {
    return {};
  }

  return {
    [attemptedMove.sourceSquare as Square]: { ...ILLEGAL_ATTEMPT_SQUARE_STYLE },
    [attemptedMove.targetSquare as Square]: { ...ILLEGAL_ATTEMPT_SQUARE_STYLE },
  };
}

/**
 * The board allows interaction only while awaiting input. Callers pass a
 * presentation when they own the answer lifecycle; with no presentation the
 * board behaves exactly as before (interaction allowed).
 */
export function answerInteractionAllowed(
  answer: BoardAnswerPresentation | null | undefined,
): boolean {
  if (!answer) {
    return true;
  }
  return answer.status === "awaiting-input";
}

export function answerMessage(answer: BoardAnswerPresentation): string {
  return answer.message ?? DEFAULT_ANSWER_MESSAGES[answer.status];
}

/**
 * Builds square highlights for an answer presentation: the attempted move's
 * source and target squares get the status fill, and the expected move's
 * squares get the expected-move ring so both treatments can coexist.
 */
export function answerSquareStyles(
  answer: BoardAnswerPresentation | null | undefined,
): BoardSquareHighlight {
  if (!answer) {
    return {};
  }

  if (answer.status === "awaiting-input" || answer.status === "disabled") {
    return {};
  }

  const fill = ANSWER_SQUARE_FILL[answer.status];
  const ring = ANSWER_SQUARE_RING[answer.status];

  const styles: BoardSquareHighlight = {};
  const attempted = answer.attemptedMove;
  if (attempted) {
    styles[attempted.sourceSquare as Square] = squareStyle(fill, ring);
    styles[attempted.targetSquare as Square] = squareStyle(fill, ring);
  }

  const expected = answer.expectedMove;
  if (expected) {
    for (const square of [expected.sourceSquare, expected.targetSquare] as Square[]) {
      styles[square] = {
        ...styles[square],
        backgroundColor: fill,
        boxShadow: `${ANSWER_SQUARE_RING[answer.status]}, inset 0 0 0 6px ${ringTransparent(
          answer.status,
        )}`,
      };
    }
  }

  return styles;
}

function squareStyle(fill: string, ring: string): CSSProperties {
  return { backgroundColor: fill, boxShadow: ring };
}

function ringTransparent(status: Exclude<BoardAnswerStatus, "awaiting-input" | "disabled">) {
  const rgba = ANSWER_SQUARE_RING[status].match(/rgba\([^)]+\)/)?.[0] ?? ANSWER_SQUARE_RING[status];
  return rgba.replace(/,\s*[\d.]+\)$/, ", 0.25)");
}

/**
 * The single composition point for the interactive board's square highlights:
 * the last-move context (its own yellow treatment) underneath, then a
 * non-locking illegal-attempt highlight, with any answer-state highlights
 * layered on top so a semantic status wins wherever the treatments share a
 * square.
 */
export function boardSquareStyles(
  answer: BoardAnswerPresentation | null | undefined,
  lastMove: LastMove | null | undefined,
  rejectedMove: LastMove | null | undefined = null,
): BoardSquareHighlight {
  const styles: BoardSquareHighlight = {};

  if (lastMove) {
    styles[lastMove.sourceSquare as Square] = { ...LAST_MOVE_SQUARE_STYLE };
    styles[lastMove.targetSquare as Square] = { ...LAST_MOVE_SQUARE_STYLE };
  }

  if (rejectedMove) {
    Object.assign(styles, illegalAttemptSquareStyles(rejectedMove));
  }

  return { ...styles, ...answerSquareStyles(answer) };
}
