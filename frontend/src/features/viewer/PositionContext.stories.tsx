import { expect, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { PositionContext } from "./PositionContext";
import type { PositionContextResponse } from "./positionContextApi";
import styles from "./Stage1Story.module.css";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const meta = {
  title: "Application/Viewer/Position Context",
  component: PositionContext,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof PositionContext>;

export default meta;
type Story = StoryObj<typeof meta>;

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return { fen: FEN, overall_exists: true, white_count: 2, black_count: 1, ...overrides };
}

function frame(children: React.ReactNode) {
  return <main className={styles.frame}>{children}</main>;
}

function constrained(children: React.ReactNode) {
  return (
    <main className={styles.frame}>
      <div className={styles.constrained}>{children}</div>
    </main>
  );
}

function recurrencePlay(white: string, black: string): NonNullable<Story["play"]> {
  return async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("group", { name: "Position recurrence" })).toBeVisible();
    await expect(canvas.getByText(white, { exact: true })).toBeVisible();
    await expect(canvas.getByText(black, { exact: true })).toBeVisible();
  };
}

export const SeenCounts: Story = {
  name: "Seen counts - White and Black scopes",
  args: { context: context() },
  render: (args) => frame(<PositionContext {...args} />),
  play: recurrencePlay("Seen in 2 games as White", "Seen in 1 games as Black"),
};

export const ZeroCounts: Story = {
  name: "Zero counts - Never seen copy",
  args: { context: context({ white_count: 0, black_count: 0 }) },
  render: (args) => frame(<PositionContext {...args} />),
  play: recurrencePlay("Never seen as White", "Never seen as Black"),
};

export const AbsentPosition: Story = {
  name: "Absent overall position - Never seen copy",
  args: { context: context({ overall_exists: false, white_count: 4, black_count: 3 }) },
  render: (args) => frame(<PositionContext {...args} />),
  play: recurrencePlay("Never seen as White", "Never seen as Black"),
};

export const Empty: Story = {
  name: "Empty - no visible treatment",
  args: { context: null },
  render: (args) => frame(<PositionContext {...args} />),
  play: async ({ canvasElement }) => {
    await expect(
      within(canvasElement).queryByRole("group", { name: "Position recurrence" }),
    ).toBeNull();
  },
};

export const Constrained: Story = {
  name: "Constrained - wrapped recurrence copy",
  args: { context: context() },
  render: (args) => constrained(<PositionContext {...args} />),
  play: recurrencePlay("Seen in 2 games as White", "Seen in 1 games as Black"),
};

export const Accessibility: Story = {
  name: "Accessibility - recurrence metadata",
  parameters: { a11y: { disable: false } },
  args: { context: context() },
  render: (args) => frame(<PositionContext {...args} />),
  play: recurrencePlay("Seen in 2 games as White", "Seen in 1 games as Black"),
};

export const ForcedColors: Story = {
  name: "Media emulation - forced colors",
  args: { context: context() },
  render: (args) => constrained(<PositionContext {...args} />),
};
