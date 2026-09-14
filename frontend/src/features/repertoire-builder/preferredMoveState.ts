import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import { queryKeys } from "../../api/queryKeys";
import {
  fetchPreferredMove,
  getPreferredMoveDateWindow,
  type PreferredMoveFailureCode,
  type PreferredMoveReader,
  type PreferredMoveResponse,
} from "./preferredMoveApi";
import { positionKeyFromFen, type Fen } from "../chess/chessPrimitives";

export type PreferredMoveReadState = {
  preferredMove: PreferredMoveResponse | null;
  loading: boolean;
  error: PreferredMoveFailureCode | null;
  completedRefreshKey: number;
};

export class PreferredMoveQueryError extends Error {
  constructor(readonly status: PreferredMoveFailureCode) {
    super(status);
    this.name = "PreferredMoveQueryError";
  }
}

async function queryPreferredMove(
  client: PreferredMoveReader,
  fen: Fen,
  signal: AbortSignal,
): Promise<PreferredMoveResponse> {
  const result = await client(fen, { signal });
  if (result.status !== "success") {
    throw new PreferredMoveQueryError(result.status);
  }
  return result.data;
}

export function usePreferredMoveState(
  fen: Fen | null,
  client: PreferredMoveReader = fetchPreferredMove,
  refreshKey = 0,
): PreferredMoveReadState {
  const [completedRefreshKey, setCompletedRefreshKey] = useState(refreshKey);
  const [refreshPending, setRefreshPending] = useState(false);
  const lastRefreshKey = useRef(refreshKey);
  const window = getPreferredMoveDateWindow();
  const positionKey = fen === null ? "" : positionKeyFromFen(fen);
  const result = useQuery({
    queryKey: queryKeys.preferredMove({
      positionKey,
      today: window.today,
      tomorrow: window.tomorrow,
    }),
    queryFn: ({ signal }) => queryPreferredMove(client, fen!, signal),
    enabled: fen !== null,
    retry: false,
    staleTime: 30 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  useEffect(() => {
    if (lastRefreshKey.current === refreshKey) {
      return;
    }
    lastRefreshKey.current = refreshKey;

    if (fen === null) {
      setCompletedRefreshKey(refreshKey);
      return;
    }

    setRefreshPending(true);
    void result.refetch();
  }, [fen, refreshKey, result]);

  useEffect(() => {
    if (!refreshPending || result.isPending || result.isFetching) {
      return;
    }
    setRefreshPending(false);
    setCompletedRefreshKey(refreshKey);
  }, [refreshKey, refreshPending, result.isFetching, result.isPending]);

  const error = result.isError
    ? result.error instanceof PreferredMoveQueryError
      ? result.error.status
      : "unexpected_failure"
    : null;
  return {
    preferredMove: result.data ?? null,
    loading: fen !== null && (result.isPending || result.isFetching),
    error,
    completedRefreshKey,
  };
}
