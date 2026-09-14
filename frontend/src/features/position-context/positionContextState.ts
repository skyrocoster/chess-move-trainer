import { useEffect, useRef, useState } from "react";

import {
  type PositionContextClient,
  type PositionContextFailureCode,
  type PositionContextResponse,
  fetchPositionContext,
  failureFromInsight,
  narrowInsightResponse,
} from "./positionContextApi";
import type { ChessSide, Fen } from "../chess/chessPrimitives";
import {
  PositionInsightQueryError,
  usePositionInsightQuery,
} from "../position-insight/positionInsightQuery";

export type PositionContextState = {
  context: PositionContextResponse | null;
  loading: boolean;
  error: PositionContextFailureCode | null;
};

function useDefaultPositionContextState(
  fen: Fen | null,
  trainerColor: ChessSide,
  refreshKey: number,
): PositionContextState {
  const query = usePositionInsightQuery(fen, trainerColor);
  const previousRefreshKey = useRef(refreshKey);
  const refreshPending = refreshKey !== previousRefreshKey.current;

  useEffect(() => {
    if (previousRefreshKey.current === refreshKey) return;
    previousRefreshKey.current = refreshKey;
    if (fen !== null) void query.refetch();
  }, [fen, query, refreshKey]);

  const selected =
    query.data === undefined || fen === null
      ? null
      : narrowInsightResponse(query.data, fen, trainerColor);
  const loading = fen !== null && (refreshPending || query.isPending || query.isFetching);
  const error = query.isError
    ? query.error instanceof PositionInsightQueryError
      ? failureFromInsight(query.error.insightError, query.error.httpStatus).status
      : "unexpected_failure"
    : selected !== null && selected.status !== "success"
      ? selected.status
      : null;

  return {
    context: !loading && !query.isError && selected?.status === "success" ? selected.data : null,
    loading,
    error,
  };
}

function useInjectedPositionContextState(
  fen: Fen | null,
  trainerColor: ChessSide,
  client: PositionContextClient,
  refreshKey = 0,
): PositionContextState {
  const [context, setContext] = useState<PositionContextResponse | null>(null);
  const [loading, setLoading] = useState(fen !== null);
  const [error, setError] = useState<PositionContextFailureCode | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    setContext(null);
    setError(null);

    if (fen === null) {
      setLoading(false);
      return () => {
        active = false;
        controller.abort();
      };
    }

    const requestedFen = fen;
    const requestedTrainerColor = trainerColor;
    setLoading(true);

    async function loadContext() {
      let result;
      try {
        result = await client(requestedFen, requestedTrainerColor, controller.signal);
      } catch {
        if (active && !controller.signal.aborted) {
          setLoading(false);
          setError("unexpected_failure");
        }
        return;
      }

      if (!active || controller.signal.aborted) {
        return;
      }
      if (result.status !== "success") {
        setLoading(false);
        setError(result.status);
        return;
      }

      setContext(result.data);
      setLoading(false);
      setError(null);
    }

    void loadContext();

    return () => {
      active = false;
      controller.abort();
    };
  }, [client, fen, trainerColor, refreshKey]);

  return { context, loading, error };
}

export function usePositionContextState(
  fen: Fen | null,
  trainerColor: ChessSide,
  client: PositionContextClient = fetchPositionContext,
  refreshKey = 0,
): PositionContextState {
  return client === fetchPositionContext
    ? useDefaultPositionContextState(fen, trainerColor, refreshKey)
    : useInjectedPositionContextState(fen, trainerColor, client, refreshKey);
}
