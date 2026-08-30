import { describe, expect, it, vi } from "vitest";

import {
  clampMoveHistoryPly,
  createMoveHistoryModel,
  findMoveHistoryEntry,
  navigateMoveHistory,
} from "./moveHistoryModel";
import type {
  MoveHistoryActivePlyChange,
  MoveHistoryInput,
  MoveHistoryNavigation,
  Ply,
} from "./moveHistoryTypes";

const HISTORY: MoveHistoryInput = {
  initialPosition: { ply: 0 },
  moves: [
    { ply: 1, san: "e4" },
    { ply: 2, san: "e5" },
    { ply: 3, san: "Nf3" },
  ],
};

describe("createMoveHistoryModel", () => {
  it("represents an initial position even when there are no moves", () => {
    const model = createMoveHistoryModel({ initialPosition: { ply: 0 }, moves: [] });

    expect(model.entries).toEqual([{ kind: "initial", ply: 0 }]);
    expect(model.bounds).toEqual({ firstPly: 0, lastPly: 0 });
    expect(findMoveHistoryEntry(model, 0)).toEqual({ kind: "initial", ply: 0 });
  });

  it("keeps the initial position first and preserves SAN move ordering", () => {
    const model = createMoveHistoryModel(HISTORY);

    expect(model.entries).toEqual([
      { kind: "initial", ply: 0 },
      { kind: "move", ply: 1, san: "e4" },
      { kind: "move", ply: 2, san: "e5" },
      { kind: "move", ply: 3, san: "Nf3" },
    ]);
    expect(model.bounds).toEqual({ firstPly: 0, lastPly: 3 });
  });
});

describe("linear Move History navigation", () => {
  const model = createMoveHistoryModel(HISTORY);

  it("keeps active selection within the linear bounds", () => {
    expect(clampMoveHistoryPly(model, -1)).toBe(0);
    expect(clampMoveHistoryPly(model, 2)).toBe(2);
    expect(clampMoveHistoryPly(model, 99)).toBe(3);

    expect(navigateMoveHistory(model, 0, "previous")).toBe(0);
    expect(navigateMoveHistory(model, 3, "next")).toBe(3);
  });

  it.each([
    [0, "next", 1],
    [1, "previous", 0],
    [1, "next", 2],
    [2, "home", 0],
    [2, "end", 3],
  ] as const)("resolves %s from Ply %s to Ply %s", (activePly, navigation, expectedPly) => {
    expect(navigateMoveHistory(model, activePly, navigation)).toBe(expectedPly);
  });

  it("has only one next/previous path and does not expose variations", () => {
    const navigation: MoveHistoryNavigation[] = ["next", "next", "previous"];
    const selectedPlys = navigation.reduce<Ply[]>(
      (plys, action) => [...plys, navigateMoveHistory(model, plys.at(-1)!, action)],
      [0],
    );

    expect(selectedPlys).toEqual([0, 1, 2, 1]);
    expect(model.entries.every((entry) => entry.kind === "initial" || entry.kind === "move")).toBe(
      true,
    );
    expect(Object.values(model.entries[1]!)).not.toContainEqual(expect.any(Array));
  });

  it("leaves selection controlled through a single active-Ply callback", () => {
    const onActivePlyChange = vi.fn<MoveHistoryActivePlyChange>();
    const selectedPly: Ply = navigateMoveHistory(model, 1, "next");

    onActivePlyChange(selectedPly);

    expect(onActivePlyChange).toHaveBeenCalledOnce();
    expect(onActivePlyChange).toHaveBeenCalledWith(2);
  });
});
