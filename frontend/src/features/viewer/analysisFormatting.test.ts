import { describe, expect, it } from "vitest";

import type { EvaluationCandidate, EvaluationResult, EvaluationStatus } from "./analysisApi";
import type { AnalysisState } from "./analysisState";
import { analysisPanelDisplay } from "./analysisFormatting";
import type { Fen } from "./chessPrimitives";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" as Fen;

const DONE_STATUS: EvaluationStatus = {
  state: "done",
  position: 0,
  attempts: 1,
  enqueued_at: "2026-08-21T00:00:00+00:00",
  started_at: "2026-08-21T00:00:00+00:00",
  completed_at: "2026-08-21T00:00:01+00:00",
  error_code: null,
};

const BASE_CANDIDATE: EvaluationCandidate = {
  rank: 1,
  score_kind: "cp",
  score_value: 34,
  wdl_wins: 420,
  wdl_draws: 300,
  wdl_losses: 280,
  pv_uci: ["e2e4"],
  depth: 28,
  seldepth: 32,
  nodes: 200_000,
  engine_time_ms: 100,
};

function candidate(overrides: Partial<EvaluationCandidate> = {}): EvaluationCandidate {
  return { ...BASE_CANDIDATE, ...overrides };
}

function evaluationResult(candidates: EvaluationCandidate[]): EvaluationResult {
  return {
    fen: FEN,
    profile_id: "test-profile",
    candidates,
    terminal_kind: null,
    completed_at: "2026-08-21T00:00:01+00:00",
    wall_time_ms: 100,
  };
}

function completedState(result: EvaluationResult, terminal = false): AnalysisState {
  return {
    observation: {
      fen: FEN,
      eligibility: "eligible",
      result,
      status: DONE_STATUS,
      terminal,
    },
    loading: false,
    error: null,
    actionError: null,
    actionPending: false,
    handleAction: async () => undefined,
    retryObservation: () => undefined,
  };
}

function missingState(): AnalysisState {
  return {
    observation: {
      fen: FEN,
      eligibility: "missing",
      result: null,
      status: null,
      terminal: false,
    },
    loading: false,
    error: null,
    actionError: null,
    actionPending: false,
    handleAction: async () => undefined,
    retryObservation: () => undefined,
  };
}

describe("analysisPanelDisplay", () => {
  it("derives percentage geometry, one-decimal labels, and an accessible aggregate from permille", () => {
    const display = analysisPanelDisplay(
      completedState(
        evaluationResult([candidate({ wdl_wins: 421, wdl_draws: 309, wdl_losses: 270 })]),
      ),
      { displayedPly: 12 },
    );

    expect(display.result).toEqual({
      stale: false,
      metadata: { displayedPly: 12, depth: 28, candidateCount: 1 },
      lines: [
        {
          rank: 1,
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

  it("keeps score kinds, SAN conversion, fallback text, ranks, and fewer-than-five candidates", () => {
    const display = analysisPanelDisplay(
      completedState(
        evaluationResult([
          candidate({ rank: 1, score_kind: "cp", score_value: 34, pv_uci: ["e2e4"] }),
          candidate({ rank: 2, score_kind: "mate", score_value: -3, pv_uci: ["d2d4"] }),
          candidate({ rank: 3, score_kind: "mate_given", score_value: 0, pv_uci: ["c2c4"] }),
          candidate({ rank: 4, score_kind: "cp", score_value: -250, pv_uci: ["a1a1"] }),
        ]),
      ),
    );

    expect(display.result?.metadata).toEqual({
      displayedPly: null,
      depth: 28,
      candidateCount: 4,
    });
    expect(display.result?.lines).toHaveLength(4);
    expect(display.result?.lines.map((line) => [line.rank, line.score, line.pv])).toEqual([
      [1, "+0.34", "1. e4"],
      [2, "-M3", "1. d4"],
      [3, "+M", "1. c4"],
      [4, "-2.50", "Line unavailable"],
    ]);
  });

  it("bounds the rendered candidate ledger to five lines", () => {
    const display = analysisPanelDisplay(
      completedState(
        evaluationResult(
          Array.from({ length: 6 }, (_, index) =>
            candidate({ rank: index + 1, score_value: index * 10 }),
          ),
        ),
      ),
    );

    expect(display.result?.metadata.candidateCount).toBe(6);
    expect(display.result?.lines).toHaveLength(5);
    expect(display.result?.lines.map((line) => line.rank)).toEqual([1, 2, 3, 4, 5]);
  });

  it("keeps a terminal result empty without inventing a line or depth", () => {
    const display = analysisPanelDisplay(
      completedState(
        {
          ...evaluationResult([]),
          terminal_kind: "checkmate",
        },
        true,
      ),
      { displayedPly: 24 },
    );

    expect(display.result).toEqual({
      stale: false,
      metadata: { displayedPly: 24, depth: null, candidateCount: 0 },
      lines: [],
    });
    expect(display.actions.update).toBe(true);
  });

  it("does not expose result metadata when no result exists", () => {
    const display = analysisPanelDisplay(missingState(), { displayedPly: 12 });

    expect(display.result).toBeNull();
    expect(display.actions.analyze).toBe(true);
  });
});
