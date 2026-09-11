import { Chess, type PieceSymbol, type Square } from "chess.js";

import type { GameDetailResponse } from "../../api/client";
import type { ChessSide, Fen, Ply, San } from "../chess/chessPrimitives";

export type GameMainLineOccurrence = {
  readonly ply: Ply;
  readonly fen: Fen;
  readonly outgoingUci: string | null;
  readonly san: San;
};

export type GameMainLineModel = {
  readonly gameUuid: string;
  readonly initialFen: Fen;
  readonly trainerOrientation: ChessSide;
  readonly occurrences: readonly GameMainLineOccurrence[];
};

const UCI_PATTERN = /^([a-h][1-8])([a-h][1-8])([qrbn])?$/;

export function sanFromFenAndUci(fen: Fen, uci: string): string {
  const match = UCI_PATTERN.exec(uci);
  if (match === null) {
    throw new Error(`Invalid UCI move: ${uci}`);
  }

  const from = match[1] as Square;
  const to = match[2] as Square;
  const promotion = match[3];
  const move =
    promotion === undefined ? { from, to } : { from, to, promotion: promotion as PieceSymbol };

  return new Chess(fen).move(move).san;
}

export function mapGameDetailResponse(response: GameDetailResponse): GameMainLineModel {
  const occurrences = [...response.occurrences]
    .sort((left, right) => left.ply - right.ply)
    .map(({ ply, fen, move_uci }) => ({
      ply,
      fen,
      outgoingUci: move_uci,
      san: move_uci === null ? null : sanFromFenAndUci(fen, move_uci),
    }));
  const initialOccurrence = occurrences.find((occurrence) => occurrence.ply === 0);

  if (initialOccurrence === undefined) {
    throw new Error("Game detail does not contain a Ply 0 occurrence.");
  }

  return {
    gameUuid: response.game_uuid,
    initialFen: initialOccurrence.fen,
    trainerOrientation: response.trainer_color,
    occurrences,
  };
}

export type GamePosition = {
  ply: Ply;
  fen: Fen;
  san: San;
};

export type Game = {
  game_uuid: string;
  initial_ply: Ply;
  subject_color: ChessSide;
  source_url: string | null;
  positions: readonly GamePosition[];
};

export type GameFailureKind =
  | "game_not_found"
  | "position_not_found"
  | "corpus_unavailable"
  | "game_unavailable"
  | "unexpected_failure";

export const GAME_FAILURE_COPY: Record<GameFailureKind, { heading: string; message: string }> = {
  game_not_found: {
    heading: "Game not found",
    message: "No stored game matches this Game UUID.",
  },
  position_not_found: {
    heading: "Position not found",
    message: "No stored position matches this game and Ply.",
  },
  corpus_unavailable: {
    heading: "Corpus unavailable",
    message: "The stored game data service is unavailable or incompatible.",
  },
  game_unavailable: {
    heading: "Game unavailable",
    message: "The stored game could not be displayed because its data is invalid.",
  },
  unexpected_failure: {
    heading: "Unable to load game",
    message: "The game could not be loaded due to an unexpected error.",
  },
};
