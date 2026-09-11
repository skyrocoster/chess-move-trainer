import { fireEvent, render, screen, within } from "@testing-library/react";
import { Chess, type Square } from "chess.js";
import type { ComponentProps } from "react";
import { vi } from "vitest";

import type {
  AnalysisClient,
  AnalysisObservation,
  AnalysisOperationResult,
} from "../analysis/analysisApi";
import type { GameDetailResponse } from "../../api/client";
import type { PositionContextClient } from "../position-context/positionContextApi";
import { GAME, GAME_UUID } from "../game/gameFixtures";
import type {
  MoveResponseDistributionClient,
  MoveResponseDistributionResponse,
} from "../move-response-distribution/moveResponseDistributionApi";
import type {
  PreferredMoveClient,
  PreferredMoveMutationResult,
  PreferredMoveResponse,
} from "./preferredMoveApi";
import RepertoireBuilderWorkspace, { type GameDetailClient } from "./RepertoireBuilderWorkspace";

export { GAME_UUID } from "../game/gameFixtures";

export const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
export const STORED_BOARD_LABEL = `Chess board: game ${GAME_UUID}, ply 2, Black at the bottom`;
export const STARTING_FEN = GAME.positions[0].fen;
export const AFTER_E4_FEN = GAME.positions[1].fen;
export const AFTER_E5_FEN = GAME.positions[2].fen;
export const AFTER_D4_FEN = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1";
export const AFTER_E8_KNIGHT_FEN = "k3N3/8/8/8/8/8/8/4K3 b - - 0 1";
export const AFTER_NF3_FEN = "rnbqkbnr/pppp1ppp/8/4p3/5N2/8/PPPP1PPP/RNBQKB1R b KQkq - 1 2";

export const GAME_DETAIL: GameDetailResponse = {
  ended_at_utc: null,
  game_uuid: GAME_UUID,
  occurrences: [
    { ply: 0, fen: STARTING_FEN, move_uci: "e2e4" },
    { ply: 1, fen: AFTER_E4_FEN, move_uci: "e7e5" },
    { ply: 2, fen: AFTER_E5_FEN, move_uci: "g1f3" },
    { ply: 3, fen: AFTER_NF3_FEN, move_uci: null },
  ],
  opponent_chesscom_uuid: null,
  opponent_rating: null,
  original_pgn: "1. e4 e5 2. Nf3",
  source_url: "https://www.chess.com/game/live/140399891142",
  started_at_utc: null,
  termination_reason: null,
  time_class: "blitz",
  time_control: "300+0",
  trainer_chesscom_uuid: "trainer-id",
  trainer_color: "white",
  trainer_outcome: null,
  trainer_rating: null,
};
export const CONTEXT = {
  observedInGames: true,
  distinctGameCount: 0,
  totalGameCount: 10,
} as const;

export function moveResponseDistributionResponse(
  fen: string,
  color: "white" | "black" = "white",
): MoveResponseDistributionResponse {
  return {
    fen,
    color,
    matching_game_count: 10,
    outgoing_occurrence_count: 12,
    replies: [
      { rank: 1, child_uci: "e2e4", san: "e4", occurrence_count: 4 },
      { rank: 2, child_uci: "d2d4", san: "d4", occurrence_count: 3 },
      { rank: 3, child_uci: "c2c4", san: "c4", occurrence_count: 2 },
      { rank: 4, child_uci: "g1f3", san: "Nf3", occurrence_count: 1 },
      { rank: 5, child_uci: "c2c3", san: "c3", occurrence_count: 1 },
      { rank: 6, child_uci: "b2b3", san: "b3", occurrence_count: 1 },
    ],
  };
}
export function noAnalysisClient(): AnalysisClient {
  const observation = (fen: string): AnalysisObservation => ({
    fen,
    state: "not_requested",
    result: null,
  });
  const success = (data: AnalysisObservation): AnalysisOperationResult<AnalysisObservation> => ({
    status: "success",
    data,
  });

  return {
    observe: vi.fn(async (fen: string) => success(observation(fen))),
    request: vi.fn(async (fen: string) => success(observation(fen))),
  };
}

