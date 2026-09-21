import type { StatisticsOverviewResponse } from "../../api/client";
import type { AnalysisOverviewFilters } from "./analysisOverviewApi";

export type OutcomeRecord = StatisticsOverviewResponse["games"]["record"];

const integerFormatter = new Intl.NumberFormat("en", { maximumFractionDigits: 0 });
const decimalFormatter = new Intl.NumberFormat("en", { maximumFractionDigits: 1 });
const percentFormatter = new Intl.NumberFormat("en", {
  style: "percent",
  maximumFractionDigits: 0,
});
const dateFormatter = new Intl.DateTimeFormat("en", {
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});
const monthFormatter = new Intl.DateTimeFormat("en", {
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});

export function formatInteger(value: number | null): string {
  return value === null ? "—" : integerFormatter.format(value);
}

export function formatDecimal(value: number | null): string {
  return value === null ? "—" : decimalFormatter.format(value);
}

export function formatRate(value: number | null): string {
  return value === null ? "—" : percentFormatter.format(value);
}

export function formatSignedInteger(value: number | null): string {
  if (value === null) return "—";
  return `${value > 0 ? "+" : ""}${integerFormatter.format(value)}`;
}

function utcDate(value: string): Date | null {
  const parsed = new Date(`${value}T00:00:00.000Z`);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function formatReportDate(value: string): string {
  const parsed = utcDate(value);
  return parsed === null ? value : dateFormatter.format(parsed);
}

export function formatMonth(value: string): string {
  const parsed = utcDate(`${value}-01`);
  return parsed === null ? value : monthFormatter.format(parsed);
}

const CATEGORY_LABELS: Record<string, string> = {
  white: "White",
  black: "Black",
  bullet: "Bullet",
  blitz: "Blitz",
  rapid: "Rapid",
  daily: "Daily",
  unknown: "Unknown",
  trainer_200_plus_higher: "Rated 200+ higher",
  trainer_50_to_199_higher: "Rated 50–199 higher",
  within_49: "Within 49 points",
  opponent_50_to_199_higher: "Opponent rated 50–199 higher",
  opponent_200_plus_higher: "Opponent rated 200+ higher",
};

export function formatCategory(value: string): string {
  return (
    CATEGORY_LABELS[value] ??
    value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())
  );
}

export function outcomeLabel(record: OutcomeRecord): string {
  const unknown = record.unknown_count > 0 ? `, ${record.unknown_count} unknown` : "";
  return `${record.win_count} wins, ${record.draw_count} draws, ${record.loss_count} losses${unknown}`;
}

export function filterScopeLabel(filters: AnalysisOverviewFilters): string {
  const dateScope =
    filters.startedOnOrAfter && filters.startedOnOrBefore
      ? `${formatReportDate(filters.startedOnOrAfter)}–${formatReportDate(filters.startedOnOrBefore)}`
      : filters.startedOnOrAfter
        ? `From ${formatReportDate(filters.startedOnOrAfter)}`
        : filters.startedOnOrBefore
          ? `Through ${formatReportDate(filters.startedOnOrBefore)}`
          : "All game dates";
  const color =
    filters.trainerColor === null ? "Both colours" : formatCategory(filters.trainerColor);
  const timeClass = filters.timeClass === null ? "All speeds" : formatCategory(filters.timeClass);
  return `${dateScope} · ${color} · ${timeClass}`;
}

export function activeFilterCount(filters: AnalysisOverviewFilters): number {
  return [
    filters.startedOnOrAfter,
    filters.startedOnOrBefore,
    filters.trainerColor,
    filters.timeClass,
  ].filter((value) => value !== null).length;
}
