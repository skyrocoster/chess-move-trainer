import userEvent from "@testing-library/user-event";
import { cleanup, fireEvent, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import axeMatchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import type { GameLookupResult } from "../viewer/positionApi";
import { PROMOTION_GAME } from "../viewer/viewerStoryFixtures";
import { VIEWER_GAME, VIEWER_GAME_UUID } from "../viewer/viewerFixtures";
import {
  AFTER_D4_FEN,
  AFTER_E4_FEN,
  AFTER_E8_KNIGHT_FEN,
  BOARD_LABEL,
  rawStyles,
  renderWorkspace,
  sharedPositionSummary,
  STARTING_FEN,
  STORED_BOARD_LABEL,
  testClients,
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
describe("RepertoireBuilderWorkspace", () => {
  function historyEntry(name: string) {
    return within(screen.getByTestId("session-move-history")).getByRole("button", { name });
  }

  it("renders the standard starting position with White at the bottom", () => {
    const { container } = renderWorkspace();
    expect(screen.getByRole("heading", { name: "Repertoire Builder", level: 1 })).toBeVisible();
    const board = screen.getByRole("group", { name: BOARD_LABEL });
    const stage = screen.getByTestId("board-eval-stage");
    const rail = screen.getByTestId("board-eval-rail-shell");
    expect(board).toBeVisible();
    expect(stage.parentElement).toBe(container.querySelector('[class*="workspace"]'));
    expect(stage).toContainElement(board);
    expect(stage).toContainElement(rail);
    expect(screen.getByRole("meter", { name: "Evaluation" })).toHaveAttribute(
      "data-orientation",
      "white",
    );
    expect(rawStyles).toMatch(/"board board session"/);
    expect(rawStyles).toMatch(/grid-template-columns:\s*minmax\(0, 1fr\) 30px minmax\(0, 1fr\)/);
    expect(rawStyles).toMatch(/"board board"/);
    expect(rawStyles).toMatch(/"controls \."/);
    expect(screen.getByTestId("session-origin")).toHaveTextContent(
      "Standard starting position; local session begins at Ply 0. Current Ply 0.",
    );
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "false");
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
    fireEvent.click(screen.getByRole("button", { name: "Flip" }));
    expect(screen.getByRole("meter", { name: "Evaluation" })).toHaveAttribute(
      "data-orientation",
      "black",
    );
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
    expect(historyEntry("White, move 1, e4")).toBeVisible();
    expect(historyEntry("Black, move 1, e5")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("board-square-e7")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e5")).toHaveAttribute("data-highlighted", "true");
    expect(sharedPositionSummary()).toHaveTextContent("OrientationBlack at the bottom");
  });

  it("selects stored and local positions through one controlled history path", async () => {
    const lookup = vi.fn().mockResolvedValue({
      status: "success" as const,
      game: { ...VIEWER_GAME, initial_ply: 2, subject_color: "black" as const },
    });
    const clients = testClients();
    const user = userEvent.setup();
    renderWorkspace({
      lookup,
      preferredMoveClient: clients.preferredMoveClient,
      positionContextClient: clients.positionContextClient,
    });
    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.type(screen.getByLabelText(/Ply/), "2");
    await user.click(screen.getByRole("button", { name: "Load game" }));
    await waitFor(() => expect(historyEntry("Black, move 1, e5")).toBeVisible());

    await user.click(screen.getByTestId("move-d2-d4"));
    expect(historyEntry("White, move 2, d4")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 3.");

    await user.click(historyEntry("White, move 1, e4"));
    expect(historyEntry("White, move 1, e4")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute(
      "data-position",
      VIEWER_GAME.positions[1].fen,
    );
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 1.");
    expect(sharedPositionSummary()).toHaveTextContent("Side to moveBlack");
    await waitFor(() =>
      expect(clients.preferredMoveClient.get).toHaveBeenCalledWith(VIEWER_GAME.positions[1].fen, {
        signal: expect.any(AbortSignal),
      }),
    );

    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(historyEntry("Black, move 1, e5")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 2.");
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(historyEntry("White, move 2, d4")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 3.");

    historyEntry("White, move 2, d4").focus();
    await user.keyboard("{Home}");
    expect(historyEntry("Initial position")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    historyEntry("Initial position").focus();
    await user.keyboard("{End}");
    expect(historyEntry("White, move 2, d4")).toHaveAttribute("aria-current", "step");
    await user.keyboard("{ArrowLeft}");
    expect(historyEntry("Black, move 1, e5")).toHaveAttribute("aria-current", "step");
  });

  it("keeps position reach frequency on the current FEN and bottom repertoire colour", async () => {
    const user = userEvent.setup();
    const clients = testClients();
    renderWorkspace(clients);

    await waitFor(() =>
      expect(clients.positionContextClient).toHaveBeenCalledWith(
        STARTING_FEN,
        expect.any(AbortSignal),
      ),
    );
    expect(screen.getByRole("meter", { name: "Position reach frequency as White" })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(screen.getByRole("meter", { name: "Position reach frequency as Black" })).toBeVisible();

    await user.click(screen.getByTestId("move-e2-e4"));
    await waitFor(() =>
      expect(clients.positionContextClient).toHaveBeenCalledWith(
        AFTER_E4_FEN,
        expect.any(AbortSignal),
      ),
    );
    expect(screen.getByRole("meter", { name: "Position reach frequency as Black" })).toBeVisible();
  });

  it("cancels a staged preview when combined-history navigation changes position", async () => {
    const user = userEvent.setup();
    const clients = testClients();
    renderWorkspace({
      preferredMoveClient: clients.preferredMoveClient,
      positionContextClient: clients.positionContextClient,
    });

    await user.click(screen.getByRole("button", { name: "Flip" }));
    await user.click(screen.getByTestId("move-e2-e4"));
    await user.click(screen.getByRole("button", { name: "Flip" }));
    await user.click(screen.getByTestId("move-e7-e5"));
    await user.click(screen.getByTestId("move-d2-d4"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute(
      "data-position",
      "rnbqkbnr/pppp1ppp/8/4p3/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3 0 2",
    );
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 2.");
    expect(screen.getByRole("button", { name: "Previous" })).toBeEnabled();

    await user.click(screen.getByRole("button", { name: "Previous" }));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 1.");
    expect(screen.getByTestId("session-status")).toHaveTextContent(
      "Moved to the previous local position.",
    );
    expect(screen.getByTestId("board-square-d2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-d4")).toHaveAttribute("data-highlighted", "false");
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
  it("clears a staged preview on Reset and when a new game loads", async () => {
    const lookup = vi.fn().mockResolvedValue({ status: "success", game: VIEWER_GAME });
    const user = userEvent.setup();
    renderWorkspace({ lookup });
    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "true");
    await user.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "false");
    expect(historyEntry("Initial position")).toBeVisible();
    await user.click(screen.getByTestId("move-e2-e4"));
    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));

    await waitFor(() =>
      expect(
        screen.getByRole("group", {
          name: `Chess board: game ${VIEWER_GAME_UUID}, ply 0, White at the bottom`,
        }),
      ).toBeVisible(),
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
  });
  it("stages my moves, cancels staging on Flip, and advances an opposing move locally", async () => {
    const user = userEvent.setup();
    const clients = testClients();
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByText("Never seen as White")).toBeVisible());
    await user.click(screen.getByTestId("move-e2-e4"));
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(sharedPositionSummary().querySelector('[data-position-side="b"]')).toHaveAttribute(
      "data-position-side-to-move",
      "true",
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("session-origin")).toHaveTextContent(
      "Standard starting position; local session begins at Ply 0. Current Ply 0.",
    );
    expect(screen.getByRole("region", { name: "Preferred move" })).toHaveAttribute(
      "data-state",
      "unsaved-played",
    );
    expect(screen.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    expect(historyEntry("Initial position")).toBeVisible();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(clients.preferredMoveClient.get).toHaveBeenCalledWith(STARTING_FEN, {
      signal: expect.any(AbortSignal),
    });
    expect(clients.positionContextClient).toHaveBeenCalledWith(
      STARTING_FEN,
      expect.any(AbortSignal),
    );
    const session = screen.getByTestId("repertoire-session");
    const status = within(session).getByTestId("session-status");
    expect(status).toHaveTextContent("My move staged: e4.");
    expect(status).toHaveAttribute("role", "status");
    expect(status).toHaveAttribute("aria-live", "polite");
    expect(within(session).getByTestId("session-move-history")).toBeVisible();
    expect(within(session).getByRole("heading", { name: "Preferred move" })).toBeVisible();
    expect(screen.getAllByText("My move staged: e4.", { exact: true })).toHaveLength(1);
    await user.click(screen.getByTestId("move-d2-d4"));
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d4"]')).toHaveLength(1);
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_D4_FEN);
    expect(screen.getByTestId("board-square-d2")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-d4")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(status).toHaveTextContent("My move staged: d4.");
    expect(screen.getAllByText("My move staged: d4.", { exact: true })).toHaveLength(1);
    await user.click(screen.getByRole("button", { name: "Flip" }));
    expect(screen.getByTestId("session-status")).toHaveTextContent(
      "Flipped to Black at the bottom.",
    );
    expect(screen.getByTestId("board-square-d2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-d4")).toHaveAttribute("data-highlighted", "false");
    expect(sharedPositionSummary()).toHaveTextContent("OrientationBlack at the bottom");
    expect(sharedPositionSummary()).toHaveTextContent("Side to moveWhite");
    await user.click(screen.getByTestId("move-e2-e4"));
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "true");
    expect(sharedPositionSummary().querySelector('[data-position-side="b"]')).toHaveAttribute(
      "data-position-side-to-move",
      "true",
    );
    expect(historyEntry("White, move 1, e4")).toHaveAttribute("aria-current", "step");
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
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Add" }));
    await waitFor(() => expect(clients.preferredMoveClient.put).toHaveBeenCalledTimes(1));
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "e2e4", effective_at: "" },
      { signal: expect.any(AbortSignal) },
    );
    await waitFor(() =>
      expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN),
    );
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(1);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(0);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-01" })).toBeVisible();
  });
  it("edits a saved move and saves one staged replacement explicitly", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByTestId("saved-move")).toHaveTextContent("e4"));
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-01" })).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Edit" }));
    await user.click(screen.getByTestId("move-d2-d4"));
    expect(screen.getByTestId("replacement-move")).toHaveTextContent("d4");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_D4_FEN);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d4"]')).toHaveLength(1);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Cancel edit" }));
    await waitFor(() =>
      expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN),
    );
    expect(screen.queryByTestId("replacement-move")).not.toBeInTheDocument();
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d2"]')).toHaveLength(1);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d4"]')).toHaveLength(0);
    expect(historyEntry("Initial position")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Edit" }));
    await user.click(screen.getByTestId("move-d2-d4"));
    await user.click(screen.getByRole("button", { name: "Save replacement" }));
    await waitFor(() => expect(clients.preferredMoveClient.put).toHaveBeenCalledTimes(1));
    expect(clients.preferredMoveClient.put).toHaveBeenCalledWith(
      { fen: STARTING_FEN, move_uci: "d2d4", effective_at: "" },
      { signal: expect.any(AbortSignal) },
    );
    await waitFor(() =>
      expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN),
    );
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d2"]')).toHaveLength(1);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d4"]')).toHaveLength(0);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
  });
  it("hydrates a persisted effective timestamp by its UTC calendar day", async () => {
    const clients = testClients("assigned", "2026-01-01T23:59:59.999000Z");
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByTestId("saved-move")).toHaveTextContent("e4"));
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-01" })).toBeVisible();
  });

  it("presents a persisted current UTC date as Today and keeps date changes explicit", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.setSystemTime(new Date("2026-01-15T23:59:59.999Z"));
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const clients = testClients("assigned", "2026-01-15T12:00:00.000000Z");
    renderWorkspace(clients);

    await waitFor(() => expect(screen.getByTestId("saved-move")).toHaveTextContent("e4"));
    expect(screen.getByTestId("effective-date")).toHaveTextContent("Effective from Today");

    await user.click(screen.getByRole("button", { name: "Effective date: 2026-01-15" }));
    const calendar = await screen.findByRole("dialog", { name: "Effective date" });
    await user.click(within(calendar).getByRole("button", { name: /January 10th, 2026/ }));

    expect(screen.getByTestId("effective-date")).toHaveTextContent("Effective from 2026-01-10");
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();
  });

  it("stages a selected promotion on the child position without local history", async () => {
    const lookup = vi.fn().mockResolvedValue({ status: "success", game: PROMOTION_GAME });
    const user = userEvent.setup();
    renderWorkspace({ lookup });
    await user.type(screen.getByLabelText("Game UUID"), VIEWER_GAME_UUID);
    await user.click(screen.getByRole("button", { name: "Load game" }));
    await waitFor(() =>
      expect(
        screen.getByRole("group", {
          name: `Chess board: game ${VIEWER_GAME_UUID}, ply 0, White at the bottom`,
        }),
      ).toBeVisible(),
    );

    await user.click(screen.getByTestId("move-e7-e8"));
    await screen.findByRole("dialog", { name: "Choose a promotion piece" });
    await user.keyboard("{Escape}");
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute(
      "data-position",
      PROMOTION_GAME.positions[0].fen,
    );
    expect(historyEntry("Initial position")).toBeVisible();
    await user.click(screen.getByTestId("move-e7-e8"));
    const dialog = await screen.findByRole("dialog", { name: "Choose a promotion piece" });
    await user.click(within(dialog).getByRole("button", { name: "Promote to knight" }));

    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute(
      "data-position",
      AFTER_E8_KNIGHT_FEN,
    );
    expect(screen.getByTestId("board-square-e7")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e8")).toHaveAttribute("data-highlighted", "true");
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e7"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e8"]')).toHaveLength(1);
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
    expect(historyEntry("Initial position")).toBeVisible();
  });
  it("plays the saved move through the local W1 path without a mutation", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Play saved move" }));

    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e2"]')).toHaveLength(0);
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="e4"]')).toHaveLength(1);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(historyEntry("White, move 1, e4")).toHaveAttribute("aria-current", "step");
    expect(screen.getByRole("region", { name: "Preferred move" })).toHaveAttribute(
      "data-state",
      "matching-played",
    );
    expect(screen.getByTestId("played-move")).toHaveTextContent("Played move: e4 (e2e4)");
    expect(screen.getByRole("button", { name: "Edit" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Remove" })).toBeVisible();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Edit" }));
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Save replacement" })).toBeVisible(),
    );
    expect(screen.getByTestId("session-origin")).toHaveTextContent("Current Ply 0.");
  });
  it("recognizes the saved move played on the board and advances the local session", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", AFTER_E4_FEN);
    expect(historyEntry("White, move 1, e4")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("session-status")).toHaveTextContent(
      "Saved move played locally: e4.",
    );
    expect(screen.getByRole("button", { name: "Previous" })).toBeEnabled();
    expect(screen.queryByTestId("saved-move")).not.toBeInTheDocument();
    expect(clients.preferredMoveClient.put).not.toHaveBeenCalled();
    expect(clients.preferredMoveClient.remove).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Reset" }));
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-01" })).toBeVisible();
    await user.click(screen.getByTestId("move-e2-e4"));
    expect(screen.queryByTestId("saved-move")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Previous" }));
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    expect(screen.getByRole("button", { name: "Effective date: 2026-01-01" })).toBeVisible();
  });
  it("stages an own-color move that is not the saved move", async () => {
    const user = userEvent.setup();
    const clients = testClients("assigned");
    renderWorkspace(clients);
    await waitFor(() => expect(screen.getByTestId("saved-move")).toBeVisible());
    await user.click(screen.getByTestId("move-d2-d4"));
    expect(sharedPositionSummary().querySelectorAll('[data-position-square="d4"]')).toHaveLength(1);
    expect(historyEntry("Initial position")).toBeVisible();
    expect(screen.getByTestId("session-status")).toHaveTextContent("My move staged: d4.");
    expect(screen.getByRole("region", { name: "Preferred move" })).toHaveAttribute(
      "data-state",
      "unsaved-played",
    );
    expect(screen.getByTestId("played-move")).toHaveTextContent("Played move: d4 (d2d4)");
    expect(screen.getByRole("button", { name: "Edit" })).toBeVisible();
  });
});
