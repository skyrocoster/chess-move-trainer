import { fn } from "storybook/test";

import type {
  AnalysisClient,
  EvaluationCandidate,
  EvaluationResult,
  EvaluationStatus,
} from "./analysisApi";
import { GAME } from "../game/gameFixtures";

export function storyAnalysisClient(): AnalysisClient {
  return {
    observe: fn(async (fen) => ({
      status: "success" as const,
      data: { fen, eligibility: "missing" as const, result: null, status: null, terminal: false },
    })),
    enqueue: fn(async () => {
      throw new Error("Stage 1 workspace stories do not exercise analysis actions");
    }),
    status: fn(async () => ({
      status: "success" as const,
      data: {
        fen: GAME.positions[0].fen,
        state: null,
        completed_at: null,
        error_code: null,
      },
    })),
  };
}

function candidateFor(move: string, rank: number): EvaluationCandidate {
  return {
    rank,
    score_kind: "cp",
    score_value: 34 - (rank - 1) * 10,
    wdl_wins: 420,
    wdl_draws: 300,
    wdl_losses: 280,
    pv_uci: [move],
    depth: 20,
    seldepth: 24,
    nodes: 200_000,
    engine_time_ms: 100,
  };
}

function candidateResult(fen: string, moves: readonly string[]): EvaluationResult {
  return {
    fen,
    profile_id: "story-candidate-profile",
    candidates: moves.map((move, index) => candidateFor(move, index + 1)),
    terminal_kind: null,
    completed_at: "2026-08-22T00:00:01+00:00",
    wall_time_ms: 100,
  };
}

function candidateStatus(): EvaluationStatus {
  return {
    state: "done",
    position: 0,
    attempts: 1,
    enqueued_at: "2026-08-22T00:00:00+00:00",
    started_at: "2026-08-22T00:00:00+00:00",
    completed_at: "2026-08-22T00:00:01+00:00",
    error_code: null,
  };
}

export function storyCandidateAnalysisClient(
  moves: readonly string[] = ["e2e4", "d2d4", "c2c4", "g1f3", "b1c3"],
): AnalysisClient {
  return {
    observe: fn(async (fen) => ({
      status: "success" as const,
      data: {
        fen,
        eligibility: "eligible" as const,
        result: candidateResult(fen, moves),
        status: candidateStatus(),
        terminal: false,
      },
    })),
    enqueue: fn(async () => {
      throw new Error("Candidate stories do not exercise analysis actions");
    }),
    status: fn(async (fen) => ({
      status: "success" as const,
      data: {
        fen,
        state: "done" as const,
        completed_at: "2026-08-22T00:00:01+00:00",
        error_code: null,
      },
    })),
  };
}
