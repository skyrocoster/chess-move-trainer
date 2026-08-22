export type Stage1SubjectColor = "white" | "black";

export type Stage1Position = {
  ply: number;
  fen: string;
  san: string | null;
};

export type Stage1Game = {
  game_uuid: string;
  initial_ply: number;
  subject_color: Stage1SubjectColor;
  source_url: string | null;
  positions: readonly Stage1Position[];
};

export const STAGE1_GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";

export const STAGE1_GAME: Stage1Game = {
  game_uuid: STAGE1_GAME_UUID,
  initial_ply: 0,
  subject_color: "white",
  source_url: "https://www.chess.com/game/live/140399891142",
  positions: [
    {
      ply: 0,
      fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
      san: null,
    },
    {
      ply: 1,
      fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
      san: "e4",
    },
    {
      ply: 2,
      fen: "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
      san: "e5",
    },
    {
      ply: 3,
      fen: "rnbqkbnr/pppp1ppp/8/4p3/5N2/8/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
      san: "Nf3",
    },
  ],
};

export const STAGE1_UNSAFE_SOURCE_GAME: Stage1Game = {
  ...STAGE1_GAME,
  source_url: "https://example.com/game/live/unsafe",
};

export const STAGE1_MISSING_SOURCE_GAME: Stage1Game = {
  ...STAGE1_GAME,
  source_url: null,
};

export type Stage1FailureKind =
  | "game_not_found"
  | "position_not_found"
  | "corpus_unavailable"
  | "game_unavailable"
  | "unexpected_failure";

export const STAGE1_FAILURE_COPY: Record<Stage1FailureKind, { heading: string; message: string }> =
  {
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
