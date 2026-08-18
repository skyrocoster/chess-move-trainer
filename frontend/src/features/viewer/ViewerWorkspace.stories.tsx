import type { Meta, StoryObj } from "@storybook/react-vite";

import ViewerWorkspace from "./ViewerWorkspace";
import styles from "./ViewerWorkspace.module.css";

const meta = {
  title: "Viewer Workspace",
  component: ViewerWorkspace,
} satisfies Meta<typeof ViewerWorkspace>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Wide: Story = {
  name: "Wide",
};

export const Constrained: Story = {
  name: "Constrained",
  render: () => (
    <div className={styles.constrainedStory}>
      <ViewerWorkspace />
    </div>
  ),
};
