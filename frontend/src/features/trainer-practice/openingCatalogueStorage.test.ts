import { describe, expect, it } from "vitest";

import type { OpeningCatalogueItemResponse } from "../../api/client";
import {
  isOpeningCatalogueSnapshot,
  OPENING_CATALOGUE_STORAGE_KEY,
  readOpeningCatalogueSnapshot,
  writeOpeningCatalogueSnapshot,
  type OpeningCatalogueSnapshot,
  type OpeningCatalogueStorage,
} from "./openingCatalogueStorage";

const ITEM: OpeningCatalogueItemResponse = {
  key: "B10:Caro-Kann Defense",
  eco: "B10",
  name: "Caro-Kann Defense",
  route_count: 2,
  games_reached: 12,
  games_deepest: 9,
};

const SNAPSHOT: OpeningCatalogueSnapshot = {
  storage_schema: 1,
  catalogue_version: "opaque-v1",
  items: [ITEM],
};

function storage(initial: Record<string, string> = {}): OpeningCatalogueStorage {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key) => values.get(key) ?? null,
    removeItem: (key) => values.delete(key),
    setItem: (key, value) => values.set(key, value),
  };
}

describe("opening catalogue storage", () => {
  it("round-trips the exact versioned namespaced envelope", () => {
    const browserStorage = storage();

    expect(writeOpeningCatalogueSnapshot(SNAPSHOT, browserStorage)).toBe(true);
    expect(readOpeningCatalogueSnapshot(browserStorage)).toEqual(SNAPSHOT);
    expect(isOpeningCatalogueSnapshot(SNAPSHOT)).toBe(true);
  });

  it("treats malformed, duplicate, and non-finite snapshots as misses", () => {
    const browserStorage = storage({
      [OPENING_CATALOGUE_STORAGE_KEY]: JSON.stringify({
        ...SNAPSHOT,
        items: [ITEM, ITEM],
      }),
      unrelated: "preserve me",
    });

    expect(readOpeningCatalogueSnapshot(browserStorage)).toBeNull();
    expect(browserStorage.getItem(OPENING_CATALOGUE_STORAGE_KEY)).toBeNull();
    expect(browserStorage.getItem("unrelated")).toBe("preserve me");

    const nonFinite = storage({
      [OPENING_CATALOGUE_STORAGE_KEY]: JSON.stringify({
        ...SNAPSHOT,
        items: [{ ...ITEM, route_count: Number.NaN }],
      }),
    });
    expect(readOpeningCatalogueSnapshot(nonFinite)).toBeNull();
  });

  it("does not throw when browser storage is unavailable or quota-limited", () => {
    const unavailable: OpeningCatalogueStorage = {
      getItem: () => {
        throw new Error("blocked");
      },
      removeItem: () => {
        throw new Error("blocked");
      },
      setItem: () => {
        throw new Error("quota");
      },
    };

    expect(readOpeningCatalogueSnapshot(unavailable)).toBeNull();
    expect(writeOpeningCatalogueSnapshot(SNAPSHOT, unavailable)).toBe(false);
  });
});
