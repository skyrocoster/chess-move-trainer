import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { AnalysisClient, AnalysisResult, EvaluationObservation } from "./analysisApi";
import { useAnalysisState } from "./analysisState";
import type { Fen } from "./chessPrimitives";

const FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";

function observation(fen: Fen): EvaluationObservation {
  return {
    fen,
    eligibility: "eligible",
    result: null,
    status: null,
    terminal: false,
  };
}

function Probe({ fen, client }: { fen: Fen; client: AnalysisClient }) {
  const state = useAnalysisState(fen, client, 0);
  return createElement(
    "output",
    { "data-testid": "observed-fen" },
    state.observation?.fen ?? "none",
  );
}

afterEach(() => cleanup());

describe("useAnalysisState", () => {
  it("keeps the current observation while only FEN counters change", async () => {
    let observeCalls = 0;
    let resolveSecond: ((value: AnalysisResult<EvaluationObservation>) => void) | undefined;
    const observe = vi.fn((requestedFen: Fen) => {
      observeCalls += 1;
      if (observeCalls === 1) {
        return Promise.resolve({ status: "success", data: observation(requestedFen) } as const);
      }
      return new Promise<AnalysisResult<EvaluationObservation>>((resolve) => {
        resolveSecond = resolve;
      });
    });
    const client: AnalysisClient = {
      observe,
      enqueue: async () => ({ status: "invalid_action" }),
      status: async () => ({ status: "unexpected_failure" }),
    };

    const view = render(createElement(Probe, { fen: FEN, client }));
    await waitFor(() => expect(screen.getByTestId("observed-fen")).toHaveTextContent(FEN));

    view.rerender(createElement(Probe, { fen: COUNTER_VARIANT_FEN, client }));
    await waitFor(() => expect(observe).toHaveBeenCalledTimes(2));
    expect(screen.getByTestId("observed-fen")).toHaveTextContent(FEN);

    expect(resolveSecond).toBeDefined();
    await act(async () => {
      resolveSecond?.({
        status: "success",
        data: observation(COUNTER_VARIANT_FEN),
      });
    });
    await waitFor(() =>
      expect(screen.getByTestId("observed-fen")).toHaveTextContent(COUNTER_VARIANT_FEN),
    );
  });
});
