import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchPositionContext } from "./positionContextApi";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function context(fen: string, overrides: Record<string, unknown> = {}) {
  return {
    fen,
    overall_exists: true,
    white_count: 2,
    black_count: 1,
    ...overrides,
  };
}

afterEach(() => vi.unstubAllGlobals());

describe("fetchPositionContext", () => {
  it("requests the full FEN with URL encoding and returns the strict response", async () => {
    const controller = new AbortController();
    const body = context(FEN);
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(body));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPositionContext(FEN, controller.signal)).resolves.toEqual({
      status: "success",
      data: body,
    });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/position-context?fen=${encodeURIComponent(FEN)}`,
      { signal: controller.signal },
    );
  });

  it("accepts a response with different counters for the same four-field identity", async () => {
    const body = context(COUNTER_VARIANT_FEN);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(body)));

    await expect(fetchPositionContext(FEN)).resolves.toEqual({ status: "success", data: body });
  });

  it("preserves zero personal-color counts separately from an absent overall position", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(context(AFTER_E4_FEN, { black_count: 0 })))
      .mockResolvedValueOnce(
        jsonResponse(context(FEN, { overall_exists: false, white_count: 0, black_count: 0 })),
      );
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPositionContext(AFTER_E4_FEN)).resolves.toEqual({
      status: "success",
      data: context(AFTER_E4_FEN, { black_count: 0 }),
    });
    await expect(fetchPositionContext(FEN)).resolves.toEqual({
      status: "success",
      data: context(FEN, { overall_exists: false, white_count: 0, black_count: 0 }),
    });
  });

  it.each([
    { ...context(FEN), extra: true },
    { ...context(FEN), white_count: -1 },
    { ...context(FEN), black_count: 1.5 },
    { ...context(FEN), overall_exists: 1 },
    { ...context(FEN), fen: "not a FEN" },
  ])("rejects malformed or extra response data", async (body) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(body)));

    await expect(fetchPositionContext(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it.each([
    [422, "invalid_fen"],
    [503, "position_context_unavailable"],
    [500, "unexpected_failure"],
  ] as const)("maps the accepted typed HTTP failure %s/%s", async (status, code) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ code, message: "safe detail" }, status)),
    );

    await expect(fetchPositionContext(FEN)).resolves.toEqual({ status: code });
  });

  it("does not trust an accepted error code on the wrong HTTP status", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse({ code: "position_context_unavailable", message: "detail" }, 500),
        ),
    );

    await expect(fetchPositionContext(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it("rejects an empty FEN before making a request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPositionContext("")).resolves.toEqual({ status: "invalid_fen" });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
