import { Chess } from "chess.js";
import { useCallback, useEffect, useMemo, useState } from "react";
import { expect, fn, userEvent, waitFor, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
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
import styles from "./PromotionPicker.module.css";

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
const ILLEGAL_MOVE_FEN = "4r1k1/8/8/8/8/4N3/4P3/4K3 w - - 0 1";

type StoryHarnessProps = {
  viewKey: string;
  originFen: string;
  originPly: number;
  label: string;
  onBranchChange?: (snapshot: BranchSnapshot) => void;
};

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

function InteractiveBoardStoryHarness({
  viewKey,
  originFen,
  originPly,
  label,
  onBranchChange,
}: StoryHarnessProps) {
  const chess = useMemo(() => new Chess(originFen), [originFen]);
  const [branchSnapshot, setBranchSnapshot] = useState<BranchSnapshot>(() => ({
    viewKey,
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
    (active: boolean): BranchSnapshot => ({
      viewKey,
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
    [chess, originFen, originPly, viewKey],
  );

  useEffect(() => {
    onBranchChange?.(branchSnapshot);
  }, [branchSnapshot, onBranchChange]);

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
      setBranchSnapshot(createSnapshot(chess.history().length > 0));
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
      label={label}
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

const meta = {
  title: "Application/Board/Interactive Board",
  component: InteractiveBoardStoryHarness,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof InteractiveBoardStoryHarness>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => (
  <main className={styles.demo} style={{ padding: "var(--cmt-spacing-24)" }}>
    {children}
  </main>
);

async function startWhitePawnBranch(canvasElement: HTMLElement) {
  const pawn = canvasElement.querySelector<HTMLElement>(
    '[data-square="e2"] [aria-roledescription="draggable"]',
  );
  pawn?.focus();
  await userEvent.keyboard("{Enter}");
  await userEvent.keyboard("{ArrowUp}{ArrowUp}{Enter}");
}

async function startPromotion(canvasElement: HTMLElement) {
  const pawn = canvasElement.querySelector<HTMLElement>(
    '[data-square="e7"] [aria-roledescription="draggable"]',
  );
  pawn?.focus();
  await userEvent.keyboard("{Enter}");
  await userEvent.keyboard("{ArrowUp}{ArrowUp}{Enter}");
}

export const EmptyOrigin: Story = {
  name: "Empty captured ply",
  args: {
    viewKey: "story:empty",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
  },
  render: (args) => frame(<InteractiveBoardStoryHarness {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByRole("group", { name: "Interactive analysis board at captured ply 0" }),
    ).toBeVisible();
    await expect(canvas.getByRole("button", { name: "White pawn on e2" })).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(STARTING_FEN);
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    await expect(canvas.getByRole("button", { name: "Undo" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Reset" })).toBeDisabled();
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
      "Make a legal move to start a temporary branch.",
    );
  },
};

export const BranchActive: Story = {
  name: "Branch active with separate SAN",
  args: {
    viewKey: "story:active",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
    onBranchChange: fn(),
  },
  render: (args) => frame(<InteractiveBoardStoryHarness {...args} />),
  play: async ({ args, canvasElement }) => {
    await startWhitePawnBranch(canvasElement);
    await expect(canvasElement.querySelector('[data-testid="branch-san"]')).toHaveTextContent(
      "1. e3",
    );
    await expect(canvasElement.querySelector('[data-testid="branch-status"]')).toHaveTextContent(
      "committed",
    );
    await expect(
      canvasElement.querySelector('[data-testid="branch-current-fen"]'),
    ).toHaveTextContent("rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1");
    await expect(args.onBranchChange).toHaveBeenLastCalledWith(
      expect.objectContaining({
        viewKey: "story:active",
        originPly: 0,
        active: true,
        moves: [expect.objectContaining({ from: "e2", to: "e3", san: "e3" })],
      }),
    );
  },
};

export const IllegalMoveRejected: Story = {
  name: "Illegal move rejected without mutation",
  args: {
    viewKey: "story:illegal",
    originFen: ILLEGAL_MOVE_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
  },
  render: (args) => frame(<InteractiveBoardStoryHarness {...args} />),
  play: async ({ canvasElement }) => {
    await startWhitePawnBranch(canvasElement);
    await expect(canvasElement.querySelector('[data-testid="branch-san"]')).toHaveTextContent(
      "No branch moves yet",
    );
    await expect(
      canvasElement.querySelector('[data-testid="branch-current-fen"]'),
    ).toHaveTextContent(ILLEGAL_MOVE_FEN);
    await expect(canvasElement.querySelector('[data-testid="branch-status"]')).toHaveTextContent(
      "Move rejected because it is illegal.",
    );
    await expect(canvasElement.querySelector('[data-testid="branch-status"]')).toHaveAttribute(
      "role",
      "status",
    );
  },
};

export const UndoAndReset: Story = {
  name: "Undo and reset",
  args: {
    viewKey: "story:undo-reset",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
    onBranchChange: fn(),
  },
  render: (args) => frame(<InteractiveBoardStoryHarness {...args} />),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await startWhitePawnBranch(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Undo" }));
    await expect(canvasElement.querySelector('[data-testid="branch-san"]')).toHaveTextContent(
      "No branch moves yet",
    );
    await expect(args.onBranchChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ active: false, moves: [] }),
    );
    await startWhitePawnBranch(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Reset" }));
    await expect(canvasElement.querySelector('[data-testid="branch-san"]')).toHaveTextContent(
      "No branch moves yet",
    );
    await expect(args.onBranchChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ active: false, moves: [] }),
    );
    await expect(
      canvasElement.querySelector('[data-testid="branch-current-fen"]'),
    ).toHaveTextContent(STARTING_FEN);
  },
};

export const PickerIntegrated: Story = {
  name: "Promotion picker integrated",
  args: {
    viewKey: "story:promotion",
    originFen: PROMOTION_FEN,
    originPly: 12,
    label: "Interactive analysis board at captured ply 12",
  },
  render: (args) => frame(<InteractiveBoardStoryHarness {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    await expect(canvas.getByText("From captured ply 12")).toBeVisible();
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(PROMOTION_FEN);

    await startPromotion(canvasElement);
    await waitFor(() =>
      expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
    );
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(PROMOTION_FEN);

    await userEvent.keyboard("{Escape}");
    await expect(body.queryByRole("dialog")).not.toBeInTheDocument();
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
      "Promotion cancelled; the captured position is unchanged.",
    );
    await expect(canvas.getByRole("button", { name: "White pawn on e7" })).toHaveFocus();

    await startPromotion(canvasElement);
    await waitFor(() =>
      expect(body.getByRole("dialog", { name: "Choose a promotion piece" })).toBeVisible(),
    );
    await userEvent.click(body.getByRole("button", { name: "Promote to knight" }));
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("1. e8=N");
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(
      "k3N3/8/8/8/8/8/8/4K3 b - - 0 1",
    );
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
      "Branch move committed: e8=N.",
    );
  },
};
