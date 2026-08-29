import { expect, fn, userEvent, waitFor, within } from "storybook/test";

import type {
  AnalysisClient,
  EvaluationCandidate,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";
import type { Game } from "./gameModel";
import type { GameLookup, GameLookupFailure } from "./positionApi";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";
import { PROMOTION_GAME } from "./viewerStoryFixtures";

export function completeGameLookup(game: Game = VIEWER_GAME): GameLookup {
  return fn(async (_uuid, initialPly) => ({
    status: "success" as const,
    game: { ...game, initial_ply: initialPly ?? 0 },
  }));
}

export function failureLookup(status: GameLookupFailure): GameLookup {
  return fn(async () => ({ status }));
}

export function storyAnalysisClient(): AnalysisClient {
  return {
    observe: fn(async (fen) => ({
      status: "success" as const,
      data: { fen, eligibility: "missing" as const, result: null, status: null, terminal: false },
    })),
    enqueue: fn(async () => {
      throw new Error("Stage 1 workspace stories do not exercise analysis actions");
    }),
    status: fn(async () => ({
      status: "success" as const,
      data: {
        fen: VIEWER_GAME.positions[0].fen,
        state: null,
        completed_at: null,
        error_code: null,
      },
    })),
  };
}

function candidateFor(move: string, rank: number): EvaluationCandidate {
  return {
    rank,
    score_kind: "cp",
    score_value: 34 - (rank - 1) * 10,
    wdl_wins: 420,
    wdl_draws: 300,
    wdl_losses: 280,
    pv_uci: [move],
    depth: 20,
    seldepth: 24,
    nodes: 200_000,
    engine_time_ms: 100,
  };
}

function candidateResult(fen: string, moves: readonly string[]): EvaluationResult {
  return {
    fen,
    profile_id: "story-candidate-profile",
    candidates: moves.map((move, index) => candidateFor(move, index + 1)),
    terminal_kind: null,
    completed_at: "2026-08-22T00:00:01+00:00",
    wall_time_ms: 100,
  };
}

function candidateStatus(): EvaluationStatus {
  return {
    state: "done",
    position: 0,
    attempts: 1,
    enqueued_at: "2026-08-22T00:00:00+00:00",
    started_at: "2026-08-22T00:00:00+00:00",
    completed_at: "2026-08-22T00:00:01+00:00",
    error_code: null,
  };
}

export function storyCandidateAnalysisClient(
  moves: readonly string[] = ["e2e4", "d2d4", "c2c4", "g1f3", "b1c3"],
): AnalysisClient {
  return {
    observe: fn(async (fen) => ({
      status: "success" as const,
      data: {
        fen,
        eligibility: "eligible" as const,
        result: candidateResult(fen, moves),
        status: candidateStatus(),
        terminal: false,
      },
    })),
    enqueue: fn(async () => {
      throw new Error("Candidate stories do not exercise analysis actions");
    }),
    status: fn(async (fen) => ({
      status: "success" as const,
      data: {
        fen,
        state: "done" as const,
        completed_at: "2026-08-22T00:00:01+00:00",
        error_code: null,
      },
    })),
  };
}

export const pendingLookup: GameLookup = () => new Promise(() => {});

export async function submit(
  canvas: ReturnType<typeof within>,
  uuid = VIEWER_GAME_UUID,
  ply?: string,
) {
  await userEvent.type(canvas.getByLabelText("Game UUID"), uuid);
  if (ply !== undefined) {
    await userEvent.type(canvas.getByLabelText(/Ply/), ply);
  }
  await userEvent.click(canvas.getByRole("button", { name: "Load game" }));
}

export async function keyboardMove(
  canvasElement: HTMLElement,
  sourceSquare: string,
  arrows: string,
) {
  const piece = canvasElement.querySelector<HTMLElement>(
    `[data-square="${sourceSquare}"] [aria-roledescription="draggable"]`,
  );
  if (!piece) {
    throw new Error(`Unable to start a keyboard move from ${sourceSquare}.`);
  }
  piece.focus();
  await userEvent.keyboard("{Enter}");
  for (const arrow of arrows.match(/\{[^}]+\}/g) ?? []) {
    await userEvent.keyboard(arrow);
  }
  await userEvent.keyboard("{Enter}");
}

export async function branchPromotionInteractionPlay({
  canvasElement,
}: {
  canvasElement: HTMLElement;
}) {
  const canvas = within(canvasElement);
  const body = within(canvasElement.ownerDocument.body);
  await submit(canvas, VIEWER_GAME_UUID, "0");
  await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
  await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(
    PROMOTION_GAME.positions[0].fen,
  );
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
    PROMOTION_GAME.positions[0].fen,
  );
  await keyboardMove(canvasElement, "e7", "{ArrowUp}{ArrowUp}");
  await waitFor(() =>
    expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
  );
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
    PROMOTION_GAME.positions[0].fen,
  );
  await userEvent.keyboard("{Escape}");
  await expect(body.queryByRole("dialog")).not.toBeInTheDocument();
  await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
    "Promotion cancelled; the captured position is unchanged.",
  );
  await keyboardMove(canvasElement, "e7", "{ArrowUp}{ArrowUp}");
  await waitFor(() =>
    expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
  );
  await userEvent.click(body.getByRole("button", { name: "Promote to knight" }));
  await expect(canvas.getByTestId("branch-san")).toHaveTextContent("1. e8=N");
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
    "k3N3/8/8/8/8/8/8/4K3 b - - 0 1",
  );
}

export async function candidatePromotionInteractionPlay({
  canvasElement,
}: {
  canvasElement: HTMLElement;
}) {
  const canvas = within(canvasElement);
  const body = within(canvasElement.ownerDocument.body);
  const originFen = PROMOTION_GAME.positions[0].fen;
  await submit(canvas, VIEWER_GAME_UUID, "0");
  await expect(canvas.getByText("Ply 0 of 0")).toBeVisible();
  const candidate = await canvas.findByRole("button", { name: /1\. e8=Q/ });
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(originFen);

  await userEvent.click(candidate);
  await waitFor(() =>
    expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
  );
  await expect(canvasElement.ownerDocument.activeElement).toBe(
    body.getByRole("button", { name: "Promote to queen" }),
  );
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(originFen);

  await userEvent.keyboard("{Escape}");
  await expect(body.queryByRole("dialog")).not.toBeInTheDocument();
  await expect(canvasElement.ownerDocument.activeElement).toBe(candidate);
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(originFen);

  await userEvent.click(candidate);
  await waitFor(() =>
    expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
  );
  await userEvent.click(body.getByRole("button", { name: "Promote to queen" }));
  await expect(canvas.getByTestId("branch-san")).toHaveTextContent("1. e8=Q+");
  await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
    "k3Q3/8/8/8/8/8/8/4K3 b - - 0 1",
  );
}

export async function finalPlay({ canvasElement }: { canvasElement: HTMLElement }) {
  const canvas = within(canvasElement);
  await submit(canvas, VIEWER_GAME_UUID, "3");
  await expect(canvas.getByText("Ply 3 of 3")).toBeVisible();
  await expect(canvas.getByRole("button", { name: "Previous" })).toBeEnabled();
  await expect(canvas.getByRole("button", { name: "Next" })).toBeDisabled();
}
