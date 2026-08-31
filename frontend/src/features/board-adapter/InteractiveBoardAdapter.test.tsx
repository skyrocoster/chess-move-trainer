import { Chess } from "chess.js";
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useCallback, useMemo, useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  InteractiveBoardAdapter,
  type InteractiveBoardMoveIntent,
} from "./InteractiveBoardAdapter";
import {
  isPromotionTarget,
  type PromotionColor,
  type PromotionCommit,
  usePromotionController,
} from "./PromotionPicker";
import type { BranchSnapshot } from "./branchModel";
import { lastMoveFromSquares } from "./lastMove";

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
      {[
        "e2",
        "e4",
        "e7",
        "e5",
        "g8",
        "f6",
        "g1",
        "f3",
        "e8",
        "e1",
        "c8",
        "d7",
        "d5",
        "d6",
        "a6",
        "a5",
        "f7",
        "g7",
      ].map((square) => (
        <span
          key={`square-${square}`}
          data-testid={`board-square-${square}`}
          data-highlighted={options.squareStyles?.[square] ? "true" : "false"}
        />
      ))}
    </div>
  ),
}));

vi.mock("./PromotionPicker", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./PromotionPicker")>();
  const choices = ["queen", "rook", "bishop", "knight"] as const;
  const pieces = { queen: "q", rook: "r", bishop: "b", knight: "n" } as const;

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
          {choices.map((choice) => (
            <button key={choice} type="button" onClick={() => onSelect(pieces[choice])}>
              Promote to {choice}
            </button>
          ))}
        </div>
      ) : null,
  };
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const BLACK_TO_MOVE_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";
const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
const CASTLING_FEN = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1";
const EN_PASSANT_FEN = "4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1";
const TERMINAL_ORIGIN_FEN = "7k/5Q2/p5K1/8/8/8/8/8 b - - 0 1";

function terminalDescription(chess: Chess) {
  if (chess.isCheckmate()) {
    return "Checkmate";
  }
  if (chess.isStalemate()) {
    return "Stalemate";
  }
  if (chess.isInsufficientMaterial()) {
    return "Draw by insufficient material";
  }
  if (chess.isDrawByFiftyMoves()) {
    return "Draw by fifty-move rule";
  }
  return null;
}

