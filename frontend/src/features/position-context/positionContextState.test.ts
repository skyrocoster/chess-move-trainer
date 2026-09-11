import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type {
  PositionContextClient,
  PositionContextResponse,
  PositionContextResult,
} from "./positionContextApi";
import { usePositionContextState } from "./positionContextState";
import type { ChessSide, Fen } from "../chess/chessPrimitives";

const FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const NEXT_FEN: Fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";
const BRANCH_FEN: Fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function context(fen: Fen, observedInGames = true): PositionContextResponse {
  return {
    fen,
    trainerColor: "white",
    observedInGames,
    distinctGameCount: observedInGames ? 2 : 0,
    totalGameCount: 3,
  };
}

function success(fen: Fen, trainerColor: ChessSide = "white"): PositionContextResult {
  return { status: "success", data: context(fen) };
}

function Probe({
  fen,
  trainerColor = "white",
  client,
}: {
  fen: Fen | null;
  trainerColor: ChessSide;
  client: PositionContextClient;
}) {
  const state = usePositionContextState(fen, trainerColor, client);
  return createElement(
    "output",
    { "data-testid": "state" },
    JSON.stringify({
      fen: state.context?.fen ?? null,
      observed: state.context?.observedInGames ?? null,
      loading: state.loading,
      error: state.error,
    }),
  );
}

afterEach(() => cleanup());

describe("usePositionContextState", () => {
  it("does not request an empty position and keeps its reset state", async () => {
    const client = vi.fn<PositionContextClient>();
    render(createElement(Probe, { fen: null, trainerColor: "white", client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({ fen: null, observed: null, loading: false, error: null }),
      ),
    );
    expect(client).not.toHaveBeenCalled();
  });

  it("loads the displayed FEN with the requested trainer color and follows a branch FEN", async () => {
    const client = vi.fn<PositionContextClient>(async (fen, trainerColor) =>
      success(fen, trainerColor),
    );
    const view = render(createElement(Probe, { fen: FEN, trainerColor: "white", client }));

    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent(FEN));
    expect(client).toHaveBeenCalledWith(FEN, "white", expect.any(AbortSignal));

    view.rerender(createElement(Probe, { fen: BRANCH_FEN, trainerColor: "white", client }));
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent(BRANCH_FEN));
    expect(client).toHaveBeenLastCalledWith(BRANCH_FEN, "white", expect.any(AbortSignal));
  });

  it("keys requests by the full displayed FEN, including counter fields", async () => {
    const client = vi.fn<PositionContextClient>(async (fen, trainerColor) =>
      success(fen, trainerColor),
    );
    const view = render(createElement(Probe, { fen: FEN, trainerColor: "white", client }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(1));

    const counterVariant = `${FEN.slice(0, -3)}17 42`;
    view.rerender(createElement(Probe, { fen: counterVariant, trainerColor: "white", client }));

    await waitFor(() => expect(client).toHaveBeenCalledTimes(2));
    expect(client).toHaveBeenLastCalledWith(counterVariant, "white", expect.any(AbortSignal));
  });

  it("refetches for the new trainer color and abandons the previous request", async () => {
    const client = vi.fn<PositionContextClient>(async (fen, trainerColor) =>
      success(fen, trainerColor),
    );
    const view = render(createElement(Probe, { fen: FEN, trainerColor: "white", client }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(1));

    const firstSignal = client.mock.calls[0][2];
    view.rerender(createElement(Probe, { fen: FEN, trainerColor: "black", client }));

    await waitFor(() => expect(client).toHaveBeenCalledTimes(2));
    expect(client).toHaveBeenLastCalledWith(FEN, "black", expect.any(AbortSignal));
    expect(firstSignal?.aborted).toBe(true);
  });

  it("discards a stale response and aborts the replaced request", async () => {
    let resolveFirst: ((result: PositionContextResult) => void) | undefined;
    let resolveSecond: ((result: PositionContextResult) => void) | undefined;
    const client = vi.fn((fen: Fen, trainerColor: ChessSide, signal?: AbortSignal) => {
      return new Promise<PositionContextResult>((resolve) => {
        if (fen === FEN) {
          resolveFirst = resolve;
        } else {
          resolveSecond = resolve;
        }
        void trainerColor;
        void signal;
      });
    });
    const view = render(createElement(Probe, { fen: FEN, trainerColor: "white", client }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(1));

    const firstSignal = client.mock.calls[0][2];
    view.rerender(createElement(Probe, { fen: NEXT_FEN, trainerColor: "white", client }));
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
    const view = render(createElement(Probe, { fen: FEN, trainerColor: "white", client }));

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({
          fen: null,
          observed: null,
          loading: false,
          error: "position_context_unavailable",
        }),
      ),
    );

    view.rerender(createElement(Probe, { fen: null, trainerColor: "white", client }));
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent(
        JSON.stringify({ fen: null, observed: null, loading: false, error: null }),
      ),
    );
    expect(client).toHaveBeenCalledTimes(1);
  });
});
