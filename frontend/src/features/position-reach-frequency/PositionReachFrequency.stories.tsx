import { expect, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";
import type { ReactNode } from "react";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { PositionContextResponse } from "../viewer/positionContextApi";
import { PositionReachFrequency } from "./PositionReachFrequency";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const meta = {
  title: "Application/Position Reach Frequency",
  component: PositionReachFrequency,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component:
          "Reusable review surface for one explicitly selected repertoire colour's reached count over its all-games denominator.",
      },
    },
  },
} satisfies Meta<typeof PositionReachFrequency>;

export default meta;
type Story = StoryObj<typeof meta>;

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return {
    fen: FEN,
    overall_exists: true,
    white_count: 2,
    black_count: 3,
    white_total: 5,
    black_total: 7,
    ...overrides,
  };
}

function frame(children: ReactNode) {
  return (
    <main
      style={{
        minBlockSize: "100vh",
        padding: "var(--cmt-spacing-32)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <div style={{ maxInlineSize: "48rem", marginInline: "auto" }}>{children}</div>
    </main>
  );
}

function constrainedFrame(children: ReactNode) {
  return (
    <main
      style={{
        minBlockSize: "100vh",
        padding: "var(--cmt-spacing-16)",
        background: "var(--md-sys-color-background)",
        color: "var(--md-sys-color-on-background)",
      }}
    >
      <div style={{ inlineSize: "160px" }}>{children}</div>
    </main>
  );
}

function expectAvailable(
  canvasElement: HTMLElement,
  color: "White" | "Black",
  fraction: string,
  percentage: string,
) {
  const canvas = within(canvasElement);
  expect(canvas.getByText(`${color} repertoire colour`, { exact: true })).toBeVisible();
  expect(canvas.getByText(fraction, { exact: true })).toBeVisible();
  expect(canvas.getByText(percentage, { exact: true })).toBeVisible();
  expect(canvas.getByRole("meter", { name: `Position reach frequency as ${color}` })).toBeVisible();
}

export const PositiveWhite: Story = {
  name: "Positive - White 2 of 5 games",
  args: { context: context(), selectedColor: "white" },
  render: (args) => frame(<PositionReachFrequency {...args} />),
  play: async ({ canvasElement }) => {
    expectAvailable(canvasElement, "White", "2 / 5 games", "40%");
  },
};

export const PositiveBlack: Story = {
  name: "Positive - Black 3 of 7 games",
  args: { context: context(), selectedColor: "black" },
  render: (args) => frame(<PositionReachFrequency {...args} />),
  play: async ({ canvasElement }) => {
    expectAvailable(canvasElement, "Black", "3 / 7 games", "42.9%");
  },
};

export const AvailableZero: Story = {
  name: "Available zero - White 0 of 5 games",
  args: { context: context({ white_count: 0 }), selectedColor: "white" },
  render: (args) => frame(<PositionReachFrequency {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("0 / 5 games", { exact: true })).toBeVisible();
    await expect(canvas.getByText("0%", { exact: true })).toBeVisible();
    await expect(
      canvas.getByRole("meter", { name: "Position reach frequency as White" }),
    ).toHaveAttribute("aria-valuetext", "0 of 5 games as White; 0% reached.");
  },
};

export const Absent: Story = {
  name: "Absent - position not in accepted game data",
  args: {
    context: context({ overall_exists: false, white_count: 4, black_count: 3 }),
    selectedColor: "black",
  },
  render: (args) => frame(<PositionReachFrequency {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      canvas.getByText("This position is not present in the accepted game data for Black."),
    ).toBeVisible();
    await expect(canvas.queryByRole("meter")).not.toBeInTheDocument();
    await expect(canvas.queryByText(/0%|0 \/ /)).not.toBeInTheDocument();
  },
};

export const Unavailable: Story = {
  name: "Unavailable - no position reach data",
  args: { context: null, selectedColor: "white" },
  render: (args) => frame(<PositionReachFrequency {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText("Position reach data is unavailable.")).toBeVisible();
    await expect(canvas.queryByRole("meter")).not.toBeInTheDocument();
  },
};

export const ConstrainedWidth: Story = {
  name: "Constrained width - wrapped summary and bar",
  args: { context: context(), selectedColor: "white" },
  render: (args) => constrainedFrame(<PositionReachFrequency {...args} />),
  play: async ({ canvasElement }) => {
    expectAvailable(canvasElement, "White", "2 / 5 games", "40%");
  },
};

export const Accessibility: Story = {
  name: "Accessibility - labelled proportional meter",
  parameters: { a11y: { disable: false } },
  args: { context: context(), selectedColor: "black" },
  render: (args) => frame(<PositionReachFrequency {...args} />),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const meter = canvas.getByRole("meter", { name: "Position reach frequency as Black" });
    await expect(meter).toHaveAttribute("aria-valuemin", "0");
    await expect(meter).toHaveAttribute("aria-valuemax", "100");
    await expect(meter).toHaveAttribute("aria-valuenow", "42.857142857142854");
    await expect(meter).toHaveAttribute("aria-valuetext", "3 of 7 games as Black; 42.9% reached.");
  },
};

export const ForcedColorsAndReducedMotion: Story = {
  name: "Media emulation - forced colors and reduced motion",
  args: { context: context(), selectedColor: "white" },
  render: (args) => constrainedFrame(<PositionReachFrequency {...args} />),
  parameters: {
    docs: {
      description: {
        story:
          "Review this constrained state with forced-colors and prefers-reduced-motion browser emulation enabled.",
      },
    },
  },
};
