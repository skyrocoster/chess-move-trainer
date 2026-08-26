import { Chess } from "chess.js";

import type { EvaluationCandidate, EvaluationResult } from "./analysisApi";
import type { AnalysisState } from "./analysisState";
import type { Fen } from "./chessPrimitives";

export type AnalysisPanelLine = {
  rank: number;
  score: string;
  pv: string;
  wdl: string;
};

export type AnalysisPanelDisplay = {
  stateLabel: string;
  error: string | null;
  actionError: string | null;
  message: { text: string; alert: boolean } | null;
  result: { stale: boolean; lines: AnalysisPanelLine[] } | null;
  actions: {
    analyze: boolean;
    update: boolean;
    retry: boolean;
    observationRetry: boolean;
    pending: boolean;
  };
};

function formatPercentage(value: number): string {
  return `${(value / 10).toFixed(1)}%`;
}

function formatWdl(candidate: EvaluationCandidate): string {
  return `W ${formatPercentage(candidate.wdl_wins)} / D ${formatPercentage(
    candidate.wdl_draws,
  )} / L ${formatPercentage(candidate.wdl_losses)}`;
}

function moveFromUci(uci: string) {
  const promotion = uci.length === 5 ? (uci[4] as "q" | "r" | "b" | "n") : undefined;
  return {
    from: uci.slice(0, 2),
    to: uci.slice(2, 4),
    ...(promotion ? { promotion } : {}),
  };
}

function formatPv(fen: Fen, pv: string[]): string {
  const chess = new Chess(fen);
  const sanMoves: string[] = [];

  pv.forEach((uci, index) => {
    const fields = chess.fen().split(" ");
    const moveNumber = fields[5];
    const whiteToMove = chess.turn() === "w";
    const move = chess.move(moveFromUci(uci));
    const prefix = whiteToMove ? `${moveNumber}. ` : index === 0 ? `${moveNumber}... ` : "";
    sanMoves.push(`${prefix}${move.san}`);
  });

  return sanMoves.join(" ");
}

function displayPv(result: EvaluationResult, candidate: EvaluationCandidate): string {
  try {
    return formatPv(result.fen, candidate.pv_uci);
  } catch {
    return "Line unavailable";
  }
}

export function formatScore(candidate: EvaluationCandidate): string {
  if (candidate.score_kind === "cp") {
    const score = candidate.score_value / 100;
    return `${score >= 0 ? "+" : ""}${score.toFixed(2)}`;
  }
  if (candidate.score_kind === "mate_given") {
    return "+M";
  }
  return `${candidate.score_value >= 0 ? "+M" : "-M"}${Math.abs(candidate.score_value)}`;
}

export function analysisPanelDisplay(analysisState: AnalysisState): AnalysisPanelDisplay {
  const { observation, loading, error, actionError, actionPending } = analysisState;
  const status = observation?.status?.state;
  const result = observation?.result;
  const stale = observation?.eligibility === "stale" || status === "queued" || status === "running";
  const showAnalyze = !loading && observation?.eligibility === "missing" && !status;
  const showUpdate =
    !loading &&
    Boolean(result) &&
    status !== "queued" &&
    status !== "running" &&
    status !== "failed";
  const showRetry = !loading && status === "failed";
  const showObservationRetry = !loading && Boolean(error);

  let stateLabel = "Loading evaluation…";
  if (!loading && error) {
    stateLabel = "Evaluation unavailable";
  } else if (status === "queued") {
    stateLabel = "Analysis queued";
  } else if (status === "running") {
    stateLabel = "Analysis running";
  } else if (status === "failed") {
    stateLabel = "Analysis failed";
  } else if (result) {
    stateLabel = stale ? "Stale analysis" : "Analysis complete";
  } else if (showAnalyze) {
    stateLabel = "Analysis available on request";
  }

  const message =
    status === "queued"
      ? { text: "This position is waiting for analysis.", alert: false }
      : status === "running"
        ? { text: "Analysis is in progress.", alert: false }
        : status === "failed"
          ? {
              text: "No complete result was published. Retry deliberately when ready.",
              alert: true,
            }
          : showAnalyze
            ? {
                text: "Analyze this displayed position deliberately to request a result.",
                alert: false,
              }
            : null;

  return {
    stateLabel,
    error,
    actionError,
    message,
    result: result
      ? {
          stale,
          lines: result.candidates.slice(0, 5).map((candidate) => ({
            rank: candidate.rank,
            score: formatScore(candidate),
            pv: displayPv(result, candidate),
            wdl: formatWdl(candidate),
          })),
        }
      : null,
    actions: {
      analyze: showAnalyze,
      update: showUpdate,
      retry: showRetry,
      observationRetry: showObservationRetry,
      pending: actionPending,
    },
  };
}
