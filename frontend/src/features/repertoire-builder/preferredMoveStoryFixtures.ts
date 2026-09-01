import type { PreferredMoveValue } from "./preferredMoveApi";
import type {
  RepertoirePositionModel,
  RepertoireSavedMoveFact,
  RepertoireStagedMoveFact,
} from "./repertoireWorkflowModel";
import type { PositionPickerMoveRecord } from "./positionPickerSession";

export const PREFERRED_MOVE_SOURCE_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const E4_MOVE: PreferredMoveValue = { san: "e4", uci: "e2e4" };
const D4_MOVE: PreferredMoveValue = { san: "d4", uci: "d2d4" };

const E4_STAGED_MOVE: PositionPickerMoveRecord = {
  sourceSquare: "e2",
  targetSquare: "e4",
  color: "white",
  san: "e4",
  position: {
    ply: 1,
    fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    san: "e4",
  },
};

const D4_STAGED_MOVE: PositionPickerMoveRecord = {
  sourceSquare: "d2",
  targetSquare: "d4",
  color: "white",
  san: "d4",
  position: {
    ply: 1,
    fen: "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1",
    san: "d4",
  },
};

function savedFact(move: PreferredMoveValue): RepertoireSavedMoveFact {
  return {
    move,
    effectiveAt: "2026-01-01T00:00:00.000Z",
    sourceFen: PREFERRED_MOVE_SOURCE_FEN,
  };
}

function stagedFact(move: PositionPickerMoveRecord): RepertoireStagedMoveFact {
  return {
    move,
    uci: `${move.sourceSquare}${move.targetSquare}${move.promotion ?? ""}`,
  };
}

export type PreferredMoveRelationship =
  | "empty"
  | "first-choice"
  | "saved"
  | "replacement"
  | "matching";

export type PreferredMoveStoryFixture = {
  relationship: PreferredMoveRelationship;
  savedPresence: "absent" | "present";
  saved: RepertoireSavedMoveFact | null;
  staged: RepertoireStagedMoveFact | null;
  comparison: "not-applicable" | "different" | "matching";
};

export const preferredMoveRelationshipFixtures: Record<
  PreferredMoveRelationship,
  PreferredMoveStoryFixture
> = {
  empty: {
    relationship: "empty",
    savedPresence: "absent",
    saved: null,
    staged: null,
    comparison: "not-applicable",
  },
  "first-choice": {
    relationship: "first-choice",
    savedPresence: "absent",
    saved: null,
    staged: stagedFact(E4_STAGED_MOVE),
    comparison: "not-applicable",
  },
  saved: {
    relationship: "saved",
    savedPresence: "present",
    saved: savedFact(E4_MOVE),
    staged: null,
    comparison: "not-applicable",
  },
  replacement: {
    relationship: "replacement",
    savedPresence: "present",
    saved: savedFact(E4_MOVE),
    staged: stagedFact(D4_STAGED_MOVE),
    comparison: "different",
  },
  matching: {
    relationship: "matching",
    savedPresence: "present",
    saved: savedFact(E4_MOVE),
    staged: stagedFact(E4_STAGED_MOVE),
    comparison: "matching",
  },
};

export function preferredMoveStoryModel(
  relationship: PreferredMoveRelationship,
  overrides: Partial<RepertoirePositionModel> = {},
): RepertoirePositionModel {
  const fixture = preferredMoveRelationshipFixtures[relationship];
  return {
    sourceFen: PREFERRED_MOVE_SOURCE_FEN,
    bottomColor: "white",
    ownTurn: true,
    personalCount: 3,
    contextMessage: "Seen in 3 games as White",
    saveability: "savable",
    ...fixture,
    ...overrides,
  };
}

export const preferredMoveStoryValues = {
  e4: E4_MOVE,
  d4: D4_MOVE,
};
