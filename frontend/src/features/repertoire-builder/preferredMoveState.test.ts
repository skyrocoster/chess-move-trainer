import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type {
  PreferredMoveReader,
  PreferredMoveResponse,
  PreferredMoveResult,
} from "./preferredMoveApi";
import { usePreferredMoveState } from "./preferredMoveState";
import type { Fen } from "../viewer/chessPrimitives";

const FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const NEXT_FEN: Fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function response(fen: Fen): PreferredMoveResponse {
  return {
    fen,
    state: "assigned",
    move: { uci: "e2e4", san: "e4" },
    effective_at: fen === FEN ? "2026-01-01T00:00:00.000000Z" : "2026-01-02T00:00:00.000000Z",
  };
}

function success(fen: Fen): PreferredMoveResult {
  return { status: "success", data: response(fen) };
}

function Probe({
  fen,
  client,
  refreshKey = 0,
}: {
  fen: Fen | null;
  client: PreferredMoveReader;
  refreshKey?: number;
}) {
  const state = usePreferredMoveState(fen, client, refreshKey);
  return createElement(
    "output",
    { "data-testid": "state" },
    JSON.stringify({
      fen: state.preferredMove?.fen ?? null,
      effective_at: state.preferredMove?.effective_at ?? null,
      loading: state.loading,
      error: state.error,
    }),
  );
}

afterEach(() => cleanup());

describe("usePreferredMoveState", () => {
  it("does not request a null position and keeps its reset state", async () => {
    const client = vi.fn<PreferredMoveReader>();
    render(createElement(Probe, { fen: null, client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({ fen: null, effective_at: null, loading: false, error: null }),
      ),
    );
    expect(client).not.toHaveBeenCalled();
  });

  it("loads the full displayed FEN and passes an abort signal", async () => {
    const client = vi.fn<PreferredMoveReader>(async (fen) => success(fen));
    render(createElement(Probe, { fen: FEN, client }));

    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent(FEN));
    expect(client).toHaveBeenCalledWith(FEN, { signal: expect.any(AbortSignal) });
  });

  it("discards a stale response and aborts the replaced request", async () => {
    let resolveFirst: ((result: PreferredMoveResult) => void) | undefined;
    let resolveSecond: ((result: PreferredMoveResult) => void) | undefined;
    const client = vi.fn((fen: Fen, options?: { signal?: AbortSignal }) => {
      void options;
      return new Promise<PreferredMoveResult>((resolve) => {
        if (fen === FEN) {
          resolveFirst = resolve;
        } else {
          resolveSecond = resolve;
        }
      });
    });
    const view = render(createElement(Probe, { fen: FEN, client }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(1));

    const firstSignal = client.mock.calls[0]?.[1]?.signal;
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

  it("exposes typed failures and clears them when the position resets", async () => {
    const client = vi
      .fn<PreferredMoveReader>()
      .mockResolvedValueOnce({ status: "position_not_found" })
      .mockResolvedValueOnce(success(FEN));
    const view = render(createElement(Probe, { fen: FEN, client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: null,
          effective_at: null,
          loading: false,
          error: "position_not_found",
        }),
      ),
    );

    view.rerender(createElement(Probe, { fen: null, client }));
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({ fen: null, effective_at: null, loading: false, error: null }),
      ),
    );
    expect(client).toHaveBeenCalledTimes(1);
  });

  it("retains the effective date through an initial read and position reload", async () => {
    const client = vi.fn<PreferredMoveReader>(async (fen) => success(fen));
    const view = render(createElement(Probe, { fen: FEN, client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: FEN,
          effective_at: "2026-01-01T00:00:00.000000Z",
          loading: false,
          error: null,
        }),
      ),
    );

    view.rerender(createElement(Probe, { fen: NEXT_FEN, client }));
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: NEXT_FEN,
          effective_at: "2026-01-02T00:00:00.000000Z",
          loading: false,
          error: null,
        }),
      ),
    );
  });

  it("retains the confirmed response while a same-position refresh is pending", async () => {
    let resolveRefresh!: (result: PreferredMoveResult) => void;
    const client = vi.fn<PreferredMoveReader>();
    client.mockResolvedValueOnce(success(FEN));
    client.mockImplementationOnce(
      () => new Promise<PreferredMoveResult>((resolve) => (resolveRefresh = resolve)),
    );
    const view = render(createElement(Probe, { fen: FEN, client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: FEN,
          effective_at: "2026-01-01T00:00:00.000000Z",
          loading: false,
          error: null,
        }),
      ),
    );

    view.rerender(createElement(Probe, { fen: FEN, client, refreshKey: 1 }));
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: FEN,
          effective_at: "2026-01-01T00:00:00.000000Z",
          loading: true,
          error: null,
        }),
      ),
    );

    resolveRefresh(success(FEN));
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: FEN,
          effective_at: "2026-01-01T00:00:00.000000Z",
          loading: false,
          error: null,
        }),
      ),
    );
  });

  it("retains the confirmed response when a same-position refresh fails", async () => {
    const client = vi
      .fn<PreferredMoveReader>()
      .mockResolvedValueOnce(success(FEN))
      .mockResolvedValueOnce({ status: "preferred_move_unavailable" });
    const view = render(createElement(Probe, { fen: FEN, client }));

    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent(FEN));
    view.rerender(createElement(Probe, { fen: FEN, client, refreshKey: 1 }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: FEN,
          effective_at: "2026-01-01T00:00:00.000000Z",
          loading: false,
          error: "preferred_move_unavailable",
        }),
      ),
    );
  });
});
