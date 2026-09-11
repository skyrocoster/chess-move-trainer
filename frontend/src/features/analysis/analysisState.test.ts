import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type {
  AnalysisClient,
  AnalysisObservation,
  AnalysisOperationResult,
  AnalysisResult,
} from "./analysisApi";
import { useAnalysisState } from "./analysisState";
import type { Fen } from "../chess/chessPrimitives";

const FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN: Fen =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const DISTINCT_POSITION_FEN: Fen =
  "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";

const RESULT: AnalysisResult = {
  lines: [
    {
      rank: 1,
      score_kind: "cp",
      score_value: 34,
      wdl_wins: 420,
      wdl_draws: 300,
      wdl_losses: 280,
      pv_uci: ["e2e4"],
      depth: 20,
    },
  ],
  terminal_kind: null,
};

function observation(
  fen: Fen,
  state: AnalysisObservation["state"],
  result: AnalysisResult | null = null,
): AnalysisObservation {
  return { fen, state, result };
}

function success(data: AnalysisObservation): AnalysisOperationResult<AnalysisObservation> {
  return { status: "success", data };
}

function Probe({ fen, client, pollIntervalMs = 0 }: {
  fen: Fen;
  client: AnalysisClient;
  pollIntervalMs?: number;
}) {
  const state = useAnalysisState(fen, client, pollIntervalMs);
  return createElement(
    "div",
    null,
    createElement(
      "output",
      { "data-testid": "analysis-state" },
      JSON.stringify({
        fen: state.observation?.fen ?? "none",
        state: state.observation?.state ?? "none",
        result: state.observation?.result ?? null,
        error: state.error,
        requestError: state.requestError,
        requestPending: state.requestPending,
      }),
    ),
    createElement("button", { onClick: () => void state.requestAnalysis() }, "request"),
  );
}

function readProbe() {
  return JSON.parse(screen.getByTestId("analysis-state").textContent ?? "{}");
}

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

describe("useAnalysisState", () => {
  it("observes automatically without requesting analysis", async () => {
    const observe = vi.fn(async (fen: Fen) => success(observation(fen, "not_requested")));
    const request = vi.fn<AnalysisClient["request"]>();
    const client: AnalysisClient = { observe, request };

    render(createElement(Probe, { fen: FEN, client }));
    await waitFor(() => expect(readProbe().state).toBe("not_requested"));

    expect(observe).toHaveBeenCalledWith(FEN, expect.any(AbortSignal));
    expect(request).not.toHaveBeenCalled();
  });

  it("polls queued and running work through observation until ready", async () => {
    vi.useFakeTimers();
    const observe = vi
      .fn<AnalysisClient["observe"]>()
      .mockResolvedValueOnce(success(observation(FEN, "queued")))
      .mockResolvedValueOnce(success(observation(FEN, "running")))
      .mockResolvedValueOnce(success(observation(FEN, "ready", RESULT)));
    const request = vi.fn<AnalysisClient["request"]>();

    render(createElement(Probe, { fen: FEN, client: { observe, request }, pollIntervalMs: 5 }));
    await act(async () => undefined);
    expect(readProbe().state).toBe("queued");

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5);
    });
    expect(readProbe().state).toBe("running");

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5);
    });
    expect(readProbe().state).toBe("ready");
    expect(observe).toHaveBeenCalledTimes(3);
    expect(request).not.toHaveBeenCalled();
  });

  it("retains a current result while active work runs and replaces it when ready", async () => {
    vi.useFakeTimers();
    const updatedResult = { ...RESULT, lines: [{ ...RESULT.lines[0]!, score_value: 81 }] };
    const observe = vi
      .fn<AnalysisClient["observe"]>()
      .mockResolvedValueOnce(success(observation(FEN, "queued", RESULT)))
      .mockResolvedValueOnce(success(observation(FEN, "running")))
      .mockResolvedValueOnce(success(observation(FEN, "ready", updatedResult)));
    const request = vi.fn<AnalysisClient["request"]>();

    render(createElement(Probe, { fen: FEN, client: { observe, request }, pollIntervalMs: 5 }));
    await act(async () => undefined);
    expect(readProbe().result.lines[0].score_value).toBe(34);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5);
    });
    expect(readProbe().state).toBe("running");
    expect(readProbe().result.lines[0].score_value).toBe(34);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5);
    });
    expect(readProbe().result.lines[0].score_value).toBe(81);
  });

  it("only requests after the deliberate intent and keeps request failures out of lifecycle state", async () => {
    const observe = vi.fn(async (fen: Fen) => success(observation(fen, "not_requested")));
    const request = vi.fn<AnalysisClient["request"]>().mockResolvedValue({
      status: "analysis_unavailable",
    });
    const client: AnalysisClient = { observe, request };

    render(createElement(Probe, { fen: FEN, client }));
    await waitFor(() => expect(readProbe().state).toBe("not_requested"));
    fireEvent.click(screen.getByRole("button", { name: "request" }));

    await waitFor(() => expect(request).toHaveBeenCalledTimes(1));
    expect(request).toHaveBeenCalledWith(FEN, expect.any(AbortSignal));
    await waitFor(() => expect(readProbe().requestError).toBe("The analysis service is unavailable."));
    expect(readProbe().state).toBe("not_requested");
  });

  it("ignores a stale observation after moving to a different position", async () => {
    let resolveFirst: ((value: AnalysisOperationResult<AnalysisObservation>) => void) | undefined;
    const observe = vi.fn((fen: Fen) => {
      if (fen === FEN) {
        return new Promise<AnalysisOperationResult<AnalysisObservation>>((resolve) => {
          resolveFirst = resolve;
        });
      }
      return Promise.resolve(success(observation(fen, "ready", RESULT)));
    });
    const request = vi.fn<AnalysisClient["request"]>();
    const view = render(createElement(Probe, { fen: FEN, client: { observe, request } }));

    view.rerender(createElement(Probe, { fen: DISTINCT_POSITION_FEN, client: { observe, request } }));
    await waitFor(() => expect(readProbe().fen).toBe(DISTINCT_POSITION_FEN));
    await act(async () => {
      resolveFirst?.(success(observation(FEN, "ready", RESULT)));
    });
    expect(readProbe().fen).toBe(DISTINCT_POSITION_FEN);
  });

  it("keeps a counter-insensitive observation while the latest counter variant loads", async () => {
    let resolveSecond: ((value: AnalysisOperationResult<AnalysisObservation>) => void) | undefined;
    let observeCalls = 0;
    const observe = vi.fn((requestedFen: Fen) => {
      observeCalls += 1;
      if (observeCalls === 1) {
        return Promise.resolve(success(observation(requestedFen, "ready", RESULT)));
      }
      return new Promise<AnalysisOperationResult<AnalysisObservation>>((resolve) => {
        resolveSecond = resolve;
      });
    });
    const request = vi.fn<AnalysisClient["request"]>();
    const view = render(createElement(Probe, { fen: FEN, client: { observe, request } }));
    await waitFor(() => expect(readProbe().fen).toBe(FEN));

    view.rerender(createElement(Probe, { fen: COUNTER_VARIANT_FEN, client: { observe, request } }));
    await waitFor(() => expect(observe).toHaveBeenCalledTimes(2));
    expect(readProbe().fen).toBe(FEN);

    await act(async () => {
      resolveSecond?.(success(observation(COUNTER_VARIANT_FEN, "ready", RESULT)));
    });
    await waitFor(() => expect(readProbe().fen).toBe(COUNTER_VARIANT_FEN));
  });
});
