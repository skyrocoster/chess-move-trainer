import { userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { BoardAdapter, type BoardAdapterProps, STARTING_FEN } from "./BoardAdapter";
import styles from "./BoardAdapter.module.css";

const RICH_FEN = "rn1qk2r/1bp1bpp1/pp1ppn1p/8/4PB2/2NP1NP1/PPPQ1PBP/R3K2R b KQkq e3 0 8";
const INVALID_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 99";

const meta = {
  title: "Application/Board/Read-only Board",
  component: BoardAdapter,
} satisfies Meta<typeof BoardAdapter>;

export default meta;

type Story = StoryObj<typeof meta>;

const startingArgs: BoardAdapterProps = {
  fen: STARTING_FEN,
  label: "Starting position",
};

export const DefaultValidStartingPosition: Story = {
  name: "Default valid starting position",
  args: startingArgs,
};

export const RichPosition: Story = {
  name: "Rich position",
  args: {
    fen: RICH_FEN,
    label: "Rich position with complete game state",
  },
};

export const BlackOrientation: Story = {
  name: "Black orientation",
  args: {
    ...startingArgs,
    orientation: "black",
    label: "Starting position from Black's side",
  },
};

export const HiddenCoordinates: Story = {
  name: "Hidden coordinates",
  args: {
    ...startingArgs,
    showCoordinates: false,
    label: "Starting position without coordinates",
  },
};

export const ConstrainedWidth: Story = {
  name: "Constrained-width sizing",
  render: (args) => (
    <div className={styles.constrainedStory}>
      <BoardAdapter {...args} />
    </div>
  ),
  args: {
    ...startingArgs,
    label: "Starting position in a constrained container",
  },
};

export const InvalidFen: Story = {
  name: "Invalid FEN",
  args: {
    fen: INVALID_FEN,
    label: "Unavailable invalid position",
  },
};

export const ExpandedPositionDescription: Story = {
  name: "Expanded Position description",
  args: {
    fen: RICH_FEN,
    label: "Rich position with expanded description",
    showCoordinates: true,
  },
  play: async ({ canvasElement }) => {
    await userEvent.click(within(canvasElement).getByText("Position description"));
  },
};
