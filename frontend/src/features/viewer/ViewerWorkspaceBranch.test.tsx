import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { InteractiveBoardMoveIntent } from "../board-adapter/InteractiveBoardAdapter";
import type { AnalysisClient } from "./analysisApi";
import ViewerWorkspace from "./ViewerWorkspace";
import type { GameLookup } from "./positionApi";
import type { BranchSnapshot } from "./temporaryBranchModel";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "./viewerFixtures";

const BRANCH_FEN = VIEWER_GAME.positions[1].fen;

vi.mock("../board-adapter/InteractiveBoardAdapter", () => ({
  InteractiveBoardAdapter: ({
    branchSnapshot,
    onMoveIntent,
    onReset,
    label,
  }: {
    branchSnapshot: BranchSnapshot;
    onMoveIntent: (intent: InteractiveBoardMoveIntent) => boolean;
    onReset: () => void;
    label: string;
  }) => {
    return (
      <section data-testid="interactive-board-adapter">
        <div role="img" aria-label={label} data-testid="interactive-board" />
        <p data-testid="branch-san">
          {branchSnapshot.moves.length > 0 ? "1. e4" : "No branch moves yet"}
        </p>
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
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={successfulLookup()} analysisClient={client} />);

    await loadGame(user);
    await screen.findByText("Ply 0 of 3");
    await user.click(screen.getByTestId("branch-test-move"));

    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. e4");
    expect(screen.getByText("Ply 0 of 3")).toBeVisible();
    expect(screen.getByText("Initial position")).toBeVisible();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    await waitFor(() =>
      expect(client.observe).toHaveBeenCalledWith(BRANCH_FEN, expect.any(AbortSignal)),
    );
    expect(client.enqueue).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Reset branch" }));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  it("deliberately analyzes only the currently displayed branch FEN", async () => {
    const client = analysisClient();
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={successfulLookup()} analysisClient={client} />);

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

  it("discards a branch immediately when replacement loading starts", async () => {
    let calls = 0;
    const lookup: GameLookup = vi.fn(async (_uuid, initialPly) => {
      calls += 1;
      return calls === 1
        ? { status: "success" as const, game: { ...VIEWER_GAME, initial_ply: initialPly ?? 0 } }
        : { status: "game_unavailable" as const };
    });
    const user = userEvent.setup();
    render(<ViewerWorkspace lookup={lookup} analysisClient={analysisClient()} />);

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
