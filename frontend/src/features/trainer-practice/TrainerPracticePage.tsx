import { useCallback, useEffect, useRef, useState } from "react";

import type {
  OpeningCatalogueItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import {
  currentUtcDate,
  defaultTrainerPracticeApi,
  isValidAsOf,
  type OpeningChoicesResult,
  type TrainerColor,
  type TrainerPracticeFilters,
  type TrainingRequirementsResult,
} from "./trainerPracticeApi";
import {
  TrainerPracticePanel,
  type TrainerPracticeFormValues,
} from "./TrainerPracticePanel";

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

const initialCatalogueState: CatalogueState = { status: "loading", openings: [] };

function catalogueStateFromResult(result: OpeningChoicesResult): CatalogueState {
  return result.status === "success"
    ? { status: "ready", openings: result.data }
    : { status: "error", openings: [] };
}

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
  const [catalogueRetry, setCatalogueRetry] = useState(0);
  const [catalogue, setCatalogue] = useState<CatalogueState>(initialCatalogueState);
  const [catalogueSearch, setCatalogueSearch] = useState("");
  const [catalogueQuery, setCatalogueQuery] = useState("");
  const [openingKey, setOpeningKey] = useState("");
  const [trainerColor, setTrainerColor] = useState<"" | TrainerColor>("");
  const [asOf, setAsOf] = useState(currentUtcDate);
  const [retrieval, setRetrieval] = useState<RetrievalState>({ status: "idle" });
  const requestId = useRef(0);
  const retrievalController = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setCatalogue(initialCatalogueState);

    void api.loadOpenings(controller.signal, catalogueQuery).then(
      (result) => {
        if (active && !controller.signal.aborted) {
          setCatalogue(catalogueStateFromResult(result));
        }
      },
      () => {
        if (active && !controller.signal.aborted) {
          setCatalogue({ status: "error", openings: [] });
        }
      },
    );

    return () => {
      active = false;
      controller.abort();
    };
  }, [api, catalogueQuery, catalogueRetry]);

  useEffect(
    () => () => {
      requestId.current += 1;
      retrievalController.current?.abort();
    },
    [],
  );

  const handleSubmit = useCallback(
    (values: TrainerPracticeFormValues) => {
      const currentRequest = ++requestId.current;
      retrievalController.current?.abort();

      if (!isValidAsOf(values.asOf)) {
        setRetrieval({ status: "invalid-date" });
        retrievalController.current = null;
        return;
      }

      const controller = new AbortController();
      retrievalController.current = controller;
      setRetrieval({ status: "loading" });

      const filters: TrainerPracticeFilters = {
        asOf: values.asOf,
        openingKey: values.openingKey === "" ? null : values.openingKey,
        trainerColor: values.trainerColor === "" ? null : values.trainerColor,
      };

      void api.loadRequirements(filters, controller.signal).then(
        (result) => {
          if (
            currentRequest === requestId.current &&
            !controller.signal.aborted
          ) {
            setRetrieval(retrievalStateFromResult(result));
          }
        },
        () => {
          if (
            currentRequest === requestId.current &&
            !controller.signal.aborted
          ) {
            setRetrieval({ status: "retrieval-error" });
          }
        },
      );
    },
    [api],
  );

  const handleRetryCatalogue = useCallback(() => {
    setCatalogueRetry((value) => value + 1);
  }, []);

  const handleSearchCatalogue = useCallback(() => {
    requestId.current += 1;
    retrievalController.current?.abort();
    retrievalController.current = null;
    setRetrieval({ status: "idle" });
    setOpeningKey("");
    setCatalogueQuery(catalogueSearch);
    setCatalogueRetry((value) => value + 1);
  }, [catalogueSearch]);

  return (
      <TrainerPracticePanel
        values={{ openingKey, trainerColor, asOf }}
        catalogueSearch={catalogueSearch}
        openings={catalogue.openings}
      catalogueStatus={catalogue.status}
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
