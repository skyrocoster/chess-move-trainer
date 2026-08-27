import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import type { ComponentProps } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  AnalysisPanel,
  type AnalysisPanelDisplay,
  type AnalysisPanelLine,
  type AnalysisPanelWdl,
} from "./AnalysisPanel";

expect.extend(matchers);

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
    renderPanel(displayFor());

    expect(screen.getByRole("heading", { level: 2, name: "Analysis" })).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("Loading evaluation…");
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("shows missing results only behind a deliberate Analyze action", async () => {
    const callbacks = renderPanel(missingDisplay());
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
    renderPanel(queuedDisplay(state));

    expect(screen.getByRole("status")).toHaveTextContent(label);
    expect(screen.getByText(message)).toBeVisible();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("renders a complete result with five ranked lines, SAN, scores, WDL, and fallback text", async () => {
    renderPanel(completeDisplay());

    expect(screen.getByRole("status")).toHaveTextContent("Analysis complete");
    expect(screen.getByRole("heading", { level: 3, name: "Best line" })).toBeVisible();
    expect(screen.getByText("Displayed position · ply 12 · depth 28 · 5 lines")).toBeVisible();
    expect(screen.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    expect(screen.getAllByRole("listitem")).toHaveLength(4);
    expect(screen.getByText("+0.34")).toBeVisible();
    expect(screen.getByText("-M3")).toBeVisible();
    expect(screen.getByText("+M")).toBeVisible();
    expect(screen.getByText("-2.50")).toBeVisible();
    expect(screen.getByText("1. e4 e5 2. Nf3")).toBeVisible();
    expect(screen.getByText("1. d4 d5")).toBeVisible();
    const bestLineFigure = screen.getByRole("figure");
    expect(within(bestLineFigure).getByText("42.0%", { exact: true })).toBeVisible();
    expect(within(bestLineFigure).getByText("30.0%", { exact: true })).toBeVisible();
    expect(within(bestLineFigure).getByText("28.0%", { exact: true })).toBeVisible();
    const bestLineTrack = within(bestLineFigure).getByRole("img", {
      name: "Win 42 percent, draw 30 percent, loss 28 percent",
    });
    expect(bestLineTrack).toBeVisible();
    const segments = bestLineTrack.querySelectorAll(":scope > span");
    expect(segments).toHaveLength(3);
    expect(Array.from(segments, (segment) => (segment as HTMLElement).style.inlineSize)).toEqual([
      "42%",
      "30%",
      "28%",
    ]);
    expect(
      screen.getByRole("img", {
        name: "Line 2: Win 20 percent, draw 30 percent, loss 50 percent",
      }),
    ).toBeVisible();
    expect(screen.getByText("Line unavailable")).toBeVisible();
    expect(screen.getByRole("button", { name: "Update analysis" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Analyze position" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Retry analysis" })).not.toBeInTheDocument();
  });

  it("labels stale results and emits a deliberate Update intention", async () => {
    const callbacks = renderPanel(completeDisplay(true));
    const user = userEvent.setup();

    expect(screen.getByRole("status")).toHaveTextContent("Stale analysis");
    expect(
      screen.getByText(
        "This result is from an earlier position. Update deliberately to refresh it.",
      ),
    ).toBeVisible();
    expect(screen.getByRole("note")).toHaveTextContent("earlier position");

    await user.click(screen.getByRole("button", { name: "Update analysis" }));

    expect(callbacks.onUpdate).toHaveBeenCalledOnce();
  });

  it("shows failed analysis as an alert and emits a deliberate Retry intention", async () => {
    const callbacks = renderPanel(failedDisplay());
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
    const callbacks = renderPanel(errorDisplay());
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
      missingDisplay({ actionError: "The analysis action could not be submitted." }),
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
    const cases: [AnalysisPanelDisplay, string][] = [
      [missingDisplay({ actions: { pending: true } }), "Analyze position"],
      [completeDisplay(false, DISPLAY_LINES, { actions: { pending: true } }), "Update analysis"],
      [failedDisplay({ actions: { pending: true } }), "Retry analysis"],
    ];

    for (const [display, buttonName] of cases) {
      cleanup();
      const callbacks = renderPanel(display);
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
    const callbacks = renderPanel(completeDisplay());
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
    renderPanel(completeDisplay(false, []));

    expect(
      screen.getByText("No candidate lines are available for this terminal position."),
    ).toBeVisible();
    expect(screen.getByRole("note")).toHaveTextContent("terminal position");
    expect(screen.queryByRole("heading", { level: 3, name: "Best line" })).not.toBeInTheDocument();
    expect(screen.queryByRole("list", { name: "Ranked analysis lines" })).not.toBeInTheDocument();
  });

  it("has no focused accessibility violations", async () => {
    const { container } = renderPanel(completeDisplay());

    expect(await axe.run({ include: [container] })).toHaveNoViolations();
  });
});
