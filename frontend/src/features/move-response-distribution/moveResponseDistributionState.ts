import { useCallback, useEffect, useRef, useState } from "react";

import type { ChessSide, Fen } from "../viewer/chessPrimitives";
import {
  fetchMoveResponseDistribution,
  type MoveResponseDistributionClient,
  type MoveResponseDistributionFailureCode,
  type MoveResponseDistributionResponse,
} from "./moveResponseDistributionApi";

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
  return data.matching_game_count === 0 || data.replies.length === 0;
}

export function useMoveResponseDistributionState(
  fen: Fen | null,
  color: ChessSide | null,
  client: MoveResponseDistributionClient = fetchMoveResponseDistribution,
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
