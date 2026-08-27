import type { ComponentProps, ReactNode } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import {
  AnalysisPanel,
  type AnalysisPanelDisplay,
  type AnalysisPanelLine,
  type AnalysisPanelWdl,
} from "./AnalysisPanel";

const meta = {
  title: "Application/Analysis/Analysis Panel",
  component: AnalysisPanel,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof AnalysisPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

function displayWdl(wins: number, draws: number, losses: number): AnalysisPanelWdl {
  const value = (percentage: number) => ({
    percentage,
    label: `${percentage.toFixed(1)}%`,
  });
  const accessibleValue = (percentage: number) =>
    `${Number.isInteger(percentage) ? percentage : percentage.toFixed(1)} percent`;

  return {
    wins: value(wins),
    draws: value(draws),
    losses: value(losses),
    accessibleLabel: `Win ${accessibleValue(wins)}, draw ${accessibleValue(
      draws,
    )}, loss ${accessibleValue(losses)}`,
  };
}

const DISPLAY_LINES: AnalysisPanelLine[] = [
  {
    rank: 1,
    score: "+0.34",
    pv: "1. e4 e5 2. Nf3",
    wdl: displayWdl(42, 30, 28),
  },
  {
    rank: 2,
    score: "-M3",
    pv: "1. d4 d5",
    wdl: displayWdl(20, 30, 50),
  },
  {
    rank: 3,
    score: "+M",
    pv: "1. c4",
    wdl: displayWdl(50, 25, 25),
  },
  {
    rank: 4,
    score: "-2.50",
    pv: "1. Nf3",
    wdl: displayWdl(10, 20, 70),
  },
  {
    rank: 5,
    score: "+0.10",
    pv: "Line unavailable",
    wdl: displayWdl(40, 30, 30),
  },
];

const DEFAULT_ACTIONS: AnalysisPanelDisplay["actions"] = {
  analyze: false,
  update: false,
  retry: false,
  observationRetry: false,
  pending: false,
};

type DisplayOverrides = Omit<Partial<AnalysisPanelDisplay>, "actions"> & {
  actions?: Partial<AnalysisPanelDisplay["actions"]>;
};

function displayFor(overrides: DisplayOverrides = {}): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return {
    stateLabel: "Loading evaluation…",
    error: null,
    actionError: null,
    message: null,
    result: null,
    ...displayOverrides,
    actions: { ...DEFAULT_ACTIONS, ...actions },
  };
}

function missingDisplay(overrides: DisplayOverrides = {}): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return displayFor({
    stateLabel: "Analysis available on request",
    message: {
      text: "Analyze this displayed position deliberately to request a result.",
      alert: false,
    },
    ...displayOverrides,
    actions: { analyze: true, ...actions },
  });
}

function queuedDisplay(state: "queued" | "running"): AnalysisPanelDisplay {
  return displayFor({
    stateLabel: state === "queued" ? "Analysis queued" : "Analysis running",
    message: {
      text:
        state === "queued" ? "This position is waiting for analysis." : "Analysis is in progress.",
      alert: false,
    },
  });
}

function completeDisplay(
  stale = false,
  lines: AnalysisPanelLine[] = DISPLAY_LINES,
  overrides: DisplayOverrides = {},
): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return displayFor({
    stateLabel: stale ? "Stale analysis" : "Analysis complete",
    result: {
      stale,
      lines,
      metadata: {
        displayedPly: 12,
        depth: lines.length > 0 ? 28 : null,
        candidateCount: lines.length,
      },
    },
    ...displayOverrides,
    actions: { update: true, ...actions },
  });
}

function failedDisplay(overrides: DisplayOverrides = {}): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return displayFor({
    stateLabel: "Analysis failed",
    message: {
      text: "No complete result was published. Retry deliberately when ready.",
      alert: true,
    },
    ...displayOverrides,
    actions: { retry: true, ...actions },
  });
}

function errorDisplay(overrides: DisplayOverrides = {}): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return displayFor({
    stateLabel: "Evaluation unavailable",
    error: "Evaluation data is unavailable.",
    ...displayOverrides,
    actions: { observationRetry: true, ...actions },
  });
}

