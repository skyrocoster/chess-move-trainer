import type { OpeningCatalogueItemResponse } from "../../api/client";

export const OPENING_CATALOGUE_STORAGE_KEY = "cmt.openings.catalogue.v1";
export const OPENING_CATALOGUE_STORAGE_SCHEMA = 1 as const;

export type OpeningCatalogueSnapshot = {
  storage_schema: typeof OPENING_CATALOGUE_STORAGE_SCHEMA;
  catalogue_version: string;
  items: OpeningCatalogueItemResponse[];
};

export type OpeningCatalogueStorage = Pick<Storage, "getItem" | "removeItem" | "setItem">;

const ITEM_FIELDS = [
  "key",
  "eco",
  "name",
  "route_count",
  "games_reached",
  "games_deepest",
] as const;
const SNAPSHOT_FIELDS = ["storage_schema", "catalogue_version", "items"] as const;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function hasExactFields(value: Record<string, unknown>, fields: readonly string[]): boolean {
  const keys = Object.keys(value);
  return keys.length === fields.length && fields.every((field) => keys.includes(field));
}

function isNonemptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim() !== "";
}

function isFiniteInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && Number.isInteger(value);
}

export function isOpeningCatalogueItem(value: unknown): value is OpeningCatalogueItemResponse {
  if (!isRecord(value) || !hasExactFields(value, ITEM_FIELDS)) {
    return false;
  }

  return (
    isNonemptyString(value.key) &&
    isNonemptyString(value.eco) &&
    isNonemptyString(value.name) &&
    isFiniteInteger(value.route_count) &&
    isFiniteInteger(value.games_reached) &&
    isFiniteInteger(value.games_deepest)
  );
}

export function isOpeningCatalogueSnapshot(value: unknown): value is OpeningCatalogueSnapshot {
  if (!isRecord(value) || !hasExactFields(value, SNAPSHOT_FIELDS)) {
    return false;
  }
  if (value.storage_schema !== OPENING_CATALOGUE_STORAGE_SCHEMA) {
    return false;
  }
  if (!isNonemptyString(value.catalogue_version) || !Array.isArray(value.items)) {
    return false;
  }

  const keys = new Set<string>();
  return value.items.every((item) => {
    if (!isOpeningCatalogueItem(item) || keys.has(item.key)) {
      return false;
    }
    keys.add(item.key);
    return true;
  });
}

function browserStorage(): OpeningCatalogueStorage | null {
  try {
    return typeof localStorage === "undefined" ? null : localStorage;
  } catch {
    return null;
  }
}

function discardInvalidSnapshot(storage: OpeningCatalogueStorage): void {
  try {
    storage.removeItem(OPENING_CATALOGUE_STORAGE_KEY);
  } catch {
    // Storage can become unavailable between the read and the cleanup.
  }
}

export function readOpeningCatalogueSnapshot(
  storage: OpeningCatalogueStorage | null = browserStorage(),
): OpeningCatalogueSnapshot | null {
  if (storage === null) {
    return null;
  }

  let raw: string | null;
  try {
    raw = storage.getItem(OPENING_CATALOGUE_STORAGE_KEY);
  } catch {
    return null;
  }
  if (raw === null) {
    return null;
  }

  try {
    const parsed: unknown = JSON.parse(raw);
    if (isOpeningCatalogueSnapshot(parsed)) {
      return parsed;
    }
  } catch {
    // Invalid JSON is handled as a cache miss below.
  }

  discardInvalidSnapshot(storage);
  return null;
}

export function writeOpeningCatalogueSnapshot(
  snapshot: OpeningCatalogueSnapshot,
  storage: OpeningCatalogueStorage | null = browserStorage(),
): boolean {
  if (storage === null || !isOpeningCatalogueSnapshot(snapshot)) {
    return false;
  }

  try {
    storage.setItem(OPENING_CATALOGUE_STORAGE_KEY, JSON.stringify(snapshot));
    return true;
  } catch {
    return false;
  }
}
