import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchPositionContext } from "./positionContextApi";
import type { PositionContextResponse } from "./positionContextApi";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

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
    as_of: "2026-09-10",
    observed_in_games: true,
    experience: { distinct_game_count: 2, occurrence_count: 5, total_game_count: 3 },
    opening: { eco: "A00", key: "a00", match: "route", name: "Uncommon Opening", ply: 0 },
    observed_move_totals: { distinct_game_count: 3, occurrence_count: 5, terminal: {} },
    observed_moves: [{ move_uci: "e2e4", distinct_game_count: 2, occurrence_count: 4 }],
    analysis: { result: null, lines: [] },
    preference: { kind: "unconfigured" },
    ...overrides,
  };
}

function expectedContext(fen: string, overrides: Partial<PositionContextResponse> = {}) {
  return {
    fen,
    trainerColor: "white" as const,
    observedInGames: true,
    distinctGameCount: 2,
    totalGameCount: 3,
    ...overrides,
  };
}

function fetchRequest(mock: ReturnType<typeof vi.fn>): Request {
  const request = mock.mock.calls[0]?.[0];
  expect(request).toBeInstanceOf(Request);
  return request as Request;
}

async function resolveInsightResult(body: unknown, status = 200) {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(body, status));
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock, result: await fetchPositionContext(FEN, "white") };
}

afterEach(() => vi.unstubAllGlobals());

describe("fetchPositionContext", () => {
  it("requests insight for the FEN, trainer color, and request-time UTC as_of", async () => {
    const controller = new AbortController();
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse(insight(FEN, { as_of: "1999-12-31" })));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPositionContext(FEN, "white", controller.signal)).resolves.toEqual({
      status: "success",
      data: expectedContext(FEN),
    });

    const request = fetchRequest(fetchMock);
    const query = new URL(request.url).searchParams;
    expect(new URL(request.url).origin + new URL(request.url).pathname).toBe(
      "http://localhost:5666/api/positions/insight",
    );
    expect(query.get("fen")).toBe(FEN);
    expect(query.get("trainer_color")).toBe("white");
    expect(query.get("as_of")).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(query.get("as_of")).not.toBe("1999-12-31");
    controller.abort();
    expect(request.signal.aborted).toBe(true);
  });

  it("maps a URL-encoded full FEN through the generated client", async () => {
    const { fetchMock, result } = await resolveInsightResult(insight(COUNTER_VARIANT_FEN));
    void result;

    const query = new URL(fetchRequest(fetchMock).url).searchParams;
    expect(query.get("fen")).toBe(FEN);
  });

  it("maps only the C03 experience facts and tolerates additive insight fields", async () => {
    const { result } = await resolveInsightResult(
      insight(COUNTER_VARIANT_FEN, { extra_additive: { nested: true } }),
    );

    expect(result).toEqual({ status: "success", data: expectedContext(COUNTER_VARIANT_FEN) });
  });

  it("preserves zero selected-color experience separately from a globally unseen position", async () => {
    const observedZero = insight(AFTER_E4_FEN, {
      trainer_color: "black",
      experience: { distinct_game_count: 0, occurrence_count: 0, total_game_count: 4 },
    });
    const globallyUnseen = insight(AFTER_E4_FEN, {
      trainer_color: "black",
      observed_in_games: false,
      experience: { distinct_game_count: 0, occurrence_count: 0, total_game_count: 0 },
    });
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(observedZero))
      .mockResolvedValueOnce(jsonResponse(globallyUnseen));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPositionContext(AFTER_E4_FEN, "black")).resolves.toEqual({
      status: "success",
      data: expectedContext(AFTER_E4_FEN, {
        trainerColor: "black",
        distinctGameCount: 0,
        totalGameCount: 4,
      }),
    });
    await expect(fetchPositionContext(AFTER_E4_FEN, "black")).resolves.toEqual({
      status: "success",
      data: expectedContext(AFTER_E4_FEN, {
        trainerColor: "black",
        observedInGames: false,
        distinctGameCount: 0,
        totalGameCount: 0,
      }),
    });
  });

  it.each([
    insight(FEN, { observed_in_games: 1 }),
    insight(FEN, {
      experience: { distinct_game_count: -1, occurrence_count: 0, total_game_count: 3 },
    }),
    insight(FEN, {
      experience: { distinct_game_count: 2, occurrence_count: 0, total_game_count: 1.5 },
    }),
    insight(FEN, { experience: null }),
    insight(FEN, { trainer_color: "black" }),
    insight(FEN, { fen: "not a FEN" }),
    { fen: FEN, trainer_color: "white", observed_in_games: true },
  ])("rejects a malformed or mismatched insight response", async (body) => {
    const { result } = await resolveInsightResult(body);

    expect(result).toEqual({ status: "unexpected_failure" });
  });

  it.each([
    [422, "invalid_fen", "invalid_fen"],
    [503, "position_insight_unavailable", "position_context_unavailable"],
    [500, "unexpected_failure", "unexpected_failure"],
  ] as const)("maps the accepted typed HTTP failure %s/%s", async (status, code, mapped) => {
    const { result } = await resolveInsightResult({ code, message: "safe detail" }, status);

    expect(result).toEqual({ status: mapped });
  });

  it("does not trust an accepted error code on the wrong HTTP status", async () => {
    const { result } = await resolveInsightResult(
      { code: "position_insight_unavailable", message: "detail" },
      500,
    );

    expect(result).toEqual({ status: "unexpected_failure" });
  });

  it("maps an untyped error body to the safe unexpected failure", async () => {
    const { result } = await resolveInsightResult("gateway timeout", 502);

    expect(result).toEqual({ status: "unexpected_failure" });
  });

  it("rejects an empty FEN before making a request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchPositionContext("", "white")).resolves.toEqual({ status: "invalid_fen" });
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
