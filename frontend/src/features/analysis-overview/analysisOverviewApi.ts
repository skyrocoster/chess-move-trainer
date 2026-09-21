import { getStatisticsOverview } from "../../api/client";
import type { GetStatisticsOverviewData, StatisticsOverviewResponse } from "../../api/client";

export type AnalysisTrainerColor = "white" | "black";
export type AnalysisTimeClass = "bullet" | "blitz" | "rapid" | "daily";

export type AnalysisOverviewFilters = {
  asOf: string;
  startedOnOrAfter: string | null;
  startedOnOrBefore: string | null;
  trainerColor: AnalysisTrainerColor | null;
  timeClass: AnalysisTimeClass | null;
};

export type AnalysisOverviewFailure =
  "invalid_filter" | "statistics_unavailable" | "unexpected_failure";

export class AnalysisOverviewQueryError extends Error {
  constructor(readonly status: AnalysisOverviewFailure) {
    super(status);
    this.name = "AnalysisOverviewQueryError";
  }
}

type StatisticsQuery = NonNullable<GetStatisticsOverviewData["query"]>;
type JsonRecord = Record<string, unknown>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function isAbortError(value: unknown): boolean {
  return isRecord(value) && value.name === "AbortError";
}

function failureFrom(error: unknown, status: number | null): AnalysisOverviewFailure {
  const code = isRecord(error) && typeof error.code === "string" ? error.code : null;
  if (status === 422 && code === "invalid_filter") return "invalid_filter";
  if (status === 503 && code === "statistics_unavailable") return "statistics_unavailable";
  return "unexpected_failure";
}

export function buildStatisticsOverviewQuery(filters: AnalysisOverviewFilters): StatisticsQuery {
  const query: StatisticsQuery = { as_of: filters.asOf };
  if (filters.startedOnOrAfter !== null) {
    query.started_on_or_after = filters.startedOnOrAfter;
  }
  if (filters.startedOnOrBefore !== null) {
    query.started_on_or_before = filters.startedOnOrBefore;
  }
  if (filters.trainerColor !== null) {
    query.trainer_color = filters.trainerColor;
  }
  if (filters.timeClass !== null) {
    query.time_class = filters.timeClass;
  }
  return query;
}

export async function fetchAnalysisOverview(
  filters: AnalysisOverviewFilters,
  signal?: AbortSignal,
): Promise<StatisticsOverviewResponse> {
  try {
    const result = await getStatisticsOverview({
      query: buildStatisticsOverviewQuery(filters),
      signal,
    });
    if (result.data === undefined || result.error !== undefined) {
      throw new AnalysisOverviewQueryError(
        failureFrom(result.error, result.response?.status ?? null),
      );
    }
    return result.data;
  } catch (error) {
    if (signal?.aborted || isAbortError(error)) throw error;
    if (error instanceof AnalysisOverviewQueryError) throw error;
    throw new AnalysisOverviewQueryError("unexpected_failure");
  }
}

export type AnalysisOverviewClient = typeof fetchAnalysisOverview;
