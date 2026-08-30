import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { InteractiveBoardMoveIntent } from "../board-adapter/InteractiveBoardAdapter";
import type { BranchSnapshot } from "../board-adapter/branchModel";
import type { LastMove } from "../board-adapter/lastMove";
import type { AnalysisClient } from "./analysisApi";
import ViewerWorkspace from "./ViewerWorkspace";
import type { GameLookup } from "./positionApi";
import type { PositionContextClient } from "./positionContextApi";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";

const BRANCH_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

vi.mock("../board-adapter/InteractiveBoardAdapter", () => ({
  InteractiveBoardAdapter: ({
    branchSnapshot,
    onMoveIntent,
    onReset,
    label,
    notice,
    lastMove,
  }: {
    branchSnapshot: BranchSnapshot;
    onMoveIntent: (intent: InteractiveBoardMoveIntent) => boolean;
    onReset: () => void;
    label: string;
    notice: string;
    lastMove: LastMove | null;
  }) => {
    return (
      <section data-testid="interactive-board-adapter">
        <div
          role="img"
          aria-label={label}
          data-testid="interactive-board"
          data-last-move-source={lastMove?.sourceSquare}
          data-last-move-target={lastMove?.targetSquare}
        />
        <p data-testid="branch-san">
          {branchSnapshot.moves.length > 0 ? "1. e4" : "No branch moves yet"}
        </p>
        <code data-testid="branch-current-fen">{branchSnapshot.currentFen}</code>
        <p data-testid="branch-status">{notice}</p>
        <button
          type="button"
          data-testid="branch-test-move"
          onClick={() =>
            onMoveIntent({
              sourceSquare: "e2",
              targetSquare: "e4",
              sourceElement: null,
              anchorElement: null,
            })
          }
        >
          Start test branch
        </button>
        <button
          type="button"
          data-testid="branch-test-black-move"
          onClick={() =>
            onMoveIntent({
              sourceSquare: "e7",
              targetSquare: "e5",
              sourceElement: null,
              anchorElement: null,
            })
          }
        >
          Continue test branch
        </button>
        <button type="button" onClick={onReset}>
          Reset branch
        </button>
      </section>
    );
  },
}));

afterEach(() => cleanup());

function successfulLookup(): GameLookup {
  return vi.fn(async (_uuid, initialPly) => ({
    status: "success" as const,
    game: { ...VIEWER_GAME, initial_ply: initialPly ?? 0 },
  }));
}

function analysisClient(): AnalysisClient {
  const observe = vi.fn(async (fen: string) => ({
    status: "success" as const,
    data: { fen, eligibility: "missing" as const, result: null, status: null, terminal: false },
  }));
  const enqueue = vi.fn(async (fen: string, action: "analyze" | "update" | "retry") => ({
    status: "success" as const,
    data: {
      fen,
      action,
      outcome: "queued",
      eligibility: "missing" as const,
      status: {
        state: "queued" as const,
        position: 0,
        attempts: 1,
        enqueued_at: "2026-08-22T00:00:00+00:00",
        started_at: null,
        completed_at: null,
        error_code: null,
      },
    },
  }));
  const status = vi.fn(async (fen: string) => ({
    status: "success" as const,
    data: { fen, state: null, completed_at: null, error_code: null },
  }));
  return {
    observe,
    enqueue,
    status,
  };
}

function completedAnalysisClient(candidateMoves: string[]): AnalysisClient {
  const observe = vi.fn(async (fen: string) => ({
    status: "success" as const,
    data: {
      fen,
      eligibility: "eligible" as const,
      result: {
        fen,
        profile_id: "test-profile",
        candidates: candidateMoves.map((move, index) => ({
          rank: index + 1,
          score_kind: "cp" as const,
          score_value: 34 - index * 10,
          wdl_wins: 420,
          wdl_draws: 300,
          wdl_losses: 280,
          pv_uci: [move],
          depth: 20,
          seldepth: 24,
          nodes: 200_000,
          engine_time_ms: 100,
        })),
        terminal_kind: null,
        completed_at: "2026-08-22T00:00:01+00:00",
        wall_time_ms: 100,
      },
      status: {
        state: "done" as const,
        position: 0,
        attempts: 1,
        enqueued_at: "2026-08-22T00:00:00+00:00",
        started_at: "2026-08-22T00:00:00+00:00",
        completed_at: "2026-08-22T00:00:01+00:00",
        error_code: null,
      },
      terminal: false,
    },
  }));
  return { observe, enqueue: vi.fn(), status: vi.fn() };
}

function positionContextClient(): PositionContextClient {
  return vi.fn(async (fen) => ({
    status: "success" as const,
    data: {
      fen,
      overall_exists: true,
      white_count: 2,
      black_count: 1,
      white_total: 10,
      black_total: 10,
    },
  }));
}

async function loadGame(user: ReturnType<typeof userEvent.setup>, ply = "") {
  await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
  if (ply) {
    await user.type(screen.getByLabelText(/Ply/), ply);
  }
  await user.click(screen.getByRole("button", { name: "Load game" }));
}

