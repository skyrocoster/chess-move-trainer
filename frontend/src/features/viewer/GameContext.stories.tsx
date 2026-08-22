import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { GameContext } from "./GameContext";
import styles from "./Stage1Story.module.css";
import {
  STAGE1_GAME,
  STAGE1_MISSING_SOURCE_GAME,
  STAGE1_UNSAFE_SOURCE_GAME,
} from "./stage1GameTypes";

const meta = {
  title: "Viewer/Stage 1/Game Context",
  component: GameContext,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof GameContext>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: React.ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);

export const Empty: Story = {
  render: () => frame(<GameContext />),
};

export const InitialPosition: Story = {
  args: { game: STAGE1_GAME, position: STAGE1_GAME.positions[0] },
  render: (args) => frame(<GameContext {...args} />),
};

export const IntermediatePosition: Story = {
  args: { game: STAGE1_GAME, position: STAGE1_GAME.positions[2] },
  render: (args) => frame(<GameContext {...args} />),
};

export const FinalPosition: Story = {
  args: { game: STAGE1_GAME, position: STAGE1_GAME.positions.at(-1) },
  render: (args) => frame(<GameContext {...args} />),
};

export const BlackSubject: Story = {
  args: {
    game: { ...STAGE1_GAME, subject_color: "black" },
    position: STAGE1_GAME.positions[1],
  },
  render: (args) => frame(<GameContext {...args} />),
};

export const UnsafeSource: Story = {
  args: { game: STAGE1_UNSAFE_SOURCE_GAME, position: STAGE1_UNSAFE_SOURCE_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
};

export const MissingSource: Story = {
  args: { game: STAGE1_MISSING_SOURCE_GAME, position: STAGE1_MISSING_SOURCE_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
};

export const Constrained: Story = {
  args: { game: STAGE1_GAME, position: STAGE1_GAME.positions[2] },
  render: (args) => constrained(<GameContext {...args} />),
};
