import { expect, fn, userEvent, waitFor, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { BoardAnswerPresentation } from "./answerPresentation";
import { InteractiveBoardHarness } from "./InteractiveBoardHarness";
import styles from "./PromotionPicker.module.css";

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
const ILLEGAL_MOVE_FEN = "4r1k1/8/8/8/8/4N3/4P3/4K3 w - - 0 1";
const TERMINAL_ORIGIN_FEN = "7k/6Q1/6K1/p7/8/8/8/8 b - - 1 2";

const meta = {
  title: "Production/Application/Board/Interactive Board",
  tags: ["status-production"],
  component: InteractiveBoardHarness,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof InteractiveBoardHarness>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => (
  <main className={styles.demo} style={{ padding: "var(--cmt-spacing-24)" }}>
    {children}
  </main>
);

const constrainedFrame = (children: React.ReactNode) => (
  <main
    className={styles.demo}
    style={{
      boxSizing: "border-box",
      inlineSize: "320px",
      maxInlineSize: "100vw",
      padding: "var(--cmt-spacing-24)",
    }}
  >
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
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByRole("group", { name: "Interactive analysis board at captured ply 0" }),
    ).toBeVisible();
    await expect(canvas.getByRole("button", { name: "White pawn on e2" })).toBeVisible();
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(STARTING_FEN);
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    await expect(canvas.getByTestId("branch-current-ply")).toHaveTextContent("Current ply 0");
    await expect(canvas.getByRole("button", { name: "Copy branch origin FEN" })).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Copy current branch FEN" })).toBeVisible();
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
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
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
    await expect(
      canvasElement.querySelector('[data-testid="branch-current-ply"]'),
    ).toHaveTextContent("Current ply 1");
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
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
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
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
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

export const ActionDisabled: Story = {
  name: "Actions disabled at empty branch",
  args: {
    viewKey: "story:action-disabled",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
  },
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("branch-san")).toHaveTextContent("No branch moves yet");
    await expect(canvas.getByRole("button", { name: "Undo" })).toBeDisabled();
    await expect(canvas.getByRole("button", { name: "Reset" })).toBeDisabled();
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
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
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

export const TerminalState: Story = {
  name: "Terminal state",
  args: {
    viewKey: "story:terminal",
    originFen: TERMINAL_ORIGIN_FEN,
    originPly: 8,
    label: "Interactive analysis board at captured ply 8",
  },
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("branch-terminal")).toHaveTextContent(
      "Terminal result: Checkmate",
    );
    await expect(canvas.getByTestId("branch-current-ply")).toHaveTextContent("Current ply 8");
    await expect(canvas.getByTestId("branch-status")).toHaveTextContent(
      "Make a legal move to start a temporary branch.",
    );
  },
};

export const CopyFeedback: Story = {
  name: "Copy feedback",
  args: {
    viewKey: "story:copy-feedback",
    originFen: STARTING_FEN,
    originPly: 4,
    label: "Interactive analysis board at captured ply 4",
  },
  render: (args) => frame(<InteractiveBoardHarness {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole("button", { name: "Copy current branch FEN" }));
    await waitFor(() => expect(canvas.getByTestId("branch-status")).toHaveTextContent(/copy/i));
    await expect(canvas.getByTestId("branch-status")).toHaveAttribute("role", "status");
  },
};

export const ConstrainedWidth: Story = {
  name: "Constrained 320px width",
  args: {
    viewKey: "story:constrained-width",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
  },
  render: (args) => constrainedFrame(<InteractiveBoardHarness {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("branch-origin-fen")).toHaveTextContent(STARTING_FEN);
    await expect(canvas.getByTestId("branch-current-fen")).toHaveTextContent(STARTING_FEN);
    await expect(canvas.getByRole("button", { name: "Copy branch origin FEN" })).toBeVisible();
    await expect(canvas.getByRole("button", { name: "Copy current branch FEN" })).toBeVisible();
  },
};

const answerStoryFrame =
  (answer: BoardAnswerPresentation) =>
  (args: { viewKey: string; originFen: string; originPly: number; label: string }) =>
    frame(<InteractiveBoardHarness {...args} answer={answer} />);

