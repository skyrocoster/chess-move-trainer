import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { deletePreferredMoves, getPreferredMoves, putPreferredMoves } from "../../api/client";
import {
  deletePreferredMove,
  fetchPreferredMove,
  getPreferredMoveDateWindow,
  putPreferredMove,
} from "./preferredMoveApi";

vi.mock("../../api/client", () => ({
  deletePreferredMoves: vi.fn(),
  getPreferredMoves: vi.fn(),
  putPreferredMoves: vi.fn(),
}));

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const NOVEL_FEN = "k7/8/8/8/8/8/4P3/4K3 w - - 0 1";
const TODAY = "2026-01-02";
const TOMORROW = "2026-01-03";

function cleanResponse(
  preference: { kind: "move"; uci: string } | { kind: "no_preference" } | { kind: "unconfigured" },
  fen = FEN,
) {
  return {
    fen,
    from: TODAY,
    until: TOMORROW,
    segments: [{ from: TODAY, until: TOMORROW, preference }],
  };
}

function putResponse(fen = FEN, uci = "e2e4") {
  return {
    fen,
    effective_from: TODAY,
    effective_until: null,
    preference: { kind: "move", uci },
    periods: [
      {
        effective_from: TODAY,
        effective_until: null,
        preference: { kind: "move", uci },
      },
    ],
  };
}

function deleteResponse(fen = FEN) {
  return {
    fen,
    effective_from: TODAY,
    effective_until: null,
    periods: [
      {
        effective_from: TODAY,
        effective_until: null,
        preference: { kind: "no_preference" },
      },
    ],
  };
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-01-02T23:59:59.999Z"));
});

afterEach(() => {
  vi.useRealTimers();
  vi.clearAllMocks();
});

describe("getPreferredMoveDateWindow", () => {
  it("derives a deterministic UTC today/tomorrow window", () => {
    expect(getPreferredMoveDateWindow(new Date("2026-12-31T23:59:59.999Z"))).toEqual({
      today: "2026-12-31",
      tomorrow: "2027-01-01",
    });
  });
});

describe("fetchPreferredMove", () => {
  it("uses the generated clean GET with the finite UTC window and preserves abort", async () => {
    const controller = new AbortController();
    vi.mocked(getPreferredMoves).mockResolvedValue({
      data: cleanResponse({ kind: "move", uci: "e2e4" }),
    } as never);

    await expect(fetchPreferredMove(FEN, { signal: controller.signal })).resolves.toEqual({
      status: "success",
      data: {
        fen: FEN,
        state: "assigned",
        move: { uci: "e2e4", san: "e4" },
        effective_at: TODAY,
      },
    });
    expect(getPreferredMoves).toHaveBeenCalledWith({
      query: { fen: FEN, from: TODAY, until: TOMORROW },
      signal: controller.signal,
    });
  });

  it.each([
    [{ kind: "no_preference" as const }, "unassigned"],
    [{ kind: "unconfigured" as const }, "unassigned"],
  ])("maps clean %s to the current no-saved view", async (preference, state) => {
    vi.mocked(getPreferredMoves).mockResolvedValue({ data: cleanResponse(preference) } as never);

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({
      status: "success",
      data: { fen: FEN, state, move: null, effective_at: null },
    });
  });

  it("selects the first complete one-day segment without doing schedule arithmetic", async () => {
    vi.mocked(getPreferredMoves).mockResolvedValue({
      data: {
        fen: FEN,
        from: TODAY,
        until: TOMORROW,
        segments: [
          { from: TODAY, until: TOMORROW, preference: { kind: "move", uci: "e2e5" } },
          { from: TODAY, until: TOMORROW, preference: { kind: "move", uci: "e2e4" } },
        ],
      },
    } as never);

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({
      status: "success",
      data: {
        fen: FEN,
        state: "assigned",
        move: { uci: "e2e4", san: "e4" },
        effective_at: TODAY,
      },
    });
  });

  it("rejects a clean response that cannot identify the requested one-day segment", async () => {
    vi.mocked(getPreferredMoves).mockResolvedValue({
      data: {
        fen: FEN,
        from: TODAY,
        until: TOMORROW,
        segments: [{ from: TODAY, until: "2026-01-04", preference: { kind: "unconfigured" } }],
      },
    } as never);

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it.each([
    [422, "invalid_fen"],
    [422, "invalid_from"],
    [422, "invalid_until"],
    [422, "invalid_window"],
    [422, "invalid_effective_from"],
    [422, "invalid_effective_until"],
    [422, "invalid_preference"],
    [422, "invalid_uci"],
    [422, "illegal_move"],
    [503, "preferred_moves_unavailable"],
    [500, "unexpected_failure"],
  ] as const)("maps only the typed clean HTTP failure %s/%s", async (status, code) => {
    vi.mocked(getPreferredMoves).mockResolvedValue({
      error: { code, message: "safe detail" },
      response: { status },
    } as never);

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({ status: code });
  });

  it("does not preserve legacy position or timestamp meanings", async () => {
    vi.mocked(getPreferredMoves).mockResolvedValue({
      error: { code: "position_not_found", message: "legacy" },
      response: { status: 404 },
    } as never);

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it("rejects an invalid FEN before making a generated request", async () => {
    await expect(fetchPreferredMove("not a FEN" as never)).resolves.toEqual({
      status: "invalid_fen",
    });
    expect(getPreferredMoves).not.toHaveBeenCalled();
  });
});

describe("putPreferredMove", () => {
  it("sends the clean open-ended PUT body with UTC today", async () => {
    const controller = new AbortController();
    vi.mocked(putPreferredMoves).mockResolvedValue({ data: putResponse() } as never);

    await expect(
      putPreferredMove({ fen: FEN, move_uci: "e2e4" }, { signal: controller.signal }),
    ).resolves.toEqual({ status: "success", data: putResponse() });
    expect(putPreferredMoves).toHaveBeenCalledWith({
      body: {
        fen: FEN,
        effective_from: TODAY,
        preference: { kind: "move", uci: "e2e4" },
      },
      signal: controller.signal,
    });
  });

  it("accepts a legal novel parent FEN without corpus membership", async () => {
    vi.mocked(putPreferredMoves).mockResolvedValue({
      data: putResponse(NOVEL_FEN, "e2e4"),
    } as never);

    await expect(putPreferredMove({ fen: NOVEL_FEN, move_uci: "e2e4" })).resolves.toEqual({
      status: "success",
      data: putResponse(NOVEL_FEN, "e2e4"),
    });
    expect(putPreferredMoves).toHaveBeenCalledWith({
      body: {
        fen: NOVEL_FEN,
        effective_from: TODAY,
        preference: { kind: "move", uci: "e2e4" },
      },
      signal: undefined,
    });
  });

  it.each([
    ["e2e", "invalid_uci"],
    ["e2e5", "illegal_move"],
  ] as const)("rejects %s as %s before mutation", async (move_uci, status) => {
    await expect(putPreferredMove({ fen: FEN, move_uci })).resolves.toEqual({ status });
    expect(putPreferredMoves).not.toHaveBeenCalled();
  });
});

describe("deletePreferredMove", () => {
  it("sends the clean open-ended DELETE body with no effective_until", async () => {
    vi.mocked(deletePreferredMoves).mockResolvedValue({ data: deleteResponse() } as never);

    await expect(deletePreferredMove({ fen: FEN })).resolves.toEqual({
      status: "success",
      data: deleteResponse(),
    });
    expect(deletePreferredMoves).toHaveBeenCalledWith({
      body: { fen: FEN, effective_from: TODAY },
      signal: undefined,
    });
  });
});