describe("ViewerWorkspace temporary branch ownership", () => {
  it("keeps captured context immutable, targets branch FEN, gates traversal, and never enqueues", async () => {
    const client = analysisClient();
    const contextClient = positionContextClient();
    const user = userEvent.setup();
    render(
      <ViewerWorkspace
        lookup={successfulLookup()}
        analysisClient={client}
        positionContextClient={contextClient}
      />,
    );

    await loadGame(user);
    await screen.findByText("Ply 0 of 3");
    expect(screen.getByTestId("interactive-board")).not.toHaveAttribute("data-last-move-source");
    expect(screen.getByTestId("interactive-board")).not.toHaveAttribute("data-last-move-target");
    await user.click(screen.getByTestId("branch-test-move"));

    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. e4");
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-source", "e2");
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-target", "e4");
    expect(screen.getByText("Ply 0 of 3")).toBeVisible();
    expect(screen.getByText("Initial position")).toBeVisible();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    await waitFor(() =>
      expect(client.observe).toHaveBeenCalledWith(BRANCH_FEN, expect.any(AbortSignal)),
    );
    await waitFor(() =>
      expect(contextClient).toHaveBeenCalledWith(BRANCH_FEN, expect.any(AbortSignal)),
    );
    expect(client.enqueue).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Reset branch" }));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByTestId("interactive-board")).not.toHaveAttribute("data-last-move-source");
    expect(screen.getByTestId("interactive-board")).not.toHaveAttribute("data-last-move-target");
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
    await waitFor(() =>
      expect(contextClient).toHaveBeenCalledWith(
        VIEWER_GAME.positions[0].fen,
        expect.any(AbortSignal),
      ),
    );
  });

  it("deliberately analyzes only the currently displayed branch FEN", async () => {
    const client = analysisClient();
    const user = userEvent.setup();
    render(
      <ViewerWorkspace
        lookup={successfulLookup()}
        analysisClient={client}
        positionContextClient={positionContextClient()}
      />,
    );

    await loadGame(user);
    await screen.findByText("Ply 0 of 3");
    await user.click(screen.getByTestId("branch-test-move"));
    await waitFor(() =>
      expect(client.observe).toHaveBeenCalledWith(BRANCH_FEN, expect.any(AbortSignal)),
    );
    expect(client.enqueue).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Analyze position" }));

    expect(client.enqueue).toHaveBeenCalledTimes(1);
    expect(client.enqueue).toHaveBeenCalledWith(BRANCH_FEN, "analyze", expect.any(AbortSignal));
    expect(vi.mocked(client.enqueue).mock.calls.map(([fen]) => fen)).toEqual([BRANCH_FEN]);
  });

  it("serializes a black temporary branch double-step with its strict target square", async () => {
    const user = userEvent.setup();
    render(
      <ViewerWorkspace
        lookup={successfulLookup()}
        analysisClient={analysisClient()}
        positionContextClient={positionContextClient()}
      />,
    );

    await loadGame(user, "1");
    await screen.findByText("Ply 1 of 3");
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-source", "e2");
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-target", "e4");
    await user.click(screen.getByTestId("branch-test-black-move"));

    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-source", "e7");
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-target", "e5");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
    );
    await user.click(screen.getByRole("button", { name: "Reset branch" }));
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-source", "e2");
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-last-move-target", "e4");

    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    );
  });

  it.each([
    ["Best", "1. e4", BRANCH_FEN],
    ["alternative", "1. d4", "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1"],
  ] as const)(
    "routes the %s candidate through the branch handler after Flip",
    async (_, name, fen) => {
      const client = completedAnalysisClient(["e2e4", "d2d4"]);
      const user = userEvent.setup();
      render(
        <ViewerWorkspace
          lookup={successfulLookup()}
          analysisClient={client}
          positionContextClient={positionContextClient()}
        />,
      );

      await loadGame(user);
      await screen.findByText("Analysis complete");
      await user.click(screen.getByRole("button", { name: "Flip" }));
      expect(screen.getByRole("img", { name: /Black at the bottom/ })).toBeVisible();

      await user.click(screen.getByRole("button", { name }));

      expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(fen);
      expect(client.enqueue).not.toHaveBeenCalled();
    },
  );

  it("rejects illegal or stale candidates without changing the branch or enqueueing analysis", async () => {
    const client = completedAnalysisClient(["e2e4", "a1a1"]);
    const user = userEvent.setup();
    render(
      <ViewerWorkspace
        lookup={successfulLookup()}
        analysisClient={client}
        positionContextClient={positionContextClient()}
      />,
    );

    await loadGame(user);
    await screen.findByText("Analysis complete");
    await user.click(screen.getByRole("button", { name: "1. e4" }));
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(BRANCH_FEN);

    await user.click(screen.getAllByRole("button", { name: "Line unavailable" })[0]);

    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(BRANCH_FEN);
    expect(screen.getByTestId("branch-status")).toHaveTextContent(
      "Move rejected because it is illegal.",
    );
    expect(client.enqueue).not.toHaveBeenCalled();
  });

  it("discards a branch immediately when replacement loading starts", async () => {
    let calls = 0;
    const lookup: GameLookup = vi.fn(async (_uuid, initialPly) => {
      calls += 1;
      return calls === 1
        ? { status: "success" as const, game: { ...VIEWER_GAME, initial_ply: initialPly ?? 0 } }
        : { status: "game_unavailable" as const };
    });
    const user = userEvent.setup();
    render(
      <ViewerWorkspace
        lookup={lookup}
        analysisClient={analysisClient()}
        positionContextClient={positionContextClient()}
      />,
    );

    await loadGame(user);
    await screen.findByText("Ply 0 of 3");
    await user.click(screen.getByTestId("branch-test-move"));
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();

    await user.click(screen.getByRole("button", { name: "Load game" }));
    await screen.findByRole("heading", { name: "Game unavailable", level: 2 });
    await waitFor(() =>
      expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet"),
    );
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });
});
