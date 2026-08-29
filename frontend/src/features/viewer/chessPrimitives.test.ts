import { Chess } from "chess.js";
import { describe, expect, it } from "vitest";

import { strictFen } from "./chessPrimitives";

describe("strictFen", () => {
  it("preserves a white double-step target without a legal en-passant capture", () => {
    const chess = new Chess();

    chess.move({ from: "e2", to: "e4" });

    expect(strictFen(chess)).toBe("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1");
  });

  it("preserves a black double-step target without a legal en-passant capture", () => {
    const chess = new Chess();
    chess.move({ from: "e2", to: "e4" });

    chess.move({ from: "e7", to: "e5" });

    expect(strictFen(chess)).toBe("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2");
  });

  it("preserves legal en-passant targets and serializes the capture result", () => {
    const chess = new Chess("7k/8/8/8/3p4/8/4P3/4K3 w - - 0 1");

    chess.move({ from: "e2", to: "e4" });
    expect(strictFen(chess)).toBe("7k/8/8/8/3pP3/8/8/4K3 b - e3 0 1");

    const capture = chess.move({ from: "d4", to: "e3" });
    expect(capture.san).toBe("dxe3");
    expect(strictFen(chess)).toBe("7k/8/8/8/8/4p3/8/4K3 w - - 0 2");
  });
});
