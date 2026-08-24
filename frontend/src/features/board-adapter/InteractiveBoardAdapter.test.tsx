import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InteractiveBoardAdapter } from "./InteractiveBoardAdapter";

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
        ["g1", "f3", "wN"],
        ["e7", "e8", "wP"],
        ["e2", "e5", "wP"],
        ["e1", "g1", "wK"],
        ["e8", "c8", "bK"],
        ["d7", "d5", "bP"],
        ["e5", "d6", "wP"],
        ["a6", "a5", "bP"],
        ["f7", "g7", "wQ"],
      ].map(([source, target, pieceType]) => (
        <button
          key={`${source}-${target}-${pieceType}`}
          type="button"
          data-testid={`move-${source}-${target}`}
          data-square={source}
          aria-roledescription="draggable"
          onClick={() => options.onPieceDrop({ sourceSquare: source, targetSquare: target })}
        >
          {options.pieces[pieceType]?.({ square: source })}
        </button>
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
  it("names operable pieces without changing representative move behavior", () => {
    renderAdapter();

    expect(screen.getByRole("group", { name: "Interactive analysis board" })).toBeInTheDocument();
    expect(
      screen.queryByRole("img", { name: "Interactive analysis board" }),
    ).not.toBeInTheDocument();
    const whitePawn = screen.getByTestId("move-e2-e4");
    const blackKnight = screen.getByTestId("move-g8-f6");
    expect(whitePawn).toHaveAccessibleName("White pawn on e2");
    expect(blackKnight).toHaveAccessibleName("Black knight on g8");

    fireEvent.click(whitePawn);
    fireEvent.click(blackKnight);

    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. e4 1... Nf6");
  });

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
