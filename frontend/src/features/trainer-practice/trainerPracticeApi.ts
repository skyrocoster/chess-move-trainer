import {
  getOpenings,
  getPositionTrainingRequirements,
} from "../../api/client";
import type {
  GetOpeningsData,
  GetPositionTrainingRequirementsData,
  OpeningCatalogueItemResponse,
  OpeningCatalogueResponse,
  TrainingRequirementItemResponse,
  TrainingRequirementResponse,
} from "../../api/client";
import {
  isOpeningCatalogueSnapshot,
  readOpeningCatalogueSnapshot,
  writeOpeningCatalogueSnapshot,
  type OpeningCatalogueSnapshot,
  type OpeningCatalogueStorage,
} from "./openingCatalogueStorage";

export const TRAINING_REQUIREMENTS_PAGE_SIZE = 100;
export const OPENING_CATALOGUE_PAGE_SIZE = 100;
export const OPENINGS_CATALOGUE_VERSION_HEADER = "X-Openings-Catalogue-Version";
const OPENING_CATALOGUE_REQUEST_CONCURRENCY = 4;

export type TrainerColor = "white" | "black";

export type TrainerPracticeFilters = {
  asOf: string;
  openingKey: string | null;
  trainerColor: TrainerColor | null;
};

export type TrainerPracticeFailureCode =
  | "invalid_date"
  | "stale_date"
  | "catalogue_error"
  | "retrieval_error";

export type OpeningChoicesResult =
  | {
      status: "success";
      data: OpeningCatalogueItemResponse[];
      catalogueVersion?: string;
    }
  | { status: "catalogue_error" };

export type TrainingRequirementsResult =
  | { status: "success"; data: TrainingRequirementResponse }
  | { status: Exclude<TrainerPracticeFailureCode, "catalogue_error"> };

export class TrainerPracticeQueryError extends Error {
  constructor(readonly status: TrainerPracticeFailureCode) {
    super(status);
    this.name = "TrainerPracticeQueryError";
  }
}

type OpeningQuery = NonNullable<GetOpeningsData["query"]>;
type TrainingQuery = NonNullable<GetPositionTrainingRequirementsData["query"]>;
type JsonRecord = Record<string, unknown>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null;
}

function isAbortError(value: unknown): boolean {
  return isRecord(value) && value.name === "AbortError";
}

function abortError(): DOMException {
  return new DOMException("The request was aborted", "AbortError");
}

function throwIfAborted(signal?: AbortSignal): void {
  if (signal?.aborted) {
    throw abortError();
  }
}

function errorCode(value: unknown): string | null {
  return isRecord(value) && typeof value.code === "string" ? value.code : null;
}

export function currentUtcDate(date = new Date()): string {
  return date.toISOString().slice(0, 10);
}

export function isValidAsOf(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false;
  }

  const date = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(date.getTime()) && currentUtcDate(date) === value;
}

type OpeningPageResult =
  | {
      status: "success";
      data: OpeningCatalogueResponse;
      catalogueVersion: string | null;
    }
  | { status: "catalogue_error" };

function normalizedSearch(search?: string): string | null {
  const value = search?.trim();
  return value ? value : null;
}

async function fetchOpeningPage(
  page: number,
  search: string | null,
  signal?: AbortSignal,
): Promise<OpeningPageResult> {
  throwIfAborted(signal);

  try {
    const query: OpeningQuery = {
      page,
      page_size: OPENING_CATALOGUE_PAGE_SIZE,
      sort: "name_asc",
    };
    if (search !== null) {
      query.search = search;
    }
    const result = await getOpenings({
      query,
      signal,
    });
    throwIfAborted(signal);
    if (result.data === undefined || result.error !== undefined) {
      return { status: "catalogue_error" };
    }
    const catalogueVersion = result.response?.headers
      .get(OPENINGS_CATALOGUE_VERSION_HEADER)
      ?.trim();
    return {
      status: "success",
      data: result.data,
      catalogueVersion: catalogueVersion || null,
    };
  } catch (error) {
    if (signal?.aborted || isAbortError(error)) {
      throw error;
    }
    return { status: "catalogue_error" };
  }
}

