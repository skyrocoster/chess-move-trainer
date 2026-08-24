import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import { AnalysisPanel } from "./AnalysisPanel";
import type {
  AnalysisClient,
  EvaluationObservation,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";
import { STAGE1_GAME } from "./stage1GameTypes";
import styles from "./Stage1Story.module.css";

const FEN = STAGE1_GAME.positions[0].fen;

const meta = {
  title: "Application/Viewer/Analysis Panel",
  component: AnalysisPanel,
  parameters: { layout: "fullscreen" },
  args: { fen: FEN },
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
    ...[2, 3, 4, 5].map((rank) => ({
      rank,
      score_kind: "cp" as const,
      score_value: 20 - rank,
      wdl_wins: 400,
      wdl_draws: 300,
      wdl_losses: 300,
      pv_uci: ["d2d4"],
      depth: 20,
      seldepth: 24,
      nodes: 200000,
      engine_time_ms: 100,
    })),
  ],
  terminal_kind: null,
  completed_at: "2026-08-21T00:00:01+00:00",
  wall_time_ms: 100,
};

function observation(
  eligibility: EvaluationObservation["eligibility"],
  currentResult: EvaluationResult | null = null,
  currentStatus: EvaluationStatus | null = null,
): EvaluationObservation {
  return {
    fen: FEN,
    eligibility,
    result: currentResult,
    status: currentStatus,
    terminal: false,
  };
}

function clientFor(value: EvaluationObservation): AnalysisClient {
  return {
    observe: fn(async () => ({ status: "success" as const, data: value })),
    enqueue: fn(async (_fen, action) => ({
      status: "success",
      data: {
        fen: FEN,
        action,
        outcome: "queued",
        eligibility: value.eligibility,
        status: status("queued"),
      },
    })),
    status: fn(async () => ({
      status: "success" as const,
      data: {
        fen: FEN,
        state: "queued" as const,
        completed_at: null,
        error_code: null,
      },
    })),
  };
}

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const panel = (args: React.ComponentProps<typeof AnalysisPanel>, pollIntervalMs = 60000) =>
  frame(<AnalysisPanel {...args} pollIntervalMs={pollIntervalMs} />);

export const Eligible: Story = {
  name: "Eligible - auto-loaded",
  args: { client: clientFor(observation("eligible", result)) },
  render: (args) => panel(args),
};

export const Missing: Story = {
  name: "Missing - Analyze required",
  args: { client: clientFor(observation("missing")) },
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Analyze position" }));
    await expect(args.client?.enqueue).toHaveBeenCalledTimes(1);
    await expect(args.client?.enqueue).toHaveBeenCalledWith(
      FEN,
      "analyze",
      expect.any(AbortSignal),
    );
  },
};

export const Stale: Story = {
  name: "Stale - Update required",
  args: { client: clientFor(observation("stale", result)) },
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Update analysis" }));
    await expect(args.client?.enqueue).toHaveBeenCalledTimes(1);
    await expect(args.client?.enqueue).toHaveBeenCalledWith(FEN, "update", expect.any(AbortSignal));
  },
};

export const Queued: Story = {
  name: "Queued - observed automatically",
  args: { client: clientFor(observation("missing", null, status("queued"))) },
  render: (args) => panel(args),
};

export const Running: Story = {
  name: "Running - observed automatically",
  args: { client: clientFor(observation("missing", null, status("running"))) },
  render: (args) => panel(args),
};

export const Completed: Story = {
  name: "Completed - five ranked lines",
  args: { client: clientFor(observation("eligible", result, status("done"))) },
  render: (args) => panel(args),
};

export const Failed: Story = {
  name: "Failed - Retry required",
  args: { client: clientFor(observation("missing", null, status("failed"))) },
  render: (args) => panel(args),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Retry analysis" }));
    await expect(args.client?.enqueue).toHaveBeenCalledTimes(1);
    await expect(args.client?.enqueue).toHaveBeenCalledWith(FEN, "retry", expect.any(AbortSignal));
  },
};
