import * as axe from "axe-core";
import userEvent from "@testing-library/user-event";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type { ComponentProps } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import axeMatchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";

import type { AnalysisClient } from "../viewer/analysisApi";
import type { GameLookupResult } from "../viewer/positionApi";
import type { PositionContextClient } from "../viewer/positionContextApi";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import type {
  PreferredMoveClient,
  PreferredMoveMutationResult,
  PreferredMoveResponse,
} from "./preferredMoveApi";
import RepertoireBuilderWorkspace from "./RepertoireBuilderWorkspace";

vi.mock("react-chessboard", () => ({
  defaultPieces: Object.fromEntries(
    ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"].map((pieceType) => [
      pieceType,
      () => <svg data-default-piece={pieceType} />,
    ]),
  ),
  Chessboard: ({
    options,
  }: {
    options: {
      position: string;
      pieces: Record<string, (props?: { square?: string }) => React.JSX.Element>;
      onPieceDrop: (args: { sourceSquare: string; targetSquare: string | null }) => boolean;
    };
  }) => (
    <div data-testid="mock-chessboard" data-position={options.position}>
      {[
        ["e2", "e4", "wP"],
        ["e7", "e5", "bP"],
        ["g8", "f6", "bN"],
        ["e7", "e8", "wP"],
        ["e2", "e5", "wP"],
        ["d2", "d4", "wP"],
      ].map(([source, target, pieceType]) => (
        <button
          key={`${source}-${target}-${pieceType}`}
          type="button"
          data-testid={`move-${source}-${target}`}
          data-square={source}
          aria-roledescription="draggable"
          aria-label={`Move ${source} to ${target}`}
          onClick={() => options.onPieceDrop({ sourceSquare: source, targetSquare: target })}
        >
          {options.pieces[pieceType]?.({ square: source })}
        </button>
      ))}
    </div>
  ),
}));

expect.extend(axeMatchers);
afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

const BOARD_LABEL = "Chess board: standard starting position, White at the bottom";
const STORED_BOARD_LABEL = `Chess board: game ${VIEWER_GAME_UUID}, ply 2, Black at the bottom`;
const STARTING_FEN = VIEWER_GAME.positions[0].fen;
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";
const CONTEXT = {
  overall_exists: true,
  white_count: 0,
  black_count: 0,
};

function noAnalysisClient(): AnalysisClient {
  return {
    observe: vi.fn(async (fen: string) => ({
      status: "success" as const,
      data: { fen, eligibility: "missing" as const, result: null, status: null, terminal: false },
    })),
    enqueue: vi.fn() as AnalysisClient["enqueue"],
    status: vi.fn() as AnalysisClient["status"],
  };
}

