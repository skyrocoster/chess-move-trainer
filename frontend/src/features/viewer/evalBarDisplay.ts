import type { EvaluationCandidate } from "./analysisApi";
import { formatScore } from "./analysisFormatting";
import type { AnalysisState } from "./analysisState";
import type { EvalBarDisplayState } from "../analysis/EvalBar";

export type EvalBarDisplay = {
  state: EvalBarDisplayState;
  value: number;
  shortValue: string;
  accessibleValue: string;
};

const CP_METER_RANGE = 1000;

function meterValue(candidate: EvaluationCandidate | null): number {
  if (!candidate) {
    return 50;
  }
  if (candidate.score_kind === "mate_given") {
    return 100;
  }
  if (candidate.score_kind === "mate") {
    return candidate.score_value >= 0 ? 100 : 0;
  }
  return Math.max(0, Math.min(100, 50 + (candidate.score_value / CP_METER_RANGE) * 50));
}

function shortValue(candidate: EvaluationCandidate | null): string {
  return candidate ? formatScore(candidate) : "0.00";
}

export function evaluationDisplay(analysisState: AnalysisState): EvalBarDisplay {
  const observation = analysisState.observation;
  const queueState = observation?.status?.state;
  const candidate = observation?.result?.candidates[0] ?? null;

  if (queueState === "queued" || queueState === "running") {
    return {
      state: "pending",
      value: meterValue(candidate),
      shortValue: shortValue(candidate),
      accessibleValue:
        queueState === "queued"
          ? "Analysis queued; evaluation pending."
          : "Analysis running; evaluation pending.",
    };
  }

  if (candidate) {
    const stale = observation?.eligibility === "stale" || queueState === "failed";
    return {
      state: "best-line",
      value: meterValue(candidate),
      shortValue: shortValue(candidate),
      accessibleValue: `${stale ? "Stale " : ""}best-line evaluation ${formatScore(candidate)}.`,
    };
  }

  if (queueState === "failed") {
    return {
      state: "neutral",
      value: meterValue(null),
      shortValue: shortValue(null),
      accessibleValue: "Analysis failed; evaluation neutral.",
    };
  }

  if (analysisState.error) {
    return {
      state: "neutral",
      value: meterValue(null),
      shortValue: shortValue(null),
      accessibleValue: "Evaluation unavailable; evaluation neutral.",
    };
  }

  return {
    state: "neutral",
    value: meterValue(null),
    shortValue: shortValue(null),
    accessibleValue: "No analysis yet; evaluation neutral.",
  };
}
