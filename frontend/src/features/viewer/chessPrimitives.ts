import { Chess } from "chess.js";

export type ChessSide = "white" | "black";

export type Fen = string;

export type Ply = number;

export type San = string | null;

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
