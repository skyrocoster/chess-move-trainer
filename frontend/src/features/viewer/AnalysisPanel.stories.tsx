import type { Meta, StoryObj } from "@storybook/react-vite";

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
  title: "Viewer/MP-10/Analysis Panel",
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
    observe: async () => ({ status: "success", data: value }),
    enqueue: async () => ({
      status: "success",
      data: {
        fen: FEN,
        action: "analyze" as const,
        outcome: "queued",
        eligibility: value.eligibility,
        status: status("queued"),
      },
    }),
    status: async () => ({
      status: "success",
      data: { fen: FEN, state: "queued" as const, completed_at: null, error_code: null },
    }),
  };
}

const frame = (children: React.ReactNode) => <main className={styles.frame}>{children}</main>;
const panel = (value: EvaluationObservation, pollIntervalMs = 60000) =>
  frame(<AnalysisPanel fen={FEN} client={clientFor(value)} pollIntervalMs={pollIntervalMs} />);

export const Eligible: Story = {
  name: "Eligible - auto-loaded",
  render: () => panel(observation("eligible", result)),
};

export const Missing: Story = {
  name: "Missing - Analyze required",
  render: () => panel(observation("missing")),
};

export const Stale: Story = {
  name: "Stale - Update required",
  render: () => panel(observation("stale", result)),
};

export const Queued: Story = {
  name: "Queued - observed automatically",
  render: () => panel(observation("missing", null, status("queued"))),
};

export const Running: Story = {
  name: "Running - observed automatically",
  render: () => panel(observation("missing", null, status("running"))),
};

export const Completed: Story = {
  name: "Completed - five ranked lines",
  render: () => panel(observation("eligible", result, status("done"))),
};

export const Failed: Story = {
  name: "Failed - Retry required",
  render: () => panel(observation("missing", null, status("failed"))),
};
