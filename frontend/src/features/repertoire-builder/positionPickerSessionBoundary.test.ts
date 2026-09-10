import { describe, expect, it } from "vitest";

import type { GameMainLineModel } from "../game/gameModel";
import {
  applySessionMove,
  createFreshSession,
  loadImportedSession,
  navigateSession,
  resetSession,
  returnToGame,
  selectSessionPly,
  sessionHistory,
  sessionHistoryBounds,
  sessionOrientation,
  STANDARD_START_FEN,
} from "./positionPickerSessionBoundary";

const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";
const AFTER_E5_FEN = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2";
const AFTER_NF3_FEN = "rnbqkbnr/pppp1ppp/8/4p3/5N2/8/PPPP1PPP/RNBQKB1R b KQkq - 1 2";
const AFTER_D4_FEN = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1";
const AFTER_C4_FEN = "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1";

const MAIN_LINE: GameMainLineModel = {
  gameUuid: "0007925c-5a8d-11f0-9740-f690a301000f",
  initialFen: STANDARD_START_FEN,
  trainerOrientation: "black",
  occurrences: [
    { ply: 0, fen: STANDARD_START_FEN, outgoingUci: "e2e4", san: "e4" },
    { ply: 1, fen: AFTER_E4_FEN, outgoingUci: "e7e5", san: "e5" },
    { ply: 2, fen: AFTER_E5_FEN, outgoingUci: "g1f3", san: "Nf3" },
    { ply: 3, fen: AFTER_NF3_FEN, outgoingUci: null, san: null },
  ],
};

const OTHER_MAIN_LINE: GameMainLineModel = {
  gameUuid: "11111111-1111-1111-1111-111111111111",
  initialFen: AFTER_D4_FEN,
  trainerOrientation: "white",
  occurrences: [{ ply: 0, fen: AFTER_D4_FEN, outgoingUci: null, san: null }],
};

