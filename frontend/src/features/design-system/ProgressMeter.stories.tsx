import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, within } from "storybook/test";
import type { ReactNode } from "react";

import { ProgressMeter } from "./ProgressMeter";

const meta = {
  title: "Production/Design System/Components/Progress Meter",
  tags: ["status-production"],
  component: ProgressMeter,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ProgressMeter>;

export default meta;
type Story = StoryObj<typeof meta>;

function shell(children: ReactNode) {
  return (
    <main
      style={{
        display: "grid",
        gap: "var(--cmt-spacing-16)",
        padding: "var(--cmt-spacing-32)",
        maxInlineSize: "40rem",
        backgroundColor: "var(--md-sys-color-surface)",
        color: "var(--md-sys-color-on-surface)",
        fontFamily: "system-ui",
      }}
    >
      {children}
    </main>
  );
}

export const Determinate: Story = {
  name: "Determinate",
  args: { value: 75, label: "Engine analysis", valueText: "75%" },
  render: (args) => shell(<ProgressMeter {...args} />),
  play: async ({ canvasElement }) => {
    await expect(
      within(canvasElement).getByRole("meter", { name: "Engine analysis" }),
    ).toHaveAttribute("aria-valuenow", "75");
  },
};

export const Unavailable: Story = {
  name: "Unavailable",
  args: { value: null, label: "Move preferences", valueText: "No coverage data" },
  render: (args) => shell(<ProgressMeter {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.queryByRole("meter")).not.toBeInTheDocument();
    await expect(canvas.getByText("No coverage data")).toBeVisible();
  },
};
