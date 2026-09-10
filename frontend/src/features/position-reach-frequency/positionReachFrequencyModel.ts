import type { ChessSide } from "../chess/chessPrimitives";
import type { PositionContextResponse } from "../position-context/positionContextApi";

export type PositionReachFrequencyState = "available" | "absent" | "unavailable";

type BasePositionReachFrequencyModel = {
  selectedColor: ChessSide;
  colorLabel: "White" | "Black";
  state: PositionReachFrequencyState;
  meterValue: number;
  message: string;
};

export type PositionReachFrequencyModel =
  | (BasePositionReachFrequencyModel & {
      state: "available";
      reached: number;
      total: number;
      percentage: number;
      fractionLabel: string;
      percentageLabel: string;
      accessibleValue: string;
    })
  | (BasePositionReachFrequencyModel & {
      state: "absent" | "unavailable";
      reached: null;
      total: null;
      percentage: null;
      fractionLabel: null;
      percentageLabel: null;
      accessibleValue: string;
    });

function colorLabel(color: ChessSide): "White" | "Black" {
  return color === "white" ? "White" : "Black";
}

function boundedPercentage(reached: number, total: number): number {
  if (total <= 0) return 0;
  return Math.max(0, Math.min(100, (reached / total) * 100));
}

function percentageLabel(value: number): string {
  return `${Number.isInteger(value) ? value : value.toFixed(1)}%`;
}

export function derivePositionReachFrequencyModel(
  context: PositionContextResponse | null,
  selectedColor: ChessSide,
): PositionReachFrequencyModel {
  const label = colorLabel(selectedColor);

  if (context === null) {
    return {
      selectedColor,
      colorLabel: label,
      state: "unavailable",
      reached: null,
      total: null,
      percentage: null,
      meterValue: 0,
      fractionLabel: null,
      percentageLabel: null,
      message: "Position reach data is unavailable.",
      accessibleValue: `Position reach data is unavailable for ${label}.`,
    };
  }

  if (!context.observedInGames) {
    return {
      selectedColor,
      colorLabel: label,
      state: "absent",
      reached: null,
      total: null,
      percentage: null,
      meterValue: 0,
      fractionLabel: null,
      percentageLabel: null,
      message: `This position is not present in the accepted game data for ${label}.`,
      accessibleValue: `This position is not present in the accepted game data for ${label}.`,
    };
  }

  const reached = context.distinctGameCount;
  const total = context.totalGameCount;
  const percentage = boundedPercentage(reached, total);
  const percent = percentageLabel(percentage);

  return {
    selectedColor,
    colorLabel: label,
    state: "available",
    reached,
    total,
    percentage,
    meterValue: percentage,
    fractionLabel: `${reached} / ${total} games`,
    percentageLabel: percent,
    message: `Reached in ${reached} of ${total} games as ${label}.`,
    accessibleValue: `${reached} of ${total} games as ${label}; ${percent} reached.`,
  };
}
