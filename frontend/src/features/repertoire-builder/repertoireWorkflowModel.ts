import type { ChessSide } from "../viewer/chessPrimitives";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import type { PreferredMoveResponse, PreferredMoveValue } from "./preferredMoveApi";
import type { PositionPickerMoveRecord } from "./positionPickerSession";

export type PositionSaveability = "unknown" | "savable" | "unsavable";

export type RepertoirePositionState =
  | "no-saved"
  | "saved"
  | "matching-played"
  | "unsaved-played";

export type RepertoirePositionModel = {
  bottomColor: ChessSide;
  personalCount: number | null;
  contextMessage: string | null;
  saveability: PositionSaveability;
  state: RepertoirePositionState;
  savedMove: PreferredMoveValue | null;
  savedMoveVisible: boolean;
  effectiveAt: string | null;
  lastPlayedMove: PositionPickerMoveRecord | null;
  lastPlayedPreferredMove: PreferredMoveResponse | null;
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
  lastPlayedMove = null,
  lastPlayedPreferredMove = null,
}: {
  context: PositionContextResponse | null;
  preferredMove: PreferredMoveResponse | null;
  sideToMove: ChessSide;
  bottomColor: ChessSide;
  lastPlayedMove?: PositionPickerMoveRecord | null;
  lastPlayedPreferredMove?: PreferredMoveResponse | null;
}): RepertoirePositionModel {
  const personalCount =
    context === null ? null : bottomColor === "white" ? context.white_count : context.black_count;
  const color = colorLabel(bottomColor);
  const ownTurn = sideToMove === bottomColor;
  const savedMove = ownTurn && preferredMove?.state === "assigned" ? preferredMove.move : null;
  const hasLastPlayedFocus = lastPlayedMove?.color === bottomColor;
  const lastPlayedMatches =
    hasLastPlayedFocus &&
    lastPlayedPreferredMove?.state === "assigned" &&
    lastPlayedPreferredMove.move !== null &&
    moveUci(lastPlayedMove) === lastPlayedPreferredMove.move.uci;
  const state: RepertoirePositionState = hasLastPlayedFocus
    ? lastPlayedMatches
      ? "matching-played"
      : "unsaved-played"
    : savedMove === null
      ? "no-saved"
      : "saved";
  const effectiveAtSource = hasLastPlayedFocus ? lastPlayedPreferredMove : preferredMove;
  const effectiveAt =
    effectiveAtSource?.state === "assigned" ? effectiveAtSource.effective_at : null;

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
    state,
    savedMove,
    savedMoveVisible: savedMove !== null,
    effectiveAt,
    lastPlayedMove,
    lastPlayedPreferredMove,
  };
}

function moveUci(move: PositionPickerMoveRecord | null | undefined): string | null {
  return move === null || move === undefined
    ? null
    : `${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""}`;
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
