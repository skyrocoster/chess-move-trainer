import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useEffect, useRef, useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { AnalysisClient } from "./analysisApi";
import ViewerWorkspace from "./ViewerWorkspace";
import type { GameLookup } from "./positionApi";
import { STAGE1_GAME, STAGE1_GAME_UUID } from "./stage1GameTypes";

const BRANCH_FEN = STAGE1_GAME.positions[1].fen;

vi.mock("../board-adapter/InteractiveBoardAdapter", () => ({
  InteractiveBoardAdapter: ({
    viewKey,
    originFen,
    originPly,
    resetToken = 0,
    onBranchChange,
    label,
  }: {
    viewKey: string;
    originFen: string;
    originPly: number;
    resetToken?: number;
    onBranchChange?: (snapshot: {
      viewKey: string;
      resetToken: number;
      originFen: string;
      currentFen: string;
      originPly: number;
      moves: readonly { color: "w"; from: string; to: string; san: string }[];
      active: boolean;
    }) => void;
    label: string;
  }) => {
    const [active, setActive] = useState(false);
    const previousResetToken = useRef(resetToken);
    useEffect(() => {
      if (previousResetToken.current === resetToken) {
        return;
      }
      previousResetToken.current = resetToken;
      setActive(false);
      onBranchChange?.({
        viewKey,
        resetToken,
        originFen,
        currentFen: originFen,
        originPly,
        moves: [],
        active: false,
      });
    }, [onBranchChange, originFen, originPly, resetToken, viewKey]);

    function startBranch() {
      setActive(true);
      onBranchChange?.({
        viewKey,
        resetToken,
        originFen,
        currentFen: BRANCH_FEN,
        originPly,
        moves: [{ color: "w", from: "e2", to: "e4", san: "e4" }],
        active: true,
      });
    }

    function resetBranch() {
      setActive(false);
      onBranchChange?.({
        viewKey,
        resetToken,
        originFen,
        currentFen: originFen,
        originPly,
        moves: [],
        active: false,
      });
    }

    return (
      <section data-testid="interactive-board-adapter">
        <div role="img" aria-label={label} data-testid="interactive-board" />
        <p data-testid="branch-san">{active ? "1. e4" : "No branch moves yet"}</p>
        <button type="button" data-testid="branch-test-move" onClick={startBranch}>
          Start test branch
        </button>
        <button type="button" onClick={resetBranch}>
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
    game: { ...STAGE1_GAME, initial_ply: initialPly ?? 0 },
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
  await user.type(screen.getByLabelText("Game UUID"), STAGE1_GAME_UUID);
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
        ? { status: "success" as const, game: { ...STAGE1_GAME, initial_ply: initialPly ?? 0 } }
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
