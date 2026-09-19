import { useCallback, useEffect, useRef, useState } from "react";

import type { ChessSide, Fen } from "../chess/chessPrimitives";
import {
  fetchMoveResponseDistribution,
  failureFromInsight,
  narrowInsightResponse,
  type MoveResponseDistributionClient,
  type MoveResponseDistributionFailureCode,
  type MoveResponseDistributionResponse,
} from "./moveResponseDistributionApi";
import {
  PositionInsightQueryError,
  usePositionInsightQuery,
} from "../position-insight/positionInsightQuery";

export type MoveResponseDistributionState = {
  status: "idle" | "loading" | "available" | "no-games" | "unavailable";
  data: MoveResponseDistributionResponse | null;
  error: MoveResponseDistributionFailureCode | null;
  retry: () => void;
};

type InternalState = Omit<MoveResponseDistributionState, "retry"> & { key: string | null };

function requestKey(fen: Fen | null, color: ChessSide | null): string | null {
  return fen === null || color === null ? null : `${fen}\u0000${color}`;
}

function isEmptyResponse(data: MoveResponseDistributionResponse): boolean {
  return data.matching_game_count === 0 || data.outgoing_occurrence_count === 0;
}

function useDefaultMoveResponseDistributionState(
  fen: Fen | null,
  color: ChessSide | null,
): MoveResponseDistributionState {
  const query = usePositionInsightQuery(fen, color);
  const selected =
    query.data === undefined || fen === null || color === null
      ? null
      : narrowInsightResponse(query.data, fen, color);
  const loading =
    fen !== null && color !== null && (query.isPending || query.isFetching);
  const error = query.isError
    ? query.error instanceof PositionInsightQueryError
      ? failureFromInsight(query.error.insightError, query.error.httpStatus).status
      : "unexpected_failure"
    : selected !== null && selected.status !== "success"
      ? selected.status
      : null;
  const data = !loading && !query.isError && selected?.status === "success" ? selected.data : null;

  return {
    status:
      fen === null || color === null
        ? "idle"
        : loading
          ? "loading"
          : error !== null
            ? "unavailable"
            : data === null
              ? "unavailable"
              : isEmptyResponse(data)
                ? "no-games"
                : "available",
    data,
    error,
    retry: () => void query.refetch(),
  };
}

function useInjectedMoveResponseDistributionState(
  fen: Fen | null,
  color: ChessSide | null,
  client: MoveResponseDistributionClient,
): MoveResponseDistributionState {
  const key = requestKey(fen, color);
  const [refreshKey, setRefreshKey] = useState(0);
  const [state, setState] = useState<InternalState>({
    key: null,
    status: "idle",
    data: null,
    error: null,
  });
  const latestKeyRef = useRef<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    latestKeyRef.current = key;

    if (key === null || fen === null || color === null) {
      setState({ key: null, status: "idle", data: null, error: null });
      return () => {
        active = false;
        controller.abort();
      };
    }

    const requestedFen = fen;
    const requestedColor = color;
    setState({ key, status: "loading", data: null, error: null });

    async function load() {
      let result;
      try {
        result = await client(requestedFen, requestedColor, controller.signal);
      } catch {
        if (active && !controller.signal.aborted && latestKeyRef.current === key) {
          setState({ key, status: "unavailable", data: null, error: "unexpected_failure" });
        }
        return;
      }

      if (!active || controller.signal.aborted || latestKeyRef.current !== key) {
        return;
      }
      if (result.status !== "success") {
        setState({ key, status: "unavailable", data: null, error: result.status });
        return;
      }

      setState({
        key,
        status: isEmptyResponse(result.data) ? "no-games" : "available",
        data: result.data,
        error: null,
      });
    }

    void load();

    return () => {
      active = false;
      controller.abort();
    };
  }, [client, color, fen, key, refreshKey]);

  const retry = useCallback(() => setRefreshKey((value) => value + 1), []);
  const stateForKey: InternalState =
    state.key === key
      ? state
      : { key, status: key === null ? "idle" : "loading", data: null, error: null };

  return {
    status: stateForKey.status,
    data: stateForKey.data,
    error: stateForKey.error,
    retry,
  };
}

export function useMoveResponseDistributionState(
  fen: Fen | null,
  color: ChessSide | null,
  client: MoveResponseDistributionClient = fetchMoveResponseDistribution,
): MoveResponseDistributionState {
  // The client is a construction-time dependency: switching it remounts this
  // feature. Keeping the implementations separate avoids unused queries for test clients.
  if (client === fetchMoveResponseDistribution) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    return useDefaultMoveResponseDistributionState(fen, color);
  }
  // eslint-disable-next-line react-hooks/rules-of-hooks
  return useInjectedMoveResponseDistributionState(fen, color, client);
}