function panelArgs(display: AnalysisPanelDisplay): ComponentProps<typeof AnalysisPanel> {
  return {
    display,
    onAnalyze: fn(),
    onUpdate: fn(),
    onRetry: fn(),
    onRetryObservation: fn(),
  };
}

const frame = (children: ReactNode) => (
  <main
    style={{
      minBlockSize: "100vh",
      padding: "var(--cmt-spacing-24)",
      background: "var(--md-sys-color-background)",
      color: "var(--md-sys-color-on-background)",
    }}
  >
    {children}
  </main>
);
const panel = (args: ComponentProps<typeof AnalysisPanel>) => frame(<AnalysisPanel {...args} />);
const constrainedPanel = (args: ComponentProps<typeof AnalysisPanel>) => (
  <main
    data-testid="analysis-panel-constrained-frame"
    style={{
      boxSizing: "border-box",
      minBlockSize: "100vh",
      maxInlineSize: "100%",
      inlineSize: "640px",
      padding: "var(--cmt-spacing-24)",
      background: "var(--md-sys-color-background)",
      color: "var(--md-sys-color-on-background)",
    }}
  >
    <AnalysisPanel {...args} />
  </main>
);

export const Loading: Story = {
  name: "Loading - observation pending",
  args: panelArgs(displayFor()),
  render: (args) => panel(args),
};

export const Missing: Story = {
  name: "Missing - Analyze required",
  args: panelArgs(missingDisplay()),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Analyze position" }));
    await expect(args.onAnalyze).toHaveBeenCalledTimes(1);
  },
};

export const Queued: Story = {
  name: "Queued - observed automatically",
  args: panelArgs(queuedDisplay("queued")),
  render: (args) => panel(args),
};

export const Running: Story = {
  name: "Running - observed automatically",
  args: panelArgs(queuedDisplay("running")),
  render: (args) => panel(args),
};

export const Complete: Story = {
  name: "Complete - five ranked lines and formatted values",
  args: panelArgs(completeDisplay()),
  render: (args) => panel(args),
};

export const ConstrainedComplete: Story = {
  name: "Complete - constrained review frame",
  args: panelArgs(completeDisplay()),
  render: (args) => constrainedPanel(args),
};

export const Stale: Story = {
  name: "Stale - Update required",
  args: panelArgs(completeDisplay(true)),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Update analysis" }));
    await expect(args.onUpdate).toHaveBeenCalledTimes(1);
  },
};

export const Failed: Story = {
  name: "Failed - Retry required",
  args: panelArgs(failedDisplay()),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Retry analysis" }));
    await expect(args.onRetry).toHaveBeenCalledTimes(1);
  },
};

export const ObservationError: Story = {
  name: "Error - Observation retry",
  args: panelArgs(errorDisplay()),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Retry observation" }));
    await expect(args.onRetryObservation).toHaveBeenCalledTimes(1);
  },
};

export const ActionPending: Story = {
  name: "Action pending - deliberate action disabled",
  args: panelArgs(missingDisplay({ actions: { pending: true } })),
  render: (args) => panel(args),
};

export const ActionError: Story = {
  name: "Action error - retry remains deliberate",
  args: panelArgs(missingDisplay({ actionError: "The analysis action could not be submitted." })),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Analyze position" }));
    await expect(args.onAnalyze).toHaveBeenCalledTimes(1);
  },
};

export const TerminalEmpty: Story = {
  name: "Complete - terminal empty result",
  args: panelArgs(completeDisplay(false, [])),
  render: (args) => panel(args),
};

export const Accessibility: Story = {
  name: "Accessibility - complete semantic presentation",
  args: panelArgs(completeDisplay()),
  render: (args) => panel(args),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("heading", { level: 2, name: "Analysis" })).toBeVisible();
    await expect(canvas.getByRole("status")).toHaveTextContent("Analysis complete");
    await expect(canvas.getByRole("heading", { level: 3, name: "Best line" })).toBeVisible();
    await expect(canvas.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    await expect(canvas.getAllByRole("listitem")).toHaveLength(4);
    await expect(canvas.queryByRole("alert")).not.toBeInTheDocument();
  },
};