function ControlledAdapterHarness({
  originFen,
  originPly = 0,
}: {
  originFen: string;
  originPly?: number;
}) {
  const chess = useMemo(() => new Chess(originFen), [originFen]);
  const [branchSnapshot, setBranchSnapshot] = useState<BranchSnapshot>(() => ({
    viewKey: "game:0",
    resetToken: 0,
    originFen,
    currentFen: originFen,
    originPly,
    moves: [],
    active: false,
  }));
  const [notice, setNotice] = useState("Make a legal move to start a temporary branch.");
  const [promotionColor, setPromotionColor] = useState<PromotionColor>(chess.turn());

  const createSnapshot = useCallback(
    (active: boolean) => ({
      viewKey: "game:0",
      resetToken: 0,
      originFen,
      currentFen: chess.fen(),
      originPly,
      moves: chess.history({ verbose: true }).map((move) => ({
        color: move.color,
        from: move.from,
        to: move.to,
        san: move.san,
        ...(move.promotion ? { promotion: move.promotion } : {}),
      })),
      active,
    }),
    [chess, originFen, originPly],
  );

  const handleCommit = useCallback(
    (commit: PromotionCommit) => {
      setBranchSnapshot(createSnapshot(true));
      setPromotionColor(chess.turn());
      setNotice(`Branch move committed: ${commit.move.san}.`);
    },
    [chess, createSnapshot],
  );

  const handleReject = useCallback(
    (reason: "illegal" | "stale") => {
      const moves = chess.history();
      setBranchSnapshot(createSnapshot(moves.length > 0));
      setPromotionColor(chess.turn());
      setNotice(
        reason === "stale"
          ? "Promotion rejected because the displayed branch position is stale."
          : "Promotion rejected because the move is illegal.",
      );
    },
    [chess, createSnapshot],
  );

  const controller = usePromotionController({
    chess,
    onCommit: handleCommit,
    onReject: handleReject,
  });
  const {
    pending,
    sourceElement,
    anchorElement,
    requestPromotion,
    selectPromotion,
    cancelPromotion,
  } = controller;

  const handleMoveIntent = useCallback(
    (intent: InteractiveBoardMoveIntent) => {
      const piece = chess.get(intent.sourceSquare);
      if (piece?.type === "p" && isPromotionTarget(piece.color, intent.targetSquare)) {
        const opened = requestPromotion(
          intent.sourceSquare,
          intent.targetSquare,
          intent.sourceElement,
          intent.anchorElement,
        );
        if (opened) {
          setBranchSnapshot(createSnapshot(true));
          setPromotionColor(piece.color);
          setNotice("Choose a promotion piece for the temporary branch.");
        }
        return false;
      }

      try {
        const move = chess.move({ from: intent.sourceSquare, to: intent.targetSquare });
        setBranchSnapshot(createSnapshot(true));
        setNotice(`Branch move committed: ${move.san}.`);
        return true;
      } catch {
        setNotice("Move rejected because it is illegal.");
        return false;
      }
    },
    [chess, createSnapshot, requestPromotion],
  );

  const handlePromotionCancel = useCallback(() => {
    cancelPromotion();
    setBranchSnapshot(createSnapshot(chess.history().length > 0));
    setPromotionColor(chess.turn());
    setNotice("Promotion cancelled; the captured position is unchanged.");
  }, [cancelPromotion, chess, createSnapshot]);

  const handleUndo = useCallback(() => {
    cancelPromotion();
    if (!chess.undo()) {
      return;
    }
    setBranchSnapshot(createSnapshot(chess.history().length > 0));
    setPromotionColor(chess.turn());
    setNotice("Undid the latest temporary branch move.");
  }, [cancelPromotion, chess, createSnapshot]);

  const handleReset = useCallback(() => {
    cancelPromotion();
    chess.load(originFen);
    setBranchSnapshot(createSnapshot(false));
    setPromotionColor(chess.turn());
    setNotice("Temporary branch reset to its captured-game ply.");
  }, [cancelPromotion, chess, createSnapshot, originFen]);

  return (
    <InteractiveBoardAdapter
      branchSnapshot={branchSnapshot}
      lastMove={
        branchSnapshot.moves.at(-1)
          ? lastMoveFromSquares(branchSnapshot.moves.at(-1)!.from, branchSnapshot.moves.at(-1)!.to)
          : null
      }
      label="Interactive analysis board"
      notice={notice}
      terminal={terminalDescription(chess)}
      promotionPending={pending}
      promotionColor={promotionColor}
      promotionSourceElement={sourceElement}
      promotionAnchorElement={anchorElement}
      onMoveIntent={handleMoveIntent}
      onPromotionSelect={selectPromotion}
      onPromotionCancel={handlePromotionCancel}
      onUndo={handleUndo}
      onReset={handleReset}
    />
  );
}

function renderAdapter(originFen = STARTING_FEN) {
  return render(<ControlledAdapterHarness originFen={originFen} />);
}

