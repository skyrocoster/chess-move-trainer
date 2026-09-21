import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { queryKeys } from "../../api/queryKeys";
import { Button } from "../design-system/Button";
import {
  formatUtcDate,
  getUtcCalendarDay,
  toUtcMidnight,
} from "../design-system/CalendarDateUtils";
import { InlineFeedback } from "../design-system/feedback/InlineFeedback";
import { PageFeedback } from "../design-system/feedback/PageFeedback";
import { AnalysisDashboard } from "./AnalysisDashboard";
import { AnalysisFilters, type AnalysisFilterDraft } from "./AnalysisFilters";
import type { AnalysisFiltersInvalid } from "./AnalysisFilters";
import {
  AnalysisOverviewQueryError,
  fetchAnalysisOverview,
  type AnalysisOverviewClient,
  type AnalysisOverviewFilters,
} from "./analysisOverviewApi";
import {
  activeFilterCount,
  filterScopeLabel,
  formatReportDate,
} from "./analysisOverviewFormatting";
import styles from "./AnalysisOverview.module.css";

function initialDraft(today: Date): AnalysisFilterDraft {
  return {
    asOf: today,
    startedOnOrAfter: null,
    startedOnOrBefore: null,
    trainerColor: null,
    timeClass: null,
  };
}

function filtersFromDraft(
  draft: AnalysisFilterDraft,
):
  | { filters: AnalysisOverviewFilters; invalid: AnalysisFiltersInvalid }
  | { error: string; invalid: AnalysisFiltersInvalid } {
  if (draft.asOf === null) {
    return {
      error: "Choose a training snapshot date before applying filters.",
      invalid: { asOf: true, startedOnOrAfter: false, startedOnOrBefore: false },
    };
  }
  const startedOnOrAfter =
    draft.startedOnOrAfter === null ? null : formatUtcDate(draft.startedOnOrAfter);
  const startedOnOrBefore =
    draft.startedOnOrBefore === null ? null : formatUtcDate(draft.startedOnOrBefore);
  if (
    startedOnOrAfter !== null &&
    startedOnOrBefore !== null &&
    startedOnOrAfter > startedOnOrBefore
  ) {
    return {
      error: "Games from must be on or before Games through.",
      invalid: { asOf: false, startedOnOrAfter: true, startedOnOrBefore: true },
    };
  }
  return {
    filters: {
      asOf: formatUtcDate(draft.asOf),
      startedOnOrAfter,
      startedOnOrBefore,
      trainerColor: draft.trainerColor,
      timeClass: draft.timeClass,
    },
    invalid: { asOf: false, startedOnOrAfter: false, startedOnOrBefore: false },
  };
}

function sameFilters(left: AnalysisOverviewFilters, right: AnalysisOverviewFilters): boolean {
  return (
    left.asOf === right.asOf &&
    left.startedOnOrAfter === right.startedOnOrAfter &&
    left.startedOnOrBefore === right.startedOnOrBefore &&
    left.trainerColor === right.trainerColor &&
    left.timeClass === right.timeClass
  );
}

function errorMessage(error: unknown): string {
  if (error instanceof AnalysisOverviewQueryError) {
    if (error.status === "invalid_filter") {
      return "The backend could not apply these filters. Review the dates and try again.";
    }
    if (error.status === "statistics_unavailable") {
      return "Analysis data is unavailable right now. Check that the rebuilt database is ready, then retry.";
    }
  }
  return "Analysis could not be loaded. Retry the report.";
}

