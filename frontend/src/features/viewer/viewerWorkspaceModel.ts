import { Chess } from "chess.js";

import { STARTING_FEN, type BoardOrientation } from "../board-adapter/BoardAdapter";
import type { BranchMove } from "../board-adapter/branchModel";
import type { Game } from "./gameModel";

export const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";

export const START_BOARD = {
  fen: STARTING_FEN,
  orientation: "white" as BoardOrientation,
  label: BOARD_LABEL,
};

export const DEFAULT_BRANCH_NOTICE = "Make a legal move to start a temporary branch.";

export function historyMoves(chess: Chess): BranchMove[] {
  return chess.history({ verbose: true }).map((move) => ({
    color: move.color,
    from: move.from,
    to: move.to,
    san: move.san,
    ...(move.promotion ? { promotion: move.promotion } : {}),
  }));
}

export function terminalDescription(chess: Chess) {
  if (chess.isCheckmate()) {
    return "Checkmate";
  }
  if (chess.isStalemate()) {
    return "Stalemate";
  }
  if (chess.isInsufficientMaterial()) {
    return "Draw by insufficient material";
  }
  if (chess.isDrawByFiftyMoves()) {
    return "Draw by fifty-move rule";
  }
  return null;
}

export function oppositeOrientation(orientation: BoardOrientation): BoardOrientation {
  return orientation === "white" ? "black" : "white";
}

export function orientationDescription(orientation: BoardOrientation): string {
  return orientation === "white" ? "White at the bottom" : "Black at the bottom";
}

export function announcementFor(game: Game, index: number): string {
  const position = game.positions[index];
  const finalPly = game.positions.at(-1)?.ply ?? 0;
  return `Ply ${position.ply} of ${finalPly}: ${position.san ?? "Initial position"}`;
}
