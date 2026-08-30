import * as axe from "axe-core";
import userEvent from "@testing-library/user-event";
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import axeMatchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import type { PreferredMoveClient } from "./preferredMoveApi";
import { PROMOTION_GAME } from "../viewer/viewerStoryFixtures";
import { VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import {
  AFTER_E4_FEN,
  AFTER_E8_KNIGHT_FEN,
  displayAnalysisClient,
  renderWorkspace,
  sharedPositionSummary,
  STARTING_FEN,
  testClients,
  type DisplayState,
} from "./repertoireBuilderTestHelpers";

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
      squareStyles?: Record<string, React.CSSProperties>;
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
      {["e2", "e4", "e7", "e5", "e8", "d2", "d4"].map((square) => (
        <span
          key={`square-${square}`}
          data-testid={`board-square-${square}`}
          data-highlighted={options.squareStyles?.[square] ? "true" : "false"}
        />
      ))}
    </div>
  ),
}));

expect.extend(axeMatchers);
afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

function historyEntry(name: string) {
  return within(screen.getByTestId("session-move-history")).getByRole("button", { name });
}

describe("RepertoireBuilderWorkspace workflow", () => {
  it("plays a saved promotion move selected on the board without staging", async () => {
    const user = userEvent.setup();
    const lookup = vi.fn().mockResolvedValue({ status: "success", game: PROMOTION_GAME });
    const preferredMoveClient: PreferredMoveClient = {
      get: vi.fn(async (fen) => ({
        status: "success" as const,
        data: {
          fen,
          state: "assigned" as const,
          move: { uci: "e7e8n", san: "e8=N" },
          effective_at: "2026-01-01T00:00:00.000000Z",
        },
      })),
      put: vi.fn(),
      remove: vi.fn(),
    };
    renderWorkspace({ lookup, preferredMoveClient });
    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByTestId("move-e7-e8"));
    const dialog = await screen.findByRole("dialog", { name: "Choose a promotion piece" });
    await user.click(within(dialog).getByRole("button", { name: "Promote to knight" }));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute(
      "data-position",
      AFTER_E8_KNIGHT_FEN,
    );
    expect(historyEntry("White, move 1, e8=N")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("session-status")).toHaveTextContent(
      "Saved move played locally: e8=N.",
    );
    expect(preferredMoveClient.put).not.toHaveBeenCalled();
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
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-10" })).toBeVisible();
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
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "e2e4", effective_at: "2026-01-10T00:00:00.000Z" },
      { signal: expect.any(AbortSignal) },
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
    expect(screen.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");
    expect(screen.getAllByText("My move staged: e4.", { exact: true })).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-10" })).toBeVisible();
  });

  it("activates a displayed Best candidate through the same local move path", async () => {
    const user = userEvent.setup();
    const client = displayAnalysisClient("completed-cp");
    renderWorkspace({ analysisClient: client });
    await user.click(screen.getByRole("button", { name: "Flip" }));
    const candidate = await screen.findByRole("button", { name: "1. e4" });
    await user.click(candidate);

    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(historyEntry("White, move 1, e4")).toHaveAttribute("aria-current", "step");
    expect(client.enqueue).not.toHaveBeenCalled();
  });

  it.each([
    ["neutral", "neutral", "50", "0.00", "No analysis yet; evaluation neutral."],
    ["completed CP", "best-line", "51.7", "+0.34", "best-line evaluation +0.34."],
    ["mate", "best-line", "0", "-M3", "best-line evaluation -M3."],
    ["pending", "pending", "50", "0.00", "Analysis queued; evaluation pending."],
    ["stale retained", "best-line", "51.7", "+0.34", "Stale best-line evaluation +0.34."],
    ["failed retained", "best-line", "51.7", "+0.34", "Stale best-line evaluation +0.34."],
    ["failed without candidate", "neutral", "50", "0.00", "Analysis failed; evaluation neutral."],
    ["unavailable", "neutral", "50", "0.00", "Evaluation unavailable; evaluation neutral."],
  ])(
    "renders %s display semantics through the Workspace evaluation rail",
    async (name, expectedState, expectedValue, shortValue, accessibleValue) => {
      const state =
        name === "completed CP"
          ? "completed-cp"
          : name === "failed without candidate"
            ? "failed-empty"
            : (name.replaceAll(" ", "-") as DisplayState);
      renderWorkspace({
        analysisClient: displayAnalysisClient(state),
        analysisPollIntervalMs: 60_000,
      });
      const meter = screen.getByRole("meter", { name: "Evaluation" });
      await waitFor(() => {
        expect(meter).toHaveAttribute("data-state", expectedState);
        expect(meter).toHaveAttribute("aria-valuenow", expectedValue);
        expect(meter).toHaveAttribute("aria-valuetext", accessibleValue);
        expect(meter).toHaveTextContent(shortValue);
      });
    },
  );

  it("flips rail orientation and fill direction without changing the evaluated score", async () => {
    const user = userEvent.setup();
    const analysisClient = displayAnalysisClient("completed-cp");
    renderWorkspace({ analysisClient });
    const meter = screen.getByRole("meter", { name: "Evaluation" });
    const indicator = meter.querySelector('[class*="indicator"]');
    if (!(indicator instanceof HTMLElement)) {
      throw new Error("The evaluation indicator is missing.");
    }

    await waitFor(() => {
      expect(analysisClient.observe).toHaveBeenCalledWith(STARTING_FEN, expect.any(AbortSignal));
      expect(meter).toHaveAttribute("data-orientation", "white");
      expect(meter).toHaveAttribute("aria-valuenow", "51.7");
      expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34.");
      expect(indicator).toHaveStyle({ height: "51.7%" });
    });

    await user.click(screen.getByRole("button", { name: "Flip" }));

    expect(meter).toHaveAttribute("data-orientation", "black");
    expect(meter).toHaveAttribute("aria-valuenow", "51.7");
    expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34.");
    expect(indicator).toHaveStyle({ height: "51.7%" });
    expect(analysisClient.observe).not.toHaveBeenCalledWith(AFTER_E4_FEN, expect.any(AbortSignal));
  });

  it("observes the staged displayed FEN separately while keeping analysis and workflow on the parent", async () => {
    const user = userEvent.setup();
    const sourceAnalysisClient = displayAnalysisClient("dual");
    const sourceObserve = sourceAnalysisClient.observe;
    const analysisClient = {
      ...sourceAnalysisClient,
      observe: vi.fn(async (fen: string, signal?: AbortSignal) => {
        const result = await sourceObserve(fen, signal);
        if (fen !== AFTER_E4_FEN || result.status !== "success" || result.data.result === null) {
          return result;
        }
        const candidate = result.data.result.candidates[0];
        if (!candidate) {
          return result;
        }
        return {
          ...result,
          data: {
            ...result.data,
            result: {
              ...result.data.result,
              candidates: [{ ...candidate, pv_uci: ["e7e5"] }],
            },
          },
        };
      }),
    };
    const clients = testClients();
    renderWorkspace({
      analysisClient,
      preferredMoveClient: clients.preferredMoveClient,
      positionContextClient: clients.positionContextClient,
    });
    await waitFor(() =>
      expect(analysisClient.observe).toHaveBeenCalledWith(STARTING_FEN, expect.any(AbortSignal)),
    );
    const meter = screen.getByRole("meter", { name: "Evaluation" });
    await waitFor(() =>
      expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34."),
    );
    await user.click(screen.getByTestId("move-e2-e4"));
    await waitFor(() =>
      expect(analysisClient.observe).toHaveBeenCalledWith(AFTER_E4_FEN, expect.any(AbortSignal)),
    );
    await waitFor(() => {
      expect(meter).toHaveAttribute("aria-valuenow", "48.3");
      expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation -0.34.");
    });
    expect(screen.getByRole("button", { name: "1. e4" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "1... e5" })).not.toBeInTheDocument();
    expect(clients.preferredMoveClient.get).toHaveBeenCalledWith(STARTING_FEN, {
      signal: expect.any(AbortSignal),
    });
    expect(clients.preferredMoveClient.get).not.toHaveBeenCalledWith(AFTER_E4_FEN, {
      signal: expect.any(AbortSignal),
    });
    expect(clients.positionContextClient).toHaveBeenCalledWith(
      STARTING_FEN,
      expect.any(AbortSignal),
    );
    expect(clients.positionContextClient).not.toHaveBeenCalledWith(
      AFTER_E4_FEN,
      expect.any(AbortSignal),
    );
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();
    expect(analysisClient.enqueue).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(meter).toHaveAttribute("data-orientation", "black");
    expect(meter).toHaveAttribute("aria-valuenow", "51.7");
    expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34.");
    expect(meter).toHaveTextContent("+0.34");
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

    expect(within(session).getByTestId("session-move-history")).toBeVisible();
    expect(within(session).getByTestId("session-status")).toHaveAttribute("aria-live", "polite");
    expect(within(session).getByRole("heading", { name: "Preferred move" })).toBeVisible();

    expect(await axe.run(container)).toHaveNoViolations();
  });
});
