import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { createTestQueryClient, QueryClientTestProvider } from "../../test-utils/QueryClientTestProvider";
import type {
  AnalysisClient,
  AnalysisObservation,
  AnalysisOperationResult,
  AnalysisResult,
} from "./analysisApi";
import { defaultAnalysisClient } from "./analysisApi";
import {
  ANALYSIS_OBSERVATION_GC_TIME,
  AnalysisQueryError,
  analysisObservationQueryKey,
  MAX_ANALYSIS_POLL_ATTEMPTS,
  useAnalysisQuery,
} from "./analysisQuery";
import { useAnalysisState } from "./analysisState";
import { positionKeyFromFen, type Fen } from "../chess/chessPrimitives";

const FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN: Fen =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const NEXT_FEN: Fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1";

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

function clientFor(observe: AnalysisClient["observe"]): AnalysisClient {
  return { observe, request: vi.fn() };
}

function QueryProbe({
  fen,
  client,
  pollIntervalMs = 5,
}: {
  fen: Fen;
  client: AnalysisClient;
  pollIntervalMs?: number;
}) {
  const query = useAnalysisQuery(fen, client, pollIntervalMs);
  return createElement(
    "output",
    { "data-testid": "query-state" },
    JSON.stringify({
      state: query.data?.state ?? null,
      result: query.data?.result ?? null,
      error: query.error instanceof AnalysisQueryError ? query.error.status : null,
      limit: query.pollLimitReached,
    }),
  );
}

function StateProbe({ fen, pollIntervalMs = 5 }: { fen: Fen; pollIntervalMs?: number }) {
  const state = useAnalysisState(fen, undefined, pollIntervalMs);
  return createElement(
    "div",
    null,
    createElement(
      "output",
      { "data-testid": "analysis-state" },
      JSON.stringify({
        state: state.observation?.state ?? null,
        result: state.observation?.result ?? null,
        loading: state.loading,
        error: state.error,
        requestError: state.requestError,
      }),
    ),
    createElement("button", { type: "button", onClick: state.retryObservation }, "retry observation"),
    createElement(
      "button",
      { type: "button", onClick: () => void state.requestAnalysis() },
      "analyze",
    ),
  );
}

function readState(testId = "query-state") {
  return JSON.parse(screen.getByTestId(testId).textContent ?? "{}");
}

async function flushQuery() {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(0);
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
  });
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe("analysisQuery", () => {
  it("deduplicates observers under the canonical position key and sends the full FEN", async () => {
    const observe = vi.fn<AnalysisClient["observe"]>().mockResolvedValue(
      success(observation(FEN, "ready", RESULT)),
    );
    const client = clientFor(observe);
    const queryClient = createTestQueryClient();

    render(
      createElement(
        QueryClientTestProvider,
        { client: queryClient },
        createElement(QueryProbe, { fen: FEN, client }),
        createElement(QueryProbe, { fen: COUNTER_VARIANT_FEN, client }),
      ),
    );

    await waitFor(() => expect(observe).toHaveBeenCalledOnce());
    expect(observe).toHaveBeenCalledWith(FEN, expect.any(AbortSignal));
    expect(queryClient.getQueryCache().findAll()).toHaveLength(1);
    const query = queryClient.getQueryCache().find({ queryKey: analysisObservationQueryKey(FEN) });
    expect(query?.options.staleTime).toBe(0);
    expect(query?.options.gcTime).toBe(ANALYSIS_OBSERVATION_GC_TIME);
  });

  it("polls queued and running observations, then stops for ready and not-requested", async () => {
    vi.useFakeTimers();
    const observe = vi
      .fn<AnalysisClient["observe"]>()
      .mockResolvedValueOnce(success(observation(FEN, "queued")))
      .mockResolvedValueOnce(success(observation(FEN, "running")))
      .mockResolvedValueOnce(success(observation(FEN, "ready", RESULT)));
    const client = clientFor(observe);

    render(
      createElement(
        QueryClientTestProvider,
        { client: createTestQueryClient() },
        createElement(QueryProbe, { fen: FEN, client, pollIntervalMs: 5 }),
      ),
    );
    await flushQuery();
    expect(readState().state).toBe("queued");

    await act(async () => {
      await vi.advanceTimersByTimeAsync(20);
    });
    await flushQuery();
    expect(readState().state).toBe("ready");
    expect(observe).toHaveBeenCalledTimes(3);

    const notRequested = vi.fn<AnalysisClient["observe"]>().mockResolvedValue(
      success(observation(NEXT_FEN, "not_requested")),
    );
    const view = render(
      createElement(
        QueryClientTestProvider,
        { client: createTestQueryClient() },
        createElement(QueryProbe, { fen: NEXT_FEN, client: clientFor(notRequested) }),
      ),
    );
    await flushQuery();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(50);
    });
    expect(notRequested).toHaveBeenCalledOnce();
    view.unmount();
  });

  it("caps active polling at sixty poll attempts", async () => {
    vi.useFakeTimers();
    const observe = vi.fn<AnalysisClient["observe"]>().mockResolvedValue(
      success(observation(FEN, "queued")),
    );
    render(
      createElement(
        QueryClientTestProvider,
        { client: createTestQueryClient() },
        createElement(QueryProbe, { fen: FEN, client: clientFor(observe), pollIntervalMs: 1 }),
      ),
    );
    await flushQuery();
    for (let attempt = 0; attempt < MAX_ANALYSIS_POLL_ATTEMPTS; attempt += 1) {
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1);
      });
    }
    expect(observe).toHaveBeenCalledTimes(MAX_ANALYSIS_POLL_ATTEMPTS + 1);
    expect(readState().limit).toBe(true);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(100);
    });
    expect(observe).toHaveBeenCalledTimes(MAX_ANALYSIS_POLL_ATTEMPTS + 1);
  });

  it("does not cache failures as successful observation data", async () => {
    const observe = vi.fn<AnalysisClient["observe"]>().mockResolvedValue({
      status: "analysis_unavailable",
    });
    const queryClient = createTestQueryClient();
    render(
      createElement(
        QueryClientTestProvider,
        { client: queryClient },
        createElement(QueryProbe, { fen: FEN, client: clientFor(observe) }),
      ),
    );

    await waitFor(() => expect(readState().error).toBe("analysis_unavailable"));
    expect(queryClient.getQueryData(analysisObservationQueryKey(FEN))).toBeUndefined();
  });
});

