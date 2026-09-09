import { describe, expect, it, vi } from "vitest";

import type {
  EvaluationCandidate,
  EvaluationObservation,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";
import { evaluationDisplay } from "./evalBarDisplay";
import type { AnalysisState } from "./analysisState";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

const candidate: EvaluationCandidate = {
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
};

const result = (nextCandidate: EvaluationCandidate): EvaluationResult => ({
  fen: FEN,
  profile_id: "mp09-balanced-nodes-v2-200000",
  candidates: [nextCandidate],
  terminal_kind: null,
  completed_at: "2026-08-21T00:00:01+00:00",
  wall_time_ms: 100,
});

const status = (state: EvaluationStatus["state"]): EvaluationStatus => ({
  state,
  position: 0,
  attempts: 1,
  enqueued_at: "2026-08-21T00:00:00+00:00",
  started_at: null,
  completed_at: null,
  error_code: null,
});

function analysisState(
  observation: EvaluationObservation | null = null,
  error: string | null = null,
): AnalysisState {
  return {
    observation,
    loading: false,
    error,
    actionError: null,
    actionPending: false,
    handleAction: vi.fn(async () => undefined),
    retryObservation: vi.fn(),
  };
}

function observation(
  nextResult: EvaluationResult | null,
  nextStatus: EvaluationStatus | null = null,
  eligibility: EvaluationObservation["eligibility"] = "eligible",
): EvaluationObservation {
  return { fen: FEN, eligibility, result: nextResult, status: nextStatus, terminal: false };
}

describe("evaluationDisplay", () => {
  it("uses a neutral short readout without deriving it from accessible prose", () => {
    const display = evaluationDisplay(analysisState(null, "Evaluation data is unavailable."));

    expect(display).toEqual({
      state: "neutral",
      value: 50,
      shortValue: "0.00",
      accessibleValue: "Evaluation unavailable; evaluation neutral.",
    });
  });

  it.each([
    ["cp", candidate, "+0.34"],
    ["positive mate", { ...candidate, score_kind: "mate" as const, score_value: 3 }, "+M3"],
    ["mate", { ...candidate, score_kind: "mate" as const, score_value: -2 }, "-M2"],
    ["mate_given", { ...candidate, score_kind: "mate_given" as const, score_value: 0 }, "+M"],
  ] as const)(
    "formats the %s candidate as the compact readout",
    (_kind, nextCandidate, shortValue) => {
      const display = evaluationDisplay(analysisState(observation(result(nextCandidate))));

      expect(display.shortValue).toBe(shortValue);
      expect(display.accessibleValue).toContain(shortValue);
      expect(display.state).toBe("best-line");
    },
  );

  it("preserves pending and retained-candidate semantics independently of the short readout", () => {
    const pending = evaluationDisplay(
      analysisState(observation(result(candidate), status("queued"), "stale")),
    );
    const failed = evaluationDisplay(
      analysisState(observation(result(candidate), status("failed"), "stale")),
    );

    expect(pending).toMatchObject({
      state: "pending",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "Analysis queued; evaluation pending.",
    });
    expect(failed).toMatchObject({
      state: "best-line",
      value: 51.7,
      shortValue: "+0.34",
      accessibleValue: "Stale best-line evaluation +0.34.",
    });
  });

  it.each([
    ["stale", "stale", null, "No analysis yet; evaluation neutral."],
    ["failed", "eligible", status("failed"), "Analysis failed; evaluation neutral."],
  ] as const)(
    "keeps a %s observation without a retained candidate neutral",
    (_state, eligibility, nextStatus, accessibleValue) => {
      const display = evaluationDisplay(analysisState(observation(null, nextStatus, eligibility)));

      expect(display).toEqual({
        state: "neutral",
        value: 50,
        shortValue: "0.00",
        accessibleValue,
      });
    },
  );

  it.each([
    ["minimum", -2000, 0, "-20.00"],
    ["maximum", 2000, 100, "+20.00"],
  ] as const)(
    "clamps the %s CP candidate for the meter",
    (_bound, scoreValue, value, shortValue) => {
      const display = evaluationDisplay(
        analysisState(observation(result({ ...candidate, score_value: scoreValue }))),
      );

      expect(display).toMatchObject({ state: "best-line", value, shortValue });
    },
  );
});
