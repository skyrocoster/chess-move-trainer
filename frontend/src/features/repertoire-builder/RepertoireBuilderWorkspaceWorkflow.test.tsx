import * as axe from "axe-core";
import userEvent from "@testing-library/user-event";
import { cleanup, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import axeMatchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import type {
  PreferredMoveClient,
  PreferredMoveMutationResult,
  PreferredMoveResult,
} from "./preferredMoveApi";
import { PROMOTION_GAME } from "../viewer/viewerStoryFixtures";
import { VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import {
  AFTER_D4_FEN,
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
vi.mock("../design-system/CalendarDate", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../design-system/CalendarDate")>();

  return {
    ...actual,
    CalendarDate: ({
      value,
      onChange,
      label = "Date",
    }: {
      value: Date | null;
      onChange: (value: Date | null) => void;
      label?: string;
    }) => {
      const displayValue = value ? value.toISOString().slice(0, 10) : "Choose date";
      return (
        <button
          type="button"
          aria-label={`${label}: ${displayValue}`}
          onClick={() => onChange(new Date("2026-01-10T00:00:00.000Z"))}
        >
          {displayValue}
        </button>
      );
    },
  };
});
vi.mock("../board-adapter/PromotionPicker", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../board-adapter/PromotionPicker")>();

  return {
    ...actual,
    PromotionPicker: ({
      pending,
      onSelect,
    }: {
      pending: { sourceSquare: string; targetSquare: string } | null;
      onSelect: (piece: "q" | "r" | "b" | "n") => void;
    }) =>
      pending ? (
        <div role="dialog" aria-label="Choose a promotion piece">
          <button type="button" onClick={() => onSelect("n")}>
            Promote to knight
          </button>
        </div>
      ) : null,
  };
});

expect.extend(axeMatchers);
afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

function historyEntry(name: string) {
  return within(screen.getByTestId("board-move-history")).getByRole("button", { name });
}

describe("RepertoireBuilderWorkspace workflow", () => {
  it("stages a saved promotion move selected on the board without a history entry", async () => {
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
    expect(historyEntry("Initial position")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("session-status")).toHaveTextContent("My move staged: e8=N.");
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
    await waitFor(() =>
      expect(screen.getByTestId("saved-move")).toHaveTextContent("No saved choice yet."),
    );
  });

  it("retains a staged replacement after Remove and keeps Save available", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByTestId("move-d2-d4"));
    await user.click(screen.getByRole("button", { name: "Remove" }));
    const dialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    await user.click(within(dialog).getByRole("button", { name: "Remove" }));

    await waitFor(() =>
      expect(screen.getByTestId("saved-move")).toHaveTextContent("No saved choice yet."),
    );
    expect(screen.getByTestId("staged-move")).toHaveTextContent("d4");
    expect(screen.getByRole("button", { name: "Save" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Change effective date" })).toBeDisabled();
    expect(historyEntry("Initial position")).toHaveAttribute("aria-current", "step");
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
  });

  it("keeps saved and staged facts during Save and clears staging only after refreshed confirmation", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    let savedMove = { uci: "e2e4", san: "e4" };
    let resolvePut!: (result: PreferredMoveMutationResult) => void;
    let resolveRefresh!: (result: PreferredMoveResult) => void;
    let getCalls = 0;
    const preferredMoveClient: PreferredMoveClient = {
      get: vi.fn(async (fen) => {
        getCalls += 1;
        if (getCalls === 1) {
          return {
            status: "success" as const,
            data: {
              fen,
              state: "assigned" as const,
              move: savedMove,
              effective_at: "2026-01-01T00:00:00.000000Z",
            },
          };
        }
        return new Promise<PreferredMoveResult>((resolve) => (resolveRefresh = resolve));
      }),
      put: vi.fn(
        ({ fen }) =>
          new Promise<PreferredMoveMutationResult>((resolve) => {
            resolvePut = (result) => {
              savedMove = { uci: "d2d4", san: "d4" };
              resolve(result);
            };
            void fen;
          }),
      ),
      remove: clients.preferredMoveClient.remove,
    };
    renderWorkspace({
      preferredMoveClient,
      positionContextClient: clients.positionContextClient,
    });
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByTestId("move-d2-d4"));
    await user.click(screen.getByRole("button", { name: "Save" }));

    await screen.findByText("Saving preferred move...", { exact: true });
    expect(screen.getByTestId("saved-move")).toHaveTextContent("e4");
    expect(screen.getByTestId("staged-move")).toHaveTextContent("d4");
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Remove" })).toBeDisabled();
    expect(historyEntry("Initial position")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_D4_FEN);

    resolvePut({
      status: "success",
      data: {
        fen: STARTING_FEN,
        changed: true,
        effective_at: "2026-01-01T00:00:00.000000Z",
      },
    });
    await waitFor(() => expect(getCalls).toBe(2));
    expect(screen.getByTestId("saved-move")).toHaveTextContent("e4");
    expect(screen.getByTestId("staged-move")).toHaveTextContent("d4");

    resolveRefresh({
      status: "success",
      data: {
        fen: STARTING_FEN,
        state: "assigned",
        move: savedMove,
        effective_at: "2026-01-01T00:00:00.000000Z",
      },
    });
    await waitFor(() => expect(screen.getByTestId("saved-move")).toHaveTextContent("d4"));
    expect(screen.getByTestId("staged-move")).toHaveTextContent("No move staged.");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
    expect(historyEntry("Initial position")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("session-status")).toHaveTextContent("Preferred move saved.");
  });

  it("retains confirmed saved and staged facts while Remove is pending and after failure", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    let resolveRemove!: (result: PreferredMoveMutationResult) => void;
    clients.preferredMoveClient.remove = vi.fn(
      () => new Promise<PreferredMoveMutationResult>((resolve) => (resolveRemove = resolve)),
    );
    renderWorkspace(clients);
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByTestId("move-d2-d4"));
    await user.click(screen.getByRole("button", { name: "Remove" }));
    const dialog = await screen.findByRole("alertdialog", { name: "Remove preferred move?" });
    await user.click(within(dialog).getByRole("button", { name: "Remove" }));

    await screen.findByText("Removing preferred move...", { exact: true });
    expect(screen.getByTestId("saved-move")).toHaveTextContent("e4");
    expect(screen.getByTestId("staged-move")).toHaveTextContent("d4");
    resolveRemove({ status: "unexpected_failure" });

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(
        "The preferred move could not be updated. Try again.",
      ),
    );
    expect(screen.getByTestId("saved-move")).toHaveTextContent("e4");
    expect(screen.getByTestId("staged-move")).toHaveTextContent("d4");
    expect(screen.getByRole("button", { name: "Save" })).toBeEnabled();
  });

  it("keeps date changes visibly disabled without opening a calendar or issuing a request", async () => {
    const user = userEvent.setup();
    const clients = testClients();
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByText("Never seen as White")).toBeVisible());
    await user.click(screen.getByTestId("move-e2-e4"));
    const dateButton = screen.getByRole("button", { name: "Change effective date" });
    expect(dateButton).toBeDisabled();
    expect(dateButton).toHaveAccessibleDescription("Date changes are temporarily unavailable");
    await user.click(dateButton);
    expect(screen.queryByTestId("calendar-date-popup")).not.toBeInTheDocument();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() => expect(clients.preferredMoveClient.put).toHaveBeenCalledTimes(1));
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "e2e4", effective_at: "" },
      { signal: expect.any(AbortSignal) },
    );
    expect(screen.queryByTestId("calendar-date-popup")).not.toBeInTheDocument();
  });

  it("retains the staged move and disabled date gate when a mutation fails", async () => {
    const user = userEvent.setup();
    const clients = testClients();
    let resolveMutation!: (result: PreferredMoveMutationResult) => void;
    clients.preferredMoveClient.put = vi.fn(
      () =>
        new Promise<PreferredMoveMutationResult>((resolve) => {
          resolveMutation = resolve;
        }),
    );
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByText("Never seen as White")).toBeVisible());
    await user.click(screen.getByTestId("move-e2-e4"));
    await user.click(screen.getByRole("button", { name: "Save" }));

    const mutationMessage = await screen.findByText("Saving preferred move...", { exact: true });
    const mutationStatus = mutationMessage.closest('[role="status"]');
    if (!(mutationStatus instanceof HTMLElement)) {
      throw new Error("The preferred move mutation status region is missing.");
    }
    expect(mutationStatus).toHaveAttribute("role", "status");
    expect(mutationStatus).toHaveAttribute("aria-live", "polite");
    const sessionStatus = screen.getByTestId("session-status");
    expect(sessionStatus).toHaveAttribute("data-testid", "session-status");
    expect(sessionStatus).toHaveRole("status");
    expect(sessionStatus).toHaveAttribute("aria-live", "polite");
    expect(sessionStatus).toHaveTextContent("My move staged: e4.");

    resolveMutation({ status: "future_effective_time" });
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "The selected date cannot be in the future.",
    );
    expect(screen.getAllByRole("alert")).toHaveLength(1);
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "e2e4", effective_at: "" },
      { signal: expect.any(AbortSignal) },
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
    expect(screen.getByTestId("session-status")).toHaveTextContent("My move staged: e4.");
    expect(screen.getAllByText("My move staged: e4.", { exact: true })).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Change effective date" })).toBeDisabled();
    expect(
      screen.getByRole("button", { name: "Change effective date" }),
    ).toHaveAccessibleDescription("Date changes are temporarily unavailable");
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

    expect(within(session).queryByTestId("board-move-history")).not.toBeInTheDocument();
    expect(
      within(screen.getByTestId("repertoire-board-lane")).getByTestId("board-move-history"),
    ).toBeVisible();
    expect(within(session).getByTestId("session-status")).toHaveAttribute("aria-live", "polite");
    expect(
      within(session).getByRole("heading", { name: "What is saved, and what is staged?" }),
    ).toBeVisible();

    expect(await axe.run(container)).toHaveNoViolations();
  });
});
