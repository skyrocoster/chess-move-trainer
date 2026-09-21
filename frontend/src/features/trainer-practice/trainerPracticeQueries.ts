import type { OpeningCatalogueItemResponse, TrainingRequirementResponse } from "../../api/client";
import type {
  OpeningCatalogueSnapshotResult,
  OpeningChoicesResult,
  TrainerPracticeFailureCode,
  TrainerPracticeFilters,
  TrainingRequirementsResult,
} from "./trainerPracticeApi";

export class TrainerPracticeQueryError extends Error {
  constructor(readonly status: TrainerPracticeFailureCode) {
    super(status);
    this.name = "TrainerPracticeQueryError";
  }
}

export async function queryOpeningCatalogueSnapshot(
  loadSnapshot: (signal?: AbortSignal) => Promise<OpeningCatalogueSnapshotResult>,
  signal: AbortSignal,
): Promise<OpeningCatalogueItemResponse[]> {
  const result = await loadSnapshot(signal);
  if (result.status !== "success") {
    throw new TrainerPracticeQueryError(result.status);
  }
  return result.data;
}

export async function queryOpeningChoices(
  loadOpenings: (signal?: AbortSignal, search?: string) => Promise<OpeningChoicesResult>,
  signal: AbortSignal,
  search: string | null,
): Promise<OpeningCatalogueItemResponse[]> {
  const result = await loadOpenings(signal, search ?? undefined);
  if (result.status !== "success") {
    throw new TrainerPracticeQueryError(result.status);
  }
  return result.data;
}

export async function queryTrainingRequirements(
  loadRequirements: (
    filters: TrainerPracticeFilters,
    signal?: AbortSignal,
  ) => Promise<TrainingRequirementsResult>,
  filters: TrainerPracticeFilters,
  signal: AbortSignal,
): Promise<TrainingRequirementResponse> {
  const result = await loadRequirements(filters, signal);
  if (result.status !== "success") {
    throw new TrainerPracticeQueryError(result.status);
  }
  return result.data;
}
