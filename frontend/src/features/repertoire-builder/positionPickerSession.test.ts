import { describe, expect, it } from "vitest";

import { VIEWER_GAME } from "../viewer/viewerFixtures";
import {
  createStandardStartSession,
  createStoredGameSession,
  flipPositionPickerSession,
  navigatePositionPickerSession,
  appendPositionPickerMove,
  selectPositionPickerMove,
  sessionSanHistory,
} from "./positionPickerSession";

describe("position picker session", () => {
  it("creates a standard-start origin with an empty local continuation", () => {
    const session = createStandardStartSession();

    expect(session.origin).toMatchObject({
      kind: "standard",
      selectedPly: 0,
      bottomColor: "white",
    });
    expect(session.prefix).toHaveLength(1);
    expect(session.prefix[0]).toMatchObject({ ply: 0, san: null });
    expect(session.currentPosition).toEqual(session.prefix[0]);
    expect(session.currentPly).toBe(0);
    expect(session.localContinuation).toEqual([]);
    expect(session.localMoves).toEqual([]);
    expect(session.localCursor).toBe(0);
    expect(session.stagedMove).toBeNull();
    expect(session.orientation).toBe("white");
  });

  it("preserves the complete stored prefix through the selected Ply and starts at that position", () => {
    const session = createStoredGameSession({
      ...VIEWER_GAME,
      initial_ply: 2,
      subject_color: "black",
    });

    expect(session.origin).toMatchObject({
      kind: "stored",
      gameUuid: VIEWER_GAME.game_uuid,
      selectedPly: 2,
      subjectColor: "black",
      bottomColor: "black",
    });
    expect(session.prefix.map((position) => position.ply)).toEqual([0, 1, 2]);
    expect(session.prefix.at(-1)).toEqual(VIEWER_GAME.positions[2]);
    expect(session.currentPosition).toEqual(VIEWER_GAME.positions[2]);
    expect(session.currentPly).toBe(2);
    expect(session.localContinuation).toEqual([]);
    expect(session.localMoves).toEqual([]);
    expect(session.localCursor).toBe(0);
    expect(session.stagedMove).toBeNull();
    expect(session.orientation).toBe("black");
  });

  it("rejects a success value without a complete prefix through its selected Ply", () => {
    expect(() =>
      createStoredGameSession({
        ...VIEWER_GAME,
        initial_ply: 2,
        positions: VIEWER_GAME.positions.slice(0, 2),
      }),
    ).toThrow("complete prefix");
  });

  it("stages a bottom-side move without changing the current position", () => {
    const session = createStandardStartSession();

    const result = selectPositionPickerMove(session, {
      sourceSquare: "e2",
      targetSquare: "e4",
    });

    expect(result?.disposition).toBe("staged");
    expect(result?.session.currentPosition).toEqual(session.currentPosition);
    expect(result?.session.localContinuation).toEqual([]);
    expect(result?.session.stagedMove).toMatchObject({
      san: "e4",
      color: "white",
      position: {
        fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
      },
    });
  });

  it("advances opposing moves, records SAN, and rejects illegal moves without mutation", () => {
    const session = flipPositionPickerSession(createStandardStartSession());

    const result = selectPositionPickerMove(session, {
      sourceSquare: "e2",
      targetSquare: "e4",
    });
    expect(result?.disposition).toBe("advanced");
    expect(result?.session.currentPosition).toMatchObject({
      ply: 1,
      san: "e4",
      fen: "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    });
    expect(result?.session.localMoves[0]).toMatchObject({
      sourceSquare: "e2",
      targetSquare: "e4",
      color: "white",
      san: "e4",
    });

    expect(
      selectPositionPickerMove(result!.session, { sourceSquare: "e2", targetSquare: "e5" }),
    ).toBeNull();
  });

  it("navigates locally and truncates only the replacement continuation", () => {
    let session = flipPositionPickerSession(createStandardStartSession());
    session = selectPositionPickerMove(session, {
      sourceSquare: "e2",
      targetSquare: "e4",
    })!.session;
    session = flipPositionPickerSession(session);
    session = selectPositionPickerMove(session, {
      sourceSquare: "e7",
      targetSquare: "e5",
    })!.session;

    expect(session.localContinuation).toHaveLength(2);
    expect(session.currentPosition.fen).toBe(
      "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
    );
    expect(sessionSanHistory(session)).toBe("1. e4 1... e5");

    session = navigatePositionPickerSession(session, "previous");
    expect(session.currentPly).toBe(1);
    expect(sessionSanHistory(session)).toBe("1. e4");

    session = selectPositionPickerMove(session, {
      sourceSquare: "e7",
      targetSquare: "e6",
    })!.session;
    expect(session.localContinuation).toHaveLength(2);
    expect(sessionSanHistory(session)).toBe("1. e4 1... e6");
    expect(session.localContinuation.at(-1)?.san).toBe("e6");

    session = navigatePositionPickerSession(session, "previous");
    session = navigatePositionPickerSession(session, "next");
    expect(session.currentPosition.san).toBe("e6");
  });

  it("preserves the current position while Flip cancels staging and changes me", () => {
    const staged = selectPositionPickerMove(createStandardStartSession(), {
      sourceSquare: "e2",
      targetSquare: "e4",
    })!.session;
    const flipped = flipPositionPickerSession(staged);

    expect(flipped.currentPosition).toEqual(staged.currentPosition);
    expect(flipped.currentPly).toBe(staged.currentPly);
    expect(flipped.bottomColor).toBe("black");
    expect(flipped.orientation).toBe("black");
    expect(flipped.stagedMove).toBeNull();
  });

  it("keeps the promotion FEN unchanged until a piece is selected", () => {
    const session = flipPositionPickerSession({
      ...createStandardStartSession(),
      prefix: [
        {
          ply: 0,
          fen: "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
          san: null,
        },
      ],
      currentPosition: {
        ply: 0,
        fen: "k7/4P3/8/8/8/8/8/4K3 w - - 0 1",
        san: null,
      },
    });
    const pending = selectPositionPickerMove(session, {
      sourceSquare: "e7",
      targetSquare: "e8",
    });
    expect(pending).toBeNull();

    const promoted = selectPositionPickerMove(session, {
      sourceSquare: "e7",
      targetSquare: "e8",
      promotion: "q",
    });
    expect(promoted?.session.currentPosition.fen).toBe("k3Q3/8/8/8/8/8/8/4K3 b - - 0 1");
  });

  it("plays a saved move through the same strict local continuation", () => {
    const next = appendPositionPickerMove(createStandardStartSession(), {
      sourceSquare: "e2",
      targetSquare: "e4",
    });

    expect(next?.currentPosition.fen).toBe(
      "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    );
  });
});
