import type { Game } from "./gameModel";
import { GAME_UUID } from "./gameFixtures";

export const PROMOTION_GAME: Game = {
  game_uuid: GAME_UUID,
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
