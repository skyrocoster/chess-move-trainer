import { fn } from "storybook/test";

import type { Game } from "./gameModel";
import type { GameLookup } from "./positionApi";
import { GAME } from "./gameFixtures";

export function completeGameLookup(game: Game = GAME): GameLookup {
  return fn(async (_uuid, initialPly) => ({
    status: "success" as const,
    game: { ...game, initial_ply: initialPly ?? 0 },
  }));
}
