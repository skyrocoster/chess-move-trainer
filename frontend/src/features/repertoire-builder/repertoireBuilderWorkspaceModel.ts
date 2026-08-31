import type { PositionPickerMoveRecord, PositionPickerSession } from "./positionPickerSession";
import type { PromotionPiece } from "../board-adapter/PromotionPicker";

export function orientationDescription(orientation: PositionPickerSession["orientation"]): string {
  return orientation === "white" ? "White at the bottom" : "Black at the bottom";
}

export function boardLabel(session: PositionPickerSession): string {
  const orientation = orientationDescription(session.orientation);
  if (session.origin.kind === "standard") {
    return `Chess board: standard starting position, ${orientation}`;
  }
  return `Chess board: game ${session.origin.gameUuid}, ply ${session.currentPly}, ${orientation}`;
}

export function originDescription(session: PositionPickerSession): string {
  if (session.origin.kind === "standard") {
    return "Standard starting position; local session begins at Ply 0.";
  }
  return `Game ${session.origin.gameUuid}; complete prefix through Ply ${session.origin.selectedPly}.`;
}

export function sessionViewKey(session: PositionPickerSession): string {
  return session.origin.kind === "standard"
    ? "repertoire:standard"
    : `repertoire:${session.origin.gameUuid}:${session.origin.selectedPly}`;
}

export function branchMove(move: PositionPickerMoveRecord) {
  return {
    color: move.color === "white" ? ("w" as const) : ("b" as const),
    from: move.sourceSquare,
    to: move.targetSquare,
    san: move.san,
    ...(move.promotion ? { promotion: move.promotion } : {}),
  };
}

export function promotionPiece(value: string | undefined): PromotionPiece | undefined {
  return value === "q" || value === "r" || value === "b" || value === "n" ? value : undefined;
}
