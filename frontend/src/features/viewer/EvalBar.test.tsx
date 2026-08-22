import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import { afterEach, describe, expect, it } from "vitest";

import { EvalBar } from "./EvalBar";
import type { EvaluationObservation, EvaluationResult, EvaluationStatus } from "./analysisApi";
import type { AnalysisState } from "./analysisState";

expect.extend(matchers);

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

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

const bestLine: EvaluationResult = {
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
  result: EvaluationResult | null = null,
  currentStatus: EvaluationStatus | null = null,
): EvaluationObservation {
  return { fen: FEN, eligibility, result, status: currentStatus, terminal: false };
}

function state(value: EvaluationObservation | null, error: string | null = null): AnalysisState {
  return {
    observation: value,
    loading: false,
    error,
    actionError: null,
    actionPending: false,
    handleAction: async () => undefined,
    retryObservation: () => undefined,
  };
}

afterEach(() => cleanup());

describe("EvalBar", () => {
  it("always reserves a neutral accessible meter before analysis", async () => {
    const user = userEvent.setup();
    const { container } = render(<EvalBar orientation="white" analysisState={state(null)} />);
    const meter = screen.getByRole("meter", { name: "Evaluation" });

    expect(meter).toHaveAttribute("data-state", "neutral");
    expect(meter).toHaveAttribute("data-orientation", "white");
    expect(meter).toHaveAttribute("aria-valuetext", "No analysis yet; evaluation neutral.");
    expect(screen.getByText("No analysis yet; evaluation neutral.")).toBeVisible();

    await user.tab();
    expect(document.activeElement).not.toBe(meter);
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });

  it.each([
    ["queued", "Analysis queued; evaluation pending."],
    ["running", "Analysis running; evaluation pending."],
  ] as const)("shows the %s pending state without inventing an evaluation", (queueState, value) => {
    render(
      <EvalBar
        orientation="black"
        analysisState={state(observation("missing", null, status(queueState)))}
      />,
    );
    const meter = screen.getByRole("meter", { name: "Evaluation" });

    expect(meter).toHaveAttribute("data-state", "pending");
    expect(meter).toHaveAttribute("data-orientation", "black");
    expect(meter).toHaveAttribute("aria-valuetext", value);
    expect(screen.getByText(value)).toBeVisible();
  });

  it("shows the completed White-relative best-line evaluation and flips with Black orientation", async () => {
    const { container } = render(
      <EvalBar
        orientation="black"
        analysisState={state(observation("eligible", bestLine, status("done")))}
      />,
    );
    const meter = screen.getByRole("meter", { name: "Evaluation" });

    expect(meter).toHaveAttribute("data-state", "best-line");
    expect(meter).toHaveAttribute("data-orientation", "black");
    expect(meter).toHaveAttribute("aria-valuetext", "best-line evaluation +0.34.");
    expect(screen.getByText("best-line evaluation +0.34.")).toBeVisible();
    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
