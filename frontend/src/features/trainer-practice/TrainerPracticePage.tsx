import { useQuery } from "@tanstack/react-query";
import { useCallback, useState } from "react";

import type {
  OpeningCatalogueItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import {
  currentUtcDate,
  defaultTrainerPracticeApi,
  isValidAsOf,
  queryOpeningChoices,
  queryTrainingRequirements,
  TrainerPracticeQueryError,
  type OpeningChoicesResult,
  type TrainerColor,
  type TrainerPracticeFilters,
  type TrainingRequirementsResult,
} from "./trainerPracticeApi";
import {
  TrainerPracticePanel,
  type TrainerPracticeFormValues,
} from "./TrainerPracticePanel";

import { queryKeys } from "../../api/queryKeys";

export type TrainerPracticeApi = {
  loadOpenings: (
    signal?: AbortSignal,
    search?: string,
  ) => Promise<OpeningChoicesResult>;
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
    return { status: result.status.replace("_", "-") as Exclude<RetrievalState["status"], "idle" | "loading" | "empty" | "success"> };
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
  const [catalogueQuery, setCatalogueQuery] = useState("");
  const [openingKey, setOpeningKey] = useState("");
  const [trainerColor, setTrainerColor] = useState<"" | TrainerColor>("");
  const [asOf, setAsOf] = useState(currentUtcDate);
  const [submittedFilters, setSubmittedFilters] = useState<TrainerPracticeFilters | null>(null);
  const [invalidDateSubmitted, setInvalidDateSubmitted] = useState(false);

  const normalizedCatalogueSearch = catalogueQuery.trim() || null;
  const catalogueResult = useQuery({
    queryKey: queryKeys.openingsCatalogue({
      search: catalogueQuery,
      pageSize: 100,
      sort: "name_asc",
    }),
    queryFn: ({ signal }) =>
      queryOpeningChoices(api.loadOpenings, signal, normalizedCatalogueSearch),
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
    : catalogueResult.isSuccess
      ? "ready"
      : "loading";
  const openings = catalogueResult.data ?? [];

  const retrieval: RetrievalState =
    submittedFilters === null
      ? invalidDateSubmitted
        ? { status: "invalid-date" }
        : { status: "idle" }
      : requirementsResult.isPending
        ? { status: "loading" }
        : requirementsResult.isError
          ? {
              status: (
                requirementsResult.error instanceof TrainerPracticeQueryError
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
      if (!isValidAsOf(values.asOf)) {
        setSubmittedFilters(null);
        setInvalidDateSubmitted(true);
        return;
      }

      const filters: TrainerPracticeFilters = {
        asOf: values.asOf,
        openingKey: values.openingKey === "" ? null : values.openingKey,
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

  const handleSearchCatalogue = useCallback(() => {
    setSubmittedFilters(null);
    setInvalidDateSubmitted(false);
    setOpeningKey("");
    const normalizedSearch = catalogueSearch.trim() || null;
    if (normalizedSearch === normalizedCatalogueSearch && catalogueResult.isError) {
      void catalogueResult.refetch();
    } else {
      setCatalogueQuery(catalogueSearch);
    }
  }, [catalogueQuery, catalogueResult, catalogueSearch, normalizedCatalogueSearch]);

  return (
      <TrainerPracticePanel
        values={{ openingKey, trainerColor, asOf }}
        catalogueSearch={catalogueSearch}
        openings={openings}
        catalogueStatus={catalogueStatus}
      retrieval={retrieval}
        onOpeningKeyChange={setOpeningKey}
        onCatalogueSearchChange={setCatalogueSearch}
        onTrainerColorChange={setTrainerColor}
      onAsOfChange={setAsOf}
        onSubmit={handleSubmit}
        onSearchCatalogue={handleSearchCatalogue}
        onRetryCatalogue={handleRetryCatalogue}
    />
  );
}
