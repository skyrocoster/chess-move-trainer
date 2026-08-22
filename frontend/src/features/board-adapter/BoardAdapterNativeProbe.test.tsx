import { describe, expect, it } from "vitest";
import { Chess } from "chess.js";

const STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

describe("chess.js 1.4.0 state oracle", () => {
  it("generates legal moves and rejects illegal move inputs exactly", () => {
    const chess = new Chess(STARTING_FEN);
    const pawnMoves = chess.moves({ square: "e2" });
    const verbosePawnMoves = chess.moves({ square: "e2", verbose: true });

    expect(pawnMoves).toEqual(["e3", "e4"]);
    expect(verbosePawnMoves.map((move) => [move.san, move.isBigPawn()])).toEqual([
      ["e3", false],
      ["e4", true],
    ]);
    expect(() => chess.move({ from: "e2", to: "e5" })).toThrow(
      'Invalid move: {"from":"e2","to":"e5"}',
    );
    expect(() => chess.move("e5")).toThrow("Invalid move: e5");
  });

  it("accepts either side to move from an arbitrary six-field FEN", () => {
    const chess = new Chess("7k/8/8/8/8/8/8/K7 b - - 12 42");

    expect(chess.turn()).toBe("b");
    expect(chess.moves()).toContain("Kg8");
    expect(chess.move("Kg8").san).toBe("Kg8");
    expect(chess.fen()).toBe("6k1/8/8/8/8/8/8/K7 w - - 13 43");
  });

  it("records SAN history and undoes the latest move", () => {
    const chess = new Chess(STARTING_FEN);

    expect(chess.move("e4").san).toBe("e4");
    expect(chess.move("e5").san).toBe("e5");
    expect(chess.history()).toEqual(["e4", "e5"]);
    expect(chess.undo()?.san).toBe("e5");
    expect(chess.history()).toEqual(["e4"]);
    expect(chess.fen()).toBe("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1");
  });

  it("describes castling and en-passant transitions", () => {
    const castling = new Chess("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
    const castlingMoves = castling
      .moves({ verbose: true })
      .filter((move) => move.isKingsideCastle() || move.isQueensideCastle());

    expect(castlingMoves.map((move) => move.san)).toEqual(["O-O", "O-O-O"]);
    expect(castling.move({ from: "e1", to: "g1" }).isKingsideCastle()).toBe(true);
    expect(castling.move({ from: "e8", to: "c8" }).isQueensideCastle()).toBe(true);
    expect(castling.fen()).toBe("2kr3r/8/8/8/8/8/8/R4RK1 w - - 2 2");

    const enPassant = new Chess("4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1");
    expect(enPassant.move({ from: "d7", to: "d5" }).isBigPawn()).toBe(true);
    const capture = enPassant
      .moves({ verbose: true, square: "e5" })
      .find((move) => move.isEnPassant());
    expect(capture?.san).toBe("exd6");
    expect(enPassant.move({ from: "e5", to: "d6" }).isEnPassant()).toBe(true);
    expect(enPassant.fen()).toBe("4k3/8/3P4/8/8/8/8/4K3 b - - 0 2");
  });

  it("supports all four promotion inputs and preserves all six FEN fields", () => {
    const promotions = [
      ["n", "e8=N", "k3N3/8/8/8/8/8/8/4K3 b - - 0 1"],
      ["b", "e8=B", "k3B3/8/8/8/8/8/8/4K3 b - - 0 1"],
      ["r", "e8=R+", "k3R3/8/8/8/8/8/8/4K3 b - - 0 1"],
      ["q", "e8=Q+", "k3Q3/8/8/8/8/8/8/4K3 b - - 0 1"],
    ] as const;

    expect(new Chess("k7/4P3/8/8/8/8/8/4K3 w - - 0 1").moves({ square: "e7" })).toEqual([
      "e8=N",
      "e8=B",
      "e8=R+",
      "e8=Q+",
    ]);

    for (const [promotion, san, fen] of promotions) {
      const chess = new Chess("k7/4P3/8/8/8/8/8/4K3 w - - 0 1");
      const move = chess.move({ from: "e7", to: "e8", promotion });

      expect(move.san).toBe(san);
      expect(move.isPromotion()).toBe(true);
      expect(chess.fen()).toBe(fen);
      expect(chess.fen().split(" ")).toHaveLength(6);
    }

    const omittedPromotion = new Chess("k7/4P3/8/8/8/8/8/4K3 w - - 0 1");
    expect(() => omittedPromotion.move({ from: "e7", to: "e8" })).toThrow(
      'Invalid move: {"from":"e7","to":"e8"}',
    );
  });

  it("reports checkmate, stalemate, insufficient material, and draw predicates", () => {
    const checkmate = new Chess("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1");
    expect(checkmate.isCheck()).toBe(true);
    expect(checkmate.isCheckmate()).toBe(true);
    expect(checkmate.isStalemate()).toBe(false);
    expect(checkmate.isGameOver()).toBe(true);

    const stalemate = new Chess("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1");
    expect(stalemate.isCheck()).toBe(false);
    expect(stalemate.isStalemate()).toBe(true);
    expect(stalemate.isDraw()).toBe(true);
    expect(stalemate.isGameOver()).toBe(true);

    const insufficient = new Chess("8/8/8/8/8/8/2k5/3K4 w - - 0 1");
    expect(insufficient.isInsufficientMaterial()).toBe(true);
    expect(insufficient.isDraw()).toBe(true);

    const fiftyMove = new Chess("8/8/8/8/8/8/2k5/3K4 w - - 100 75");
    expect(fiftyMove.isDrawByFiftyMoves()).toBe(true);
    expect(fiftyMove.isGameOver()).toBe(true);
  });
});
