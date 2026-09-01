import { Chess, type Square } from "chess.js";

import { STARTING_FEN } from "../board-adapter/BoardAdapter";
import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import { strictFen, type ChessSide, type Ply } from "../viewer/chessPrimitives";
import type { Game, GamePosition } from "../viewer/gameModel";
import type { PromotionPiece } from "../board-adapter/PromotionPicker";

export type PositionPickerOrigin =
  | {
      kind: "standard";
      selectedPly: 0;
      bottomColor: "white";
      prefix: readonly [GamePosition];
    }
  | {
      kind: "stored";
      gameUuid: string;
      selectedPly: Ply;
      subjectColor: ChessSide;
      bottomColor: ChessSide;
      prefix: readonly GamePosition[];
    };

export type PositionPickerSession = {
  origin: PositionPickerOrigin;
  prefix: readonly GamePosition[];
  localContinuation: readonly GamePosition[];
  localMoves: readonly PositionPickerMoveRecord[];
  currentPosition: GamePosition;
  currentPly: Ply;
  localCursor: number;
  bottomColor: ChessSide;
  orientation: BoardOrientation;
  stagedMove: PositionPickerMoveRecord | null;
};

export type PositionPickerMove = {
  sourceSquare: Square;
  targetSquare: Square;
  promotion?: PromotionPiece;
};

export type PositionPickerMoveRecord = PositionPickerMove & {
  color: ChessSide;
  san: string;
  position: GamePosition;
};

export type PositionPickerTransition = {
  move: PositionPickerMoveRecord;
  sourcePosition: GamePosition;
};

export type PositionPickerMoveResult =
  | {
      disposition: "staged";
      move: PositionPickerMoveRecord;
      session: PositionPickerSession;
    }
  | {
      disposition: "advanced";
      move: PositionPickerMoveRecord;
      session: PositionPickerSession;
    };

export type PositionPickerNavigation = "previous" | "next" | "home" | "end";

const STANDARD_START_POSITION: GamePosition = {
  ply: 0,
  fen: STARTING_FEN,
  san: null,
};

export function createStandardStartSession(): PositionPickerSession {
  const prefix = [STANDARD_START_POSITION] as const;

  return {
    origin: {
      kind: "standard",
      selectedPly: 0,
      bottomColor: "white",
      prefix,
    },
    prefix,
    localContinuation: [],
    localMoves: [],
    currentPosition: STANDARD_START_POSITION,
    currentPly: 0,
    localCursor: 0,
    bottomColor: "white",
    orientation: "white",
    stagedMove: null,
  };
}

export function createStoredGameSession(game: Game): PositionPickerSession {
  const selectedPly = game.initial_ply;
  const currentPosition = game.positions.find((position) => position.ply === selectedPly);
  const prefix = game.positions.slice(0, selectedPly + 1);

  if (
    currentPosition === undefined ||
    prefix.length !== selectedPly + 1 ||
    prefix.at(-1)?.ply !== selectedPly
  ) {
    throw new Error("Stored game does not contain a complete prefix through its selected Ply.");
  }

  return {
    origin: {
      kind: "stored",
      gameUuid: game.game_uuid,
      selectedPly,
      subjectColor: game.subject_color,
      bottomColor: game.subject_color,
      prefix,
    },
    prefix,
    localContinuation: [],
    localMoves: [],
    currentPosition,
    currentPly: selectedPly,
    localCursor: 0,
    bottomColor: game.subject_color,
    orientation: game.subject_color,
    stagedMove: null,
  };
}

function sideFromColor(color: "w" | "b"): ChessSide {
  return color === "w" ? "white" : "black";
}

function positionAfterMove(
  session: PositionPickerSession,
  move: PositionPickerMove,
): PositionPickerMoveRecord | null {
  const chess = new Chess(session.currentPosition.fen);
  try {
    const chessMove = chess.move({
      from: move.sourceSquare,
      to: move.targetSquare,
      ...(move.promotion ? { promotion: move.promotion } : {}),
    });
    return {
      ...move,
      color: sideFromColor(chessMove.color),
      san: chessMove.san,
      position: {
        ply: session.currentPly + 1,
        fen: strictFen(chess),
        san: chessMove.san,
      },
    };
  } catch {
    return null;
  }
}

function appendMove(
  session: PositionPickerSession,
  move: PositionPickerMoveRecord,
): PositionPickerSession {
  const localContinuation = [
    ...session.localContinuation.slice(0, session.localCursor),
    move.position,
  ];
  const localMoves = [...session.localMoves.slice(0, session.localCursor), move];
  return {
    ...session,
    localContinuation,
    localMoves,
    currentPosition: move.position,
    currentPly: move.position.ply,
    localCursor: localContinuation.length,
    stagedMove: null,
  };
}

export function selectPositionPickerMove(
  session: PositionPickerSession,
  move: PositionPickerMove,
): PositionPickerMoveResult | null {
  const moveRecord = positionAfterMove(session, move);
  if (!moveRecord) {
    return null;
  }

  if (moveRecord.color === session.bottomColor) {
    return {
      disposition: "staged",
      move: moveRecord,
      session: { ...session, stagedMove: moveRecord },
    };
  }

  return {
    disposition: "advanced",
    move: moveRecord,
    session: appendMove(session, moveRecord),
  };
}

