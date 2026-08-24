import type { ChessSide, Fen, Ply, San } from "./chessPrimitives";

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
