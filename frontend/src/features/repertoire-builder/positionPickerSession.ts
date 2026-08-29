import { Chess, type Square } from "chess.js";

import { STARTING_FEN } from "../board-adapter/BoardAdapter";
import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import type { ChessSide, Ply } from "../viewer/chessPrimitives";
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

function currentBasePosition(session: PositionPickerSession): GamePosition {
  return session.prefix.at(-1)!;
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
        fen: chess.fen(),
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

export function appendPositionPickerMove(
  session: PositionPickerSession,
  move: PositionPickerMove,
): PositionPickerSession | null {
  const moveRecord = positionAfterMove(session, move);
  return moveRecord ? appendMove(session, moveRecord) : null;
}

export function navigatePositionPickerSession(
  session: PositionPickerSession,
  direction: "previous" | "next",
): PositionPickerSession {
  const delta = direction === "previous" ? -1 : 1;
  const localCursor = Math.max(
    0,
    Math.min(session.localContinuation.length, session.localCursor + delta),
  );
  const currentPosition =
    localCursor === 0 ? currentBasePosition(session) : session.localContinuation[localCursor - 1]!;
  return {
    ...session,
    currentPosition,
    currentPly: currentPosition.ply,
    localCursor,
    stagedMove: null,
  };
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
