import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { EvalBar, type EvalBarProps } from "./EvalBar";

const meta = {
  title: "Application/Viewer/Evaluation Bar",
  component: EvalBar,
  decorators: [
    (Story) => (
      <div style={{ background: "var(--md-sys-color-background)" }}>
        <Story />
      </div>
    ),
  ],
  parameters: { layout: "centered" },
} satisfies Meta<typeof EvalBar>;

export default meta;
type Story = StoryObj<typeof meta>;

type ExpectedDisplay = Pick<EvalBarProps, "orientation" | "state" | "value" | "accessibleValue">;

function expectDisplay(canvasElement: HTMLElement, expected: ExpectedDisplay) {
  const canvas = within(canvasElement);
  const meter = canvas.getByRole("meter", { name: "Evaluation" });

  expect(meter).toHaveAttribute("data-state", expected.state);
  expect(meter).toHaveAttribute("data-orientation", expected.orientation);
  expect(meter).toHaveAttribute("aria-valuemin", "0");
  expect(meter).toHaveAttribute("aria-valuemax", "100");
  expect(meter).toHaveAttribute("aria-valuenow", String(expected.value));
  expect(meter).toHaveAttribute("aria-valuetext", expected.accessibleValue);
  expect(canvas.getByText(expected.accessibleValue, { exact: true })).toBeVisible();

  return meter;
}

export const Neutral: Story = {
  name: "Neutral - before analysis",
  args: {
    orientation: "white",
    state: "neutral",
    value: 50,
    accessibleValue: "No analysis yet; evaluation neutral.",
  },
  play: async ({ canvasElement }) => {
    const meter = expectDisplay(canvasElement, {
      orientation: "white",
      state: "neutral",
      value: 50,
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
    await userEvent.tab();
    await expect(meter).not.toHaveFocus();
  },
};

export const Unavailable: Story = {
  name: "Unavailable - neutral fallback",
  args: {
    orientation: "white",
    state: "neutral",
    value: 50,
    accessibleValue: "Evaluation unavailable; evaluation neutral.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "neutral",
      value: 50,
      accessibleValue: "Evaluation unavailable; evaluation neutral.",
    });
  },
};

export const Queued: Story = {
  name: "Queued - pending analysis",
  args: {
    orientation: "white",
    state: "pending",
    value: 50,
    accessibleValue: "Analysis queued; evaluation pending.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "pending",
      value: 50,
      accessibleValue: "Analysis queued; evaluation pending.",
    });
  },
};

export const Running: Story = {
  name: "Running - pending analysis",
  args: {
    orientation: "black",
    state: "pending",
    value: 50,
    accessibleValue: "Analysis running; evaluation pending.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "black",
      state: "pending",
      value: 50,
      accessibleValue: "Analysis running; evaluation pending.",
    });
  },
};

export const BestLine: Story = {
  name: "Best line - completed evaluation",
  args: {
    orientation: "black",
    state: "best-line",
    value: 51.7,
    accessibleValue: "best-line evaluation +0.34.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "black",
      state: "best-line",
      value: 51.7,
      accessibleValue: "best-line evaluation +0.34.",
    });
  },
};

export const CompletedNegativeCp: Story = {
  name: "Completed - negative CP",
  args: {
    orientation: "white",
    state: "best-line",
    value: 48.3,
    accessibleValue: "best-line evaluation -0.34.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "best-line",
      value: 48.3,
      accessibleValue: "best-line evaluation -0.34.",
    });
  },
};

export const CompletedPositiveMate: Story = {
  name: "Completed - positive mate",
  args: {
    orientation: "white",
    state: "best-line",
    value: 100,
    accessibleValue: "best-line evaluation +M3.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "best-line",
      value: 100,
      accessibleValue: "best-line evaluation +M3.",
    });
  },
};

export const CompletedNegativeMate: Story = {
  name: "Completed - negative mate",
  args: {
    orientation: "black",
    state: "best-line",
    value: 0,
    accessibleValue: "best-line evaluation -M2.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "black",
      state: "best-line",
      value: 0,
      accessibleValue: "best-line evaluation -M2.",
    });
  },
};

export const CompletedMateGiven: Story = {
  name: "Completed - mate given",
  args: {
    orientation: "white",
    state: "best-line",
    value: 100,
    accessibleValue: "best-line evaluation +M.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "best-line",
      value: 100,
      accessibleValue: "best-line evaluation +M.",
    });
  },
};

export const StaleWithRetainedCandidate: Story = {
  name: "Stale - retained candidate",
  args: {
    orientation: "white",
    state: "best-line",
    value: 51.7,
    accessibleValue: "Stale best-line evaluation +0.34.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "best-line",
      value: 51.7,
      accessibleValue: "Stale best-line evaluation +0.34.",
    });
  },
};

export const StaleWithoutRetainedCandidate: Story = {
  name: "Stale - no retained candidate",
  args: {
    orientation: "white",
    state: "neutral",
    value: 50,
    accessibleValue: "No analysis yet; evaluation neutral.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "neutral",
      value: 50,
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
  },
};

export const FailedWithRetainedCandidate: Story = {
  name: "Failed - retained candidate",
  args: {
    orientation: "black",
    state: "best-line",
    value: 51.7,
    accessibleValue: "Stale best-line evaluation +0.34.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "black",
      state: "best-line",
      value: 51.7,
      accessibleValue: "Stale best-line evaluation +0.34.",
    });
  },
};

export const FailedWithoutRetainedCandidate: Story = {
  name: "Failed - no retained candidate",
  args: {
    orientation: "black",
    state: "neutral",
    value: 50,
    accessibleValue: "Analysis failed; evaluation neutral.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "black",
      state: "neutral",
      value: 50,
      accessibleValue: "Analysis failed; evaluation neutral.",
    });
  },
};

export const ClampedMinimum: Story = {
  name: "Completed - clamped minimum",
  args: {
    orientation: "white",
    state: "best-line",
    value: 0,
    accessibleValue: "best-line evaluation -20.00.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "white",
      state: "best-line",
      value: 0,
      accessibleValue: "best-line evaluation -20.00.",
    });
  },
};

export const ClampedMaximum: Story = {
  name: "Completed - clamped maximum",
  args: {
    orientation: "black",
    state: "best-line",
    value: 100,
    accessibleValue: "best-line evaluation +20.00.",
  },
  play: async ({ canvasElement }) => {
    expectDisplay(canvasElement, {
      orientation: "black",
      state: "best-line",
      value: 100,
      accessibleValue: "best-line evaluation +20.00.",
    });
  },
};
