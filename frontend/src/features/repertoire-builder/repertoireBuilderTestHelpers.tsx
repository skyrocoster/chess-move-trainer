import { fireEvent, render, screen, within } from "@testing-library/react";
import { Chess, type Square } from "chess.js";
import type { ComponentProps } from "react";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { vi } from "vitest";

import type {
  AnalysisClient,
  EvaluationCandidate,
  EvaluationObservation,
  EvaluationStatus,
} from "../viewer/analysisApi";
import type { PositionContextClient } from "../viewer/positionContextApi";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import type {
  PreferredMoveClient,
  PreferredMoveMutationResult,
  PreferredMoveResponse,
} from "./preferredMoveApi";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";

export const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
export const STORED_BOARD_LABEL = `Chess board: game ${VIEWER_GAME_UUID}, ply 2, Black at the bottom`;
export const STARTING_FEN = VIEWER_GAME.positions[0].fen;
export const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";
export const AFTER_D4_FEN = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1";
export const AFTER_E8_KNIGHT_FEN = "k3N3/8/8/8/8/8/8/4K3 b - - 0 1";
export const CONTEXT = {
  overall_exists: true,
  white_count: 0,
  black_count: 0,
  white_total: 10,
  black_total: 10,
};
export const rawStyles = readFileSync(
  join(dirname(fileURLToPath(import.meta.url)), "RepertoireBuilderWorkspace.module.css"),
  "utf8",
);

export function noAnalysisClient(): AnalysisClient {
  return {
    observe: vi.fn(async (fen: string) => ({
      status: "success" as const,
      data: { fen, eligibility: "missing" as const, result: null, status: null, terminal: false },
    })),
    enqueue: vi.fn() as AnalysisClient["enqueue"],
    status: vi.fn() as AnalysisClient["status"],
  };
}

export const DONE_STATUS: EvaluationStatus = {
  state: "done",
  position: 0,
  attempts: 1,
  enqueued_at: "2026-08-22T00:00:00+00:00",
  started_at: "2026-08-22T00:00:00+00:00",
  completed_at: "2026-08-22T00:00:01+00:00",
  error_code: null,
};

export function displayCandidate(fen: string, overrides: Partial<EvaluationCandidate> = {}) {
  return {
    rank: 1,
    score_kind: "cp" as const,
    score_value: 34,
    wdl_wins: 420,
    wdl_draws: 300,
    wdl_losses: 280,
    pv_uci: ["e2e4"],
    depth: 20,
    seldepth: 24,
    nodes: 200_000,
    engine_time_ms: 100,
    ...overrides,
    fen,
  };
}

export type DisplayState =
  | "neutral"
  | "completed-cp"
  | "mate"
  | "pending"
  | "stale-retained"
  | "failed-retained"
  | "failed-empty"
  | "unavailable"
  | "dual";

export function displayAnalysisClient(state: DisplayState): AnalysisClient {
  return {
    observe: vi.fn(async (fen: string) => {
      if (state === "unavailable") {
        return { status: "evaluation_unavailable" as const };
      }
      const candidate =
        state === "completed-cp" ||
        state === "stale-retained" ||
        state === "failed-retained" ||
        state === "dual"
          ? displayCandidate(
              fen,
              state === "dual" ? { score_value: fen === STARTING_FEN ? 34 : -34 } : {},
            )
          : state === "mate"
            ? displayCandidate(fen, { score_kind: "mate", score_value: -3 })
            : null;
      const queueState =
        state === "pending"
          ? "queued"
          : state === "failed-retained" || state === "failed-empty"
            ? "failed"
            : "done";
      return {
        status: "success" as const,
        data: {
          fen,
          eligibility:
            state === "stale-retained" ? ("stale" as const) : candidate ? "eligible" : "missing",
          result: candidate
            ? {
                fen,
                profile_id: "test-profile",
                candidates: [candidate],
                terminal_kind: null,
                completed_at: "2026-08-22T00:00:01+00:00",
                wall_time_ms: 100,
              }
            : null,
          status: state === "neutral" ? null : { ...DONE_STATUS, state: queueState },
          terminal: false,
        } satisfies EvaluationObservation,
      };
    }),
    enqueue: vi.fn() as AnalysisClient["enqueue"],
    status: vi.fn() as AnalysisClient["status"],
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

export function mutationResponse(fen: string): PreferredMoveMutationResult {
  return {
    status: "success",
    data: { fen, changed: true, effective_at: "2026-01-01T00:00:00.000000Z" },
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
    put: vi.fn(async ({ fen, move_uci, effective_at }) => {
      state = "assigned";
      effectiveAt = effective_at || "2026-01-01T00:00:00.000000Z";
      const chess = new Chess(fen);
      const move = chess.move({
        from: move_uci.slice(0, 2) as Square,
        to: move_uci.slice(2, 4) as Square,
        ...(move_uci.length === 5 ? { promotion: move_uci.slice(4) as "q" | "r" | "b" | "n" } : {}),
      });
      savedMove = { uci: move_uci, san: move.san };
      return mutationResponse(fen);
    }),
    remove: vi.fn(async ({ fen }) => {
      state = "unassigned";
      effectiveAt = null;
      savedMove = null;
      return mutationResponse(fen);
    }),
  };
  const positionContextClient: PositionContextClient = vi.fn(async (fen) => ({
    status: "success" as const,
    data: { fen, ...CONTEXT },
  }));
  return { preferredMoveClient, positionContextClient };
}

export function renderWorkspace(
  props: ComponentProps<typeof RepertoireBuilderWorkspace> = {},
): ReturnType<typeof render> {
  const clients = testClients();
  return render(
    <RepertoireBuilderWorkspace
      analysisClient={noAnalysisClient()}
      preferredMoveClient={clients.preferredMoveClient}
      positionContextClient={clients.positionContextClient}
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
