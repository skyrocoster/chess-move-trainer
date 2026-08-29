import type { Game } from "./gameModel";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";

export const PROMOTION_GAME: Game = {
  game_uuid: VIEWER_GAME_UUID,
  initial_ply: 0,
  subject_color: "white",
  source_url: "https://www.chess.com/game/live/140399891142",
  positions: [
    {
      ply: 0,
      fen: "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
      san: null,
    },
  ],
};

function singlePositionGame(fen: string): Game {
  return { ...VIEWER_GAME, positions: [{ ply: 0, fen, san: null }] };
}

export const CASTLING_GAME = singlePositionGame("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
export const EN_PASSANT_GAME = singlePositionGame("4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1");
export const TERMINAL_GAME = singlePositionGame("7k/5Q2/p5K1/8/8/8/8/8 b - - 0 1");
