import type { ChessSide } from "../viewer/chessPrimitives";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import type { PreferredMoveResponse, PreferredMoveValue } from "./preferredMoveApi";
import type { PositionPickerMoveRecord } from "./positionPickerSession";

export type PositionSaveability = "unknown" | "savable" | "unsavable";

export type RepertoirePositionModel = {
  bottomColor: ChessSide;
  personalCount: number | null;
  contextMessage: string | null;
  saveability: PositionSaveability;
  savedMove: PreferredMoveValue | null;
  savedMoveVisible: boolean;
};

export type PreferredMoveDraftMode = "add" | "edit";

export type PreferredMoveDraftState = {
  mode: "idle" | PreferredMoveDraftMode;
  stagedMove: PositionPickerMoveRecord | null;
};

function colorLabel(color: ChessSide): "White" | "Black" {
  return color === "white" ? "White" : "Black";
}

export function deriveRepertoirePositionModel({
  context,
  preferredMove,
  sideToMove,
  bottomColor,
}: {
  context: PositionContextResponse | null;
  preferredMove: PreferredMoveResponse | null;
  sideToMove: ChessSide;
  bottomColor: ChessSide;
}): RepertoirePositionModel {
  const personalCount =
    context === null ? null : bottomColor === "white" ? context.white_count : context.black_count;
  const color = colorLabel(bottomColor);
  const ownTurn = sideToMove === bottomColor;
  const savedMove = ownTurn && preferredMove?.state === "assigned" ? preferredMove.move : null;

  return {
    bottomColor,
    personalCount,
    contextMessage:
      context === null
        ? null
        : context.overall_exists && personalCount !== null && personalCount > 0
          ? `Seen in ${personalCount} games as ${color}`
          : `Never seen as ${color}`,
    saveability: context === null ? "unknown" : context.overall_exists ? "savable" : "unsavable",
    savedMove,
    savedMoveVisible: savedMove !== null,
  };
}

export function emptyPreferredMoveDraft(): PreferredMoveDraftState {
  return { mode: "idle", stagedMove: null };
}

export function beginPreferredMoveDraft(mode: PreferredMoveDraftMode): PreferredMoveDraftState {
  return { mode, stagedMove: null };
}

export function stagePreferredMoveDraft(
  draft: PreferredMoveDraftState,
  move: PositionPickerMoveRecord,
  bottomColor: ChessSide,
): PreferredMoveDraftState | null {
  if (draft.mode === "idle" || move.color !== bottomColor) {
    return null;
  }
  return { ...draft, stagedMove: move };
}

export function cancelPreferredMoveDraft(): PreferredMoveDraftState {
  return emptyPreferredMoveDraft();
}
