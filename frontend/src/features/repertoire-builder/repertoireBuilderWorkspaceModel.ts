import { Chess, type PieceSymbol, type Square } from "chess.js";

import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import type { BranchMove } from "../board-adapter/branchModel";
import type { ChessSide } from "../chess/chessPrimitives";
import type {
  PositionPickerSessionBoundary,
  SessionPosition,
} from "./positionPickerSessionBoundary";
import type { PromotionPiece } from "../board-adapter/PromotionPicker";

export function orientationDescription(orientation: BoardOrientation): string {
  return orientation === "white" ? "White at the bottom" : "Black at the bottom";
}

export function boardLabel(
  session: PositionPickerSessionBoundary,
  orientation: BoardOrientation,
): string {
  const orientationLabel = orientationDescription(orientation);
  if (session.kind === "fresh") {
    return `Chess board: standard starting position, ${orientationLabel}`;
  }
  return `Chess board: game ${session.mainLine!.gameUuid}, ply ${session.currentPosition.ply}, ${orientationLabel}`;
}

export function originDescription(session: PositionPickerSessionBoundary): string {
  if (session.kind === "fresh") {
    return "Standard starting position; local session begins at Ply 0.";
  }
  return `Game ${session.mainLine!.gameUuid}; complete game loaded at Ply 0.`;
}

export function sessionViewKey(session: PositionPickerSessionBoundary): string {
  return session.kind === "fresh"
    ? "repertoire:standard"
    : `repertoire:${session.mainLine!.gameUuid}`;
}

function moveFromUci(uci: string) {
  const promotion = uci.slice(4);
  return {
    from: uci.slice(0, 2) as Square,
    to: uci.slice(2, 4) as Square,
    ...(promotion ? { promotion: promotion as PieceSymbol } : {}),
  };
}

function sideFromColor(color: "w" | "b"): ChessSide {
  return color === "w" ? "white" : "black";
}

export function branchMoves(
  session: PositionPickerSessionBoundary,
): readonly BranchMove[] {
  if (session.branch === null) {
    return [];
  }

  const branchLength = Math.max(
    0,
    session.currentIndex - session.branch.branchPointIndex,
  );
  return session.branch.transitions.slice(0, branchLength).map((transition, index) => {
    const chess = new Chess(transition.parentFEN);
    const move = chess.move(moveFromUci(transition.outgoingUCI));
    const position: SessionPosition | undefined = session.branch?.positions[index];
    return {
      color: sideFromColor(move.color),
      from: move.from,
      to: move.to,
      san: position?.san ?? move.san,
      ...(move.promotion ? { promotion: move.promotion } : {}),
    };
  });
}

export function promotionPiece(value: string | undefined): PromotionPiece | undefined {
  return value === "q" || value === "r" || value === "b" || value === "n" ? value : undefined;
}
