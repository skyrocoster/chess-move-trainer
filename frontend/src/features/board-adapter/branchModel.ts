import type { Move } from "chess.js";

export type BranchMove = Pick<Move, "color" | "from" | "to" | "san"> & {
  promotion?: string;
};

export type BranchSnapshot = {
  viewKey: string;
  resetToken: number;
  originFen: string;
  currentFen: string;
  originPly: number;
  moves: readonly BranchMove[];
  active: boolean;
};
