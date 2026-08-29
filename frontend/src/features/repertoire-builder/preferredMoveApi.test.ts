import { afterEach, describe, expect, it, vi } from "vitest";

import { deletePreferredMove, fetchPreferredMove, putPreferredMove } from "./preferredMoveApi";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function assigned(fen = FEN) {
  return { fen, state: "assigned", move: { uci: "e2e4", san: "e4" } };
}

function mutation(fen = FEN) {
  return { fen, changed: true, effective_at: "2026-01-01T00:00:00.000000Z" };
}

afterEach(() => vi.unstubAllGlobals());

describe("fetchPreferredMove", () => {
  it("requests the full FEN and preserves an optional as-of instant", async () => {
    const controller = new AbortController();
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(assigned()));
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      fetchPreferredMove(FEN, {
        asOf: "2026-01-02T00:00:00Z",
        signal: controller.signal,
      }),
    ).resolves.toEqual({ status: "success", data: assigned() });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/preferred-move?fen=${encodeURIComponent(FEN)}&as_of=2026-01-02T00%3A00%3A00Z`,
      { signal: controller.signal },
    );
  });

  it("accepts a canonical response with different counters for the same four-field position", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(assigned(COUNTER_FEN))));

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({
      status: "success",
      data: assigned(COUNTER_FEN),
    });
  });

  it("accepts the explicit unassigned response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ fen: FEN, state: "unassigned", move: null })),
    );

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({
      status: "success",
      data: { fen: FEN, state: "unassigned", move: null },
    });
  });

  it.each([
    { ...assigned(), extra: true },
    { ...assigned(), state: "unassigned" },
    { ...assigned(), move: { uci: "e2e5", san: "e5" } },
    { ...assigned(), move: { uci: "e2e4", san: "" } },
    { fen: "not a FEN", state: "assigned", move: { uci: "e2e4", san: "e4" } },
  ])("rejects malformed or extra response data", async (body) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(body)));

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it.each([
    [422, "invalid_fen"],
    [422, "invalid_move"],
    [422, "invalid_timestamp"],
    [422, "future_effective_time"],
    [404, "position_not_found"],
    [503, "preferred_move_unavailable"],
    [500, "unexpected_failure"],
  ] as const)("maps the accepted typed HTTP failure %s/%s", async (status, code) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ code, message: "safe detail" }, status)),
    );

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({ status: code });
  });

  it("does not trust an accepted error code on the wrong HTTP status", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(jsonResponse({ code: "position_not_found", message: "detail" }, 500)),
    );

    await expect(fetchPreferredMove(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it("rejects an invalid full FEN before making a request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPreferredMove("" as never)).resolves.toEqual({ status: "invalid_fen" });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe("putPreferredMove", () => {
  it("sends the fixed-owner request shape with legal canonical UCI", async () => {
    const controller = new AbortController();
    const request = { fen: FEN, move_uci: "e2e4", effective_at: null };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(mutation()));
    vi.stubGlobal("fetch", fetchMock);

    await expect(putPreferredMove(request, { signal: controller.signal })).resolves.toEqual({
      status: "success",
      data: mutation(),
    });
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:5666/api/preferred-move", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: controller.signal,
    });
  });

  it("rejects illegal UCI before making a mutation request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(putPreferredMove({ fen: FEN, move_uci: "e2e5" })).resolves.toEqual({
      status: "invalid_move",
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects an unexpected mutation response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ ...mutation(), extra: true })));

    await expect(putPreferredMove({ fen: FEN, move_uci: "e2e4" })).resolves.toEqual({
      status: "unexpected_failure",
    });
  });
});

describe("deletePreferredMove", () => {
  it("sends the accepted DELETE query and preserves a blank effective date", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(mutation()));
    vi.stubGlobal("fetch", fetchMock);

    await expect(deletePreferredMove({ fen: FEN, effective_at: "" })).resolves.toEqual({
      status: "success",
      data: mutation(),
    });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/preferred-move?fen=${encodeURIComponent(FEN)}&effective_at=`,
      { method: "DELETE", signal: undefined },
    );
  });

  it("accepts a legal promotion UCI request without adding an owner field", async () => {
    const promotionFen = "k7/4P3/8/8/8/8/8/4K3 w - - 0 1";
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(mutation(promotionFen)));
    vi.stubGlobal("fetch", fetchMock);

    await expect(
      putPreferredMove({ fen: promotionFen, move_uci: "e7e8q", effective_at: "" }),
    ).resolves.toEqual({ status: "success", data: mutation(promotionFen) });
    expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({
      body: JSON.stringify({ fen: promotionFen, move_uci: "e7e8q", effective_at: "" }),
    });
  });

  it("uses the accepted counter-sensitive full FEN on mutation responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(mutation(AFTER_E4_FEN))));

    await expect(putPreferredMove({ fen: AFTER_E4_FEN, move_uci: "e7e5" })).resolves.toEqual({
      status: "success",
      data: mutation(AFTER_E4_FEN),
    });
  });
});
