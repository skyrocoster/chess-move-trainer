import { expect, fn, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { BoardControl } from "./BoardControl";
import styles from "./Stage1Story.module.css";

const meta = {
  title: "Application/Viewer/Board Controls",
  component: BoardControl,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof BoardControl>;

export default meta;
type Story = StoryObj<typeof meta>;

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const constrained = (children: React.ReactNode) => (
  <main className={styles.frame}>
    <div className={styles.constrained}>{children}</div>
  </main>
);

export const Empty: Story = {
  render: () => frame(<BoardControl />),
};

export const InitialBoundary: Story = {
  args: { currentPly: 0, finalPly: 3 },
  render: (args) => frame(<BoardControl {...args} />),
};

export const Intermediate: Story = {
  args: { currentPly: 1, finalPly: 3, onPrevious: fn(), onNext: fn() },
  render: (args) =>
    frame(
      <BoardControl
        {...args}
        onPrevious={() => args.onPrevious?.()}
        onNext={() => args.onNext?.()}
      />,
    ),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const previous = canvas.getByRole("button", { name: "Previous" });
    const next = canvas.getByRole("button", { name: "Next" });
    await expect(previous).toBeEnabled();
    await expect(next).toBeEnabled();

    await userEvent.click(previous);
    await userEvent.click(next);
    await expect(args.onPrevious).toHaveBeenCalledTimes(1);
    await expect(args.onNext).toHaveBeenCalledTimes(1);
  },
};

export const FinalBoundary: Story = {
  args: { currentPly: 3, finalPly: 3 },
  render: (args) => frame(<BoardControl {...args} />),
};

export const Loading: Story = {
  args: { currentPly: 1, finalPly: 3, loading: true },
  render: (args) => frame(<BoardControl {...args} />),
};

export const Constrained: Story = {
  args: { currentPly: 1, finalPly: 3 },
  render: (args) => constrained(<BoardControl {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const toolbar = canvas.getByRole("toolbar", { name: "Board controls" });
    await expect(within(toolbar).getAllByRole("button")).toHaveLength(2);
  },
};

export const KeyboardToolbar: Story = {
  args: { currentPly: 1, finalPly: 3, onPrevious: fn(), onNext: fn() },
  render: (args) =>
    frame(
      <BoardControl
        {...args}
        onPrevious={() => args.onPrevious?.()}
        onNext={() => args.onNext?.()}
      />,
    ),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const toolbar = canvas.getByRole("toolbar", { name: "Board controls" });
    const previous = within(toolbar).getByRole("button", { name: "Previous" });
    const next = within(toolbar).getByRole("button", { name: "Next" });
    previous.focus();
    await userEvent.keyboard("{Enter}");
    await expect(args.onPrevious).toHaveBeenCalledTimes(1);
    await userEvent.keyboard("{ArrowRight}");
    await expect(next).toHaveFocus();
    await userEvent.keyboard(" ");
    await expect(args.onNext).toHaveBeenCalledTimes(1);
  },
};