export function AnalysisPage({
  client = fetchAnalysisOverview,
}: {
  client?: AnalysisOverviewClient;
}) {
  const [today] = useState(() => toUtcMidnight(getUtcCalendarDay(new Date())));
  const [draft, setDraft] = useState<AnalysisFilterDraft>(() => initialDraft(today));
  const [appliedFilters, setAppliedFilters] = useState<AnalysisOverviewFilters>(() => ({
    asOf: formatUtcDate(today),
    startedOnOrAfter: null,
    startedOnOrBefore: null,
    trainerColor: null,
    timeClass: null,
  }));
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const [invalidFields, setInvalidFields] = useState<AnalysisFiltersInvalid>({
    asOf: false,
    startedOnOrAfter: false,
    startedOnOrBefore: false,
  });

  const report = useQuery({
    queryKey: queryKeys.statisticsOverview(appliedFilters),
    queryFn: ({ signal }) => client(appliedFilters, signal),
    placeholderData: keepPreviousData,
    retry: false,
    staleTime: 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  function applyFilters() {
    const result = filtersFromDraft(draft);
    if ("error" in result) {
      setValidationMessage(result.error);
      setInvalidFields(result.invalid);
      return;
    }
    setValidationMessage(null);
    setInvalidFields(result.invalid);
    if (sameFilters(result.filters, appliedFilters)) {
      void report.refetch();
      return;
    }
    setAppliedFilters(result.filters);
  }

  function resetFilters() {
    const resetDraft = initialDraft(today);
    const resetOutcome = filtersFromDraft(resetDraft);
    setDraft(resetDraft);
    setValidationMessage(null);
    setInvalidFields({ asOf: false, startedOnOrAfter: false, startedOnOrBefore: false });
    if ("filters" in resetOutcome) {
      if (sameFilters(resetOutcome.filters, appliedFilters)) {
        void report.refetch();
      } else {
        setAppliedFilters(resetOutcome.filters);
      }
    }
  }

  const data = report.data;
  const updateError = report.isError && data !== undefined;
  const displayedFilters: AnalysisOverviewFilters | null = data
    ? {
        asOf: data.as_of,
        startedOnOrAfter: data.filters.started_on_or_after,
        startedOnOrBefore: data.filters.started_on_or_before,
        trainerColor: data.filters.trainer_color,
        timeClass: data.filters.time_class,
      }
    : null;

  return (
    <section className={styles.page} aria-labelledby="analysis-overview-heading">
      <header className={styles.pageHeader}>
        <p className={styles.eyebrow}>Your games</p>
        <h1 id="analysis-overview-heading">Analysis</h1>
        <p>Find the patterns in your results, openings, and repertoire preparation.</p>
      </header>

      <AnalysisFilters
        draft={draft}
        activeCount={activeFilterCount(appliedFilters)}
        validationMessage={validationMessage}
        invalid={invalidFields}
        applying={report.isFetching}
        onChange={(nextDraft) => {
          setDraft(nextDraft);
          setValidationMessage(null);
          setInvalidFields({ asOf: false, startedOnOrAfter: false, startedOnOrBefore: false });
        }}
        onApply={applyFilters}
        onReset={resetFilters}
      />

      {data && displayedFilters ? (
        <div className={styles.appliedScope}>
          <div>
            <span>Showing</span>
            <strong>{filterScopeLabel(displayedFilters)}</strong>
          </div>
          <div>
            <span>Training snapshot</span>
            <strong>{formatReportDate(data.as_of)}</strong>
          </div>
        </div>
      ) : null}

      {report.isPending ? (
        <PageFeedback
          severity="information"
          heading="Building your report"
          message="Loading game results and preparation coverage…"
          role="status"
          aria-live="polite"
        />
      ) : null}

      {report.isError && data === undefined ? (
        <div className={styles.feedbackStack}>
          <PageFeedback
            severity="error"
            heading="Analysis unavailable"
            message={errorMessage(report.error)}
            role="alert"
            aria-live="assertive"
          />
          <Button variant="secondary" onClick={() => void report.refetch()}>
            Retry report
          </Button>
        </div>
      ) : null}

      {updateError ? (
        <div className={styles.updateNotice}>
          <InlineFeedback
            severity="error"
            message={`${errorMessage(report.error)} The previous report remains visible.`}
            role="alert"
            aria-live="assertive"
          />
          <Button size="sm" variant="secondary" onClick={() => void report.refetch()}>
            Retry update
          </Button>
        </div>
      ) : null}

      {report.isFetching && data !== undefined && !updateError ? (
        <p className={styles.updating} role="status" aria-live="polite">
          Updating analysis…
        </p>
      ) : null}

      {data && data.games.record.total_count === 0 ? (
        <div className={styles.feedbackStack}>
          <PageFeedback
            severity="information"
            heading="No games match these filters"
            message="Widen the date range, include both colours, or choose another time class."
            role="status"
            aria-live="polite"
          />
          <Button variant="secondary" onClick={resetFilters}>
            Clear game filters
          </Button>
        </div>
      ) : null}

      {data && data.games.record.total_count > 0 ? <AnalysisDashboard data={data} /> : null}
    </section>
  );
}
