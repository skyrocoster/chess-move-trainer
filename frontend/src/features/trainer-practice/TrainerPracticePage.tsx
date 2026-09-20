import { useQuery } from "@tanstack/react-query";
import { useCallback, useState } from "react";

import type { OpeningCatalogueItemResponse, TrainingRequirementResponse } from "../../api/client";
import { queryKeys } from "../../api/queryKeys";
import { readOpeningCatalogueSnapshot } from "./openingCatalogueStorage";
import {
  formatUtcDate,
  getUtcCalendarDay,
  toUtcMidnight,
} from "../design-system/CalendarDateUtils";
import type { CalendarDateValue } from "../design-system/CalendarDate";
import {
  defaultTrainerPracticeApi,
  queryOpeningCatalogueSnapshot,
  isValidAsOf,
  queryTrainingRequirements,
  TrainerPracticeQueryError,
  type OpeningCatalogueSnapshotResult,
  type TrainerColor,
  type TrainerPracticeFilters,
  type TrainingRequirementsResult,
} from "./trainerPracticeApi";
import type { OpeningSelection } from "./OpeningSearchCombobox";
import { TrainerPracticePanel, type TrainerPracticeFormValues } from "./TrainerPracticePanel";

export type TrainerPracticeApi = {
  loadCatalogue: (signal?: AbortSignal) => Promise<OpeningCatalogueSnapshotResult>;
  loadRequirements: (
    filters: TrainerPracticeFilters,
    signal?: AbortSignal,
  ) => Promise<TrainingRequirementsResult>;
};

type CatalogueState = {
  status: "loading" | "ready" | "error";
  openings: OpeningCatalogueItemResponse[];
};

type RetrievalState =
  | { status: "idle" | "loading" }
  | { status: "catalogue-error" | "retrieval-error" | "invalid-date" | "stale-date" }
  | { status: "empty" | "success"; data: TrainingRequirementResponse };

function retrievalStateFromResult(result: TrainingRequirementsResult): RetrievalState {
  if (result.status !== "success") {
    return {
      status: result.status.replace("_", "-") as Exclude<
        RetrievalState["status"],
        "idle" | "loading" | "empty" | "success"
      >,
    };
  }
  return {
    status: result.data.items.length === 0 ? "empty" : "success",
    data: result.data,
  };
}

export function TrainerPracticePage({
  api = defaultTrainerPracticeApi,
}: {
  api?: TrainerPracticeApi;
}) {
  const [catalogueSearch, setCatalogueSearch] = useState("");
  const [openingSelection, setOpeningSelection] = useState<OpeningSelection>(null);
  const [trainerColor, setTrainerColor] = useState<"" | TrainerColor>("");
  const [asOf, setAsOf] = useState<CalendarDateValue>(() =>
    toUtcMidnight(getUtcCalendarDay(new Date())),
  );
  const [submittedFilters, setSubmittedFilters] = useState<TrainerPracticeFilters | null>(null);
  const [invalidDateSubmitted, setInvalidDateSubmitted] = useState(false);
  const [storedCatalogue] = useState(readOpeningCatalogueSnapshot);

  const catalogueResult = useQuery({
    queryKey: queryKeys.openingsCatalogueSnapshot(),
    queryFn: ({ signal }) => queryOpeningCatalogueSnapshot(api.loadCatalogue, signal),
    initialData: storedCatalogue?.items,
    initialDataUpdatedAt: storedCatalogue === null ? undefined : 0,
    retry: false,
    staleTime: 15 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });

  const queryFilters = submittedFilters ?? {
    asOf: "",
    openingKey: null,
    trainerColor: null,
  };
  const requirementsResult = useQuery({
    queryKey: queryKeys.trainingRequirements({
      asOf: queryFilters.asOf,
      trainerColor: queryFilters.trainerColor,
      openingKey: queryFilters.openingKey,
      openingMatch: queryFilters.openingKey === null ? null : "reached",
      trainingRequirementLt: 0,
      pageSize: 100,
    }),
    queryFn: ({ signal }) =>
      queryTrainingRequirements(api.loadRequirements, submittedFilters!, signal),
    enabled: submittedFilters !== null,
    retry: false,
    staleTime: 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  const catalogueStatus: CatalogueState["status"] = catalogueResult.isError
    ? "error"
    : catalogueResult.isFetching || !catalogueResult.isSuccess
      ? "loading"
      : "ready";
  const openings = catalogueResult.data ?? storedCatalogue?.items ?? [];

  const retrieval: RetrievalState =
    submittedFilters === null
      ? invalidDateSubmitted
        ? { status: "invalid-date" }
        : { status: "idle" }
      : requirementsResult.isPending
        ? { status: "loading" }
        : requirementsResult.isError
          ? {
              status: (requirementsResult.error instanceof TrainerPracticeQueryError
                ? requirementsResult.error.status
                : "retrieval_error"
              ).replace("_", "-") as Exclude<
                RetrievalState["status"],
                "idle" | "loading" | "empty" | "success"
              >,
            }
          : requirementsResult.data === undefined
            ? { status: "loading" }
            : retrievalStateFromResult({ status: "success", data: requirementsResult.data });

  const handleSubmit = useCallback(
    (values: TrainerPracticeFormValues) => {
      if (values.openingSelection === null) {
        setSubmittedFilters(null);
        setInvalidDateSubmitted(false);
        return;
      }
      const asOfString = values.asOf === null ? "" : formatUtcDate(values.asOf);
      if (!isValidAsOf(asOfString)) {
        setSubmittedFilters(null);
        setInvalidDateSubmitted(true);
        return;
      }

      const filters: TrainerPracticeFilters = {
        asOf: asOfString,
        openingKey:
          values.openingSelection?.kind === "specific" ? values.openingSelection.key : null,
        trainerColor: values.trainerColor === "" ? null : values.trainerColor,
      };
      setInvalidDateSubmitted(false);
      if (
        submittedFilters !== null &&
        submittedFilters.asOf === filters.asOf &&
        submittedFilters.openingKey === filters.openingKey &&
        submittedFilters.trainerColor === filters.trainerColor
      ) {
        if (requirementsResult.isError) {
          void requirementsResult.refetch();
        }
        return;
      }
      setSubmittedFilters(filters);
    },
    [requirementsResult, submittedFilters],
  );

  const handleRetryCatalogue = useCallback(() => {
    void catalogueResult.refetch();
  }, [catalogueResult]);

  const handleMissingOpeningSelection = useCallback(() => {
    setOpeningSelection(null);
    setCatalogueSearch("");
  }, []);

  return (
    <TrainerPracticePanel
      values={{ openingSelection, trainerColor, asOf }}
      catalogueSearch={catalogueSearch}
      openings={openings}
      catalogueStatus={catalogueStatus}
      retrieval={retrieval}
      onOpeningSelectionChange={setOpeningSelection}
      onCatalogueSearchChange={setCatalogueSearch}
      onMissingOpeningSelection={handleMissingOpeningSelection}
      onTrainerColorChange={setTrainerColor}
      onAsOfChange={setAsOf}
      onSubmit={handleSubmit}
      onRetryCatalogue={handleRetryCatalogue}
    />
  );
}
