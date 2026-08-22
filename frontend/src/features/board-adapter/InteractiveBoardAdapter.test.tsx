import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InteractiveBoardAdapter } from "./InteractiveBoardAdapter";

vi.mock("react-chessboard", () => ({
  Chessboard: ({
    options,
  }: {
    options: {
      position: string;
      onPieceDrop: (args: { sourceSquare: string; targetSquare: string | null }) => boolean;
    };
  }) => (
    <div data-testid="mock-chessboard" data-position={options.position}>
      {[
        ["e2", "e4", "White pawn"],
        ["e7", "e5", "Black pawn"],
        ["g1", "f3", "White knight"],
        ["e7", "e8", "White promotion pawn"],
        ["e2", "e5", "Illegal white pawn"],
        ["e1", "g1", "White kingside castle"],
        ["e8", "c8", "Black queenside castle"],
        ["d7", "d5", "Black double-step pawn"],
        ["e5", "d6", "White en-passant capture"],
        ["a6", "a5", "Black terminal fixture pawn"],
        ["f7", "g7", "White terminal fixture queen"],
      ].map(([source, target, name]) => (
        <button
          key={`${source}-${target}-${name}`}
          type="button"
          data-testid={`move-${source}-${target}`}
          data-square={source}
          aria-roledescription="draggable"
          aria-label={name}
          onClick={() => options.onPieceDrop({ sourceSquare: source, targetSquare: target })}
        />
      ))}
    </div>
  ),
}));

afterEach(() => cleanup());

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const BLACK_TO_MOVE_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";
const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
const CASTLING_FEN = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1";
const EN_PASSANT_FEN = "4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1";
const TERMINAL_ORIGIN_FEN = "7k/5Q2/p5K1/8/8/8/8/8 b - - 0 1";

function renderAdapter(originFen = STARTING_FEN) {
  return render(
    <InteractiveBoardAdapter
      viewKey="game:0"
      originFen={originFen}
      originPly={0}
      label="Interactive analysis board"
    />,
  );
}

describe("InteractiveBoardAdapter", () => {
  it("starts empty, rejects illegal movement without mutation, and supports both Undo and Reset", () => {
    renderAdapter();

    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByTestId("branch-origin-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Reset" })).toBeDisabled();

    fireEvent.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. e4");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    );
    const branchFen = screen.getByTestId("mock-chessboard").getAttribute("data-position");
    expect(branchFen).not.toBe(STARTING_FEN);

    fireEvent.click(screen.getByTestId("move-e2-e5"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", branchFen);
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(branchFen ?? "");
    expect(screen.getByTestId("branch-status")).toHaveTextContent("illegal");

    fireEvent.click(screen.getByRole("button", { name: "Undo" }));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);

    fireEvent.click(screen.getByTestId("move-e2-e4"));
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
  });

  it("formats a separate branch SAN line for the side to move at the origin", () => {
    renderAdapter(BLACK_TO_MOVE_FEN);

    fireEvent.click(screen.getByTestId("move-e7-e5"));
    fireEvent.click(screen.getByTestId("move-g1-f3"));

    expect(screen.getByTestId("branch-san")).toHaveTextContent("1... e5 2. Nf3");
  });

  it.each([
    ["queen", "1. e8=Q+", "k3Q3/8/8/8/8/8/8/4K3 b - - 0 1"],
    ["rook", "1. e8=R+", "k3R3/8/8/8/8/8/8/4K3 b - - 0 1"],
    ["bishop", "1. e8=B", "k3B3/8/8/8/8/8/8/4K3 b - - 0 1"],
    ["knight", "1. e8=N", "k3N3/8/8/8/8/8/8/4K3 b - - 0 1"],
  ] as const)("routes %s promotion through the approved picker", (name, san, fen) => {
    renderAdapter(PROMOTION_FEN);

    fireEvent.click(screen.getByTestId("move-e7-e8"));
    expect(screen.getByRole("dialog", { name: "Choose a promotion piece" })).toBeInTheDocument();
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(PROMOTION_FEN);
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", PROMOTION_FEN);

    fireEvent.click(screen.getByRole("button", { name: `Promote to ${name}` }));

    expect(screen.getByTestId("branch-san")).toHaveTextContent(san);
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(fen);
    expect(screen.getByTestId("branch-current-fen").textContent?.split(" ")).toHaveLength(6);
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", fen);
  });

  it("commits both legal castling transitions with exact SAN and FEN", () => {
    renderAdapter(CASTLING_FEN);

    fireEvent.click(screen.getByTestId("move-e1-g1"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. O-O");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "r3k2r/8/8/8/8/8/8/R4RK1 b kq - 1 1",
    );

    fireEvent.click(screen.getByTestId("move-e8-c8"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. O-O 1... O-O-O");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "2kr3r/8/8/8/8/8/8/R4RK1 w - - 2 2",
    );
  });

  it("commits the en-passant target and capture with exact SAN and FEN", () => {
    renderAdapter(EN_PASSANT_FEN);

    fireEvent.click(screen.getByTestId("move-d7-d5"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1... d5");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2",
    );

    fireEvent.click(screen.getByTestId("move-e5-d6"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1... d5 2. exd6");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "4k3/8/3P4/8/8/8/8/4K3 b - - 0 2",
    );
  });

  it("presents a verified terminal classification after a complete self-play branch", () => {
    renderAdapter(TERMINAL_ORIGIN_FEN);

    fireEvent.click(screen.getByTestId("move-a6-a5"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1... a5");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "7k/5Q2/6K1/p7/8/8/8/8 w - - 0 2",
    );

    fireEvent.click(screen.getByTestId("move-f7-g7"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1... a5 2. Qg7#");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "7k/6Q1/6K1/p7/8/8/8/8 b - - 1 2",
    );
    expect(screen.getByTestId("branch-terminal")).toHaveTextContent("Terminal result: Checkmate");
  });

  it("reports immutable origin and active state separately from the current branch position", () => {
    const onBranchChange = vi.fn();
    render(
      <InteractiveBoardAdapter
        viewKey="game:2"
        originFen={BLACK_TO_MOVE_FEN}
        originPly={2}
        label="Interactive analysis board"
        onBranchChange={onBranchChange}
      />,
    );

    fireEvent.click(screen.getByTestId("move-e7-e5"));
    const latest = onBranchChange.mock.lastCall?.[0];
    expect(latest).toMatchObject({
      viewKey: "game:2",
      originFen: BLACK_TO_MOVE_FEN,
      originPly: 2,
      active: true,
    });
    expect(latest.currentFen).not.toBe(BLACK_TO_MOVE_FEN);
  });
});
