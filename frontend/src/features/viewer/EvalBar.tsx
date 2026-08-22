import { Meter } from "@base-ui/react/meter";

import type { BoardOrientation } from "../board-adapter/BoardAdapter";
import type { EvaluationCandidate } from "./analysisApi";
import { formatScore } from "./analysisFormatting";
import type { AnalysisState } from "./analysisState";
import styles from "./EvalBar.module.css";

export type EvalBarProps = {
  orientation: BoardOrientation;
  analysisState?: AnalysisState | null;
};

type EvalBarDisplayState = "neutral" | "pending" | "best-line";

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

function displayState(analysisState: AnalysisState | null | undefined): {
  state: EvalBarDisplayState;
  candidate: EvaluationCandidate | null;
  accessibleValue: string;
} {
  const observation = analysisState?.observation;
  const queueState = observation?.status?.state;
  const candidate = observation?.result?.candidates[0] ?? null;

  if (queueState === "queued" || queueState === "running") {
    return {
      state: "pending",
      candidate,
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
      candidate,
      accessibleValue: `${stale ? "Stale " : ""}best-line evaluation ${formatScore(candidate)}.`,
    };
  }

  if (queueState === "failed") {
    return {
      state: "neutral",
      candidate: null,
      accessibleValue: "Analysis failed; evaluation neutral.",
    };
  }

  if (analysisState?.error) {
    return {
      state: "neutral",
      candidate: null,
      accessibleValue: "Evaluation unavailable; evaluation neutral.",
    };
  }

  return {
    state: "neutral",
    candidate: null,
    accessibleValue: "No analysis yet; evaluation neutral.",
  };
}

export function EvalBar({ orientation, analysisState }: EvalBarProps) {
  const { state, candidate, accessibleValue } = displayState(analysisState);
  const value = meterValue(candidate);

  return (
    <Meter.Root
      className={styles.bar}
      data-orientation={orientation}
      data-state={state}
      min={0}
      max={100}
      value={value}
      aria-valuetext={accessibleValue}
    >
      <Meter.Label className={styles.label}>Evaluation</Meter.Label>
      <Meter.Track className={styles.track}>
        <Meter.Indicator
          className={styles.indicator}
          style={{ width: "100%", height: `${value}%` }}
        />
      </Meter.Track>
      <Meter.Value className={styles.value}>{() => accessibleValue}</Meter.Value>
    </Meter.Root>
  );
}
