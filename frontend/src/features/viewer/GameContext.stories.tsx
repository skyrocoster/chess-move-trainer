import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { GameContext } from "./GameContext";
import styles from "./Stage1Story.module.css";
import { MISSING_SOURCE_GAME, UNSAFE_SOURCE_GAME, VIEWER_GAME } from "./viewerFixtures";

const meta = {
  title: "Application/Viewer/Game Context",
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
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[0] },
  render: (args) => frame(<GameContext {...args} />),
};

export const IntermediatePosition: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[2] },
  render: (args) => frame(<GameContext {...args} />),
};

export const FinalPosition: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions.at(-1) },
  render: (args) => frame(<GameContext {...args} />),
};

export const BlackSubject: Story = {
  args: {
    game: { ...VIEWER_GAME, subject_color: "black" },
    position: VIEWER_GAME.positions[1],
  },
  render: (args) => frame(<GameContext {...args} />),
};

export const UnsafeSource: Story = {
  args: { game: UNSAFE_SOURCE_GAME, position: UNSAFE_SOURCE_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
};

export const MissingSource: Story = {
  args: { game: MISSING_SOURCE_GAME, position: MISSING_SOURCE_GAME.positions[1] },
  render: (args) => frame(<GameContext {...args} />),
};

export const Constrained: Story = {
  args: { game: VIEWER_GAME, position: VIEWER_GAME.positions[2] },
  render: (args) => constrained(<GameContext {...args} />),
};
