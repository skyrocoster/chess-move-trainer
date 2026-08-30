/** A half-move index owned by the shared Move History feature. */
export type Ply = number;

/** Standard Algebraic Notation for one move. */
export type San = string;

export interface MoveHistoryInitialPosition {
  readonly ply: Ply;
}

export interface MoveHistoryMove {
  readonly ply: Ply;
  readonly san: San;
}

export interface MoveHistoryInput {
  readonly initialPosition: MoveHistoryInitialPosition;
  readonly moves: readonly MoveHistoryMove[];
}

export type MoveHistoryEntry =
  | ({ readonly kind: "initial" } & MoveHistoryInitialPosition)
  | ({ readonly kind: "move" } & MoveHistoryMove);

export interface MoveHistoryBounds {
  readonly firstPly: Ply;
  readonly lastPly: Ply;
}

export type MoveHistoryNavigation = "previous" | "next" | "home" | "end";

/** Controlled consumers receive the selected Ply; the history owns no route state. */
export type MoveHistoryActivePlyChange = (ply: Ply) => void;

export interface MoveHistoryControlledState {
  readonly activePly: Ply;
  readonly onActivePlyChange: MoveHistoryActivePlyChange;
}
