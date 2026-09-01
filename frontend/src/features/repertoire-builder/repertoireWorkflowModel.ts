import type { ChessSide } from "../viewer/chessPrimitives";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import type { PreferredMoveResponse, PreferredMoveValue } from "./preferredMoveApi";
import type { PositionPickerMoveRecord } from "./positionPickerSession";

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

export type RepertoireStagedMoveFact = {
  move: PositionPickerMoveRecord;
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
  staged: RepertoireStagedMoveFact | null;
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
  stagedMove = null,
  preferredMoveKnown = true,
}: {
  context: PositionContextResponse | null;
  preferredMove: PreferredMoveResponse | null;
  sideToMove: ChessSide;
  bottomColor: ChessSide;
  sourceFen?: string;
  stagedMove?: PositionPickerMoveRecord | null;
  preferredMoveKnown?: boolean;
}): RepertoirePositionModel {
  const personalCount =
    context === null ? null : bottomColor === "white" ? context.white_count : context.black_count;
  const color = colorLabel(bottomColor);
  const ownTurn = sideToMove === bottomColor;
  const savedPresence = !preferredMoveKnown
    ? "unknown"
    : preferredMove?.state === "assigned"
      ? "present"
      : "absent";
  const savedMove = savedPresence === "present" ? (preferredMove?.move ?? null) : null;
  const stagedFact =
    stagedMove !== null && stagedMove.color === bottomColor
      ? { move: stagedMove, uci: canonicalMoveUci(stagedMove)! }
      : null;
  const saved =
    savedMove !== null && preferredMove !== null
      ? { move: savedMove, effectiveAt: preferredMove.effective_at!, sourceFen }
      : null;
  const comparison: PreferredMoveComparison =
    savedPresence === "unknown"
      ? "unknown"
      : saved === null || stagedFact === null
        ? "not-applicable"
        : stagedFact.uci === saved.move.uci
          ? "matching"
          : "different";
  const relationship: RepertoirePositionRelationship =
    savedPresence === "unknown"
      ? "unknown"
      : saved === null
        ? stagedFact === null
          ? "empty"
          : "first-choice"
        : stagedFact === null
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
        : context.overall_exists && personalCount !== null && personalCount > 0
          ? `Seen in ${personalCount} games as ${color}`
          : `Never seen as ${color}`,
    saveability: context === null ? "unknown" : context.overall_exists ? "savable" : "unsavable",
    savedPresence,
    saved,
    staged: stagedFact,
    comparison,
    relationship,
  };
}

export function canonicalMoveUci(move: PositionPickerMoveRecord | null | undefined): string | null {
  return move === null || move === undefined
    ? null
    : `${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""}`;
}
