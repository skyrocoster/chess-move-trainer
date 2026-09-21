import { beforeEach, describe, expect, it, vi } from "vitest";

import { getStatisticsOverview } from "../../api/client";
import type { StatisticsOverviewResponse } from "../../api/client";
import {
  AnalysisOverviewQueryError,
  buildStatisticsOverviewQuery,
  fetchAnalysisOverview,
  type AnalysisOverviewFilters,
} from "./analysisOverviewApi";

vi.mock("../../api/client", () => ({
  getStatisticsOverview: vi.fn(),
}));

const FILTERS: AnalysisOverviewFilters = {
  asOf: "2026-09-21",
  startedOnOrAfter: null,
  startedOnOrBefore: null,
  trainerColor: null,
  timeClass: null,
};

const OVERVIEW = { as_of: "2026-09-21" } as StatisticsOverviewResponse;
const getStatisticsOverviewMock = vi.mocked(getStatisticsOverview);

describe("analysis overview API", () => {
  beforeEach(() => {
    getStatisticsOverviewMock.mockReset();
  });

  it("builds only the filters selected by the user", () => {
    expect(buildStatisticsOverviewQuery(FILTERS)).toEqual({ as_of: "2026-09-21" });
    expect(
      buildStatisticsOverviewQuery({
        ...FILTERS,
        startedOnOrAfter: "2026-01-01",
        startedOnOrBefore: "2026-08-31",
        trainerColor: "white",
        timeClass: "rapid",
      }),
    ).toEqual({
      as_of: "2026-09-21",
      started_on_or_after: "2026-01-01",
      started_on_or_before: "2026-08-31",
      trainer_color: "white",
      time_class: "rapid",
    });
  });

  it("returns the typed overview from the central generated client", async () => {
    getStatisticsOverviewMock.mockResolvedValue({ data: OVERVIEW } as never);

    await expect(fetchAnalysisOverview(FILTERS)).resolves.toBe(OVERVIEW);
    expect(getStatisticsOverviewMock).toHaveBeenCalledWith({
      query: { as_of: "2026-09-21" },
      signal: undefined,
    });
  });

  it("maps unavailable and unexpected failures to stable query errors", async () => {
    getStatisticsOverviewMock.mockResolvedValueOnce({
      error: { code: "statistics_unavailable" },
      response: { status: 503 },
    } as never);

    await expect(fetchAnalysisOverview(FILTERS)).rejects.toMatchObject({
      name: "AnalysisOverviewQueryError",
      status: "statistics_unavailable",
    } satisfies Partial<AnalysisOverviewQueryError>);

    getStatisticsOverviewMock.mockRejectedValueOnce(new TypeError("network down"));
    await expect(fetchAnalysisOverview(FILTERS)).rejects.toMatchObject({
      status: "unexpected_failure",
    });
  });
});
