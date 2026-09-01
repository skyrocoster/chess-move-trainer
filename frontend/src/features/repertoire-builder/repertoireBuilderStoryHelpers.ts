import { Chess } from "chess.js";
import { expect, fn, userEvent, within } from "storybook/test";

import type {
  PositionContextClient,
  PositionContextFailureCode,
  PositionContextResponse,
} from "../viewer/positionContextApi";
import type { Fen } from "../viewer/chessPrimitives";
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
}