export function buildTrainingRequirementsQuery(
  filters: TrainerPracticeFilters,
  page: number,
): TrainingQuery {
  const query: TrainingQuery = {
    as_of: filters.asOf,
    training_requirement_lt: 0,
    page,
    page_size: TRAINING_REQUIREMENTS_PAGE_SIZE,
  };

  if (filters.trainerColor !== null) {
    query.trainer_color = filters.trainerColor;
  }
  if (filters.openingKey !== null) {
    query.opening_key = filters.openingKey;
    query.opening_match = "reached";
  }

  return query;
}

export async function fetchOpeningChoices(
  signal?: AbortSignal,
  search?: string,
): Promise<OpeningChoicesResult> {
  const normalized = normalizedSearch(search);
  const firstPage = await fetchOpeningPage(1, normalized, signal);
  if (firstPage.status !== "success") {
    return { status: "catalogue_error" };
  }

  const firstPageData = firstPage.data;
  if (normalized === null || !firstPageData.has_next || firstPageData.total_pages <= 1) {
    return {
      status: "success",
      data: firstPageData.items,
      ...(firstPage.catalogueVersion === null
        ? {}
        : { catalogueVersion: firstPage.catalogueVersion }),
    };
  }

  const openings: OpeningCatalogueItemResponse[] = [...firstPageData.items];
  const remainingPageNumbers = Array.from(
    { length: firstPageData.total_pages - 1 },
    (_, index) => index + 2,
  );
  for (
    let offset = 0;
    offset < remainingPageNumbers.length;
    offset += OPENING_CATALOGUE_REQUEST_CONCURRENCY
  ) {
    const pages = await Promise.all(
      remainingPageNumbers
        .slice(offset, offset + OPENING_CATALOGUE_REQUEST_CONCURRENCY)
        .map((page) => fetchOpeningPage(page, normalized, signal)),
    );
    for (const page of pages) {
      if (page.status !== "success") {
        return { status: "catalogue_error" };
      }
      openings.push(...page.data.items);
    }
  }
  return {
    status: "success",
    data: openings,
    ...(firstPage.catalogueVersion === null
      ? {}
      : { catalogueVersion: firstPage.catalogueVersion }),
  };
}

export type OpeningCatalogueSnapshotResult =
  | {
      status: "success";
      data: OpeningCatalogueItemResponse[];
      catalogueVersion: string;
    }
  | { status: "catalogue_error" };

function hasValidCataloguePage(
  page: OpeningCatalogueResponse,
  expectedPage: number,
): boolean {
  return (
    Number.isInteger(page.page) &&
    page.page === expectedPage &&
    Number.isInteger(page.page_size) &&
    page.page_size === OPENING_CATALOGUE_PAGE_SIZE &&
    Number.isInteger(page.total) &&
    page.total >= 0 &&
    Number.isInteger(page.total_pages) &&
    page.total_pages >= 0 &&
    Array.isArray(page.items)
  );
}

export async function fetchOpeningCatalogueSnapshot(
  signal?: AbortSignal,
  storage?: OpeningCatalogueStorage | null,
): Promise<OpeningCatalogueSnapshotResult> {
  const stored = readOpeningCatalogueSnapshot(storage);
  const firstPage = await fetchOpeningPage(1, null, signal);
  if (
    firstPage.status !== "success" ||
    firstPage.catalogueVersion === null ||
    !hasValidCataloguePage(firstPage.data, 1)
  ) {
    return { status: "catalogue_error" };
  }

  const version = firstPage.catalogueVersion;
  if (stored !== null && stored.catalogue_version === version) {
    return {
      status: "success",
      data: stored.items,
      catalogueVersion: version,
    };
  }

  const firstPageData = firstPage.data;
  const remainingPageNumbers = Array.from(
    { length: Math.max(0, firstPageData.total_pages - 1) },
    (_, index) => index + 2,
  );
  const openings: OpeningCatalogueItemResponse[] = [...firstPageData.items];

  for (
    let offset = 0;
    offset < remainingPageNumbers.length;
    offset += OPENING_CATALOGUE_REQUEST_CONCURRENCY
  ) {
    const pages = await Promise.all(
      remainingPageNumbers
        .slice(offset, offset + OPENING_CATALOGUE_REQUEST_CONCURRENCY)
        .map((page) => fetchOpeningPage(page, null, signal)),
    );
    for (const [index, page] of pages.entries()) {
      const expectedPage = remainingPageNumbers[offset + index];
      if (
        page.status !== "success" ||
        page.catalogueVersion !== version ||
        !hasValidCataloguePage(page.data, expectedPage) ||
        page.data.total !== firstPageData.total ||
        page.data.total_pages !== firstPageData.total_pages
      ) {
        return { status: "catalogue_error" };
      }
      openings.push(...page.data.items);
    }
  }

  if (openings.length !== firstPageData.total) {
    return { status: "catalogue_error" };
  }

  const replacement: OpeningCatalogueSnapshot = {
    storage_schema: 1,
    catalogue_version: version,
    items: openings,
  };
  if (!isOpeningCatalogueSnapshot(replacement)) {
    return { status: "catalogue_error" };
  }
  writeOpeningCatalogueSnapshot(replacement, storage);
  return { status: "success", data: openings, catalogueVersion: version };
}

