import type {
  MoveHistoryBounds,
  MoveHistoryControlledState,
  MoveHistoryEntry,
  MoveHistoryInitialPosition,
  MoveHistoryInput,
  MoveHistoryNavigation,
  MoveHistoryMove,
  Ply,
} from "./moveHistoryTypes";

export interface MoveHistoryModel {
  readonly entries: readonly MoveHistoryEntry[];
  readonly bounds: MoveHistoryBounds;
}

/**
 * Creates the one ordered line represented by the initial position followed by
 * its SAN moves. The supplied move order is preserved and no branch data is
 * introduced.
 */
export function createMoveHistoryModel({
  initialPosition,
  moves,
}: MoveHistoryInput): MoveHistoryModel {
  const entries: MoveHistoryEntry[] = [
    { kind: "initial", ...initialPosition },
    ...moves.map((move: MoveHistoryMove) => ({ kind: "move" as const, ...move })),
  ];

  return {
    entries,
    bounds: {
      firstPly: initialPosition.ply,
      lastPly: entries.at(-1)!.ply,
    },
  };
}

export function findMoveHistoryEntry(
  model: MoveHistoryModel,
  ply: Ply,
): MoveHistoryEntry | undefined {
  return model.entries.find((entry) => entry.ply === ply);
}

export function clampMoveHistoryPly(model: MoveHistoryModel, ply: Ply): Ply {
  return Math.min(Math.max(ply, model.bounds.firstPly), model.bounds.lastPly);
}

/**
 * Resolves linear navigation without changing controlled state. Previous and
 * next stop at the bounds; Home and End select the first and last Ply.
 */
export function navigateMoveHistory(
  model: MoveHistoryModel,
  activePly: Ply,
  navigation: MoveHistoryNavigation,
): Ply {
  const boundedPly = clampMoveHistoryPly(model, activePly);

  switch (navigation) {
    case "previous":
      return Math.max(model.bounds.firstPly, boundedPly - 1);
    case "next":
      return Math.min(model.bounds.lastPly, boundedPly + 1);
    case "home":
      return model.bounds.firstPly;
    case "end":
      return model.bounds.lastPly;
  }
}

export type MoveHistoryControlledModel = MoveHistoryModel & MoveHistoryControlledState;

export function moveHistoryEntries(
  initialPosition: MoveHistoryInitialPosition,
  moves: readonly MoveHistoryMove[],
): readonly MoveHistoryEntry[] {
  return createMoveHistoryModel({ initialPosition, moves }).entries;
}
