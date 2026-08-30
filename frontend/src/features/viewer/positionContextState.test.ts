import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type {
  PositionContextClient,
  PositionContextResponse,
  PositionContextResult,
} from "./positionContextApi";
import { usePositionContextState } from "./positionContextState";
import type { Fen } from "./chessPrimitives";

const FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const NEXT_FEN: Fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";
const BRANCH_FEN: Fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function context(fen: Fen, overallExists = true): PositionContextResponse {
  return {
    fen,
    overall_exists: overallExists,
    white_count: overallExists ? 2 : 0,
    black_count: overallExists ? 1 : 0,
    white_total: 3,
    black_total: 2,
  };
}

function success(fen: Fen): PositionContextResult {
  return { status: "success", data: context(fen) };
}

function Probe({ fen, client }: { fen: Fen | null; client: PositionContextClient }) {
  const state = usePositionContextState(fen, client);
  return createElement(
    "output",
    { "data-testid": "state" },
    JSON.stringify({
      fen: state.context?.fen ?? null,
      loading: state.loading,
      error: state.error,
    }),
  );
}

afterEach(() => cleanup());

describe("usePositionContextState", () => {
  it("does not request the empty Viewer and keeps its reset state", async () => {
    const client = vi.fn<PositionContextClient>();
    render(createElement(Probe, { fen: null, client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({ fen: null, loading: false, error: null }),
      ),
    );
    expect(client).not.toHaveBeenCalled();
  });

  it("loads the displayed FEN and follows a temporary branch FEN", async () => {
    const client = vi.fn<PositionContextClient>(async (fen) => success(fen));
    const view = render(createElement(Probe, { fen: FEN, client }));

    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent(FEN));
    expect(client).toHaveBeenCalledWith(FEN, expect.any(AbortSignal));

    view.rerender(createElement(Probe, { fen: BRANCH_FEN, client }));
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent(BRANCH_FEN));
    expect(client).toHaveBeenLastCalledWith(BRANCH_FEN, expect.any(AbortSignal));
  });

  it("keys requests by the full displayed FEN, including counter fields", async () => {
    const client = vi.fn<PositionContextClient>(async (fen) => success(fen));
    const view = render(createElement(Probe, { fen: FEN, client }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(1));

    const counterVariant = `${FEN.slice(0, -3)}17 42`;
    view.rerender(createElement(Probe, { fen: counterVariant, client }));

    await waitFor(() => expect(client).toHaveBeenCalledTimes(2));
    expect(client).toHaveBeenLastCalledWith(counterVariant, expect.any(AbortSignal));
  });

  it("discards a stale response and aborts the replaced request", async () => {
    let resolveFirst: ((result: PositionContextResult) => void) | undefined;
    let resolveSecond: ((result: PositionContextResult) => void) | undefined;
    const client = vi.fn((fen: Fen, signal?: AbortSignal) => {
      return new Promise<PositionContextResult>((resolve) => {
        if (fen === FEN) {
          resolveFirst = resolve;
        } else {
          resolveSecond = resolve;
        }
        void signal;
      });
    });
    const view = render(createElement(Probe, { fen: FEN, client }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(1));

    const firstSignal = client.mock.calls[0][1];
    view.rerender(createElement(Probe, { fen: NEXT_FEN, client }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(2));
    expect(firstSignal).toBeDefined();
    expect(firstSignal?.aborted).toBe(true);

    await act(async () => {
      resolveFirst?.(success(FEN));
    });
    expect(screen.getByTestId("state")).not.toHaveTextContent(FEN);

    await act(async () => {
      resolveSecond?.(success(NEXT_FEN));
    });
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent(NEXT_FEN));
  });

  it("exposes typed failures safely and clears them when reset", async () => {
    const client = vi
      .fn<PositionContextClient>()
      .mockResolvedValueOnce({ status: "position_context_unavailable" })
      .mockResolvedValueOnce(success(FEN));
    const view = render(createElement(Probe, { fen: FEN, client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({ fen: null, loading: false, error: "position_context_unavailable" }),
      ),
    );

    view.rerender(createElement(Probe, { fen: null, client }));
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({ fen: null, loading: false, error: null }),
      ),
    );
    expect(client).toHaveBeenCalledTimes(1);
  });
});
