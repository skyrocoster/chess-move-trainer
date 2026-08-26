import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import type { ComponentProps } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AnalysisPanel } from "./AnalysisPanel";
import type { AnalysisPanelDisplay } from "./analysisFormatting";
import { analysisPanelDisplay } from "./analysisFormatting";
import type { EvaluationObservation, EvaluationResult, EvaluationStatus } from "./analysisApi";
import type { AnalysisState } from "./analysisState";

expect.extend(matchers);

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function queueStatus(state: EvaluationStatus["state"]): EvaluationStatus {
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

function result(): EvaluationResult {
  return {
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
}

function observation(
  eligibility: EvaluationObservation["eligibility"],
  currentResult: EvaluationResult | null = null,
  status: EvaluationStatus | null = null,
  terminal = false,
): EvaluationObservation {
  return { fen: FEN, eligibility, result: currentResult, status, terminal };
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
    handleAction: vi.fn(),
    retryObservation: vi.fn(),
    ...overrides,
  });
}

type PanelCallbacks = Pick<
  ComponentProps<typeof AnalysisPanel>,
  "onAnalyze" | "onUpdate" | "onRetry" | "onRetryObservation"
>;

function renderPanel(display: AnalysisPanelDisplay, overrides: Partial<PanelCallbacks> = {}) {
  const callbacks: PanelCallbacks = {
    onAnalyze: vi.fn(),
    onUpdate: vi.fn(),
    onRetry: vi.fn(),
    onRetryObservation: vi.fn(),
    ...overrides,
  };
  const rendered = render(<AnalysisPanel display={display} {...callbacks} />);
  return { ...callbacks, ...rendered };
}

afterEach(() => cleanup());

