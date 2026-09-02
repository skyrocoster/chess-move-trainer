import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type {
  MoveResponseDistributionClient,
  MoveResponseDistributionResponse,
  MoveResponseDistributionResult,
} from "./moveResponseDistributionApi";
import { useMoveResponseDistributionState } from "./moveResponseDistributionState";

const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function data(color: "white" | "black" = "white"): MoveResponseDistributionResponse {
  return {
    fen: FEN,
    color,
    matching_game_count: 1,
    replies: [
      { rank: 1, child_uci: "e2e4", san: "e4", distinct_game_count: 1, opening_name: null },
    ],
  };
}

function Probe({
  fen,
  color,
  client,
}: {
  fen: string | null;
  color: "white" | "black";
  client: MoveResponseDistributionClient;
}) {
  const state = useMoveResponseDistributionState(fen, color, client);
  return (
    <>
      <output data-testid="state">{state.status}</output>
      <output data-testid="data">{state.data?.color ?? ""}</output>
      <output data-testid="error">{state.error ?? ""}</output>
      <button type="button" onClick={state.retry}>
        retry
      </button>
    </>
  );
}

afterEach(() => cleanup());

describe("useMoveResponseDistributionState", () => {
  it("exposes loading, available, no-games, and unavailable states", async () => {
    const results: MoveResponseDistributionResult[] = [
      { status: "success", data: data() },
      { status: "success", data: { ...data(), matching_game_count: 0, replies: [] } },
      { status: "move_response_distribution_unavailable" },
    ];
    const client = vi.fn<MoveResponseDistributionClient>(async () => results.shift()!);
    const { rerender } = render(<Probe fen={FEN} color="white" client={client} />);

    expect(screen.getByTestId("state")).toHaveTextContent("loading");
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent("available"));

    rerender(<Probe fen={`${FEN} `.trim()} color="black" client={client} />);
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent("no-games"));

    rerender(<Probe fen={FEN} color="white" client={client} />);
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent("unavailable"));
  });

  it("clears old data immediately and ignores a stale result after position replacement", async () => {
    const pending: Array<{
      resolve: (result: MoveResponseDistributionResult) => void;
      signal?: AbortSignal;
    }> = [];
    const client = vi.fn<MoveResponseDistributionClient>(
      (_fen, _color, signal) =>
        new Promise((resolve) => {
          pending.push({ resolve, signal });
        }),
    );
    const { rerender } = render(<Probe fen={FEN} color="white" client={client} />);
    await waitFor(() => expect(client).toHaveBeenCalledOnce());

    const secondFen = FEN.replace(" 0 1", "1 1");
    rerender(<Probe fen={secondFen} color="black" client={client} />);
    expect(screen.getByTestId("state")).toHaveTextContent("loading");
    expect(screen.getByTestId("data")).toHaveTextContent("");
    expect(pending[0]?.signal?.aborted).toBe(true);

    act(() => pending[0]?.resolve({ status: "success", data: data("white") }));
    await waitFor(() => expect(client).toHaveBeenCalledTimes(2));
    expect(screen.getByTestId("state")).toHaveTextContent("loading");
    expect(screen.getByTestId("data")).toHaveTextContent("");

    act(() =>
      pending[1]?.resolve({ status: "success", data: { ...data("black"), fen: secondFen } }),
    );
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent("available"));
    expect(screen.getByTestId("data")).toHaveTextContent("black");
  });

  it("retries only the current request", async () => {
    const client = vi
      .fn<MoveResponseDistributionClient>()
      .mockResolvedValueOnce({ status: "move_response_distribution_unavailable" })
      .mockResolvedValueOnce({ status: "success", data: data() });
    render(<Probe fen={FEN} color="white" client={client} />);

    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent("unavailable"));
    await act(async () => screen.getByRole("button", { name: "retry" }).click());
    await waitFor(() => expect(screen.getByTestId("state")).toHaveTextContent("available"));
    expect(client).toHaveBeenCalledTimes(2);
    expect(client).toHaveBeenLastCalledWith(FEN, "white", expect.any(AbortSignal));
  });

  it("stays idle without a position and does not request data", () => {
    const client = vi.fn<MoveResponseDistributionClient>();
    render(<Probe fen={null} color="white" client={client} />);

    expect(screen.getByTestId("state")).toHaveTextContent("idle");
    expect(client).not.toHaveBeenCalled();
  });
});
