import type { ChessSide, Fen, Ply, San } from "../chess/chessPrimitives";
import type { GameMainLineModel } from "../game/gameModel";

export type SessionPosition = {
  readonly ply: Ply;
  readonly fen: Fen;
  readonly san: San;
};

export type SelectedTransition = {
  readonly parentFEN: Fen;
  readonly outgoingUCI: string;
};

export type SessionMove = {
  readonly outgoingUCI: string;
  readonly resultingFEN: Fen;
  readonly san: string;
};

export type TemporaryBranch = {
  readonly branchPointIndex: number;
  readonly positions: readonly SessionPosition[];
  readonly transitions: readonly SelectedTransition[];
};

export type PositionPickerSessionBoundary = {
  readonly kind: "fresh" | "imported";
  readonly mainLine: GameMainLineModel | null;
  readonly currentIndex: number;
  readonly currentPosition: SessionPosition;
  readonly selectedTransition: SelectedTransition | null;
  readonly branch: TemporaryBranch | null;
};

export type SessionNavigation = "previous" | "next" | "home" | "end";

export const STANDARD_START_FEN: Fen =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const STANDARD_START_POSITION: SessionPosition = {
  ply: 0,
  fen: STANDARD_START_FEN,
  san: null,
};

function importedPositions(mainLine: GameMainLineModel): readonly SessionPosition[] {
  return mainLine.occurrences.map((occurrence, index) => ({
    ply: occurrence.ply,
    fen: occurrence.fen,
    san: index === 0 ? null : mainLine.occurrences[index - 1]!.san,
  }));
}

function mainLinePositions(session: PositionPickerSessionBoundary): readonly SessionPosition[] {
  return session.mainLine === null ? [STANDARD_START_POSITION] : importedPositions(session.mainLine);
}

export function sessionHistory(
  session: PositionPickerSessionBoundary,
): readonly SessionPosition[] {
  const positions = mainLinePositions(session);
  if (session.branch === null) {
    return positions;
  }

  return [
    ...positions.slice(0, session.branch.branchPointIndex + 1),
    ...session.branch.positions,
  ];
}

function selectedTransitionAt(
  session: PositionPickerSessionBoundary,
  index: number,
): SelectedTransition | null {
  if (index === 0) {
    return null;
  }

  if (session.branch !== null && index > session.branch.branchPointIndex) {
    return session.branch.transitions[index - session.branch.branchPointIndex - 1] ?? null;
  }

  const previousOccurrence = session.mainLine?.occurrences[index - 1];
  return previousOccurrence?.outgoingUci === null || previousOccurrence?.outgoingUci === undefined
    ? null
    : {
        parentFEN: previousOccurrence.fen,
        outgoingUCI: previousOccurrence.outgoingUci,
      };
}

function atIndex(
  session: PositionPickerSessionBoundary,
  index: number,
): PositionPickerSessionBoundary {
  const history = sessionHistory(session);
  const currentPosition = history[index];
  if (currentPosition === undefined) {
    throw new Error(`Session history index is out of bounds: ${index}`);
  }

  return {
    ...session,
    currentIndex: index,
    currentPosition,
    selectedTransition: selectedTransitionAt(session, index),
  };
}

function createSession(
  kind: PositionPickerSessionBoundary["kind"],
  mainLine: GameMainLineModel | null,
): PositionPickerSessionBoundary {
  const session: PositionPickerSessionBoundary = {
    kind,
    mainLine,
    currentIndex: 0,
    currentPosition: mainLine === null ? STANDARD_START_POSITION : importedPositions(mainLine)[0]!,
    selectedTransition: null,
    branch: null,
  };
  return session;
}

export function createFreshSession(): PositionPickerSessionBoundary {
  return createSession("fresh", null);
}

export function loadImportedSession(
  mainLine: GameMainLineModel,
): PositionPickerSessionBoundary {
  if (mainLine.occurrences.length === 0 || mainLine.occurrences[0]?.ply !== 0) {
    throw new Error("Imported main line must begin with a Ply 0 occurrence.");
  }

  return createSession("imported", mainLine);
}

export function resetSession(): PositionPickerSessionBoundary {
  return createFreshSession();
}