/**
 * Commits any pending staged owner move into the local continuation so the next
 * move is evaluated from the displayed (post-staged) position rather than the
 * pre-staged current position. When no move is staged the session is unchanged.
 */
export function commitStagedMove(
  session: PositionPickerSession,
): PositionPickerSession {
  if (session.stagedMove === null) {
    return session;
  }
  return appendMove({ ...session, stagedMove: null }, session.stagedMove);
}

/**
 * Selects a move with staged-move-aware fallback so an already staged owner
 * preview is not lost when the next interaction is a different owner move.
 *
 * - With no staged move the behavior matches selectPositionPickerMove.
 * - With a staged owner move, the candidate is first tried against the current
 *   (pre-staged) position. A legal same-color move replaces the staged preview
 *   instead of committing the earlier stage.
 * - If the candidate is illegal as a same-color replacement but legal after the
 *   staged move is committed (an opponent reply), the staged move is committed
 *   and the reply is appended.
 */
export function applyPositionPickerMove(
  session: PositionPickerSession,
  move: PositionPickerMove,
): PositionPickerMoveResult | null {
  if (session.stagedMove === null) {
    return selectPositionPickerMove(session, move);
  }

  const sameColorReplacement = selectPositionPickerMove(session, move);
  if (sameColorReplacement !== null) {
    return sameColorReplacement;
  }

  return selectPositionPickerMove(commitStagedMove(session), move);
}

/** Plays a saved owner move as a child preview without committing it to history. */
export function playAndStagePositionPickerMove(
  session: PositionPickerSession,
  move: PositionPickerMove,
): Extract<PositionPickerMoveResult, { disposition: "staged" }> | null {
  const result = selectPositionPickerMove(session, move);
  return result?.disposition === "staged" ? result : null;
}

/** Returns the one represented line: the complete stored prefix then local continuation. */
export function positionPickerHistory(session: PositionPickerSession): readonly GamePosition[] {
  return [...session.prefix, ...session.localContinuation];
}

export function positionPickerHistoryBounds(session: PositionPickerSession): {
  firstPly: Ply;
  lastPly: Ply;
} {
  const history = positionPickerHistory(session);
  return {
    firstPly: history[0]!.ply,
    lastPly: history.at(-1)!.ply,
  };
}

/** Returns the staged preview or the committed local move at the displayed position. */
export function positionPickerSelectedTransition(
  session: PositionPickerSession,
): PositionPickerTransition | null {
  if (session.stagedMove !== null) {
    return {
      move: session.stagedMove,
      sourcePosition: session.currentPosition,
    };
  }

  const localIndex = session.localCursor - 1;
  const move = session.localMoves[localIndex];
  if (
    localIndex < 0 ||
    move === undefined ||
    move.position.ply !== session.currentPosition.ply ||
    move.position.fen !== session.currentPosition.fen
  ) {
    return null;
  }

  const sourcePosition =
    localIndex === 0
      ? session.prefix.find((position) => position.ply === move.position.ply - 1)
      : session.localContinuation[localIndex - 1];
  return sourcePosition === undefined ? null : { move, sourcePosition };
}

/** Selects a represented position without changing the stored or local line. */
export function selectPositionPickerPly(
  session: PositionPickerSession,
  ply: Ply,
): PositionPickerSession | null {
  const currentPosition = positionPickerHistory(session).find((position) => position.ply === ply);
  if (!currentPosition) {
    return null;
  }

  const localIndex = session.localContinuation.findIndex((position) => position.ply === ply);
  return {
    ...session,
    currentPosition,
    currentPly: currentPosition.ply,
    localCursor: localIndex < 0 ? 0 : localIndex + 1,
    stagedMove: null,
  };
}

export function navigatePositionPickerSession(
  session: PositionPickerSession,
  direction: PositionPickerNavigation,
): PositionPickerSession {
  const history = positionPickerHistory(session);
  const currentIndex = Math.max(
    0,
    history.findIndex((position) => position.ply === session.currentPly),
  );
  const targetIndex =
    direction === "previous"
      ? Math.max(0, currentIndex - 1)
      : direction === "next"
        ? Math.min(history.length - 1, currentIndex + 1)
        : direction === "home"
          ? 0
          : history.length - 1;
  return selectPositionPickerPly(session, history[targetIndex]!.ply) ?? session;
}

export function flipPositionPickerSession(session: PositionPickerSession): PositionPickerSession {
  const bottomColor: ChessSide = session.bottomColor === "white" ? "black" : "white";
  return {
    ...session,
    bottomColor,
    orientation: bottomColor,
    stagedMove: null,
  };
}

export function sessionSanHistory(session: PositionPickerSession): string {
  const positions = [
    ...session.prefix,
    ...session.localContinuation.slice(0, session.localCursor),
  ].filter((position) => position.ply > 0 && position.san !== null);

  return positions
    .map((position) => {
      const moveNumber = Math.floor((position.ply + 1) / 2);
      return `${position.ply % 2 === 1 ? `${moveNumber}.` : `${moveNumber}...`} ${position.san}`;
    })
    .join(" ");
}
