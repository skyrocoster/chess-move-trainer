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

const DEFAULT_MOVE: PreferredMoveValue = { uci: "e2e4", san: "e4" };

export type StoryPreferredMoveOptions = {
  initialState?: PreferredMoveResponse["state"];
  initialMove?: PreferredMoveValue;
  readFailure?: PreferredMoveFailureCode;
  putFailure?: PreferredMoveFailureCode;
  removeFailure?: PreferredMoveFailureCode;
};

export type StoryPositionContextOptions = Partial<
  Pick<PositionContextResponse, "overall_exists" | "white_count" | "black_count">
> & {
  failure?: PositionContextFailureCode;
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
  let state = options.initialState ?? "unassigned";
  let move = options.initialMove ?? DEFAULT_MOVE;
  let assignedFen: Fen | null = null;

  return {
    get: fn(async (fen) => {
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
        },
      };
    }),
    put: fn(async ({ fen, move_uci, effective_at }) => {
      if (options.putFailure) {
        return { status: options.putFailure };
      }
      move = moveFromRequest(fen, move_uci);
      state = "assigned";
      assignedFen = fen;
      return mutationResponse(fen, effective_at ?? "");
    }),
    remove: fn(async ({ fen, effective_at }) => {
      if (options.removeFailure) {
        return { status: options.removeFailure };
      }
      state = "unassigned";
      return mutationResponse(fen, effective_at ?? "");
    }),
  };
}

export function storyPositionContextClient(
  options: StoryPositionContextOptions = {},
): PositionContextClient {
  return fn(async (fen) => {
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
      },
    };
  });
}

function ordinal(day: number): string {
  if (day % 100 >= 11 && day % 100 <= 13) {
    return `${day}th`;
  }
  return `${day}${day % 10 === 1 ? "st" : day % 10 === 2 ? "nd" : day % 10 === 3 ? "rd" : "th"}`;
}

export async function selectCurrentUtcDate(canvasElement: HTMLElement): Promise<string> {
  const canvas = within(canvasElement);
  const body = within(canvasElement.ownerDocument.body);
  const now = new Date();
  const month = new Intl.DateTimeFormat("en-US", { month: "long", timeZone: "UTC" }).format(now);
  const day = now.getUTCDate();
  const year = now.getUTCFullYear();

  await userEvent.click(await canvas.findByRole("button", { name: "Effective date: Choose date" }));
  const calendar = await body.findByRole("dialog", { name: "Effective date" });
  await userEvent.click(
    within(calendar).getByRole("button", {
      name: new RegExp(`${month} ${ordinal(day)}, ${year}`),
    }),
  );
  return `${String(year).padStart(4, "0")}-${String(now.getUTCMonth() + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

export async function loadGame(canvas: ReturnType<typeof within>, gameUuid: string, ply?: string) {
  await userEvent.type(canvas.getByLabelText("Game UUID"), gameUuid);
  if (ply !== undefined) {
    await userEvent.type(canvas.getByLabelText(/Ply/), ply);
  }
  await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
}

export async function expectNoHorizontalOverflow(canvasElement: HTMLElement) {
  const documentElement = canvasElement.ownerDocument.documentElement;
  await expect(documentElement.scrollWidth).toBeLessThanOrEqual(documentElement.clientWidth);
}
