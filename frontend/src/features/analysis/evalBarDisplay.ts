import type { AnalysisLine } from "./analysisApi";
import { formatScore } from "./analysisFormatting";
import type { AnalysisState } from "./analysisState";
import type { EvalBarDisplayState } from "./EvalBar";

export type EvalBarDisplay = {
  state: EvalBarDisplayState;
  value: number;
  shortValue: string;
  accessibleValue: string;
};

const CP_METER_RANGE = 1000;

function meterValue(line: AnalysisLine | null): number {
  if (!line) {
    return 50;
  }
  if (line.score_kind === "mate") {
    return line.score_value >= 0 ? 100 : 0;
  }
  return Math.max(0, Math.min(100, 50 + (line.score_value / CP_METER_RANGE) * 50));
}

function shortValue(line: AnalysisLine | null): string {
  return line ? formatScore(line) : "0.00";
}

export function evaluationDisplay(analysisState: AnalysisState): EvalBarDisplay {
  const observation = analysisState.observation;
  const active = observation?.state === "queued" || observation?.state === "running";
  const line = observation?.result?.lines[0] ?? null;

  if (active) {
    return {
      state: "pending",
      value: meterValue(line),
      shortValue: shortValue(line),
      accessibleValue:
        observation?.state === "queued"
          ? "Analysis queued; evaluation pending."
          : "Analysis running; evaluation pending.",
    };
  }

  if (line) {
    return {
      state: "best-line",
      value: meterValue(line),
      shortValue: shortValue(line),
      accessibleValue: `Best-line evaluation ${formatScore(line)}.`,
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