describe("position picker session boundary", () => {
  it("creates fresh state and Reset discards a temporary line", () => {
    const fresh = createFreshSession();
    const branched = applySessionMove(fresh, {
      outgoingUCI: "e2e4",
      resultingFEN: AFTER_E4_FEN,
      san: "e4",
    });
    const reset = resetSession();

    expect(fresh).toMatchObject({
      kind: "fresh",
      mainLine: null,
      currentIndex: 0,
      currentPosition: { ply: 0, fen: STANDARD_START_FEN, san: null },
      selectedTransition: null,
      branch: null,
    });
    expect(branched.branch?.positions).toHaveLength(1);
    expect(reset).toEqual(fresh);
  });

  it("loads the complete immutable main line at Ply 0 with Next available", () => {
    const session = loadImportedSession(MAIN_LINE);

    expect(session.kind).toBe("imported");
    expect(session.mainLine).toBe(MAIN_LINE);
    expect(session.currentPosition).toEqual({ ply: 0, fen: STANDARD_START_FEN, san: null });
    expect(session.selectedTransition).toBeNull();
    expect(session.branch).toBeNull();
    expect(sessionHistory(session).map((position) => position.ply)).toEqual([0, 1, 2, 3]);
    expect(sessionHistory(session).map((position) => position.san)).toEqual([
      null,
      "e4",
      "e5",
      "Nf3",
    ]);
    expect(sessionHistoryBounds(session)).toEqual({ firstPly: 0, lastPly: 3 });
    expect(navigateSession(session, "next").currentPosition.ply).toBe(1);
  });

  it("bounds Previous, Next, Home, End, and direct history selection", () => {
    const session = loadImportedSession(MAIN_LINE);
    const atEnd = navigateSession(session, "end");

    expect(atEnd.currentPosition.ply).toBe(3);
    expect(navigateSession(atEnd, "next").currentPosition.ply).toBe(3);
    expect(navigateSession(atEnd, "previous").currentPosition.ply).toBe(2);
    expect(navigateSession(atEnd, "home").currentPosition.ply).toBe(0);
    expect(navigateSession(session, "previous").currentPosition.ply).toBe(0);
    expect(selectSessionPly(session, 2)?.currentPosition).toEqual({
      ply: 2,
      fen: AFTER_E5_FEN,
      san: "e5",
    });
    expect(selectSessionPly(session, 99)).toBeNull();
  });

  it("derives the selected parent transition and has none at Ply 0", () => {
    const session = loadImportedSession(MAIN_LINE);

    expect(session.selectedTransition).toBeNull();
    expect(selectSessionPly(session, 1)?.selectedTransition).toEqual({
      parentFEN: STANDARD_START_FEN,
      outgoingUCI: "e2e4",
    });
    expect(selectSessionPly(session, 2)?.selectedTransition).toEqual({
      parentFEN: AFTER_E4_FEN,
      outgoingUCI: "e7e5",
    });
  });

  it("advances a matching main-line move without creating a branch", () => {
    const session = loadImportedSession(MAIN_LINE);
    const advanced = applySessionMove(session, {
      outgoingUCI: "e2e4",
      resultingFEN: "ignored for an imported match",
      san: "ignored for an imported match",
    });

    expect(advanced.currentPosition).toEqual({ ply: 1, fen: AFTER_E4_FEN, san: "e4" });
    expect(advanced.branch).toBeNull();
    expect(advanced.mainLine).toBe(MAIN_LINE);
  });

  it("creates one linear branch, preserves the main line, and does not rejoin by FEN", () => {
    const session = loadImportedSession(MAIN_LINE);
    const branched = applySessionMove(session, {
      outgoingUCI: "d2d4",
      resultingFEN: AFTER_E4_FEN,
      san: "d4",
    });
    const continued = applySessionMove(branched, {
      outgoingUCI: "e7e5",
      resultingFEN: AFTER_E5_FEN,
      san: "e5",
    });

    expect(continued.mainLine).toBe(MAIN_LINE);
    expect(continued.branch).toMatchObject({
      branchPointIndex: 0,
      positions: [
        { ply: 1, fen: AFTER_E4_FEN, san: "d4" },
        { ply: 2, fen: AFTER_E5_FEN, san: "e5" },
      ],
    });
    expect(sessionHistory(continued).map((position) => position.san)).toEqual([null, "d4", "e5"]);
    expect(continued.selectedTransition).toEqual({
      parentFEN: AFTER_E4_FEN,
      outgoingUCI: "e7e5",
    });
  });

  it("replaces only the branch tail after replaying from earlier branch history", () => {
    const branched = applySessionMove(loadImportedSession(MAIN_LINE), {
      outgoingUCI: "d2d4",
      resultingFEN: AFTER_D4_FEN,
      san: "d4",
    });
    const continued = applySessionMove(branched, {
      outgoingUCI: "e7e5",
      resultingFEN: AFTER_E5_FEN,
      san: "e5",
    });
    const earlier = selectSessionPly(continued, 1)!;
    const replaced = applySessionMove(earlier, {
      outgoingUCI: "c7c5",
      resultingFEN: AFTER_C4_FEN,
      san: "c5",
    });

    expect(sessionHistory(replaced).map((position) => position.san)).toEqual([null, "d4", "c5"]);
    expect(replaced.branch?.positions).toHaveLength(2);
    expect(replaced.branch?.transitions.map((transition) => transition.outgoingUCI)).toEqual([
      "d2d4",
      "c7c5",
    ]);
    expect(replaced.mainLine).toBe(MAIN_LINE);
  });

  it("returns to the imported game at the branch point and discards the branch", () => {
    const branched = applySessionMove(loadImportedSession(MAIN_LINE), {
      outgoingUCI: "d2d4",
      resultingFEN: AFTER_D4_FEN,
      san: "d4",
    });
    const returned = returnToGame(branched);

    expect(returned.branch).toBeNull();
    expect(returned.currentPosition).toEqual({ ply: 0, fen: STANDARD_START_FEN, san: null });
    expect(returned.selectedTransition).toBeNull();
    expect(sessionHistory(returned)).toEqual(sessionHistory(loadImportedSession(MAIN_LINE)));
  });

  it("replaces the current session when a new game is loaded", () => {
    const branched = applySessionMove(loadImportedSession(MAIN_LINE), {
      outgoingUCI: "d2d4",
      resultingFEN: AFTER_D4_FEN,
      san: "d4",
    });
    const replacement = loadImportedSession(OTHER_MAIN_LINE);

    expect(replacement.mainLine).toBe(OTHER_MAIN_LINE);
    expect(replacement.mainLine).not.toBe(branched.mainLine);
    expect(replacement.branch).toBeNull();
    expect(replacement.currentPosition).toEqual({ ply: 0, fen: AFTER_D4_FEN, san: null });
  });

  it("keeps trainer orientation with the imported boundary", () => {
    expect(sessionOrientation(createFreshSession())).toBe("white");
    expect(sessionOrientation(loadImportedSession(MAIN_LINE))).toBe("black");
  });
});
