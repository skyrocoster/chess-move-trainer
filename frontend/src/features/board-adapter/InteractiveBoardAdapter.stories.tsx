import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { InteractiveBoardAdapter } from "./InteractiveBoardAdapter";
import styles from "./PromotionPicker.module.css";

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const PROMOTION_FEN = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";

const meta = {
  title: "Application/Board/Interactive Board",
  component: InteractiveBoardAdapter,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof InteractiveBoardAdapter>;

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

export const EmptyOrigin: Story = {
  name: "Empty captured ply",
  args: {
    viewKey: "story:empty",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
  },
  render: (args) => frame(<InteractiveBoardAdapter {...args} />),
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
  render: (args) => frame(<InteractiveBoardAdapter {...args} />),
  play: async ({ args, canvasElement }) => {
    await startWhitePawnBranch(canvasElement);
    await expect(canvasElement.querySelector('[data-testid="branch-san"]')).toHaveTextContent(
      "1. e3",
    );
    await expect(canvasElement.querySelector('[data-testid="branch-status"]')).toHaveTextContent(
      "committed",
    );
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

export const UndoAndReset: Story = {
  name: "Undo and reset",
  args: {
    viewKey: "story:undo-reset",
    originFen: STARTING_FEN,
    originPly: 0,
    label: "Interactive analysis board at captured ply 0",
    onBranchChange: fn(),
  },
  render: (args) => frame(<InteractiveBoardAdapter {...args} />),
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
  render: (args) => frame(<InteractiveBoardAdapter {...args} />),
};
