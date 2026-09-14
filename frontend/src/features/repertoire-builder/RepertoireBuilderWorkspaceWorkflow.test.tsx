import userEvent from "@testing-library/user-event";
import "./RepertoireBuilderWorkspace.testSetup";
import { cleanup, fireEvent, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { createTestQueryClient } from "../../test-utils/QueryClientTestProvider";
import {
  GAME_DETAIL,
  GAME_UUID,
  renderWorkspace,
  testClients,
  STARTING_FEN,
  AFTER_E4_FEN,
  AFTER_D4_FEN,
} from "./repertoireBuilderTestHelpers";
import type { GameDetailClient } from "./RepertoireBuilderWorkspace";

afterEach(() => cleanup());

function successfulGameClient(detail = GAME_DETAIL) {
  return vi.fn<GameDetailClient>().mockResolvedValue({ data: detail, error: undefined });
}

async function load(
  detail = GAME_DETAIL,
  options: {
    preferredMoveClient?: ReturnType<typeof testClients>["preferredMoveClient"];
    queryClient?: ReturnType<typeof createTestQueryClient>;
  } = {},
) {
  const user = userEvent.setup();
  const { queryClient, ...workspaceOptions } = options;
  renderWorkspace({ gameClient: successfulGameClient(detail), ...workspaceOptions }, queryClient);
  fireEvent.change(screen.getByLabelText("Game UUID"), { target: { value: GAME_UUID } });
  await user.click(screen.getByRole("button", { name: "Load game" }));
  await waitFor(() =>
    expect(
      within(screen.getByTestId("board-move-history")).getByRole("button", {
        name: "White, move 1, e4",
      }),
    ).toBeVisible(),
  );
  return user;
}

describe("RepertoireBuilderWorkspace workflow", () => {
  it("uses the imported trainer transition parent for explicit Preferred Move save", async () => {
    const clients = testClients();
    const user = await load(GAME_DETAIL, { preferredMoveClient: clients.preferredMoveClient });

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("selected-move")).toHaveTextContent("e4");
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Save e4" }));
    await waitFor(() => expect(clients.preferredMoveClient.put).toHaveBeenCalledOnce());
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "e2e4" },
      { signal: expect.any(AbortSignal) },
    );
    await waitFor(() =>
      expect(clients.preferredMoveClient.get).toHaveBeenLastCalledWith(STARTING_FEN, {
        signal: expect.any(AbortSignal),
      }),
    );
    await waitFor(() =>
      expect(screen.getByTestId("saved-move")).toHaveTextContent("e4"),
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
  });

  it("invalidates only the preferred and related read families after a successful save", async () => {
    const clients = testClients();
    const queryClient = createTestQueryClient();
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries");
    const user = userEvent.setup();
    renderWorkspace({ preferredMoveClient: clients.preferredMoveClient }, queryClient);

    await user.click(screen.getByTestId("move-e2-e4"));
    await user.click(screen.getByRole("button", { name: "Save e4" }));
    await waitFor(() =>
      expect(screen.getByTestId("branch-status")).toHaveTextContent("Preferred move saved."),
    );

    expect(invalidateQueries).toHaveBeenCalledTimes(3);
    expect(invalidateQueries.mock.calls.map(([filters]) => filters.queryKey[0])).toEqual([
      "preferredMove",
      "trainingRequirements",
      "positionInsight",
    ]);
  });

  it("uses the same parent transition for a manually played trainer move", async () => {
    const clients = testClients();
    const user = userEvent.setup();
    renderWorkspace({ preferredMoveClient: clients.preferredMoveClient });

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("selected-move")).toHaveTextContent("e4");
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Save e4" }));
    await waitFor(() =>
      expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
        { fen: STARTING_FEN, move_uci: "e2e4" },
        { signal: expect.any(AbortSignal) },
      ),
    );
  });

  it("excludes an opponent transition from Preferred Move candidates", async () => {
    const clients = testClients();
    const user = await load(
      { ...GAME_DETAIL, trainer_color: "black" },
      { preferredMoveClient: clients.preferredMoveClient },
    );

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("selected-move")).toHaveTextContent("No move selected");
    expect(screen.queryByRole("button", { name: /Save/ })).not.toBeInTheDocument();
    await waitFor(() =>
      expect(clients.preferredMoveClient.get).toHaveBeenLastCalledWith(AFTER_E4_FEN, {
        signal: expect.any(AbortSignal),
      }),
    );
  });

  it("derives a branch trainer transition from its branch parent and saves explicitly", async () => {
    const clients = testClients();
    renderWorkspace({ preferredMoveClient: clients.preferredMoveClient });
    const user = userEvent.setup();

    await user.click(screen.getByTestId("move-d2-d4"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_D4_FEN);
    expect(screen.getByTestId("selected-move")).toHaveTextContent("d4");
    await user.click(screen.getByRole("button", { name: "Save d4" }));
    await waitFor(() =>
      expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
        { fen: STARTING_FEN, move_uci: "d2d4" },
        { signal: expect.any(AbortSignal) },
      ),
    );
  });

  it("keeps Remove explicit and preserves saved state until the mutation succeeds", async () => {
    const clients = testClients("assigned");
    const user = userEvent.setup();
    renderWorkspace({ preferredMoveClient: clients.preferredMoveClient });
    await waitFor(() => expect(screen.getByTestId("saved-move")).toHaveTextContent("e4"));

    await user.click(screen.getByRole("button", { name: "Remove" }));
    const dialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Remove" }));
    const openDialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    await user.click(within(openDialog).getByRole("button", { name: "Remove" }));
    await waitFor(() =>
      expect(clients.preferredMoveClient.remove).toHaveBeenCalledWith(
        { fen: STARTING_FEN },
        { signal: expect.any(AbortSignal) },
      ),
    );
    await waitFor(() =>
      expect(clients.preferredMoveClient.get).toHaveBeenLastCalledWith(STARTING_FEN, {
        signal: expect.any(AbortSignal),
      }),
    );
    await waitFor(() => expect(screen.getByTestId("saved-move")).toHaveTextContent("None yet"));
  });

  it("retains the selected transition when an explicit save fails", async () => {
    const clients = testClients();
    clients.preferredMoveClient.put = vi.fn(async () => ({
      status: "unexpected_failure" as const,
    }));
    const user = userEvent.setup();
    renderWorkspace({ preferredMoveClient: clients.preferredMoveClient });
    await user.click(screen.getByTestId("move-e2-e4"));
    await user.click(screen.getByRole("button", { name: "Save e4" }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(
        "The preferred move could not be updated.",
      ),
    );
    expect(screen.getByTestId("selected-move")).toHaveTextContent("e4");
  });

  it("saves a legal parent transition when corpus observation is absent", async () => {
    const clients = testClients();
    clients.positionContextClient.mockImplementation(async (fen, trainerColor) => ({
      status: "success" as const,
      data: {
        fen,
        trainerColor,
        observedInGames: false,
        distinctGameCount: 0,
        totalGameCount: 0,
      },
    }));
    const user = userEvent.setup();
    renderWorkspace({
      preferredMoveClient: clients.preferredMoveClient,
      positionContextClient: clients.positionContextClient,
    });

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByRole("button", { name: "Save e4" })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Save e4" }));

    await waitFor(() =>
      expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
        { fen: STARTING_FEN, move_uci: "e2e4" },
        { signal: expect.any(AbortSignal) },
      ),
    );
    await waitFor(() =>
      expect(screen.getByTestId("branch-status")).toHaveTextContent("Preferred move saved."),
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
  });
});
