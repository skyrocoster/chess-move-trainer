import { expect, fn, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { RepertoireBoardLane } from "./RepertoireBoardLane";

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const evaluation = {
  state: "neutral",
  value: 50,
  shortValue: "0.00",
  accessibleValue: "No analysis yet; evaluation neutral.",
} as const;

const board = {
  branchSnapshot: {
    viewKey: "board-lane-story",
    resetToken: 0,
    originFen: STARTING_FEN,
    currentFen: STARTING_FEN,
    originPly: 0,
    moves: [],
    active: false,
  },
  label: "Chess board: standard starting position, White at the bottom",
  notice: "Select a legal move to continue the local line.",
  terminal: null,
  lastMove: null,
  promotionPending: null,
  promotionColor: "w" as const,
  promotionSourceElement: null,
  promotionAnchorElement: null,
  showBranchPanel: false,
  onMoveIntent: () => false,
  onPromotionSelect: fn(),
  onPromotionCancel: fn(),
  onUndo: fn(),
  onReset: fn(),
};

const controls = {
  hasGame: true,
  canGoPrevious: false,
  canGoNext: true,
  onPrevious: fn(),
  onNext: fn(),
  onFlip: fn(),
};

const history = {
  initialPosition: { ply: 0 },
  moves: [
    { ply: 1, san: "e4" },
    { ply: 2, san: "e5" },
  ],
  activePly: 2,
  onActivePlyChange: fn(),
};

const meta = {
  title: "Application/Repertoire Builder/Board Lane",
  component: RepertoireBoardLane,
  parameters: { layout: "fullscreen" },
  args: {
    orientation: "white" as const,
    evaluation,
    viewKey: "board-lane-story",
    board,
    controls,
    history,
  },
} satisfies Meta<typeof RepertoireBoardLane>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Standard: Story = {
  name: "Board, controls, and controlled history",
  render: () => (
    <main style={{ maxInlineSize: "40rem", margin: "0 auto", padding: "var(--cmt-spacing-24)" }}>
      <RepertoireBoardLane
        orientation="white"
        evaluation={evaluation}
        viewKey="board-lane-story"
        board={board}
        controls={controls}
        history={history}
      />
    </main>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const lane = canvas.getByTestId("repertoire-board-lane");
    await expect(lane).toBeVisible();
    await expect(lane).toContainElement(canvas.getByTestId("board-eval-stage"));
    await expect(canvas.getByRole("toolbar", { name: "Board controls" })).toBeVisible();
    const moveHistory = within(lane).getByTestId("board-move-history");
    await expect(moveHistory).toHaveAccessibleName("Repertoire move history");
    await expect(within(moveHistory).getAllByRole("button")).toHaveLength(3);
    await expect(
      within(moveHistory).getByRole("button", { name: "Black, move 1, e5" }),
    ).toHaveAttribute("aria-current", "step");
  },
};
