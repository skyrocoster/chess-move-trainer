import type { Move } from "chess.js";

import type { Fen, Ply } from "./chessPrimitives";

export type BranchMove = Pick<Move, "color" | "from" | "to" | "san"> & {
  promotion?: string;
};

export type BranchSnapshot = {
  viewKey: string;
  resetToken: number;
  originFen: Fen;
  currentFen: Fen;
  originPly: Ply;
  moves: readonly BranchMove[];
  active: boolean;
};
