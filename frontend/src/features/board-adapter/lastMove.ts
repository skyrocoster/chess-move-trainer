import { Chess, type Square } from "chess.js";
import type { CSSProperties } from "react";

export type LastMove = {
  sourceSquare: Square;
  targetSquare: Square;
};

const LAST_MOVE_SQUARE_STYLE: CSSProperties = {
  backgroundColor: "rgba(250, 204, 21, 0.42)",
  boxShadow: "inset 0 0 0 3px rgba(146, 94, 0, 0.42)",
};

export function lastMoveFromSquares(sourceSquare: Square, targetSquare: Square): LastMove {
  return { sourceSquare, targetSquare };
}

export function deriveLastMove(
  previousFen: string | null | undefined,
  san: string | null | undefined,
): LastMove | null {
  if (!previousFen || !san) {
    return null;
  }

  try {
    const chess = new Chess(previousFen);
    const move = chess.move(san);
    return lastMoveFromSquares(move.from, move.to);
  } catch {
    return null;
  }
}

export function lastMoveSquareStyles(
  lastMove: LastMove | null | undefined,
): Record<string, CSSProperties> {
  if (!lastMove) {
    return {};
  }

  return {
    [lastMove.sourceSquare]: LAST_MOVE_SQUARE_STYLE,
    [lastMove.targetSquare]: LAST_MOVE_SQUARE_STYLE,
  };
}
