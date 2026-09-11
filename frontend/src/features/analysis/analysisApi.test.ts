import { afterEach, describe, expect, it, vi } from "vitest";

import { getAnalysis, requestAnalysis as generatedRequestAnalysis } from "../../api/client";
import {
  fetchAnalysis,
  positionKeyFromFen,
  requestAnalysis,
  validateAnalysisFen,
} from "./analysisApi";

vi.mock("../../api/client", () => ({
  getAnalysis: vi.fn(),
  requestAnalysis: vi.fn(),
}));

const getAnalysisMock = vi.mocked(getAnalysis);
const generatedRequestAnalysisMock = vi.mocked(generatedRequestAnalysis);

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const DISTINCT_POSITION_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";

const LINE = {
  rank: 1,
  score_kind: "cp",
  score_value: 34,
  wdl_wins: 420,
  wdl_draws: 300,
  wdl_losses: 280,
  pv_uci: ["e2e4", "e7e5", "g1f3"],
  depth: 20,
};

const RESULT = {
  configuration_version: 1,
  engine_name: "stockfish",
  engine_version: "test",
  lines: [LINE],
  quality: "tool",
  settings: { depth: 20 },
  terminal_kind: null,
};

function apiResult(data: unknown, status = 200) {
  return {
    data,
    error: undefined,
    response: { status },
  } as Awaited<ReturnType<typeof getAnalysis>>;
}

function apiError(code: string, status: number) {
  return {
    data: undefined,
    error: { code, message: "typed failure" },
    response: { status },
  } as Awaited<ReturnType<typeof getAnalysis>>;
}

function observation(overrides: Record<string, unknown> = {}) {
  return {
    fen: FEN,
    state: "ready",
    result: RESULT,
    ...overrides,
  };
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("analysisApi", () => {
  it("derives PositionKey from identity fields only", () => {
    expect(positionKeyFromFen(FEN)).toBe(positionKeyFromFen(COUNTER_VARIANT_FEN));
    expect(positionKeyFromFen(FEN)).not.toBe(positionKeyFromFen(DISTINCT_POSITION_FEN));
  });

  it("strictly validates the canonical FEN boundary and size bound", () => {
    expect(validateAnalysisFen(FEN)).toBeNull();
    expect(validateAnalysisFen(` ${FEN}`)).toBe("invalid_fen");
    expect(validateAnalysisFen(FEN.replace(" - 0 1", "  - 0 1"))).toBe("invalid_fen");
    expect(validateAnalysisFen("x".repeat(129))).toBe("invalid_fen");
  });

  it("observes through the generated clean GET and maps only clean result fields", async () => {
    getAnalysisMock.mockResolvedValue(
      apiResult({
        ...observation(),
        extra: "tolerated",
        result: { ...RESULT, extra: "tolerated" },
      }),
    );

    await expect(fetchAnalysis(FEN)).resolves.toEqual({
      status: "success",
      data: {
        fen: FEN,
        state: "ready",
        result: { lines: [LINE], terminal_kind: null },
      },
    });
    expect(getAnalysisMock).toHaveBeenCalledWith({
      query: { fen: FEN },
      signal: undefined,
    });
  });

  it("accepts a counter-only observation identity variant without a result FEN", async () => {
    getAnalysisMock.mockResolvedValue(
      apiResult({
        ...observation({ fen: COUNTER_VARIANT_FEN }),
        result: RESULT,
      }),
    );

    await expect(fetchAnalysis(FEN)).resolves.toEqual({
      status: "success",
      data: {
        fen: COUNTER_VARIANT_FEN,
        state: "ready",
        result: { lines: [LINE], terminal_kind: null },
      },
    });
  });

  it("rejects malformed or different-position observations", async () => {
    getAnalysisMock.mockResolvedValue(apiResult({ ...observation(), fen: DISTINCT_POSITION_FEN }));

    await expect(fetchAnalysis(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it.each([
    [503, "analysis_unavailable"],
    [422, "invalid_fen"],
    [500, "unexpected_failure"],
  ] as const)("maps typed clean HTTP failure %s/%s", async (status, code) => {
    getAnalysisMock.mockResolvedValue(apiError(code, status));

    await expect(fetchAnalysis(FEN)).resolves.toEqual({ status: code });
  });

  it("deliberately requests Tool analysis through the generated clean POST", async () => {
    generatedRequestAnalysisMock.mockResolvedValue(
      apiResult(observation({ state: "queued" }), 202),
    );

    await expect(requestAnalysis(FEN)).resolves.toEqual({
      status: "success",
      data: {
        fen: FEN,
        state: "queued",
        result: { lines: [LINE], terminal_kind: null },
      },
    });
    expect(generatedRequestAnalysisMock).toHaveBeenCalledWith({
      body: { fen: FEN, quality: "tool" },
      signal: undefined,
    });
  });

  it("does not call generated operations for an invalid FEN", async () => {
    await expect(requestAnalysis(`${FEN} `)).resolves.toEqual({ status: "invalid_fen" });
    await expect(fetchAnalysis(`${FEN} `)).resolves.toEqual({ status: "invalid_fen" });
    expect(getAnalysisMock).not.toHaveBeenCalled();
    expect(generatedRequestAnalysisMock).not.toHaveBeenCalled();
  });
});
