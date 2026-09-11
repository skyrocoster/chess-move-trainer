import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import matchers from "@chialab/vitest-axe";
import type {} from "@chialab/vitest-axe/matchers";
import type { ComponentProps } from "react";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
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
    move: "e2e4",
    score: "+0.34",
    pv: "1. e4 e5 2. Nf3",
    wdl: displayWdl(42, 30, 28),
  },
  {
    rank: 2,
    move: "d2d4",
    score: "-M3",
    pv: "1. d4 d5",
    wdl: displayWdl(20, 30, 50),
  },
  {
    rank: 3,
    move: "c2c4",
    score: "+M3",
    pv: "1. c4",
    wdl: displayWdl(50, 25, 25),
  },
  {
    rank: 4,
    move: "g1f3",
    score: "-2.50",
    pv: "1. Nf3",
    wdl: displayWdl(10, 20, 70),
  },
  {
    rank: 5,
    move: "b1c3",
    score: "+0.10",
    pv: "Line unavailable",
    wdl: displayWdl(40, 30, 30),
  },
];

const DEFAULT_ACTIONS: AnalysisPanelDisplay["actions"] = {
  analyze: false,
  observationRetry: false,
  pending: false,
};

type DisplayOverrides = Omit<Partial<AnalysisPanelDisplay>, "actions"> & {
  actions?: Partial<AnalysisPanelDisplay["actions"]>;
};

function displayFor(overrides: DisplayOverrides = {}): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return {
    stateLabel: "Loading analysis…",
    error: null,
    requestError: null,
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
    message: { text: "Analyze this displayed position deliberately to request a result." },
    ...displayOverrides,
    actions: { analyze: true, ...actions },
  });
}

function queuedDisplay(state: "queued" | "running"): AnalysisPanelDisplay {
  return displayFor({
    stateLabel: state === "queued" ? "Analysis queued" : "Analysis running",
    message: {
      text: state === "queued" ? "This position is waiting for analysis." : "Analysis is in progress.",
    },
  });
}

function completeDisplay(
  lines: AnalysisPanelLine[] = DISPLAY_LINES,
  overrides: DisplayOverrides = {},
): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return displayFor({
    stateLabel: "Analysis complete",
    result: {
      lines,
      metadata: {
        displayedPly: 12,
        depth: lines.length > 0 ? 28 : null,
        candidateCount: lines.length,
      },
    },
    ...displayOverrides,
    actions: { ...actions },
  });
}

function errorDisplay(overrides: DisplayOverrides = {}): AnalysisPanelDisplay {
  const { actions, ...displayOverrides } = overrides;
  return displayFor({
    stateLabel: "Analysis unavailable",
    error: "The analysis could not be loaded.",
    ...displayOverrides,
    actions: { observationRetry: true, ...actions },
  });
}

type PanelCallbacks = Pick<
  ComponentProps<typeof AnalysisPanel>,
  "onAnalyze" | "onRetryObservation" | "onCandidateMove"
>;

function renderPanel(
  display: AnalysisPanelDisplay,
  overrides: Partial<PanelCallbacks> = {},
  embedded = false,
) {
  const callbacks: PanelCallbacks = {
    onAnalyze: vi.fn(),
    onRetryObservation: vi.fn(),
    ...overrides,
  };
  const rendered = render(<AnalysisPanel display={display} embedded={embedded} {...callbacks} />);
  return { ...callbacks, ...rendered };
}

afterEach(() => cleanup());