export async function queryOpeningCatalogueSnapshot(
  loadSnapshot: (
    signal?: AbortSignal,
  ) => Promise<OpeningCatalogueSnapshotResult>,
  signal: AbortSignal,
): Promise<OpeningCatalogueItemResponse[]> {
  const result = await loadSnapshot(signal);
  if (result.status !== "success") {
    throw new TrainerPracticeQueryError(result.status);
  }
  return result.data;
}

function mapRequirementsFailure(error: unknown, status: number | null): TrainingRequirementsResult {
  const code = errorCode(error);
  if (status === 409 && code === "training_requirements_stale") {
    return { status: "stale_date" };
  }
  if (status === 422 && code === "invalid_as_of") {
    return { status: "invalid_date" };
  }
  return { status: "retrieval_error" };
}

function itemKey(item: TrainingRequirementItemResponse): string {
  return `${item.fen}\u0000${item.trainer_color}\u0000${item.preferred_move_uci}`;
}

export async function fetchTrainingRequirements(
  filters: TrainerPracticeFilters,
  signal?: AbortSignal,
): Promise<TrainingRequirementsResult> {
  if (!isValidAsOf(filters.asOf)) {
    return { status: "invalid_date" };
  }

  let page = 1;
  let firstPage: TrainingRequirementResponse | null = null;
  const loadedItems: TrainingRequirementItemResponse[] = [];
  const seenPages = new Set<number>();
  const seenItems = new Set<string>();

  while (firstPage === null || loadedItems.length < firstPage.total) {
    throwIfAborted(signal);

    let result;
    try {
      result = await getPositionTrainingRequirements({
        query: buildTrainingRequirementsQuery(filters, page),
        signal,
      });
    } catch (error) {
      if (signal?.aborted || isAbortError(error)) {
        throw error;
      }
      return { status: "retrieval_error" };
    }

    throwIfAborted(signal);
    if (result.data === undefined || result.error !== undefined) {
      return mapRequirementsFailure(result.error, result.response?.status ?? null);
    }

    const response = result.data;
    if (
      seenPages.has(response.page) ||
      response.page !== page ||
      (firstPage !== null && response.total !== firstPage.total)
    ) {
      return { status: "retrieval_error" };
    }
    seenPages.add(response.page);
    firstPage ??= response;

    const before = loadedItems.length;
    for (const item of response.items) {
      const key = itemKey(item);
      if (!seenItems.has(key)) {
        seenItems.add(key);
        loadedItems.push(item);
      }
    }

    if (loadedItems.length >= firstPage.total) {
      break;
    }
    if (response.items.length === 0 || loadedItems.length === before) {
      return { status: "retrieval_error" };
    }
    page += 1;
  }

  return {
    status: "success",
    data: {
      ...firstPage,
      items: loadedItems,
    },
  };
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

export const defaultTrainerPracticeApi = {
  loadCatalogue: fetchOpeningCatalogueSnapshot,
  loadRequirements: fetchTrainingRequirements,
};