function completedAnalysisClient(): AnalysisClient {
  return {
    observe: vi.fn(async (fen: string) => ({
      status: "success" as const,
      data: {
        fen,
        eligibility: "eligible" as const,
        result: {
          fen,
          profile_id: "test-profile",
          candidates: [
            {
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
            },
          ],
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
    })),
    enqueue: vi.fn() as AnalysisClient["enqueue"],
    status: vi.fn() as AnalysisClient["status"],
  };
}

function preferredMoveResponse(
  fen: string,
  state: PreferredMoveResponse["state"] = "unassigned",
): PreferredMoveResponse {
  return {
    fen,
    state,
    move: state === "assigned" ? { uci: "e2e4", san: "e4" } : null,
  };
}

function mutationResponse(fen: string): PreferredMoveMutationResult {
  return {
    status: "success",
    data: { fen, changed: true, effective_at: "2026-01-01T00:00:00.000000Z" },
  };
}

function testClients(initialState: PreferredMoveResponse["state"] = "unassigned") {
  let state = initialState;
  const preferredMoveClient: PreferredMoveClient = {
    get: vi.fn(async (fen) => ({
      status: "success" as const,
      data: preferredMoveResponse(fen, state),
    })),
    put: vi.fn(async ({ fen }) => {
      state = "assigned";
      return mutationResponse(fen);
    }),
    remove: vi.fn(async ({ fen }) => {
      state = "unassigned";
      return mutationResponse(fen);
    }),
  };
  const positionContextClient: PositionContextClient = vi.fn(async (fen) => ({
    status: "success" as const,
    data: { fen, ...CONTEXT },
  }));
  return { preferredMoveClient, positionContextClient };
}

function renderWorkspace(
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

function sharedPositionSummary(): HTMLElement {
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

describe("RepertoireBuilderWorkspace", () => {
  it("renders the standard starting position with White at the bottom", () => {
    const { container } = renderWorkspace();

    expect(screen.getByRole("heading", { name: "Repertoire Builder", level: 1 })).toBeVisible();
    const board = screen.getByRole("group", { name: BOARD_LABEL });
    expect(board).toBeVisible();
    expect(screen.getByTestId("session-origin")).toHaveTextContent(
      "Standard starting position; local session begins at Ply 0. Current Ply 0.",
    );
    const descriptionRow = screen.getByTestId("position-description-row");
    expect(board.contains(descriptionRow)).toBe(false);
    expect(descriptionRow.parentElement).toBe(container.querySelector('[class*="workspace"]'));
    expect(descriptionRow.className).toMatch(/positionDescription/);
    const description = screen.getByRole("button", { name: "Position description" });
    expect(description).toHaveAttribute("aria-expanded", "false");
    fireEvent.click(description);
    expect(sharedPositionSummary()).toHaveTextContent("OrientationWhite at the bottom");
    description.focus();
    expect(description).toHaveFocus();
  });

  it("loads a stored game with the complete prefix through the selected Ply and subject orientation", async () => {
    const lookup = vi.fn().mockResolvedValue({
      status: "success",
      game: { ...VIEWER_GAME, initial_ply: 2, subject_color: "black" },
    });
    const user = userEvent.setup();
    renderWorkspace({ lookup });

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.type(screen.getByLabelText(/Ply/), "2");
    await user.click(screen.getByRole("button", { name: "Load game" }));

    await waitFor(() =>
      expect(screen.getByRole("group", { name: STORED_BOARD_LABEL })).toBeVisible(),
    );
    expect(lookup).toHaveBeenCalledWith(VIEWER_GAME_UUID, 2, expect.any(AbortSignal));
    expect(screen.getByTestId("session-origin")).toHaveTextContent(
      `Game ${VIEWER_GAME_UUID}; complete prefix through Ply 2. Current Ply 2.`,
    );
    expect(screen.getByTestId("session-san-history")).toHaveTextContent("1. e4 1... e5");
    expect(sharedPositionSummary()).toHaveTextContent("OrientationBlack at the bottom");
  });

  it("exposes loading state while a stored game request is pending", async () => {
    let resolveLookup!: (result: GameLookupResult) => void;
    const lookup = vi.fn(
      () =>
        new Promise<GameLookupResult>((resolve) => {
          resolveLookup = resolve;
        }),
    );
    const user = userEvent.setup();
    renderWorkspace({ lookup });

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(screen.getByText("Loading the complete game...")).toBeVisible();
    expect(screen.getByRole("button", { name: "Load game" })).toBeDisabled();

    resolveLookup({ status: "success", game: VIEWER_GAME });
    await waitFor(() => expect(screen.getByRole("button", { name: "Load game" })).toBeEnabled());
    expect(
      screen.getByRole("group", {
        name: `Chess board: game ${VIEWER_GAME_UUID}, ply 0, White at the bottom`,
      }),
    ).toBeVisible();
  });

  it("keeps the current session safe when loading fails and Reset returns to standard start", async () => {
    const lookup = vi.fn().mockResolvedValue({ status: "game_not_found" as const });
    const user = userEvent.setup();
    renderWorkspace({ lookup });

    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));

    expect(await screen.findByText("Game not found")).toBeVisible();
    expect(screen.getByRole("group", { name: BOARD_LABEL })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByLabelText("Game UUID")).toHaveValue("");
    expect(screen.getByLabelText(/Ply/)).toHaveValue("");
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Standard starting position");
    expect(screen.queryByText("Game not found")).not.toBeInTheDocument();
  });

  it("stages my moves, cancels staging on Flip, and advances an opposing move locally", async () => {
    const user = userEvent.setup();
    renderWorkspace();

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(1);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(0);
    const session = screen.getByTestId("repertoire-session");
    const status = within(session).getByTestId("session-status");
    expect(status).toHaveTextContent("My move staged: e4.");
    expect(status).toHaveAttribute("role", "status");
    expect(status).toHaveAttribute("aria-live", "polite");
    expect(within(session).getByTestId("session-san-history")).toBeVisible();
    expect(within(session).getByRole("heading", { name: "Preferred move" })).toBeVisible();
    expect(screen.getAllByText("My move staged: e4.", { exact: true })).toHaveLength(1);

    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(screen.getByTestId("session-status")).toHaveTextContent(
      "Flipped to Black at the bottom.",
    );
    expect(sharedPositionSummary()).toHaveTextContent("OrientationBlack at the bottom");
    expect(sharedPositionSummary()).toHaveTextContent("Side to moveWhite");

    await user.click(screen.getByTestId("move-e2-e4"));
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(sharedPositionSummary().querySelector('[data-position-side="b"]')).toHaveAttribute(
      "data-position-side-to-move",
      "true",
    );
    expect(screen.getByTestId("session-san-history")).toHaveTextContent("1. e4");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(screen.getByRole("button", { name: "Previous" })).toBeEnabled();
  });

  it("adds a staged move only after explicit Add and sends blank effective-now date", async () => {
    const user = userEvent.setup();
    const clients = testClients();
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByText("Never seen as White")).toBeVisible());
    await user.click(screen.getByTestId("move-e2-e4"));
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Add" }));
    await waitFor(() => expect(clients.preferredMoveClient.put).toHaveBeenCalledTimes(1));
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "e2e4", effective_at: "" },
      { signal: expect.any(AbortSignal) },
    );
    expect(screen.getByRole("button", { name: "Effective date: Choose date" })).toBeVisible();
  });

  it("edits a saved move and saves one staged replacement explicitly", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByTestId("saved-move")).toHaveTextContent("e4"));
    await user.click(screen.getByRole("button", { name: "Edit" }));
    await user.click(screen.getByTestId("move-d2-d4"));
    expect(screen.getByTestId("replacement-move")).toHaveTextContent("d4");
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Save replacement" }));
    await waitFor(() => expect(clients.preferredMoveClient.put).toHaveBeenCalledTimes(1));
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "d2d4", effective_at: "" },
      { signal: expect.any(AbortSignal) },
    );
  });

  it("plays the saved move through the local W1 path without a mutation", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Play saved move" }));

    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(screen.getByTestId("session-san-history")).toHaveTextContent("1. e4");
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();
  });

  it("requires confirmation before Remove and only clears the saved move after success", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Remove" }));
    const dialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();
    expect(screen.getByTestId("saved-move")).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Remove" }));
    const openDialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    await user.click(within(openDialog).getByRole("button", { name: "Remove" }));
    await waitFor(() => expect(clients.preferredMoveClient.remove).toHaveBeenCalledTimes(1));
    expect(clients.preferredMoveClient.remove).toHaveBeenCalledWith(
      { fen: STARTING_FEN, effective_at: "" },
      { signal: expect.any(AbortSignal) },
    );
    await waitFor(() => expect(screen.queryByTestId("saved-move")).not.toBeInTheDocument());
  });

  it("uses UTC-midnight for a selected date and clears it only after success", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.setSystemTime(new Date("2026-01-15T23:59:59.999Z"));
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const clients = testClients();
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByText("Never seen as White")).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Effective date: Choose date" }));
    const calendar = await screen.findByRole("dialog", { name: "Effective date" });
    await user.click(within(calendar).getByRole("button", { name: /January 10th, 2026/ }));
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-10" })).toBeVisible();

    await user.click(screen.getByTestId("move-e2-e4"));
    await user.click(screen.getByRole("button", { name: "Add" }));
    await waitFor(() => expect(clients.preferredMoveClient.put).toHaveBeenCalledTimes(1));
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "e2e4", effective_at: "2026-01-10T00:00:00.000Z" },
      { signal: expect.any(AbortSignal) },
    );
    expect(screen.getByRole("button", { name: "Effective date: Choose date" })).toBeVisible();
  });

  it("retains the staged move and date when a mutation fails", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.setSystemTime(new Date("2026-01-15T23:59:59.999Z"));
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const clients = testClients();
    clients.preferredMoveClient.put = vi.fn(async () => ({
      status: "future_effective_time" as const,
    }));
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByText("Never seen as White")).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Effective date: Choose date" }));
    const calendar = await screen.findByRole("dialog", { name: "Effective date" });
    await user.click(within(calendar).getByRole("button", { name: /January 10th, 2026/ }));
    await user.click(screen.getByTestId("move-e2-e4"));
    await user.click(screen.getByRole("button", { name: "Add" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "The selected date cannot be in the future.",
    );
    expect(screen.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");
    expect(screen.getAllByText("My move staged: e4.", { exact: true })).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-10" })).toBeVisible();
  });

  it("activates a displayed Best candidate through the same local move path", async () => {
    const user = userEvent.setup();
    const client = completedAnalysisClient();
    renderWorkspace({ analysisClient: client });

    await user.click(screen.getByRole("button", { name: "Flip" }));
    const candidate = await screen.findByRole("button", { name: "1. e4" });
    await user.click(candidate);

    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(screen.getByTestId("session-san-history")).toHaveTextContent("1. e4");
    expect(client.enqueue).not.toHaveBeenCalled();
  });

  it("keeps local controls only and does not expose chess Undo or Reset actions", () => {
    renderWorkspace();

    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Flip" })).toBeEnabled();
    expect(screen.queryByRole("button", { name: "Undo" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Reset branch" })).not.toBeInTheDocument();
  });

  it("passes a focused accessibility check", async () => {
    const { container } = renderWorkspace();
    const session = screen.getByTestId("repertoire-session");

    expect(within(session).getByTestId("session-san-history")).toBeVisible();
    expect(within(session).getByTestId("session-status")).toHaveAttribute("aria-live", "polite");
    expect(within(session).getByRole("heading", { name: "Preferred move" })).toBeVisible();

    expect(await axe.run(container)).toHaveNoViolations();
  });
});