describe("InteractiveBoardAdapter", () => {
  it("names operable pieces without changing representative move behavior", () => {
    renderAdapter();

    expect(screen.getByRole("group", { name: "Interactive analysis board" })).toBeInTheDocument();
    expect(screen.getByTestId("interactive-board")).toHaveAttribute("data-board-visual");
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
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("branch-origin-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Reset" })).toBeDisabled();

    fireEvent.click(screen.getByTestId("move-e2-e4"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. e4");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    );
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "true");
    const branchFen = screen.getByTestId("mock-chessboard").getAttribute("data-position");
    expect(branchFen).not.toBe(STARTING_FEN);

    fireEvent.click(screen.getByTestId("move-e2-e5"));
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", branchFen);
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(branchFen ?? "");
    expect(screen.getByTestId("branch-status")).toHaveTextContent("illegal");

    fireEvent.click(screen.getByRole("button", { name: "Undo" }));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);

    fireEvent.click(screen.getByTestId("move-e2-e4"));
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("board-square-e2")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("board-square-e4")).toHaveAttribute("data-highlighted", "false");
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute("data-position", STARTING_FEN);
  });

  it("presents exact FEN values with distinct copy controls and bounded feedback", async () => {
    vi.useFakeTimers();
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    renderAdapter();

    expect(screen.getByTestId("branch-origin-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    expect(screen.getByTestId("branch-origin-fen").textContent?.split(" ")).toHaveLength(6);
    expect(screen.getByTestId("branch-current-fen").textContent?.split(" ")).toHaveLength(6);
    expect(screen.getByRole("button", { name: "Copy branch origin FEN" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy current branch FEN" })).toBeInTheDocument();
    expect(screen.getByTestId("branch-status")).toHaveTextContent(
      "Make a legal move to start a temporary branch.",
    );

    fireEvent.click(screen.getByRole("button", { name: "Copy branch origin FEN" }));
    await act(async () => {
      await Promise.resolve();
    });

    expect(writeText).toHaveBeenCalledWith(STARTING_FEN);
    expect(screen.getByTestId("branch-status")).toHaveTextContent("Copied branch origin FEN.");
    expect(screen.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Reset" })).toBeDisabled();

    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(screen.getByTestId("branch-status")).toHaveTextContent(
      "Make a legal move to start a temporary branch.",
    );

    writeText.mockRejectedValueOnce(new Error("clipboard unavailable"));
    fireEvent.click(screen.getByRole("button", { name: "Copy current branch FEN" }));
    await act(async () => {
      await Promise.resolve();
    });
    expect(screen.getByTestId("branch-status")).toHaveTextContent(
      "Unable to copy current branch FEN.",
    );
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
    expect(screen.getByTestId("board-square-e7")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e8")).toHaveAttribute("data-highlighted", "true");
  });

  it("commits both legal castling transitions with exact SAN and FEN", () => {
    renderAdapter(CASTLING_FEN);

    fireEvent.click(screen.getByTestId("move-e1-g1"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. O-O");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "r3k2r/8/8/8/8/8/8/R4RK1 b kq - 1 1",
    );
    expect(screen.getByTestId("board-square-e1")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-g1")).toHaveAttribute("data-highlighted", "true");

    fireEvent.click(screen.getByTestId("move-e8-c8"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1. O-O 1... O-O-O");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "2kr3r/8/8/8/8/8/8/R4RK1 w - - 2 2",
    );
    expect(screen.getByTestId("board-square-e8")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-c8")).toHaveAttribute("data-highlighted", "true");
  });

  it("commits the en-passant target and capture with exact SAN and FEN", () => {
    renderAdapter(EN_PASSANT_FEN);

    fireEvent.click(screen.getByTestId("move-d7-d5"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1... d5");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2",
    );
    expect(screen.getByTestId("board-square-d7")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-d5")).toHaveAttribute("data-highlighted", "true");

    fireEvent.click(screen.getByTestId("move-e5-d6"));
    expect(screen.getByTestId("branch-san")).toHaveTextContent("1... d5 2. exd6");
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(
      "4k3/8/3P4/8/8/8/8/4K3 b - - 0 2",
    );
    expect(screen.getByTestId("board-square-e5")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-d6")).toHaveAttribute("data-highlighted", "true");
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

  it("renders controlled branch data and emits movement intentions", () => {
    const onMoveIntent = vi.fn(() => false);
    const branchSnapshot: BranchSnapshot = {
      viewKey: "game:2",
      resetToken: 4,
      originFen: BLACK_TO_MOVE_FEN,
      currentFen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
      originPly: 2,
      moves: [{ color: "b", from: "e7", to: "e5", san: "e5" }],
      active: true,
    };
    render(
      <InteractiveBoardAdapter
        branchSnapshot={branchSnapshot}
        lastMove={lastMoveFromSquares("e7", "e5")}
        label="Interactive analysis board"
        notice="Branch move committed: e5."
        terminal={null}
        promotionPending={null}
        promotionColor="b"
        promotionSourceElement={null}
        promotionAnchorElement={null}
        onMoveIntent={onMoveIntent}
        onPromotionSelect={vi.fn()}
        onPromotionCancel={vi.fn()}
        onUndo={vi.fn()}
        onReset={vi.fn()}
      />,
    );

    expect(screen.getByTestId("branch-origin-fen")).toHaveTextContent(BLACK_TO_MOVE_FEN);
    expect(screen.getByTestId("branch-current-fen")).toHaveTextContent(branchSnapshot.currentFen);
    expect(screen.getByTestId("branch-current-ply")).toHaveTextContent("Current ply 3");
    expect(screen.getByRole("button", { name: "Reset" })).toBeEnabled();
    expect(screen.getByTestId("board-square-e7")).toHaveAttribute("data-highlighted", "true");
    expect(screen.getByTestId("board-square-e5")).toHaveAttribute("data-highlighted", "true");

    fireEvent.click(screen.getByTestId("move-e7-e5"));
    expect(onMoveIntent).toHaveBeenCalledWith(
      expect.objectContaining({ sourceSquare: "e7", targetSquare: "e5" }),
    );
  });
});
