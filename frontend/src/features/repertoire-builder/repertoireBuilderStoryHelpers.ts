import { Chess } from "chess.js";
import { expect, fn, userEvent, within } from "storybook/test";

import type {
  PositionContextClient,
  PositionContextFailureCode,
  PositionContextResponse,
} from "../viewer/positionContextApi";
import type { Fen } from "../viewer/chessPrimitives";
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
import {
  preferredMoveRelationshipFixtures,
  type PreferredMoveRelationship,
} from "./preferredMoveStoryFixtures";

const DEFAULT_MOVE: PreferredMoveValue = { uci: "e2e4", san: "e4" };

export type StoryPreferredMoveOptions = {
  relationship?: PreferredMoveRelationship;
  savedMove?: PreferredMoveValue;
  effectiveAt?: string;
  readFailure?: PreferredMoveFailureCode;
  putFailure?: PreferredMoveFailureCode;
  removeFailure?: PreferredMoveFailureCode;
  pendingMutation?: "save" | "remove";
  pendingRead?: boolean;
};

export type StoryPositionContextOptions = Partial<
  Pick<
    PositionContextResponse,
    "overall_exists" | "white_count" | "black_count" | "white_total" | "black_total"
  >
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
        ["f1c4", "Bc4", 1],
        ["b1c3", "Nc3", 1],
        ["b2b3", "b3", 1],
      ]
    : blackToMove
      ? [
          ["e7e5", "e5", 4],
          ["c7c5", "c5", 3],
          ["g8f6", "Nf6", 2],
          ["d7d5", "d5", 1],
          ["c7c6", "c6", 1],
          ["g7g6", "g6", 1],
        ]
      : [
          ["e2e4", "e4", 4],
          ["d2d4", "d4", 3],
          ["c2c4", "c4", 2],
          ["g1f3", "Nf3", 1],
          ["c2c3", "c3", 1],
          ["b2b3", "b3", 1],
        ];

  return {
    fen,
    color,
    matching_game_count: 10,
    replies: replies.map(([child_uci, san, distinct_game_count], index) => ({
      rank: index + 1,
      child_uci,
      san,
      distinct_game_count,
      opening_name: index === 1 ? "Queen's Pawn Game" : null,
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
    data: { fen, changed: true, effective_at: effectiveAt || "2026-08-29T00:00:00.000Z" },
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
  let effectiveAt =
    options.effectiveAt ?? (state === "assigned" ? "2026-01-01T00:00:00.000000Z" : null);
  let assignedFen: Fen | null = null;

  return {
    get: fn(async (fen) => {
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
    put: fn(async ({ fen, move_uci, effective_at }) => {
      if (options.pendingMutation === "save") {
        return new Promise<never>(() => undefined);
      }
      if (options.putFailure) {
        return { status: options.putFailure };
      }
      move = moveFromRequest(fen, move_uci);
      state = "assigned";
      assignedFen = fen;
      effectiveAt = effective_at || "2026-08-29T00:00:00.000Z";
      return mutationResponse(fen, effective_at ?? "");
    }),
    remove: fn(async ({ fen, effective_at }) => {
      if (options.pendingMutation === "remove") {
        return new Promise<never>(() => undefined);
      }
      if (options.removeFailure) {
        return { status: options.removeFailure };
      }
      state = "unassigned";
      effectiveAt = null;
      return mutationResponse(fen, effective_at ?? "");
    }),
  };
}

export function storyPositionContextClient(
  options: StoryPositionContextOptions = {},
): PositionContextClient {
  return fn(async (fen) => {
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
        overall_exists: options.overall_exists ?? true,
        white_count: options.white_count ?? 3,
        black_count: options.black_count ?? 2,
        white_total: options.white_total ?? 10,
        black_total: options.black_total ?? 10,
      },
    };
  });
}

export async function loadGame(canvas: ReturnType<typeof within>, gameUuid: string, ply?: string) {
  await userEvent.type(canvas.getByLabelText("Game UUID"), gameUuid);
  if (ply !== undefined) {
    await userEvent.type(canvas.getByLabelText(/Ply/), ply);
  }
  await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
  await expect(canvas.getByTestId("session-status")).toHaveTextContent(
    "Select a legal move to continue the local line.",
  );
}

export async function expectNoHorizontalOverflow(canvasElement: HTMLElement) {
  const documentElement = canvasElement.ownerDocument.documentElement;
  await expect(documentElement.scrollWidth).toBeLessThanOrEqual(documentElement.clientWidth);
  await expect(canvasElement.ownerDocument.body.scrollWidth).toBeLessThanOrEqual(
    canvasElement.ownerDocument.body.clientWidth,
  );
}