describe("AnalysisPanel", () => {
  it("keeps the standalone card surface by default and marks embedded mode as opt-in", () => {
    const standalone = renderPanel(completeDisplay());
    const standalonePanel = screen.getByRole("region", { name: "Analysis" });
    expect(standalonePanel).not.toHaveAttribute("data-embedded");
    standalone.unmount();

    renderPanel(completeDisplay(), {}, true);
    expect(screen.getByRole("region", { name: "Analysis" })).toHaveAttribute(
      "data-embedded",
      "true",
    );

    const panelCss = readFileSync(
      join(dirname(fileURLToPath(import.meta.url)), "AnalysisPanel.module.css"),
      "utf8",
    );
    expect(panelCss.match(/\.panel\s*\{[^}]*\}/)?.[0]).toContain(
      "border: 1px solid var(--md-sys-color-outline-variant);",
    );
    expect(panelCss.match(/\.panel\.embedded\s*\{[^}]*\}/)?.[0]).toContain("border: 0;");
    expect(panelCss).not.toContain(".staleMessage");
    expect(panelCss).not.toContain(".updateHelp");
  });

  it("renders the loading display without inventing controls", () => {
    renderPanel(displayFor());

    expect(screen.getByRole("heading", { level: 2, name: "Analysis" })).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("Loading analysis…");
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("shows not-requested results only behind a deliberate Analyze action", async () => {
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

  it("renders a complete result with five ranked lines, SAN, scores, and WDL without update controls", () => {
    renderPanel(completeDisplay());

    expect(screen.getByRole("status")).toHaveTextContent("Analysis complete");
    expect(screen.getByRole("heading", { level: 3, name: "Best line" })).toBeVisible();
    expect(screen.getByText("Displayed position · ply 12 · depth 28 · 5 lines")).toBeVisible();
    expect(screen.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    expect(screen.getAllByRole("listitem")).toHaveLength(4);
    expect(screen.getByText("+0.34")).toBeVisible();
    expect(screen.getByText("-M3")).toBeVisible();
    expect(screen.getByText("+M3")).toBeVisible();
    expect(screen.getByText("-2.50")).toBeVisible();
    expect(screen.getByText("1. e4 e5 2. Nf3")).toBeVisible();
    expect(screen.getByText("1. d4 d5")).toBeVisible();
    const bestLineFigure = screen.getByRole("figure");
    expect(within(bestLineFigure).getByText("42.0%", { exact: true })).toBeVisible();
    expect(within(bestLineFigure).getByText("30.0%", { exact: true })).toBeVisible();
    expect(within(bestLineFigure).getByText("28.0%", { exact: true })).toBeVisible();
    expect(
      within(bestLineFigure).getByRole("img", {
        name: "Win 42 percent, draw 30 percent, loss 28 percent",
      }),
    ).toBeVisible();
    expect(screen.getByText("Line unavailable")).toBeVisible();
    expect(screen.queryByRole("button", { name: "Update analysis" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Retry analysis" })).not.toBeInTheDocument();
  });

  it("exposes every candidate as a native pointer and keyboard control when controlled", async () => {
    const onCandidateMove = vi.fn();
    renderPanel(completeDisplay(), { onCandidateMove });
    const user = userEvent.setup();
    const bestLine = screen.getByRole("button", { name: "1. e4 e5 2. Nf3" });
    const alternativeLine = screen.getByRole("button", { name: "1. d4 d5" });

    expect(screen.getAllByRole("button")).toHaveLength(5);
    expect(bestLine).toHaveAttribute("type", "button");
    expect(alternativeLine).toHaveAttribute("type", "button");

    await user.tab();
    expect(bestLine).toHaveFocus();
    await user.keyboard("{Enter}");
    await user.keyboard(" ");
    expect(onCandidateMove).toHaveBeenNthCalledWith(2, "e2e4");

    await user.click(alternativeLine);
    expect(onCandidateMove).toHaveBeenNthCalledWith(3, "d2d4");
  });

  it("shows an observation error with only observation retry", async () => {
    const callbacks = renderPanel(errorDisplay());
    const user = userEvent.setup();

    expect(screen.getByRole("status")).toHaveTextContent("Analysis unavailable");
    expect(screen.getByRole("alert")).toHaveTextContent("The analysis could not be loaded.");
    expect(screen.getByRole("button", { name: "Retry observation" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Analyze position" })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Retry observation" }));

    expect(callbacks.onRetryObservation).toHaveBeenCalledOnce();
  });

  it("shows request errors without adding a failed lifecycle or retry control", () => {
    renderPanel(missingDisplay({ requestError: "The analysis request could not be submitted." }));

    expect(screen.getByRole("alert")).toHaveTextContent("The analysis request could not be submitted.");
    expect(screen.getByRole("button", { name: "Analyze position" })).toBeVisible();
    expect(screen.queryByRole("button", { name: "Retry analysis" })).not.toBeInTheDocument();
  });

  it("disables only the deliberate request while pending", async () => {
    const callbacks = renderPanel(missingDisplay({ actions: { pending: true } }));
    const user = userEvent.setup();
    const button = screen.getByRole("button", { name: "Analyze position" });

    expect(button).toBeDisabled();
    await user.click(button);
    expect(callbacks.onAnalyze).not.toHaveBeenCalled();
  });

  it("emits controlled Analyze and observation-retry intentions without automatic behavior", async () => {
    const display = displayFor({ actions: { analyze: true, observationRetry: true } });
    const callbacks = renderPanel(display);
    const user = userEvent.setup();

    expect(callbacks.onAnalyze).not.toHaveBeenCalled();
    expect(callbacks.onRetryObservation).not.toHaveBeenCalled();

    await user.click(screen.getByRole("button", { name: "Analyze position" }));
    await user.click(screen.getByRole("button", { name: "Retry observation" }));

    expect(callbacks.onAnalyze).toHaveBeenCalledOnce();
    expect(callbacks.onRetryObservation).toHaveBeenCalledOnce();
  });

  it("keeps status, alerts, list labeling, and native focus behavior semantic", async () => {
    const { onCandidateMove } = renderPanel(completeDisplay(), { onCandidateMove: vi.fn() });

    expect(screen.getByRole("heading", { level: 2, name: "Analysis" })).toHaveAttribute(
      "id",
      "analysis-panel-heading",
    );
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    expect(screen.getByRole("list", { name: "Ranked analysis lines" })).toBeVisible();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.getByRole("status")).not.toHaveAttribute("tabindex");
    expect(onCandidateMove).not.toHaveBeenCalled();
  });

  it("does not invent candidate lines for a terminal empty result", () => {
    renderPanel(completeDisplay([]));

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