export function selectSessionPly(
  session: PositionPickerSessionBoundary,
  ply: Ply,
): PositionPickerSessionBoundary | null {
  const index = sessionHistory(session).findIndex((position) => position.ply === ply);
  return index < 0 ? null : atIndex(session, index);
}

export function navigateSession(
  session: PositionPickerSessionBoundary,
  direction: SessionNavigation,
): PositionPickerSessionBoundary {
  const lastIndex = sessionHistory(session).length - 1;
  const targetIndex =
    direction === "previous"
      ? Math.max(0, session.currentIndex - 1)
      : direction === "next"
        ? Math.min(lastIndex, session.currentIndex + 1)
        : direction === "home"
          ? 0
          : lastIndex;

  return atIndex(session, targetIndex);
}

function branchWithMove(
  session: PositionPickerSessionBoundary,
  move: SessionMove,
): PositionPickerSessionBoundary {
  const existingBranch = session.branch;
  const branchPointIndex =
    existingBranch !== null && session.currentIndex >= existingBranch.branchPointIndex
      ? existingBranch.branchPointIndex
      : session.currentIndex;
  const branchCursor =
    existingBranch !== null && session.currentIndex >= branchPointIndex
      ? session.currentIndex - branchPointIndex
      : 0;
  const transition: SelectedTransition = {
    parentFEN: session.currentPosition.fen,
    outgoingUCI: move.outgoingUCI,
  };
  const position: SessionPosition = {
    ply: session.currentPosition.ply + 1,
    fen: move.resultingFEN,
    san: move.san,
  };
  const branch: TemporaryBranch = {
    branchPointIndex,
    positions: [
      ...(existingBranch?.branchPointIndex === branchPointIndex
        ? existingBranch.positions.slice(0, branchCursor)
        : []),
      position,
    ],
    transitions: [
      ...(existingBranch?.branchPointIndex === branchPointIndex
        ? existingBranch.transitions.slice(0, branchCursor)
        : []),
      transition,
    ],
  };

  const nextSession = { ...session, branch };
  return atIndex(nextSession, branchPointIndex + branch.positions.length);
}

export function applySessionMove(
  session: PositionPickerSessionBoundary,
  move: SessionMove,
): PositionPickerSessionBoundary {
  const mainPositions = mainLinePositions(session);
  const branchPointIndex = session.branch?.branchPointIndex;
  const isOnImportedPrefix = branchPointIndex === undefined || session.currentIndex <= branchPointIndex;
  const expectedMainUCI =
    session.mainLine !== null && session.currentIndex < mainPositions.length - 1
      ? session.mainLine.occurrences[session.currentIndex]?.outgoingUci
      : undefined;

  if (session.mainLine !== null && isOnImportedPrefix && move.outgoingUCI === expectedMainUCI) {
    if (session.branch !== null && session.currentIndex === branchPointIndex) {
      return atIndex({ ...session, branch: null }, session.currentIndex + 1);
    }
    return atIndex(session, session.currentIndex + 1);
  }

  if (session.branch !== null && session.currentIndex > session.branch.branchPointIndex) {
    const branchCursor = session.currentIndex - session.branch.branchPointIndex;
    const expectedBranchUCI = session.branch.transitions[branchCursor]?.outgoingUCI;
    if (move.outgoingUCI === expectedBranchUCI) {
      return atIndex(session, session.currentIndex + 1);
    }
  }

  return branchWithMove(session, move);
}

export function returnToGame(
  session: PositionPickerSessionBoundary,
): PositionPickerSessionBoundary {
  if (session.branch === null) {
    return session;
  }

  const branchPointIndex = session.branch.branchPointIndex;
  return atIndex({ ...session, branch: null }, branchPointIndex);
}

export function sessionHistoryBounds(session: PositionPickerSessionBoundary): {
  firstPly: Ply;
  lastPly: Ply;
} {
  const history = sessionHistory(session);
  return {
    firstPly: history[0]!.ply,
    lastPly: history.at(-1)!.ply,
  };
}

export function sessionOrientation(
  session: PositionPickerSessionBoundary,
): ChessSide {
  return session.mainLine?.trainerOrientation ?? "white";
}