export function preferredMoveResponse(
  fen: string,
  state: PreferredMoveResponse["state"] = "unassigned",
): PreferredMoveResponse {
  return {
    fen,
    state,
    move: state === "assigned" ? { uci: "e2e4", san: "e4" } : null,
    effective_at: state === "assigned" ? "2026-01-01T00:00:00.000000Z" : null,
  };
}

export function mutationResponse(
  fen: string,
  preference: "move" | "no_preference" = "move",
  uci = "e2e4",
): PreferredMoveMutationResult {
  if (preference === "no_preference") {
    return {
      status: "success",
      data: {
        fen,
        effective_from: "2026-01-02",
        effective_until: null,
        periods: [
          {
            effective_from: "2026-01-02",
            effective_until: null,
            preference: { kind: "no_preference" },
          },
        ],
      },
    };
  }
  return {
    status: "success",
    data: {
      fen,
      effective_from: "2026-01-02",
      effective_until: null,
      preference: { kind: "move", uci },
      periods: [
        {
          effective_from: "2026-01-02",
          effective_until: null,
          preference: { kind: "move", uci },
        },
      ],
    },
  };
}

export function testClients(
  initialState: PreferredMoveResponse["state"] = "unassigned",
  initialEffectiveAt = "2026-01-01T00:00:00.000000Z",
) {
  let state = initialState;
  let effectiveAt = state === "assigned" ? initialEffectiveAt : null;
  let savedMove = state === "assigned" ? { uci: "e2e4", san: "e4" } : null;
  const preferredMoveClient: PreferredMoveClient = {
    get: vi.fn(async (fen) => ({
      status: "success" as const,
      data: {
        ...preferredMoveResponse(fen, state),
        move: savedMove,
        effective_at: state === "assigned" ? effectiveAt : null,
      },
    })),
    put: vi.fn(async ({ fen, move_uci }) => {
      state = "assigned";
      effectiveAt = "2026-01-02";
      const chess = new Chess(fen);
      const move = chess.move({
        from: move_uci.slice(0, 2) as Square,
        to: move_uci.slice(2, 4) as Square,
        ...(move_uci.length === 5 ? { promotion: move_uci.slice(4) as "q" | "r" | "b" | "n" } : {}),
      });
      savedMove = { uci: move_uci, san: move.san };
      return mutationResponse(fen, "move", move_uci);
    }),
    remove: vi.fn(async ({ fen }) => {
      state = "unassigned";
      effectiveAt = null;
      savedMove = null;
      return mutationResponse(fen, "no_preference");
    }),
  };
  const positionContextClient: PositionContextClient = vi.fn(async (fen, trainerColor) => ({
    status: "success" as const,
    data: { fen, trainerColor, ...CONTEXT },
  }));
  const moveResponseDistributionClient: MoveResponseDistributionClient = vi.fn(
    async (fen, color) => ({
      status: "success" as const,
      data: moveResponseDistributionResponse(fen, color),
    }),
  );
  return { preferredMoveClient, positionContextClient, moveResponseDistributionClient };
}

export function gameClient(detail: GameDetailResponse = GAME_DETAIL): GameDetailClient {
  return vi.fn(async () => ({ data: detail, error: undefined }));
}

export function renderWorkspace(
  props: ComponentProps<typeof RepertoireBuilderWorkspace> = {},
): ReturnType<typeof render> {
  const clients = testClients();
  return render(
    <RepertoireBuilderWorkspace
      analysisClient={noAnalysisClient()}
      gameClient={gameClient()}
      preferredMoveClient={clients.preferredMoveClient}
      positionContextClient={clients.positionContextClient}
      moveResponseDistributionClient={clients.moveResponseDistributionClient}
      {...props}
    />,
  );
}

export function sharedPositionSummary(): HTMLElement {
  const row = screen.getByTestId("position-description-row");
  const description = within(row).getByRole("button", { name: "Position description" });
  if (description.getAttribute("aria-expanded") === "false") {
    fireEvent.click(description);
  }
  const summary = row.querySelector("[data-position-summary]");
  if (!(summary instanceof HTMLElement)) {
    throw new Error("The shared position summary is missing.");
  }
  return summary;
}
