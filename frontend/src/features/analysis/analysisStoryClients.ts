import { fn } from "storybook/test";

import type {
  AnalysisClient,
  AnalysisLine,
  AnalysisObservation,
  AnalysisOperationResult,
  AnalysisResult,
  AnalysisStateValue,
} from "./analysisApi";
import type { Fen } from "../chess/chessPrimitives";

type AnalysisSuccess = AnalysisOperationResult<AnalysisObservation>;

function cleanLine(move: string, rank: number, scoreValue: number): AnalysisLine {
  return {
    rank,
    score_kind: "cp",
    score_value: scoreValue,
    wdl_wins: 420,
    wdl_draws: 300,
    wdl_losses: 280,
    pv_uci: [move],
    depth: 20,
  };
}

function cleanResult(moves: readonly string[], scoreOffset = 0): AnalysisResult {
  return {
    lines: moves.map((move, index) => cleanLine(move, index + 1, 34 - index * 10 + scoreOffset)),
    terminal_kind: null,
  };
}

function cleanObservation(
  fen: Fen,
  state: AnalysisStateValue,
  result: AnalysisResult | null,
): AnalysisSuccess {
  return {
    status: "success",
    data: { fen, state, result },
  };
}

export type StoryAnalysisLifecycleEvent = {
  operation: "observe" | "request";
  fen: Fen;
  state: AnalysisStateValue;
  hasResult: boolean;
  quality?: "tool";
};

function emitLifecycleEvent(
  onEvent: ((event: StoryAnalysisLifecycleEvent) => void) | undefined,
  event: StoryAnalysisLifecycleEvent,
) {
  onEvent?.(event);
}

export function storyAnalysisClient(): AnalysisClient {
  return {
    observe: fn(async (fen) => cleanObservation(fen, "not_requested", null)),
    request: fn(async (fen) => cleanObservation(fen, "queued", null)),
  };
}

export function storyCandidateAnalysisClient(
  moves: readonly string[] = ["e2e4", "d2d4", "c2c4", "g1f3", "b1c3"],
): AnalysisClient {
  return {
    observe: fn(async (fen) => cleanObservation(fen, "ready", cleanResult(moves))),
    request: fn(async (fen) => cleanObservation(fen, "ready", cleanResult(moves))),
  };
}

export function storySelectedPositionAnalysisClient(
  onEvent?: (event: StoryAnalysisLifecycleEvent) => void,
): AnalysisClient {
  const initialMoves = ["d2d4"] as const;
  const readyMoves = ["e2e4"] as const;
  let primaryFen: Fen | null = null;
  let requestStarted = false;
  let pollCount = 0;

  const observe = fn(async (fen: Fen): Promise<AnalysisSuccess> => {
    primaryFen ??= fen;

    let state: AnalysisStateValue = "not_requested";
    let result: AnalysisResult | null = null;
    if (fen === primaryFen) {
      if (!requestStarted) {
        result = null;
      } else if (pollCount === 0) {
        pollCount += 1;
        state = "running";
        result = cleanResult(initialMoves);
      } else {
        state = "ready";
        result = cleanResult(readyMoves, 8);
      }
    }

    emitLifecycleEvent(onEvent, {
      operation: "observe",
      fen,
      state,
      hasResult: result !== null,
    });
    return cleanObservation(fen, state, result);
  });

  const request = fn(async (fen: Fen): Promise<AnalysisSuccess> => {
    primaryFen ??= fen;
    requestStarted = true;
    pollCount = 0;
    const result = cleanResult(initialMoves);
    emitLifecycleEvent(onEvent, {
      operation: "request",
      fen,
      state: "queued",
      hasResult: true,
      quality: "tool",
    });
    return cleanObservation(fen, "queued", result);
  });

  return { observe, request };
}
