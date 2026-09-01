import { describe, expect, it } from "vitest";

import type { PositionContextResponse } from "../viewer/positionContextApi";
import { canonicalMoveUci, deriveRepertoirePositionModel } from "./repertoireWorkflowModel";
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

const DIFFERENT_MOVE: PositionPickerMoveRecord = {
  ...WHITE_MOVE,
  sourceSquare: "d2",
  targetSquare: "d4",
  san: "d4",
};

describe("repertoire position model", () => {
  const assignedPreferredMove = {
    fen: FEN,
    state: "assigned" as const,
    move: { uci: "e2e4", san: "e4" },
    effective_at: "2026-01-01T00:00:00.000000Z",
  };

  it.each([
    ["empty", null, null, "not-applicable"],
    ["first-choice", null, WHITE_MOVE, "not-applicable"],
    ["saved", assignedPreferredMove, null, "not-applicable"],
    ["replacement", assignedPreferredMove, DIFFERENT_MOVE, "different"],
    ["matching", assignedPreferredMove, WHITE_MOVE, "matching"],
  ] as const)(
    "derives the %s relationship from confirmed saved and local staged facts",
    (relationship, preferredMove, stagedMove, comparison) => {
      const model = deriveRepertoirePositionModel({
        context: context(),
        preferredMove,
        sideToMove: "white",
        bottomColor: "white",
        sourceFen: FEN,
        stagedMove,
      });

      expect(model).toMatchObject({
        sourceFen: FEN,
        ownTurn: true,
        relationship,
        comparison,
        savedPresence: preferredMove ? "present" : "absent",
      });
      expect(model.saved).toEqual(
        preferredMove
          ? {
              move: preferredMove.move,
              effectiveAt: preferredMove.effective_at,
              sourceFen: FEN,
            }
          : null,
      );
      expect(model.staged).toEqual(
        stagedMove ? { move: stagedMove, uci: canonicalMoveUci(stagedMove) } : null,
      );
    },
  );

  it("uses canonical UCI, including promotion, rather than SAN for identity", () => {
    const promoted: PositionPickerMoveRecord = {
      ...WHITE_MOVE,
      sourceSquare: "e7",
      targetSquare: "e8",
      san: "e8=Q",
      promotion: "q",
    };

    expect(canonicalMoveUci(promoted)).toBe("e7e8q");
    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove: {
          ...assignedPreferredMove,
          move: { uci: "e7e8n", san: "e8=N" },
        },
        sideToMove: "white",
        bottomColor: "white",
        sourceFen: FEN,
        stagedMove: { ...promoted, san: "e8=N" },
      }),
    ).toMatchObject({ relationship: "replacement", comparison: "different" });
  });

  it("keeps saved facts visible as read-only context on the opponent turn", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove: assignedPreferredMove,
        sideToMove: "black",
        bottomColor: "white",
        sourceFen: FEN,
      }),
    ).toMatchObject({
      ownTurn: false,
      savedPresence: "present",
      saved: {
        move: assignedPreferredMove.move,
        effectiveAt: assignedPreferredMove.effective_at,
        sourceFen: FEN,
      },
      relationship: "saved",
    });
  });

  it("withholds relationship facts until the preferred read is confirmed", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove: null,
        preferredMoveKnown: false,
        sideToMove: "white",
        bottomColor: "white",
        sourceFen: FEN,
        stagedMove: WHITE_MOVE,
      }),
    ).toMatchObject({
      savedPresence: "unknown",
      relationship: "unknown",
      comparison: "unknown",
      saved: null,
      staged: {
        move: WHITE_MOVE,
        uci: "e2e4",
      },
    });
  });

  it("maps bottom color to its personal count and keeps zero savable", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context(),
        preferredMove: null,
        sideToMove: "white",
        bottomColor: "black",
        sourceFen: FEN,
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
        sourceFen: FEN,
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
        sourceFen: FEN,
      }),
    ).toMatchObject({
      personalCount: null,
      contextMessage: null,
      saveability: "unknown",
    });
  });
});
