import { describe, expect, it } from "vitest";

import type { PositionContextResponse } from "../viewer/positionContextApi";
import {
  beginPreferredMoveDraft,
  cancelPreferredMoveDraft,
  deriveRepertoirePositionModel,
  emptyPreferredMoveDraft,
  stagePreferredMoveDraft,
} from "./repertoireWorkflowModel";
import type { PositionPickerMoveRecord } from "./positionPickerSession";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return {
    fen: FEN,
    overall_exists: true,
    white_count: 2,
    black_count: 0,
    white_total: 3,
    black_total: 2,
    ...overrides,
  };
}

const WHITE_MOVE: PositionPickerMoveRecord = {
  sourceSquare: "e2",
  targetSquare: "e4",
  color: "white",
  san: "e4",
  position: { ply: 1, fen: AFTER_E4_FEN, san: "e4" },
};

const BLACK_MOVE: PositionPickerMoveRecord = {
  sourceSquare: "e7",
  targetSquare: "e5",
  color: "black",
  san: "e5",
  position: { ply: 1, fen: AFTER_E4_FEN, san: "e5" },
};

describe("repertoire position model", () => {
  const assignedPreferredMove = {
    fen: FEN,
    state: "assigned" as const,
    move: { uci: "e2e4", san: "e4" },
    effective_at: "2026-01-01T00:00:00.000000Z",
  };

  it.each([
    ["no-saved", null, null, null],
    ["saved", assignedPreferredMove, null, null],
    ["matching-played", assignedPreferredMove, WHITE_MOVE, assignedPreferredMove],
    [
      "unsaved-played",
      { ...assignedPreferredMove, move: { uci: "d2d4", san: "d4" } },
      WHITE_MOVE,
      { ...assignedPreferredMove, move: { uci: "d2d4", san: "d4" } },
    ],
  ])(
    "derives the %s state from saved and last-played workflow data",
    (state, preferredMove, lastPlayedMove, lastPlayedPreferredMove) => {
      expect(
        deriveRepertoirePositionModel({
          context: context(),
          preferredMove,
          sideToMove: "white",
          bottomColor: "white",
          lastPlayedMove,
          lastPlayedPreferredMove,
        }),
      ).toMatchObject({ state });
    },
  );

  it("maps bottom color to its personal count and keeps zero savable", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove: null,
        sideToMove: "white",
        bottomColor: "black",
      }),
    ).toMatchObject({
      personalCount: 0,
      contextMessage: "Never seen as Black",
      saveability: "savable",
    });
  });

  it("marks an absent overall position unsavable even when counts are zero", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context({ overall_exists: false }),
        preferredMove: null,
        sideToMove: "white",
        bottomColor: "white",
      }),
    ).toMatchObject({
      personalCount: 2,
      contextMessage: "Never seen as White",
      saveability: "unsavable",
    });
  });

  it("keeps context unknown until a response exists", () => {
    expect(
      deriveRepertoirePositionModel({
        context: null,
        preferredMove: null,
        sideToMove: "white",
        bottomColor: "white",
      }),
    ).toMatchObject({
      personalCount: null,
      contextMessage: null,
      saveability: "unknown",
    });
  });

  it("only exposes an assigned saved move on the bottom-color turn", () => {
    const preferredMove = assignedPreferredMove;

    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove,
        sideToMove: "white",
        bottomColor: "white",
      }),
    ).toMatchObject({ savedMove: preferredMove.move, savedMoveVisible: true });
    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove,
        sideToMove: "black",
        bottomColor: "white",
      }),
    ).toMatchObject({ savedMove: null, savedMoveVisible: false });
  });

  it("retains the focused preferred response and its persisted effective timestamp", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove: null,
        sideToMove: "black",
        bottomColor: "white",
        lastPlayedMove: WHITE_MOVE,
        lastPlayedPreferredMove: assignedPreferredMove,
      }),
    ).toMatchObject({
      state: "matching-played",
      lastPlayedMove: WHITE_MOVE,
      lastPlayedPreferredMove: assignedPreferredMove,
      effectiveAt: assignedPreferredMove.effective_at,
    });
  });
});

describe("preferred move draft model", () => {
  it("starts and cancels explicit Add/Edit drafts without persistence", () => {
    expect(emptyPreferredMoveDraft()).toEqual({ mode: "idle", stagedMove: null });
    expect(beginPreferredMoveDraft("add")).toEqual({ mode: "add", stagedMove: null });
    expect(beginPreferredMoveDraft("edit")).toEqual({ mode: "edit", stagedMove: null });
    expect(cancelPreferredMoveDraft()).toEqual({ mode: "idle", stagedMove: null });
  });

  it("stages only a bottom-color move and preserves the Add/Edit mode", () => {
    const add = beginPreferredMoveDraft("add");
    const edit = beginPreferredMoveDraft("edit");

    expect(stagePreferredMoveDraft(add, WHITE_MOVE, "white")).toEqual({
      mode: "add",
      stagedMove: WHITE_MOVE,
    });
    expect(stagePreferredMoveDraft(edit, WHITE_MOVE, "white")).toEqual({
      mode: "edit",
      stagedMove: WHITE_MOVE,
    });
    expect(stagePreferredMoveDraft(add, BLACK_MOVE, "white")).toBeNull();
    expect(stagePreferredMoveDraft(emptyPreferredMoveDraft(), WHITE_MOVE, "white")).toBeNull();
  });
});
