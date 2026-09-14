import { Chess } from "chess.js";

export type ChessSide = "white" | "black";

export type Fen = string;

export type Ply = number;

export type San = string | null;

/**
 * The part of a FEN that identifies a position for server reads.
 * Halfmove and fullmove counters are intentionally excluded.
 */
export function positionKeyFromFen(fen: Fen): string {
  return fen.split(" ").slice(0, 4).join(" ");
}

export function strictFen(chess: Chess): Fen {
  const fen = chess.fen({ forceEnpassantSquare: true });
  const lastMove = chess.history({ verbose: true }).at(-1);

  if (!lastMove?.isBigPawn() || fen.split(" ")[3] !== "-") {
    return fen;
  }

  const fields = fen.split(" ");
  fields[3] = `${lastMove.to[0]}${lastMove.color === "w" ? "3" : "6"}`;
  return fields.join(" ");
}
