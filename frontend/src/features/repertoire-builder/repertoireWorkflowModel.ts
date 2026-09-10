import type { ChessSide } from "../chess/chessPrimitives";
import { sanFromFenAndUci } from "../game/gameModel";
import type { PositionContextResponse } from "../position-context/positionContextApi";
import type { PreferredMoveResponse, PreferredMoveValue } from "./preferredMoveApi";
import type { SelectedTransition } from "./positionPickerSessionBoundary";

export type PositionSaveability = "unknown" | "savable" | "unsavable";

export type RepertoirePositionRelationship =
  | "unknown"
  | "empty"
  | "first-choice"
  | "saved"
  | "replacement"
  | "matching";

export type PreferredMoveComparison = "unknown" | "not-applicable" | "different" | "matching";

export type RepertoireSavedMoveFact = {
  move: PreferredMoveValue;
  effectiveAt: string;
  sourceFen: string;
};

export type RepertoireSelectedMoveFact = {
  transition: SelectedTransition;
  san: string;
  uci: string;
};

export type RepertoirePositionModel = {
  sourceFen: string;
  bottomColor: ChessSide;
  ownTurn: boolean;
  personalCount: number | null;
  contextMessage: string | null;
  saveability: PositionSaveability;
  savedPresence: "unknown" | "absent" | "present";
  saved: RepertoireSavedMoveFact | null;
  selected: RepertoireSelectedMoveFact | null;
  comparison: PreferredMoveComparison;
  relationship: RepertoirePositionRelationship;
};

function colorLabel(color: ChessSide): "White" | "Black" {
  return color === "white" ? "White" : "Black";
}

export function deriveRepertoirePositionModel({
  context,
  preferredMove,
  sideToMove,
  bottomColor,
  sourceFen = preferredMove?.fen ?? "",
  selectedTransition = null,
  preferredMoveKnown = true,
}: {
  context: PositionContextResponse | null;
  preferredMove: PreferredMoveResponse | null;
  sideToMove: ChessSide;
  bottomColor: ChessSide;
  sourceFen?: string;
  selectedTransition?: SelectedTransition | null;
  preferredMoveKnown?: boolean;
}): RepertoirePositionModel {
  const personalCount =
    context === null ? null : context.distinctGameCount;
  const color = colorLabel(context === null ? bottomColor : context.trainerColor);
  const ownTurn = sideToMove === bottomColor;
  const savedPresence = !preferredMoveKnown
    ? "unknown"
    : preferredMove?.state === "assigned"
      ? "present"
      : "absent";
  const savedMove = savedPresence === "present" ? (preferredMove?.move ?? null) : null;
  const selected =
    selectedTransition !== null && ownTurn
      ? {
          transition: selectedTransition,
          san: sanFromFenAndUci(selectedTransition.parentFEN, selectedTransition.outgoingUCI),
          uci: selectedTransition.outgoingUCI,
        }
      : null;
  const saved =
    savedMove !== null && preferredMove !== null
      ? { move: savedMove, effectiveAt: preferredMove.effective_at!, sourceFen }
      : null;
  const comparison: PreferredMoveComparison =
    savedPresence === "unknown"
      ? "unknown"
      : saved === null || selected === null
        ? "not-applicable"
        : selected.uci === saved.move.uci
          ? "matching"
          : "different";
  const relationship: RepertoirePositionRelationship =
    savedPresence === "unknown"
      ? "unknown"
      : saved === null
        ? selected === null
          ? "empty"
          : "first-choice"
        : selected === null
          ? "saved"
          : comparison === "matching"
            ? "matching"
            : "replacement";
  return {
    sourceFen,
    bottomColor,
    ownTurn,
    personalCount,
    contextMessage:
      context === null
        ? null
        : context.observedInGames && context.distinctGameCount > 0
          ? `Seen in ${context.distinctGameCount} games as ${color}`
          : `Never seen as ${color}`,
    saveability:
      context === null ? "unknown" : context.observedInGames ? "savable" : "unsavable",
    savedPresence,
    saved,
    selected,
    comparison,
    relationship,
  };
}
