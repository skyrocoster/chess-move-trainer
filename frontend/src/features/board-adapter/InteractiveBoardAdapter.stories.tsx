import { expect, fn, userEvent, waitFor, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { InteractiveBoardHarness } from "./InteractiveBoardHarness";
import styles from "./PromotionPicker.module.css";

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
const ILLEGAL_MOVE_FEN = "4r1k1/8/8/8/8/4N3/4P3/4K3 w - - 0 1";
const TERMINAL_ORIGIN_FEN = "7k/6Q1/6K1/p7/8/8/8/8 b - - 1 2";

const meta = {
  title: "Application/Board/Interactive Board",
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
