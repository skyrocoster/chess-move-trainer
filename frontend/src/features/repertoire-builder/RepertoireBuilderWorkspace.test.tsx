import userEvent from "@testing-library/user-event";
import "./RepertoireBuilderWorkspace.testSetup";
import { cleanup, fireEvent, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { AnalysisClient, AnalysisObservation, AnalysisOperationResult } from "../analysis/analysisApi";
import { GAME_DETAIL, GAME_UUID, renderWorkspace, testClients, STARTING_FEN, AFTER_E4_FEN, AFTER_E5_FEN, AFTER_D4_FEN, AFTER_NF3_FEN } from "./repertoireBuilderTestHelpers";
import type { GameDetailClient } from "./RepertoireBuilderWorkspace";

afterEach(() => cleanup());

function historyEntry(name: string) {
  return within(screen.getByTestId("board-move-history")).getByRole("button", { name });
}

function successfulGameClient() {
  return vi.fn<GameDetailClient>().mockResolvedValue({ data: GAME_DETAIL, error: undefined });
}

function cleanAnalysisClient(): AnalysisClient {
  let requested = false;
  const result = {
    lines: [
      {
        rank: 1,
        score_kind: "cp" as const,
        score_value: 34,
        wdl_wins: 420,
        wdl_draws: 300,
        wdl_losses: 280,
        pv_uci: ["e2e4"],
        depth: 20,
      },
    ],
    terminal_kind: null,
  };
  const observation = (fen: string): AnalysisObservation => ({
    fen,
    state: requested ? "ready" : "not_requested",
    result: requested ? result : null,
  });
  const success = (fen: string): AnalysisOperationResult<AnalysisObservation> => ({
    status: "success",
    data: observation(fen),
  });

  return {
    observe: vi.fn(async (fen: string) => success(fen)),
    request: vi.fn(async (fen: string) => {
      requested = true;
      return success(fen);
    }),
  };
}

async function loadGame(
  gameClient: GameDetailClient = successfulGameClient(),
  clients = testClients(),
) {
  const user = userEvent.setup();
  renderWorkspace({ gameClient, ...clients });
  fireEvent.change(screen.getByLabelText("Game UUID"), { target: { value: GAME_UUID } });
  await user.click(screen.getByRole("button", { name: "Load game" }));
  await waitFor(() => expect(screen.getByTestId("session-origin")).toHaveTextContent("complete game loaded"));
  return user;
}

describe("RepertoireBuilderWorkspace", () => {
  it("observes the selected FEN without requesting work until Analyze is deliberate", async () => {
    const analysisClient = cleanAnalysisClient();
    const user = userEvent.setup();
    renderWorkspace({ analysisClient });

    await waitFor(() => expect(analysisClient.observe).toHaveBeenCalledWith(STARTING_FEN, expect.any(AbortSignal)));
    expect(analysisClient.request).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Analyze position" }));
    await waitFor(() => expect(analysisClient.request).toHaveBeenCalledWith(STARTING_FEN, expect.any(AbortSignal)));

    const candidate = await screen.findByRole("button", { name: "1. e4" });
    await user.click(candidate);
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    await waitFor(() => expect(analysisClient.observe).toHaveBeenCalledWith(AFTER_E4_FEN, expect.any(AbortSignal)));
  });

  it("starts fresh at one selected standard-start position", async () => {
    const clients = testClients();
    renderWorkspace(clients);

    expect(screen.getByTestId("session-origin")).toHaveTextContent(
      "Standard starting position; local session begins at Ply 0. Current Ply 0.",
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    await waitFor(() =>
      expect(clients.positionContextClient).toHaveBeenCalledWith(
        STARTING_FEN,
        "white",
        expect.any(AbortSignal),
      ),
    );
    expect(screen.queryByLabelText(/Ply/)).not.toBeInTheDocument();
    expect(screen.queryByTestId("staged-move")).not.toBeInTheDocument();
  });

  it("loads the complete clean game through getGame at Ply 0", async () => {
    const gameClient = successfulGameClient();
    await loadGame(gameClient);

    expect(gameClient).toHaveBeenCalledWith({
      path: { game_uuid: GAME_UUID },
      signal: expect.any(AbortSignal),
    });
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toHaveAttribute("aria-current", "step");
    expect(historyEntry("White, move 1, e4")).toBeVisible();
    expect(historyEntry("Black, move 1, e5")).toBeVisible();
    expect(historyEntry("White, move 2, Nf3")).toBeVisible();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
    expect(screen.queryByLabelText("Ply", { exact: true })).not.toBeInTheDocument();
  });

  it("navigates the complete imported line and keeps every surface on one current FEN", async () => {
    const clients = testClients();
    const user = await loadGame(successfulGameClient(), clients);

    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 1.");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(historyEntry("White, move 1, e4")).toHaveAttribute("aria-current", "step");
    await waitFor(() =>
      expect(clients.positionContextClient).toHaveBeenCalledWith(
        AFTER_E4_FEN,
        "white",
        expect.any(AbortSignal),
      ),
    );
    expect(screen.getByRole("button", { name: "Previous" })).toBeEnabled();

    await user.click(historyEntry("White, move 2, Nf3"));
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 3.");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_NF3_FEN);
    await user.click(historyEntry("Initial position"));
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
  });

  it("advances a recorded UCI move immediately and derives the trainer transition from its parent", async () => {
    const clients = testClients();
    const user = userEvent.setup();
    renderWorkspace(clients);
    await waitFor(() => expect(clients.preferredMoveClient.get).toHaveBeenCalledWith(STARTING_FEN, expect.anything()));

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 1.");
    expect(historyEntry("White, move 1, e4")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("selected-move")).toHaveTextContent("e4");
    expect(screen.getByRole("button", { name: "Save e4" })).toBeVisible();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    await waitFor(() =>
      expect(clients.preferredMoveClient.get).toHaveBeenLastCalledWith(STARTING_FEN, {
        signal: expect.any(AbortSignal),
      }),
    );
  });

  it("creates a branch on divergence, replaces its tail, and returns to the intact game", async () => {
    const user = await loadGame(successfulGameClient());

    await user.click(screen.getByTestId("move-d2-d4"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_D4_FEN);
    expect(historyEntry("White, move 1, d4")).toHaveAttribute("aria-current", "step");
    expect(screen.getByLabelText("Temporary branch")).toBeVisible();
    expect(screen.getByTestId("branch-current-ply")).toHaveTextContent("Current ply 1");

    await user.click(screen.getByTestId("move-e7-e5"));
    expect(historyEntry("Black, move 1, e5")).toHaveAttribute("aria-current", "step");
    await user.click(historyEntry("White, move 1, d4"));
    await user.click(screen.getByTestId("move-g8-f6"));
    expect(historyEntry("Black, move 1, Nf6")).toHaveAttribute("aria-current", "step");
    expect(screen.queryByRole("button", { name: "Black, move 1, e5" })).not.toBeInTheDocument();

    const branch = screen.getByLabelText("Temporary branch");
    await user.click(within(branch).getByRole("button", { name: "Reset" }));
    expect(screen.queryByLabelText("Temporary branch")).not.toBeInTheDocument();
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("White, move 1, e4")).toBeVisible();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  it("resets the session and replaces it with a new loaded game", async () => {
    const user = userEvent.setup();
    const gameClient = successfulGameClient();
    renderWorkspace({ gameClient });
    await user.click(screen.getByTestId("move-e2-e4"));
    const loaderActions = screen.getByRole("button", { name: "Load game" }).parentElement!;
    await user.click(within(loaderActions).getByRole("button", { name: "Reset" }));
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Standard starting position");
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");

    fireEvent.change(screen.getByLabelText("Game UUID"), { target: { value: GAME_UUID } });
    await user.click(screen.getByRole("button", { name: "Load game" }));
    await waitFor(() => expect(screen.getByTestId("session-origin")).toHaveTextContent("complete game loaded"));
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  it("maps clean not-found, unavailable, validation, and unexpected failures without a legacy Ply error", async () => {
    const cases = [
      [{ code: "game_not_found", message: "missing" }, 404, "Game not found"],
      [{ code: "games_unavailable", message: "down" }, 503, "Corpus unavailable"],
      [{ detail: [] }, 422, "Game unavailable"],
      [{ code: "unexpected_failure", message: "bad" }, 500, "Unable to load game"],
    ] as const;

    for (const [error, status, heading] of cases) {
      cleanup();
      const gameClient = vi.fn<GameDetailClient>().mockResolvedValue({
        data: undefined,
        error,
        response: new Response(null, { status }),
      });
      const user = userEvent.setup();
      renderWorkspace({ gameClient });
      fireEvent.change(screen.getByLabelText("Game UUID"), { target: { value: GAME_UUID } });
      await user.click(screen.getByRole("button", { name: "Load game" }));
      expect(await screen.findByText(heading)).toBeVisible();
      expect(screen.queryByText("Position not found")).not.toBeInTheDocument();
    }
  });

  it("aborts a pending clean load when Reset is pressed", async () => {
    let resolve!: (result: Awaited<ReturnType<GameDetailClient>>) => void;
    const gameClient = vi.fn<GameDetailClient>().mockImplementation(
      () => new Promise((done) => (resolve = done)),
    );
    const user = userEvent.setup();
    renderWorkspace({ gameClient });
    fireEvent.change(screen.getByLabelText("Game UUID"), { target: { value: GAME_UUID } });
    await user.click(screen.getByRole("button", { name: "Load game" }));
    const signal = gameClient.mock.calls[0]?.[0].signal;
    expect(screen.getByText("Loading the complete game...")).toBeVisible();
    const loaderActions = screen.getByRole("button", { name: "Load game" }).parentElement!;
    await user.click(within(loaderActions).getByRole("button", { name: "Reset" }));
    expect(signal?.aborted).toBe(true);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Standard starting position");
    resolve({ data: GAME_DETAIL, error: undefined });
  });

  it("keeps the selected position consistent across analysis and move responses", async () => {
    const clients = testClients();
    const user = userEvent.setup();
    renderWorkspace(clients);
    await user.click(screen.getByTestId("move-e2-e4"));

    await waitFor(() =>
      expect(clients.moveResponseDistributionClient).toHaveBeenCalledWith(
        AFTER_E4_FEN,
        "white",
        expect.any(AbortSignal),
      ),
    );
    expect(clients.positionContextClient).toHaveBeenCalledWith(
      AFTER_E4_FEN,
      "white",
      expect.any(AbortSignal),
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 1.");
  });

  it("refetches context for the opposite trainer color when the board flips", async () => {
    const clients = testClients();
    const user = userEvent.setup();
    renderWorkspace(clients);
    await waitFor(() =>
      expect(clients.positionContextClient).toHaveBeenCalledWith(
        STARTING_FEN,
        "white",
        expect.any(AbortSignal),
      ),
    );

    await user.click(screen.getByRole("button", { name: "Flip" }));
    await waitFor(() =>
      expect(clients.positionContextClient).toHaveBeenLastCalledWith(
        STARTING_FEN,
        "black",
        expect.any(AbortSignal),
      ),
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
  });
});
