import type { Game } from "./gameModel";

export const VIEWER_GAME_UUID = "0007925c-5a8d-11f0-9740-f690a301000f";

export const VIEWER_GAME: Game = {
  game_uuid: VIEWER_GAME_UUID,
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

export const UNSAFE_SOURCE_GAME: Game = {
  ...VIEWER_GAME,
  source_url: "https://example.com/game/live/unsafe",
};

export const MISSING_SOURCE_GAME: Game = {
  ...VIEWER_GAME,
  source_url: null,
};
