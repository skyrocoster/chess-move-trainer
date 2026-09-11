import { Chess } from "chess.js";

import type {
  AnalysisPanelDisplay,
  AnalysisPanelWdl,
  AnalysisPanelWdlValue,
} from "../analysis/AnalysisPanel";
import type { AnalysisLine, AnalysisObservation, AnalysisResult } from "./analysisApi";
import type { AnalysisState } from "./analysisState";
import type { Fen } from "../chess/chessPrimitives";

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

function formatWdl(line: AnalysisLine): AnalysisPanelWdl {
  const wins = wdlValue(line.wdl_wins);
  const draws = wdlValue(line.wdl_draws);
  const losses = wdlValue(line.wdl_losses);

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

function displayPv(observationFen: Fen, line: AnalysisLine): string {
  try {
    return formatPv(observationFen, line.pv_uci);
  } catch {
    return "Line unavailable";
  }
}

export function formatScore(line: AnalysisLine): string {
  if (line.score_kind === "cp") {
    const score = line.score_value / 100;
    return `${score >= 0 ? "+" : ""}${score.toFixed(2)}`;
  }
  return `${line.score_value >= 0 ? "+M" : "-M"}${Math.abs(line.score_value)}`;
}

function resultDisplay(
  observation: AnalysisObservation,
  result: AnalysisResult,
  displayedPly: number | undefined,
): NonNullable<AnalysisPanelDisplay["result"]> {
  return {
    metadata: {
      displayedPly: displayedPly ?? null,
      depth: result.lines[0]?.depth ?? null,
      candidateCount: result.lines.length,
    },
    lines: result.lines.slice(0, 5).map((line) => ({
      rank: line.rank,
      move: line.pv_uci[0],
      score: formatScore(line),
      pv: displayPv(observation.fen, line),
      wdl: formatWdl(line),
    })),
  };
}

export function analysisPanelDisplay(
  analysisState: AnalysisState,
  options: AnalysisPanelDisplayOptions = {},
): AnalysisPanelDisplay {
  const { observation, loading, error, requestError, requestPending } = analysisState;
  const state = observation?.state;
  const result = observation?.result;
  const active = state === "queued" || state === "running";
  const showAnalyze = !loading && state === "not_requested";
  const showObservationRetry = !loading && Boolean(error);

  let stateLabel = "Loading analysis…";
  if (!loading && error) {
    stateLabel = "Analysis unavailable";
  } else if (state === "queued") {
    stateLabel = "Analysis queued";
  } else if (state === "running") {
    stateLabel = "Analysis running";
  } else if (result) {
    stateLabel = "Analysis complete";
  } else if (showAnalyze) {
    stateLabel = "Analysis available on request";
  }

  const message = active
    ? {
        text:
          state === "queued"
            ? "This position is waiting for analysis."
            : "Analysis is in progress.",
      }
    : showAnalyze
      ? {
          text: "Analyze this displayed position deliberately to request a result.",
        }
      : null;

  return {
    stateLabel,
    error,
    requestError,
    message,
    result: observation && result ? resultDisplay(observation, result, options.displayedPly) : null,
    actions: {
      analyze: showAnalyze,
      observationRetry: showObservationRetry,
      pending: requestPending,
    },
  };
}
