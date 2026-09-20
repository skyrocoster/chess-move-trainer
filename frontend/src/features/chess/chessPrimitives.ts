import { Chess, type PieceSymbol, type Square } from "chess.js";

export type ChessSide = "white" | "black";

export type Fen = string;

export type Ply = number;

export type San = string | null;

export type UciMove = {
  from: Square;
  to: Square;
  promotion?: PieceSymbol;
};

const UCI_PATTERN = /^([a-h][1-8])([a-h][1-8])([qrbn])?$/;

export function parseUciMove(uci: string): UciMove {
  const match = UCI_PATTERN.exec(uci);
  if (match === null) {
    throw new Error(`Invalid UCI move: ${uci}`);
  }

  const from = match[1] as Square;
  const to = match[2] as Square;
  const promotion = match[3] as PieceSymbol | undefined;
  return promotion === undefined ? { from, to } : { from, to, promotion };
}

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
