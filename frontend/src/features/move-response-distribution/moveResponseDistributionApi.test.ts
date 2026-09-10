import { afterEach, describe, expect, it, vi } from "vitest";

import {
  fetchMoveResponseDistribution,
  validateMoveResponseDistributionColor,
  validateMoveResponseDistributionFen,
} from "./moveResponseDistributionApi";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const CASTLING_FEN = "4k3/8/8/8/8/8/8/4K2R w K - 0 1";

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    text: async () => JSON.stringify(body),
  } as unknown as Response;
}

function insight(fen: string, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    fen,
    trainer_color: "white",
    as_of: "1999-12-31",
    observed_in_games: true,
    experience: { distinct_game_count: 4, occurrence_count: 5, total_game_count: 8 },
    observed_move_totals: {
      distinct_game_count: 7,
      occurrence_count: 14,
      terminal: { distinct_game_count: 1, occurrence_count: 1 },
    },
    observed_moves: [
      { move_uci: "d2d4", distinct_game_count: 3, occurrence_count: 3 },
      { move_uci: "e2e4", distinct_game_count: 4, occurrence_count: 5 },
      { move_uci: "c2c4", distinct_game_count: 2, occurrence_count: 2 },
      { move_uci: "g1f3", distinct_game_count: 1, occurrence_count: 1 },
      { move_uci: "c2c3", distinct_game_count: 1, occurrence_count: 1 },
      { move_uci: "b2b3", distinct_game_count: 1, occurrence_count: 1 },
      { move_uci: "f2f4", distinct_game_count: 1, occurrence_count: 1 },
    ],
    opening: null,
    analysis: { state: "not_requested", result: null },
    preference: { kind: "unconfigured" },
    ...overrides,
  };
}

function expectedData(fen = FEN) {
  return {
    fen,
    color: "white",
    matching_game_count: 4,
    outgoing_occurrence_count: 14,
    replies: [
      { rank: 1, child_uci: "e2e4", san: "e4", occurrence_count: 5 },
      { rank: 2, child_uci: "d2d4", san: "d4", occurrence_count: 3 },
      { rank: 3, child_uci: "c2c4", san: "c4", occurrence_count: 2 },
      { rank: 4, child_uci: "b2b3", san: "b3", occurrence_count: 1 },
      { rank: 5, child_uci: "c2c3", san: "c3", occurrence_count: 1 },
      { rank: 6, child_uci: "f2f4", san: "f4", occurrence_count: 1 },
      { rank: 7, child_uci: "g1f3", san: "Nf3", occurrence_count: 1 },
    ],
  };
}

function fetchRequest(mock: ReturnType<typeof vi.fn>): Request {
  const request = mock.mock.calls[0]?.[0];
  expect(request).toBeInstanceOf(Request);
  return request as Request;
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("fetchMoveResponseDistribution", () => {
  it("requests Position Insight with the selected FEN, color, UTC date, and signal", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-09-10T21:30:00.000Z"));
    const controller = new AbortController();
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(insight(FEN)));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchMoveResponseDistribution(FEN, "white", controller.signal)).resolves.toEqual({
      status: "success",
      data: expectedData(),
    });

    const request = fetchRequest(fetchMock);
    const url = new URL(request.url);
    expect(url.origin + url.pathname).toBe("http://localhost:5666/api/positions/insight");
    expect(url.searchParams.get("fen")).toBe(FEN);
    expect(url.searchParams.get("trainer_color")).toBe("white");
    expect(url.searchParams.get("as_of")).toBe("2026-09-10");
    controller.abort();
    expect(request.signal.aborted).toBe(true);
  });

  it("accepts additive fields and different counters for the same canonical position", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse(
          insight(COUNTER_VARIANT_FEN, {
            extra_additive: { retained: true },
            as_of: "2000-01-01",
          }),
        ),
      ),
    );

    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({
      status: "success",
      data: expectedData(COUNTER_VARIANT_FEN),
    });
  });

  it("derives legal SAN independently and ranks descending by occurrence then UCI", async () => {
    const body = insight(CASTLING_FEN, {
      observed_move_totals: {
        distinct_game_count: 1,
        occurrence_count: 1,
        terminal: { distinct_game_count: 0, occurrence_count: 0 },
      },
      observed_moves: [{ move_uci: "e1g1", occurrence_count: 1 }],
    });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(body)));

    await expect(fetchMoveResponseDistribution(CASTLING_FEN, "white")).resolves.toEqual({
      status: "success",
      data: {
        fen: CASTLING_FEN,
        color: "white",
        matching_game_count: 4,
        outgoing_occurrence_count: 1,
        replies: [{ rank: 1, child_uci: "e1g1", san: "O-O", occurrence_count: 1 }],
      },
    });
  });

  it.each([
    insight(FEN, { fen: "not a FEN" }),
    insight(FEN, { trainer_color: "black" }),
    insight(FEN, { experience: { distinct_game_count: -1 } }),
    insight(FEN, { experience: { distinct_game_count: 1.5 } }),
    insight(FEN, {
      observed_move_totals: { occurrence_count: -1 },
    }),
    insight(FEN, {
      observed_move_totals: { occurrence_count: 1.5 },
    }),
    insight(FEN, {
      observed_moves: [{ move_uci: "e2e4", occurrence_count: -1 }],
    }),
    insight(FEN, {
      observed_moves: [{ move_uci: "e2e4", occurrence_count: 1.5 }],
      observed_move_totals: { occurrence_count: 1 },
    }),
    insight(FEN, { observed_moves: [{ move_uci: "e2e5", occurrence_count: 1 }] }),
    insight(FEN, { observed_moves: [{ move_uci: "E2E4", occurrence_count: 1 }] }),
    insight(FEN, {
      observed_moves: [
        { move_uci: "e2e4", occurrence_count: 1 },
        { move_uci: "e2e4", occurrence_count: 1 },
      ],
      observed_move_totals: { occurrence_count: 2 },
    }),
    insight(FEN, { observed_move_totals: { occurrence_count: 13 } }),
  ])("rejects malformed, illegal, duplicate, or unreconciled insight data", async (body) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(body)));

    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({
      status: "unexpected_failure",
    });
  });

  it.each([
    [422, "invalid_fen", "invalid_fen"],
    [422, "invalid_trainer_color", "invalid_color"],
    [503, "position_insight_unavailable", "move_response_distribution_unavailable"],
    [500, "unexpected_failure", "unexpected_failure"],
  ] as const)("maps the accepted typed HTTP failure %s/%s", async (status, code, mapped) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ code, message: "safe detail" }, status)),
    );

    await expect(fetchMoveResponseDistribution(FEN, "white")).resolves.toEqual({ status: mapped });
  });

  it("does not trust an accepted insight error code on the wrong HTTP status", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse({ code: "position_insight_unavailable", message: "detail" }, 500),
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

  it("rejects invalid FEN and color before making a request", async () => {
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