describe("default analysis state", () => {
  it("retains results during active polling, invalidates only real transitions, and retries", async () => {
    vi.useFakeTimers();
    const observe = vi
      .spyOn(defaultAnalysisClient, "observe")
      .mockResolvedValueOnce(success(observation(FEN, "ready", RESULT)))
      .mockResolvedValueOnce(success(observation(FEN, "running")))
      .mockResolvedValueOnce(success(observation(FEN, "running")))
      .mockResolvedValueOnce(success(observation(FEN, "ready", { ...RESULT, lines: [] })));
    const queryClient = createTestQueryClient();
    const invalidate = vi.spyOn(queryClient, "invalidateQueries");
    render(
      createElement(
        QueryClientTestProvider,
        { client: queryClient },
        createElement(StateProbe, { fen: FEN, pollIntervalMs: 5 }),
      ),
    );

    await flushQuery();
    expect(readState("analysis-state").state).toBe("ready");
    await act(async () => {
      await screen.getByRole("button", { name: "retry observation" }).click();
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(5);
    });
    expect(readState("analysis-state").result.lines).toHaveLength(1);
    expect(invalidate).toHaveBeenCalledTimes(1);

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5);
    });
    expect(invalidate).toHaveBeenCalledTimes(1);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(5);
    });
    expect(invalidate).toHaveBeenCalledTimes(2);
  });

  it("invalidates analysis and insight after a successful deliberate request", async () => {
    const observe = vi
      .spyOn(defaultAnalysisClient, "observe")
      .mockResolvedValue(success(observation(FEN, "not_requested")));
    const request = vi
      .spyOn(defaultAnalysisClient, "request")
      .mockResolvedValue(success(observation(FEN, "queued")));
    const queryClient = createTestQueryClient();
    const invalidate = vi.spyOn(queryClient, "invalidateQueries");
    render(
      createElement(
        QueryClientTestProvider,
        { client: queryClient },
        createElement(StateProbe, { fen: FEN }),
      ),
    );
    await waitFor(() => expect(observe).toHaveBeenCalledOnce());
    await act(async () => {
      screen.getByRole("button", { name: "analyze" }).click();
    });

    await waitFor(() => expect(request).toHaveBeenCalledOnce());
    expect(invalidate).toHaveBeenCalledTimes(2);
    expect(invalidate.mock.calls.map(([filters]) => filters.queryKey)).toEqual([
      analysisObservationQueryKey(FEN),
      ["positionInsight", positionKeyFromFen(FEN)],
    ]);
  });

  it("aborts a replaced observation and ignores its late result", async () => {
    let resolveFirst!: (result: AnalysisOperationResult<AnalysisObservation>) => void;
    const observe = vi.spyOn(defaultAnalysisClient, "observe").mockImplementation((fen) => {
      if (fen === FEN) {
        return new Promise((resolve) => {
          resolveFirst = resolve;
        });
      }
      return Promise.resolve(success(observation(fen, "ready", RESULT)));
    });
    const view = render(
      createElement(
        QueryClientTestProvider,
        { client: createTestQueryClient() },
        createElement(StateProbe, { fen: FEN }),
      ),
    );
    await waitFor(() => expect(observe).toHaveBeenCalledOnce());
    const firstSignal = observe.mock.calls[0]?.[1];
    view.rerender(
      createElement(
        QueryClientTestProvider,
        { client: createTestQueryClient() },
        createElement(StateProbe, { fen: NEXT_FEN }),
      ),
    );
    await waitFor(() => expect(observe).toHaveBeenCalledTimes(2));
    expect(firstSignal?.aborted).toBe(true);
    await act(async () => {
      resolveFirst(success(observation(FEN, "ready", RESULT)));
    });
    expect(readState("analysis-state").state).toBe("ready");
  });
});
