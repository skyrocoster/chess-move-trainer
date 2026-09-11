import { describe, expect, it } from "vitest";

import type { AnalysisLine, AnalysisObservation, AnalysisResult } from "./analysisApi";
import type { AnalysisState } from "./analysisState";
import { analysisPanelDisplay } from "./analysisFormatting";
import type { Fen } from "../chess/chessPrimitives";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" as Fen;

const BASE_LINE: AnalysisLine = {
  rank: 1,
  score_kind: "cp",
  score_value: 34,
  wdl_wins: 420,
  wdl_draws: 300,
  wdl_losses: 280,
  pv_uci: ["e2e4"],
  depth: 28,
};

function line(overrides: Partial<AnalysisLine> = {}): AnalysisLine {
  return { ...BASE_LINE, ...overrides };
}

function result(lines: AnalysisLine[]): AnalysisResult {
  return { lines, terminal_kind: null };
}

function state(
  nextState: AnalysisObservation["state"],
  nextResult: AnalysisResult | null,
  error: string | null = null,
): AnalysisState {
  const observation: AnalysisObservation = { fen: FEN, state: nextState, result: nextResult };
  return {
    observation,
    loading: false,
    error,
    requestError: null,
    requestPending: false,
    requestAnalysis: async () => undefined,
    retryObservation: () => undefined,
  };
}

describe("analysisPanelDisplay", () => {
  it("derives percentage geometry, one-decimal labels, and an accessible aggregate", () => {
    const display = analysisPanelDisplay(
      state("ready", result([line({ wdl_wins: 421, wdl_draws: 309, wdl_losses: 270 })])),
      { displayedPly: 12 },
    );

    expect(display.result).toEqual({
      metadata: { displayedPly: 12, depth: 28, candidateCount: 1 },
      lines: [
        {
          rank: 1,
          move: "e2e4",
          score: "+0.34",
          pv: "1. e4",
          wdl: {
            wins: { percentage: 42.1, label: "42.1%" },
            draws: { percentage: 30.9, label: "30.9%" },
            losses: { percentage: 27, label: "27.0%" },
            accessibleLabel: "Win 42.1 percent, draw 30.9 percent, loss 27 percent",
          },
        },
      ],
    });
  });

  it("keeps score kinds, SAN conversion, fallback text, ranks, and fewer-than-five lines", () => {
    const display = analysisPanelDisplay(
      state(
        "ready",
        result([
          line({ rank: 1, score_kind: "cp", score_value: 34, pv_uci: ["e2e4"] }),
          line({ rank: 2, score_kind: "mate", score_value: -3, pv_uci: ["d2d4"] }),
          line({ rank: 3, score_kind: "mate", score_value: 3, pv_uci: ["c2c4"] }),
          line({ rank: 4, score_kind: "cp", score_value: -250, pv_uci: ["a1a1"] }),
        ]),
      ),
    );

    expect(display.result?.metadata).toEqual({
      displayedPly: null,
      depth: 28,
      candidateCount: 4,
    });
    expect(display.result?.lines).toHaveLength(4);
    expect(display.result?.lines.map((nextLine) => [nextLine.rank, nextLine.score, nextLine.pv])).toEqual([
      [1, "+0.34", "1. e4"],
      [2, "-M3", "1. d4"],
      [3, "+M3", "1. c4"],
      [4, "-2.50", "Line unavailable"],
    ]);
  });

  it("bounds the rendered line ledger to five lines", () => {
    const display = analysisPanelDisplay(
      state(
        "ready",
        result(Array.from({ length: 6 }, (_, index) => line({ rank: index + 1, score_value: index * 10 }))),
      ),
    );

    expect(display.result?.metadata.candidateCount).toBe(6);
    expect(display.result?.lines).toHaveLength(5);
    expect(display.result?.lines.map((nextLine) => nextLine.rank)).toEqual([1, 2, 3, 4, 5]);
  });

  it("keeps terminal result empty and removes update/retry derivation", () => {
    const display = analysisPanelDisplay(
      state("ready", { lines: [], terminal_kind: "checkmate" }),
      { displayedPly: 24 },
    );

    expect(display.result).toEqual({
      metadata: { displayedPly: 24, depth: null, candidateCount: 0 },
      lines: [],
    });
    expect(display.actions).toEqual({ analyze: false, observationRetry: false, pending: false });
  });

  it("shows a deliberate request only for the clean not-requested state", () => {
    const display = analysisPanelDisplay(state("not_requested", null));

    expect(display.result).toBeNull();
    expect(display.actions.analyze).toBe(true);
  });

  it("uses the observation FEN for retained-result PV formatting", () => {
    const counterVariant = `${FEN.slice(0, -3)}17 42` as Fen;
    const display = analysisPanelDisplay({
      ...state("running", result([line()])),
      observation: { fen: counterVariant, state: "running", result: result([line()]) },
    });

    expect(display.result?.lines[0]?.pv).toBe("42. e4");
    expect(display.stateLabel).toBe("Analysis running");
  });
});
