import { describe, expect, it } from "vitest";

import type { PositionContextResponse } from "../position-context/positionContextApi";
import { sanFromFenAndUci } from "../game/gameModel";
import type { SelectedTransition } from "./positionPickerSessionBoundary";
import { deriveRepertoirePositionModel } from "./repertoireWorkflowModel";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function context(overrides: Partial<PositionContextResponse> = {}): PositionContextResponse {
  return {
    fen: FEN,
    trainerColor: "white",
    observedInGames: true,
    distinctGameCount: 2,
    totalGameCount: 3,
    ...overrides,
  };
}

const E4_TRANSITION: SelectedTransition = { parentFEN: FEN, outgoingUCI: "e2e4" };
const D4_TRANSITION: SelectedTransition = { parentFEN: FEN, outgoingUCI: "d2d4" };

function selectedFact(transition: SelectedTransition) {
  return {
    transition,
    san: sanFromFenAndUci(transition.parentFEN, transition.outgoingUCI),
    uci: transition.outgoingUCI,
  };
}

describe("repertoire position model", () => {
  const assignedPreferredMove = {
    fen: FEN,
    state: "assigned" as const,
    move: { uci: "e2e4", san: "e4" },
    effective_at: "2026-01-01T00:00:00.000000Z",
  };

  it.each([
    ["empty", null, null, "not-applicable"],
    ["first-choice", null, E4_TRANSITION, "not-applicable"],
    ["saved", assignedPreferredMove, null, "not-applicable"],
    ["replacement", assignedPreferredMove, D4_TRANSITION, "different"],
    ["matching", assignedPreferredMove, E4_TRANSITION, "matching"],
  ] as const)(
    "derives the %s relationship from confirmed saved and local selected facts",
    (relationship, preferredMove, selectedTransition, comparison) => {
      const model = deriveRepertoirePositionModel({
        context: context(),
        preferredMove,
        sideToMove: "white",
        bottomColor: "white",
        sourceFen: FEN,
        selectedTransition,
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
      expect(model.selected).toEqual(selectedTransition ? selectedFact(selectedTransition) : null);
    },
  );

  it("uses canonical UCI, including promotion, rather than SAN for identity", () => {
    const PROMOTION_PARENT_FEN = "5k2/4P3/8/8/8/8/8/4K3 w - - 0 1";
    const promotedTransition: SelectedTransition = {
      parentFEN: PROMOTION_PARENT_FEN,
      outgoingUCI: "e7e8q",
    };

    expect(selectedFact(promotedTransition).san).toBe("e8=Q+");
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
        selectedTransition: promotedTransition,
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
        selectedTransition: E4_TRANSITION,
      }),
    ).toMatchObject({
      savedPresence: "unknown",
      relationship: "unknown",
      comparison: "unknown",
      saved: null,
      selected: selectedFact(E4_TRANSITION),
    });
  });

  it("maps the requested trainer color to its distinct-game count and keeps zero savable", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context({ trainerColor: "black", distinctGameCount: 0, totalGameCount: 2 }),
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

  it("marks a globally unobserved position unsavable even when loaded experience exists", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context({ observedInGames: false }),
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

  it("summarizes an observed position with zero selected-color experience as never seen", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context({ trainerColor: "black", distinctGameCount: 0, totalGameCount: 2 }),
        preferredMove: null,
        sideToMove: "black",
        bottomColor: "black",
        sourceFen: FEN,
      }),
    ).toMatchObject({
      contextMessage: "Never seen as Black",
      saveability: "savable",
    });
  });

  it("summarizes seen experience with the trainer color's distinct-game count", () => {
    expect(
      deriveRepertoirePositionModel({
        context: context({ trainerColor: "black", distinctGameCount: 5, totalGameCount: 7 }),
        preferredMove: null,
        sideToMove: "black",
        bottomColor: "black",
        sourceFen: FEN,
      }),
    ).toMatchObject({
      personalCount: 5,
      contextMessage: "Seen in 5 games as Black",
      saveability: "savable",
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
