import { afterEach, describe, expect, it, vi } from "vitest";

import {
  fetchMoveResponseDistribution,
  validateMoveResponseDistributionColor,
  validateMoveResponseDistributionFen,
} from "./moveResponseDistributionApi";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";

function response(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function distribution(overrides: Record<string, unknown> = {}) {
  return {
    fen: FEN,
    color: "white",
    matching_game_count: 4,
    replies: [
      {
        rank: 1,
        child_uci: "e2e4",
        san: "e4",
        distinct_game_count: 3,
        opening_name: null,
      },
      {
        rank: 2,
        child_uci: "d2d4",
        san: "d4",
        distinct_game_count: 2,
        opening_name: "Queen's Pawn Game",
      },
    ],
    ...overrides,
  };
}

afterEach(() => vi.unstubAllGlobals());

describe("fetchMoveResponseDistribution", () => {
  it("requests the encoded FEN and selected colour and returns the strict response", async () => {
    const controller = new AbortController();
    const body = distribution();
    const fetchMock = vi.fn().mockResolvedValue(response(body));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchMoveResponseDistribution(FEN, "white", controller.signal)).resolves.toEqual({
      status: "success",
      data: body,
    });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/move-response-distribution?fen=${encodeURIComponent(FEN)}&color=white`,
      { signal: controller.signal },
    );
  });

  it("accepts different counters for the same four-field parent identity", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(response(distribution({ fen: COUNTER_VARIANT_FEN }))),
    );

    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({
      status: "success",
      data: distribution({ fen: COUNTER_VARIANT_FEN }),
    });
  });

  it.each([
    { ...distribution(), extra: true },
    { ...distribution(), fen: "not a FEN" },
    { ...distribution(), color: "black" },
    { ...distribution(), matching_game_count: -1 },
    { ...distribution(), matching_game_count: 1.5 },
    { ...distribution(), replies: [{ ...distribution().replies[0], extra: true }] },
    { ...distribution(), replies: [{ ...distribution().replies[0], rank: 2 }] },
    { ...distribution(), replies: [{ ...distribution().replies[0], child_uci: "e2e5" }] },
    { ...distribution(), replies: [{ ...distribution().replies[0], san: "d4" }] },
    { ...distribution(), replies: [{ ...distribution().replies[0], opening_name: "" }] },
  ])("rejects malformed or mismatched success data", async (body) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response(body)));

    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({
      status: "unexpected_failure",
    });
  });

  it.each([
    [422, "invalid_fen"],
    [422, "invalid_color"],
    [503, "move_response_distribution_unavailable"],
    [500, "unexpected_failure"],
  ] as const)("maps the accepted typed HTTP failure %s/%s", async (status, code) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(response({ code, message: "safe detail" }, status)),
    );

    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({ status: code });
  });

  it("does not trust a valid error code on the wrong HTTP status", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          response({ code: "move_response_distribution_unavailable", message: "detail" }, 500),
        ),
    );

    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({
      status: "unexpected_failure",
    });
  });

  it("returns network failures as unexpected failures and preserves abort rejection", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));
    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({
      status: "unexpected_failure",
    });

    const controller = new AbortController();
    controller.abort();
    const aborted = new DOMException("The operation was aborted.", "AbortError");
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(aborted));
    await expect(fetchMoveResponseDistribution(FEN, "white", controller.signal)).rejects.toBe(
      aborted,
    );
  });

  it("rejects invalid FEN and colour before making a request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchMoveResponseDistribution("", "white")).resolves.toEqual({
      status: "invalid_fen",
    });
    await expect(fetchMoveResponseDistribution(FEN, "green" as "white")).resolves.toEqual({
      status: "invalid_color",
    });
    expect(fetchMock).not.toHaveBeenCalled();
    expect(validateMoveResponseDistributionFen("not a FEN")).toBe("invalid_fen");
    expect(validateMoveResponseDistributionColor("green")).toBe("invalid_color");
  });
});
