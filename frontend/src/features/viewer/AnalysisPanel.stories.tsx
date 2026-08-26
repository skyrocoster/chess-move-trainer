import type { ComponentProps, ReactNode } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { AnalysisPanel } from "./AnalysisPanel";
import type { EvaluationObservation, EvaluationResult, EvaluationStatus } from "./analysisApi";
import { analysisPanelDisplay, type AnalysisPanelDisplay } from "./analysisFormatting";
import type { AnalysisState } from "./analysisState";
import styles from "./Stage1Story.module.css";
import { VIEWER_GAME } from "./viewerFixtures";

const FEN = VIEWER_GAME.positions[0].fen;

const meta = {
  title: "Application/Viewer/Analysis Panel",
  component: AnalysisPanel,
  parameters: { layout: "fullscreen" },
} satisfies Meta<typeof AnalysisPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

function status(state: EvaluationStatus["state"]): EvaluationStatus {
  return {
    state,
    position: 0,
    attempts: 1,
    enqueued_at: "2026-08-21T00:00:00+00:00",
    started_at: state === "queued" ? null : "2026-08-21T00:00:00+00:00",
    completed_at: state === "done" || state === "failed" ? "2026-08-21T00:00:01+00:00" : null,
    error_code: state === "failed" ? "engine_failure" : null,
  };
}

const result: EvaluationResult = {
  fen: FEN,
  profile_id: "mp09-balanced-nodes-v2-200000",
  candidates: [
    {
      rank: 1,
      score_kind: "cp",
      score_value: 34,
      wdl_wins: 420,
      wdl_draws: 300,
      wdl_losses: 280,
      pv_uci: ["e2e4", "e7e5", "g1f3"],
      depth: 20,
      seldepth: 24,
      nodes: 200000,
      engine_time_ms: 100,
    },
    {
      rank: 2,
      score_kind: "mate",
      score_value: -3,
      wdl_wins: 200,
      wdl_draws: 300,
      wdl_losses: 500,
      pv_uci: ["d2d4", "d7d5"],
      depth: 20,
      seldepth: 24,
      nodes: 200000,
      engine_time_ms: 100,
    },
    {
      rank: 3,
      score_kind: "mate_given",
      score_value: 0,
      wdl_wins: 500,
      wdl_draws: 250,
      wdl_losses: 250,
      pv_uci: ["c2c4"],
      depth: 20,
      seldepth: 24,
      nodes: 200000,
      engine_time_ms: 100,
    },
    {
      rank: 4,
      score_kind: "cp",
      score_value: -250,
      wdl_wins: 100,
      wdl_draws: 200,
      wdl_losses: 700,
      pv_uci: ["g1f3"],
      depth: 20,
      seldepth: 24,
      nodes: 200000,
      engine_time_ms: 100,
    },
    {
      rank: 5,
      score_kind: "cp",
      score_value: 10,
      wdl_wins: 400,
      wdl_draws: 300,
      wdl_losses: 300,
      pv_uci: ["not-a-move"],
      depth: 20,
      seldepth: 24,
      nodes: 200000,
      engine_time_ms: 100,
    },
  ],
  terminal_kind: null,
  completed_at: "2026-08-21T00:00:01+00:00",
  wall_time_ms: 100,
};

function observation(
  eligibility: EvaluationObservation["eligibility"],
  currentResult: EvaluationResult | null = null,
  currentStatus: EvaluationStatus | null = null,
  terminal = false,
): EvaluationObservation {
  return {
    fen: FEN,
    eligibility,
    result: currentResult,
    status: currentStatus,
    terminal,
  };
}

type DisplayStateInputs = Pick<
  AnalysisState,
  "observation" | "loading" | "error" | "actionError" | "actionPending"
>;

function displayFor(overrides: Partial<DisplayStateInputs> = {}): AnalysisPanelDisplay {
  return analysisPanelDisplay({
    observation: null,
    loading: false,
    error: null,
    actionError: null,
    actionPending: false,
    handleAction: async () => {},
    retryObservation: () => {},
    ...overrides,
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

const frame = (children: ReactNode) => <main className={styles.frame}>{children}</main>;
const panel = (args: ComponentProps<typeof AnalysisPanel>) => frame(<AnalysisPanel {...args} />);

export const Loading: Story = {
  name: "Loading - observation pending",
  args: panelArgs(displayFor({ loading: true })),
  render: (args) => panel(args),
};

export const Missing: Story = {
  name: "Missing - Analyze required",
  args: panelArgs(displayFor({ observation: observation("missing") })),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Analyze position" }));
    await expect(args.onAnalyze).toHaveBeenCalledTimes(1);
  },
};

export const Queued: Story = {
  name: "Queued - observed automatically",
  args: panelArgs(displayFor({ observation: observation("missing", null, status("queued")) })),
  render: (args) => panel(args),
};

export const Running: Story = {
  name: "Running - observed automatically",
  args: panelArgs(displayFor({ observation: observation("missing", null, status("running")) })),
  render: (args) => panel(args),
};

export const Complete: Story = {
  name: "Complete - five ranked lines and formatted values",
  args: panelArgs(displayFor({ observation: observation("eligible", result, status("done")) })),
  render: (args) => panel(args),
};

export const Stale: Story = {
  name: "Stale - Update required",
  args: panelArgs(displayFor({ observation: observation("stale", result, status("done")) })),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Update analysis" }));
    await expect(args.onUpdate).toHaveBeenCalledTimes(1);
  },
};

export const Failed: Story = {
  name: "Failed - Retry required",
  args: panelArgs(displayFor({ observation: observation("missing", null, status("failed")) })),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Retry analysis" }));
    await expect(args.onRetry).toHaveBeenCalledTimes(1);
  },
};

export const ObservationError: Story = {
  name: "Error - Observation retry",
  args: panelArgs(displayFor({ error: "Evaluation data is unavailable." })),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Retry observation" }));
    await expect(args.onRetryObservation).toHaveBeenCalledTimes(1);
  },
};

export const ActionPending: Story = {
  name: "Action pending - deliberate action disabled",
  args: panelArgs(displayFor({ observation: observation("missing"), actionPending: true })),
  render: (args) => panel(args),
};

export const ActionError: Story = {
  name: "Action error - retry remains deliberate",
  args: panelArgs(
    displayFor({
      observation: observation("missing"),
      actionError: "The analysis action could not be submitted.",
    }),
  ),
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Analyze position" }));
    await expect(args.onAnalyze).toHaveBeenCalledTimes(1);
  },
};

export const TerminalEmpty: Story = {
  name: "Complete - terminal empty result",
  args: panelArgs(
    displayFor({
      observation: observation(
        "eligible",
        { ...result, candidates: [], terminal_kind: "checkmate" },
        status("done"),
        true,
      ),
    }),
  ),
  render: (args) => panel(args),
};

export const Accessibility: Story = {
  name: "Accessibility - complete semantic presentation",
  args: panelArgs(displayFor({ observation: observation("eligible", result, status("done")) })),
  render: (args) => panel(args),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("heading", { level: 2, name: "Analysis" })).toBeVisible();
    await expect(canvas.getByRole("status")).toHaveTextContent("Analysis complete");
    await expect(canvas.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    await expect(canvas.getAllByRole("listitem")).toHaveLength(5);
    await expect(canvas.queryByRole("alert")).not.toBeInTheDocument();
  },
};