const answerStoryArgs = {
  viewKey: "story:answer",
  originFen: STARTING_FEN,
  originPly: 0,
  label: "Interactive answer board",
} as const;

async function expectAnswerStatus(
  canvasElement: HTMLElement,
  message: string,
  lock: "true" | "false",
) {
  const canvas = within(canvasElement);
  const status = canvas.getByTestId("board-answer-status");
  await expect(status).toHaveTextContent(message);
  await expect(status).toHaveAttribute("role", "status");
  await expect(canvasElement.querySelector('[data-testid="interactive-board"]')).toHaveAttribute(
    "data-locked",
    lock,
  );
}

export const AnswerAwaitingInput: Story = {
  name: "Answer: awaiting input",
  args: { ...answerStoryArgs },
  render: answerStoryFrame({ status: "awaiting-input" }),
  play: async ({ canvasElement }) => {
    await expectAnswerStatus(canvasElement, "Awaiting your move.", "false");
    const group = within(canvasElement).getByRole("group", { name: "Interactive answer board" });
    await expect(group).not.toHaveAttribute("aria-disabled");
  },
};

export const AnswerIllegal: Story = {
  name: "Answer: illegal attempted move",
  args: { ...answerStoryArgs },
  render: answerStoryFrame({
    status: "illegal",
    attemptedMove: { sourceSquare: "e2", targetSquare: "e4" },
  }),
  play: async ({ canvasElement }) => {
    await expectAnswerStatus(canvasElement, "That move is illegal here.", "true");
    const group = within(canvasElement).getByRole("group", { name: "Interactive answer board" });
    await expect(group).toHaveAttribute("aria-disabled", "true");
  },
};

export const AnswerIncorrect: Story = {
  name: "Answer: incorrect legal move with expected reveal",
  args: { ...answerStoryArgs },
  render: answerStoryFrame({
    status: "incorrect",
    attemptedMove: { sourceSquare: "e2", targetSquare: "e4" },
    expectedMove: { sourceSquare: "g1", targetSquare: "f3" },
  }),
  play: async ({ canvasElement }) => {
    await expectAnswerStatus(
      canvasElement,
      "That move is legal but not the expected move.",
      "true",
    );
  },
};

export const AnswerCorrect: Story = {
  name: "Answer: correct move",
  args: { ...answerStoryArgs },
  render: answerStoryFrame({
    status: "correct",
    attemptedMove: { sourceSquare: "g1", targetSquare: "f3" },
  }),
  play: async ({ canvasElement }) => {
    await expectAnswerStatus(canvasElement, "Correct move.", "true");
  },
};

export const AnswerRevealed: Story = {
  name: "Answer: revealed expected move",
  args: { ...answerStoryArgs },
  render: answerStoryFrame({
    status: "revealed",
    expectedMove: { sourceSquare: "e2", targetSquare: "e4" },
  }),
  play: async ({ canvasElement }) => {
    await expectAnswerStatus(
      canvasElement,
      "The expected move is highlighted on the board.",
      "true",
    );
  },
};

export const AnswerDisabled: Story = {
  name: "Answer: locked while updating",
  args: { ...answerStoryArgs },
  render: answerStoryFrame({ status: "disabled" }),
  play: async ({ canvasElement }) => {
    await expectAnswerStatus(
      canvasElement,
      "The board is locked while the position updates.",
      "true",
    );
  },
};

export const AnswerWithContext: Story = {
  name: "Answer: awaiting input with last-move context",
  args: {
    viewKey: "story:answer-context",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive answer board with context",
  },
  render: answerStoryFrame({ status: "awaiting-input" }),
  play: async ({ canvasElement }) => {
    await startWhitePawnBranch(canvasElement);
    const canvas = within(canvasElement);
    await expect(canvas.getByTestId("board-answer-status")).toHaveTextContent(
      "Awaiting your move.",
    );
    await expect(canvas.getByTestId("interactive-board")).toHaveAttribute("data-locked", "false");
  },
};
