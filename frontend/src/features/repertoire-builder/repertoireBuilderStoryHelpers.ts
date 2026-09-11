import { Chess } from "chess.js";
import { expect, fn, userEvent, within } from "storybook/test";

import type { GameDetailResponse } from "../../api/client";
import { GAME_UUID } from "../game/gameFixtures";
import type {
  PositionContextClient,
  PositionContextFailureCode,
  PositionContextResponse,
} from "../position-context/positionContextApi";
import type { Fen } from "../chess/chessPrimitives";
import type {
  MoveResponseDistributionClient,
  MoveResponseDistributionResponse,
} from "../move-response-distribution/moveResponseDistributionApi";
import type {
  PreferredMoveClient,
  PreferredMoveFailureCode,
  PreferredMoveResponse,
  PreferredMoveValue,
} from "./preferredMoveApi";
import { getPreferredMoveDateWindow } from "./preferredMoveApi";
import {
  preferredMoveRelationshipFixtures,
  type PreferredMoveRelationship,
} from "./preferredMoveStoryFixtures";
import type { GameDetailClient } from "./RepertoireBuilderWorkspace";

const DEFAULT_MOVE: PreferredMoveValue = { uci: "e2e4", san: "e4" };

export const STORY_GAME_DETAIL: GameDetailResponse = {
  ended_at_utc: null,
  game_uuid: "0007925c-5a8d-11f0-9740-f690a301000f",
  occurrences: [
    {
      ply: 0,
      fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
      move_uci: "e2e4",
    },
    {
      ply: 1,
      fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
      move_uci: "e7e5",
    },
    {
      ply: 2,
      fen: "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
      move_uci: "g1f3",
    },
    {
      ply: 3,
      fen: "rnbqkbnr/pppp1ppp/8/4p3/5N2/8/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
      move_uci: null,
    },
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

export const STORY_BLACK_SUBJECT_GAME_DETAIL: GameDetailResponse = {
  ...STORY_GAME_DETAIL,
  trainer_color: "black",
};

export const STORY_PROMOTION_GAME_DETAIL: GameDetailResponse = {
  ended_at_utc: null,
  game_uuid: GAME_UUID,
  occurrences: [{ ply: 0, fen: "k7/4P3/8/8/8/8/8/4K3 w - - 0 1", move_uci: null }],
  opponent_chesscom_uuid: null,
  opponent_rating: null,
  original_pgn: "",
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

export function storyGameClient(detail: GameDetailResponse = STORY_GAME_DETAIL): GameDetailClient {
  return fn(async () => ({ data: detail, error: undefined }));
}

export type StoryPreferredMoveOptions = {
  relationship?: PreferredMoveRelationship;
  savedMove?: PreferredMoveValue;
  readFailure?: PreferredMoveFailureCode;
  putFailure?: PreferredMoveFailureCode;
  removeFailure?: PreferredMoveFailureCode;
  pendingMutation?: "save" | "remove";
  pendingRead?: boolean;
  onRequest?: (request: StoryPreferredMoveRequest) => void;
};

export type StoryPreferredMoveRequest =
  | {
      method: "GET";
      fen: Fen;
      from: string;
      until: string;
    }
  | {
      method: "PUT";
      fen: Fen;
      move_uci: string;
      effective_from: string;
    }
  | {
      method: "DELETE";
      fen: Fen;
      effective_from: string;
    };

export function storyPreferredMoveDateWindow() {
  return getPreferredMoveDateWindow();
}

export type StoryPositionContextOptions = Partial<
  Pick<PositionContextResponse, "observedInGames" | "distinctGameCount" | "totalGameCount">
> & {
  failure?: PositionContextFailureCode;
  pending?: boolean;
};

function moveResponseData(fen: Fen, color: "white" | "black"): MoveResponseDistributionResponse {
  const afterStoredE5 = fen === "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2";
  const blackToMove = fen.split(" ")[1] === "b";
  const replies: readonly [string, string, number][] = afterStoredE5
    ? [
        ["g1f3", "Nf3", 4],
        ["d2d4", "d4", 3],
        ["c2c4", "c4", 2],
        ["b1c3", "Nc3", 1],
        ["b2b3", "b3", 1],
        ["f1c4", "Bc4", 1],
      ]
    : blackToMove
      ? [
          ["e7e5", "e5", 4],
          ["c7c5", "c5", 3],
          ["g8f6", "Nf6", 2],
          ["c7c6", "c6", 1],
          ["d7d5", "d5", 1],
          ["g7g6", "g6", 1],
        ]
      : [
          ["e2e4", "e4", 4],
          ["d2d4", "d4", 3],
          ["c2c4", "c4", 2],
          ["b2b3", "b3", 1],
          ["c2c3", "c3", 1],
          ["g1f3", "Nf3", 1],
        ];

  return {
    fen,
    color,
    matching_game_count: 10,
    outgoing_occurrence_count: replies.reduce(
      (total, [, , occurrenceCount]) => total + occurrenceCount,
      0,
    ),
    replies: replies.map(([child_uci, san, occurrence_count], index) => ({
      rank: index + 1,
      child_uci,
      san,
      occurrence_count,
    })),
  };
}

export function storyMoveResponseDistributionClient(): MoveResponseDistributionClient {
  return fn(async (fen, color) => ({
    status: "success" as const,
    data: moveResponseData(fen, color),
  }));
}

function mutationResponse(fen: Fen, effectiveAt: string) {
  return {
    status: "success" as const,
    data: { fen, changed: true, effective_at: effectiveAt },
  };
}

function moveFromRequest(fen: Fen, uci: string): PreferredMoveValue {
  const chess = new Chess(fen);
  const move = chess.move({
    from: uci.slice(0, 2),
    to: uci.slice(2, 4),
    ...(uci.length === 5 ? { promotion: uci.slice(4) as "q" | "r" | "b" | "n" } : {}),
  });
  return { uci, san: move.san };
}

export function storyPreferredMoveClient(
  options: StoryPreferredMoveOptions = {},
): PreferredMoveClient {
  const relationship = options.relationship ?? "empty";
  const fixture = preferredMoveRelationshipFixtures[relationship];
  let state: PreferredMoveResponse["state"] =
    fixture.savedPresence === "present" ? "assigned" : "unassigned";
  let move = options.savedMove ?? fixture.saved?.move ?? DEFAULT_MOVE;
  let effectiveAt = state === "assigned" ? "2026-01-01T00:00:00.000000Z" : null;
  let assignedFen: Fen | null = null;

  return {
    get: fn(async (fen) => {
      const { today, tomorrow } = storyPreferredMoveDateWindow();
      options.onRequest?.({ method: "GET", fen, from: today, until: tomorrow });
      if (options.pendingRead) {
        return new Promise<never>(() => undefined);
      }
      if (options.readFailure) {
        return { status: options.readFailure };
      }
      if (state === "assigned" && assignedFen === null) {
        assignedFen = fen;
      }
      const assigned = state === "assigned" && assignedFen === fen;
      return {
        status: "success" as const,
        data: {
          fen,
          state: assigned ? ("assigned" as const) : ("unassigned" as const),
          move: assigned ? move : null,
          effective_at: assigned ? effectiveAt : null,
        },
      };
    }),
    put: fn(async ({ fen, move_uci }) => {
      const { today } = storyPreferredMoveDateWindow();
      options.onRequest?.({ method: "PUT", fen, move_uci, effective_from: today });
      if (options.pendingMutation === "save") {
        return new Promise<never>(() => undefined);
      }
      if (options.putFailure) {
        return { status: options.putFailure };
      }
      move = moveFromRequest(fen, move_uci);
      state = "assigned";
      assignedFen = fen;
      const { today: effectiveToday } = storyPreferredMoveDateWindow();
      effectiveAt = `${effectiveToday}T00:00:00.000000Z`;
      return mutationResponse(fen, effectiveAt);
    }),
    remove: fn(async ({ fen }) => {
      const { today } = storyPreferredMoveDateWindow();
      options.onRequest?.({ method: "DELETE", fen, effective_from: today });
      if (options.pendingMutation === "remove") {
        return new Promise<never>(() => undefined);
      }
      if (options.removeFailure) {
        return { status: options.removeFailure };
      }
      state = "unassigned";
      effectiveAt = null;
      return mutationResponse(fen, `${today}T00:00:00.000000Z`);
    }),
  };
}

const DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR = { white: 3, black: 2 } as const;
const DEFAULT_TOTAL_GAME_COUNT = 10;

export function storyPositionContextClient(
  options: StoryPositionContextOptions = {},
): PositionContextClient {
  return fn(async (fen, trainerColor) => {
    if (options.pending) {
      return new Promise<never>(() => undefined);
    }
    if (options.failure) {
      return { status: options.failure };
    }
    return {
      status: "success" as const,
      data: {
        fen,
        trainerColor,
        observedInGames: options.observedInGames ?? true,
        distinctGameCount:
          options.distinctGameCount ?? DEFAULT_DISTINCT_GAME_COUNT_BY_COLOR[trainerColor],
        totalGameCount: options.totalGameCount ?? DEFAULT_TOTAL_GAME_COUNT,
      },
    };
  });
}

export async function loadGame(canvas: ReturnType<typeof within>, gameUuid: string) {
  await userEvent.type(canvas.getByLabelText("Game UUID"), gameUuid);
  await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
  await expect(canvas.getByTestId("session-origin")).toHaveTextContent("complete game loaded");
}

export async function expectNoHorizontalOverflow(canvasElement: HTMLElement) {
  const documentElement = canvasElement.ownerDocument.documentElement;
  await expect(documentElement.scrollWidth).toBeLessThanOrEqual(documentElement.clientWidth);
  await expect(canvasElement.ownerDocument.body.scrollWidth).toBeLessThanOrEqual(
    canvasElement.ownerDocument.body.clientWidth,
  );
}
