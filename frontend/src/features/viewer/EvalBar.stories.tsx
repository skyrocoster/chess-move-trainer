import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/cmt-tokens.css";
import "../../styles/cmt-typescale.css";
import type { EvaluationObservation, EvaluationResult, EvaluationStatus } from "./analysisApi";
import { EvalBar } from "./EvalBar";
import type { AnalysisState } from "./analysisState";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

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
      pv_uci: ["e2e4"],
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
): EvaluationObservation {
  return {
    fen: FEN,
    eligibility,
    result: currentResult,
    status: currentStatus,
    terminal: false,
  };
}

function state(value: EvaluationObservation): AnalysisState {
  return {
    observation: value,
    loading: false,
    error: null,
    actionError: null,
    actionPending: false,
    handleAction: async () => undefined,
    retryObservation: () => undefined,
  };
}

export const Neutral: Story = {
  name: "Neutral - before analysis",
  args: { orientation: "white", analysisState: state(observation("missing")) },
};

export const Queued: Story = {
  name: "Queued - pending analysis",
  args: {
    orientation: "white",
    analysisState: state(observation("missing", null, status("queued"))),
  },
};

export const Running: Story = {
  name: "Running - pending analysis",
  args: {
    orientation: "black",
    analysisState: state(observation("missing", null, status("running"))),
  },
};

export const BestLine: Story = {
  name: "Best line - completed evaluation",
  args: {
    orientation: "black",
    analysisState: state(observation("eligible", result, status("done"))),
  },
};
