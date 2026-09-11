import { describe, expect, it, vi } from "vitest";

import type { AnalysisLine, AnalysisObservation, AnalysisResult } from "./analysisApi";
import { evaluationDisplay } from "./evalBarDisplay";
import type { AnalysisState } from "./analysisState";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const BASE_LINE: AnalysisLine = {
  rank: 1,
  score_kind: "cp",
  score_value: 34,
  wdl_wins: 420,
  wdl_draws: 300,
  wdl_losses: 280,
  pv_uci: ["e2e4"],
  depth: 20,
};

const result = (line: AnalysisLine): AnalysisResult => ({
  lines: [line],
  terminal_kind: null,
});

function analysisState(
  observation: AnalysisObservation | null = null,
  error: string | null = null,
): AnalysisState {
  return {
    observation,
    loading: false,
    error,
    requestError: null,
    requestPending: false,
    requestAnalysis: vi.fn(async () => undefined),
    retryObservation: vi.fn(),
  };
}

function observation(
  nextResult: AnalysisResult | null,
  state: AnalysisObservation["state"] = "ready",
): AnalysisObservation {
  return { fen: FEN, state, result: nextResult };
}

describe("evaluationDisplay", () => {
  it("uses a neutral readout when observation fails", () => {
    const display = evaluationDisplay(analysisState(null, "The analysis could not be loaded."));

    expect(display).toEqual({
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "Evaluation unavailable; evaluation neutral.",
    });
  });

  it.each([
    ["cp", BASE_LINE, "+0.34"],
    ["positive mate", { ...BASE_LINE, score_kind: "mate" as const, score_value: 3 }, "+M3"],
    ["negative mate", { ...BASE_LINE, score_kind: "mate" as const, score_value: -2 }, "-M2"],
  ] as const)("formats the %s line as the compact readout", (_kind, line, shortValue) => {
    const display = evaluationDisplay(analysisState(observation(result(line))));

    expect(display.shortValue).toBe(shortValue);
    expect(display.accessibleValue).toContain(shortValue);
    expect(display.state).toBe("best-line");
  });

  it("preserves pending and retained-line semantics", () => {
    const pending = evaluationDisplay(analysisState(observation(result(BASE_LINE), "queued")));
    const running = evaluationDisplay(
      analysisState(observation(result(BASE_LINE), "running"), "The analysis could not be loaded."),
    );

    expect(pending).toMatchObject({
      state: "pending",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "Analysis queued; evaluation pending.",
    });
    expect(running).toMatchObject({
      state: "pending",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "Analysis running; evaluation pending.",
    });
  });

  it("keeps a ready terminal observation neutral without inventing a line", () => {
    const display = evaluationDisplay(
      analysisState(observation({ lines: [], terminal_kind: "checkmate" })),
    );

    expect(display).toEqual({
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "No analysis yet; evaluation neutral.",
    });
  });

  it.each([
    ["minimum", -2000, 0, "-20.00"],
    ["maximum", 2000, 100, "+20.00"],
  ] as const)("clamps the %s CP line for the meter", (_bound, scoreValue, value, shortValue) => {
    const display = evaluationDisplay(
      analysisState(observation(result({ ...BASE_LINE, score_value: scoreValue }))),
    );

    expect(display).toMatchObject({ state: "best-line", value, shortValue });
  });
});
