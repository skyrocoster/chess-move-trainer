import { afterEach, describe, expect, it, vi } from "vitest";

import {
  enqueueEvaluation,
  fetchEvaluation,
  fetchEvaluationStatus,
  validateAnalysisFen,
} from "./analysisApi";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const CANDIDATE = {
  rank: 1,
  score_kind: "cp",
  score_value: 34,
  wdl_wins: 420,
  wdl_draws: 300,
  wdl_losses: 280,
  pv_uci: ["e2e4", "e7e5", "g1f3"],
  depth: 20,
  seldepth: 24,
  nodes: 200000,
  engine_time_ms: 100,
};
const RESULT = {
  fen: FEN,
  profile_id: "mp09-balanced-nodes-v2-200000",
  candidates: [CANDIDATE],
  terminal_kind: null,
  completed_at: "2026-08-21T00:00:00+00:00",
  wall_time_ms: 100,
};
const STATUS = {
  state: "done",
  position: 0,
  attempts: 1,
  enqueued_at: "2026-08-21T00:00:00+00:00",
  started_at: "2026-08-21T00:00:00+00:00",
  completed_at: "2026-08-21T00:00:00+00:00",
  error_code: null,
};

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function observation(overrides: Record<string, unknown> = {}) {
  return {
    fen: FEN,
    eligibility: "eligible",
    result: RESULT,
    status: null,
    terminal: false,
    ...overrides,
  };
}

afterEach(() => vi.unstubAllGlobals());

describe("analysisApi", () => {
  it("strictly validates the canonical FEN boundary and size bound", () => {
    expect(validateAnalysisFen(FEN)).toBeNull();
    expect(validateAnalysisFen(` ${FEN}`)).toBe("invalid_fen");
    expect(validateAnalysisFen(FEN.replace(" - 0 1", "  - 0 1"))).toBe("invalid_fen");
    expect(validateAnalysisFen("x".repeat(129))).toBe("request_too_large");
  });

  it("loads an exact eligible observation without computation", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(observation()));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchEvaluation(FEN)).resolves.toEqual({
      status: "success",
      data: observation(),
    });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/evaluation?fen=${encodeURIComponent(FEN)}`,
      { signal: undefined },
    );
  });

  it("rejects malformed or extra response keys", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ ...observation(), extra: true })),
    );

    await expect(fetchEvaluation(FEN)).resolves.toEqual({ status: "unexpected_failure" });
  });

  it.each([
    [503, "evaluation_unavailable"],
    [422, "invalid_fen"],
    [409, "invalid_transition"],
    [500, "unexpected_failure"],
  ] as const)("maps typed HTTP failure %s/%s", async (status, code) => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({ code, message: "typed failure" }, status)),
    );

    await expect(fetchEvaluation(FEN)).resolves.toEqual({ status: code });
  });

  it("deliberately enqueues an action with the exact POST contract", async () => {
    const body = {
      fen: FEN,
      action: "analyze",
      outcome: "queued",
      eligibility: "missing",
      status: { ...STATUS, state: "queued", completed_at: null },
    };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(body, 202));
    vi.stubGlobal("fetch", fetchMock);

    await expect(enqueueEvaluation(FEN, "analyze")).resolves.toEqual({
      status: "success",
      data: body,
    });
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:5666/api/evaluation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen: FEN, action: "analyze" }),
      signal: undefined,
    });
  });

  it("rejects invalid actions and never sends invalid FEN requests", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(enqueueEvaluation(FEN, "compute" as never)).resolves.toEqual({
      status: "invalid_action",
    });
    await expect(fetchEvaluation(`${FEN} `)).resolves.toEqual({ status: "invalid_fen" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("observes queue completion through the separate status endpoint", async () => {
    const body = {
      fen: FEN,
      state: "done",
      completed_at: STATUS.completed_at,
      error_code: null,
    };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(body));
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchEvaluationStatus(FEN)).resolves.toEqual({ status: "success", data: body });
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:5666/api/evaluation/status?fen=${encodeURIComponent(FEN)}`,
      { signal: undefined },
    );
  });
});