describe("AnalysisPanel", () => {
  it("renders the loading display without inventing controls", () => {
    renderPanel(displayFor({ loading: true }));

    expect(screen.getByRole("heading", { level: 2, name: "Analysis" })).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("Loading evaluation…");
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("shows missing results only behind a deliberate Analyze action", async () => {
    const callbacks = renderPanel(displayFor({ observation: observation("missing") }));
    const user = userEvent.setup();

    expect(screen.getByRole("status")).toHaveTextContent("Analysis available on request");
    expect(
      screen.getByText("Analyze this displayed position deliberately to request a result."),
    ).toBeVisible();
    expect(screen.getByRole("button", { name: "Analyze position" })).toBeVisible();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(callbacks.onAnalyze).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Analyze position" }));

    expect(callbacks.onAnalyze).toHaveBeenCalledOnce();
  });

  it.each([
    ["queued", "Analysis queued", "This position is waiting for analysis."],
    ["running", "Analysis running", "Analysis is in progress."],
  ] as const)("renders the %s display without action controls", (state, label, message) => {
    renderPanel(displayFor({ observation: observation("missing", null, queueStatus(state)) }));

    expect(screen.getByRole("status")).toHaveTextContent(label);
    expect(screen.getByText(message)).toBeVisible();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("renders a complete result with five ranked lines, SAN, scores, WDL, and fallback text", () => {
    renderPanel(
      displayFor({
        observation: observation("eligible", result(), queueStatus("done")),
      }),
    );

    expect(screen.getByRole("status")).toHaveTextContent("Analysis complete");
    expect(screen.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    expect(screen.getAllByRole("listitem")).toHaveLength(5);
    expect(screen.getByText("+0.34")).toBeVisible();
    expect(screen.getByText("-M3")).toBeVisible();
    expect(screen.getByText("+M")).toBeVisible();
    expect(screen.getByText("-2.50")).toBeVisible();
    expect(screen.getByText("1. e4 e5 2. Nf3")).toBeVisible();
    expect(screen.getByText("1. d4 d5")).toBeVisible();
    expect(screen.getByText("W 42.0% / D 30.0% / L 28.0%")).toBeVisible();
    expect(screen.getByText("W 20.0% / D 30.0% / L 50.0%")).toBeVisible();
    expect(screen.getByText("Line unavailable")).toBeVisible();
    expect(screen.getByRole("button", { name: "Update analysis" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Analyze position" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Retry analysis" })).not.toBeInTheDocument();
  });

  it("labels stale results and emits a deliberate Update intention", async () => {
    const callbacks = renderPanel(
      displayFor({ observation: observation("stale", result(), queueStatus("done")) }),
    );
    const user = userEvent.setup();

    expect(screen.getByRole("status")).toHaveTextContent("Stale analysis");
    expect(screen.getByText("Stale analysis; update deliberately to refresh it.")).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Update analysis" }));

    expect(callbacks.onUpdate).toHaveBeenCalledOnce();
  });

  it("shows failed analysis as an alert and emits a deliberate Retry intention", async () => {
    const callbacks = renderPanel(
      displayFor({
        observation: observation("missing", null, queueStatus("failed")),
      }),
    );
    const user = userEvent.setup();

    expect(screen.getByRole("status")).toHaveTextContent("Analysis failed");
    expect(screen.getByRole("alert")).toHaveTextContent(
      "No complete result was published. Retry deliberately when ready.",
    );
    expect(screen.getByRole("button", { name: "Retry analysis" })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Retry analysis" }));

    expect(callbacks.onRetry).toHaveBeenCalledOnce();
  });

  it("shows an observation error and only retries observation deliberately", async () => {
    const callbacks = renderPanel(displayFor({ error: "Evaluation data is unavailable." }));
    const user = userEvent.setup();

    expect(screen.getByRole("status")).toHaveTextContent("Evaluation unavailable");
    expect(screen.getByRole("alert")).toHaveTextContent("Evaluation data is unavailable.");
    expect(screen.getByRole("button", { name: "Retry observation" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Analyze position" })).not.toBeInTheDocument();
    expect(callbacks.onRetryObservation).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Retry observation" }));

    expect(callbacks.onRetryObservation).toHaveBeenCalledOnce();
  });

  it("renders action errors as alerts without changing deliberate action ownership", async () => {
    const callbacks = renderPanel(
      displayFor({
        observation: observation("missing"),
        actionError: "The analysis action could not be submitted.",
      }),
    );
    const user = userEvent.setup();

    expect(screen.getByRole("alert")).toHaveTextContent(
      "The analysis action could not be submitted.",
    );
    expect(screen.getByRole("button", { name: "Analyze position" })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "Analyze position" }));

    expect(callbacks.onAnalyze).toHaveBeenCalledOnce();
  });

  it("disables only the pending analysis actions", async () => {
    const cases = [
      [observation("missing"), "Analyze position"],
      [observation("eligible", result(), queueStatus("done")), "Update analysis"],
      [observation("missing", null, queueStatus("failed")), "Retry analysis"],
    ] as const;

    for (const [currentObservation, buttonName] of cases) {
      cleanup();
      const callbacks = renderPanel(
        displayFor({ observation: currentObservation, actionPending: true }),
      );
      const user = userEvent.setup();
      const button = screen.getByRole("button", { name: buttonName });

      expect(button).toBeDisabled();
      await user.click(button);
      expect(callbacks.onAnalyze).not.toHaveBeenCalled();
      expect(callbacks.onUpdate).not.toHaveBeenCalled();
      expect(callbacks.onRetry).not.toHaveBeenCalled();
    }
  });

  it("emits each controlled intention without automatic behavior", async () => {
    const display: AnalysisPanelDisplay = {
      stateLabel: "Controlled action fixture",
      error: null,
      actionError: null,
      message: null,
      result: null,
      actions: {
        analyze: true,
        update: true,
        retry: true,
        observationRetry: true,
        pending: false,
      },
    };
    const callbacks = renderPanel(display);
    const user = userEvent.setup();

    expect(callbacks.onAnalyze).not.toHaveBeenCalled();
    expect(callbacks.onUpdate).not.toHaveBeenCalled();
    expect(callbacks.onRetry).not.toHaveBeenCalled();
    expect(callbacks.onRetryObservation).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Analyze position" }));
    await user.click(screen.getByRole("button", { name: "Update analysis" }));
    await user.click(screen.getByRole("button", { name: "Retry analysis" }));
    await user.click(screen.getByRole("button", { name: "Retry observation" }));

    expect(callbacks.onAnalyze).toHaveBeenCalledOnce();
    expect(callbacks.onUpdate).toHaveBeenCalledOnce();
    expect(callbacks.onRetry).toHaveBeenCalledOnce();
    expect(callbacks.onRetryObservation).toHaveBeenCalledOnce();
  });

  it("keeps status, alerts, list labeling, and native focus behavior semantic", async () => {
    const callbacks = renderPanel(
      displayFor({
        observation: observation("eligible", result(), queueStatus("done")),
      }),
    );
    const user = userEvent.setup();
    const update = screen.getByRole("button", { name: "Update analysis" });

    expect(screen.getByRole("heading", { level: 2, name: "Analysis" })).toHaveAttribute(
      "id",
      "analysis-panel-heading",
    );
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    expect(screen.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.getByRole("status")).not.toHaveAttribute("tabindex");

    await user.tab();
    expect(update).toHaveFocus();
    await user.click(update);

    expect(update).toHaveFocus();
    expect(callbacks.onUpdate).toHaveBeenCalledOnce();
  });

  it("does not invent candidate lines for a terminal empty result", () => {
    const terminal = {
      ...result(),
      candidates: [],
      terminal_kind: "checkmate",
    };
    renderPanel(
      displayFor({
        observation: observation("eligible", terminal, queueStatus("done"), true),
      }),
    );

    expect(
      screen.getByText("No candidate lines are available for this terminal position."),
    ).toBeVisible();
    expect(screen.queryByRole("list", { name: "Ranked analysis lines" })).not.toBeInTheDocument();
  });

  it("has no focused accessibility violations", async () => {
    const { container } = renderPanel(
      displayFor({
        observation: observation("eligible", result(), queueStatus("done")),
      }),
    );

    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
