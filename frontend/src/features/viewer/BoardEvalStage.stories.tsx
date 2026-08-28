import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { BoardAdapter, STARTING_FEN } from "../board-adapter/BoardAdapter";
import { BoardEvalStage } from "./BoardEvalStage";

const meta = {
  title: "Application/Viewer/Board Evaluation Stage",
  component: BoardEvalStage,
  args: { children: <div /> },
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof BoardEvalStage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const StartingPosition: Story = {
  args: {
    orientation: "white",
    display: {
      state: "best-line",
      value: 63,
      shortValue: "+0.52",
      accessibleValue: "Best-line evaluation +0.52.",
    },
  },
  render: (args) => (
    <main
      style={{
        minHeight: "100vh",
        maxWidth: "66rem",
        padding: "var(--cmt-spacing-24)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <h1>Board evaluation stage</h1>
      <BoardEvalStage {...args}>
        <BoardAdapter
          fen={STARTING_FEN}
          label="Starting position with evaluation"
          orientation={args.orientation}
        />
      </BoardEvalStage>
    </main>
  ),
};
