import { Chess } from "chess.js";

import type {
  AnalysisPanelDisplay,
  AnalysisPanelWdl,
  AnalysisPanelWdlValue,
} from "../analysis/AnalysisPanel";
import type { EvaluationCandidate, EvaluationResult } from "./analysisApi";
import type { AnalysisState } from "./analysisState";
import type { Fen } from "./chessPrimitives";

export type {
  AnalysisPanelDisplay,
  AnalysisPanelLine,
  AnalysisPanelResultMetadata,
  AnalysisPanelWdl,
  AnalysisPanelWdlValue,
} from "../analysis/AnalysisPanel";

export type AnalysisPanelDisplayOptions = {
  displayedPly?: number;
};

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`;
}

function formatAccessiblePercentage(value: AnalysisPanelWdlValue): string {
  return `${Number.isInteger(value.percentage) ? value.percentage : value.percentage.toFixed(1)} percent`;
}

function wdlValue(permille: number): AnalysisPanelWdlValue {
  const percentage = permille / 10;
  return { percentage, label: formatPercentage(percentage) };
}

function formatWdl(candidate: EvaluationCandidate): AnalysisPanelWdl {
  const wins = wdlValue(candidate.wdl_wins);
  const draws = wdlValue(candidate.wdl_draws);
  const losses = wdlValue(candidate.wdl_losses);

  return {
    wins,
    draws,
    losses,
    accessibleLabel: `Win ${formatAccessiblePercentage(wins)}, draw ${formatAccessiblePercentage(
      draws,
    )}, loss ${formatAccessiblePercentage(losses)}`,
  };
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

export function analysisPanelDisplay(
  analysisState: AnalysisState,
  options: AnalysisPanelDisplayOptions = {},
): AnalysisPanelDisplay {
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
          metadata: {
            displayedPly: options.displayedPly ?? null,
            depth: result.candidates[0]?.depth ?? null,
            candidateCount: result.candidates.length,
          },
          lines: result.candidates.slice(0, 5).map((candidate) => ({
            rank: candidate.rank,
            move: candidate.pv_uci[0]!,
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
