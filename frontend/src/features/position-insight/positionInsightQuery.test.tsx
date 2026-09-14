import { QueryClient } from "@tanstack/react-query";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { QueryClientTestProvider } from "../../test-utils/QueryClientTestProvider";
import type { ChessSide, Fen } from "../chess/chessPrimitives";
import { usePositionContextState } from "../position-context/positionContextState";
import { useMoveResponseDistributionState } from "../move-response-distribution/moveResponseDistributionState";
import {
  POSITION_INSIGHT_GC_TIME,
  POSITION_INSIGHT_STALE_TIME,
  positionInsightQueryKey,
} from "./positionInsightQuery";

const FEN: Fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
const COUNTER_VARIANT_FEN: Fen =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 17 42";
const AFTER_E4_FEN: Fen =
  "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1";

function insight(fen: string, color: ChessSide, asOf: string): Record<string, unknown> {
  return {
    fen,
    trainer_color: color,
    as_of: asOf,
    observed_in_games: true,
    experience: { distinct_game_count: 2, occurrence_count: 5, total_game_count: 3 },
    opening: null,
    observed_move_totals: {
      distinct_game_count: 2,
      occurrence_count: 1,
      terminal: { distinct_game_count: 0, occurrence_count: 0 },
    },
    observed_moves: [{ move_uci: "e2e4", distinct_game_count: 1, occurrence_count: 1 }],
    analysis: { state: "not_requested", result: null },
    preference: { kind: "unconfigured" },
  };
}

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    text: async () => JSON.stringify(body),
  } as unknown as Response;
}

function Consumers({ fen, color }: { fen: Fen; color: ChessSide }) {
  const context = usePositionContextState(fen, color);
  const distribution = useMoveResponseDistributionState(fen, color);
  return (
    <>
      <output data-testid="context">
        {JSON.stringify({ loading: context.loading, error: context.error, fen: context.context?.fen })}
      </output>
      <output data-testid="distribution">
        {JSON.stringify({ status: distribution.status, error: distribution.error })}
      </output>
    </>
  );
}

function renderConsumers(
  client: QueryClient,
  fen: Fen = FEN,
  color: ChessSide = "white",
) {
  return render(
    <QueryClientTestProvider client={client}>
      <Consumers fen={fen} color={color} />
    </QueryClientTestProvider>,
  );
}

function requestFrom(fetchMock: ReturnType<typeof vi.fn>): Request {
  return fetchMock.mock.calls.at(-1)?.[0] as Request;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("shared position insight query", () => {
  it("deduplicates context and distribution reads and treats counter fields as equivalent", async () => {
    const fetchMock = vi.fn().mockImplementation(async (request: Request) => {
      const query = new URL(request.url).searchParams;
      return jsonResponse(insight(query.get("fen")!, query.get("trainer_color") as ChessSide, query.get("as_of")!));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();

    const view = renderConsumers(client);
    await waitFor(() => expect(screen.getByTestId("distribution")).toHaveTextContent('"status":"available"'));
    expect(fetchMock).toHaveBeenCalledOnce();

    view.rerender(
      <QueryClientTestProvider client={client}>
        <Consumers fen={COUNTER_VARIANT_FEN} color="white" />
      </QueryClientTestProvider>,
    );
    await waitFor(() => expect(screen.getByTestId("context")).toHaveTextContent('"loading":false'));
    expect(fetchMock).toHaveBeenCalledOnce();
    expect(new URL(requestFrom(fetchMock).url).searchParams.get("fen")).toBe(FEN);
  });

  it("keeps colour, UTC date, and position boundaries distinct", async () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-09-10T23:59:00.000Z"));
    const fetchMock = vi.fn().mockImplementation(async (request: Request) => {
      const query = new URL(request.url).searchParams;
      return jsonResponse(insight(query.get("fen")!, query.get("trainer_color") as ChessSide, query.get("as_of")!));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const view = renderConsumers(client);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    view.rerender(
      <QueryClientTestProvider client={client}>
        <Consumers fen={FEN} color="black" />
      </QueryClientTestProvider>,
    );
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));

    vi.setSystemTime(new Date("2026-09-11T00:01:00.000Z"));
    view.rerender(
      <QueryClientTestProvider client={client}>
        <Consumers fen={FEN} color="white" />
      </QueryClientTestProvider>,
    );
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));

    view.rerender(
      <QueryClientTestProvider client={client}>
        <Consumers fen={AFTER_E4_FEN} color="white" />
      </QueryClientTestProvider>,
    );
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(4));
    expect(client.getQueryCache().findAll()).toHaveLength(4);
  });

  it("uses the approved freshness and retention policy", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(insight(FEN, "white", "2026-09-10")));
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    renderConsumers(client);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    const query = client.getQueryCache().find({ queryKey: positionInsightQueryKey(FEN, "white") });
    expect(query?.options.staleTime).toBe(POSITION_INSIGHT_STALE_TIME);
    expect(query?.options.gcTime).toBe(POSITION_INSIGHT_GC_TIME);
  });

  it.each([
    ["malformed", { observed_moves: [{ move_uci: "e2e5", occurrence_count: 1 }] }, 200],
    ["unsuccessful", { code: "position_insight_unavailable", message: "safe detail" }, 503],
  ] as const)("does not cache a %s response as successful data", async (_label, body, status) => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(body, status));
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    renderConsumers(client, AFTER_E4_FEN);

    await waitFor(() => expect(screen.getByTestId("distribution")).toHaveTextContent('"status":"unavailable"'));
    expect(client.getQueryData(positionInsightQueryKey(AFTER_E4_FEN, "white"))).toBeUndefined();
  });
});
